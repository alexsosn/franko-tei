# I/20 post-freeze image-reading comparison (adversarial provisional audit)

**Source:** original native image `images/vol1/page-00020.jpg` from pinned `e871f32537e81f81896f6ce9a6658aba667db9c5`; image SHA `60cb6b24dfce29bbf2e0655caf172e515b74510ef8af64d430a09afeb7120bf3` per pinned manifest, source-gated in PR #37 Actions.

**Comparison order:** Our image-only complete first response was frozen at commit `800ffde9a7d73d30a9bc67f1b6845bea33850cd7` BEFORE viewing `pilot/image_first/vol1_scan00020_first.md` and the other structured first response on branch `codex/image-first-five-full-pages-20261111` (PR #30). Neither input was modified during comparison.

**Readers:** ours `chat-single-context-2026-11-11-I20-new-visual`; other `chat-single-context-2026-11-11-five-page-reading`. Both independently identify GPT-6 single working drafts with `run_id=null`, no witnessed model execution IDs and no actual third reviewing agent. These context IDs alone do NOT prove separate independent model execution. We count agreement/disagreement, not CER or historical accuracy.

**Coverage:** 42 line strings including printed XI in BOTH frozen records. 18 textual line disagreements; 24 line-level exact agreements. Comparable **line positions**, not necessarily identical pixel crop geometries; our source-linked boxes are estimated. No omitted printed line is immediately obvious from the visual full-page survey; this is not a character-by-character coverage attestation.

## Disagreements requiring independent native-image adjudication

| Physical line (folio counted as 1) | PR #37 frozen image reading | PR #30 first-pass reading | Adversarial finding / decision |
| --- | --- | --- | --- |
| 2 | стольські конституції згадують також про фальшиві βιβλία ἐπ᾽ ὀνόμασι | стольські конституції згадують також про фальшиві βιβλία ἐπ' ὀνόμασι | Unresolved: Greek elision punctuation (U+1FBD versus ASCII apostrophe); image enlargement required. |
| 3 | Χριστοῦ, а з старозавітних βιβλία ἀπόκρυφα Μωσέως καὶ Ἐνὼχ καὶ Ἀδὰμ, | Χριστοῦ, а з старозавітних βιβλία ἀπόκρυφα Μωσέως καὶ Ἐνὼχ καὶ Ἀδάμ, | Unresolved: Ἀδὰμ versus Ἀδάμ; breathings and accents require pixel-level inspection. |
| 4 | Ἠσαΐου τε καὶ Δαβὶδ καὶ Ἠλία καὶ τῶν τριῶν πατριαρχῶν, φθοροποιὰ τε καὶ ἀληθείας | Ἠσαΐου τε καὶ Δαβὶδ καὶ Ἠλία καὶ τῶν τριῶν πατριαρχῶν, φθοροποιά τε καὶ ἀληθείας | Unresolved: φθοροποιὰ versus φθοροποιά; accent placement cannot be inferred from standard Greek. |
| 16 | шованої бібліографії з поданєм, кілько віршів має кождий твір. Чи- | шованої бібліоґрафії з поданєм, кілько віршів має кожний твір. Чи- | Unresolved: бібліографії / бібліоґрафії and кождий / кожний. Pixel glyph comparison required. |
| 18 | Καὶ ὅσα τῆς Παλαιᾶς εἰσιν ἀπόκρυφα: Ἐνώχ, Πατριάρχαι, Προσευχὴ Ἰωσήφ, | Καὶ ὅσα τῆς Παλαιᾶς εἰσιν ἀπόκρυφα: Ἐνὼχ, Πατριάρχαι, Προσευχὴ Ἰωσὴφ, | Unresolved: two Greek names with differing tonos. Do not import a canonical printed list. |
| 19 | Διαθήκη Μωσέως, Ἀνάληψις Μωσέως, Ἀβραάμ, Ἐλδὰδ καὶ Μωδάδ, Ἠλίας προ- | Διαθήκη Μωσέως, Ἀνάληψις Μωσέως, Ἀβραάμ, Ἐλδὰδ καὶ Μωδὰδ, Ἠλίας προ- | Unresolved: Μωδάδ versus Μωδὰδ; printed accent not independently attested. |
| 23 | свою статю „Synopsis sacrae scripturae“, приписану св. Афанасьеви | свою статю „Synopsis sacrae scripturae“, приписану св. Афанасиеви | Unresolved: Афанасьеви / Афанасиеви. Early-Ukrainian glyph reading, not modernization. |
| 24 | і опубліковану між його творами (Athanasii Opera omnia II, 154), | і опублїковану між его творами (Athanasii Opera omnia II, 154), | HIGH PRIORITY: our \`опубліковану між його\` may be modernized against historical source; other reading has \`опублїковану між его\`. Preserve BOTH until image close check. |
| 25 | бо тут приведено ті самі апокріфи. Незвісно також, з якого часу | бо тут приведено ті самі апокріфи. Невісно також, з якого часу | Unresolved: Незвісно / Невісно. Do not insert 'з' by grammar alone. |
| 26 | походить статя „Quaestiones et responsiones Anastasii Sinaitae“, тільки | походить статя „Questiones et responsiones Anastasii Sinaitae“, тільки | HIGH PRIORITY: our \`Quaestiones\` may be standard Latin correction; other reads \`Questiones\`. Inspect exact printed letters. |
| 27 | вона не Анастасієва. Єї славянський переклад є в Сборнику Свято- | вона не Анастасиева. Сї словянський переклад є в Сборнику Свято- | HIGH PRIORITY: \`Єї славянський\` / \`Сї словянський\` and Анастасієва / Анастасиева; likely reader mistake on at least one witness. |
| 28 | славовім з 1073 р., приписаний Григорію Богослову значить, був уже | славовім з 1073 р., приписаний Григорию Богослову значить, був уже | Unresolved: Григорію / Григорию; historical orthography. |
| 32 | ческой коммиссіи 1861 года, вып. I. СПбургъ 1862), стор. 1—2; | ческой комиссии 1861 года, вып. I. СПбургъ 1862), стор. 1—2; | Unresolved: коммиссіи / комиссии in prereform Russian bibliography. |
| 38 | 60 і вказані вже книги Порфирєва, Рейса, Цана, а також великі | 60 і вказані вже книги Порфірєва, Рейса, Цана, а також великі | Unresolved: Порфирєва / Порфірєва. |
| 39 | енциклопедії Герцога і Плїтта та Вецера і Вельте). | енциклопедії Герцога і Плітта та Вецера і Вельте). | Unresolved: Плїтта / Плітта. |
| 40 | V. Секта Богомилів і єї вплив на розширенє апо- | V. Секта Богомилів і її вплив на розширенє апо- | Unresolved: єї / її. |
| 41 | крифів по Словянщинї. Розширенє апокріфічних оповідань по | крїфів по Словянщинї. Розширенє апокріфічних оповідань по | Unresolved: крифів / крїфів. |
| 42 | Словянщинї тісно звязане с повстанєм і розвоєм секти Богомилів | Словянщинї тїсно звязане с повстанєм і розвоєм секти Богомилів | Unresolved: тісно / тїсно. |

## Agreements also requiring audit

Exact agreements in the frozen line strings do NOT validate historic punctuation, Greek accents, or physical bboxes. Representative visually re-inspected agreements: physical lines 1 (folio XI), 5 (Fr. X. Funck citation), 13 (first paragraph boundary), 17 (introductory apocrypha-list line), 29 (end of Simeon paragraph), 33 (Jagić), 36 (South Slav bibliographic continuation), 37 (academy imprint). These are spot checks of visible page structure and physical line coverage, **not** a full independent reviewer sign-off. The other reader's folio bbox appears on the left whereas the scan's roman folio **XI is at upper right**: pixel geometry must be checked, not trusted from metadata.

## Blockers, QA and next actions

1. Preserve the exact first responses from both branches. Do not silently patch Greek, Russian or Ukrainian letters in a frozen first-read artifact or promote agreement to 'verified'.
2. A third agent must inspect the **actual native JPEG and selected magnified crops**, address these disagreements and sample agreements, annotate all historic accents, and produce separate line-level decisions/remaining alternatives. Special priority: lines 24/26/27 where normalization or obvious transcription error is plausible.
3. Verify full-page line geometry and potential historical Unicode normalization; TEI P5 RNG passes structural serialization only. For scholarly completion: page-wide third-party inspection, full TEI Schematron, and TEI→TF source-backed Unicode roundtrip.
4. Frozen development pages cannot be used as holdout for claimed CER. Rights to rehost museum scan are not established by the repository license.

**This comparison was performed as a distinct failure-seeking review pass in the same ChatGPT turn after the first output was frozen, not as an independent third reviewing agent.** It must not be recorded as completed #11 blind-review gate.
