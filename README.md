# JSON Lewis & Short
A Latin dictionary in JSON format, based off of the Perseus Project's Lewis and Short XML version.

## Loading into a database

`tools/ls_db.py` loads the `ls_*.json` files into SQLite, PostgreSQL or MySQL,
verifies the load is lossless, and then removes the JSON from the repository.
See [tools/README.md](tools/README.md) for the schema and the steps.

## Translation API (boilerplate)

Python + FastAPI. No HTTP routes yet — just config, a database session helper,
and a `translate()` service that looks up Latin or English words and returns
matching entries.

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