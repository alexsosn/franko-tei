"""Exact line and language anchors for an existing corpus search entry.

Input is a validated frozen candidate and, optionally, sparse validated
editorial projection rows. Offsets are Unicode code points; line offsets
are page-relative and language spans are line-relative. No text normalization
or semantic inference from physical regions.
"""
from copy import deepcopy
import re

from .agent_evidence import validate_language_spans


def project_search_entry(draft, suffix, candidate_blob, changes=()):
    """Return one literal search record with matching annotation metadata."""
    if not re.fullmatch(r"[a-f0-9]{40}", candidate_blob):
        raise ValueError("invalid candidate blob")
    reading = draft["reading"]
    reader_id = reading["reader_id"]
    overrides = {}
    for row in changes:
        identifier = row["line_id"]
        if identifier in overrides:
            raise ValueError("duplicate editorial line")
        overrides[identifier] = row
    parts, anchors = [], []
    offset = 0
    corrected = False
    for region in reading["regions"]:
        for line in region["lines"]:
            text = line["text"]
            spans = line["language_spans"]
            language_status = "source_annotation" if spans else "unannotated"
            row = overrides.pop(line["id"], None)
            if row is not None:
                if row["original"] != text or row["region_id"] != region["id"]:
                    raise ValueError("stale editorial line anchor")
                status = row["status"]
                if status == "accepted_confirmation":
                    if row["text"] != text or row["language_spans"] != spans:
                        raise ValueError("confirmation changed source text or annotations")
                elif status in ("accepted_correction", "supplementary_correction"):
                    if row["text"] == text:
                        raise ValueError("correction did not change text")
                    text, spans = row["text"], row["language_spans"]
                    if status == "accepted_correction" and spans:
                        raise ValueError("accepted correction reused language spans")
                    language_status = ("needs_reannotation" if not spans
                                       else "supplementary_annotation")
                    corrected = True
                else:
                    raise ValueError("unsupported editorial line status")
            validate_language_spans(text, spans, reader_id)
            anchors.append(dict(region_id=region["id"], region_kind=region["kind"],
                                line_id=line["id"], start=offset, end=offset + len(text),
                                language_status=language_status,
                                language_spans=deepcopy(spans)))
            parts.append(text)
            offset += len(text) + 1
    if overrides:
        raise ValueError("editorial line missing from candidate")
    result = dict(scan=draft["scan_page"], suffix=suffix, text="\n".join(parts),
                  annotation=dict(candidate_blob=candidate_blob, reader_id=reader_id,
                                  model_id=reading["model_id"],
                                  model_version=reading["model_version"],
                                  printed_page=draft.get("printed_page_observed"),
                                  lines=anchors))
    if corrected:
        result["reviewed"] = True
    return result
