-- Prototype / not frozen.
-- Nested sense outline, flattened (~101,654 rows).
-- Created by: tools/ls_db.py create_schema()
--
-- In the source JSON a string is a sense and a nested list holds the
-- sub-senses of the sense above it. That tree becomes rows:
--
--   parent_sense_id  NULL at the top level; otherwise the parent row
--   ordinal          order among siblings
--   depth            0–3 in this data
--   path             display / cite form:  4.1.1
--   sort_key         zero-padded:          04.01.01
--
-- Always ORDER BY sort_key, never by path. Some entries run past nine
-- senses at one level (ab reaches 22); a string sort of path puts 10
-- ahead of 2.
--
-- Twenty-nine rows have NULL sense_text. Those are structural: a
-- sub-sense list appeared with no parent sense string above it, and a
-- NULL-text node preserves that shape so the data round-trips.

CREATE TABLE IF NOT EXISTS senses (
    sense_id         INTEGER NOT NULL PRIMARY KEY,  -- assigned by the loader, not AUTOINCREMENT
    entry_key        TEXT    NOT NULL,
    parent_sense_id  INTEGER,                       -- NULL = top-level sense
    ordinal          INTEGER NOT NULL,
    depth            INTEGER NOT NULL,
    path             TEXT    NOT NULL,
    sort_key         TEXT    NOT NULL,
    sense_text       TEXT,                          -- NULL = structural grouping node

    FOREIGN KEY (entry_key)       REFERENCES entries (entry_key),
    FOREIGN KEY (parent_sense_id) REFERENCES senses  (sense_id)
);

CREATE INDEX IF NOT EXISTS idx_senses_entry  ON senses (entry_key);
CREATE INDEX IF NOT EXISTS idx_senses_parent ON senses (parent_sense_id);
CREATE INDEX IF NOT EXISTS idx_senses_sort   ON senses (entry_key, sort_key);
