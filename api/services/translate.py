"""Word → dictionary matches.

This is the core of the translation API: take an English or Latin word, ask
the database for hits, and return full entries (via tools.lookup). HTTP
routing is not wired yet; call these functions directly or from a future
endpoint layer.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Literal, Sequence

from tools.lookup import get_entries
from tools.ls_db import Database

from api.services.definition_mode import (
    DEFAULT_DEFINITION_MODE,
    DefinitionMode,
    apply_definition_mode_to_entries,
    normalize_definition_mode,
)

Lang = Literal["la", "en"]

# Cap English sense-text search so a broad query cannot pull the whole lexicon.
DEFAULT_LIMIT = 25


def translate(
    db: Database,
    word: str,
    *,
    lang: Lang,
    limit: int = DEFAULT_LIMIT,
    definition_mode: DefinitionMode | str | None = DEFAULT_DEFINITION_MODE,
) -> List[dict[str, Any]]:
    """Return matching Lewis & Short entries for `word`.

    `lang` selects the search strategy:
      - ``"la"``: Latin headword / alternative form (exact, case-insensitive)
      - ``"en"``: English gloss text inside senses (substring, case-insensitive)

    ``definition_mode`` controls sense depth in each returned entry (Latin →
    English clients usually want ``"simplified"`` or ``"full"``; English → Latin
    lookups ignore it today but may use it later):
      - ``"full"``: entire ``senses`` tree (default)
      - ``"simplified"``: at most three top-level senses per entry

    Results are full entry dicts in the original JSON shape, ordered by how
    the search ranked them. Empty string / whitespace yields no matches.
    """
    needle = (word or "").strip()
    if not needle:
        return []

    if lang == "la":
        keys = _latin_keys(db, needle, limit=limit)
    elif lang == "en":
        keys = _english_keys(db, needle, limit=limit)
    else:
        raise ValueError("lang must be 'la' or 'en', got %r" % (lang,))

    entries = _entries_in_order(db, keys)
    mode = normalize_definition_mode(definition_mode)
    return apply_definition_mode_to_entries(entries, mode)


def _latin_keys(db: Database, word: str, *, limit: int) -> List[str]:
    """Exact match on entry_key, title_orthography, or alternative form text."""
    # Lower() keeps SQLite/Postgres/MySQL behaviour aligned for ASCII keys;
    # macron-bearing title_orthography still needs an exact typed match.
    lowered = word.lower()
    cursor = db.execute(
        """
        SELECT entry_key FROM (
            SELECT entry_key, 0 AS rank
            FROM entries
            WHERE lower(entry_key) = ?
            UNION
            SELECT entry_key, 1 AS rank
            FROM entries
            WHERE title_orthography IS NOT NULL
              AND lower(title_orthography) = ?
            UNION
            SELECT entry_key, 2 AS rank
            FROM entry_forms
            WHERE lower(form_text) = ?
        ) AS hits
        ORDER BY rank, entry_key
        LIMIT ?
        """,
        (lowered, lowered, lowered, limit),
    )
    keys = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return _unique(keys)


def _english_keys(db: Database, word: str, *, limit: int) -> List[str]:
    """Entries whose sense text contains `word` (case-insensitive substring)."""
    # Escape LIKE metacharacters so a user query of "100%" is literal.
    pattern = "%" + _escape_like(word.lower()) + "%"
    cursor = db.execute(
        """
        SELECT DISTINCT entry_key
        FROM senses
        WHERE sense_text IS NOT NULL
          AND lower(sense_text) LIKE ? ESCAPE '\\'
        ORDER BY entry_key
        LIMIT ?
        """,
        (pattern, limit),
    )
    keys = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return keys


def _entries_in_order(db: Database, keys: Sequence[str]) -> List[dict[str, Any]]:
    if not keys:
        return []
    found = get_entries(db.connection, keys)
    return [found[key] for key in keys if key in found]


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _unique(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out
