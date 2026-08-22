-- Draft / not created by ls_db.py.
-- Cached declension / conjugation grids for morphology.paradigm.
--
-- Today api/services/paradigm.py is a stub (returns None). Tables are
-- generated at request time when this lands; this sketch is only if we
-- decide to persist them. paradigm_json would match
-- json-schemas/common/paradigm_tables.json.

CREATE TABLE IF NOT EXISTS paradigms (
    entry_key       TEXT NOT NULL PRIMARY KEY,
    paradigm_type   TEXT NOT NULL,   -- noun | verb | adjective | pronoun | participle | unknown
    word_stem       TEXT,
    paradigm_json   TEXT NOT NULL,   -- full grid payload

    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);
