# Low-confidence definitions awaiting review

Every entry here carries a `# review: <key> <reason>` comment directly above
it in `definitions/<L>.txt` (see `CLAUDE.md`, "The rank contract"). Two kinds
of flag land here:

- **Brevity flags**, added automatically at write time whenever a rank 1/2
  gloss needed three or more words to stay accurate — `check` refuses to pass
  without one.
- **Accuracy flags**, added by a targeted audit (see below) for glosses that
  parse cleanly (1-2 words) but that the audit judged genuinely
  low-confidence: the wrong part of speech, a rank 2 that doesn't earn its
  slot over rank 1, two different headwords sharing a gloss that blurs a real
  distinction, or a meaning not clearly grounded in the source entry.

None of these are known-wrong — they're flagged so a human can settle them,
same as the existing convention. See GitHub issue for this audit's summary.

This file is a snapshot of `python tools/definitions.py review` for A-D.
Regenerate at any time with:

```
python tools/definitions.py review          # all written letters
python tools/definitions.py review A         # one letter
```

To resolve an item: either accept the gloss as-is (remove its row here and
the `# review:` line in the file), or edit `definitions/<L>.txt` to fix it
and drop the `# review:` line, then re-run `check`.

## A.txt (30)

- [ ] `abiegnus` r1 "made of fir" — English has no adjective for 'of fir'; three words kept, confirmed
- [ ] `abjuro` r1 "deny on oath" — 'disavow' loses the oath, which is the whole point of the word
- [ ] `acer2` r1/r2 "sharp" / "keen" — [audit] 'keen' just restates 'sharp'; the mental/acute sense that might justify a second gloss is already covered separately at rank 6
- [ ] `acquiro` r1/r2 "acquire" / "gain" — [audit] 'gain' just restates 'acquire'; the entry never marks off a genuinely distinct second sense
- [ ] `admolior` r1 "lay hands on" — general sense is 'bring one thing to another'; the attested use is manus admoliri
- [ ] `adusque` r1 "as far as" — 'unto' is archaic and vague; is a 3-word preposition gloss acceptable here?
- [ ] `aestivo` r1 "spend the summer" — English has no one-word verb for it; 'summer' as a verb reads as the noun
- [ ] `agninus` r1 "of a lamb" — 'lamb' would also read fine; three words kept, confirmed
- [ ] `aio` r1/r2 "say" / "affirm" — [audit] 'affirm' just restates 'say'; the real distinct sense (say yes, opposite of nego) is already given fully at rank 3
- [ ] `alius2` r1/r2 "other" / "another" — [audit] 'another' doesn't earn its slot over 'other'; the real distinguishing nuance (one of many, vs. alter's one of two) only appears at rank 3
- [ ] `amburbium` r1 "procession round Rome" — a procession round Rome; "procession" alone loses the rite, and English has no single word
- [ ] `amento` r1 "fit with a thong" — the sense is to fit a javelin with its throwing-strap; English has no verb for it
- [ ] `angustiae` r1/r2 "narrows" / "straits" — [audit] 'straits' just restates 'narrows' (same literal geographic sense); the real second sense is the figurative want/difficulty first given at rank 4
- [ ] `antestor` r1 "call to witness" — the sense is to call a bystander as witness at the opening of a suit; English has no verb for it
- [ ] `aplustre` r1 "ship's curved stern" — English has no word for the curved ornamented stern-piece of a ship
- [ ] `aprugnus` r1 "of wild boar" — three words kept; "boar's" alone loses the wild boar, which is the whole of it
- [ ] `apud` r1 "with" — no single English preposition covers it; "with" is nearest, but "at", "among" and "before" are each right in their place
- [ ] `arbustus` r1 "planted with trees" — the sense is land set with trees for vines to climb; "wooded" would suggest natural woodland instead
- [ ] `arcera` r1 "covered wagon" — English has no word for the boarded litter-wagon the Twelve Tables allowed the sick
- [ ] `arietinus` r1 "of a ram" — three words kept, matching agninus; "ram's" alone reads as a possessive rather than a class
- [ ] `armipotens` r1 "mighty in arms" — a compound meaning potent in arms; "warlike" or "valiant" alone drops the force of potens
- [ ] `arrogatio` r1 "formal adoption" — a particular Roman form of adoption; English has no word for it
- [ ] `arse verse` r1 "avert fire" — an Etruscan charm rather than Latin; the gloss is the ancient explanation averte ignem. **Note:** this flag's key is stored as `arse verse` (a two-word headword); `definitions.py`'s review parser currently mis-splits it as `arse`, so it silently drops out of `tools/definitions.py review` output. Pre-existing tooling quirk, not touched by this audit — worth a follow-up fix in `tools/definitions.py` if anyone's in there.
- [ ] `artio2` r1 "train up" — attested only through the participle artitus; there is no ordinary English verb for it
- [ ] `artus1` r1/r2 "narrow" / "tight" — [audit] 'tight' just restates 'narrow' (same physical sense); the real second sense is the figurative strict/severe, first given at rank 4
- [ ] `as` r1 "unit" / r2 "copper coin" — the root sense is the unit of any divided whole, but a reader most often meets the coin
- [ ] `assero1` r1 "plant beside" — the point of the word is setting one plant beside another; "plant" alone loses it
- [ ] `assiduus1` r1 "taxpayer" — a class in the Servian constitution; "taxpayer" is the nearest single word but drops the property qualification
- [ ] `assulatim` r1 "into splinters" — "piecemeal" is already articulatim's gloss and this word is specifically about splintering
- [ ] `astringo` r1/r2 "tighten" / "bind" — [audit] 'bind' just restates 'tighten' (same literal sense); the real second sense is the figurative put-under-obligation, first given at rank 4

## B.txt (11)

- [ ] `bellipotens` r1 "mighty in war" — English has no one-word adjective for it; 'valiant' drops the war, which is the whole word
- [ ] `belua` r1 "beast" — [audit] L&S explicitly contrasts belua (large or fierce beast) with the broader bestia1; plain "beast" for both erases a distinction the source dictionary itself calls out
- [ ] `bidental` r1 "lightning shrine" — English has no word for a spot struck by lightning and then consecrated; 'shrine' is close but not exact
- [ ] `bigae` r1 "two-horse chariot" — the pair of horses and the car they draw are one word in Latin; 'chariot' alone loses the pair
- [ ] `bigatus` r1 "stamped with a chariot" — 'stamped with a two-horse chariot' is the whole word; English has neither the adjective nor a name for the coin
- [ ] `bimaris` r1 "between two seas" — English has no one-word adjective for 'lying between two seas'
- [ ] `bimatus` r1 "age of two" — a noun for 'the age of two years'; English has no noun that carries it
- [ ] `bimembris` r1 "double-limbed" — literally 'of double members'; in practice always half man and half beast, which no single English word carries
- [ ] `bipatens` r1 "opening both ways" — of double doors that open both ways; English has no adjective, and 'folding' misses the being thrown open
- [ ] `bracchialis` r1 "of the arm" — 'of arms' would read as weapons, so the article is needed; English has no adjective for it
- [ ] `bustuarius` r1 "of the pyre" — the sense is 'of the burning place'; English has no adjective, and 'funeral' is far too wide

## C.txt (33)

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
- [ ] `contendo` r1/r2 "strive" / "contend" — [audit] rank 2 'contend' restates rank 1 'strive' as near-synonyms; the entry's real distinct sense (to assert/maintain in argument) is already given at rank 4
- [ ] `contionalis` r1 "of the assembly" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `contorqueo` r1/r2 "twist" / "vehement" — [audit] rank 2 'vehement' is adjective-shaped (the perfect-participle sense) for a headword that is fundamentally a verb; doesn't read as a verb sense
- [ ] `coronarius` r1 "of a wreath" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `crinalis` r1 "of the hair" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `crucio` r1/r2 "torture" / "torment" — [audit] rank 2 'torment' is a near-synonym of rank 1 'torture' (entry gives them jointly for the same physical sense); the real second branch, mental affliction, is already at rank 3
- [ ] `cubicularius` r1 "of a bedroom" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `cunctor` r1/r2 "hesitate" / "linger" — [audit] rank 2 'linger' is a near-synonym of rank 1 'hesitate' for personal delay; the entry's genuinely distinct transferred sense (of things moving slowly) is already at rank 3
- [ ] `curialis` r1 "of a curia" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `curiatus` r1 "of the curiae" — needs the article to be accurate; no shorter English phrasing fits
- [ ] `cursus` r1/r2 "course" / "journey" — [audit] rank 2 'journey' is a near-synonym of rank 1 'course'; the entry's real figurative sense is separately given at rank 4
- [ ] `curvus` r1/r2 "curved" / "crooked" — [audit] rank 2 'crooked' is a near-synonym of rank 1 'curved'; the entry's genuine figurative sense ('wrong') is already at rank 3

## D.txt (8)

- [ ] `demetior` r1 "measure" — [audit] L&S explicitly contrasts this with dimetior ("dimetior is to measure the parts of a whole"); sharing the bare gloss "measure" with dimetior erases that distinction
- [ ] `denicalis` r1 "purifying from death" — a narrow religious technical term with no natural one-word English adjective; occurs only in the phrase "feriae denicales", funeral rites purifying a family after a death
- [ ] `dicis` r1 "for form's sake" — has no independent meaning outside the fixed phrase dicis causa/gratia
- [ ] `diffarreatio` r1 "divorce" — [audit] one specific archaic religious ceremony for dissolving a confarreatio marriage, not divorce in general; sharing "divorce" with divortium loses that narrower, technical sense
- [ ] `dimetior` r1 "measure" — [audit] L&S defines this specifically as measuring the parts of a whole, as opposed to demetior (measuring a whole); the shared gloss "measure" erases that source-drawn distinction
- [ ] `discessio` r1/r2 "division" / "separation" — [audit] dominant classical use (per L&S, "far more freq.") is the specific Senate procedure of voting by dividing into groups, not the general "division" divisio denotes; the bare gloss loses that
- [ ] `discors` r1 "discordant" — [audit] fundamentally about people/things at variance (dis+cor); sharing "discordant" with dissonus, whose core sense is discordant sound, blurs a real domain difference
- [ ] `dissonus` r1 "discordant" — [audit] literally about discordant sound (dis+sonus), only secondarily generalized to "differing"; sharing "discordant" with discors blurs that distinction

## E.txt onward

Not started. Re-run `python tools/definitions.py review` and extend this
file once more letters have curated definitions.
