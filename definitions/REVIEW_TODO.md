# Low-confidence definitions awaiting review

Progress: 25 of 85 settled.

Every rank 1/2 gloss that needed three or more words carries a `# review:`
comment above it (see `CLAUDE.md`, "The rank contract"), explaining why the
short form didn't fit cleanly. These are the low-confidence spots in the
curated definitions: not necessarily wrong, but not settled to one or two
words and worth a second pair of eyes.

This file is a checklist built from `python tools/definitions.py review`
across every letter written so far. Regenerate the raw list at any time with:

```
python tools/definitions.py review
```

A ticked item has been settled: either the gloss was accepted as the best
English available (the `# review:` line stays, because `check` still needs
it on any three-word gloss), or it was tightened and the flag dropped. The
text after the dash records the verdict. An unticked item still carries the
writer's original reason and is waiting for a decision.

To resolve an item: accept the gloss as-is and tick it here with a one-line
verdict, or edit `definitions/<L>.txt` to tighten the gloss, drop its
`# review:` line, re-run `check`, and tick it here saying what changed.

## A.txt (22)

- [x] `abiegnus` r1 "made of fir" — accepted; English has no adjective for fir, and "fir" alone reads as the noun
- [x] `abjuro` r1 "deny on oath" — accepted; "abjure" and "forswear" both mean renounce in modern English, and the oath-denial of a debt is the whole word
- [x] `admolior` r1 "lay hands on" — accepted; the verb is all but confined to manus admoliri, and the general sense is carried at rank 3
- [x] `adusque` r1 "as far as" — accepted; a three-word preposition gloss is fine here, and CLAUDE.md cites this very word as the model ("as far as", not "unto")
- [x] `aestivo` r1 "spend the summer" — accepted; English has no verb for it, and CLAUDE.md uses this word as the model flag
- [x] `agninus` r1 "of a lamb" — accepted; three words kept to match arietinus and aprugnus, and "lamb" alone reads as the noun
- [x] `amburbium` r1 "procession round Rome" — accepted; a named rite with no English name, and "procession" alone loses that it circled the city
- [x] `amento` r1 "fit with a thong" — accepted; L&S's own gloss is "furnish with a strap or thong", and English has no verb for it
- [x] `antestor` r1 "call to witness" — accepted; a term of legal procedure that English has no verb for, and the procedure is explained at ranks 3-4
- [x] `aplustre` r1 "curved stern" — tightened to "curved stern" and flag dropped; "ship's" was redundant since a stern is always a ship's, and rank 3 carries the ornaments
- [x] `aprugnus` r1 "of wild boar" — accepted; "of wild boar" is the whole word, and "boar's" alone loses the wild
- [x] `apud` r1 "with" — accepted; a one-word gloss flagged for confidence only; no single English preposition covers it, and ranks 3-9 carry the real range
- [x] `arbustus` r1 "planted with trees" — accepted; "wooded" would suggest natural woodland where the word means land set with trees for vines
- [x] `arcera` r1 "covered wagon" — accepted; a two-word gloss flagged for confidence only; English has no name for the boarded sick-wagon of the Twelve Tables
- [x] `arietinus` r1 "of a ram" — accepted; three words kept to match agninus and aprugnus, since "ram's" alone reads as a possessive
- [x] `armipotens` r1 "mighty in arms" — accepted; matches bellipotens, and "warlike" drops the potens
- [x] `arrogatio` r1 "adrogation" — tightened to "adrogation" and flag dropped; it is the exact English legal term (OED), where "formal adoption" described every adoption and so said nothing
- [x] `artio2` r1 "train" — tightened to "train" and flag dropped; "up" added nothing, and rank 3 carries the participle artitus, schooled in the arts
- [x] `as` r1 "copper coin" / r2 "unit" — ranks swapped to "copper coin" then "unit"; the note itself said readers meet the coin first, and the rank contract orders by what a learner meets
- [x] `assero1` r1 "plant beside" — accepted; "plant" alone loses the beside, which is the whole word
- [x] `assiduus1` r1 "propertied citizen" — tightened to "propertied citizen" and flag dropped; the word names the class above the proletarii, and "taxpayer" was Servius' etymology, not the meaning
- [x] `assulatim` r1 "into splinters" — accepted; a two-word gloss flagged for confidence only, and "piecemeal" is articulatim

## B.txt (10)

- [x] `bellipotens` r1 "mighty in war" — accepted; matches armipotens, and "valiant" drops the war
- [x] `bidental` r1 "lightning shrine" — accepted; English has no name for a lightning-struck spot consecrated and fenced off, and ranks 3-5 explain it
- [x] `bigae` r1 "two-horse chariot" — accepted; "chariot" alone loses the pair of horses, which is the word
- [ ] `bigatus` r1 "stamped with a chariot" — 'stamped with a two-horse chariot' is the whole word; English has neither the adjective nor a name for the coin
- [ ] `bimaris` r1 "between two seas" — English has no one-word adjective for 'lying between two seas'
- [ ] `bimatus` r1 "age of two" — a noun for 'the age of two years'; English has no noun that carries it
- [ ] `bimembris` r1 "double-limbed" — literally 'of double members'; in practice always half man and half beast, which no single English word carries
- [ ] `bipatens` r1 "opening both ways" — of double doors that open both ways; English has no adjective, and 'folding' misses the being thrown open
- [ ] `bracchialis` r1 "of the arm" — 'of arms' would read as weapons, so the article is needed; English has no adjective for it
- [ ] `bustuarius` r1 "of the pyre" — the sense is 'of the burning place'; English has no adjective, and 'funeral' is far too wide

## C.txt (27)

- [ ] `caeduus` r1 "fit for felling" — of wood that may be cut without harming the stand; 'coppiced' names the practice rather than the fitness
- [ ] `caesim` r1 "with the edge" — the military sense is 'with the edge', against punctim 'with the point'; English has no single adverb
- [ ] `caestus` r1 "boxing strap" — a leaded hide strap bound round the hands; 'boxing-glove' suggests padding, which is the opposite of it
- [ ] `capularis` r1 "ready for burial" — said of an old man close to death, literally 'fit for the bier'; English has no adjective for it
- [ ] `castrensis` r1 "of the camp" — 'of camp' reads oddly without the article; 'military' would be militaris, and English has no adjective tied to the camp itself
- [ ] `caudicarius` r1 "of tree trunks" — used almost only of barges built from rough tree trunks; English has no adjective for it
- [ ] `ce` r1 "here" — an inseparable demonstrative suffix; 'here' is the nearest English deictic, but it is not a word that stands alone
- [ ] `censualis` r1 "of the census" — a late legal adjective tied to the census; English has no adjective, and 'census' alone reads as the noun
- [ ] `centenarius` r1 "of a hundred" — 'consisting of a hundred'; English has no adjective, and 'hundredfold' answers to centuplex instead
- [ ] `centumviri` r1 "court of a hundred" — the name of a Roman civil court; there is no English name for it, and a translation has to spell the number out
- [ ] `centuplico` r1 "increase a hundredfold" — English has no one-word verb for increasing a thing a hundredfold
- [ ] `centurialis` r1 "of a century" — 'belonging to a centuria' in any of that word's senses; English has no adjective for it
- [ ] `centurio1` r1 "divide into centuries" — 'to divide into centuries'; English has no verb that carries it
- [ ] `circumcidaneus` r1 "pared round" — used only of must from a second pressing, after the mass left in the press was pared round; the gloss alone conveys nothing
- [ ] `cis` r1 "on this side" — a preposition meaning 'on this side of'; English has no single word for it, and cis- survives only as a prefix
- [ ] `clarigatio` r1 "demand for redress" — the fetial ceremony of formally demanding redress before war; English has no name for it
- [ ] `comitialis` r1 "of the comitia" — "comitial" exists but is obscure; "of the comitia" names the actual institution plainly
- [ ] `commissorius` r1 "of a forfeiture clause" — jurid. term found almost only in "lex commissoria"; "of forfeiture" names the clause, a single word would mislead
- [ ] `confarreo` r1 "wed by confarreatio" — denotes marrying specifically via the confarreatio bread-rite; no single English word covers that
- [ ] `congiarius` r1 "of a congius" — "of a congius" needs the article to be accurate; no shorter English phrasing fits
- [ ] `congius` r1 "a Roman liquid measure of about six pints" — the precise volume needs more than one word; no exact English equivalent
- [ ] `contionalis` r1 "of the assembly" — "of the assembly" needs the article to be accurate; no shorter English phrasing fits
- [ ] `coronarius` r1 "of a wreath" — "of a wreath" needs the article to be accurate; no shorter English phrasing fits
- [ ] `crinalis` r1 "of the hair" — "of the hair" needs the article to be accurate; no shorter English phrasing fits
- [ ] `cubicularius` r1 "of a bedroom" — "of a bedroom" needs the article to be accurate; no shorter English phrasing fits
- [ ] `curialis` r1 "of a curia" — "of a curia" needs the article to be accurate; no shorter English phrasing fits
- [ ] `curiatus` r1 "of the curiae" — "of the curiae" needs the article to be accurate; no shorter English phrasing fits

## D.txt (2)

- [ ] `denicalis` r1 "purifying from death" — is a narrow religious technical term with no natural one-word English adjective; occurs only in the phrase "feriae denicales", funeral rites purifying a family after a death
- [ ] `dicis` r1 "for form's sake" — has no independent meaning outside the fixed phrase dicis causa/gratia

## E.txt (4)

- [ ] `eadem` r1 "likewise" — is the adverbial ablative of idem; no single word covers "by the same route"
- [ ] `eatenus` r1 "so far" — is a correlative adverb of extent; English needs a phrase
- [ ] `eblandior` r1 "coax out" — needs a verb phrase; English has no single verb for "get by flattery"
- [ ] `eodem` r1 "to the same place" — is the old dat/abl of idem used adverbially; no single word covers "to that same place"

## F.txt (1)

- [ ] `fideicommissarius` r1 "of a trust-bequest" — relates to the Roman fideicommissum trust-bequest; English has no adjective for it

## G.txt (5)

- [ ] `galeo` r1 "cover with a helmet" — English has no one-word verb for putting on a helmet; "helm" would wrongly suggest steering
- [ ] `gentilicius` r1 "of a clan" — "of a clan" needs the article to be accurate; no shorter English phrasing fits
- [ ] `genuinus2` r1 "of the cheek" — "of the cheek" needs the article to be accurate; no shorter English phrasing fits
- [ ] `gravedinosus` r1 "prone to colds" — English has no adjective for catching colds easily; described directly
- [ ] `gregalis` r1 "of the herd" — "of the herd" needs the article to be accurate; no shorter English phrasing fits

## I.txt (3)

- [ ] `imperatorius` r1 "of a general" — "of a general" needs the article to be accurate; no shorter English phrasing fits
- [ ] `infulatus` r1 "wearing a fillet" — no single English word for "wearing a sacred fillet"; described directly
- [ ] `intermenstruus` r1 "of the time between two months, at the new moon" — astronomical term for "the time between two months" has no one-word English equivalent

## J.txt (1)

- [ ] `jurisperitus` r1 "learned in the law" — no one-word adjective for "skilled in the law"; nearest single words distort the meaning

## L.txt (1)

- [ ] `lectisternium` r1 "a banquet offered to the gods" — no single English word for this Roman religious rite; described directly

## M.txt (1)

- [ ] `mutatorius` r1 "of changing clothes" — extremely rare (post-class.); no natural one-word gloss for "of changing clothes"

## N.txt (1)

- [ ] `noegeum` r1 "garment" — a single obscure citation with disputed description (purple-trimmed vs plain white garment); kept generic

## O.txt (1)

- [ ] `obvius` r1 "in the way" / r2 "obvious" — "in the way" needs three words; no single English word covers "positioned so as to meet" without losing the sense

## P.txt (6)

- [ ] `patrimus` r1 "having a father still living" — -- no single English word for "having a father still alive"; needed for the ritual pairing patrimi et matrimi
- [ ] `penes` r1 "in the power of" — -- preposition meaning "in the possession or power of"; no single English preposition captures it precisely
- [ ] `peremnis` r1 "of crossing a river" — -- a narrow augural technical term with no natural English adjective; occurs only in the phrase "peremne auspicium," the omen-taking ritual performed when crossing a river
- [ ] `perendinus` r1 "occurring the day after tomorrow" — -- no single English word for "occurring the day after tomorrow"
- [ ] `pollingo` r1 "wash and lay out (a corpse)" — no one-word or two-word English verb covers 'wash and lay out a corpse for burial'
- [ ] `pridie` r1 "the day before" — 'the day before' is the accurate gloss; no single or double word captures it
