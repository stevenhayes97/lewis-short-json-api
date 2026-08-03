"""Read dictionary entries back out of the database as JSON-ready dicts.

Companion to ls_db.py. That script loads the data; this one reads it. Both
speak plain DB-API 2.0, so the same code works against SQLite, PostgreSQL and
MySQL connections.

    import sqlite3, json
    from lookup import get_entry, get_entries

    con = sqlite3.connect("lewis_short.db")
    json.dumps(get_entry(con, "abacus"), ensure_ascii=False)

Keep `ensure_ascii=False` when serializing: the text is full of macrons and
Greek, and escaping it roughly doubles the payload.

Use `get_entries` for anything returning more than one entry. `get_entry`
costs three queries, so calling it in a loop over 50 search hits is 150 round
trips; `get_entries` answers the same question in three.

If you loaded with raw_json (the ls_db.py default rather than --no-raw), you do
not need any of this for whole-entry fetches -- `SELECT raw_json FROM entries
WHERE entry_key = ?` hands back the response body directly, already serialized.
This module is what you want when that column is absent, or when you need
entries as dicts rather than as text.
"""

SCALARS = (
    "entry_type",
    "part_of_speech",
    "title_orthography",
    "title_genitive",
    "declension",
    "gender",
    "greek_word",
    "main_notes",
)

# entry_forms.form_kind -> the JSON field it came from. The source spells the
# genitive one "alternative_genative"; that typo is preserved on the way out so
# responses match the original files.
FORM_FIELD = {"orthography": "alternative_orthography", "genitive": "alternative_genative"}

# SQLite's default limit on host parameters is 999 on older builds, so batch
# queries are chunked below that.
CHUNK = 500


def _placeholder(con):
    """`?` for SQLite, `%s` for essentially everything else."""
    return "?" if type(con).__module__.split(".")[0] == "sqlite3" else "%s"


def _assemble(key, row, forms, senses):
    """Turn one entry's rows into the dict shape of the original JSON."""
    entry = {"key": key}
    entry.update(dict(zip(SCALARS, row)))

    for form_kind, form_text in forms:
        entry.setdefault(FORM_FIELD[form_kind], []).append(form_text)

    # Rebuild the sense outline: a string is a sense, and a nested list holds
    # the sub-senses of the sense above it. A NULL sense_text marks a
    # structural node that contributes only its children -- see ls_db.py.
    children, text_of = {}, {}
    for sense_id, parent_sense_id, sense_text in senses:
        children.setdefault(parent_sense_id, []).append(sense_id)
        text_of[sense_id] = sense_text

    def branch(parent_sense_id):
        out = []
        for sense_id in children.get(parent_sense_id, []):
            if text_of[sense_id] is not None:
                out.append(text_of[sense_id])
            sub = branch(sense_id)
            if sub:
                out.append(sub)
        return out

    entry["senses"] = branch(None)
    return {name: value for name, value in entry.items() if value is not None}


def get_entry(con, key):
    """Return one entry as a dict, or None if there is no such headword.

    Three queries. Reproduces the original JSON exactly, except that entries
    which omitted `senses` altogether come back with an empty list, so every
    response has the same shape.
    """
    ph = _placeholder(con)
    cur = con.cursor()

    cur.execute("SELECT %s FROM entries WHERE entry_key = %s" % (", ".join(SCALARS), ph), (key,))
    row = cur.fetchone()
    if row is None:
        return None

    cur.execute(
        "SELECT form_kind, form_text FROM entry_forms WHERE entry_key = %s"
        " ORDER BY form_kind, ordinal" % ph,
        (key,),
    )
    forms = cur.fetchall()

    cur.execute(
        "SELECT sense_id, parent_sense_id, sense_text FROM senses WHERE entry_key = %s"
        " ORDER BY sort_key" % ph,
        (key,),
    )
    senses = cur.fetchall()

    return _assemble(key, row, forms, senses)


def get_entries(con, keys):
    """Return {key: entry} for many headwords, in three queries per chunk.

    Missing keys are simply absent from the result. The caller decides the
    output order, which for a search endpoint usually means keeping the order
    the search returned:

        found = get_entries(con, hits)
        [found[k] for k in hits if k in found]
    """
    ph = _placeholder(con)
    keys = list(dict.fromkeys(keys))  # de-duplicate, keep first-seen order
    if not keys:
        return {}

    cur = con.cursor()
    rows, forms, senses = {}, {}, {}

    for start in range(0, len(keys), CHUNK):
        chunk = keys[start : start + CHUNK]
        marks = ", ".join([ph] * len(chunk))

        cur.execute(
            "SELECT entry_key, %s FROM entries WHERE entry_key IN (%s)" % (", ".join(SCALARS), marks),
            tuple(chunk),
        )
        for row in cur.fetchall():
            rows[row[0]] = row[1:]

        cur.execute(
            "SELECT entry_key, form_kind, form_text FROM entry_forms"
            " WHERE entry_key IN (%s) ORDER BY entry_key, form_kind, ordinal" % marks,
            tuple(chunk),
        )
        for entry_key, form_kind, form_text in cur.fetchall():
            forms.setdefault(entry_key, []).append((form_kind, form_text))

        cur.execute(
            "SELECT entry_key, sense_id, parent_sense_id, sense_text FROM senses"
            " WHERE entry_key IN (%s) ORDER BY entry_key, sort_key" % marks,
            tuple(chunk),
        )
        for entry_key, sense_id, parent_sense_id, sense_text in cur.fetchall():
            senses.setdefault(entry_key, []).append((sense_id, parent_sense_id, sense_text))

    return {
        key: _assemble(key, row, forms.get(key, ()), senses.get(key, ()))
        for key, row in rows.items()
    }
