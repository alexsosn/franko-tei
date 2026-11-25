"""Provisional navigation projection of Franko's printed indexes.

Explicit reviewed-in-draft line partitions; no OCR, no guessed page offsets.
"""
from collections import defaultdict
import hashlib
import json
import re

# Inclusive physical scan ranges; end-line ordinals apply only to the frozen
# first-page reading in each section. The source line arrays remain literal.
SECTIONS = (
    ("names", 416, 430, "gpt62-i416-first-image-20261125",
     {"index-left": [1,2,3,4,5,6,7,10,11,12,14,15,16,17,18,29],
      "index-right": [1,2,3,4,5,6,7,8,9,10,11,12,13,20,21,22,23,24,26,27,28,30,31]}),
    ("works", 431, 436, "gpt62-i431-first-image-20261125",
     {"left-a": [3,4,5,6,7,8,10,12,13,14,15,17,18,21,23],
      "left-b": [3], "right-b": [1,3,4,5,8,9,11,12],
      "right-v": [1,2,3,4,6,8,10,13,15]}),
    ("motifs", 437, 458, "gpt62-i437-first-image-20261125",
     {"motifs": [2,3,6,8,9,10,11,13,14,16,18,20,22,24,26,28,30]}),
    ("glossary", 459, 462, "gpt62-i459-first-image-20261125",
     {"left": [2,3,6,7,9,12,14,20,22],
      "right": [2,4,6,8,10,13,15,17,19,20,22]}),
)
SOURCE_BLOBS = {416: "4dc041eecb418dc4f16654feb3f4dd98ed592452",
                431: "e664c2826055e20af0f7696e8e3c4e5f54e2a379",
                437: "df3dba2453e10ee5ee44b9bfc12edb5304cc409f",
                459: "70c19e15133c47d635d4b50c5f80a1af06af040e"}
NUMBER = r"[1-9][0-9]{0,2}"
TOKEN = NUMBER + r"(?:[—–-]" + NUMBER + r")?"
TAIL = re.compile(r"\s+(" + TOKEN + r"(?:\s*,\s*" + TOKEN + r")*)\s*,?$")


def folio_targets(observations):
    """Only unique explicit Arabic folio observations, never arithmetic."""
    candidates = defaultdict(set)
    for scan, printed in observations:
        if isinstance(printed, str) and re.fullmatch(NUMBER, printed):
            page = int(printed)
            if 1 <= page <= 340:
                candidates[page].add(scan)
    return {p: next(iter(scans)) for p, scans in candidates.items() if len(scans) == 1}


def make_ref(literal, targets, role="citation"):
    numbers = [int(n) for n in re.split(r"[—–-]", literal)]
    start, end = numbers[0], numbers[-1]
    if not 1 <= start <= end <= 340:
        return None
    pages = range(start, end + 1)
    return dict(literal=literal, volume="1", role=role,
                targets=[dict(page=p, scan=targets[p]) for p in pages if p in targets],
                missing=[p for p in pages if p not in targets])


def parse_entry(kind, lines, targets):
    """Derive display label/refs; the underlying lines never change.

    Do not treat arbitrary digits in a motif or glossary gloss as citations.
    Unsupported or suspicious numeric tails stay in the literal label.
    """
    joined = " ".join(lines)
    if kind == "glossary":
        m = re.match(r"^(.+?) (" + TOKEN + r") (.+)$", joined)
        if not m:
            return joined, "", []
        label, literal, detail = m.groups()
        ref = make_ref(literal, targets)
        if ref is None:
            return joined, "", []
        refs = [ref]
        # Explicitly labelled variant references, not every numeral in a gloss.
        for found in re.finditer(r"\bстор\.\s+(" + TOKEN + r")(?=\s|$|[.,;])", detail):
            other = make_ref(found[1], targets, "variant")
            if other:
                refs.append(other)
        return label, detail, refs
    m = TAIL.search(joined)
    if not m:
        return joined, "", []
    refs = [make_ref(token.strip(), targets) for token in m[1].split(",")]
    if not all(refs):
        return joined, "", []
    label = joined[:m.start()].rstrip()
    if kind == "motifs":
        label = re.sub(r"(?:\s+\.)+\s*$", "", label)
    if not label:
        return joined, "", []
    return label, "", refs


def read_draft(path):
    raw = path.read_bytes()
    data = json.loads(raw)
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    return data, blob


def build_printed_indexes(pilot, ref):
    files = {}
    for path in sorted(pilot.glob("vol1_scan*_single_reading.json")):
        data, blob = read_draft(path)
        if data["volume"] != "1":
            raise ValueError(f"wrong volume: {path}")
        scan = data["scan_page"]
        if path.name != f"vol1_scan{scan:05d}_single_reading.json" or scan in files:
            raise ValueError(f"duplicate or mismatched scan: {path}")
        files[scan] = (path, data, blob)
    targets = folio_targets((scan, d["printed_page_observed"])
                            for scan, (_, d, _) in files.items() if 76 <= scan <= 415)
    sections = []
    for kind, start, end, reader, partitions in SECTIONS:
        path, draft, blob = files[start]
        reading = draft["reading"]
        if reading["reader_id"] != reader or blob != SOURCE_BLOBS[start]:
            raise ValueError(f"index partition source changed: {path}")
        source = dict(volume="1", scan=start, path="pilot/" + path.name,
                      blob=blob, reader_id=reader, asset_commit=draft["asset_commit"])
        entries = []
        seen_regions = set()
        for region in reading["regions"]:
            region_id = region["id"]
            if region_id not in partitions:
                if region["kind"] == "body" and region_id != "intro":
                    raise ValueError(f"unpartitioned body region: {path}: {region_id}")
                continue
            seen_regions.add(region_id)
            lines = region["lines"]
            ends = partitions[region_id]
            if sorted(set(ends)) != ends or ends[0] < 1 or ends[-1] != len(lines):
                raise ValueError(f"index line partition no longer fits: {path}: {region_id}")
            previous = 0
            for stop in ends:
                part = [{"id": l["id"], "text": l["text"]} for l in lines[previous:stop]]
                label, detail, refs = parse_entry(kind, [l["text"] for l in part], targets)
                # Only the explicit Abraham block on the pilot motif page.
                context = "Авраам" if kind == "motifs" and label.startswith("„") else ""
                entries.append(dict(id=f"v1-{start}-{part[0]['id']}", source=source,
                                    region_id=region_id, lines=part, label=label,
                                    detail=detail, context=context, refs=refs))
                previous = stop
        if seen_regions != set(partitions):
            raise ValueError(f"missing index regions: {path}")
        sections.append(dict(volume="1", kind=kind, scans=list(range(start, end + 1)),
                             draft_scans=[n for n in range(start, end + 1) if n in files],
                             structured_scans=[start], entries=entries))
    return dict(schema_version=1, ref=ref, status="agent_unverified", sections=sections)
