# Low-confidence definitions awaiting review

Progress: 85 of 85 settled.

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
- [x] `bigatus` r1 "stamped with a chariot" — accepted; English has neither an adjective nor a name for the coin, and rank 3 gives the full stamp
- [x] `bimaris` r1 "between two seas" — accepted; a compound English can only unpack, and it is nearly always Corinth
- [x] `bimatus` r1 "age of two" — accepted; English has no noun for the age of two years
- [x] `bimembris` r1 "double-limbed" — accepted; a one-word gloss flagged for confidence only, and the centaur sense sits at rank 4
- [x] `bipatens` r1 "opening both ways" — accepted; "folding" would miss the doors being thrown open on both leaves
- [x] `bracchialis` r1 "of the arm" — accepted; "of arms" would read as weapons, so the article is needed
- [x] `bustuarius` r1 "of the pyre" — accepted; "funeral" is far wider than the burning place, and rank 3 gives the gladiator

## C.txt (27)

- [x] `caeduus` r1 "fit for felling" — accepted; "coppiced" names the practice where the word means fitness for cutting
- [x] `caesim` r1 "with the edge" — accepted; English has no adverb for a cut with the edge as against the point
- [x] `caestus` r1 "cestus" — tightened to "cestus" and flag dropped; it is the exact English word (OED), and rank 3 describes the leaded strap
- [x] `capularis` r1 "moribund" — corrected to "moribund" and flag dropped; "ready for burial" read as already dead, where the word is said of a living old man at death's door
- [x] `castrensis` r1 "of the camp" — accepted; "military" is militaris, and "of camp" reads oddly without the article
- [x] `caudicarius` r1 "of tree trunks" — accepted; almost only of log-built barges, and English has no adjective for it
- [x] `ce` r1 "here" — accepted; a one-word gloss flagged for confidence only; a suffix has no standalone English, and ranks 3-6 explain its forms
- [x] `censualis` r1 "of the census" — accepted; "census" alone reads as the noun
- [x] `centenarius` r1 "of a hundred" — accepted; "hundredfold" is centuplex, and English has no adjective for consisting of a hundred
- [x] `centumviri` r1 "court of a hundred" — accepted; the court has no English name, and the number must be spelt out
- [x] `centuplico` r1 "increase a hundredfold" — accepted; "centuple" exists as a verb but reads as an adjective on its own
- [x] `centurialis` r1 "of a century" — accepted; belonging to a centuria in any of its senses, which English cannot compress
- [x] `centurio1` r1 "divide into centuries" — accepted; English has no verb for dividing into centuries, and rank 5 gives comitia centuriata
- [x] `circumcidaneus` r1 "pared round" — accepted; a two-word literal gloss flagged for confidence only; the word exists for one kind of must, which rank 3 explains
- [x] `cis` r1 "on this side" — accepted; a preposition with no one-word English, like adusque
- [x] `clarigatio` r1 "demand for redress" — accepted; a fetial ceremony with no English name, explained at rank 3
- [x] `comitialis` r1 "of the comitia" — accepted; "comitial" exists but is obscure, and naming the institution is plainer
- [x] `commissorius` r1 "of forfeiture" — tightened to "of forfeiture" and flag dropped; the clause is named at rank 3, and the note itself preferred the shorter form
- [x] `confarreo` r1 "wed by confarreatio" — accepted, and a rank 3 added describing the rite; no English verb covers marrying by confarreatio
- [x] `congiarius` r1 "of a congius" — accepted; the article is needed, and rank 3 gives the congiarium largess
- [x] `congius` r1 "liquid measure" — tightened to "liquid measure" and flag dropped; the nine-word volume now sits at rank 3, which is where a precise quantity belongs
- [x] `contionalis` r1 "of the assembly" — accepted, and a rank 3 added with contionalis clamor and contionalis senex; the article is needed
- [x] `coronarius` r1 "of a wreath" — accepted; the article is needed, and rank 3 gives the garland-maker
- [x] `crinalis` r1 "of the hair" — accepted, and a rank 3 added with vitta crinalis and the hair-pin; the article is needed
- [x] `cubicularius` r1 "of a bedroom" — accepted; the article is needed, and rank 3 gives the chamber-servant
- [x] `curialis` r1 "of a curia" — accepted; the article is needed, and ranks 3-4 give the member and the late court sense
- [x] `curiatus` r1 "of the curiae" — accepted; comitia curiata at rank 3 is the whole use

## D.txt (2)

- [x] `denicalis` r1 "purifying from death" — accepted, and a rank 3 added for feriae denicales, the only phrase the word occurs in
- [x] `dicis` r1 "for form's sake" — accepted; a genitive with no life outside dicis causa, which rank 3 gives

## E.txt (4)

- [x] `eadem` r1 "the same way" — re-ranked: "the same way" first, since that is the Cicero and Livy sense, with the Plautine "likewise" moved to rank 4; flag kept, no one-word English
- [x] `eatenus` r1 "so far" — accepted; "so far" is L&S's own gloss, and the correlative is explained at rank 3
- [x] `eblandior` r1 "wheedle" — tightened to "wheedle" and flag dropped; wheedle means precisely to obtain by flattery, and rank 3 adds eblandita suffragia
- [x] `eodem` r1 "to the same place" — accepted; an adverb of place with no one-word English, like the prepositions

## F.txt (1)

- [x] `fideicommissarius` r1 "fideicommissary" — tightened to "fideicommissary" and flag dropped; the English legal adjective exists (OED), and rank 3 now explains the fideicommissum

## G.txt (5)

- [x] `galeo` r1 "cover with a helmet" — accepted; "helm" would suggest steering, and English has no other verb for it
- [x] `gentilicius` r1 "of a clan" — accepted; the article is needed, and "clan" is the standard rendering of gens
- [x] `genuinus2` r1 "molar" — tightened to "molar" and flag dropped; the word is used only of the back teeth, and "of the cheek" was its etymology, now at rank 3
- [x] `gravedinosus` r1 "prone to colds" — accepted; "catarrhal" would mean having a cold, not catching them easily
- [x] `gregalis` r1 "of the herd" — accepted; the article is needed, and ranks 3-4 give comrades and the common sort

## I.txt (3)

- [x] `imperatorius` r1 "of a general" — accepted; the article is needed, and rank 3 gives the imperial sense
- [x] `infulatus` r1 "wearing a fillet" — accepted; "filleted" means boned in English, so the phrase is needed
- [x] `intermenstruus` r1 "between two months" — tightened from eleven words to "between two months", L&S's own gloss, with the new moon at ranks 3-4; flag kept at three words

## J.txt (1)

- [x] `jurisperitus` r1 "learned in the law" — accepted, and a rank 3 added for the noun use, a jurist; "legal" or "juridical" would each distort it

## L.txt (1)

- [x] `lectisternium` r1 "banquet for the gods" — tightened to "banquet for the gods" and the rite itself added at rank 3, which was missing; flag kept, a named rite with no English name

## M.txt (1)

- [x] `mutatorius` r1 "of changing clothes" — accepted; a rare post-classical word whose only sure sense is the change of clothing

## N.txt (1)

- [x] `noegeum` r1 "garment" — accepted; a one-word gloss flagged for confidence only, since the one citation's description is disputed

## O.txt (1)

- [x] `obvius` r1 "in one's path" / r2 "obvious" — corrected to "in one's path"; "in the way" reads as obstruction in modern English, and the meeting construction is now at rank 3; flag kept at three words

## P.txt (6)

- [x] `patrimus` r1 "having a father still living" — accepted; English has no word for having a living father, and the pairing patrimi et matrimi sits at rank 3
- [x] `penes` r1 "in the power of" — accepted; a preposition with no one-word English, like apud and cis
- [x] `peremnis` r1 "of crossing a river" — accepted; an augural term found only in peremne auspicium, which rank 3 gives
- [x] `perendinus` r1 "after tomorrow" — tightened to "after tomorrow", L&S's own gloss, and flag dropped; "occurring" was padding
- [x] `pollingo` r1 "lay out" — tightened to "lay out" and flag dropped; laying out is exactly preparing a corpse in English, and the washing is at rank 3
- [x] `pridie` r1 "the day before" — accepted, and ranks 3-4 added for the accusative and pridie quam constructions; an adverb with no shorter English

## Wider problems found in the scan, not yet fixed

- **L&S shorthand in ranks 3+.** `CLAUDE.md` says to drop the apparatus, but
  C, D, E, F, I and P (written later than A and B) lead roughly 3,000 lines
  with `trop.`, `transf.`, `meton.`, `milit.`, `jurid.`, `post-Aug.` and the
  like, either as `trop:` or `(trop.)`. A and B spell these out ("figuratively",
  "of soldiers", "in late Latin"). Fixing it is a rewrite of those files,
  not a review item, so it is recorded here rather than done piecemeal.
