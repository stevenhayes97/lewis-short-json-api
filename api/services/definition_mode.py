"""Trim Lewis & Short sense trees and build Logeion / Scriba-shaped payloads."""

from __future__ import annotations

import copy
import re
from typing import Any, Literal, TypeAlias

from api.services.paradigm import paradigm_from_entry

DefinitionMode: TypeAlias = Literal["both", "brief", "full"]

DEFAULT_DEFINITION_MODE: DefinitionMode = "both"
BRIEF_GLOSS_LIMIT = 3
BRIEF_GLOSS_MAX_CHARS = 160

SenseTree = list[Any]

# Legacy request values from earlier drafts.
_LEGACY_MODES = {"simplified": "brief", "full": "full"}


def normalize_definition_mode(value: str | None) -> DefinitionMode:
    """Return a supported mode; unknown / omitted values become ``both``."""
    if not value:
        return DEFAULT_DEFINITION_MODE
    if value in ("both", "brief", "full"):
        return value  # type: ignore[return-value]
    if value in _LEGACY_MODES:
        return _LEGACY_MODES[value]  # type: ignore[return-value]
    return DEFAULT_DEFINITION_MODE


def truncate_top_level_senses(senses: SenseTree, *, limit: int) -> SenseTree:
    """Keep at most ``limit`` top-level sense nodes; nested content is unchanged."""
    if limit < 0:
        raise ValueError("limit must be non-negative")
    return senses[:limit]


def _top_level_sense_strings(senses: SenseTree) -> list[str]:
    out: list[str] = []
    for node in senses:
        if isinstance(node, str):
            out.append(node)
        elif isinstance(node, list):
            for sub in node:
                if isinstance(sub, str):
                    out.append(sub)
                    break
    return out


def _shorten_gloss(text: str, *, max_chars: int = BRIEF_GLOSS_MAX_CHARS) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1].rstrip() + "…"


def brief_glosses_from_entry(entry: dict[str, Any]) -> list[str]:
    """Logeion-style short gloss lines from the first few top-level senses."""
    senses = entry.get("senses")
    if not isinstance(senses, list):
        return []
    lines = _top_level_sense_strings(senses)[:BRIEF_GLOSS_LIMIT]
    return [_shorten_gloss(line) for line in lines if line.strip()]


def primary_english_gloss(brief: list[str]) -> str:
    if not brief:
        return ""
    first = brief[0]
    for sep in (";", ","):
        if sep in first:
            chunk = first.split(sep, 1)[0].strip()
            if chunk:
                return chunk
    return first.split(".", 1)[0].strip() or first


def normalize_include_paradigms(value: bool | None) -> bool:
    if value is None:
        return True
    return bool(value)


def morphology_tab_from_entry(
    entry: dict[str, Any],
    *,
    include_paradigms: bool = True,
) -> dict[str, Any]:
    tab: dict[str, Any] = {}
    key = entry.get("key")
    if isinstance(key, str) and key:
        tab["headword"] = key
    for field in (
        "title_orthography",
        "title_genitive",
        "gender",
        "alternative_orthography",
        "alternative_genative",
    ):
        value = entry.get(field)
        if value:
            tab[field] = value
    if "declension" in entry:
        tab["declension"] = entry.get("declension")
    notes = entry.get("main_notes")
    if isinstance(notes, str) and notes.strip():
        tab["lemma_line"] = notes.strip()
    if include_paradigms:
        paradigm = paradigm_from_entry(entry)
        if paradigm:
            tab["paradigm"] = paradigm
    return tab


def connections_tab_from_entry(entry: dict[str, Any]) -> dict[str, Any]:
    tab: dict[str, Any] = {}
    for field in ("entry_type", "greek_word"):
        value = entry.get(field)
        if isinstance(value, str) and value.strip():
            if field == "greek_word":
                tab["greek_equivalent"] = value.strip()
            else:
                tab[field] = value.strip()
    notes = entry.get("main_notes")
    if isinstance(notes, str) and notes.strip():
        tab["notes"] = notes.strip()
    return tab


def definitions_for_mode(entry: dict[str, Any], mode: DefinitionMode) -> SenseTree:
    senses = entry.get("senses")
    if not isinstance(senses, list):
        return []
    if mode == "brief":
        return []
    return copy.deepcopy(senses)


def format_english_word_result(
    entry: dict[str, Any],
    mode: DefinitionMode,
    *,
    include_paradigms: bool = True,
) -> dict[str, Any]:
    """Map one Lewis & Short entry dict to the current ``english_word_result`` draft.

    Field order matches the intended UI stack: brief_glosses, definitions,
    then morphology (optional paradigm) and connections. Schema shape is WIP;
    keep this formatter in sync when drafts change.
    """
    brief = brief_glosses_from_entry(entry)
    if mode == "full":
        brief = []
    elif mode == "brief":
        pass
    # both: keep brief

    pos = entry.get("part_of_speech") or ""
    if isinstance(pos, str):
        pos = pos.strip()
    if not pos:
        pos = "unknown"

    primary = primary_english_gloss(brief)
    if not primary and mode != "brief":
        fallback_brief = brief_glosses_from_entry(entry)
        primary = primary_english_gloss(fallback_brief) or entry.get("key") or "?"

    return {
        "english_word": primary or "?",
        "part_of_speech": pos,
        "summary": "",
        "brief_glosses": brief,
        "definitions": definitions_for_mode(entry, mode),
        "morphology": morphology_tab_from_entry(
            entry,
            include_paradigms=include_paradigms,
        ),
        "connections": connections_tab_from_entry(entry),
    }


def format_english_word_response(
    latin_word: str,
    entries: list[dict[str, Any]],
    mode: DefinitionMode | str | None = None,
    *,
    include_paradigms: bool | None = None,
) -> dict[str, Any]:
    effective = normalize_definition_mode(mode if isinstance(mode, str) else None)
    paradigms = normalize_include_paradigms(include_paradigms)
    return {
        "translation_type": "english_word",
        "latin_word": latin_word,
        "definition_mode": effective,
        "include_paradigms": paradigms,
        "results": [
            format_english_word_result(
                entry,
                effective,
                include_paradigms=paradigms,
            )
            for entry in entries
        ],
    }


def apply_definition_mode_to_entry(
    entry: dict[str, Any],
    mode: DefinitionMode,
) -> dict[str, Any]:
    """Return a copy of ``entry`` with ``senses`` trimmed for brief-only callers."""
    if mode != "brief":
        return entry
    out = copy.deepcopy(entry)
    senses = out.get("senses")
    if isinstance(senses, list):
        out["senses"] = truncate_top_level_senses(senses, limit=BRIEF_GLOSS_LIMIT)
    return out


def apply_definition_mode_to_entries(
    entries: list[dict[str, Any]],
    mode: DefinitionMode,
) -> list[dict[str, Any]]:
    if mode != "brief":
        return entries
    return [apply_definition_mode_to_entry(entry, mode) for entry in entries]
