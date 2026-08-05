"""Trim Lewis & Short sense trees for client-selected definition detail."""

from __future__ import annotations

import copy
from typing import Any, Literal, TypeAlias

DefinitionMode: TypeAlias = Literal["full", "simplified"]

DEFAULT_DEFINITION_MODE: DefinitionMode = "full"
SIMPLIFIED_TOP_LEVEL_SENSE_LIMIT = 3

SenseTree = list[Any]


def normalize_definition_mode(value: str | None) -> DefinitionMode:
    """Return a supported mode; unknown / omitted values become ``full``."""
    if value == "simplified":
        return "simplified"
    return "full"


def truncate_top_level_senses(senses: SenseTree, *, limit: int) -> SenseTree:
    """Keep at most ``limit`` top-level sense nodes; nested content is unchanged."""
    if limit < 0:
        raise ValueError("limit must be non-negative")
    return senses[:limit]


def apply_definition_mode_to_entry(
    entry: dict[str, Any],
    mode: DefinitionMode,
) -> dict[str, Any]:
    """Return a copy of ``entry`` with ``senses`` trimmed when mode is simplified."""
    if mode == "full":
        return entry
    out = copy.deepcopy(entry)
    senses = out.get("senses")
    if isinstance(senses, list):
        out["senses"] = truncate_top_level_senses(
            senses,
            limit=SIMPLIFIED_TOP_LEVEL_SENSE_LIMIT,
        )
    return out


def apply_definition_mode_to_entries(
    entries: list[dict[str, Any]],
    mode: DefinitionMode,
) -> list[dict[str, Any]]:
    if mode == "full":
        return entries
    return [apply_definition_mode_to_entry(entry, mode) for entry in entries]
