-- Prototype / not frozen.
-- The curated layer -- the tables tools/curated_db.py creates on top of the
-- live schema. Load after schema.sql:
--
--     sqlite3 /tmp/ls-schema-preview.db < schema/schema.sql
--     sqlite3 /tmp/ls-schema-preview.db < schema/curated.sql
--
-- The text files are the source of truth; `curated_db.py load` drops and
-- rebuilds all of this from them on every run.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- curated_definitions — definitions/<LETTER>.txt, one row per line (~31,500)
-- key | rank | definition. Rank 1 is the one-word gloss, 2 optional, 3+ phrases.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS curated_definitions (
    entry_key    TEXT    NOT NULL,
    rank         INTEGER NOT NULL,
    definition   TEXT    NOT NULL,
    review_note  TEXT,     -- the word's `# review:` reason, on its rank 1-2 lines
    PRIMARY KEY (entry_key, rank),
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key),
    CHECK (rank BETWEEN 1 AND 10)
);

CREATE INDEX IF NOT EXISTS idx_curated_def_rank ON curated_definitions (rank);

-- ---------------------------------------------------------------------------
-- curated_sentences — sentences/<LETTER>.txt, one sentence per word (~8,200)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS curated_sentences (
    entry_key   TEXT NOT NULL PRIMARY KEY,
    latin       TEXT NOT NULL,   -- no macrons, j spelling, no final full stop
    english     TEXT NOT NULL,
    third_note  TEXT,            -- the `# third:` reason when the verb is third person
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

-- ---------------------------------------------------------------------------
-- curated_skips — `# skip:` lines from both layers
-- No foreign key: a skip records a decision, not content.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS curated_skips (
    entry_key  TEXT NOT NULL,
    layer      TEXT NOT NULL,    -- definitions | sentences
    reason     TEXT,
    PRIMARY KEY (entry_key, layer),
    CHECK (layer IN ('definitions', 'sentences'))
);

-- ---------------------------------------------------------------------------
-- curated_tags — definitions/tags.txt, the image tag shown beside a word
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS curated_tags (
    entry_key  TEXT NOT NULL PRIMARY KEY,
    tag        TEXT NOT NULL,    -- one of TAGS in tools/definitions.py
    FOREIGN KEY (entry_key) REFERENCES entries (entry_key)
);

CREATE INDEX IF NOT EXISTS idx_curated_tags_tag ON curated_tags (tag);

-- ---------------------------------------------------------------------------
-- learner_entries — one flat row per word with a curated definition
-- ---------------------------------------------------------------------------

CREATE VIEW IF NOT EXISTS learner_entries AS
SELECT e.entry_key,
       e.title_orthography,
       e.part_of_speech,
       d1.definition AS gloss_1,
       d2.definition AS gloss_2,
       (SELECT COUNT(*) FROM curated_definitions d WHERE d.entry_key = e.entry_key) AS rank_count,
       s.latin AS sentence_latin,
       s.english AS sentence_english,
       g.tag
FROM entries e
JOIN curated_definitions d1 ON d1.entry_key = e.entry_key AND d1.rank = 1
LEFT JOIN curated_definitions d2 ON d2.entry_key = e.entry_key AND d2.rank = 2
LEFT JOIN curated_sentences s ON s.entry_key = e.entry_key
LEFT JOIN curated_tags g ON g.entry_key = e.entry_key;
