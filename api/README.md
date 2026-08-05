# Translation API

Lightweight FastAPI app that will expose Lewis & Short lookups over HTTP.
This first step wires the non-HTTP pieces only.

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
`format_english_word_response(latin_word, entries, definition_mode="both")`.
That default returns **brief glosses and full definitions** (Logeion-style)
plus **morphology** and **connections** tabs (Scriba-style). Use `brief` or
`full` to omit one side of the definition payload when saving bandwidth.

Load a database before calling the service — see [tools/README.md](../tools/README.md).
