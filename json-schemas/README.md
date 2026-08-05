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
`summary` is reserved for later (often agent-written) and may be `""`.

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
| `both` (default) | `brief_glosses` and `definitions` populated; tabs always filled when source data exists. |
| `brief` | `brief_glosses` only (empty `definitions`); tabs still returned. |
| `full` | Long `definitions` only (empty `brief_glosses`); tabs still returned. |

Responses echo the effective `definition_mode`. Tab schemas live under
`json-schemas/common/morphology_tab.json` and `connections_tab.json`.
Generated full case paradigms (future) may extend `morphology` or reuse
`latin_word`-style tables when principal parts can be inferred.
