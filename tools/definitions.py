"""Chunk helper for the curated definitions files under definitions/.

Three subcommands, run from the repository root:

    python tools/definitions.py next G          which words to write next
    python tools/definitions.py check G         validate the format
    python tools/definitions.py status          coverage, per letter

`next` picks words for you so chunks stay deterministic and resumable: the
eligible set is computed from ls_<L>.json by fixed rules (see ELIGIBILITY
below), and anything already written to definitions/<L>.txt -- or explicitly
skipped there with a `# skip:` line -- drops out. Two people running it on the
same repository state get the same list.

`check` is the gate before committing a chunk. It enforces the line format,
the rank rules, and that every key exists in the source file.

Windows consoles often default to cp1252; the dictionary text is full of
macrons and Greek, so stdout is reconfigured to UTF-8 on the way in.
"""

from __future__ import annotations

import argparse
import json
import string
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFINITIONS_DIR = ROOT / "definitions"

# ELIGIBILITY -- which headwords are worth a learner-facing definition.
#
# The source files carry far more than teachable vocabulary: ls_G.json holds
# 892 entries, but 452 of those are proper nouns, Greek transliterations,
# hapax legomena and one-citation curiosities. The rules below cut G to 172.
#
# entry_type must be "main"        drops greek/foreign/hapax/gloss/spur
# key must start lowercase         drops proper nouns (Gabali, Gabaon, ...)
# senses must be non-empty         drops stubs such as genus2
# sense text >= MIN_SENSE_CHARS    drops entries that are one gloss and a cite
MIN_SENSE_CHARS = 250

MAX_RANK = 10

# Ranks 1 and 2 are the short glosses shown in their own section on the entry
# page; 3+ are the broadened senses. One word is the default and the strong
# preference, but two or three are allowed where one word misreads on its own
# -- an adjective glossed with a bare noun (aestivus "summer") looks like a
# noun with no sentence around it. Four words is a phrase, and fails.
SHORT_RANKS = (1, 2)
MAX_SHORT_WORDS = 3

# Rank 2 is optional -- written only when a second gloss carries a genuinely
# distinct core meaning -- so a 1 -> 3 jump is legal and nothing else is.
OPTIONAL_RANK = 2


def source_path(letter: str) -> Path:
    return ROOT / f"ls_{letter.upper()}.json"


def definitions_path(letter: str) -> Path:
    return DEFINITIONS_DIR / f"{letter.upper()}.txt"


def sense_chars(senses) -> int:
    """Total length of a sense tree's text, nested sub-senses included."""
    return sum(len(s) if isinstance(s, str) else sense_chars(s) for s in senses)


def load_entries(letter: str) -> list[dict]:
    path = source_path(letter)
    if not path.exists():
        raise SystemExit(
            f"{path.name} not found. If you have run `ls_db.py wipe`, restore it with:\n"
            f"  python tools/ls_db.py --db sqlite:///lewis_short.db export --out-dir . --from-raw"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def eligible_keys(letter: str) -> list[str]:
    """Headwords worth defining, alphabetical. See ELIGIBILITY above."""
    return sorted(
        e["key"]
        for e in load_entries(letter)
        if e.get("entry_type") == "main"
        and e["key"][:1].islower()
        and e.get("senses")
        and sense_chars(e["senses"]) >= MIN_SENSE_CHARS
    )


def parse_definitions(letter: str) -> tuple[list[tuple[int, str, int, str]], set[str]]:
    """Return ([(line_no, key, rank, definition)], {skipped keys}).

    Comment lines are ignored except `# skip: <key> <reason>`, which records a
    word deliberately passed over so `next` stops offering it.
    """
    path = definitions_path(letter)
    if not path.exists():
        return [], set()

    rows, skipped = [], set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if line[1:].lstrip().startswith("skip:"):
                rest = line.split("skip:", 1)[1].split()
                if rest:
                    skipped.add(rest[0])
            continue
        parts = [p.strip() for p in line.split("|")]
        rank = int(parts[1]) if len(parts) == 3 and parts[1].isdigit() else -1
        rows.append((line_no, parts[0], rank, parts[2] if len(parts) == 3 else line))
    return rows, skipped


def cmd_next(args) -> int:
    letter = args.letter.upper()
    rows, skipped = parse_definitions(letter)
    done = {key for _, key, _, _ in rows}

    todo = [k for k in eligible_keys(letter) if k not in done and k not in skipped]
    remaining = len(todo)
    todo = todo[: args.count]

    if not todo:
        print(f"{letter}: nothing left -- all {len(done)} eligible words are written.")
        return 0

    print(f"{letter}: {len(done)} written, {len(skipped)} skipped, {remaining} to go.")
    print(f"\nNext {len(todo)}:\n  " + ", ".join(todo))

    if args.show:
        entries = {e["key"]: e for e in load_entries(letter)}
        for key in todo:
            entry = entries[key]
            print(f"\n##### {key} | {entry.get('part_of_speech')} | {entry.get('main_notes', '')[:100]}")
            _print_senses(entry["senses"])
    return 0


def _print_senses(senses, depth: int = 0) -> None:
    for sense in senses:
        if isinstance(sense, str):
            print("  " * depth + "- " + sense[:200].replace("\n", " "))
        else:
            _print_senses(sense, depth + 1)


def check_letter(letter: str) -> list[str]:
    """Validate one definitions file. Returns a list of complaints."""
    letter = letter.upper()
    path = definitions_path(letter)
    if not path.exists():
        return [f"{path} does not exist"]

    errors: list[str] = []
    where = lambda n: f"{path.name}:{n}"

    try:
        keys_in_source = {e["key"] for e in load_entries(letter)}
    except SystemExit:
        keys_in_source = None
        print(f"note: ls_{letter}.json absent, skipping the key-exists check")

    ranks: dict[str, list[int]] = {}
    order: list[str] = []

    for line_no, key, rank, definition in parse_definitions(letter)[0]:
        if rank == -1:
            errors.append(f"{where(line_no)}: expected 'key | rank | definition'")
            continue
        if keys_in_source is not None and key not in keys_in_source:
            errors.append(f"{where(line_no)}: key {key!r} is not in ls_{letter}.json")
        if not definition:
            errors.append(f"{where(line_no)}: empty definition")
        if rank in SHORT_RANKS and len(definition.split()) > MAX_SHORT_WORDS:
            errors.append(
                f"{where(line_no)}: rank {rank} takes at most {MAX_SHORT_WORDS} words"
                f" (one preferred), got {definition!r}"
            )
        if key not in ranks:
            ranks[key] = []
            order.append(key)
        ranks[key].append(rank)

    for key, rs in ranks.items():
        if rs[0] != 1:
            errors.append(f"{key}: starts at rank {rs[0]}, must start at 1")
        if rs != sorted(rs):
            errors.append(f"{key}: ranks out of order: {rs}")
        if len(rs) != len(set(rs)):
            errors.append(f"{key}: duplicate ranks: {rs}")
        if len(rs) > MAX_RANK:
            errors.append(f"{key}: {len(rs)} ranks, the cap is {MAX_RANK}")
        gaps = [r for r in range(1, rs[-1] + 1) if r not in rs]
        if gaps not in ([], [OPTIONAL_RANK]):
            errors.append(f"{key}: gap at rank(s) {gaps}; only {OPTIONAL_RANK} may be skipped")

    if len(set(order)) != len(order):
        errors.append("keys are not grouped: some key's lines are split apart")
    elif order != sorted(order):
        first = next(i for i in range(1, len(order)) if order[i] < order[i - 1])
        errors.append(f"keys out of alphabetical order at {order[first]!r} (after {order[first - 1]!r})")

    if not errors:
        print(f"{path.name}: {len(ranks)} words, {sum(len(r) for r in ranks.values())} lines, all checks passed.")
    return errors


def cmd_check(args) -> int:
    letters = [args.letter] if args.letter else _written_letters()
    if not letters:
        print("nothing to check: definitions/ is empty")
        return 0

    errors = []
    for letter in letters:
        errors += check_letter(letter)

    for error in errors:
        print(f"  {error}")
    if errors:
        print(f"\n{len(errors)} problem(s) found.")
    return 1 if errors else 0


def _written_letters() -> list[str]:
    if not DEFINITIONS_DIR.exists():
        return []
    return sorted(p.stem for p in DEFINITIONS_DIR.glob("*.txt") if len(p.stem) == 1)


def cmd_status(args) -> int:
    print(f"{'':<3} {'written':>8} {'skipped':>8} {'eligible':>9}  progress")
    total_done = total_eligible = 0

    for letter in string.ascii_uppercase:
        if not source_path(letter).exists():
            continue
        eligible = eligible_keys(letter)
        rows, skipped = parse_definitions(letter)
        done = {key for _, key, _, _ in rows}
        total_done += len(done)
        total_eligible += len(eligible)

        if not done and not args.all:
            continue
        pct = 100.0 * len(done) / len(eligible) if eligible else 0.0
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"{letter:<3} {len(done):>8} {len(skipped):>8} {len(eligible):>9}  {bar} {pct:5.1f}%")

    pct = 100.0 * total_done / total_eligible if total_eligible else 0.0
    print(f"\ntotal: {total_done} of {total_eligible} eligible words ({pct:.1f}%)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_next = sub.add_parser("next", help="list the next words to define")
    p_next.add_argument("letter", help="which letter, e.g. G")
    p_next.add_argument("-n", "--count", type=int, default=10, help="how many (default 10)")
    p_next.add_argument("--show", action="store_true", help="also print each word's senses")
    p_next.set_defaults(func=cmd_next)

    p_check = sub.add_parser("check", help="validate definitions files")
    p_check.add_argument("letter", nargs="?", help="one letter, or omit for every written file")
    p_check.set_defaults(func=cmd_check)

    p_status = sub.add_parser("status", help="show coverage per letter")
    p_status.add_argument("--all", action="store_true", help="include letters not yet started")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    try:
        return args.func(args)
    except BrokenPipeError:
        # Piping into `head` closes stdout early; that is not an error.
        sys.stderr.close()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
