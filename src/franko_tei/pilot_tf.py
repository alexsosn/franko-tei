"""Fail-closed Text-Fabric export of an image-anchored, single-reader TEI pilot.

Requires both the exact regenerated TEI document and its original working-draft
JSON. XML supplies text and TEI IDs; JSON retains span script/offsets not yet
encoded in this TEI schema. Output remains agent_unverified.
"""
import argparse
import json
from pathlib import Path
import tempfile
from xml.etree import ElementTree as ET

from .pilot_tei import (
    TEI, XML, extract_transcribed_lines, render_pilot_tei,
    tag, validate_single_draft,
)


def _xid(node):
    return node.get(f"{{{XML}}}id")


def compile_graph(xml, payload, image_width, image_height):
    """Return (nodeFeatures, edgeFeatures, metaData), without writing to disk.

    Every slot is one unchanged Unicode code point. Physical line separators
    are explicit newline slots belonging to the page, not to either line.
    TEI links and source metadata remain on ordinary TF nodes/features.
    """
    if not isinstance(payload, dict) or payload.get("status") != "agent_unverified":
        raise ValueError("Text-Fabric pilot requires agent_unverified source evidence")
    if payload.get("schema_version") != "single-image-draft-v0":
        raise ValueError("Text-Fabric pilot requires a single-image-draft-v0 reading")
    if not isinstance(xml, str) or xml != render_pilot_tei(payload, image_width, image_height):
        raise ValueError("TEI must exactly reproduce validated, unverified source draft")
    root = ET.fromstring(xml)
    if root.tag != tag("TEI"):
        raise ValueError("TEI namespace missing")
    div = root.find(f"./{tag('text')}/{tag('body')}/{tag('div')}")
    surf = root.find(f"./{tag('facsimile')}/{tag('surface')}")
    if div is None or surf is None:
        raise ValueError("required TEI page/facsimile structure missing")
    graphic = surf.find(tag("graphic"))
    if graphic is None or not graphic.get("url"):
        raise ValueError("TEI facsimile graphic link missing")

    regions = payload["reading"]["regions"]
    abs_ = div.findall(tag("ab"))
    if len(abs_) != len(regions):
        raise ValueError("TEI region coverage differs from evidence")
    source_lines = [line for region in regions for line in region["lines"]]
    text_lines = extract_transcribed_lines(xml)
    if len(source_lines) != len(text_lines) or any(
            source["text"] != actual for source, actual in zip(source_lines, text_lines)):
        raise ValueError("TEI line content differs from evidence")
    raw = "\n".join(text_lines)
    if payload["reading"].get("raw_response") != raw:
        raise ValueError("first reading text order or contents changed")
    if not raw:
        raise ValueError("cannot export an empty page as a character-slot corpus")

    # Every original code point, including spaces, combining marks and physical
    # line-break delimiters, becomes a slot. Do not run NFC or tokenization.
    nf = {
        "otype": {n: "char" for n in range(1, len(raw) + 1)},
        "ch": {n: ch for n, ch in enumerate(raw, 1)},
    }
    oslots = {}
    next_node = len(raw) + 1

    def feature(name, node, value):
        # Null unknown labels do not become fake language/script assertions.
        if value is not None:
            nf.setdefault(name, {})[node] = value

    def node(kind, slots, **features):
        nonlocal next_node
        if not slots:
            raise ValueError(f"{kind}: non-slot node cannot be empty")
        result = next_node
        next_node += 1
        nf["otype"][result] = kind
        oslots[result] = set(slots)
        for key, value in features.items():
            feature(key, result, value)
        return result

    cursor = 1
    lines = []
    parsed_regions = []
    for region, ab in zip(regions, abs_):
        lbs = ab.findall(tag("lb"))
        if len(lbs) != len(region["lines"]):
            raise ValueError("TEI line anchor count differs from evidence")
        region_slots = []
        for source, lb in zip(region["lines"], lbs):
            physical_text = text_lines[len(lines)]
            slots = tuple(range(cursor, cursor + len(physical_text)))
            if "".join(nf["ch"][s] for s in slots) != physical_text:
                raise ValueError("physical line character slots lost fidelity")
            cursor += len(physical_text)
            if len(lines) < len(source_lines) - 1:
                if nf["ch"].get(cursor) != "\n":
                    raise ValueError("physical line delimiter is missing")
                cursor += 1
            line_id = _xid(lb)
            if not line_id or lb.get("facs", "")[0:1] != "#":
                raise ValueError("missing TEI line/facsimile identity")
            if lb.get("facs", "")[1:] != f"zone-v{payload['volume']}-s{payload['scan_page']:05d}-line-{source['id']}":
                raise ValueError("TEI line facsimile identity differs from source")
            lines.append({"source": source, "slots": slots, "xmlId": line_id,
                          "facs": lb.get("facs"), "region": region["id"]})
            region_slots.extend(slots)
        if not _xid(ab) or not ab.get("facs", "").startswith("#"):
            raise ValueError("TEI region identity/facsimile missing")
        parsed_regions.append({"source": region, "slots": tuple(region_slots),
                               "xmlId": _xid(ab), "facs": ab.get("facs")})
    if cursor != len(raw) + 1:
        raise ValueError("character slots do not account for all physical lines")
    ids = [_xid(root), _xid(surf), _xid(div)]
    ids += [r["xmlId"] for r in parsed_regions] + [l["xmlId"] for l in lines]
    if any(not s for s in ids) or len(ids) != len(set(ids)):
        raise ValueError("missing/duplicate TEI IDs")

    # Language labels/spans are backed by the exact same versioned original
    # reading; script labels are carried from JSON because pilot TEI v0 has
    # not yet serialized ISO 15924 script identifiers.
    for line in lines:
        spans = line["source"]["language_spans"]
        for position, span in enumerate(spans, 1):
            subset = line["slots"][span["start"]:span["end"]]
            if len(subset) != span["end"] - span["start"]:
                raise ValueError("language span is outside line")
            node("language_span", subset,
                 lineTeiId=line["xmlId"], spanOrdinal=position,
                 startOffset=span["start"], endOffset=span["end"],
                 lang=span["language"], script=span["script"],
                 languageUncertain="yes" if span["uncertain"] else "no",
                 textVersion=span["text_version"],
                 status="agent_unverified")

    for index, line in enumerate(lines, 1):
        x, y, w, h = line["source"]["bbox_xywh"]
        node("line", line["slots"],
             teiId=line["xmlId"], facs=line["facs"], lineOrdinal=index,
             lineSourceId=line["source"]["id"], readingId=payload["reading"]["reader_id"],
             geometryEstimated="yes" if line["source"]["geometry_estimated"] else "no",
             ulx=str(x), uly=str(y), lrx=str(x+w), lry=str(y+h),
             status="agent_unverified")

    for region in parsed_regions:
        x, y, w, h = region["source"]["bbox_xywh"]
        node("region", region["slots"],
             teiId=region["xmlId"], facs=region["facs"],
             regionSourceId=region["source"]["id"], regionKind=region["source"]["kind"],
             geometryEstimated="yes" if region["source"]["geometry_estimated"] else "no",
             ulx=str(x), uly=str(y), lrx=str(x+w), lry=str(y+h),
             status="agent_unverified")

    # Transcription uncertainty is an audit annotation linked to the affected
    # physical line, never a manuscript textual variant or an attested witness.
    by_lb = {line["xmlId"]: line["slots"] for line in lines}
    notes = div.findall(tag("note"))
    if len(notes) != len(payload["reading"]["uncertainty_notes"]):
        raise ValueError("TEI uncertainty annotations do not match reading")
    for annotation in notes:
        link = annotation.get("corresp", "")
        if not link.startswith("#") or link[1:] not in by_lb:
            raise ValueError("unresolved uncertainty line reference")
        if annotation.get("type") != "agent-reading-uncertainty" or not _xid(annotation):
            raise ValueError("unexpected TEI note type or identity")
        node("uncertainty", by_lb[link[1:]],
             teiId=_xid(annotation), lineTeiId=link[1:],
             noteText=annotation.text, status="agent_unverified")

    # Printed page label is observed image text; @pb/@div n encode *scan*
    # index in the current pilot TEI. Never infer foliation from this index.
    node("page", range(1, len(raw) + 1),
         teiId=_xid(div), facs=div.get("facs"),
         scanPage=payload["scan_page"], volume=int(payload["volume"]),
         printedPageObserved=payload.get("printed_page_observed"),
         sourceImageSha256=payload["source_image_sha256"],
         sourcePdfSha256Claim=payload["source_pdf_sha256_claimed_by_manifest"],
         sourceImagePath=payload["source_image_path"],
         sourceImageUri=graphic.get("url"),
         sourceAssetCommit=payload["asset_commit"],
         readingId=payload["reading"]["reader_id"],
         readingContextId=payload["reading"]["context_id"],
         readerModelId=payload["reading"]["model_id"],
         status="agent_unverified")

    if max(nf["otype"]) != len(nf["otype"]):
        raise ValueError("TF node IDs must be dense")
    # Geometry is written as numeric-string coordinate values: TF supports
    # int/string, not floats. Never truncate estimated fractional source boxes.
    # Feature metadata is checked by Fabric.save: no opaque JSON blobs or None.
    integers = {"volume", "scanPage",
                "lineOrdinal", "spanOrdinal", "startOffset", "endOffset"}
    meta = {name: {"valueType": "int" if name in integers else "str"} for name in nf}
    meta["oslots"] = {"valueType": "str"}
    meta["otext"] = {"fmt:text-orig-full": "{ch}"}
    meta[""] = {
        "source": "franko-tei: image-anchored single-reader TEI pilot",
        "status": "agent_unverified",
        "description": "Working first reading; no independent review or released scholarly edition",
    }
    return nf, {"oslots": oslots}, meta


def export_to_tf(graph, output, expected_text, expected_lines, expected_image_sha):
    """Atomic save and real Fabric reload/roundtrip; never overwrite."""
    from tf.fabric import Fabric

    output = Path(output)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite Text-Fabric pilot: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    nf, ef, meta = graph
    with tempfile.TemporaryDirectory(prefix=".pilot-tf-", dir=output.parent) as parent:
        stage = Path(parent) / "tf"
        stage.mkdir()
        tf = Fabric(locations=str(stage), silent="deep")
        if not tf.save(nodeFeatures=nf, edgeFeatures=ef, metaData=meta,
                       location=str(stage), silent="deep"):
            raise RuntimeError("Text-Fabric save failed")
        reloaded = Fabric(locations=str(stage), silent="deep").load(
            "otype oslots ch teiId scanPage sourceImageSha256 status", silent="deep")
        if not reloaded:
            raise RuntimeError("Text-Fabric load failed")
        F, E = reloaded.F, reloaded.E
        actual = "".join(F.ch.v(i) for i in range(1, F.otype.maxSlot + 1))
        if actual != expected_text:
            raise ValueError("Text-Fabric exact page code-point roundtrip failed")
        if ["".join(F.ch.v(s) for s in sorted(E.oslots.s(n)))
            for n in F.otype.s("line")] != expected_lines:
            raise ValueError("Text-Fabric physical line roundtrip failed")
        pages = F.otype.s("page")
        if len(pages) != 1 or F.sourceImageSha256.v(pages[0]) != expected_image_sha:
            raise ValueError("Text-Fabric page source provenance lost")
        if F.status.v(pages[0]) != "agent_unverified":
            raise ValueError("Text-Fabric verification status was changed")
        if output.exists():
            raise FileExistsError("output appeared concurrently")
        stage.rename(output)
    return len(expected_lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--tei", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise FileExistsError("refusing to overwrite existing Text-Fabric output")
        payload = json.loads(args.evidence.read_text(encoding="utf8"))
        dimensions = validate_single_draft(payload, args.images)
        xml = args.tei.read_text(encoding="utf8")
        graph = compile_graph(xml, payload, dimensions["width"], dimensions["height"])
        lines = extract_transcribed_lines(xml)
        count = export_to_tf(graph, args.output, "\n".join(lines), lines,
                             dimensions["image_sha256"])
    except (ValueError, KeyError, TypeError, OSError, RuntimeError, ImportError) as exc:
        parser.error(str(exc))
    print(f"Saved and reloaded {count} lines of agent_unverified pilot TF at {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
