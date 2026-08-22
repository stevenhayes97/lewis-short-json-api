-- Draft / not created by ls_db.py.
-- Combined curated-layer tables. Load after the live schema:
--
--     sqlite3 /tmp/ls-schema-preview.db < schema/schema.sql
--     sqlite3 /tmp/ls-schema-preview.db < schema/draft/schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS curated_definitions (
    entry_key    TEXT    NOT NULL,
    rank         INTEGER NOT NULL,
    definition   TEXT    NOT NULL,
    needs_review INTEGER NOT NULL DEFAULT 0,
    review_note  TEXT,
    PRIMARY KEY (entry_key, rank),
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key),
    CHECK (rank >= 1 AND rank <= 10)
);

CREATE INDEX IF NOT EXISTS idx_curated_def_rank
    ON curated_definitions (rank);

CREATE TABLE IF NOT EXISTS curated_skips (
    entry_key  TEXT NOT NULL PRIMARY KEY,
    reason     TEXT NOT NULL,
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE TABLE IF NOT EXISTS entry_summaries (
    entry_key  TEXT NOT NULL PRIMARY KEY,
    summary    TEXT NOT NULL,
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE TABLE IF NOT EXISTS example_sentences (
    example_id    INTEGER NOT NULL PRIMARY KEY,
    entry_key     TEXT    NOT NULL,
    ordinal       INTEGER NOT NULL,
    latin_text    TEXT    NOT NULL,
    english_text  TEXT    NOT NULL,
    note          TEXT,
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE INDEX IF NOT EXISTS idx_examples_entry
    ON example_sentences (entry_key, ordinal);

CREATE TABLE IF NOT EXISTS paradigms (
    entry_key      TEXT NOT NULL PRIMARY KEY,
    paradigm_type  TEXT NOT NULL,
    word_stem      TEXT,
    paradigm_json  TEXT NOT NULL,
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);
