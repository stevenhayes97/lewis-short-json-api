# JSON Lewis & Short

A Latin dictionary API and data pipeline grounded in the Perseus Project's Lewis
and Short XML, aimed at building a **learner-first dictionary of your own**—not
a bare mirror of L&S.

Lewis & Short remains the scholarly source of truth (senses, etymology,
cross-references, attribution). It is dense and citation-heavy, so the product
vision treats it as a **reference layer**, alongside tools like Logeion, rather
than as the primary reading experience. Curated, agent-assisted content sits on
top: clearer summaries, paradigms, and examples you control.

## Entry vision

An entry page should read top-to-bottom like this:

1. **Summarized definition** — short, ordered glosses/senses written for lookup
   and learners (drafted with L&S, Logeion, and similar sources as references)
2. **Declension / conjugation tables** — when the lemma calls for them
3. **Example sentences** — Latin examples (with English) that illustrate real use
4. **Full Lewis & Short** — the complete L&S material at the bottom for scholarly
   and academic use, kept in one place when someone wants the original prose

That order keeps teaching and quick reference first; the archival dictionary
stays available without dominating the page.

| Layer | Source | Role |
| --- | --- | --- |
| **Scholarly core** | Lewis & Short (via Perseus JSON) | Full definitions, `main_notes`, Greek links, lemma lines—footer / deep dive |
| **Curated entry** | This project (rules, agents, editorial review) | Summarized definition, paradigms, example sentences, learner notes (`summary`, etc.) |

Draft API shapes (WIP, still evolving) live under
[`json-schemas/README.md`](json-schemas/README.md).

## Loading into a database

`tools/ls_db.py` loads the `ls_*.json` files into SQLite, PostgreSQL or MySQL,
verifies the load is lossless, and then removes the JSON from the repository.
See [tools/README.md](tools/README.md) for the schema and the steps.

## Translation API (boilerplate)

Python + FastAPI. No HTTP routes yet — just config, a database session helper,
and a `translate()` service that looks up Latin or English words and returns
matching entries.

WIP request/response drafts live under [`json-schemas/`](json-schemas/README.md)
(`requests/` and `responses/` for each `translation_type`). Shapes may change
freely until an explicit 1.0 freeze — see that README’s status note.

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
