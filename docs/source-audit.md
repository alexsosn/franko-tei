# Source research 2026-11-11

The five landing pages in `src/franko_tei/sources.json` were located at the official Дім Франка museum site and linked to the corresponding PDF URLs (vols. I–V, 1896/1899/1902/1906/1910). Volume III's PDF text layer is accessible to online textual indexing and displays severe errors even in title-page text, e.g. `ANOKPIÓK I ЛЕГЕНДИ` for the title. Do not treat that OCR as ground truth.

Evidence:
- Volume I https://dimfranka.lviv.ua/material/апокрифи-і-легенди-з-українських-руко-5
- Volume II https://dimfranka.lviv.ua/material/апокрифи-і-легенди-з-українських-руко-2
- Volume III https://dimfranka.lviv.ua/material/апокрифи-і-легенди-з-українських-руко-4
- Volume IV https://dimfranka.lviv.ua/material/апокрифи-і-легенди-з-українських-руко
- Volume V https://dimfranka.lviv.ua/material/апокрифи-і-легенди-з-українських-руко-3

**Unverified at this point:** actual scan image quality; downloadable complete PDF bytes from this execution environment (network DNS blocked); SHA256; page counts; source file licensing/redistribution rights; printed-page/scan-page mapping; holdout CER; whether content is text layer vs images on each page. The project is not yet a digitized corpus.

Next: download all five externally via the declared URLs, obtain `sha256sum`/PDF page counts, record per-page raw OCR availability and typographic strata, inspect images. Check permissions before mirroring scans. Curate line-level diplomatic holdout before picking an OCR engine.

Franko's original editorial practice involved interventions and different manuscript versions. These need structural treatment, not only character-perfect OCR. See TEI critical apparatus guidelines.
