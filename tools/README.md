# Moving the dictionary into a database

`ls_db.py` loads the 25 `ls_*.json` files into a relational database, checks the
load is lossless, and then removes the JSON from the repository.

Nothing here runs automatically. Run the steps yourself, in order, and stop if
any of them complains.

## Requirements

Python 3.7 or newer. Nothing else, if you use SQLite.

| Target | Extra install |
| --- | --- |
| SQLite | none — it ships with Python |
| PostgreSQL | `pip install "psycopg[binary]"` |
| MySQL / MariaDB | `pip install PyMySQL` |

## The three steps

Run these from the repository root.

```
python tools/ls_db.py --db sqlite:///lewis_short.db load
python tools/ls_db.py --db sqlite:///lewis_short.db verify
python tools/ls_db.py --db sqlite:///lewis_short.db wipe
```

`load` builds the schema and inserts everything (about 5 seconds, ~74 MB
SQLite file). `verify` rebuilds the JSON out of the database and diffs it
against the files on disk. `wipe` re-runs that verification and, only if it
passes, `git rm`s the 25 JSON files — then stops, so you review the deletion
and commit it yourself. Nothing is committed or pushed for you.

`wipe` prompts for confirmation; pass `--yes` to skip the prompt.

### Database URLs

```
sqlite:///lewis_short.db                    relative path (three slashes)
sqlite:////srv/data/lewis_short.db          absolute path (four slashes)
C:\data\lewis_short.db                      a plain path works too
postgresql://user:password@localhost/lewis_short
mysql://user:password@localhost/lewis_short
```

On Windows, `py tools\ls_db.py ...` works if `python` is not on your PATH.

## Schema

Four tables. `entry_key` is the original JSON `key`, and it is unique across all
25 files, so it serves as the primary key throughout.

**`entries`** — one row per headword (51,596).

| Column | Notes |
| --- | --- |
| `entry_key` | primary key, e.g. `abacus` |
| `source_file`, `file_index` | which JSON file it came from, and its position in it |
| `entry_type` | `main`, `greek`, `hapax`, `gloss`, `spur`, `foreign` |
| `part_of_speech` | free text, 197 distinct values, often NULL |
| `title_orthography`, `title_genitive` | headword and genitive as printed |
| `declension` | 1–4, NULL for anything not declined |
| `gender` | `M`, `F`, `N`, `Comm`, and compounds like `M.f` |
| `greek_word` | Greek etymon, when the entry gives one |
| `main_notes` | the entry's leading prose |
| `raw_json` | the original JSON object, verbatim |

Indexed on `entry_type`, `part_of_speech`, `gender`, and `(declension, gender)`.

**`senses`** — 101,654 rows, the nested sense outline flattened.

`parent_sense_id` is NULL at the top level; `ordinal` gives the order among
siblings; `depth` runs 0–3. Join on `parent_sense_id` to walk the tree.

Position comes in two forms. `path` reads naturally — `4.1.1` — and is what you
want to display or cite. `sort_key` zero-pads every segment — `04.01.01` — and
is what you want in `ORDER BY`. **Always order by `sort_key`, never by `path`.**
Some entries run past nine senses at one level (`ab` reaches 22), and a string
sort of `path` puts sense 10 ahead of sense 2.

Twenty-nine rows have a NULL `sense_text`. Those are structural: in the source
JSON a few sub-sense lists appear with no parent sense string above them, and a
NULL-text node preserves that shape so the data round-trips exactly.

**`entry_forms`** — 8,392 alternative spellings, one per row, `form_kind` being
`orthography` or `genitive`. (The source spells the latter field
`alternative_genative`; the database uses the corrected name.)

**`entry_extra`** — empty today. Any JSON field the script does not recognise
lands here as `field_name` / `value_json` rather than being silently dropped, so
a future change to the source data cannot lose anything.

### Example queries

```sql
-- every third-declension feminine noun
SELECT entry_key, title_orthography, title_genitive
FROM entries
WHERE declension = 3 AND gender = 'F';

-- an entry with its senses in reading order
SELECT s.path, s.sense_text
FROM senses s
WHERE s.entry_key = 'amo'
ORDER BY s.sort_key;

-- headwords whose senses mention war
SELECT DISTINCT e.entry_key, e.title_orthography
FROM entries e
JOIN senses s ON s.entry_key = e.entry_key
WHERE s.sense_text LIKE '%war%';

-- look a word up by an alternative spelling
SELECT e.entry_key, f.form_text
FROM entry_forms f
JOIN entries e ON e.entry_key = f.entry_key
WHERE f.form_text = 'ăbax';
```

## Performance: should this have been a JSON column?

Short answer: it already is one, alongside the tables. `raw_json` holds each
entry as JSON, so if your API serves whole entries you can return that string
directly and skip reassembly entirely. You do not have to choose.

Measured on this data — 51,596 entries, best of several warm runs.

**Fetching one whole entry.** On SQLite, reading `raw_json` and returning it
is 5.8x faster than rebuilding the entry from the tables, because there is no
round trip to hide the work behind:

| | ms/entry |
| --- | --- |
| `raw_json`, returned as-is | 0.006 |
| `raw_json`, parsed into a dict | 0.012 |
| rebuilt from the normalized tables | 0.038 |

On PostgreSQL the same three land at 0.092 / 0.108 / 0.118 ms. The gap nearly
vanishes: the client round trip dominates, so the storage format barely
matters. Note the middle column — a `jsonb` column measured *slower* than
`text` for plain fetching (0.108 vs 0.092), because Postgres re-serializes
`jsonb` on output. `jsonb` earns its keep only when you query inside it.

**Filtering.** With the right index, typed columns and `jsonb` tie:

| | ms/query |
| --- | --- |
| typed columns, `(declension, gender)` index | 3.15 |
| `jsonb` with a matching expression index | 3.14 |
| `jsonb` with a GIN index | 6.21 |
| `jsonb`, no index | 48.0 |

The tie holds only if you build an expression index per field you filter on.
Miss one and you are at the bottom row.

**Searching sense text** is where the normalized tables clearly win —
substring search over `senses` is 51 ms against 239 ms for scanning whole JSON
documents as text, because the sense rows are far smaller than the documents
containing them.

**What `raw_json` costs.** It inflates the `entries` heap from 5 MB to 24 MB on
PostgreSQL, which makes any sequential scan of that table roughly 50% slower.
If you never fetch whole entries, `--no-raw` is the better trade.

So: keep both if you serve whole entries and also want to query them, which is
the normal case for an API. Use `--no-raw` if entries are only ever a query
result, never a response body.

## Getting the JSON back

`raw_json` holds each entry exactly as it appeared, so the files can be
regenerated at any time:

```
python tools/ls_db.py --db sqlite:///lewis_short.db export --out-dir export --from-raw
```

This has been checked: the exported files parse identically to the originals,
entry for entry, across all 25 files. Without `--from-raw` the export is rebuilt
from the normalized tables instead, which is the stronger test of the schema —
that is what `verify` compares.

Pass `--no-raw` to `load` if you would rather not store the duplicate copy. It
halves the database to about 37 MB and gives up byte-exact restore; the
normalized tables still round-trip.

## Other options

| Option | Effect |
| --- | --- |
| `--recreate` | drop and rebuild the tables (`load` refuses to run against a non-empty database otherwise) |
| `--no-raw` | skip the `raw_json` column |
| `--batch-size N` | rows per `executemany`, default 1000 |
| `--keep-local` | `wipe` untracks the files but leaves them on disk |
| `--skip-verify` | `wipe` without checking the database first — not recommended |
| `--source-dir`, `--pattern` | point at a different directory or glob |

## One thing `wipe` cannot do

Deleting the files removes them from the working tree and from future commits,
but every past commit still contains them, so a fresh `git clone` downloads all
74 MB regardless. Only rewriting history (`git filter-repo --path-glob 'ls_*.json'
--invert-paths`) actually shrinks the clone, and that rewrites every commit hash
— which breaks existing clones and forks. Worth doing deliberately and
separately, if at all.

## What was tested

The load, verify, export and wipe paths were each run end to end against SQLite
and PostgreSQL 16, on all 51,596 entries, with the export confirmed identical to
the source files. The benchmark numbers above come from the same two engines on
the same data. The MySQL path is written to the same interface but was not
exercised against a live server.
