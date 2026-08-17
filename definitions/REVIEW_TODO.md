# Low-confidence definitions awaiting review

Every rank 1/2 gloss that needed three or more words carries a `# review:`
comment above it (see `CLAUDE.md`, "The rank contract"), explaining why the
short form didn't fit cleanly. These are the low-confidence spots in the
curated definitions: not necessarily wrong, but not settled to one or two
words and worth a second pair of eyes.

This file is a snapshot of `python tools/definitions.py review` for A–D,
turned into a checklist. `D.txt` doesn't exist yet — no definitions have been
written for D, so there's nothing to flag there yet.

Regenerate the list at any time with:

```
python tools/definitions.py review A
python tools/definitions.py review B
python tools/definitions.py review C
python tools/definitions.py review D   # once D.txt exists
```

To resolve an item: either accept the gloss as-is (remove it from this list),
or edit `definitions/<L>.txt` to tighten the gloss and drop its `# review:`
line, then re-run `check`.

## A.txt (23)

- [ ] `abiegnus` r1 "made of fir" — English has no adjective for 'of fir'; three words kept, confirmed
- [ ] `abjuro` r1 "deny on oath" — 'disavow' loses the oath, which is the whole point of the word
- [ ] `admolior` r1 "lay hands on" — general sense is 'bring one thing to another'; the attested use is manus admoliri
- [ ] `adusque` r1 "as far as" — 'unto' is archaic and vague; is a 3-word preposition gloss acceptable here?
- [ ] `aestivo` r1 "spend the summer" — English has no one-word verb for it; 'summer' as a verb reads as the noun
- [ ] `agninus` r1 "of a lamb" — 'lamb' would also read fine; three words kept, confirmed
- [ ] `amburbium` r1 "procession round Rome" — a procession round Rome; "procession" alone loses the rite, and English has no single word
- [ ] `amento` r1 "fit with a thong" — the sense is to fit a javelin with its throwing-strap; English has no verb for it
- [ ] `antestor` r1 "call to witness" — the sense is to call a bystander as witness at the opening of a suit; English has no verb for it
- [ ] `aplustre` r1 "ship's curved stern" — English has no word for the curved ornamented stern-piece of a ship
- [ ] `aprugnus` r1 "of wild boar" — three words kept; "boar's" alone loses the wild boar, which is the whole of it
- [ ] `apud` r1 "with" — no single English preposition covers it; "with" is nearest, but "at", "among" and "before" are each right in their place
- [ ] `arbustus` r1 "planted with trees" — the sense is land set with trees for vines to climb; "wooded" would suggest natural woodland instead
- [ ] `arcera` r1 "covered wagon" — English has no word for the boarded litter-wagon the Twelve Tables allowed the sick
- [ ] `arietinus` r1 "of a ram" — three words kept, matching agninus; "ram's" alone reads as a possessive rather than a class
- [ ] `armipotens` r1 "mighty in arms" — a compound meaning potent in arms; "warlike" or "valiant" alone drops the force of potens
- [ ] `arrogatio` r1 "formal adoption" — a particular Roman form of adoption; English has no word for it
- [ ] `artio2` r1 "train up" — attested only through the participle artitus; there is no ordinary English verb for it
- [ ] `as` r1 "unit" / r2 "copper coin" — the root sense is the unit of any divided whole, but a reader most often meets the coin
- [ ] `assero1` r1 "plant beside" — the point of the word is setting one plant beside another; "plant" alone loses it
- [ ] `assiduus1` r1 "taxpayer" — a class in the Servian constitution; "taxpayer" is the nearest single word but drops the property qualification
- [ ] `assulatim` r1 "into splinters" — "piecemeal" is already articulatim's gloss and this word is specifically about splintering

## B.txt (10)

- [ ] `bellipotens` r1 "mighty in war" — English has no one-word adjective for it; 'valiant' drops the war, which is the whole word
- [ ] `bidental` r1 "lightning shrine" — English has no word for a spot struck by lightning and then consecrated; 'shrine' is close but not exact
- [ ] `bigae` r1 "two-horse chariot" — the pair of horses and the car they draw are one word in Latin; 'chariot' alone loses the pair
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
- [ ] `congiarius` r1 "of a congius" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `congius` r1 "a Roman liquid measure of about six pints" — the precise volume needs more than one word; no exact English equivalent
- [ ] `contionalis` r1 "of the assembly" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `coronarius` r1 "of a wreath" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `crinalis` r1 "of the hair" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `cubicularius` r1 "of a bedroom" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `curialis` r1 "of a curia" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `curiatus` r1 "of the curiae" — needs the article to be accurate; no shorter English phrasing fits

## D.txt

Not started — `definitions/D.txt` doesn't exist yet, so there's nothing to
review here. Re-run this list once D has been written.
