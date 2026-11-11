"""Merge source-checked, agent_unverified pilot TEI pages into one TF corpus.

No OCR, blind reader, or independent reviewer is synthesized here.
"""
import argparse
import hashlib
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .pilot_tf import Graph, verify_source_gated_pilot

TYPES = ("languageSpan", "uncertainty", "line", "region", "page")

# Git *blob* SHA-1 for the exact unmodified UTF-8 manifest.json at the pinned
# e871f32537e81f81896f6ce9a6658aba667db9c5 asset commit. Without this
# second trust anchor, a forged image plus forged local manifest could pass
# the ordinary image-against-manifest hash check.
PINNED_MANIFEST_BLOBS = {
    "1": "5609cac9aa5295e0a903bcc6856123d719338654",
    "2": "f2880210e5fe07fb5a8d6792e2b9844c4a282fa5",
    "3": "3c9b9c9abc5655b2af980eb137751e29a0b4fc53",
    "4": "93262d692fcc3bfdfc26c0c22a8cc9ef2887a7fd",
    "5": "707bf7169b8d7d8ea51ad3aedc4a3e0371817e62",
}


def _verify_pinned_manifest(volume, images_root):
    """Authenticate the *exact* locally supplied manifest against Git."""
    if not isinstance(volume, str) or volume not in PINNED_MANIFEST_BLOBS:
        raise ValueError("unknown volume for pinned manifest")
    path = Path(images_root) / f"vol{volume}" / "manifest.json"
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError("missing pinned source manifest") from exc
    blob = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()
    if blob != PINNED_MANIFEST_BLOBS[volume]:
        raise ValueError("local manifest does not match pinned asset commit")


def _inspect(volume, scan, graph):
    if not isinstance(volume, str) or volume not in {"1", "2", "3", "4", "5"} or type(scan) is not int or scan < 1:
        raise ValueError("invalid volume/scan")
    if not isinstance(graph, Graph):
        raise ValueError("expected a TF Graph")
    f = graph.node_features
    types = f.get("otype", {})
    if not types or set(types.values()) - {"char", *TYPES}:
        raise ValueError("unsupported TF node types")
    if sorted(types) != list(range(1, len(types) + 1)):
        raise ValueError("noncontiguous TF nodes")
    slots = sorted(n for n, kind in types.items() if kind == "char")
    if slots != list(range(1, len(slots) + 1)):
        raise ValueError("char slots must be contiguous and start at 1")
    pages = [n for n, kind in types.items() if kind == "page"]
    if len(pages) != 1:
        raise ValueError("one page per input graph required")
    page = pages[0]
    if f.get("status", {}).get(page) != "agent_unverified":
        raise ValueError("only agent_unverified TF can be combined")
    if f.get("scanPage", {}).get(page) != scan:
        raise ValueError("scan page differs from input graph")
    if f.get("teiId", {}).get(page) != f"page-v{volume}-s{scan:05d}":
        raise ValueError("page TEI source identity differs from volume/scan")
    source = f.get("imageUrl", {}).get(page)
    expected_path = f"/images/vol{volume}/page-{scan:05d}."
    if not isinstance(source, str) or expected_path not in source or not (
        source.endswith(".jpg") or source.endswith(".png")
    ):
        raise ValueError("source image URL differs from volume/scan")
    if graph.edge_features.get("oslots", {}).get(page) != set(slots):
        raise ValueError("page must span every transcribed character")
    for n in slots:
        glyph = f.get("glyph", {}).get(n)
        codepoint = f.get("codepoint", {}).get(n)
        if not isinstance(glyph, str) or len(glyph) != 1 or (
            type(codepoint) is not int or ord(glyph) != codepoint
        ):
            raise ValueError("glyph/codepoint mismatch")
    for n, kind in types.items():
        if kind == "char":
            continue
        slotset = graph.edge_features.get("oslots", {}).get(n)
        if not isinstance(slotset, set) or not slotset or not slotset.issubset(set(slots)):
            raise ValueError("non-slot node points outside character slots")
        if not f.get("teiId", {}).get(n):
            raise ValueError("missing non-slot TEI identity")
    return source, slots


def merge_pilot_graphs(entries):
    """Pure graph composition; production uses verify_source_gated_batch."""
    entries = list(entries)
    if len(entries) < 2:
        raise ValueError("batch needs two or more source pages")
    pages_seen, sources_seen, ids_seen = set(), set(), set()
    records = []
    metadata = None
    for volume, scan, graph in entries:
        # Validate scalar key types *before* putting them into a hash set.
        _inspect(volume, scan, graph)
        if (volume, scan) in pages_seen:
            raise ValueError("duplicate volume/scan pair")
        pages_seen.add((volume, scan))
        source, slots = _inspect(volume, scan, graph)
        if source in sources_seen:
            raise ValueError("duplicate source image URL")
        sources_seen.add(source)
        if metadata is None:
            metadata = deepcopy(graph.metadata)
        else:
            # Different pages legitimately use different OPTIONAL features.
            # Preserve every feature definition while refusing disagreements
            # about any shared feature, otext setting, or valueType.
            for name, definition in graph.metadata.items():
                if name in metadata:
                    if metadata[name] != definition:
                        raise ValueError(f"incompatible TF metadata for {name}")
                else:
                    metadata[name] = deepcopy(definition)
        for n, typ in graph.node_features["otype"].items():
            if typ != "char":
                ident = graph.node_features["teiId"][n]
                if ident in ids_seen:
                    raise ValueError("duplicate TEI xml:id")
                ids_seen.add(ident)
        records.append({"volume": volume, "scan": scan, "graph": graph,
                        "slots": slots, "map": {}})

    result = Graph(node_features={"otype": {}}, edge_features={"oslots": {}},
                   metadata=metadata)
    out = result.node_features

    def transfer(graph, old, new):
        for name, values in graph.node_features.items():
            if name != "otype" and old in values:
                out.setdefault(name, {})[new] = values[old]

    # Char slots must be contiguous at the front of the TF node space.
    index = 1
    for record in records:
        graph = record["graph"]
        for old in record["slots"]:
            record["map"][old] = index
            out["otype"][index] = "char"
            transfer(graph, old, index)
            index += 1

    # Keep type-group ordering globally and document reading order by page.
    for typ in TYPES:
        for record in records:
            graph = record["graph"]
            for old, kind in sorted(graph.node_features["otype"].items()):
                if kind != typ:
                    continue
                out["otype"][index] = typ
                transfer(graph, old, index)
                result.edge_features["oslots"][index] = {
                    record["map"][s] for s in graph.edge_features["oslots"][old]
                }
                if typ == "page":
                    out.setdefault("volume", {})[index] = record["volume"]
                    out.setdefault("pageKey", {})[index] = (
                        f"v{record['volume']}-s{record['scan']:05d}"
                    )
                index += 1
    result.metadata["otext"]["sectionFeatures"] = "pageKey,regionId,lineId"
    result.metadata["pageKey"] = {"valueType": "str"}
    result.metadata["volume"] = {"valueType": "str"}
    return result


def verify_source_gated_batch(pairs, images_root):
    """Hash each real image and rebuild immutable TEI before graph composition."""
    pairs = list(pairs)
    if len(pairs) < 2:
        raise ValueError("batch needs two or more evidence/TEI pairs")
    entries = []
    for evidence_path, tei_path in pairs:
        payload = json.loads(Path(evidence_path).read_text(encoding="utf8"))
        if not isinstance(payload, dict):
            raise ValueError("pilot evidence must be a JSON object")
        _verify_pinned_manifest(payload.get("volume"), images_root)
        graph = verify_source_gated_pilot(tei_path, evidence_path, images_root)
        entries.append((payload["volume"], payload["scan_page"], graph))
    return merge_pilot_graphs(entries)


def save_pilot_tf_batch(pairs, images_root, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    graph = verify_source_gated_batch(pairs, images_root)
    from tf.fabric import Fabric

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".pilot-tf-batch-", dir=output.parent) as temp:
        stage = Path(temp) / "tf"
        stage.mkdir()
        fabric = Fabric(locations=str(stage), silent="deep")
        if fabric.save(nodeFeatures=graph.node_features,
                       edgeFeatures=graph.edge_features,
                       metaData=graph.metadata, silent="deep") is not True:
            raise RuntimeError("Text-Fabric failed to save the corpus")
        stage.rename(output)
    return graph


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--evidence", action="append", required=True, type=Path)
    parser.add_argument("--tei", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if len(args.evidence) != len(args.tei) or len(args.evidence) < 2:
        parser.error("provide two or more matching --evidence/--tei pairs")
    try:
        graph = save_pilot_tf_batch(
            list(zip(args.evidence, args.tei)), args.images, args.output)
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        parser.error(str(exc))
    types = list(graph.node_features["otype"].values())
    print(f"Wrote {types.count('page')} unverified pages, "
          f"{types.count('char')} Unicode slots to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
