# SQLite schema sketches

**Status: prototype / not frozen.**

These files are a readable picture of the tables `tools/ls_db.py` creates
and `tools/curated_db.py` create, plus two drafted tables nothing builds yet.
They are for looking at — in an editor, a SQL GUI, or a diagram tool — not
a contract the loader is required to follow.

- Prefer evolving the SQL when the product shape changes.
- The live schema is still the Python: `create_schema` in `tools/ls_db.py` and
  `tools/curated_db.py`.
- Do not treat column names, foreign keys, or the draft tables as locked.

```
schema/
  schema.sql              all four L&S tables + indexes, one file
  entries.sql
  entry_forms.sql
  entry_extra.sql
  senses.sql
  curated.sql             curated layer, created by tools/curated_db.py
  draft/                  not created by anything yet
    entry_summaries.sql
    paradigms.sql
    schema.sql            both draft tables, one file
```

Load the live sketch into a throwaway database:

```
sqlite3 /tmp/ls-schema-preview.db < schema/schema.sql
```

`curated.sql` and the draft files assume the L&S tables already exist (they
reference `entries.entry_key`). Load them after `schema.sql`.

## What is live vs drafted

| Table | Status | Source |
| --- | --- | --- |
| `entries` | created by `ls_db.py load` | `ls_*.json` scalars + optional `raw_json` |
| `entry_forms` | created by `ls_db.py load` | `alternative_orthography` / `alternative_genative` |
| `entry_extra` | created by `ls_db.py load` | unrecognised JSON fields (empty today) |
| `senses` | created by `ls_db.py load` | nested `senses` tree, flattened |
| `curated_definitions` | created by `curated_db.py load` | `definitions/<LETTER>.txt` |
| `curated_sentences` | created by `curated_db.py load` | `sentences/<LETTER>.txt` |
| `curated_skips` | created by `curated_db.py load` | `# skip:` lines in both sets of files |
| `curated_tags` | created by `curated_db.py load` | `definitions/tags.txt` |
| `learner_entries` | view, `curated_db.py load` | one flat row per defined word |
| `entry_summaries` | draft | API `summary` field (case governance, etc.) |
| `paradigms` | draft | cached declension / conjugation grids |

## Differences from the live loader

The sketches add a few things the Python DDL does not, because they make the
relationships visible:

- `FOREIGN KEY` clauses (the loader sets `PRAGMA foreign_keys = ON` but does
  not declare the keys)
- `UNIQUE` / `CHECK` hints where the data already behaves that way
- comments on every column

Ids (`form_id`, `extra_id`, `sense_id`) are assigned by the loader, not by
`AUTOINCREMENT`. The sketches keep that: `INTEGER PRIMARY KEY` with no
autoincrement clause.

`raw_json` is included. `load --no-raw` omits that column.

## Entity picture (live tables)

```mermaid
erDiagram
    entries ||--o{ entry_forms : "has forms"
    entries ||--o{ entry_extra : "has extras"
    entries ||--o{ senses : "has senses"
    senses ||--o{ senses : "parent_sense_id"

    entries {
        TEXT entry_key PK
        TEXT source_file
        INTEGER file_index
        TEXT entry_type
        TEXT part_of_speech
        TEXT title_orthography
        TEXT title_genitive
        INTEGER declension
        TEXT gender
        TEXT greek_word
        TEXT main_notes
        TEXT raw_json
    }

    entry_forms {
        INTEGER form_id PK
        TEXT entry_key FK
        TEXT form_kind
        INTEGER ordinal
        TEXT form_text
    }

    entry_extra {
        INTEGER extra_id PK
        TEXT entry_key FK
        TEXT field_name
        TEXT value_json
    }

    senses {
        INTEGER sense_id PK
        TEXT entry_key FK
        INTEGER parent_sense_id FK
        INTEGER ordinal
        INTEGER depth
        TEXT path
        TEXT sort_key
        TEXT sense_text
    }
```

## Entity picture (curated layer and drafts)

The curated tables hang off `entries` the same way. `curated_db.py` builds
them; `entry_summaries` and `paradigms` are still drafts.

```mermaid
erDiagram
    entries ||--o{ curated_definitions : "has glosses"
    entries ||--o| curated_sentences : "has example"
    entries ||--o| curated_tags : "may have image tag"
    entries ||--o| entry_summaries : "has summary (draft)"
    entries ||--o| paradigms : "may cache paradigm (draft)"

    curated_definitions {
        TEXT entry_key PK
        INTEGER rank PK
        TEXT definition
        TEXT review_note
    }

    curated_sentences {
        TEXT entry_key PK
        TEXT latin
        TEXT english
        TEXT third_note
    }

    curated_skips {
        TEXT entry_key PK
        TEXT layer PK
        TEXT reason
    }

    curated_tags {
        TEXT entry_key PK
        TEXT tag
    }

    entry_summaries {
        TEXT entry_key PK
        TEXT summary
    }

    paradigms {
        TEXT entry_key PK
        TEXT paradigm_type
        TEXT word_stem
        TEXT paradigm_json
    }
```
