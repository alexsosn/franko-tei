# I/43 (XXXIV): complete native-image first reading and in-line Joseph drama dialogue

## Original source / research

Volume I physical scan **43**, original printed folio **XXXIV** at upper left, original 1190×1731 JPEG `images/vol1/page-00043.jpg` at pinned source-asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, actual source JPEG SHA256 `0e11c8d61260f69d4eb2b7f1be2bd9b3ace7b1b5eec4acc7d6275570e9dc47a9`. The PDF SHA stored in JSON is a manifest claim, not a newly rechecked PDF. The text is Franko's printed account of a 1708 Kyiv Joseph drama, **not** a newly inspected 1708 original dramatic manuscript.

The [frozen full direct native-image-first reading](../pilot/vol1_scan00043_single_reading.json) preserves **41 body physical lines plus Roman folio XXXIV**, divided into eight printed text blocks **4+13+1+3+8+3+7+2**. The initial four source lines quote the publication history of `Іосифъ патріарха` and the Tikhonravov `op. cit. II, 356—427` source. The remaining 35 dialogue lines reproduce in-source, asymmetrically positioned labels `П е н т е ф р і й`, `П е н т.`, `В е л м о ж а` and `В е л м.`, their alternating speeches about Joseph's elevation in Egypt and the accusation of Potiphar's wife; the final two prose lines begin a new reference to a Paschal drama, ending mid-sentence `...вся основана на`. Neither the preceding page nor I/44 is allowed to supply or complete any of the first reader's physical lines.

**Structural limitation:** Printed speaker labels share physical lines with dialogue and are spatially staggered. The current pilot serializes each physical line in an `ab type="body"` source zone without TEI `<speaker>`/`<sp>` turn semantics. Splitting labels into fictional extra `lb` source lines would be incorrect; any later dramatic-structure annotation must preserve all 42 original source positions and exact characters. Original boxes and whitespace are **estimated**, not measured glyph boundaries. The first pass includes no footnote, printer signature, source occlusion or separate colophon.

## Research → plan → TDD → source-verified TEI

1. Inspected immutable native original page first and defined layout as 4+13+1+3+8+3+7+2 body lines. Test-only [red-first source contract](../tests/test_vol1_page43_image.py) `e0a7e90d` required page hash, printed Roman folio, all 41 body lines, original source dialogue labels and estimated boxes without false blank overlap. [CI 43191159253](https://github.com/alexsosn/franko-tei/actions/runs/43191159253) deliberately failed because new source data was absent.
2. Froze full original-image-only single-reader response as `b5e1f12f` **before** opening original embedded PDF OCR or a competing I/43 transcription. `reading.raw_response` equals the 42 physical source text positions joined by original line breaks; all source lines have stable IDs and uncertainties. [CI 43191374771](https://github.com/alexsosn/franko-tei/actions/runs/43191374771) passed.
3. [Dedicated source-gated I/43 original JPEG → TEI P5 workflow](../.github/workflows/pilot-vol1-page43.yml) `16d897e3` fetches only immutable original JPEG + original source manifest, rehashes bytes, asserts **one `pb`, 42 `lb`, exact source line strings**, then validates TEI P5 4.12.0 Relax NG; it uploads only a seven-day text-only provisional TEI artifact. [CI 43191428896](https://github.com/alexsosn/franko-tei/actions/runs/43191428896) and [real original JPEG/TEI 43191429159](https://github.com/alexsosn/franko-tei/actions/runs/43191429159) passed.
4. A second red-first review test `f20bc222` demanded a separately anchored post-freeze historical glyph/source challenge record with explicit no-independent-review flags. [CI 43191567299](https://github.com/alexsosn/franko-tei/actions/runs/43191567299) failed for missing review file, while [source JPEG/TEI 43191567363](https://github.com/alexsosn/franko-tei/actions/runs/43191567363) stayed green. Then [provisional original-source challenge JSON](../pilot/reviews/vol1_scan00043_post_freeze_challenges.json) committed `008d30c4` without rewriting the first-reader text. Final PR-head CI and native source gate must also both pass before merge.

The real-byte source workflow, line roundtrip and TEI RNG **certify identity, physical coverage and XML structural validity only**, not the printed historical glyphs, late-eighteenth-century scholarly witnesses or verified dialogue turn semantics.

## Failure-oriented native-image review, post-freeze

After the frozen first full source reading had been persisted, the native image was reexamined specifically for false fluent word replacements. The original embedded PDF OCR was opened **only afterward**, as a fallible negative control: it changes Roman `XXXIV` to `XXXIY`, corrupts Cyrillic into Latin fragments, and even invents additional question-line splits. It is not independent full OCR truth or a blind second reader.

Three competing, **unresolved** source glyph hypotheses are recorded in separate JSON:

- **Body line 13**: `всѣми чтомій` versus possible `всѣми чтимій`, vowel under old type unclear.
- **Body line 16**: `погубить, или` versus possible `погубити, или`, old infinitive ending uncertain.
- **Body line 19**: `Ни ли` versus possible `Нѣ ли`, brief old Russian phrase, yat uncertain.

Additional source doubts include unusual `Ко толицѣй`, `Изійдохъ`, `Премногими азъ прелщахъ`, `Взыскахъ ему отмстити`, punctuation and exact letterspacing of character labels. No outside dramatic edition was used to force a fluent or modernized reconstruction.

**Editorial status** remains `agent_unverified`. One full source-image first reading, a same-context independent-in-objective error search but **no independently blind full second source reader, third external philological adjudication, certified CER, verified TEI/TF/Context Fabric release or primary manuscript attestation**. The source scan/PDF is not redistributed under the software license. #11 and Old Slavonic I/34 defect #66 stay open. The next sequential physical page is **I/44** (printed folio to observe directly rather than infer).
