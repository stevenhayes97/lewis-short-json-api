"""Pull one entry from an ls_*.json array without loading the whole file.

The files are a top-level JSON array of objects. We stream-parse one object at
a time with json.JSONDecoder.raw_decode and stop when the key matches.

"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Windows consoles often default to cp1252; L&S text uses macrons/Greek.
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
PATH = ROOT / "ls_C.json"
TARGET = "canis1"

DEFINITIONS_DIR = ROOT / "definitions"


def iter_definitions():
    for path in sorted(DEFINITIONS_DIR.glob("*.txt")):
        with path.open(encoding="utf-8") as f:
            for line in f.readlines()[2:]:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, rank, definition = (p.strip() for p in line.split("|", 2))
                yield path.stem, key, int(rank), definition


def find_entry(path: Path, key: str) -> dict | None:
    decoder = json.JSONDecoder()
    with path.open(encoding="utf-8") as f:
        buf = ""

        # Consume leading whitespace and the opening '['.
        while True:
            chunk = f.read(8192)
            if not chunk:
                raise SystemExit(f"empty or invalid JSON: {path}")
            buf += chunk
            buf = buf.lstrip()
            if buf.startswith("["):
                buf = buf[1:]
                break

        while True:
            buf = buf.lstrip()
            while True:
                if buf.startswith(","):
                    buf = buf[1:].lstrip()
                    continue
                if buf.startswith("]"):
                    return None
                if buf.startswith("{"):
                    break
                chunk = f.read(65536)
                if not chunk:
                    return None
                buf += chunk
                buf = buf.lstrip()

            # Grow the buffer until one full object parses.
            while True:
                try:
                    obj, end = decoder.raw_decode(buf)
                    buf = buf[end:]
                    break
                except json.JSONDecodeError:
                    chunk = f.read(65536)
                    if not chunk:
                        raise
                    buf += chunk

            if obj.get("key") == key:
                return obj


if __name__ == "__main__":
    entry = find_entry(PATH, TARGET)
    if entry is None:
        raise SystemExit(f"{TARGET!r} not found in {PATH.name}")
    
    definition = json.dumps(entry, ensure_ascii=False, indent=2)
    print(definition)

    # for letter, key, rank, definition in iter_definitions():
    #     if rank in [1,2]:
    #         print(letter, key, rank, definition)