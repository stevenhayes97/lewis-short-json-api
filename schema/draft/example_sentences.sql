-- Draft / not created by ls_db.py.
-- Latin + English examples on the entry page (product vision item 3).
--
-- Not Lewis & Short citations — those stay in senses / main_notes.
-- These would be curated learner sentences, one or more per headword.

CREATE TABLE IF NOT EXISTS example_sentences (
    example_id    INTEGER NOT NULL PRIMARY KEY,
    entry_key     TEXT    NOT NULL,
    ordinal       INTEGER NOT NULL,   -- display order for that entry
    latin_text    TEXT    NOT NULL,   -- j-convention, matching the keys (injuria, jus)
    english_text  TEXT    NOT NULL,
    note          TEXT,               -- optional construction hint

    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE INDEX IF NOT EXISTS idx_examples_entry
    ON example_sentences (entry_key, ordinal);

-- Example shape (not loaded):
--   gaudeo / 1 / gaudere victoria / to delight in the victory
--   gero1  / 1 / bellum gerere cum aliquo / to make war on someone
