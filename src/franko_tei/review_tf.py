"""Write a source-gated Text-Fabric corpus of selected diplomatic text."""
import argparse
import json
from pathlib import Path
import subprocess

from .pilot_tei import extract_transcribed_lines
from .pilot_tf import build_tf_graph, verify_graph_roundtrip
from .pilot_tf_batch import merge_pilot_graphs, _save_graph
from .review_tei import ledger_at_checkout, _verified_editorial_page
from .review_bundle import PATH, match, git_source_loader
from .native_collation import load_native_collation


def save_current_tf(repo, paths, images_root, revision, output):
    """Select one candidate per scan; apply accepted readings before conversion.

    This explicit two-or-more-page pilot does not choose scholarly readings
    automatically or claim completeness. The full snapshot is checked once.
    """
    repo = Path(repo).resolve()
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    paths = list(paths)
    if len(paths) < 2:
        raise ValueError("select at least two source pages")
    seen = set()
    for path in paths:
        match(PATH, path, "candidate path")
        key = tuple(path.split("_", 2)[:2])
        if key in seen:
            raise ValueError("select exactly one candidate per physical page")
        seen.add(key)
    ledger = ledger_at_checkout(repo, revision)
    loader = git_source_loader(repo, revision)
    entries, expected = [], []
    for path in sorted(paths):
        xml = _verified_editorial_page(path, images_root, revision, ledger, loader,
                                       collation=load_native_collation(repo, revision, path))
        payload = json.loads(loader(revision, path).decode("utf-8"))
        graph = build_tf_graph(xml)
        expected.extend(extract_transcribed_lines(xml))
        entries.append((payload["volume"], payload["scan_page"], graph))
    merged = merge_pilot_graphs(entries)
    if verify_graph_roundtrip(merged) != expected:
        raise ValueError("selected TEI/TF physical-line roundtrip failed")
    merged.metadata["otext"]["editionRevision"] = revision
    return _save_graph(merged, output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--revision", required=True)
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        graph = save_current_tf(args.repo, args.candidate, args.images,
                                args.revision, args.output)
    except (ValueError, OSError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    print(f"Wrote {list(graph.node_features['otype'].values()).count('page')} "
          "selected working pages; not a verified edition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
