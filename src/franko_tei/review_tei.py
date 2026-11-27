"""Current diplomatic working TEI; editorial history stays in Git."""
import argparse
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

from .pilot_tei import (XML, tag, xml_id, _sub, render_pilot_tei,
                        extract_transcribed_lines, validate_single_draft)
from .pilot_tf_batch import _verify_pinned_manifest
from .review_adjudication import check_repository, project_lines
from .review_bundle import SHA, PATH, match, git_source_loader
from .native_collation import load_native_collation

ID = "{"+XML+"}id"


def render_editorial_tei(raw, path, ledger, width, height, revision, *, source_loader=None, collation=None):
    """Project a validated ledger; the lower-level serializer does not check images.

    The output contains selected text, source anchors and unresolved reading
    indicators, not an event log. Frozen candidates and the Git ledger remain
    unchanged. A line-level uncertainty does not assert a specific glyph.
    """
    match(SHA, revision, "editorial projection revision")
    match(PATH, path, "candidate path")
    page_key = path.split("_", 2)[:2]
    if any(other != path and other.split("_", 2)[:2] == page_key
           for other, _ in ledger):
        raise ValueError("accepted decisions belong to another candidate on this page")
    rows = project_lines(raw, path, ledger, source_loader=source_loader,
                         projection_commit=revision, collation=collation)
    source = json.loads(raw.decode("utf-8"))
    original = render_pilot_tei(source, width, height)
    if extract_transcribed_lines(original) != [r["original"] for r in rows]:
        raise ValueError("frozen TEI text roundtrip failed")
    accepted = [r for r in rows if r["status"] in {"accepted_correction", "native_collation"}]
    root = ET.fromstring(original)
    page = root.find("./"+tag("text")+"/"+tag("body")+"/"+tag("div"))
    prefix = f'lb-v{source["volume"]}-s{source["scan_page"]:05d}-'
    anchors = {}
    for parent in page:
        if parent.tag != tag("ab") and not (
                parent.tag == tag("note") and parent.get("type") == "source-footnote"):
            continue
        for child in parent:
            if child.tag == tag("lb"):
                ident = child.get(ID)
                if ident in anchors:
                    raise ValueError("duplicate physical line ID")
                anchors[ident] = (parent, child)
    for row in accepted:
        ident = prefix+row["line_id"]
        parent, lb = anchors[ident]
        siblings = list(parent)
        for child in siblings[siblings.index(lb)+1:]:
            if child.tag == tag("lb"):
                break
            # Lexical expansions target the old text and must not survive a
            # correction. Other nested markup remains structurally protected.
            if (child.tag != tag("seg") or child.get("type") != "language-attribution"
                    or any(grand.tag != tag("choice") for grand in child)):
                raise ValueError("correction would remove structural markup")
            parent.remove(child)
        lb.tail = row["text"]

    # Keep unresolved source-line locations, not obsolete literals, model
    # rationales, confirmation events or contributor metadata.
    uncertain = set()
    for note in page.findall(tag("note")):
        if note.get("type") == "agent-reading-uncertainty":
            anchor = note.get("corresp")
            if not anchor or anchor[1:] not in anchors or not anchor.startswith("#"):
                raise ValueError("uncertainty lacks physical line anchor")
            uncertain.add(anchor)
            page.remove(note)
    for anchor in sorted(uncertain):
        n = _sub(page, "note", "Reading requires verification against the printed source.",
                 {"type": "transcription-uncertainty", "corresp": anchor})
        xml_id(n, "uncertainty-"+anchor[1:])

    # A single snapshot identifier suffices to reconstruct the edition from
    # Git; no per-line history or model-specific workflow data is exported.
    header = root.find(tag("teiHeader"))
    fd = header.find(tag("fileDesc"))
    title_stmt = fd.find(tag("titleStmt"))
    title_stmt.find(tag("title")).text = (
        f'Franko, Апокріфи і лєґенди — vol. {source["volume"]}, '
        f'scan {source["scan_page"]} (provisional diplomatic text)')
    for child in title_stmt.findall(tag("respStmt")):
        title_stmt.remove(child)
    edition_stmt = ET.Element(tag("editionStmt"))
    _sub(edition_stmt, "edition", "Current diplomatic working text", {"n": revision})
    fd.insert(list(fd).index(title_stmt)+1, edition_stmt)
    fd.find(tag("publicationStmt")).find(tag("p")).text = (
        "Unreleased working text (agent_unverified); not a verified edition.")
    encoding = header.find(tag("encodingDesc"))
    encoding.clear()
    _sub(encoding, "p", "Diplomatic physical-line transcription of the printed edition. "
         "Geometry is estimated; unresolved readings are indicated by line. "
         "Language ranges requiring reassessment are not asserted.")
    revision_desc = header.find(tag("revisionDesc"))
    if revision_desc is not None:
        header.remove(revision_desc)
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
    return _verified_editorial_page(path, images_root, revision, ledger, loader,
                                    collation=load_native_collation(repo, revision, path))


def _verified_editorial_page(path, images_root, revision, ledger, loader, *, collation=None):
    match(PATH, path, "candidate path")
    raw = loader(revision, path)
    source = json.loads(raw.decode("utf-8"))
    _verify_pinned_manifest(source["volume"], images_root)
    dimensions = validate_single_draft(source, images_root)
    return render_editorial_tei(raw, path, ledger, dimensions["width"],
                                dimensions["height"], revision, source_loader=loader,
                                collation=collation)


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
