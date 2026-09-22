"""Build reference/j_words.json: every headword spelled with a consonantal j.

Lewis & Short writes consonantal i as j (`janitor`, `ejus`, `injuria`). The
output maps each such key, verbatim, to its classical spelling with j -> i and
J -> I, so a caller can swap spellings at display time without touching keys:

    {"abjicio": "abicio", ..., "janitor": "ianitor", ...}

Run from the repository root, with the ls_*.json source files present:

    python tools/j_words.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reference" / "j_words.json"


def main() -> None:
    files = sorted(ROOT.glob("ls_*.json"))
    if not files:
        raise SystemExit(
            "no ls_*.json files; restore them with "
            "`python tools/ls_db.py export --from-raw`"
        )
    keys = {
        entry["key"]
        for path in files
        for entry in json.loads(path.read_text(encoding="utf-8"))
        if "j" in entry["key"].lower()
    }
    mapping = {k: k.replace("j", "i").replace("J", "I") for k in sorted(keys)}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(mapping)} keys to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
