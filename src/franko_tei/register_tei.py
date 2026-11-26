"""Opt-in semantic TEI projection for the annotated volume III registers.

Input is the frozen source JSON bytes and the existing structural annotation.
No transcription or geometry is regenerated. The caller must independently
validate the native image (validate_single_draft) for a source-gated export.
"""
from hashlib import sha1
import json
import re
from xml.etree import ElementTree as ET

from .pilot_tei import XML, tag, xml_id, render_pilot_tei, validate_single_draft

ID = "{"+XML+"}id"
KINDS = {
    "numbered_entry": "Printed numbered entry",
    "printed_blank": "Printed empty cell; not a lacuna",
    "literal": "Literal printed reading",
    "dash": "Literal printed dash",
    "question_mark": "Literal printed question mark",
    "ditto_name": "Literal name ditto; unresolved",
    "ditto_place": "Literal place ditto; unresolved",
}
SYMBOLS = {"—": "dash", "?": "question_mark", "id.": "ditto_name",
           "idem": "ditto_name", "ibid.": "ditto_place", "ibidem": "ditto_place"}
APOSTLE = ("mark", "matthew", "luke", "john", "acts")
DISCIPLE = ("pseudo-dorotheus", "pseudo-hippolytus-b", "pseudo-hippolytus-z")
ROLES = ("name", "preaching_place")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def _source_page(raw, annotation):
    payload = json.loads(raw)
    scan = payload["scan_page"]
    require(payload["volume"] == annotation["volume"] == "3" and
            payload["status"] == annotation["status"] == "agent_unverified" and
            annotation["kind"] == "comparative_register", "invalid source/annotation status")
    apostle = scan == 34
    require(annotation["id"] == ("vol3-preface-canonical-apostle-register" if apostle
                                 else "vol3-preface-seventy-disciples-comparison"),
            "unexpected logical register ID")
    if apostle:
        require(annotation["schema_version"] == "printed-apostle-register-annotation-v1",
                "wrong apostle annotation schema")
        page = annotation
    else:
        require(scan in (72, 73, 74) and
                annotation["schema_version"] == "printed-comparative-register-annotation-v1",
                "wrong disciple annotation schema")
        require([p["scan_page"] for p in annotation["pages"]] == [72, 73, 74],
                "unexpected table page sequence")
        page = next(p for p in annotation["pages"] if p["scan_page"] == scan)
    require(page["scan_page"] == scan and
            page["printed_page"] == payload["printed_page_observed"] and
            page["source_reader_id"] == payload["reading"]["reader_id"] and
            page["source_image_sha256"] == payload["source_image_sha256"],
            "annotation source metadata mismatch")
    blob = sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
    require(blob == page["source_record_blob"], "annotation source blob mismatch")
    return payload, page, apostle


def _grid(payload, page, annotation, apostle):
    """Validate all cell ownership and order before reparenting any XML."""
    regions = {r["id"]: r["lines"] for r in payload["reading"]["regions"]}
    if apostle:
        require(tuple(c["id"] for c in page["columns"]) == APOSTLE, "wrong apostle columns")
        columns = ["table-"+x for x in APOSTLE]
        groups = list(APOSTLE)
        roles = ["name"]*5
        headings = [[(c["heading_line_ids"], 1, i) for i,c in enumerate(page["columns"])]]
        for c, ids in zip(columns, headings[0]):
            require(ids[0] == [l["id"] for l in regions[c][:2]], "invalid heading")
        start = 2
    else:
        require(tuple(g["id"] for g in annotation["column_groups"]) == DISCIPLE and
                [(c["index"], c["role"]) for g in annotation["column_groups"]
                 for c in g["columns"]] == list(zip(range(1,7), ROLES*3)),
                "wrong paired columns")
        columns = [f"table-col-{i}" for i in range(1,7)]
        groups = [g for g in DISCIPLE for _ in ROLES]
        roles = list(ROLES)*3
        group_regions = [f"table-group-{i}" for i in range(1,4)]
        require(page["group_heading_line_ids"] ==
                [regions[c][0]["id"] for c in group_regions] and
                all(len(regions[c]) == 1 for c in group_regions), "invalid group heading")
        require(page["column_heading_line_ids"] == [regions[c][0]["id"] for c in columns],
                "invalid column heading")
        headings = [[([line],2,i*2) for i,line in enumerate(page["group_heading_line_ids"])],
                    [([line],1,i) for i,line in enumerate(page["column_heading_line_ids"])]]
        start = 1
    used = [[] for _ in columns]
    by_id = {l["id"]: l for c in columns for l in regions[c]}
    row_ids = []
    data = []
    prev_y = None
    scan = payload["scan_page"]
    expected_numbers = {72: (1,20), 73: (21,61), 74: (62,70)}
    last_number = 0 if apostle else expected_numbers[scan][0]-1
    for i, row in enumerate(page["rows"],1):
        require(len(row["cells"]) == len(columns), "wrong row width")
        if apostle:
            rid = str(i)
            require(row["visual_row"] == i, "visual row out of order")
            row_number = None
            after_number = None
        else:
            row_number = row["printed_number"]
            after_number = row.get("after_number")
            if row_number is None:
                require(after_number == last_number and after_number in (2,40,46),
                        "invalid inserted row")
                rid = f"after-{after_number}"
            else:
                require(type(row_number) is int and row_number == last_number+1 and
                        after_number is None, "invalid printed row number")
                last_number = row_number
                rid = f"n{row_number}"
            require(row["id"] == rid, "invalid row ID")
        require(rid not in row_ids, "duplicate row")
        row_ids.append(rid)
        starts = set()
        cells = []
        for j,c in enumerate(row["cells"]):
            ids = c["line_ids"] if apostle else [c["line_id"]]
            kind = c["kind"]
            require(kind in KINDS, "unknown cell kind")
            number = None
            if apostle:
                require(c["column_id"] == APOSTLE[j], "column identity mismatch")
                if not ids:
                    require(kind == "printed_blank" and j == 3 and i in (7,12)
                            and "number" not in c and "number_label" not in c,
                            "invalid blank cell")
                else:
                    require(kind == "numbered_entry" and not (j == 3 and i in (7,12)),
                            "invalid numbered entry")
                    number = c["number"]
                    require(type(number) is int and number == i-(1 if j == 3 and i>7 else 0),
                            "invalid entry number")
            else:
                require(kind not in ("printed_blank", "numbered_entry"), "invalid disciple cell kind")
            if ids:
                require(all(x in by_id for x in ids), "unknown physical line")
                lines = [by_id[x] for x in ids]
                first = lines[0]["text"]
                starts.add(lines[0]["bbox_xywh"][1])
                if apostle or (j == 0 and row_number is not None):
                    n = number if apostle else row_number
                    label = c["number_label"] if apostle else row["number_label"]
                    literal = str(n)+"."
                    expected = {"start": 0, "end": len(literal), "literal": literal}
                    if apostle:
                        expected["line_id"] = ids[0]
                    require(label == expected and first.startswith(literal+" "),
                            "printed label mismatch")
                    first = first[len(literal)+1:]
                if apostle:
                    require(all(not re.match(r"^\d+\. ", l["text"]) for l in lines[1:]),
                            "cell crosses numbered entries")
                else:
                    require(kind == SYMBOLS.get(first,"literal"), "literal classification mismatch")
                    if j == 0 and row_number is None:
                        require(first == "—", "inserted row must retain printed dash")
            used[j].extend(ids)
            cells.append((ids,kind,number,groups[j],roles[j]))
        require(len(starts)==1, "unaligned row geometry")
        y = next(iter(starts))
        require(prev_y is None or y>prev_y, "row geometry out of order")
        prev_y = y
        data.append((rid,row_number,after_number,cells))
    for j,c in enumerate(columns):
        require(used[j] == [l["id"] for l in regions[c][start:]],
                "missing, duplicated, reordered or cross-column lines")
    require(len(data) == ({34:12,72:21,73:43,74:9}[scan]), "wrong data row count")
    if not apostle:
        require(last_number == expected_numbers[scan][1], "incomplete printed sequence")
    return columns, groups, roles, headings, data


def _element(parent, name, ident, attrs):
    e = ET.SubElement(parent,tag(name),attrs)
    xml_id(e,ident)
    return e


def render_register_tei(raw, annotation, width, height):
    """Render a page fragment; does not claim that JPEG bytes were validated."""
    payload, page, apostle = _source_page(raw, annotation)
    columns, groups, roles, headings, data = _grid(payload,page,annotation,apostle)
    scan = payload["scan_page"]
    prefix = f"v3-s{scan:05d}"
    root = ET.fromstring(render_pilot_tei(payload,width,height))
    div = root.find(".//"+tag("body")+"/"+tag("div"))
    bibl = root.find(".//"+tag("sourceDesc")+"/"+tag("bibl"))
    for name,value in (("Frozen-source-git-blob",page["source_record_blob"]),
                       ("Frozen-source-commit",page["source_record_commit"]),
                       ("Frozen-source-reader",page["source_reader_id"])):
        ET.SubElement(bibl,tag("idno"),{"type":name}).text = value
    enc = root.find(".//"+tag("encodingDesc"))
    declaration = ET.SubElement(enc,tag("classDecl"))
    taxonomy = _element(declaration,"taxonomy",prefix+"-register-vocabulary",{})
    vocab = {"reg-kind-"+k:v for k,v in KINDS.items()}
    vocab.update({"reg-group-"+g:g for g in set(groups)})
    vocab.update({"reg-role-"+role:role for role in set(roles)})
    vocab["reg-logical-"+annotation["id"]] = annotation["description"]
    vocab["reg-inserted-row"] = "Printed unnumbered row after the preceding number"
    for key in sorted(vocab):
        cat = _element(taxonomy,"category",key,{})
        ET.SubElement(cat,tag("catDesc")).text = vocab[key]
    reg_ids = set(columns)
    if not apostle:
        reg_ids.update(f"table-group-{i}" for i in range(1,4))
    region_xml = [e for e in div if e.get(ID) in
                  {f"ab-{prefix}-{r}" for r in reg_ids}]
    require(len(region_xml)==len(reg_ids), "missing source table region")
    indices = [list(div).index(e) for e in region_xml]
    require(indices == list(range(indices[0], indices[0]+len(indices))),
            "non-contiguous table regions")
    parts = {}
    for region in region_xml:
        current = None
        require(not region.text, "unanchored table text")
        for child in region:
            if child.tag == tag("lb"):
                current = child.get(ID).removeprefix(f"lb-{prefix}-")
                require(current not in parts, "duplicate source line")
                parts[current] = []
            require(current is not None, "unanchored table inline")
            parts[current].append(child)
        div.remove(region)
    table_id = prefix+"-register"
    table = ET.Element(tag("table"),{"rows":str(len(headings)+len(data)),
                                     "cols":str(len(columns)),
                                     "ana":"#reg-logical-"+annotation["id"]})
    xml_id(table,table_id)
    # Relative fragment links use the documented standalone output filenames.
    for attr,other in (("prev",scan-1),("next",scan+1)):
        if not apostle and other in (72,73,74):
            table.set(attr,f"vol3-s{other:05d}.xml#v3-s{other:05d}-register")
    div.insert(indices[0],table)
    def append_lines(cell,ids):
        for line in ids:
            require(line in parts,"missing or duplicate projected line")
            cell.extend(parts.pop(line))
    for i,header in enumerate(headings,1):
        row = _element(table,"row",table_id+f"-h{i}",{"role":"label"})
        for ids,span,j in header:
            ana = "#reg-group-"+groups[j]
            if span==1:
                ana += " #reg-role-"+roles[j]
            cell = _element(row,"cell",row.get(ID)+f"-c{j+1}",
                            {"role":"label","cols":str(span),"ana":ana})
            append_lines(cell,ids)
    for rid,number,after,cells in data:
        attrs = {"role":"data"}
        if number is not None:
            attrs["n"] = str(number)
        if after is not None:
            attrs["ana"] = "#reg-inserted-row"
        row = _element(table,"row",table_id+"-r"+rid,attrs)
        for j,(ids,kind,n,group,role) in enumerate(cells,1):
            attrs = {"role":"data","ana":f"#reg-kind-{kind} #reg-group-{group} #reg-role-{role}"}
            if n is not None:
                attrs["n"] = str(n)
            cell = _element(row,"cell",row.get(ID)+f"-c{j}",attrs)
            append_lines(cell,ids)
    require(not parts,"unassigned physical lines")
    return '<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(root,encoding="unicode")+"\n"


def render_source_gated_register_tei(raw, annotation, images_root):
    """Check original JPEG/manifest and render with verified image dimensions."""
    payload = json.loads(raw)
    measured = validate_single_draft(payload,images_root)
    return render_register_tei(raw,annotation,measured["width"],measured["height"])


def extract_register_source_lines(xml):
    """Reconstruct original column-major physical order using unchanged zones."""
    root = ET.fromstring(xml)
    lines = {}
    for container in root.iter():
        if not (container.tag in (tag("ab"),tag("cell")) or
                (container.tag == tag("note") and container.get("type") == "source-footnote")):
            continue
        key = None
        for child in container:
            if child.tag == tag("lb"):
                key = child.get("facs")
                require(key and key.startswith("#") and key not in lines,"invalid line anchor")
                lines[key] = child.tail or ""
            elif child.tag == tag("seg"):
                require(key is not None,"segment without line")
                lines[key] += "".join(child.itertext())+(child.tail or "")
            elif child.tag == tag("gap"):
                require(key is not None and child.get("reason")=="illegible" and
                        child.get("extent")=="unknown" and child.get("unit")=="character",
                        "invalid gap")
                lines[key] += "…"+(child.tail or "")
            else:
                raise ValueError("unexpected physical inline")
    zones = root.findall(".//"+tag("surface")+"/"+tag("zone")+"/"+tag("zone"))
    order = ["#"+z.get(ID) for z in zones]
    require(len(order)==len(set(order)) and set(order)==set(lines),"source zone coverage mismatch")
    return [lines[k] for k in order]
