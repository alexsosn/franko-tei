"""Build read-only search projections, retaining distinct frozen candidates."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from printed_indexes import build_printed_indexes

from franko_tei.pilot_batch import discover_readings, check_draft_offline
from franko_tei.review_adjudication import check_repository, project_lines, StaleEditorialSource
from franko_tei.review_bundle import blob_sha, git_source_loader
from franko_tei.pilot_tei import PINNED_ASSET_COMMIT

# Physical scan counts in the five immutable asset manifests at this commit.
# These include front matter, blank/scan-only pages, and printed contents.
SCAN_COUNTS = (469, 526, 446, 580, 316)


# This reviewed evidence record is deliberately allowlisted. It is not a
# contributor decision, a new frozen candidate, or proof of image verification.
SUPPLEMENTARY_AUDIT = "reviews/vol1_scan00024_unstamped_facs_20261126.json"


def supplementary_page(pilot, ref):
    """Project the reviewed I/24 photo collation onto its exact alternate blob."""
    audit_path = pilot / SUPPLEMENTARY_AUDIT
    if not audit_path.is_file():
        return None
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if (audit["schema_version"], audit["status"], audit["volume"],
            audit["scan_page"], audit["printed_page"]) != (
            "supplementary-photo-collation-audit-v1", "agent_unverified", "1", 24, "XV"):
        raise ValueError("invalid supplementary page identity")
    photos = [p["sha256"] for p in audit["photographs"]]
    if len(photos) != 2 or len(set(photos)) != 2 or any(
            not re.fullmatch(r"[a-f0-9]{64}", digest) for digest in photos):
        raise ValueError("missing distinct supplementary photograph digests")
    candidates = audit["compared_candidates"]
    expected = ["pilot/vol1_scan00024_single_reading.json",
                "pilot/vol1_scan00024_alternate_reading_01.json"]
    if [c["path"] for c in candidates] != expected:
        raise ValueError("wrong supplementary source paths")
    sources = []
    for c in candidates:
        raw = (pilot / Path(c["path"]).name).read_bytes()
        if blob_sha(raw) != c["blob"]:
            raise ValueError("supplementary source blob changed")
        draft = json.loads(raw)
        check_draft_offline(Path(c["path"]), draft)
        if (draft["volume"], draft["scan_page"], draft["printed_page_observed"]) != ("1", 24, "XV"):
            raise ValueError("supplementary candidate page mismatch")
        if audit["pinned_image"] != dict(asset_commit=draft["asset_commit"],
                                        path=draft["source_image_path"],
                                        sha256=draft["source_image_sha256"]):
            raise ValueError("supplementary pinned image mismatch")
        sources.append(draft)
    def physical(draft):
        return [(reg, line) for reg in draft["reading"]["regions"] for line in reg["lines"]]
    old, chosen = map(physical, sources)
    rows = audit["rows"]
    if len(rows) != len(old) or len(rows) != len(chosen):
        raise ValueError("supplementary row coverage mismatch")
    covered = {identifier for area in sources[1]["reading"]["coverage"]["occlusions"]
               if area["kind"] == "library_stamp" and area["obscures_source_letters"] is True
               for identifier in area["affected_line_ids"]}
    changes, recovered = [], set()
    for evidence, (_, first), (region, line) in zip(rows, old, chosen):
        if (evidence["line_id"] != first["id"] or evidence["line_id"] != line["id"]
                or evidence["first_reading"] != first["text"]
                or evidence["alternate_reading"] != line["text"]
                or type(evidence["obscured_on_pinned_scan"]) is not bool
                or evidence["obscured_on_pinned_scan"] != (line.get("unreadable_suffix") is True)):
            raise ValueError("supplementary row source mismatch")
        literal = evidence["photo_reading"]
        if not isinstance(literal, str) or not literal.strip() or any(
                ch in literal for ch in ("\n", "\r", "\x00", "…")):
            raise ValueError("invalid supplementary text")
        if evidence["obscured_on_pinned_scan"]:
            if (line["id"] not in covered or not line["text"].endswith("…")
                    or not literal.startswith(line["text"][:-1])
                    or len(literal) <= len(line["text"][:-1])
                    or evidence["confidence"] != "suffix_legible_in_both_photos"):
                raise ValueError("invalid stamp recovery")
            recovered.add(line["id"])
        if literal == line["text"]:
            continue
        if region["kind"] != "body" or evidence["confidence"] not in (
                "suffix_legible_in_both_photos", "provisional_visual_collation"):
            raise ValueError("invalid supplementary correction region")
        # These four rows are monolingual. Do not copy stale offsets; reconstruct
        # only when the old lexical span is uniform (the gap marker is neutral).
        linguistic = [s for s in line["language_spans"] if s["language"] != "zxx"]
        if len(linguistic) != 1 or linguistic[0]["start"] != 0 or linguistic[0]["end"] != len(line["text"].rstrip("…")):
            raise ValueError("supplementary row requires explicit language reannotation")
        span = dict(linguistic[0], end=len(literal), uncertain=True)
        changes.append(dict(line_id=line["id"], region_id=region["id"],
                            original=line["text"], text=literal,
                            status="supplementary_correction",
                            language_spans=[span],
                            obscured_on_pinned_scan=evidence["obscured_on_pinned_scan"],
                            photograph_sha256=photos,
                            evidence_url="https://github.com/alexsosn/franko-tei/blob/" + ref + "/pilot/" + SUPPLEMENTARY_AUDIT))
    if recovered != covered or not recovered:
        raise ValueError("supplementary stamp coverage mismatch")
    return dict(volume="1", scan=24, suffix="alternate_reading_01",
                path=expected[1], blob=candidates[1]["blob"], lines=changes)


# Additional reviewed photo records. The record path, expected line IDs and
# page identity are explicit; do not auto-publish arbitrary audit files.
PHOTO_PAGES = {("2", 19): ("XV", {"preface-line-40"}),
               ("4", 19): ("XV", {"preface-line-39", "preface-line-41"}),
               ("1", 418): ("343", {"index-a-l014"})}


def supplementary_partial_pages(pilot, ref):
    pages = []
    for (volume, scan), (folio, required) in PHOTO_PAGES.items():
        stem = f"vol{volume}_scan{scan:05d}"
        evidence_path = f"reviews/{stem}_unstamped_facs_20261126.json"
        audit_path = pilot / evidence_path
        if not audit_path.is_file():
            continue
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        if (audit["schema_version"], audit["status"], audit["volume"],
                audit["scan_page"], audit["printed_page"]) != (
                "supplementary-photo-collation-audit-v2", "agent_unverified", volume, scan, folio):
            raise ValueError("invalid supplementary page identity")
        photos = [p["sha256"] for p in audit["photographs"]]
        if len(photos) != (4 if scan == 418 else 1) or len(set(photos)) != len(photos) or any(
                not re.fullmatch(r"[a-f0-9]{64}", digest) for digest in photos):
            raise ValueError("invalid supplementary photograph digests")
        path = f"pilot/{stem}_single_reading.json"
        raw = (pilot / Path(path).name).read_bytes()
        blob = blob_sha(raw)
        if audit["source"] != dict(path=path, blob=blob):
            raise ValueError("supplementary source blob changed")
        draft = json.loads(raw)
        check_draft_offline(Path(path), draft)
        if (draft["volume"], draft["scan_page"], draft["printed_page_observed"]) != (volume, scan, folio):
            raise ValueError("supplementary source page mismatch")
        if audit["pinned_image"] != dict(asset_commit=draft["asset_commit"],
                                        path=draft["source_image_path"], sha256=draft["source_image_sha256"]):
            raise ValueError("supplementary pinned image mismatch")
        reading = draft["reading"]
        lines = {l["id"]: (reg, l) for reg in reading["regions"] for l in reg["lines"]}
        covered = {identifier for area in reading["coverage"].get("occlusions", [])
                   if area["kind"] == "library_stamp" and area["obscures_source_letters"] is True
                   for identifier in area["affected_line_ids"]}
        changes, seen, recovered = [], set(), set()
        for row in audit["rows"]:
            identifier = row["line_id"]
            if identifier not in lines or identifier in seen:
                raise ValueError("unknown or duplicate supplementary line")
            seen.add(identifier)
            region, line = lines[identifier]
            obscured = line.get("unreadable_suffix") is True
            if (row["region_id"] != region["id"] or row["original"] != line["text"]
                    or type(row["obscured_on_pinned_scan"]) is not bool
                    or row["obscured_on_pinned_scan"] != obscured):
                raise ValueError("supplementary row source mismatch")
            literal = row["photo_reading"]
            if row["status"] == "collation_only":
                if literal != line["text"] or obscured:
                    raise ValueError("invalid confirmation-only row")
                continue
            if (row["status"] != "correction" or region["kind"] != "body" or identifier not in required
                    or not isinstance(literal, str) or not literal.strip() or literal == line["text"]
                    or any(ch in literal for ch in ("\n", "\r", "\x00", "…"))):
                raise ValueError("invalid supplementary correction")
            if obscured:
                prefix = line["text"].removesuffix("…")
                if (identifier not in covered or not line["text"].endswith("…")
                        or not literal.startswith(prefix) or len(literal) <= len(prefix)):
                    raise ValueError("invalid stamp recovery")
                recovered.add(identifier)
            spans = row["language_spans"]
            end = 0
            for span in spans:
                if (span["start"] != end or type(span["end"]) is not int or not end < span["end"] <= len(literal)
                        or span["text_version"] != reading["reader_id"] or span["uncertain"] is not True
                        or (span["language"], span["script"]) not in
                        {("uk", "Cyrl"), ("ru", "Cyrl"), ("de", "Latn"), ("zxx", "Zyyy")}):
                    raise ValueError("invalid supplementary span")
                end = span["end"]
            if end != len(literal):
                raise ValueError("incomplete supplementary spans")
            changes.append(dict(line_id=identifier, region_id=region["id"], original=line["text"],
                                text=literal, status="supplementary_correction", language_spans=spans,
                                obscured_on_pinned_scan=obscured, photograph_sha256=photos,
                                evidence_url=f"https://github.com/alexsosn/franko-tei/blob/{ref}/pilot/{evidence_path}"))
        if recovered != covered or {row["line_id"] for row in changes} != required:
            raise ValueError("incomplete supplementary recovery")
        pages.append(dict(volume=volume, scan=scan, suffix="single_reading",
                          path=path, blob=blob, lines=changes))
    return pages


def build(pilot, output, ref):
    if not re.fullmatch(r"[a-f0-9]{40}", ref):
        raise ValueError("expected exact source commit SHA")
    entries = {str(v): [] for v in range(1, 6)}
    repo = pilot.resolve().parent
    ledger = check_repository(repo, ref)
    source_loader = git_source_loader(repo, ref)
    pages, unavailable = [], []
    supplements = {p['path']: p for p in supplementary_partial_pages(pilot, ref)}
    first_supplement = supplementary_page(pilot, ref)
    if first_supplement:
        supplements[first_supplement['path']] = first_supplement
    affected = {key[0] for key in ledger}
    if supplements.keys() & affected:
        raise ValueError('supplementary and contributor projections require explicit reconciliation')
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
        supplement = supplements.get(candidate_path)
        if supplement:
            pages.append(supplement)
            replacements = {r['line_id']: r['text'] for r in supplement['lines']}
            corrected = '\n'.join(replacements.get(line['id'], line['text'])
                                  for region in draft['reading']['regions'] for line in region['lines'])
            entries[volume].append(dict(scan=scan, suffix=suffix, text=corrected, reviewed=True))
        if candidate_path in affected:
            seen.add(candidate_path)
            try:
                rows = project_lines(raw, candidate_path, ledger, source_loader=source_loader,
                                     projection_commit=ref)
            except StaleEditorialSource:
                unavailable.append({"path": candidate_path, "reason": "source_blob_changed"})
                continue
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
    (output / "printed-indexes.json").write_text(
        json.dumps(build_printed_indexes(pilot, ref, supplements), ensure_ascii=False, separators=(",", ":")), encoding="utf-8",
    )
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
