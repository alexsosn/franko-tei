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

## Bounded source reconnaissance

`franko-tei fetch-scan --volume 3 --output scans/vol3.pdf` downloads exactly the declared museum PDF locally, validates PDF magic and allowed final redirect host, limits the transfer to 1 GB, and returns a SHA256. `franko-tei inspect-scan --volume 3 --pdf scans/vol3.pdf --output audit/vol3.json` records physical PDF page count and per-page embedded text length. These measurements **do not verify text correctness**, printed pagination, rights or image completeness.

`.github/workflows/source-recon.yml` allows manually selecting any volume and performs a bounded reconnaissance of volume III when the workflow/code changes in a PR. The runner keeps scan bytes transiently and uploads **only** the JSON audit report; it does not rehost scan images. Site availability, source server response and GitHub Actions egress are not guaranteed. If unavailable, log the explicit failure and evaluate an alternate authorized source; never fabricate hashes.
