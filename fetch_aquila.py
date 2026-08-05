#!/usr/bin/env python3
"""Fetch ls_A.json from the lewis-short-json-api repo and print entries whose
key matches "aquila" (case-insensitive).

Usage:
    python3 fetch_aquila.py            # downloads from GitHub (raw, main branch)
    python3 fetch_aquila.py path/to/ls_A.json   # reads a local copy instead
"""

import json
import sys
import urllib.request

RAW_URL = (
    "https://raw.githubusercontent.com/stevenhayes97/"
    "lewis-short-json-api/main/ls_A.json"
)


def load_entries(source: str | None) -> list[dict]:
    if source:
        with open(source, encoding="utf-8") as f:
            return json.load(f)

    with urllib.request.urlopen(RAW_URL) as resp:
        return json.load(resp)


def main() -> None:
    source = sys.argv[1] if len(sys.argv) > 1 else None
    entries = load_entries(source)

    matches = [e for e in entries if "aquila" in e.get("key", "").lower()]

    if not matches:
        print("No entries found matching 'aquila'.")
        return

    for entry in matches:
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        print("-" * 60)


if __name__ == "__main__":
    main()
