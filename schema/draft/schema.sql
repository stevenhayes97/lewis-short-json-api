-- Draft / not created by ls_db.py.
-- Tables not built yet. Load after the live schema:
--
--     sqlite3 /tmp/ls-schema-preview.db < schema/schema.sql
--     sqlite3 /tmp/ls-schema-preview.db < schema/draft/schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS entry_summaries (
    entry_key  TEXT NOT NULL PRIMARY KEY,
    summary    TEXT NOT NULL,
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE TABLE IF NOT EXISTS paradigms (
    entry_key      TEXT NOT NULL PRIMARY KEY,
    paradigm_type  TEXT NOT NULL,
    word_stem      TEXT,
    paradigm_json  TEXT NOT NULL,
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);
