"""Conservative completeness gate: an incomplete/unreviewed corpus is not a release."""
from .edition import load_pages


def release_issues(catalog, transcription_paths):
    issues = []
    for volume in catalog["volumes"]:
        vid = volume["id"]
        if volume["sha256"] is None or volume["scan_pages"] is None:
            issues.append(f"volume {vid}: source scan count/checksum not audited")
        if vid not in transcription_paths:
            issues.append(f"volume {vid}: no page transcription supplied")
            continue
        try:
            pages = load_pages(transcription_paths[vid], volume)
        except (ValueError, OSError) as exc:
            issues.append(f"volume {vid}: invalid transcription: {exc}")
            continue
        if any(page.status != "verified" for page in pages):
            issues.append(f"volume {vid}: unverified OCR/transcription pages present")
        if volume["scan_pages"] is not None:
            missing = set(range(1, volume["scan_pages"] + 1)) - {p.scan_page for p in pages}
            if missing:
                issues.append(f"volume {vid}: {len(missing)} scan pages missing from coverage")
    return issues
