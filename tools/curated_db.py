"""Load the curated layer into the database ls_db.py built.

Run from the repository root, after `ls_db.py load`:

    python tools/curated_db.py --db sqlite:///lewis_short.db load

The text files stay the source of truth -- definitions/<L>.txt,
definitions/tags.txt and sentences/<L>.txt -- so every `load` drops the
curated tables and rebuilds them from the files. They are small (about 40,000
rows) and the rebuild takes about a second.

Five objects, all keyed on `entries.entry_key`:

    curated_definitions   one row per (key, rank) line
    curated_sentences     one row per example sentence
    curated_skips         `# skip:` lines, from either layer
    curated_tags          definitions/tags.txt
    learner_entries       a view: one flat row per defined word

Both checkers run first, and a file that fails them is not loaded.

Written for SQLite and PostgreSQL. MySQL 8 reserves the word `rank`, so the
definitions table will not create there.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import definitions  # noqa: E402
import sentences  # noqa: E402
from ls_db import column_types, connect, table_exists  # noqa: E402

VIEWS = ("learner_entries",)
TABLES = ("curated_definitions", "curated_sentences", "curated_skips", "curated_tags")


def create_schema(db):
    t = column_types(db.dialect)
    statements = [
        # review_note is set on the rank 1-2 lines of a word with a
        # `# review:` comment: the short gloss a human still has to settle.
        """
        CREATE TABLE curated_definitions (
            entry_key {key} NOT NULL REFERENCES entries (entry_key),
            rank {int} NOT NULL CHECK (rank BETWEEN 1 AND 10),
            definition {text} NOT NULL,
            review_note {text},
            PRIMARY KEY (entry_key, rank)
        )
        """,
        # third_note is set when a `# third:` comment let the verb take the
        # third person singular, and says why the first person fails.
        """
        CREATE TABLE curated_sentences (
            entry_key {key} NOT NULL PRIMARY KEY REFERENCES entries (entry_key),
            latin {text} NOT NULL,
            english {text} NOT NULL,
            third_note {text}
        )
        """,
        # No foreign key: a skip may name a word the source has misfiled, and
        # it records a decision rather than content.
        """
        CREATE TABLE curated_skips (
            entry_key {key} NOT NULL,
            layer {short} NOT NULL CHECK (layer IN ('definitions', 'sentences')),
            reason {text},
            PRIMARY KEY (entry_key, layer)
        )
        """,
        """
        CREATE TABLE curated_tags (
            entry_key {key} NOT NULL PRIMARY KEY REFERENCES entries (entry_key),
            tag {short} NOT NULL
        )
        """,
        "CREATE INDEX idx_curated_def_rank ON curated_definitions (rank)",
        "CREATE INDEX idx_curated_tags_tag ON curated_tags (tag)",
        """
        CREATE VIEW learner_entries AS
        SELECT e.entry_key,
               e.title_orthography,
               e.part_of_speech,
               d1.definition AS gloss_1,
               d2.definition AS gloss_2,
               (SELECT COUNT(*) FROM curated_definitions d WHERE d.entry_key = e.entry_key) AS rank_count,
               s.latin AS sentence_latin,
               s.english AS sentence_english,
               g.tag
        FROM entries e
        JOIN curated_definitions d1 ON d1.entry_key = e.entry_key AND d1.rank = 1
        LEFT JOIN curated_definitions d2 ON d2.entry_key = e.entry_key AND d2.rank = 2
        LEFT JOIN curated_sentences s ON s.entry_key = e.entry_key
        LEFT JOIN curated_tags g ON g.entry_key = e.entry_key
        """,
    ]
    for statement in statements:
        db.execute(statement.format(**t)).close()


def drop_schema(db):
    for view in VIEWS:
        db.execute("DROP VIEW IF EXISTS %s" % view).close()
    for table in TABLES:
        db.execute("DROP TABLE IF EXISTS %s" % table).close()


# ---------------------------------------------------------------------------
# Files -> rows
# ---------------------------------------------------------------------------


def comment_notes(path: Path, tag: str) -> dict[str, str]:
    """{key: reason} for every `# <tag> <key> <reason>` line in a file.

    The chunk tools keep only the key for `skip:` and `third:`; the reason is
    worth having in the database, so it is read here rather than changing
    what those tools return.
    """
    if not path.exists():
        return {}
    notes = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        body = line.strip()[1:].lstrip() if line.strip().startswith("#") else ""
        if body.startswith(tag):
            rest = body[len(tag):].split(None, 1)
            if rest:
                notes[rest[0]] = rest[1].strip() if len(rest) > 1 else ""
    return notes


def definition_rows(letter):
    rows, _skipped, review = definitions.parse_definitions(letter)
    out = []
    for _, key, rank, text in rows:
        note = review.get(key) if rank in definitions.SHORT_RANKS else None
        out.append((key, rank, text, note))
    skips = comment_notes(definitions.definitions_path(letter), "skip:")
    return out, skips


def sentence_rows(letter):
    rows, _skipped, _third = sentences.parse_sentences(letter)
    path = sentences.sentences_path(letter)
    third = comment_notes(path, "third:")
    out = [(key, latin, english, third.get(key)) for _, key, latin, english in rows]
    return out, comment_notes(path, "skip:")


def tag_rows():
    path = definitions.DEFINITIONS_DIR / definitions.TAGS_FILE
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            key, tag = (p.strip() for p in line.split("|"))
            out.append((key, tag))
    return out


def run_checks():
    """Both checkers over every written letter; returns their complaints."""
    errors = []
    with contextlib.redirect_stdout(io.StringIO()):
        for letter in definitions._written_letters():
            errors += definitions.check_letter(letter)
        errors += definitions.check_tags()
        for letter in sentences._written_letters():
            errors += sentences.check_letter(letter)
    return errors


# ---------------------------------------------------------------------------


def command_load(args):
    if not args.skip_check:
        errors = run_checks()
        if errors:
            for error in errors:
                print("  %s" % error)
            sys.exit("\n%d problem(s) in the curated files; fix them or pass --skip-check." % len(errors))

    def_rows, skip_rows, sent_rows = [], [], []
    for letter in definitions._written_letters():
        rows, skips = definition_rows(letter)
        def_rows += rows
        skip_rows += [(key, "definitions", why) for key, why in skips.items()]
    for letter in sentences._written_letters():
        rows, skips = sentence_rows(letter)
        sent_rows += rows
        skip_rows += [(key, "sentences", why) for key, why in skips.items()]
    tags = tag_rows()

    db = connect(args.db)
    try:
        if not table_exists(db, "entries"):
            sys.exit("No entries table in %s. Run first: python tools/ls_db.py --db %s load" % (args.db, args.db))

        drop_schema(db)
        create_schema(db)
        for statement, rows in (
            ("INSERT INTO curated_definitions VALUES (?, ?, ?, ?)", def_rows),
            ("INSERT INTO curated_sentences VALUES (?, ?, ?, ?)", sent_rows),
            ("INSERT INTO curated_skips VALUES (?, ?, ?)", skip_rows),
            ("INSERT INTO curated_tags VALUES (?, ?)", tags),
        ):
            db.executemany(statement, rows)
        db.commit()

        words = db.scalar("SELECT COUNT(*) FROM learner_entries")
        print("Loaded %d definitions across %d words." % (len(def_rows), words))
        print("       %d sentences, %d skips, %d tags." % (len(sent_rows), len(skip_rows), len(tags)))
    finally:
        db.close()


def build_parser():
    parser = argparse.ArgumentParser(
        prog="curated_db.py",
        description="Load the curated definitions, sentences and tags into the L&S database.",
    )
    parser.add_argument("--db", required=True, help="database URL or SQLite file path, as for ls_db.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    load_parser = subparsers.add_parser("load", help="drop and rebuild the curated tables from the text files")
    load_parser.add_argument("--skip-check", action="store_true", help="load without running the checkers first")
    load_parser.set_defaults(func=command_load)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
