"""Curated example sentences, read on demand from sentences/<LETTER>.txt.

Each noun and verb with a curated definition may carry one simple sentence,
written and validated with tools/sentences.py. A letter's file is read the
first time a word from it is asked for, then kept in memory; the files are
part of the repository, so they never change under a running server.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from tools.sentences import parse_sentences


@lru_cache(maxsize=None)
def sentences_for_letter(letter: str) -> dict[str, dict[str, str]]:
    """{key: {"latin": ..., "english": ...}} for one letter; empty if unwritten."""
    rows, _skipped, _third = parse_sentences(letter)
    return {key: {"latin": latin, "english": english} for _, key, latin, english in rows if latin}


def example_sentence(key: str) -> Optional[dict[str, str]]:
    """The example sentence for an entry key (``puella``, ``gero1``), or None."""
    if not key:
        return None
    return sentences_for_letter(key[0].upper()).get(key)
