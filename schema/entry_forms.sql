-- Prototype / not frozen.
-- Alternative spellings (~8,392 rows). One row per form.
-- Created by: tools/ls_db.py create_schema()
--
-- form_kind is the corrected name:
--   orthography  <- JSON field alternative_orthography
--   genitive     <- JSON field alternative_genative  (source typo kept on export)

CREATE TABLE IF NOT EXISTS entry_forms (
    form_id    INTEGER NOT NULL PRIMARY KEY,  -- assigned by the loader, not AUTOINCREMENT
    entry_key  TEXT    NOT NULL,
    form_kind  TEXT    NOT NULL,              -- 'orthography' | 'genitive'
    ordinal    INTEGER NOT NULL,              -- 1-based order inside that kind
    form_text  TEXT    NOT NULL,              -- e.g. ăbax

    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE INDEX IF NOT EXISTS idx_forms_entry ON entry_forms (entry_key);
CREATE INDEX IF NOT EXISTS idx_forms_text  ON entry_forms (form_text);

-- Visual aid only — the live loader does not declare this CHECK.
-- CHECK (form_kind IN ('orthography', 'genitive'))
