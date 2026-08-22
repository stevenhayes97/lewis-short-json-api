-- Prototype / not frozen.
-- One row per Lewis & Short headword (~51,596).
-- Created by: tools/ls_db.py create_schema()
--
-- entry_key is the original JSON `key` and is unique across all 25 source
-- files, so it is the primary key everywhere else too. Homographs keep their
-- digit: gero1 vs gero2.

CREATE TABLE IF NOT EXISTS entries (
    entry_key          TEXT    NOT NULL PRIMARY KEY,  -- e.g. abacus, gero1
    source_file        TEXT    NOT NULL,              -- ls_A.json … ls_Z.json
    file_index         INTEGER NOT NULL,              -- position inside that file

    entry_type         TEXT,                          -- main, greek, hapax, gloss, spur, foreign
    part_of_speech     TEXT,                          -- free text (~197 values), often NULL
    title_orthography  TEXT,                          -- headword as printed (macrons, etc.)
    title_genitive     TEXT,                          -- genitive ending or full genitive
    declension         INTEGER,                       -- 1–4 in the source; NULL if not declined
    gender             TEXT,                          -- M, F, N, Comm, compounds like M.f
    greek_word         TEXT,                          -- Greek etymon, when the entry gives one
    main_notes         TEXT,                          -- leading prose (etymology, lemma line)

    -- Original JSON object, verbatim. Omitted if the DB was loaded with --no-raw.
    -- Whole-entry API fetches can return this string and skip reassembly.
    raw_json           TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_type        ON entries (entry_type);
CREATE INDEX IF NOT EXISTS idx_entries_pos         ON entries (part_of_speech);
CREATE INDEX IF NOT EXISTS idx_entries_decl_gender ON entries (declension, gender);
CREATE INDEX IF NOT EXISTS idx_entries_gender      ON entries (gender);

-- Visual aid only — the live loader does not declare this uniqueness.
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_entries_file_pos
--     ON entries (source_file, file_index);
