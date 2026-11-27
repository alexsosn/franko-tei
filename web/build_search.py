"""Build read-only search projections, retaining distinct frozen candidates."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from printed_indexes import build_printed_indexes

from franko_tei.pilot_batch import discover_readings, check_draft_offline
from franko_tei.search_annotations import project_search_entry
from franko_tei.review_adjudication import check_repository, project_lines, StaleEditorialSource
from franko_tei.review_bundle import blob_sha, git_source_loader
from franko_tei.pilot_tei import PINNED_ASSET_COMMIT
from franko_tei.native_collation import CANDIDATE as NATIVE_CANDIDATE, load_native_collation

# Physical scan counts in the five immutable asset manifests at this commit.
# These include front matter, blank/scan-only pages, and printed contents.
SCAN_COUNTS = (469, 526, 446, 580, 316)


# Re-export existing helper names for callers/tests; one validation path.
from franko_tei.supplementary import (SUPPLEMENTARY_AUDIT, supplementary_page,
                                     supplementary_partial_pages, supplementary_pages)


def build(pilot, output, ref):
    if not re.fullmatch(r"[a-f0-9]{40}", ref):
        raise ValueError("expected exact source commit SHA")
    entries = {str(v): [] for v in range(1, 6)}
    repo = pilot.resolve().parent
    ledger = check_repository(repo, ref)
    source_loader = git_source_loader(repo, ref)
    pages, unavailable = [], []
    supplements = supplementary_pages(pilot, ref)
    collation = load_native_collation(repo, ref, NATIVE_CANDIDATE)
    affected = {key[0] for key in ledger} | {NATIVE_CANDIDATE}
    if supplements.keys() & affected:
        raise ValueError('supplementary and contributor projections require explicit reconciliation')
    seen = set()
    for path in discover_readings(pilot):
        raw = path.read_bytes()
        draft = json.loads(raw.decode("utf-8"))
        check_draft_offline(path, draft)
        volume, scan = draft["volume"], draft["scan_page"]
        suffix = path.stem.split("_", 2)[2]
        raw_entry = project_search_entry(draft, suffix, blob_sha(raw))
        entries[volume].append(raw_entry)
        candidate_path = "pilot/" + path.name
        supplement = supplements.get(candidate_path)
        if supplement:
            pages.append(supplement)
            entries[volume].append(project_search_entry(draft, suffix, blob_sha(raw),
                                                       supplement['lines']))
        if candidate_path in affected:
            seen.add(candidate_path)
            try:
                rows = project_lines(raw, candidate_path, ledger, source_loader=source_loader,
                                     projection_commit=ref,
                                     collation=collation if candidate_path == NATIVE_CANDIDATE else None)
            except StaleEditorialSource:
                unavailable.append({"path": candidate_path, "reason": "source_blob_changed"})
                continue
            accepted = []
            for row in rows:
                if row["status"] == "agent_unverified":
                    continue
                entry = ledger.get((candidate_path, row["line_id"]))
                if entry is not None:
                    row = dict(row, contributor_login=entry["submitter"]["login_at_intake"],
                               review_reason=entry["adjudication"]["reason"])
                accepted.append(row)
            pages.append(dict(volume=volume, scan=scan, suffix=suffix, path=candidate_path,
                              blob=blob_sha(raw), lines=accepted))
            projected = project_search_entry(draft, suffix, blob_sha(raw), accepted)
            if projected.get("reviewed"):
                entries[volume].append(projected)
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
    (output / "printed-indexes.json").write_text(
        json.dumps(build_printed_indexes(pilot, ref, supplements,
                                         editorial={p["path"]: p for p in pages}), ensure_ascii=False, separators=(",", ":")), encoding="utf-8",
    )
    (output / "coverage.json").write_text(
        json.dumps(dict(ref=ref, asset_commit=PINNED_ASSET_COMMIT, volumes=volumes),
                   separators=(",", ":")), encoding="utf-8",
    )
    (output / "editorial.json").write_text(json.dumps(dict(ref=ref, pages=pages, unavailable=unavailable), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for volume, rows in entries.items():
        # Load annotations only on demand; ordinary literal search keeps its
        # original compact payload and record contract.
        available = {(p["scan"], p["suffix"]) for p in pages if p["volume"] == volume}
        stale = {p["path"] for p in unavailable}
        literal = []
        for row in rows:
            entry = {k: v for k, v in row.items() if k != "annotation"}
            a = row["annotation"]
            path = f'pilot/vol{volume}_scan{row["scan"]:05d}_{row["suffix"]}.json'
            entry.update(model_id=a["model_id"], model_version=a["model_version"],
                         candidate_blob=a["candidate_blob"], reader_id=a["reader_id"],
                         editorial=("available" if (row["scan"], row["suffix"]) in available
                                    else "unavailable" if path in stale else "none"))
            literal.append(entry)
        annotations = [{k: v for k, v in row.items() if k != "text"} for row in rows]
        (output / f"vol{volume}.json").write_text(
            json.dumps(dict(ref=ref, volume=volume, entries=literal), ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        (output / f"annotation-vol{volume}.json").write_text(
            json.dumps(dict(schema_version="search-annotation-v1", ref=ref, volume=volume,
                            offset_unit="unicode_code_point", entries=annotations),
                       ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, default=Path("pilot"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ref = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    build(args.pilot, args.output, ref)
