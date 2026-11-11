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

`.github/workflows/source-recon.yml` is a manually dispatched reconnaissance task; it is deliberately not a required PR check, because access to the museum download server is currently restricted from GitHub Actions. The runner keeps scan bytes transiently and uploads **only** the JSON audit report; it does not rehost scan images. Site availability, source server response and GitHub Actions egress are not guaranteed. If unavailable, log the explicit failure and evaluate an alternate authorized source; never fabricate hashes.

The first GitHub runner attempt (Source reconnaissance run 43014586524, PR #9) failed before downloading because Python could not encode a raw Unicode filename in the HTTP request. The downloader now percent-encodes it. The second runner attempt (run 43014952677, 2026-11-11) reached the museum server but received **HTTP 403 Forbidden**. This is an external source-access blocker, **not** evidence of a completed PDF download. CI for all local code/tests passed separately (run 43014952673, Python 3.10 and 3.12). Until an authorized PDF is available, SHA256, page counts, text-layer metadata and quality evaluation must remain unverified. Agents may inspect an authorized locally acquired copy using `franko-tei inspect-scan --volume N --pdf /path/to/volume.pdf --output local/volume.json`, but must record its URL/provenance independently and never silently claim it came from a blocked museum URL. The scan is deliberately not checked into Git or uploaded to GitHub Actions artifacts.
