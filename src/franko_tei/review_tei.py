"""Separate, provisional editorial TEI; frozen candidate XML remains immutable."""
import argparse
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

from .pilot_tei import (XML, tag, xml_id, _sub, render_pilot_tei,
                        extract_transcribed_lines, validate_single_draft)
from .pilot_tf_batch import _verify_pinned_manifest
from .review_adjudication import check_repository, project_lines
from .review_bundle import REPO, SHA, PATH, match, git_source_loader

ID = "{"+XML+"}id"
WEB = "https://github.com/" + REPO


def render_editorial_tei(raw, path, ledger, width, height, revision, *, source_loader=None):
    """Project a validated ledger; the lower-level serializer does not check images.

    Source notes on corrected lines retain their original literal and identity,
    but are explicitly about the source reading, not offsets into the new text.
    """
    match(SHA, revision, "editorial projection revision")
    rows = project_lines(raw, path, ledger, source_loader=source_loader, projection_commit=revision)
    source = json.loads(raw.decode("utf-8"))
    original = render_pilot_tei(source, width, height)
    if extract_transcribed_lines(original) != [r["original"] for r in rows]:
        raise ValueError("frozen TEI text roundtrip failed")
    accepted = [r for r in rows if r["status"] != "agent_unverified"]
    if not accepted:
        return original
    root = ET.fromstring(original)
    page = root.find("./"+tag("text")+"/"+tag("body")+"/"+tag("div"))
    prefix = f'lb-v{source["volume"]}-s{source["scan_page"]:05d}-'
    anchors = {}
    for parent in page:
        if parent.tag != tag("ab") and not (
                parent.tag == tag("note") and parent.get("type") == "source-footnote"):
            continue
        for index, child in enumerate(parent):
            if child.tag == tag("lb"):
                ident = child.get(ID)
                if ident in anchors:
                    raise ValueError("duplicate physical line ID")
                anchors[ident] = (parent, child)
    for row in accepted:
        ident = prefix+row["line_id"]
        parent, lb = anchors[ident]
        entry = ledger[(path, row["line_id"])]
        if row["status"] == "accepted_correction":
            siblings = list(parent)
            for child in siblings[siblings.index(lb)+1:]:
                if child.tag == tag("lb"):
                    break
                if child.tag != tag("seg") or child.get("type") != "language-attribution" or len(child):
                    raise ValueError("correction would remove structural markup")
                parent.remove(child)
            lb.tail = row["text"]
            for note in page.findall(tag("note")):
                if (note.get("type") == "agent-reading-uncertainty"
                        and note.get("corresp") == "#"+ident):
                    note.set("subtype", "source-reading-needs-reassessment")
        note = _sub(page, "note", attrs={
            "type": "editorial-review", "subtype": row["status"],
            "corresp": "#"+ident,
            "source": WEB+"/blob/"+row["source_commit"]+"/"+path,
        })
        xml_id(note, "review-"+row["event_id"])
        _sub(note, "quote", row["original"], {"type":"frozen-source-reading"})
        _sub(note, "seg", row["review_kind"], {"type":"review-kind"})
        _sub(note, "seg", str(row["contributor_id"]), {"type":"contributor-github-id"})
        _sub(note, "seg", row["language_status"], {"type":"language-status"})
        _sub(note, "seg", row["uncertainty_status"], {"type":"uncertainty-status"})
        _sub(note, "ref", "Submitted review", {
            "type":"review-issue", "target":row["issue_url"]})
        _sub(note, "ref", row["bundle_id"], {
            "type":"intake-record", "target":WEB+"/blob/"+revision+
            "/reviews/intake/"+row["bundle_id"]+".json"})
        _sub(note, "ref", row["event_id"], {
            "type":"adjudication-record", "target":WEB+"/blob/"+revision+
            "/reviews/adjudications/"+row["event_id"]+".json"})
        if "source_revision" in row:
            provenance = row["source_revision"]
            _sub(note, "ref", "Annotation-only source revision", {
                "type": "annotation-source-revision",
                "target": WEB+"/blob/"+provenance["projected_commit"]+"/"+path})
            _sub(note, "seg", provenance["accepted_blob"], {"type":"accepted-source-blob"})
            _sub(note, "seg", provenance["projected_blob"], {"type":"projected-source-blob"})
        _sub(note, "seg", entry["adjudication"]["reason"], {"type":"review-reason"})
    header = root.find(tag("teiHeader"))
    encoding = header.find(tag("encodingDesc"))
    _sub(encoding, "p", "Provisional editorial projection from accepted line decisions. "
         "Original literals remain in editorial-review notes; corrected language "
         "spans are withheld and source uncertainty needs reassessment. "
         "Acceptance is not page verification. See immutable ledger records.")
    _sub(header.find(tag("revisionDesc")), "change",
         "Projected accepted line decisions from Git revision "+revision+".")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(root, encoding="unicode")+'\n'
    if extract_transcribed_lines(xml) != [r["text"] for r in rows]:
        raise ValueError("editorial TEI text roundtrip failed")
    return xml


def _git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], timeout=30)


def ledger_at_checkout(repo, revision):
    """Only a checkout of the named trusted snapshot; no uncommitted ledger data."""
    match(SHA, revision, "trusted checkout revision")
    if _git(repo, "rev-parse", "HEAD").decode().strip() != revision:
        raise ValueError("checkout must match projection revision")
    # check_repository compares every committed record's bytes; exact path sets
    # additionally reject added records, including ignored/untracked files.
    roots = ("reviews/intake", "reviews/adjudications")
    committed = {p.decode("utf-8") for p in _git(
        repo, "ls-tree", "-r", "-z", "--name-only", revision, "--", *roots
    ).split(b"\0") if p}
    local = {p.relative_to(repo).as_posix() for folder in roots
             for p in (repo/folder).glob("*")}
    if committed != local:
        raise ValueError("ledger checkout contains uncommitted records")
    return check_repository(repo, revision, revision)


def verified_editorial_tei(repo, path, images_root, revision):
    """Read candidate from Git and authenticate pinned manifest and native image."""
    repo = Path(repo).resolve()
    match(PATH, path, "candidate path")
    ledger = ledger_at_checkout(repo, revision)
    loader = git_source_loader(repo, revision)
    raw = loader(revision, path)
    source = json.loads(raw.decode("utf-8"))
    _verify_pinned_manifest(source["volume"], images_root)
    dimensions = validate_single_draft(source, images_root)
    return render_editorial_tei(raw, path, ledger, dimensions["width"],
                                dimensions["height"], revision, source_loader=loader)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--revision", required=True,
                        help="Exact trusted main-history commit checked out locally")
    parser.add_argument("--candidate", required=True, help="Repository-relative pilot JSON path")
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        xml = verified_editorial_tei(args.repo, args.candidate, args.images, args.revision)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as out:
            out.write(xml)
    except (ValueError, OSError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    print(f"Wrote {args.output}; provisional, not a verified edition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
