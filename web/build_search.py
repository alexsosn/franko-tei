"""Build read-only search projections, retaining distinct frozen candidates."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from franko_tei.pilot_batch import discover_readings, check_draft_offline


def build(pilot, output, ref):
    if not re.fullmatch(r"[a-f0-9]{40}", ref):
        raise ValueError("expected exact source commit SHA")
    entries = {str(v): [] for v in range(1, 6)}
    for path in discover_readings(pilot):
        draft = json.loads(path.read_text(encoding="utf-8"))
        check_draft_offline(path, draft)
        volume, scan = draft["volume"], draft["scan_page"]
        suffix = path.stem.split("_", 2)[2]
        text = "\n".join(line["text"] for region in draft["reading"]["regions"] for line in region["lines"])
        entries[volume].append(dict(scan=scan, suffix=suffix, text=text))
    output.mkdir(parents=True, exist_ok=True)
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
