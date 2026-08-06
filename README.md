# JSON Lewis & Short

A Latin dictionary in JSON format, based off of the Perseus Project's Lewis and Short XML version.

This project is **not** a mirror of Lewis & Short alone. L&S is the authoritative
base layer (entries, senses, etymology, cross-references). On top of that, the
Translation API adds an **enhancement layer**: structured morphology, generated
paradigms, Logeion/Scriba-friendly layouts, and learner-facing fields that L&S
does not provide out of the box.

Without that layer, repackaging the dictionary adds little; the goal is a tool
that is yours to extend—quick-reference notes, agent-written summaries, and
future teaching aids—while keeping dictionary prose and attribution intact.

| Layer | Source | Role |
| --- | --- | --- |
| **Dictionary core** | Lewis & Short (via Perseus JSON) | Definitions, `main_notes`, Greek links, lemma lines |
| **Enhancements** | This API and schemas | Paradigms, brief gloss ordering, tabs, `summary`, sentence translation (planned) |

Enhancement contracts and conventions: [`json-schemas/README.md`](json-schemas/README.md).

## Loading into a database

`tools/ls_db.py` loads the `ls_*.json` files into SQLite, PostgreSQL or MySQL,
verifies the load is lossless, and then removes the JSON from the repository.
See [tools/README.md](tools/README.md) for the schema and the steps.

## Translation API (boilerplate)

Python + FastAPI. No HTTP routes yet — just config, a database session helper,
and a `translate()` service that looks up Latin or English words and returns
matching entries.

Request/response contracts live under [`json-schemas/`](json-schemas/README.md)
(`requests/` and `responses/` for each `translation_type`).

```
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# load the dictionary once (SQLite, ~74 MB)
python tools/ls_db.py --db sqlite:///lewis_short.db load

# exercise the service without an HTTP server
python -c "
from api.db import db_session
from api.services import translate

with db_session() as db:
    print([e['key'] for e in translate(db, 'amo', lang='la')])
    print([e['key'] for e in translate(db, 'love', lang='en')][:5])
"
```

Optional: point at another database with `LEWIS_SHORT_DATABASE_URL` (same URL
shapes as `tools/ls_db.py`). When routes are added, run with
`uvicorn api.main:app --reload` from the repository root.

## Credits

Text provided by Perseus Digital Library, with funding from The National Endowment for the Humanities.

Original version available for viewing and download at http://www.perseus.tufts.edu/