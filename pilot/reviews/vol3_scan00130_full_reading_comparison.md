# III/130: independent image-first full-page reading disagreement audit

## Evidence and frozen responses

Original printed **page 44**, physical scan **III/130**, native `images/vol3/page-00130.jpg` at commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, SHA256 from pinned manifest `51e830aa1fa46edd0746e6a9bbf25f2938fc2950a5b4011decea030b7fc64eae`, dimensions 1190×1791. Real-source hash gate is separately exercised by the PR #42 CI job.

First-pass A already present on `main` (`pilot/vol3_scan00130_single_reading.json`, context `chat-single-context-2026-11-11-III130`). Independently produced and frozen without consulting any prior III/130 text: first-pass B at `pilot/vol3_scan00130_independent_image_reading_b.json`, context `chat-single-context-2026-11-11-III130-B`. Additional draft C in PR #30 (`pilot/image_first/vol3_scan00130_single_reading.json`) was not consulted until after B freeze. All three self-report GPT-6 image-only reading with `run_id=null`; **independence of underlying executions cannot be proved solely from metadata**.

No historical word is marked verified, and there is no consensus-generated conflation. Generated TEI from B is source-linked *unverified* and does not replace A.

## Coverage and disagreement statistics

- A and B each have **44 physical text strings**: 1 folio + 22 body + 20 mixed Ukrainian/Greek apparatus + 1 line of bottom notes. Their line positions are comparable, though geometries are only estimated.
- **38 of 44** physical lines differ textually between A and B. The 6 exactly matching lines (1, 32, 33, 38, 40, 43) are still **unverified**; Unicode equality is not image-grounded correctness.
- B also differs from C on **40 of 44** aligned physical lines. There is no accuracy or CER calculation from this.

## Full A/B difference register (do not merge into text witness apparatus)

| Physical line, folio as 1 | Frozen reading A (main) | Frozen reading B (#42) | Status |
| --- | --- | --- | --- |
| 2 | хощете, чада?“ ѡни же рѣша ей: „Что есть сде Феѡкла?“ ѡна | хочете, чада?“ ѡни же рѣша ей: „Что есть сде Феѡкла?“ ѡна | unresolved |
| 3 | же рече имъ: „Азъ есмь, и что хощете?“ ѡни же рѣша ей: | же рече имъ: „Азъ есмь, и что хочете?“ ѡни же рѣша ей: | unresolved |
| 4 | „Тебѣ ны сѧ вѣсхотѣло“⁴⁷). она же рече имъ: „Мене ли старица?“ | „Тебѣ ны са въсхотѣло“⁴⁷). она же рече имъ: „Мене ли старица?“ | unresolved |
| 5 | ѡни же рѣша: „Нѣкако намъ сътворити волѧ своѧ, егоже ради | ѡни же рѣша: „Нѣкако намъ сътворити волю своѧ, егоже ради | unresolved |
| 6 | помышл есмь“⁴⁸). рече имъ ст҃а дѣва: „Пождете мене, чада, и ѹ- | помилѹ есмь“⁴⁸). рече имъ ст҃а дѣва: „Пождете мене, чада, и оу- | unresolved |
| 7 | зрите славоу бж҃ію“. ѡни же держима ими вѣзревши на нѣко ре- | зрите славоу бж҃ію“. ѡна же держима ими възревши на н҃бо ре- | unresolved |
| 8 | че: „Б҃же страшный и бессмртный, избавляй мѧ ѡ ѡгнѧ, не пре- | че: „Бж҃е страшный и бессмѣртный, избавляй мя ѡ огня, не пре- | unresolved |
| 9 | давый мене Фамироу, не предавый мене Александроу, избавляй мѧ | давкий мене Фалмироу, не предавкий мене Александроу, избавий мя | unresolved |
| 10 | ѡ зверій и поскѹшествовавый, избави мѧ и ѡ сихъ безакон- | ѡ звѣрїй и постѣшествовавший, избави мя и ѡ сихъ беззакон- | unresolved |
| 11 | никъ, и не мози мене въ роѹкѣ сътворити женамъ на старость, | никъ, и не мозѹ мене въ роугъ сътворити женам на старость, | unresolved |
| 12 | но съвѣрши дѣвство мое!“ и абіе гла҃ б҃ы съ нб҃се гл҃а к ней: | но съвѣрши дѣйство мое!“ и абие гласъ бы съ н҃бе г҃ла к ней: | unresolved |
| 13 | „Феѡкла, истинная раба моя, не бой сѧ, азъ есмь с тобою. вѣзри, | „Феѡкла, истинная раба моя, не бой са, азъ есмь с тобою. възри, | unresolved |
| 14 | да идеже ти сѧ мѣсто ѡбрѣзеть, тоу ти боудет вѣчный домъ | да идѣже ти са мѣсто ѡверзеть, тоу ти будет вѣчный домъ | unresolved |
| 15 | и тоу тебѣ посѣщю“. Зревши же видѣ камень ѡкѣрстъ, и по | и тоу тебѣ посѣщю“. Зревши же видѣ камень ѡверстъ, и по | unresolved |
| 16 | реченомоу к ней ѡбрацивши ѡ нихъ внидѣ въ камень, и сѣтише | реченомоу к ней ѡбращший ѡ нихъ внидѣ въ камень, и сътще | unresolved |
| 17 | са камень яко не знати, гдѣ сѧ растоупилъ. ѡни же ѧша за | са камень яко не знати, гдѣ са растоупилъ. ѡни же ѧша за | unresolved |
| 18 | ризы еѧ, и етерѧ часть амофора еѧ ѡста вънѣ. вѣры ради кр҃- | онзи еѧ, и етера часть амофора еѧ ѡста вънѣ. вѣры ради кр҃- | unresolved |
| 19 | тѧнъ. и сице сконча житіе свое дѣва бжія, первомѫчница и равна | тѧанъ. и сицѣ сконча житїе свое дѣва бж҃іѧ, первомучица и равна | unresolved |
| 20 | аполмъ, инокинѧ*). бѣ же й. лѣтъ, егда послѹшаше оученія | аполлъ, инокинѣ*). въ же н҃. лѣтъ, егда послоушаше оученїа | unresolved |
| 21 | Паѹла, жить же потомъ ѡко в҃ мѹченїихъ, ѡво въ горѣ лѣт | Паѹла, жить же потомъ ѡко въ мѹченїѧхъ, ѡбо въ горѣ лѣт | unresolved |
| 22 | н҃. и в҃. б҃ы же всѣхъ лѣт и въ животѣ еѧ п҃.**). лѣтъ исполни. | н҃. и в҃. бы же всѣхъ лѣтъ и въ животѣ еѧ п҃.**) лѣт исполни. | unresolved |
| 23 | Въ славу Ѡца и С҃на и ст҃го Д҃ха нынѣ и присно и в вѣки вѣком. | Въ славу Ѡц҃а и С҃на и ст҃го Дх҃а нынѣ и пр҃но и въ вѣкы вѣкѡм. | unresolved |
| 24 | ¹) В грецькім час. ²) Σιμμέα καὶ Ζηνοῦν ³) Λέκτρε ⁴) В оріг. сі остатні слова | ¹) В грецькім вас. ²) Σιμιᾶς καὶ Ζήνων ³) Λέκτρος ⁴) В оріг. сі остатні слова | unresolved |
| 25 | належать іще до Онисѳорової промови: „і погостіть“. ⁵) Περὶ ἐγκρατείας ⁶) Отсе | належать іще до Онисїфорової промови: „і погостїть“. ⁵) Περὶ ἐγκρατείας ⁶) Отсе | unresolved |
| 26 | речене в оріг. стоїть перед нашим попереднім ⁷) Отсе реченє нашого тексту вложе- | реченє в оріг. стоїть перед нашим попереднїм ⁷) Отсе реченє нашого тексту зложе- | unresolved |
| 27 | не з двох половинок різних речень грецького тексту: „Щасливі ті, що приняли му- | не з двох подвоєнь різних речень грецького тексту: „Щасливі ті, що приняли му- | unresolved |
| 28 | дрість Ісуса Христа, бо вони назвуть ся синами найвисшого. Щасливі ті, що ввійшли | дрість Ісуса Христа, бо вони назвуть ся синами найвищого. Щасливі ті, що війшли | unresolved |
| 29 | в злуку з Ісусом Христом, бо вони будуть у світлі“. Слова надруковані тут курсі- | в злуку з Ісусом Христом, бо вони будуть у світлї“. Слова надруковані тут курси- | unresolved |
| 30 | вом, у нашім тексті пропущені; очевидно або копіст, або перекладач перескочив зо- | вом, у нашім текстї пропущені; очевидно або копіст, або перекладач перескочив зо- | unresolved |
| 31 | ром від одного Іс Хса до другого. ⁸) и лѹси в оріг. vac. ⁹) В оріг. Θέκλα τις πάρθε- | ром від одного Іс Хса до другого. ⁸) и лоусн в оріг. час. ⁹) В оріг. Θέκλα τις πάρθε- | unresolved |
| 34 | зрадливі та хитроумні слова. ¹⁴) очевидна помилка зам. моужь съ Иконійскій, в оріг. | зрадливі та хитроумні слова. ¹⁴) очевидна помилка зам. мужик с҃ Иконийски, в оріг. | unresolved |
| 35 | ὁ ἄνθρωπος οὗτος τὴν Ἰκονέων і т. д. ¹⁵) ἕνα καὶ μόνον ¹⁶) τοῖς ὑπ’ αὐτοῦ | ὁ ἄνθρωπος οὗτος τὴν Ἰκονείαν і т. д. ¹⁵) ἕνα καὶ μόνον ¹⁶) τοῖς ὑπ᾽ αὐτοῦ | unresolved |
| 36 | λόγοις ¹⁷) Θάμυρις ¹⁸) φοβούμενος τὴν ἔκπληξιν αὐτῆς, лякаючись її остовпіння. | λόγοις ¹⁷) Θέμυρις ¹⁸) φοβούμενος τὴν ἔκπληξιν αὐτῆς, лякаючись її остовпіння. | unresolved |
| 37 | ¹⁹) τίνες ἐστέ — хто ви такі. ²⁰) κατελθὼ ²¹) καστέλιον ²²) В грецькім дословно: „І | ¹⁹) τίνες ἐστέ — хто ви такі. ²⁰) καστελῳ ²¹) καστέλιον ²²) В грецькім дословно: „І | unresolved |
| 39 | вінси скликати купу народа і дали знати начальникови“. ²³) В оріг. дословно: „а Те- | віси скликати купу народа і дали знати начальникови“. ²³) В оріг. дословно: „а Те- | unresolved |
| 41 | ник велів їй привести на суд. ²⁴) εἰσήχθη γυμνή — вивели її голу ²⁵) в оріг. | ник велів і її привести на суд. ²⁴) εἰσήχθη γυμνή — виведи її голу ²⁵) в оріг. | unresolved |
| 42 | ἐθαύμασεν τὴν ἐν αὐτῇ δύναμιν — дивував ся її силі. ²⁶) ἦχον ὑπόγαιον — під- | ἐθαύμασεν τὴν ἐν αὐτῇ δύναμιν — дивував ся її силї. ²⁶) ἦχον ὑπόγαιον — під- | unresolved |
| 44 | *) В рукоп. иконникъ нынѣ. **) Львів рукоп. ѡ. | *) В рукоп. иконинѣ нынѣ. **) Львів рукоп. б. | unresolved |

## Failure-seeking visual inspection priorities

1. Body: хощете / хочете, ѧ/а, titla, superscripts and possibly interlinear digits.
2. Body: proper names Фамироу/Фалмироу, Alexandra, letter shapes.
3. Body: phrase дѣвство/дѣйство, and the exact heavenly speech.
4. Apparatus: Greek Σιμμέα, Ζηνοῦν, Λέκτρε vs B alternatives.
5. Apparatus: `з двох половинок` vs B's `з двох подвоєнь` — B likely visibly mistaken.
6. Apparatus: exact ⁸) Greek/Slavonic note and ¹⁴) printed Church Slavonic lemma.
7. Apparatus: Greek πολυτονικά, especially Θάμυρις/Θέμυρις, Ἰκονέων/Ἰκονείαν.
8. Bottom: tiny glyphs in both asterisk notes need crop-level inspection.

The native image confirms the **existence and ordering** of these text zones, not every old glyph at this resolution. Representative source spot-checks: visible line containing `не з двох половинок різних речень` strongly conflicts with B's `не з двох подвоєнь` (B appears wrong); in the Greek notes `Σιμμέα` and `Ζηνοῦν` differ substantially from B, and the bottom asterisk notes are too small for a reliable single look. These are findings and targets, not blanket auto-corrections.

## Required continuation

1. Do not erase either raw first response; produce *separate* line-level adjudication evidence with actual magnified original-image inspection by another reviewing context, including agreements and every apparatus line.
2. No forced majority vote among A/B/C, no OCR-confidence winner and no normalization based on grammatical likelihood. Attribute Greek, Church Slavonic and Ukrainian/Latin spans to the specific text version.
3. Test source JPEG against immutable manifest, XML P5 RNG/Schematron, and image-backed TEI→Text-Fabric exact Unicode/text/page provenance roundtrips once reviewed reading versions exist.
4. Distinguish independent reading comparison from an actual independently executed third reviewer; neither is a gold set. No source rights or stable release are implied.

This note is a **post-freeze same-context adversarial comparison** after direct image viewing, not #11's completed third blind review.
