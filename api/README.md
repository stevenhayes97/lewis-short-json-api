# Translation API

Lightweight FastAPI app that will expose Lewis & Short lookups over HTTP.
This first step wires the non-HTTP pieces only.

| Module | Role |
| --- | --- |
| `main.py` | FastAPI app object — **no routes yet** |
| `config.py` | `LEWIS_SHORT_DATABASE_URL` (default `sqlite:///lewis_short.db`) |
| `db.py` | context-managed connection via `tools.ls_db.connect` |
| `services/translate.py` | `translate(db, word, lang="la"|"en", definition_mode="full"|"simplified")` → list of entry dicts |

`translate` reuses `tools.lookup.get_entries` so response shapes match the
original JSON. Latin search is an exact, case-insensitive match on
`entry_key`, `title_orthography`, or `entry_forms.form_text`. English search
is a case-insensitive substring over `senses.sense_text`, capped by `limit`
(default 25).

For Latin → English use cases, pass `definition_mode="simplified"` to cap each
entry at three top-level senses (see `json-schemas/common/definition_mode.json`).
Omit the flag or use `"full"` for the complete sense tree.

Load a database before calling the service — see [tools/README.md](../tools/README.md).
