"""Build read-only search projections, retaining distinct frozen candidates."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from franko_tei.pilot_batch import discover_readings, check_draft_offline
from franko_tei.review_adjudication import check_repository, project_lines
from franko_tei.review_bundle import blob_sha
from franko_tei.pilot_tei import PINNED_ASSET_COMMIT

# Physical scan counts in the five immutable asset manifests at this commit.
# These include front matter, blank/scan-only pages, and printed contents.
SCAN_COUNTS = (469, 526, 446, 580, 316)


def build(pilot, output, ref):
    if not re.fullmatch(r"[a-f0-9]{40}", ref):
        raise ValueError("expected exact source commit SHA")
    entries = {str(v): [] for v in range(1, 6)}
    repo = pilot.resolve().parent
    ledger = check_repository(repo, ref)
    pages, unavailable = [], []
    affected = {key[0] for key in ledger}
    seen = set()
    for path in discover_readings(pilot):
        raw = path.read_bytes()
        draft = json.loads(raw.decode("utf-8"))
        check_draft_offline(path, draft)
        volume, scan = draft["volume"], draft["scan_page"]
        suffix = path.stem.split("_", 2)[2]
        text = "\n".join(line["text"] for region in draft["reading"]["regions"] for line in region["lines"])
        entries[volume].append(dict(scan=scan, suffix=suffix, text=text))
        candidate_path = "pilot/" + path.name
        if candidate_path in affected:
            seen.add(candidate_path)
            targets = [value["event"]["target"] for key, value in ledger.items() if key[0] == candidate_path]
            if any(t["candidate_blob"] != blob_sha(raw) for t in targets):
                unavailable.append({"path": candidate_path, "reason": "source_blob_changed"})
                continue
            rows = project_lines(raw, candidate_path, ledger)
            accepted = [dict(r, contributor_login=ledger[(candidate_path, r["line_id"])]["submitter"]["login_at_intake"],
                             review_reason=ledger[(candidate_path, r["line_id"])]["adjudication"]["reason"])
                        for r in rows if r["status"] != "agent_unverified"]
            pages.append(dict(volume=volume, scan=scan, suffix=suffix, path=candidate_path,
                              blob=blob_sha(raw), lines=accepted))
            corrected = "\n".join(r["text"] for r in rows)
            if corrected != text:
                entries[volume].append(dict(scan=scan, suffix=suffix, text=corrected, reviewed=True))
    unavailable.extend({"path": p, "reason": "source_missing"} for p in sorted(affected-seen))
    volumes = {}
    for volume, rows in entries.items():
        total = SCAN_COUNTS[int(volume)-1]
        counts = {}
        for row in rows:
            if row.get("reviewed"):
                continue
            scan = row["scan"]
            if type(scan) is not int or not 1 <= scan <= total:
                raise ValueError(f"candidate outside pinned volume manifest: {volume}/{scan}")
            counts[scan] = counts.get(scan, 0) + 1
        volumes[volume] = dict(total=total, scans=sorted(counts),
                               candidates=sum(counts.values()),
                               multiple=sorted(n for n,c in counts.items() if c > 1))
    output.mkdir(parents=True, exist_ok=True)
    (output / "coverage.json").write_text(
        json.dumps(dict(ref=ref, asset_commit=PINNED_ASSET_COMMIT, volumes=volumes),
                   separators=(",", ":")), encoding="utf-8",
    )
    (output / "editorial.json").write_text(json.dumps(dict(ref=ref, pages=pages, unavailable=unavailable), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for volume, rows in entries.items():
        (output / f"vol{volume}.json").write_text(
            json.dumps(dict(ref=ref, volume=volume, entries=rows), ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, default=Path("pilot"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ref = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    build(args.pilot, args.output, ref)
