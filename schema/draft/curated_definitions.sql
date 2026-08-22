-- Draft / not created by ls_db.py.
-- Ranked learner glosses from definitions/<LETTER>.txt.
--
-- Line format:  key | rank | simplified modern English definition
-- Rank 1 is the one-word gloss a student meets first. Rank 2 is optional
-- (a second distinct core meaning). Ranks 3+ are full phrases.
-- A 1 → 3 jump is legal; any other gap is not. Cap is 10 ranks per word.

CREATE TABLE IF NOT EXISTS curated_definitions (
    entry_key    TEXT    NOT NULL,
    rank         INTEGER NOT NULL,
    definition   TEXT    NOT NULL,
    needs_review INTEGER NOT NULL DEFAULT 0,  -- 1 when the file had a # review: line
    review_note  TEXT,                        -- why the short form did not fit cleanly

    PRIMARY KEY (entry_key, rank),
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key),
    CHECK (rank >= 1 AND rank <= 10)
);

CREATE INDEX IF NOT EXISTS idx_curated_def_rank
    ON curated_definitions (rank);

-- Example shape (not loaded):
--   gaudeo | 1 | rejoice
--   gaudeo | 2 | delight
--   gaudeo | 3 | to be glad, feel joy inwardly, as against laetor …
