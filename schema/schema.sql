-- Prototype / not frozen.
-- Combined live SQLite schema — the four tables tools/ls_db.py actually
-- creates, plus indexes. Foreign keys are declared here for a visual
-- (the live loader enables PRAGMA foreign_keys but does not declare them).
--
--     sqlite3 /tmp/ls-schema-preview.db < schema/schema.sql
--
-- Ids are assigned by the loader, not by AUTOINCREMENT.
-- raw_json is the default; `load --no-raw` omits that column.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- ---------------------------------------------------------------------------
-- entries — one row per headword (~51,596)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS entries (
    entry_key          TEXT    NOT NULL PRIMARY KEY,
    source_file        TEXT    NOT NULL,
    file_index         INTEGER NOT NULL,
    entry_type         TEXT,
    part_of_speech     TEXT,
    title_orthography  TEXT,
    title_genitive     TEXT,
    declension         INTEGER,
    gender             TEXT,
    greek_word         TEXT,
    main_notes         TEXT,
    raw_json           TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_type        ON entries (entry_type);
CREATE INDEX IF NOT EXISTS idx_entries_pos         ON entries (part_of_speech);
CREATE INDEX IF NOT EXISTS idx_entries_decl_gender ON entries (declension, gender);
CREATE INDEX IF NOT EXISTS idx_entries_gender      ON entries (gender);

-- ---------------------------------------------------------------------------
-- entry_forms — alternative spellings (~8,392)
-- form_kind: orthography | genitive
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS entry_forms (
    form_id    INTEGER NOT NULL PRIMARY KEY,
    entry_key  TEXT    NOT NULL,
    form_kind  TEXT    NOT NULL,
    ordinal    INTEGER NOT NULL,
    form_text  TEXT    NOT NULL,
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE INDEX IF NOT EXISTS idx_forms_entry ON entry_forms (entry_key);
CREATE INDEX IF NOT EXISTS idx_forms_text  ON entry_forms (form_text);

-- ---------------------------------------------------------------------------
-- entry_extra — unrecognised JSON fields (empty today)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS entry_extra (
    extra_id    INTEGER NOT NULL PRIMARY KEY,
    entry_key   TEXT    NOT NULL,
    field_name  TEXT    NOT NULL,
    value_json  TEXT,
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE INDEX IF NOT EXISTS idx_extra_entry ON entry_extra (entry_key);

-- ---------------------------------------------------------------------------
-- senses — flattened sense tree (~101,654)
-- ORDER BY sort_key (zero-padded), never by path
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS senses (
    sense_id         INTEGER NOT NULL PRIMARY KEY,
    entry_key        TEXT    NOT NULL,
    parent_sense_id  INTEGER,
    ordinal          INTEGER NOT NULL,
    depth            INTEGER NOT NULL,
    path             TEXT    NOT NULL,
    sort_key         TEXT    NOT NULL,
    sense_text       TEXT,
    FOREIGN KEY (entry_key)       REFERENCES entries (entry_key),
    FOREIGN KEY (parent_sense_id) REFERENCES senses  (sense_id)
);

CREATE INDEX IF NOT EXISTS idx_senses_entry  ON senses (entry_key);
CREATE INDEX IF NOT EXISTS idx_senses_parent ON senses (parent_sense_id);
CREATE INDEX IF NOT EXISTS idx_senses_sort   ON senses (entry_key, sort_key);
