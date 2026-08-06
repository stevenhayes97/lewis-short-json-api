# Translation API

Lightweight FastAPI app that will expose Lewis & Short lookups over HTTP.
This first step wires the non-HTTP pieces only.

L&S entries are the base; response shaping (gloss order, morphology, paradigms,
`summary`, etc.) is the enhancement layer — see the root [README](../README.md).

| Module | Role |
| --- | --- |
| `main.py` | FastAPI app object — **no routes yet** |
| `config.py` | `LEWIS_SHORT_DATABASE_URL` (default `sqlite:///lewis_short.db`) |
| `db.py` | context-managed connection via `tools.ls_db.connect` |
| `services/translate.py` | `translate(db, word, lang="la"|"en")` → full entry dicts |
| `services/english_word.py` | `format_english_word_response(...)` → Logeion + Scriba JSON |

`translate` reuses `tools.lookup.get_entries` so response shapes match the
original JSON. Latin search is an exact, case-insensitive match on
`entry_key`, `title_orthography`, or `entry_forms.form_text`. English search
is a case-insensitive substring over `senses.sense_text`, capped by `limit`
(default 25).

Latin → English clients typically call `translate(..., lang="la")`, then
`format_english_word_response(latin_word, entries)` (defaults:
`definition_mode="both"`, `include_paradigms=True`). That returns **brief glosses
first**, the **full definition list** below, then **morphology** (with optional
`paradigm` tables) and **connections**. Set `include_paradigms=False` to omit
generated declension/conjugation grids from the payload.

Load a database before calling the service — see [tools/README.md](../tools/README.md).
