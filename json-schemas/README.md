# Translation API JSON Schemas

Contract sketches for the four starting translation call types. Keys are
snake_case; controlled-vocabulary values are lowercase.

```
json-schemas/
  requests/     inbound bodies
  responses/    outbound bodies (always a `results` array)
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

## Definition detail (Latin → English)

Clients may set optional `definition_mode` on `english_word` and
`english_sentence` requests (`json-schemas/common/definition_mode.json`):

| Value | Behavior |
| --- | --- |
| `full` (default) | Every top-level sense from each matched headword; nested sub-senses stay intact. |
| `simplified` | At most the first **three** top-level senses per headword (sub-senses under those are still included). |

Responses echo the effective `definition_mode`. Word results include a
`definitions` array shaped like the dictionary `senses` tree (strings and
nested arrays).
