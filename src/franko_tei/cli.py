"""Small dependency-light CLI; no auto promotion of OCR to verified text."""
import argparse
import json
from pathlib import Path
import sys
from .catalog import get_volume, load_catalog
from .edition import build_tei, load_pages, validate_tei
from .ingest import extract_pdf_text
from .ocr_benchmark import benchmark
from .release import release_issues
from .source_audit import download_source, inspect_pdf


def main(argv=None):
    parser = argparse.ArgumentParser(prog="franko-tei")
    parser.add_argument("--catalog", default=None, help="Optional separately audited catalogue JSON")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog")
    fetch = commands.add_parser("fetch-scan", help="Download one museum PDF to an ignored local path")
    fetch.add_argument("--volume", required=True, choices=[str(i) for i in range(1, 6)])
    fetch.add_argument("--output", required=True)
    inspect = commands.add_parser("inspect-scan", help="Audit local PDF byte checksum and page/text-layer counts")
    inspect.add_argument("--volume", required=True, choices=[str(i) for i in range(1, 6)])
    inspect.add_argument("--pdf", required=True)
    inspect.add_argument("--output", required=True)
    extract = commands.add_parser("extract-pdf", help="Stage EXISTING PDF text layer as unverified OCR")
    extract.add_argument("--volume", required=True, choices=[str(i) for i in range(1, 6)])
    extract.add_argument("--pdf", required=True)
    extract.add_argument("--output", required=True)
    extract.add_argument("--start", type=int, default=1)
    extract.add_argument("--end", type=int)
    evaluate = commands.add_parser("benchmark-ocr", help="Strict CER against independently verified page/line transcriptions")
    evaluate.add_argument("--volume", required=True, choices=[str(i) for i in range(1, 6)])
    evaluate.add_argument("--reference", required=True)
    evaluate.add_argument("--candidate", required=True)
    evaluate.add_argument("--output", required=True)
    build = commands.add_parser("build-tei", help="Export independently verified pages only (partial draft)")
    build.add_argument("--volume", required=True, choices=[str(i) for i in range(1, 6)])
    build.add_argument("--input", required=True)
    build.add_argument("--output", required=True)
    check = commands.add_parser("validate-tei", help="Basic structural checks; not full RNG validation")
    check.add_argument("--input", required=True)
    release = commands.add_parser("audit-release", help="Fail closed on missing pages and checksums")
    for i in range(1, 6):
        release.add_argument(f"--volume-{i}")
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
        if args.command == "catalog":
            print(json.dumps(catalog, ensure_ascii=False, indent=2))
        elif args.command == "fetch-scan":
            print(json.dumps(download_source(get_volume(catalog, args.volume), args.output), ensure_ascii=False))
        elif args.command == "inspect-scan":
            report = inspect_pdf(get_volume(catalog, args.volume), args.pdf)
            target = Path(args.output)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Wrote metadata audit to {target}; content has NOT been verified")
        elif args.command == "extract-pdf":
            print(json.dumps(extract_pdf_text(args.pdf, args.volume, args.output, args.start, args.end)))
        elif args.command == "benchmark-ocr":
            report = benchmark(args.reference, args.candidate, args.volume, args.catalog)
            target = Path(args.output)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Measured CER {report['cer']:.5f} on {report['reference_pages']} checked pages; wrote {target}")
        elif args.command == "build-tei":
            volume = get_volume(catalog, args.volume)
            pages = load_pages(args.input, volume)
            xml = build_tei(catalog, volume, pages)
            validate_tei(xml)
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(xml, encoding="utf-8")
            print(f"Wrote partial, independently verified TEI to {output}")
        elif args.command == "validate-tei":
            validate_tei(Path(args.input).read_text(encoding="utf-8"))
            print("Passed basic structural checks (not TEI Relax NG)")
        else:
            paths = {str(i): getattr(args, f"volume_{i}") for i in range(1, 6) if getattr(args, f"volume_{i}")}
            problems = release_issues(catalog, paths)
            if problems:
                print("Release blocked:\n" + "\n".join("- " + item for item in problems), file=sys.stderr)
                return 1
            print("Coverage/verification metadata gates passed (TEI/TF quality checks are separate)")
        return 0
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
