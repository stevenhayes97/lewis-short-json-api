-- Prototype / not frozen.
-- Overflow for JSON fields the loader does not recognise.
-- Created by: tools/ls_db.py create_schema()
--
-- Empty today. Anything the source grows later lands here as field_name /
-- value_json rather than being dropped, so a future change cannot lose data.

CREATE TABLE IF NOT EXISTS entry_extra (
    extra_id    INTEGER NOT NULL PRIMARY KEY,  -- assigned by the loader, not AUTOINCREMENT
    entry_key   TEXT    NOT NULL,
    field_name  TEXT    NOT NULL,              -- the unknown JSON key
    value_json  TEXT,                          -- that field's value, JSON-encoded

    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE INDEX IF NOT EXISTS idx_extra_entry ON entry_extra (entry_key);
