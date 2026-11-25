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
# Additional explicitly segmented pages in the glossary. None has an
# entry crossing the recorded scan/column boundaries in these drafts.
EXTRA_PAGES = {
    "names": (
        (417, "gpt62-i417-first-image-20261125", {
            "index-left": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49],
            "index-right": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,22,23,24,25,26,27,28,29,30,31,32,33,35,36,37,38,39,41,42,43,44,45,47,48,49]}),
        (418, "gpt62-i418-first-image-20261125", {
            "index-a": [1,2,3,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23],
            "index-b": [1,2,3,4,5,6,7],
            "index-v-left": [1,4,5,6,7,8,10,12,13,14],
            "index-v-right": [2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,24,25,26,27,28,29,30,32,33,34,35,36,37,38,39,40,41,42,43,44,45],
            "index-g": [1,2]}),
        (419, "gpt62-i419-first-image-20261125", {
            "left": [1,2,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49],
            "right-g": [1,2,3],
            "right-d": [4,5,6,7,8,9,10,13,14,18,19,21,22,23,24,25,26,27,28,29,30,32,33,34,35,36,37,38,39,40,41,42,43]}),
        (420, "gpt62-i420-first-image-20261125", {
            "left": [3,4,5,6,7,8,9,10,11,12,13,14,24,25,26,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47],
            "right": [1,2,3,5,6,7,8,9,10,11,12,13,18,19,20,21,22,23,24,26,27,28,29,30,31,32,33,39,40,41,42,43,44,45,46,47,48,49]}),
        (421, "gpt62-i421-first-image-20261125", {
            "left-e": [1,2,3,4,5,6,7,8,9,10],
            "left-zh": [4,5,6],
            "left-z": [1,2,4,5,7,9,10,11,13,14,15,16,17,18,19,20,21],
            "left-i": [1,2],
            "right": [1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,26,28,29,30,31,32,44,45,46,47,49]}),
    ),
    "glossary": (
        (460, "gpt62-i460-first-image-20261125", {
            "left": [2,3,4,6,8,10,11,13,15,18,20,22,24,25,26,28,30,32,35,37,38,40,41,43,44,45,49],
            "right": [1,2,3,4,6,8,10,13,15,17,20,22,24,26,27,28,30,31,33,35,36,37,39,40,41,42,44,45,47,48,49]}),
        (461, "gpt62-i461-first-image-20261125", {
            "left": [2,3,6,7,10,11,14,16,17,18,20,21,22,24,26,28,29,31,33,34,36,37,38,40,42,43,44,46,47,48,49],
            "right": [3,7,9,11,13,17,21,22,24,25,26,28,33,35,37,38,40,43,45,46,47,48,49]}),
        (462, "gpt62-i462-first-image-20261125", {
            "left": [1,2,4,9,10,12,14,16,17,19,21,22,24,26,28,30,31,33,35,38,41,42,43,44,46,47],
            "right": [2,3,4,7,8,10,11,13,14,15,17,19,22,24,25,26,27,29,30,31,33,34,35,37,39,40,41,42,44,46,48]}),
    ),
}
# Editorial context is separate from the printed ditto glyphs.
NAME_CONTEXTS = {
    (417, "index-left", 2): "Академія Наук",
    (417, "index-left", 3): "Академія Наук",
    (417, "index-left", 40): "Анна",
    (417, "index-left", 41): "Анна",
    (418, "index-a", 15): "камінь",
    (418, "index-v-left", 6): "Вавилонський",
    (418, "index-v-left", 7): "Вавилонський",
    (418, "index-v-right", 14): "Василий",
    (418, "index-v-right", 15): "Василий",
    (418, "index-v-right", 16): "Василий",
    (419, "left", 10): "Гаїдад",
    (419, "left", 19): "Геннадій",
    (419, "left", 22): "Георгій",
    (419, "left", 23): "Георгій",
    (419, "left", 25): "син Левіїв",
    (419, "left", 41): "Григорій",
    (419, "left", 42): "Григорій",
    (419, "left", 43): "Григорій",
    (419, "left", 44): "Григорій",
    (419, "left", 45): "Григорій",
    (419, "left", 46): "Григорій",
    (419, "left", 47): "Григорій",
    (419, "left", 48): "Григорій",
    (419, "left", 49): "Григорій",
    (420, "right", 12): "Енос",
    (420, "right", 13): "Енос",
    (420, "right", 44): "Єтривська",
    (421, "left-z", 2): "син Яковів",
    (421, "right", 3): "імя Бога",
    (421, "right", 4): "імя Бога",
    (421, "right", 5): "імя Бога",
    (421, "right", 21): "цар",
}
SOURCE_BLOBS.update({
    417: "d2e707ec31b1757619e7cc293d69de50f562d2fc",
    418: "2f9210d9d0f69d99f61c585cbb923361019861a1",
    419: "300c03db9adbeab783be0dc51f753525f03b4f9f",
    420: "06ddfea746b776b7227d95d7445ba77bfe9c551b",
    421: "a3ff6bfec252e48cb942d0577657017b9fb9dfc8",
    460: "600c616fe03fe0531c7e6d730d4192d88bc43f67",
    461: "d4d6497923b6d002dd66a69f79066cd4bed93e13",
    462: "f54a224cb68cd485fe90b5ff1ddca922d2deaf88",
})
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
        # Two explicitly named forms in one gloss, each with its own page:
        # Попава 199, попавица 241; Ꙗза 12, яза 148.
        paired = re.match(r"^([^\d]+?) (" + NUMBER + r"), ([^\d]+?) (" + NUMBER + r") (.+)$", joined)
        if paired:
            first, p1, second, p2, detail = paired.groups()
            refs = [make_ref(p1, targets), make_ref(p2, targets)]
            if all(refs):
                refs[0]["form"], refs[1]["form"] = first, second
                return f"{first} {p1}, {second} {p2}", detail, refs
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
    if kind == "names":
        # Some source rows use full stops as separators, or lack punctuation.
        # Split only explicit comma/period boundaries. A damaged token such as
        # "2 9" is not two page references or a guessed 29/209.
        m = re.fullmatch(r"(.+?)\s+([0-9][0-9\s,.—–-]*)", joined)
        if m:
            label, tail = m.groups()
            tokens = [token.strip() for token in re.split(r"[,.]", tail) if token.strip()]
            refs = []
            for token in tokens:
                ref = make_ref(token, targets) if re.fullmatch(TOKEN, token) else None
                refs.append(ref or dict(literal=token, volume="1", role="unresolved",
                                        targets=[], missing=[]))
            if any(ref["role"] != "unresolved" for ref in refs):
                return label, "", refs
            return joined, "", []
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
        draft_scans = [n for n in range(start, end + 1) if n in files]
        section = dict(volume="1", kind=kind, scans=list(range(start, end + 1)),
                       draft_scans=draft_scans, structured_scans=[], entries=[])
        sections.append(section)
        for scan, reader, partitions in ((start, reader, partitions), *EXTRA_PAGES.get(kind, ())):
            # A changed/missing reading must not publish stale partitions or block
            # unrelated reader deployments. Re-segment explicitly against new bytes.
            if scan not in files:
                continue
            path, draft, blob = files[scan]
            reading = draft["reading"]
            if reading["reader_id"] != reader or blob != SOURCE_BLOBS[scan]:
                continue
            source = dict(volume="1", scan=scan, path="pilot/" + path.name,
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
                    context = ("Авраам" if kind == "motifs" and label.startswith("„")
                               else NAME_CONTEXTS.get((scan, region_id, previous + 1), "") if kind == "names" else "")
                    entries.append(dict(id=f"v1-{scan}-{part[0]['id']}", source=source,
                                        region_id=region_id, lines=part, label=label,
                                        detail=detail, context=context, refs=refs))
                    previous = stop
            if seen_regions != set(partitions):
                raise ValueError(f"missing index regions: {path}")
            section["structured_scans"].append(scan)
            section["entries"].extend(entries)
    return dict(schema_version=1, ref=ref, status="agent_unverified", sections=sections)
