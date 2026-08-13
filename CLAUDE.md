# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this repo is

A learner-first Latin dictionary built on the Perseus Project's Lewis & Short
XML. `README.md` has the product vision; the short version is that L&S is the
scholarly reference layer, and a curated layer of clearer, learner-facing
material sits on top of it.

| Path | What it holds |
| --- | --- |
| `ls_A.json` … `ls_Z.json` | the L&S source data, one file per letter, a top-level JSON array of entry objects |
| `definitions/<LETTER>.txt` | **the curated definitions** — the recurring task below |
| `tools/definitions.py` | chunk helper for that task (`next`, `check`, `status`) |
| `tools/ls_db.py`, `tools/lookup.py` | load the JSON into SQL, read it back out — see `tools/README.md` |
| `json-schemas/` | draft API request/response shapes, still evolving |
| `api/` | FastAPI boilerplate, no routes yet |

Source entry shape: `key`, `entry_type`, `part_of_speech`, `main_notes`, and
`senses` — a tree where a string is a sense and a nested list holds the
sub-senses of the sense above it.

---

# Recurring task: writing curated definitions

Turning L&S's dense, citation-heavy prose into short ranked definitions a
student can actually use. **This is done in chunks of ~10 words at a time**,
and every chunk follows the same loop.

## The loop

```
python tools/definitions.py next G -n 10 --show   # 1. what to write, with its source senses
                                                  # 2. write the lines into definitions/G.txt
python tools/definitions.py check G               # 3. must pass before committing
git add definitions/G.txt && git commit           # 4. one commit per chunk
```

`next` computes the words for you, so chunks are deterministic and resumable —
it lists eligible words not yet written, alphabetically. Never hand-pick words
outside that list; if a word it offers is not worth defining, record it in the
file rather than silently passing over it:

```
# skip: galbanum a resin, one citation, nothing to teach
```

`status` shows coverage per letter when you want the wider picture.

## Line format

Pipe-delimited, because definitions contain commas:

```
key | rank | simplified modern English definition
```

- **key** — the `key` from the JSON object, **verbatim**. Homographs keep their
  digit: `gero1`, not `gero`. That is what joins a line back to its entry.
- **rank** — an integer from 1. Rank 1 is the sense a student meets most often
  and should learn first. **Rank by learner utility and real frequency in
  classical texts, not by L&S's own ordering** — L&S leads with etymology and
  archaic citations, which is the opposite of what a learner needs first.
- **definition** — plain modern English.

Each file opens with two `#` comment lines (format legend, source note). Lines
are grouped by key, ranks ascending, keys in alphabetical order — `check`
enforces all three.

## The rank contract

This is the part that matters most, and the part most easily got wrong.

| Rank | What goes there |
| --- | --- |
| **1** | **One word.** The bare memorizable gloss, nothing else: `gladius \| 1 \| sword`. Verbs take the plain English infinitive without "to": `gero1 \| 1 \| carry`. |
| **2** | **One word, and only if it earns it** — a second, genuinely *distinct* core meaning, not a near-synonym of rank 1. `gaudeo` earns one ("rejoice", then "delight"); `gladius` does not, since "blade" only restates "sword". |
| **3+** | **Full phrases.** The broadened senses: transferred and figurative uses, idioms, and construction hints where the construction is the actual difficulty. |

Ranks 1 and 2 are shown together in their own section on the entry page, with
no sentence around them to lean on, so each has to read correctly alone.

**Accuracy first, brevity second.** One word is the target, but two or three
are right whenever one word would only approximate — `check` fails at four.
Never sacrifice a real definition to keep the count at one: `adnepos` is a
great-great-great-grandson, not a "descendant"; `acervatim` is `in heaps`, not
"wholesale"; `adusque` is `as far as`, not "unto". Those three were one-word
glosses that told a learner something vaguer than the truth.

Two tests catch most cases:

- **Part of speech.** An adjective glossed with a bare noun reads as a noun —
  `aestivus | 1 | of summer`, not `summer`, since `aestas` is the noun and
  `aestivo` the verb. A verb needs a verb: `aestivo | 1 | spend the summer`,
  `absum | 1 | be absent`. Verbs still drop the "to".
- **Words a shared gloss would blur.** `accolo` (of people) and `adjaceo` (of
  places) were both "adjoin"; they are now `dwell near` and `lie near`.
  `albeo`/`albico` are stative and `albesco` inchoative: `be white` against
  `turn white`.

About 6% of the first 410 words use more than one word. A chunk running far
above that is padding; far below it is probably forcing single words that do
not fit.

An uncommon English word is fine when it is the exact one — `aedilicius | 1 |
aedilician` and `admirabilitas | 1 | wonderfulness` are deliberate. The rule
is against *vagueness*, not against precision that happens to be unfamiliar.

Rank 2 is the only rank that may be skipped — a `1 → 3` jump is legal, any
other gap is an error. Cap is 10 ranks per word; most words want 4–8, and a
narrow word wanting only 3 should have only 3. Padding out to 10 is worse than
stopping early.

## Writing the English

- **Drop the apparatus.** No citations (`Cic. Off. 1, 10`), no L&S shorthand
  (`v. a.`, `syn.`, `post-Aug.`, `Absol.`), no macrons in the definition text.
- **Aggregate, don't transcribe.** L&S is the grounding, but write from the
  wider picture of classical usage — the way a good student dictionary would
  put it. Collapse L&S's fine sub-branches into the senses a learner actually
  needs, and drop citation-only curiosities entirely.
- **Give constructions where they are the difficulty.** `gaudeo` + ablative,
  `gratia` after a genitive meaning "for the sake of", `se gerere` + adverb.
  Illustrate with a bare Latin phrase and its English, no citation:
  `bellum gerere cum aliquo, to make war on someone`.
- **Never invent a sense.** Everything must be defensible against the entry.
  Distilling and reordering is the job; adding meanings is not.
- Keep the register plain and modern. "unwholesome", not "noxious of humours".

## Which words are eligible

`next` applies these rules (constants live at the top of `tools/definitions.py`):

- `entry_type` is `main` — drops `greek`, `foreign`, `hapax`, `gloss`, `spur`
- key starts lowercase — drops proper nouns (`Gabali`, `Gabaon`)
- `senses` is non-empty — drops stubs like `genus2`
- sense text is ≥ 250 characters — drops one-gloss-and-a-citation entries

For G that is 172 words out of 892 entries; about 11,000 across the dictionary.
Widen or narrow the net by changing `MIN_SENSE_CHARS`, not by picking around it.

## Gotchas

- **Homograph keys.** `gero1` (carry) / `gero2` (a rare noun); `genus1` (birth,
  kind) / `genus2` (a variant of *genu*, with no senses at all). Always define
  the key `next` gives you, and keep that exact string in column 1.
- **`check` must pass before you commit.** It catches the mistakes that are
  invisible on a read-through — a key out of alphabetical order, a rank 2 that
  crept up to three words, a duplicate rank.
- **The source files may be gone.** `tools/ls_db.py wipe` removes the
  `ls_*.json` files once they are loaded into SQL. If they are missing, restore
  them with `ls_db.py export --from-raw` (the command is in the error message),
  or read entries through `tools/lookup.py`.
- **Don't reformat existing lines** while adding a chunk. Chunks are reviewed as
  diffs; a re-sorted or rewrapped file buries the ten new words in noise.

## Known limits of the format

Recorded from an audit of the first 400 words of A, so they are not
rediscovered each chunk. None is a defect in an individual line.

- **Rank 1 collides across parts of speech.** 44 rank-1 glosses in `A.txt` are
  shared by two or more words: `approach` covers seven (`accedo`, `accessus2`,
  `adeo1`, `aditio`, `aditus2`, `advento`, `aggredio`), `equal` four, `bronze`
  four, and `summer` serves a noun, a verb and an adjective alike. With no
  part-of-speech column there is nothing to separate them, which blunts rank 1
  for the memorisation job it exists to do. Fixing it means either a new column
  or letting rank 1 take a qualifying word — both change every file already
  written, so **do not change the format without asking.**
- **One-word rank 1 strains on function words.** It fits nouns and adjectives
  cleanly; adverbs, impersonals and prepositions have no one-word English
  equivalent. Precedent is to pick the closest single word and carry the real
  sense at rank 3 — `advesperascit | 1 | darkens`, `adusque | 1 | unto`,
  `acervatim | 1 | wholesale`.
- **Spelling and orthography.** The definition text is British English
  (`honour`, `colour`, `recognise`). Latin illustrations follow the source's
  `j` convention, matching the keys: `injuria`, `jus`, `adjicere` — not
  `iniuria`, `ius`, `adicere`.
- **Verify quotations against the entry, not from memory.** Three of the first
  238 illustrations were wrong this way: `aio` got an imperative `aie`, which
  does not exist (the entry says `imper. ai`); `aetas` got `vinum aetatis
  suae`, unidiomatic, where the entry supplies the real idiom `aetatem ferre`;
  and `albesco` got `dies albescit, day is breaking`, when that entry's cites
  are whitening hair and the sea whitening under wind, not dawn. Composing an
  illustration is allowed, but check the entry first — a wrong phrase teaches a
  student something false, and prefer the entry's own idiom when it has one.
- **Rank 2 is the rank most often taken without earning it.** Of the first 150
  rank 2s, six were plain near-synonyms of rank 1 and were removed:
  `aeternus` eternal/endless, `adhortor` encourage/urge, `agitatio`
  movement/agitation, `aerumna` hardship/distress, `aduro` scorch/burn,
  `adjungo` attach/join. Before writing one, say both glosses aloud: if the
  second only restates the first in other words, skip to rank 3.

## Committing

Work on the branch you were told to use, one commit per chunk, subject naming
the letter and the range, e.g. `Add definitions for G: galbanum through gallus1`.
Do not open a pull request unless asked.
