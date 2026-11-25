"""Report printed superscript apparatus labels overlapping cu/chu spans.

Read-only: do not infer footnote targets, alter frozen readings or treat
ordinary Arabic digits or historical Cyrillic numeral letters as labels.
"""
import argparse
import json
from pathlib import Path
import re

from .pilot_batch import discover_readings

_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_LABEL = re.compile(
    rf"[{_DIGITS}]+(?:[—–][{_DIGITS}]+)?\)|"
    rf"[{_DIGITS}]+[—–](?![{_DIGITS}])"
)


def find_label_overlaps(text, spans):
    """Yield code-point offsets of candidate labels overlapping cu/chu."""
    for match in _LABEL.finditer(text):
        start, end = match.span()
        if any(s.get("language") in {"cu", "chu"}
               and s["start"] < end and start < s["end"] for s in spans):
            yield start, end, match.group()


def audit_reading(data):
    for region in data["reading"]["regions"]:
        for line in region["lines"]:
            for start, end, literal in find_label_overlaps(
                    line["text"], line.get("language_spans", [])):
                yield {"region": region["id"], "line": line["id"],
                       "start": start, "end": end, "literal": literal}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=Path, default=Path("pilot"))
    args = parser.parse_args()
    for path in discover_readings(args.pilot):
        data = json.loads(path.read_text(encoding="utf-8"))
        for finding in audit_reading(data):
            print(json.dumps({"path": str(path), **finding}, ensure_ascii=False))


if __name__ == "__main__":
    main()
