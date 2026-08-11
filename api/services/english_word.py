"""Map Lewis & Short entry dicts to english_word JSON Schema responses.

JSON Schema files under ``json-schemas/`` are WIP drafts; update formatters
alongside schema changes rather than treating either as frozen.
"""

from api.services.definition_mode import (
    format_english_word_response,
    format_english_word_result,
)

__all__ = ["format_english_word_response", "format_english_word_result"]
