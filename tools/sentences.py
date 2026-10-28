"""Chunk helper for the example sentence files under sentences/.

Three subcommands, run from the repository root:

    python tools/sentences.py next G           which words to write next
    python tools/sentences.py check G          validate the format
    python tools/sentences.py status           coverage, per letter

Each noun and verb with a curated definition gets one very simple Latin
sentence and its English, stored as `key | Latin | English`:

    puella | Puella caelum videt | The girl sees the sky
    video | Cibum calidum video | I see the warm food

A noun appears as the subject, in its headword form (the nominative
singular). A verb appears in its headword form (the first person singular
present). Every sentence is a single clause.

`next` picks words the same way tools/definitions.py does, so chunks stay
deterministic and resumable: the eligible set is every noun or verb that
already has a line in definitions/<L>.txt, alphabetical, minus anything
written or `# skip:`ped in sentences/<L>.txt.
"""

from __future__ import annotations

import argparse
import re
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from definitions import ROOT, load_entries, parse_definitions, source_path  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

SENTENCES_DIR = ROOT / "sentences"

# WORD CLASSES -- which entries get a sentence. Nouns and verbs only, for now.
#
# L&S's part_of_speech is patchy: about a fifth of the defined verbs carry
# None or "P. a." (participial adjective) instead of "verb". A verb is
# recovered from main_notes when its key ends like a first person (-o, -or)
# and the notes open with principal parts ("dis-cerno, crevi, cretum, 3")
# rather than a gender ("natio, onis, f."). The few misfires get `# skip:`.
NOUN_POS = {"noun"}
VERB_POS = {"verb"}
VERB_POS_PREFIX = "v. "
LOOSE_POS = {None, "", "P. a.", "P. a.P. a."}
PRINCIPAL_PARTS = re.compile(r"^[^,\s(]+,\s*[^\s,]+")
GENDER = re.compile(r"(?:^|[\s,)])(?:f|m|n|comm)\.")

# A verb whose headword is a third person (libet, licet, taedet, ningit) has
# no first person to show, so it is left out.
IMPERSONAL_ENDING = "t"

# A single clause: no clause-joining punctuation, and none of the words that
# open a subordinate clause. `cum` is absent on purpose -- as a preposition
# ("cum amico ambulo") it is everywhere in simple sentences.
CLAUSE_PUNCTUATION = re.compile(r"[,;:]")
SUBORDINATORS = frozenset({
    "antequam", "dum", "donec", "etsi", "nisi", "postquam", "priusquam",
    "quae", "quamquam", "quando", "quia", "qui", "quod", "quoniam",
    "si", "ubi", "ut", "ne",
})

# Plain text only: no macrons, no final full stop. Latin follows the source's
# `j` spelling, matching the keys (jus, injuria).
LATIN_TEXT = re.compile(r"^[A-Z][a-z]*(?: [a-z]+)*$")
ENGLISH_TEXT = re.compile(r"^[A-Z][^.!?]*[^.!?\s]$|^[A-Z]$")


def sentences_path(letter: str) -> Path:
    return SENTENCES_DIR / f"{letter.upper()}.txt"


def headword(key: str) -> str:
    """The key without its homograph digit: gero1 -> gero."""
    return key.rstrip("0123456789")


def word_class(entry: dict) -> str | None:
    """'noun', 'verb', or None for anything that gets no sentence."""
    pos = entry.get("part_of_speech")
    notes = entry.get("main_notes") or ""
    stem = headword(entry["key"])
    if pos in NOUN_POS:
        return "noun"
    if pos in VERB_POS or (pos or "").startswith(VERB_POS_PREFIX):
        verb = True
    else:
        verb = (
            pos in LOOSE_POS
            and stem.endswith(("o", "or"))
            and PRINCIPAL_PARTS.match(notes) is not None
            and not GENDER.search(notes[:60])
        )
    if verb and not stem.endswith(IMPERSONAL_ENDING):
        return "verb"
    return None


def eligible(letter: str) -> dict[str, str]:
    """{key: 'noun' | 'verb'} for every defined noun or verb, alphabetical."""
    defined = {key for _, key, _, _ in parse_definitions(letter)[0]}
    if not defined:
        return {}
    classes = {e["key"]: word_class(e) for e in load_entries(letter) if e["key"] in defined}
    return {k: classes[k] for k in sorted(classes) if classes[k]}


def parse_sentences(letter: str) -> tuple[list[tuple[int, str, str, str]], set[str]]:
    """Return ([(line_no, key, latin, english)], {skipped}).

    Comment lines are ignored except `# skip: <key> <reason>`, which records a
    word deliberately passed over so `next` stops offering it.
    """
    path = sentences_path(letter)
    if not path.exists():
        return [], set()

    rows, skipped = [], set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            body = line[1:].lstrip()
            if body.startswith("skip:"):
                rest = body.split("skip:", 1)[1].split()
                if rest:
                    skipped.add(rest[0])
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3:
            rows.append((line_no, *parts))
        else:
            rows.append((line_no, parts[0], "", line))
    return rows, skipped


def cmd_next(args) -> int:
    letter = args.letter.upper()
    rows, skipped = parse_sentences(letter)
    done = {key for _, key, _, _ in rows}

    classes = eligible(letter)
    todo = [k for k in classes if k not in done and k not in skipped]
    remaining = len(todo)
    todo = todo[: args.count]

    if not todo:
        print(f"{letter}: nothing left -- all {len(done)} eligible words have a sentence.")
        return 0

    print(f"{letter}: {len(done)} written, {len(skipped)} skipped, {remaining} to go.")
    print(f"\nNext {len(todo)}:\n  " + ", ".join(todo))

    if args.show:
        defs: dict[str, list[str]] = {}
        for _, key, rank, definition in parse_definitions(letter)[0]:
            if key in todo and rank <= 3:
                defs.setdefault(key, []).append(f"{rank}. {definition}")
        entries = {e["key"]: e for e in load_entries(letter)}
        for key in todo:
            print(f"\n##### {key} | {classes[key]} | {entries[key].get('main_notes', '')[:80]}")
            for line in defs[key]:
                print("  " + line[:160])
    return 0


def check_letter(letter: str) -> list[str]:
    """Validate one sentences file. Returns a list of complaints."""
    letter = letter.upper()
    path = sentences_path(letter)
    if not path.exists():
        return [f"{path} does not exist"]

    errors: list[str] = []
    where = lambda n: f"{path.name}:{n}"

    try:
        classes = eligible(letter)
    except SystemExit:
        classes = None
        print(f"note: ls_{letter}.json absent, skipping the eligibility checks")

    keys: list[str] = []
    rows, _skipped = parse_sentences(letter)
    for line_no, key, latin, english in rows:
        keys.append(key)
        if not latin:
            errors.append(f"{where(line_no)}: expected 'key | Latin | English'")
            continue
        if classes is not None and key not in classes:
            errors.append(f"{where(line_no)}: {key!r} is not a defined noun or verb in {letter}")
        if not LATIN_TEXT.match(latin):
            errors.append(
                f"{where(line_no)}: Latin {latin!r} must be plain lowercase words after a capital,"
                f" no punctuation or macrons"
            )
        if not ENGLISH_TEXT.match(english) or CLAUSE_PUNCTUATION.search(english):
            errors.append(
                f"{where(line_no)}: English {english!r} must start with a capital and carry"
                f" no clause punctuation or final stop"
            )
        words = latin.lower().split()
        if headword(key) not in words:
            errors.append(
                f"{where(line_no)}: {latin!r} does not use the headword form {headword(key)!r}"
            )
        joiners = sorted(SUBORDINATORS.intersection(words))
        if joiners:
            errors.append(f"{where(line_no)}: {latin!r} is not a single clause ({', '.join(joiners)})")
        if classes is not None and classes.get(key) == "verb" and not english.startswith("I "):
            errors.append(f"{where(line_no)}: verb sentence {english!r} should be first person, 'I ...'")

    if len(set(keys)) != len(keys):
        errors.append(f"{path.name}: a key has more than one sentence; one per word")
    elif keys != sorted(keys):
        first = next(i for i in range(1, len(keys)) if keys[i] < keys[i - 1])
        errors.append(f"{path.name}: keys out of alphabetical order at {keys[first]!r}")

    if not errors:
        print(f"{path.name}: {len(keys)} sentences, all checks passed.")
    return errors


def _written_letters() -> list[str]:
    if not SENTENCES_DIR.exists():
        return []
    return sorted(p.stem for p in SENTENCES_DIR.glob("*.txt") if len(p.stem) == 1)


def cmd_check(args) -> int:
    letters = [args.letter] if args.letter else _written_letters()
    if not letters:
        print("nothing to check: sentences/ is empty")
        return 0

    errors = []
    for letter in letters:
        errors += check_letter(letter)
    for error in errors:
        print(f"  {error}")
    if errors:
        print(f"\n{len(errors)} problem(s) found.")
    return 1 if errors else 0


def cmd_status(args) -> int:
    print(f"{'':<3} {'written':>8} {'skipped':>8} {'eligible':>9}  progress")
    total_done = total_eligible = 0

    for letter in string.ascii_uppercase:
        if not source_path(letter).exists():
            continue
        classes = eligible(letter)
        rows, skipped = parse_sentences(letter)
        done = {key for _, key, _, _ in rows}
        total_done += len(done)
        total_eligible += len(classes)

        if not done and not args.all:
            continue
        pct = 100.0 * len(done) / len(classes) if classes else 0.0
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"{letter:<3} {len(done):>8} {len(skipped):>8} {len(classes):>9}  {bar} {pct:5.1f}%")

    pct = 100.0 * total_done / total_eligible if total_eligible else 0.0
    print(f"\ntotal: {total_done} of {total_eligible} eligible words ({pct:.1f}%)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_next = sub.add_parser("next", help="list the next words to write a sentence for")
    p_next.add_argument("letter", help="which letter, e.g. G")
    p_next.add_argument("-n", "--count", type=int, default=10, help="how many (default 10)")
    p_next.add_argument("--show", action="store_true", help="also print each word's top definitions")
    p_next.set_defaults(func=cmd_next)

    p_check = sub.add_parser("check", help="validate sentence files")
    p_check.add_argument("letter", nargs="?", help="one letter, or omit for every written file")
    p_check.set_defaults(func=cmd_check)

    p_status = sub.add_parser("status", help="show coverage per letter")
    p_status.add_argument("--all", action="store_true", help="include letters not yet started")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    try:
        return args.func(args)
    except BrokenPipeError:
        sys.stderr.close()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
