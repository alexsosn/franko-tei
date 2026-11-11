"""Fail-closed export of reviewed diplomatic lines to structurally minimal TEI P5.

The export is intentionally page based. A later edition layer must segment works,
notes, manuscript witnesses, and apparatus before publication.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import xml.etree.ElementTree as ET

TEI = "http://www.tei-c.org/ns/1.0"
XML = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("", TEI)


def tag(name):
    return f"{{{TEI}}}{name}"


@dataclass(frozen=True)
class Page:
    volume: str
    scan_page: int
    status: str
    lines: tuple[str, ...]
    transcribed_by: str
    reviewed_by: str | None
    printed_page: str | None = None
    kind: str = "unclassified"
    source_sha256: str | None = None

    @classmethod
    def from_dict(cls, raw):
        allowed = {field.name for field in cls.__dataclass_fields__.values()}
        if set(raw) - allowed:
            raise ValueError(f"Unexpected page properties: {sorted(set(raw) - allowed)}")
        if not isinstance(raw.get("lines"), list) or any(not isinstance(x, str) for x in raw["lines"]):
            raise ValueError("lines must be a list of strings")
        return cls(**{**raw, "lines": tuple(raw["lines"])})

    def validate(self, volume):
        if self.volume != volume["id"]:
            raise ValueError("Page volume does not match requested volume")
        if type(self.scan_page) is not int or self.scan_page < 1:
            raise ValueError("scan_page is a 1-based integer")
        if self.status not in {"ocr_unchecked", "transcribed", "verified"}:
            raise ValueError(f"Unknown status: {self.status}")
        if not self.transcribed_by.strip():
            raise ValueError("transcribed_by is mandatory")
        if self.status == "verified" and (not self.reviewed_by or self.transcribed_by == self.reviewed_by):
            raise ValueError("Verified pages require an independent named reviewer")
        if self.status == "verified" and not any(line.strip() for line in self.lines):
            raise ValueError("Verified pages need nonempty line content; blank pages require an explicit later policy")
        if any("\n" in line or "\r" in line for line in self.lines):
            raise ValueError("Every line must be a single line")
        if self.kind not in {"unclassified", "title_page", "front_matter", "source_text", "editorial_notes", "index", "other"}:
            raise ValueError("Unknown kind")
        if self.printed_page is not None and not isinstance(self.printed_page, str):
            raise ValueError("printed_page must be a string or null")
        if volume.get("sha256") and self.status == "verified" and self.source_sha256 != volume["sha256"]:
            raise ValueError("Verified page source checksum does not match catalogue")


def load_pages(path, volume):
    pages = []
    for line_number, text in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not text.strip():
            continue
        try:
            page = Page.from_dict(json.loads(text))
            page.validate(volume)
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
        pages.append(page)
    indices = [p.scan_page for p in pages]
    if len(indices) != len(set(indices)):
        raise ValueError("Duplicate scan page number")
    if indices != sorted(indices):
        raise ValueError("Pages must be in ascending scan order")
    if volume.get("scan_pages") and any(n > volume["scan_pages"] for n in indices):
        raise ValueError("Page exceeds audited scan length")
    return pages


def build_tei(catalog, volume, pages):
    if not pages or any(p.status != "verified" for p in pages):
        raise ValueError("TEI export only accepts independently verified pages")
    for page in pages:
        page.validate(volume)
    root = ET.Element(tag("TEI"), {f"{{{XML}}}id": f"franko-vol-{volume['id']}"})
    header = ET.SubElement(root, tag("teiHeader"))
    desc = ET.SubElement(header, tag("fileDesc"))
    title_stmt = ET.SubElement(desc, tag("titleStmt"))
    ET.SubElement(title_stmt, tag("title")).text = f"{catalog['project']}. Том {volume['roman']}: {volume['title']}"
    ET.SubElement(title_stmt, tag("editor")).text = catalog["editor"]
    resp = ET.SubElement(title_stmt, tag("respStmt"))
    ET.SubElement(resp, tag("resp")).text = "Diplomatic transcription and independent review: page-level agents named in audit source"
    ET.SubElement(resp, tag("name")).text = "franko-tei contributors"
    publ = ET.SubElement(desc, tag("publicationStmt"))
    ET.SubElement(publ, tag("p")).text = "Unreleased partial digital transcription; not a critical edition or a manuscript facsimile."
    src = ET.SubElement(desc, tag("sourceDesc"))
    bibl = ET.SubElement(src, tag("bibl"))
    ET.SubElement(bibl, tag("title")).text = catalog["project"] + ". " + volume["title"]
    ET.SubElement(bibl, tag("editor")).text = catalog["editor"]
    ET.SubElement(bibl, tag("pubPlace")).text = catalog["place"]
    ET.SubElement(bibl, tag("publisher")).text = catalog["publisher"]
    ET.SubElement(bibl, tag("date"), {"when": str(volume["year"])}).text = str(volume["year"])
    ET.SubElement(bibl, tag("ref"), {"target": volume["landing_url"]}).text = "Scanned printed edition at Дім Франка"
    encoding = ET.SubElement(header, tag("encodingDesc"))
    eddecl = ET.SubElement(encoding, tag("editorialDecl"))
    ET.SubElement(eddecl, tag("p")).text = "Text is transcribed from Franko's printed edition, not directly from his cited manuscripts. Orthography retained; printed page labels and scan-page numbers are separate. Work and apparatus segmentation pending."
    profile = ET.SubElement(header, tag("profileDesc"))
    ET.SubElement(profile, tag("textClass"))
    text = ET.SubElement(root, tag("text"), {"type": "partial-diplomatic-transcription"})
    body = ET.SubElement(text, tag("body"))
    div = ET.SubElement(body, tag("div"), {"type": "unsegmented-pages", f"{{{XML}}}id": f"vol-{volume['id']}-pages"})
    for page in pages:
        # @n uses printed foliation when available; @xml:id records physical PDF page index.
        pb_attrs = {f"{{{XML}}}id": f"v{volume['id']}-scan-{page.scan_page:05d}", "facs": f"{volume['pdf_url']}#page={page.scan_page}"}
        if page.printed_page is not None:
            pb_attrs["n"] = page.printed_page
        ET.SubElement(div, tag("pb"), pb_attrs)
        ab = ET.SubElement(div, tag("ab"), {"type": page.kind})
        for i, line in enumerate(page.lines, 1):
            lb = ET.SubElement(ab, tag("lb"), {"n": str(i)})
            lb.tail = line
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def validate_tei(xml):
    root = ET.fromstring(xml)
    if root.tag != tag("TEI"):
        raise ValueError("Not TEI P5 namespace")
    for path in ("teiHeader/fileDesc/sourceDesc/bibl/ref", "text/body/div/pb"):
        if root.find("/".join(tag(t) for t in path.split("/"))) is None:
            raise ValueError(f"Missing required element: {path}")
    if any(pb.attrib.get("facs", "").startswith("#") for pb in root.findall(".//" + tag("pb"))):
        raise ValueError("Unresolvable facsimile reference")
    return True
