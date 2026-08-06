# Translation API JSON Schemas

Contract sketches for the four starting translation call types. Keys are
snake_case; controlled-vocabulary values are lowercase.

```
json-schemas/
  requests/     inbound bodies
  responses/    outbound bodies (always a `results` array)
  common/       shared enums and tab shapes
```

| `translation_type` | Direction | Unit |
| --- | --- | --- |
| `latin_word` | English → Latin | word |
| `english_word` | Latin → English | word |
| `latin_sentence` | English → Latin | sentence |
| `english_sentence` | Latin → English | sentence |

`latin_word` response items currently describe **nouns** (gender, declension,
case tables). Other parts of speech will get their own result shapes later.
Sentence result items are minimal placeholders until the agent path is defined.
### `summary` (learning / quick reference)

Each word or sentence result includes a `summary` string (may be `""` until filled,
often by an agent). Clients can surface it as an extra column, callout, or sidebar
blurb alongside glosses and morphology.

**Intended content** — case governance for fast lookup while reading or composing:

| Entry kind | What to put in `summary` |
| --- | --- |
| **Prepositions** | Which noun case the preposition takes (and brief sense splits when case differs, e.g. in / on / against). |
| **Verbs** | Which case(s) objects or complements use (accusative, dative, genitive, ablative, double objects, etc.). |

Other concise learner notes are fine when case is not the main story, but preposition
and verb case patterns are the default high-value use.

**Not the same as `connections.notes`** — that field is the full Lewis & Short
`main_notes` text (etymology, cross-references). Keep dictionary prose there; keep
case cheat-sheets in `summary`.

Schema: `json-schemas/common/summary_field.json`.

## Latin → English word UX (Logeion + Scriba)

`english_word` results are shaped so a client can mirror two familiar apps:

| App | What the API supports |
| --- | --- |
| **Logeion** | `brief_glosses` (short hit list) and `definitions` (full Lewis & Short tree) together when `definition_mode` is `both` (default). |
| **Scriba** | `definitions` as the main reading tab; `morphology` and `connections` as a second tab (lemma line, forms, gender/declension, Greek links, notes). |

Optional `definition_mode` on `english_word` and `english_sentence` requests
(`json-schemas/common/definition_mode.json`):

| Value | Behavior |
| --- | --- |
| `both` (default) | `brief_glosses` first (most common senses), then full `definitions`; morphology and connections follow. |
| `brief` | `brief_glosses` only (empty `definitions`); tabs still returned. |
| `full` | Long `definitions` only (empty `brief_glosses`); tabs still returned. |

Optional `include_paradigms` (default **true**) on `english_word` requests: when
true, attach `morphology.paradigm` (declension / conjugation tables) whenever
the server can generate them; when false, omit that block for a lighter payload.
Clients may still collapse paradigms in the UI when they are present.

Responses echo `definition_mode` and `include_paradigms`. Tab schemas:
`json-schemas/common/morphology_tab.json`, `connections_tab.json`, and
`paradigm_tables.json`. Generated full case paradigms may extend `morphology`
or reuse `latin_word`-style tables when principal parts can be inferred.
