#!/usr/bin/env python3
"""Load the Lewis & Short JSON files into a relational database, and retire them
from the repository once the load is verified.

Four subcommands:

    load    create the schema and insert every entry
    verify  rebuild the JSON from the database and diff it against the files
    export  write the database back out as JSON files
    wipe    verify, then `git rm` the JSON files

Only the standard library is required for SQLite. PostgreSQL needs `psycopg`
(v3) or `psycopg2`; MySQL/MariaDB needs `PyMySQL`.

    python tools/ls_db.py load --db sqlite:///lewis_short.db
    python tools/ls_db.py verify --db sqlite:///lewis_short.db
    python tools/ls_db.py wipe --db sqlite:///lewis_short.db --yes

Run `python tools/ls_db.py <subcommand> --help` for the full option list.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from urllib.parse import unquote, urlparse

# ---------------------------------------------------------------------------
# Shape of the source data
# ---------------------------------------------------------------------------

# Scalars that become columns on `entries`. Anything here that is missing from
# an entry is stored as NULL.
SCALAR_FIELDS = (
    "entry_type",
    "part_of_speech",
    "title_orthography",
    "title_genitive",
    "declension",
    "gender",
    "greek_word",
    "main_notes",
)

# List-of-string fields. Each element becomes a row in `entry_forms`, tagged
# with the kind below. "alternative_genative" is misspelled in the source data;
# it is stored under the corrected kind name.
LIST_FIELDS = {
    "alternative_orthography": "orthography",
    "alternative_genative": "genitive",
}

# Handled structurally rather than as a column.
STRUCTURAL_FIELDS = ("key", "senses")

KNOWN_FIELDS = frozenset(SCALAR_FIELDS) | frozenset(LIST_FIELDS) | frozenset(STRUCTURAL_FIELDS)

DEFAULT_PATTERN = "ls_*.json"


# ---------------------------------------------------------------------------
# Database plumbing
# ---------------------------------------------------------------------------


class Database:
    """Thin wrapper over a DB-API 2.0 connection.

    Hides the two things that actually differ between engines: the parameter
    placeholder and a handful of column types. SQL is written with `?` and
    rewritten for engines that want `%s`.
    """

    def __init__(self, dialect, connection, placeholder):
        self.dialect = dialect
        self.connection = connection
        self.placeholder = placeholder

    def sql(self, statement):
        if self.placeholder == "?":
            return statement
        return statement.replace("?", self.placeholder)

    def execute(self, statement, params=()):
        cursor = self.connection.cursor()
        cursor.execute(self.sql(statement), params)
        return cursor

    def executemany(self, statement, rows):
        if not rows:
            return
        cursor = self.connection.cursor()
        cursor.executemany(self.sql(statement), rows)
        cursor.close()

    def scalar(self, statement, params=()):
        cursor = self.execute(statement, params)
        row = cursor.fetchone()
        cursor.close()
        return None if row is None else row[0]

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def connect(db_url):
    """Open `db_url`. A bare filesystem path is treated as SQLite."""
    scheme = urlparse(db_url).scheme.lower()
    # A Windows drive letter ("C:\data\ls.db") parses as a one-character
    # scheme; that is a path, not a URL.
    if len(scheme) == 1:
        scheme = ""

    if scheme in ("", "sqlite", "sqlite3", "file"):
        import sqlite3

        path = db_url
        if scheme:
            # Follow the usual convention: sqlite:///relative.db is relative,
            # sqlite:////absolute/path.db is absolute. Both leave exactly one
            # leading slash after the scheme, so strip one and no more.
            path = unquote(db_url.split("://", 1)[1])
            if path.startswith("/"):
                path = path[1:]
        if not path:
            sys.exit("No SQLite path given in %r" % db_url)
        parent = os.path.dirname(os.path.abspath(path))
        if path != ":memory:" and not os.path.isdir(parent):
            sys.exit("Directory does not exist: %s" % parent)
        connection = sqlite3.connect(path)
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute("PRAGMA foreign_keys = ON")
        return Database("sqlite", connection, "?")

    if scheme in ("postgres", "postgresql"):
        try:
            import psycopg  # type: ignore

            connection = psycopg.connect(db_url)
        except ImportError:
            try:
                import psycopg2  # type: ignore

                connection = psycopg2.connect(db_url)
            except ImportError:
                sys.exit("PostgreSQL support needs a driver: pip install psycopg[binary]")
        return Database("postgresql", connection, "%s")

    if scheme in ("mysql", "mariadb"):
        try:
            import pymysql  # type: ignore
        except ImportError:
            sys.exit("MySQL support needs a driver: pip install PyMySQL")
        parsed = urlparse(db_url)
        connection = pymysql.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=(parsed.path or "/").lstrip("/"),
            charset="utf8mb4",
        )
        return Database("mysql", connection, "%s")

    sys.exit("Unsupported database URL: %s" % db_url)


def column_types(dialect):
    """Per-engine column types. Keys are short aliases used in the DDL below."""
    if dialect == "postgresql":
        return {"key": "VARCHAR(191)", "short": "VARCHAR(191)", "text": "TEXT", "int": "INTEGER", "id": "BIGINT"}
    if dialect == "mysql":
        # utf8mb4 indexes cap at 191 chars, and MySQL TEXT cannot be a PK.
        return {"key": "VARCHAR(191)", "short": "VARCHAR(191)", "text": "MEDIUMTEXT", "int": "INT", "id": "BIGINT"}
    return {"key": "TEXT", "short": "TEXT", "text": "TEXT", "int": "INTEGER", "id": "INTEGER"}


TABLES = ("senses", "entry_extra", "entry_forms", "entries")  # child-first, for DROP


def create_schema(db, with_raw):
    t = column_types(db.dialect)
    raw_column = ",\n    raw_json {text}".format(**t) if with_raw else ""

    statements = [
        """
        CREATE TABLE IF NOT EXISTS entries (
            entry_key {key} NOT NULL PRIMARY KEY,
            source_file {short} NOT NULL,
            file_index {int} NOT NULL,
            entry_type {short},
            part_of_speech {short},
            title_orthography {short},
            title_genitive {short},
            declension {int},
            gender {short},
            greek_word {short},
            main_notes {text}{raw}
        )
        """.format(raw=raw_column, **t),
        """
        CREATE TABLE IF NOT EXISTS entry_forms (
            form_id {id} NOT NULL PRIMARY KEY,
            entry_key {key} NOT NULL,
            form_kind {short} NOT NULL,
            ordinal {int} NOT NULL,
            form_text {short} NOT NULL
        )
        """.format(**t),
        """
        CREATE TABLE IF NOT EXISTS entry_extra (
            extra_id {id} NOT NULL PRIMARY KEY,
            entry_key {key} NOT NULL,
            field_name {short} NOT NULL,
            value_json {text}
        )
        """.format(**t),
        # parent_sense_id is NULL for top-level senses. sense_text is NULL for
        # the handful of structural nodes that group sub-senses with no sense
        # of their own -- see build_sense_rows().
        """
        CREATE TABLE IF NOT EXISTS senses (
            sense_id {id} NOT NULL PRIMARY KEY,
            entry_key {key} NOT NULL,
            parent_sense_id {id},
            ordinal {int} NOT NULL,
            depth {int} NOT NULL,
            path {short} NOT NULL,
            sort_key {short} NOT NULL,
            sense_text {text}
        )
        """.format(**t),
    ]
    for statement in statements:
        db.execute(statement).close()
    db.commit()

    indexes = [
        ("idx_entries_type", "entries (entry_type)"),
        ("idx_entries_pos", "entries (part_of_speech)"),
        # Declension and gender are the obvious morphological filters, and
        # without these a lookup like "third-declension feminines" degrades to
        # a full scan of a table made large by raw_json.
        ("idx_entries_decl_gender", "entries (declension, gender)"),
        ("idx_entries_gender", "entries (gender)"),
        ("idx_forms_entry", "entry_forms (entry_key)"),
        ("idx_forms_text", "entry_forms (form_text)"),
        ("idx_extra_entry", "entry_extra (entry_key)"),
        ("idx_senses_entry", "senses (entry_key)"),
        ("idx_senses_parent", "senses (parent_sense_id)"),
        ("idx_senses_sort", "senses (entry_key, sort_key)"),
    ]
    # MySQL has no CREATE INDEX IF NOT EXISTS, so create each one on its own
    # and treat a failure as "it is already there".
    for name, target in indexes:
        try:
            db.execute("CREATE INDEX %s ON %s" % (name, target)).close()
            db.commit()
        except Exception:
            try:
                db.connection.rollback()
            except Exception:
                pass


def drop_schema(db):
    for table in TABLES:
        db.execute("DROP TABLE IF EXISTS %s" % table).close()
    db.commit()


def table_exists(db, name):
    try:
        db.execute("SELECT 1 FROM %s WHERE 1 = 0" % name).close()
        return True
    except Exception:
        # A failed statement poisons a PostgreSQL transaction; start a new one.
        try:
            db.connection.rollback()
        except Exception:
            pass
        return False


# ---------------------------------------------------------------------------
# JSON -> rows
# ---------------------------------------------------------------------------


def build_sense_rows(entry_key, senses, next_id, parent_id=None, depth=0, prefix="", sort_prefix=""):
    """Flatten the nested `senses` outline into rows.

    A string element is a sense. A list element holds the sub-senses of the
    string that precedes it. A list with no preceding string (29 of these
    exist) becomes a NULL-text node so the nesting survives a round trip.

    Each row gets two positions: `path` reads naturally ("4.1.1"), and
    `sort_key` zero-pads every segment ("04.01.01") so that ordering by it is
    reading order. Some entries have more than nine senses at one level, where
    a plain string sort of `path` would put 10 ahead of 2.

    `next_id` is a one-element list used as a mutable counter, so sense ids are
    assigned here rather than by the database. That keeps inserts batchable and
    avoids per-engine autoincrement syntax.
    """
    rows = []
    ordinal = 0
    last_sense_id = None

    for element in senses:
        is_group = isinstance(element, list)
        if is_group and last_sense_id is not None:
            rows.extend(
                build_sense_rows(
                    entry_key, element, next_id, last_sense_id, depth + 1, last_path + ".", last_sort + "."
                )
            )
            continue

        # A sense string, or a placeholder for a list with no sense above it.
        ordinal += 1
        sense_id = next_id[0]
        next_id[0] += 1
        path = "%s%d" % (prefix, ordinal)
        sort_key = "%s%02d" % (sort_prefix, ordinal)
        rows.append((sense_id, entry_key, parent_id, ordinal, depth, path, sort_key, None if is_group else element))
        last_sense_id, last_path, last_sort = sense_id, path, sort_key

        if is_group:
            rows.extend(
                build_sense_rows(entry_key, element, next_id, sense_id, depth + 1, path + ".", sort_key + ".")
            )

    return rows


def build_entry_rows(entry, source_file, file_index, next_form_id, next_extra_id, next_sense_id, with_raw):
    entry_key = entry["key"]

    values = [entry_key, source_file, file_index]
    values.extend(entry.get(field) for field in SCALAR_FIELDS)
    if with_raw:
        values.append(json.dumps(entry, ensure_ascii=False, sort_keys=True))

    forms = []
    for field, kind in LIST_FIELDS.items():
        for ordinal, form_text in enumerate(entry.get(field) or [], start=1):
            forms.append((next_form_id[0], entry_key, kind, ordinal, form_text))
            next_form_id[0] += 1

    # Anything the source grows later lands here instead of being dropped.
    extras = []
    for field in sorted(set(entry) - KNOWN_FIELDS):
        extras.append((next_extra_id[0], entry_key, field, json.dumps(entry[field], ensure_ascii=False)))
        next_extra_id[0] += 1

    senses = build_sense_rows(entry_key, entry.get("senses") or [], next_sense_id)

    return tuple(values), forms, extras, senses


def entry_insert_sql(with_raw):
    columns = ["entry_key", "source_file", "file_index"] + list(SCALAR_FIELDS)
    if with_raw:
        columns.append("raw_json")
    placeholders = ", ".join("?" for _ in columns)
    return "INSERT INTO entries (%s) VALUES (%s)" % (", ".join(columns), placeholders)


FORM_INSERT = "INSERT INTO entry_forms (form_id, entry_key, form_kind, ordinal, form_text) VALUES (?, ?, ?, ?, ?)"
EXTRA_INSERT = "INSERT INTO entry_extra (extra_id, entry_key, field_name, value_json) VALUES (?, ?, ?, ?)"
SENSE_INSERT = (
    "INSERT INTO senses (sense_id, entry_key, parent_sense_id, ordinal, depth, path, sort_key, sense_text) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
)


def source_files(directory, pattern):
    paths = sorted(glob.glob(os.path.join(directory, pattern)))
    if not paths:
        sys.exit("No files matched %s in %s" % (pattern, os.path.abspath(directory)))
    return paths


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# Subcommand: load
# ---------------------------------------------------------------------------


def command_load(args):
    db = connect(args.db)
    with_raw = not args.no_raw

    try:
        if args.recreate:
            drop_schema(db)
        elif table_exists(db, "entries"):
            existing = db.scalar("SELECT COUNT(*) FROM entries")
            if existing:
                sys.exit(
                    "entries already holds %d rows. Re-run with --recreate to rebuild "
                    "from scratch, or point --db at a different database." % existing
                )

        create_schema(db, with_raw)

        insert_entry = entry_insert_sql(with_raw)
        next_form_id, next_extra_id, next_sense_id = [1], [1], [1]
        totals = {"entries": 0, "forms": 0, "extras": 0, "senses": 0}

        for path in source_files(args.source_dir, args.pattern):
            source_file = os.path.basename(path)
            entries = load_json(path)

            entry_rows, form_rows, extra_rows, sense_rows = [], [], [], []
            for file_index, entry in enumerate(entries):
                one, forms, extras, senses = build_entry_rows(
                    entry, source_file, file_index, next_form_id, next_extra_id, next_sense_id, with_raw
                )
                entry_rows.append(one)
                form_rows.extend(forms)
                extra_rows.extend(extras)
                sense_rows.extend(senses)

            for statement, rows in (
                (insert_entry, entry_rows),
                (FORM_INSERT, form_rows),
                (EXTRA_INSERT, extra_rows),
                (SENSE_INSERT, sense_rows),
            ):
                for start in range(0, len(rows), args.batch_size):
                    db.executemany(statement, rows[start : start + args.batch_size])
            db.commit()

            totals["entries"] += len(entry_rows)
            totals["forms"] += len(form_rows)
            totals["extras"] += len(extra_rows)
            totals["senses"] += len(sense_rows)
            print("  %-14s %6d entries  %6d senses" % (source_file, len(entry_rows), len(sense_rows)))

        print(
            "\nLoaded %d entries, %d senses, %d alternative forms, %d extra fields."
            % (totals["entries"], totals["senses"], totals["forms"], totals["extras"])
        )
        print("Next: python %s verify --db %s" % (os.path.relpath(__file__), args.db))
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Reading back out
# ---------------------------------------------------------------------------


def fetch_entries(db, source_file, with_raw):
    """Rebuild every entry of one source file from the normalized tables."""
    columns = ["entry_key", "file_index"] + list(SCALAR_FIELDS)
    if with_raw:
        columns.append("raw_json")

    cursor = db.execute(
        "SELECT %s FROM entries WHERE source_file = ? ORDER BY file_index" % ", ".join(columns),
        (source_file,),
    )
    rows = cursor.fetchall()
    cursor.close()

    entries = {}
    order = []
    for row in rows:
        entry_key = row[0]
        order.append(entry_key)
        record = {"key": entry_key}
        for name, value in zip(SCALAR_FIELDS, row[2 : 2 + len(SCALAR_FIELDS)]):
            record[name] = value
        for field in LIST_FIELDS:
            record[field] = []
        record["senses"] = []
        if with_raw:
            record["__raw__"] = row[-1]
        entries[entry_key] = record

    if not order:
        return []

    cursor = db.execute(
        "SELECT f.entry_key, f.form_kind, f.form_text FROM entry_forms f "
        "JOIN entries e ON e.entry_key = f.entry_key WHERE e.source_file = ? "
        "ORDER BY f.entry_key, f.form_kind, f.ordinal",
        (source_file,),
    )
    kind_to_field = {kind: field for field, kind in LIST_FIELDS.items()}
    for entry_key, form_kind, form_text in cursor.fetchall():
        entries[entry_key][kind_to_field[form_kind]].append(form_text)
    cursor.close()

    cursor = db.execute(
        "SELECT x.entry_key, x.field_name, x.value_json FROM entry_extra x "
        "JOIN entries e ON e.entry_key = x.entry_key WHERE e.source_file = ? "
        "ORDER BY x.entry_key, x.field_name",
        (source_file,),
    )
    for entry_key, field_name, value_json in cursor.fetchall():
        entries[entry_key][field_name] = json.loads(value_json)
    cursor.close()

    cursor = db.execute(
        "SELECT s.entry_key, s.sense_id, s.parent_sense_id, s.sense_text FROM senses s "
        "JOIN entries e ON e.entry_key = s.entry_key WHERE e.source_file = ? "
        "ORDER BY s.entry_key, s.depth, s.ordinal",
        (source_file,),
    )
    children = {}
    text_of = {}
    for entry_key, sense_id, parent_sense_id, sense_text in cursor.fetchall():
        children.setdefault((entry_key, parent_sense_id), []).append(sense_id)
        text_of[sense_id] = sense_text
    cursor.close()

    def rebuild(entry_key, parent_sense_id):
        out = []
        for sense_id in children.get((entry_key, parent_sense_id), []):
            sense_text = text_of[sense_id]
            if sense_text is not None:
                out.append(sense_text)
            sub = rebuild(entry_key, sense_id)
            if sub:
                out.append(sub)
        return out

    for entry_key in order:
        entries[entry_key]["senses"] = rebuild(entry_key, None)

    return [entries[entry_key] for entry_key in order]


def normalize_for_compare(entry):
    """Drop the absent-vs-null distinction the columns cannot carry.

    A handful of source entries omit `senses`, `gender`, or others entirely,
    while others carry them as null. Once loaded, both read back as null, so
    comparison treats missing and null as equal and empty lists as absent.
    """
    out = {}
    for name, value in entry.items():
        if name.startswith("__"):
            continue
        if value is None:
            continue
        if isinstance(value, list) and not value:
            continue
        out[name] = value
    return out


# ---------------------------------------------------------------------------
# Subcommand: verify
# ---------------------------------------------------------------------------


def command_verify(args):
    db = connect(args.db)
    try:
        require_loaded(db, args.db)
        with_raw = raw_available(db)
        paths = source_files(args.source_dir, args.pattern)
        total_entries = 0
        problems = []

        for path in paths:
            source_file = os.path.basename(path)
            original = load_json(path)
            rebuilt = fetch_entries(db, source_file, with_raw)

            if len(original) != len(rebuilt):
                problems.append(
                    "%s: %d entries in JSON, %d in database" % (source_file, len(original), len(rebuilt))
                )
                continue

            mismatches = 0
            raw_mismatches = 0
            for source_entry, db_entry in zip(original, rebuilt):
                if normalize_for_compare(source_entry) != normalize_for_compare(db_entry):
                    mismatches += 1
                    if mismatches == 1:
                        problems.append(
                            "%s: first mismatch at key %r" % (source_file, source_entry.get("key"))
                        )
                if with_raw and json.loads(db_entry["__raw__"]) != source_entry:
                    raw_mismatches += 1

            if mismatches:
                problems.append("%s: %d entries differ" % (source_file, mismatches))
            if raw_mismatches:
                problems.append("%s: %d raw_json values differ" % (source_file, raw_mismatches))

            total_entries += len(original)
            status = "OK" if not mismatches and not raw_mismatches else "MISMATCH"
            print("  %-14s %6d entries  %s" % (source_file, len(original), status))

        if problems:
            print("\nVerification FAILED:")
            for problem in problems:
                print("  - " + problem)
            return 1

        print(
            "\nVerified %d entries across %d files. Database matches the JSON%s."
            % (total_entries, len(paths), " (including byte-exact raw_json)" if with_raw else "")
        )
        return 0
    finally:
        db.close()


def require_loaded(db, db_url):
    if not table_exists(db, "entries"):
        sys.exit("No `entries` table in %s -- run the `load` subcommand first." % db_url)
    if not db.scalar("SELECT COUNT(*) FROM entries"):
        sys.exit("The `entries` table in %s is empty -- run the `load` subcommand first." % db_url)


def raw_available(db):
    try:
        db.execute("SELECT raw_json FROM entries WHERE 1 = 0").close()
        return True
    except Exception:
        try:
            db.connection.rollback()
        except Exception:
            pass
        return False


# ---------------------------------------------------------------------------
# Subcommand: export
# ---------------------------------------------------------------------------


def command_export(args):
    db = connect(args.db)
    try:
        require_loaded(db, args.db)
        with_raw = raw_available(db)
        cursor = db.execute("SELECT DISTINCT source_file FROM entries ORDER BY source_file")
        files = [row[0] for row in cursor.fetchall()]
        cursor.close()
        if not files:
            sys.exit("No entries found in the database.")

        os.makedirs(args.out_dir, exist_ok=True)
        for source_file in files:
            entries = fetch_entries(db, source_file, with_raw)
            if args.from_raw:
                if not with_raw:
                    sys.exit("--from-raw needs a database loaded without --no-raw.")
                payload = [json.loads(entry["__raw__"]) for entry in entries]
            else:
                payload = [normalize_for_compare(entry) for entry in entries]

            out_path = os.path.join(args.out_dir, source_file)
            with open(out_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=args.indent)
                handle.write("\n")
            print("  wrote %-14s %6d entries" % (source_file, len(payload)))

        print("\nExported %d files to %s" % (len(files), os.path.abspath(args.out_dir)))
        return 0
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Subcommand: wipe
# ---------------------------------------------------------------------------


def command_wipe(args):
    paths = source_files(args.source_dir, args.pattern)

    if args.skip_verify:
        print("Skipping verification at your request.\n")
    else:
        print("Verifying the database against the JSON before removing anything...\n")
        if command_verify(args) != 0:
            sys.exit("\nRefusing to remove the JSON files: verification failed.")
        print("")

    print("These %d files will be removed from the repository:" % len(paths))
    for path in paths:
        print("  " + os.path.relpath(path, args.source_dir))

    if not args.yes:
        answer = input("\nType 'wipe' to confirm: ").strip()
        if answer != "wipe":
            sys.exit("Aborted. Nothing was removed.")

    command = ["git", "rm", "--quiet"]
    if args.keep_local:
        command.append("--cached")
    command.extend(paths)

    result = subprocess.run(command, cwd=args.source_dir)
    if result.returncode != 0:
        sys.exit("git rm failed with exit code %d." % result.returncode)

    print("\nRemoved %d files from the git index%s." % (len(paths), "" if args.keep_local else " and from disk"))
    print("Nothing has been committed or pushed. To finish:")
    print('    git commit -m "Move dictionary data into the database"')
    print("    git push")
    print(
        "\nNote: the files stay in git history, so `git clone` still downloads them.\n"
        "Rewriting history (git filter-repo) is the only way to shrink the clone,\n"
        "and it rewrites every commit hash -- worth doing deliberately, separately."
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ls_db.py",
        description="Load the Lewis & Short JSON files into a database and retire them from the repo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Database URLs:\n"
            "  sqlite:///lewis_short.db              relative path (three slashes)\n"
            "  sqlite:////srv/data/lewis_short.db    absolute path (four slashes)\n"
            "  C:\\\\data\\\\lewis_short.db               a bare path also works\n"
            "  postgresql://user:pass@localhost/ls   needs psycopg\n"
            "  mysql://user:pass@localhost/ls        needs PyMySQL\n"
        ),
    )
    parser.add_argument("--db", required=True, help="database URL or SQLite file path")
    parser.add_argument(
        "--source-dir",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="directory holding the JSON files (default: the repository root)",
    )
    parser.add_argument("--pattern", default=DEFAULT_PATTERN, help="glob for the JSON files (default: %(default)s)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    load_parser = subparsers.add_parser("load", help="create the schema and insert every entry")
    load_parser.add_argument("--recreate", action="store_true", help="drop existing tables first")
    load_parser.add_argument(
        "--no-raw",
        action="store_true",
        help="skip the raw_json column (saves ~75 MB, gives up byte-exact restore)",
    )
    load_parser.add_argument("--batch-size", type=int, default=1000, help="rows per executemany (default: %(default)s)")
    load_parser.set_defaults(func=command_load)

    verify_parser = subparsers.add_parser("verify", help="diff the database against the JSON files")
    verify_parser.set_defaults(func=command_verify)

    export_parser = subparsers.add_parser("export", help="write the database back out as JSON")
    export_parser.add_argument("--out-dir", default="export", help="destination directory (default: %(default)s)")
    export_parser.add_argument("--indent", type=int, default=2, help="JSON indent (default: %(default)s)")
    export_parser.add_argument("--from-raw", action="store_true", help="export the stored raw_json verbatim")
    export_parser.set_defaults(func=command_export)

    wipe_parser = subparsers.add_parser("wipe", help="verify, then git rm the JSON files")
    wipe_parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    wipe_parser.add_argument("--keep-local", action="store_true", help="git rm --cached: untrack but keep on disk")
    wipe_parser.add_argument("--skip-verify", action="store_true", help="remove without verifying first")
    wipe_parser.set_defaults(func=command_wipe)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
