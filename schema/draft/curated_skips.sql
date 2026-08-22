-- Draft / not created by ls_db.py.
-- Headwords the curated-definitions pass explicitly skipped.
--
-- Recorded in definitions/<LETTER>.txt as:
--   # skip: galbanum a resin, one citation, nothing to teach
--
-- tools/definitions.py treats a skip the same as "already written" so the
-- next-chunk picker does not offer the word again.

CREATE TABLE IF NOT EXISTS curated_skips (
    entry_key  TEXT NOT NULL PRIMARY KEY,
    reason     TEXT NOT NULL,

    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);
