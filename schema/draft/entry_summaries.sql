-- Draft / not created by ls_db.py.
-- Learner quick-reference blurb on a word result (API field `summary`).
--
-- Distinct from entries.main_notes / connections.notes, which carry the
-- full Lewis & Short prose. Intended content:
--   prepositions — which noun case they take (and sense splits by case)
--   verbs        — which case(s) objects or complements use
-- Empty string in the API until filled; this table would store only rows
-- that actually have a summary.

CREATE TABLE IF NOT EXISTS entry_summaries (
    entry_key  TEXT NOT NULL PRIMARY KEY,
    summary    TEXT NOT NULL,

    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);
