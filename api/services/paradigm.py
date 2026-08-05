"""Build declension / conjugation tables from dictionary entries (when possible)."""

from __future__ import annotations

from typing import Any


def paradigm_from_entry(entry: dict[str, Any]) -> dict[str, Any] | None:
    """Return a paradigm payload for ``morphology.paradigm``, or None if unknown.

    Lewis & Short JSON does not ship full paradigms; this hook will grow as
    stem inference and conjugation generation are implemented.
    """
    _ = entry
    return None
