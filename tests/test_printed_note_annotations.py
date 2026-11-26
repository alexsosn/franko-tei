"""Validate source-bound printed note and rendition annotations, without export."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrintedNoteAnnotationsTests(unittest.TestCase):
    def test_joseph_rubric_batch(self):
        path = ROOT / "pilot/structure/vol1_joseph_rubrics_232_235.json"
        a = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(a["status"], "agent_unverified")
        self.assertEqual(a["volume"], "1")
        self.assertEqual([p["scan_page"] for p in a["pages"]], [232,233,234,235])
        counts, rubric_counts = [], []
        for p in a["pages"]:
            source = json.loads((ROOT / p["source_pilot_path"]).read_text(encoding="utf-8"))
            self.assertEqual(source["scan_page"], p["scan_page"])
            self.assertEqual(source["source_image_sha256"], p["source_image_sha256"])
            self.assertEqual(source["reading"]["reader_id"], p["source_reader_id"])
            regions = {r["id"]:r for r in source["reading"]["regions"]}
            lines = {l["id"]:l["text"] for r in regions.values() for l in r["lines"]}
            expected = [(l["id"],m.start(),m.group()) for r in regions.values()
                        if r["kind"] in {"body","heading"} for l in r["lines"]
                        for m in re.finditer(r"\*+\)",l["text"])]
            actual = []
            rubrics = []
            for link in p["links"]:
                anchor = link["marker"]
                target = regions[link["note_region_id"]]
                self.assertEqual(target["kind"], "note")
                self.assertTrue(target["lines"][0]["text"].startswith(anchor["literal"]))
                self.assertEqual(lines[anchor["line_id"]][anchor["start"]:anchor["end"]],anchor["literal"])
                actual.append((anchor["line_id"],anchor["start"],anchor["literal"]))
                if link["kind"] == "reported_manuscript_rubric":
                    rubrics.append(link)
                    self.assertEqual(link["note_region_id"],"rubric-note")
                    self.assertIn("киноваром",target["lines"][0]["text"])
                    self.assertEqual(link["printed_rendition"],"letter_spaced")
                    self.assertEqual(link["manuscript_rendition"],"cinnabar_reported_by_franko")
                    self.assertEqual(link["range_status"],"printed_extent_provisional")
                    self.assertIn(link["start_boundary_status"],{"visually_clear","uncertain"})
                    fragments=link["extent_fragments"]
                    self.assertIn(len(fragments),{1,2})
                    self.assertEqual(fragments[-1]["line_id"],anchor["line_id"])
                    self.assertEqual(fragments[-1]["end"],anchor["start"])
                    ordered=[l["id"] for r in regions.values() for l in r["lines"]]
                    for i, part in enumerate(fragments):
                        self.assertEqual(lines[part["line_id"]][part["start"]:part["end"]],part["literal"])
                        self.assertLess(part["start"],part["end"])
                        if i:
                            self.assertEqual(ordered.index(part["line_id"]),ordered.index(fragments[i-1]["line_id"])+1)
                            self.assertEqual(fragments[i-1]["end"],len(lines[fragments[i-1]["line_id"]]))
                            self.assertEqual(part["start"],0)
                    self.assertLessEqual(fragments[-1]["start"],link["observed_fragment"]["start"])
                    extent = link["observed_fragment"]
                    self.assertEqual(extent["line_id"],anchor["line_id"])
                    self.assertEqual(extent["end"],anchor["start"])
                    self.assertLess(extent["start"],extent["end"])
                    self.assertEqual(lines[extent["line_id"]][extent["start"]:extent["end"]],extent["literal"])
                else:
                    self.assertNotIn("manuscript_rendition",link)
            self.assertEqual(actual,expected)
            self.assertEqual(len(actual),len(set(actual)))
            for link in source["reading"].get("source_note_links",[]):
                self.assertTrue(any(x["marker"]["line_id"]==link["marker_line_id"]
                    and x["marker"]["start"]==link["marker_start"]
                    and x["marker"]["literal"]==link["marker_text"]
                    and x["note_region_id"]==link["note_region_id"] for x in p["links"]))
            counts.append(len(actual))
            rubric_counts.append(len(rubrics))
        self.assertEqual(counts,[2,6,3,4])
        self.assertEqual(rubric_counts,[1,4,3,4])
        title = a["title_continuation"]
        p = a["pages"][0]
        source=json.loads((ROOT/p["source_pilot_path"]).read_text(encoding="utf-8"))
        line=next(l for r in source["reading"]["regions"] for l in r["lines"] if l["id"]==title["line_id"])
        self.assertEqual(line["text"][:title["end"]],title["literal"])
        self.assertEqual(line["text"][title["body_start"]:].split()[0],"Іяковъ")
        self.assertEqual(title["heading_region_id"],"joseph-title")

    def test_extent_starts_and_cross_line_continuity(self):
        a=json.loads((ROOT / "pilot/structure/vol1_joseph_rubrics_232_235.json").read_text(encoding="utf-8"))
        expected={
            (232,"joseph-family-l017"):("joseph-family-l016","А до того", "visually_clear"),
            (233,"dreams-l006"):("dreams-l006","Ано вашѣ", "visually_clear"),
            (233,"dreams-l015"):("dreams-l015","оузяло сл҃нце", "uncertain"),
            (233,"dreams-l026"):("dreams-l026","миналъ лагодне", "uncertain"),
            (233,"journey-l007"):("journey-l006","братію свою", "visually_clear"),
            (234,"narrative-l007"):("narrative-l006","порвав-", "visually_clear"),
            (234,"narrative-l021"):("narrative-l020","не", "uncertain"),
            (234,"narrative-l030"):("narrative-l030","ме, і ѡн", "uncertain"),
            (235,"narrative-l004"):("narrative-l003","нѣколи не бу-", "uncertain"),
            (235,"narrative-l013"):("narrative-l012","еслибыс знав", "uncertain"),
            (235,"narrative-l023"):("narrative-l022","Оувидѣв-", "uncertain"),
            (235,"narrative-l035"):("narrative-l035","Видѣвши", "visually_clear"),
        }
        seen=set()
        for p in a["pages"]:
            for link in p["links"]:
                if link["kind"]!="reported_manuscript_rubric":
                    self.assertNotIn("extent_fragments",link)
                    continue
                key=(p["scan_page"],link["marker"]["line_id"])
                start=link["extent_fragments"][0]
                line,prefix,status=expected[key]
                self.assertEqual(start["line_id"],line)
                self.assertTrue(start["literal"].startswith(prefix))
                self.assertEqual(link["start_boundary_status"],status)
                seen.add(key)
        self.assertEqual(seen,set(expected))


class LogicalNoteEntriesTests(unittest.TestCase):
    """Source-bound logical notes, independent of physical region partitioning."""

    def load_fixture(self):
        path = ROOT / "pilot/structure/vol1_editorial_note_entries.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def load_source(self, page):
        return json.loads((ROOT / page["source_pilot_path"]).read_text(encoding="utf-8"))

    def check_page(self, page, source):
        self.assertEqual(source["volume"], "1")
        self.assertEqual(source["scan_page"], page["scan_page"])
        self.assertEqual(source["printed_page_observed"], page["printed_page"])
        self.assertEqual(source["source_image_sha256"], page["source_image_sha256"])
        self.assertEqual(source["reading"]["reader_id"], page["source_reader_id"])
        self.assertRegex(page["source_record_blob"], r"^[0-9a-f]{40}$")
        self.assertRegex(page["source_record_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(page["source_pilot_path"],
                         f"pilot/vol1_scan{page['scan_page']:05d}_single_reading.json")
        # Commit/blob are historical provenance. Check exact current text anchors
        # and source identity, not equality of the whole mutable annotation blob.
        regions = {r["id"]: r for r in source["reading"]["regions"]}
        body_lines = {l["id"]: l["text"] for r in regions.values()
                      if r["kind"] in {"body", "heading"} for l in r["lines"]}
        entries = {}
        covered = {}
        for entry in page["entries"]:
            self.assertNotIn(entry["id"], entries)
            entries[entry["id"]] = entry
            self.assertTrue(entry["id"].startswith(f"v1-s{page['scan_page']:05d}-"))
            region = regions[entry["note_region_id"]]
            self.assertEqual(region["kind"], "note")
            lines = {l["id"]: l["text"] for l in region["lines"]}
            expected_order = list(lines)
            fragments = entry["fragments"]
            self.assertTrue(fragments)
            self.assertRegex(entry["label"], r"^\*+\)$")
            first = fragments[0]
            self.assertTrue(first["literal"].startswith(entry["label"]))
            self.assertEqual(re.match(r"\*+\)", first["literal"]).group(), entry["label"])
            for i, f in enumerate(fragments):
                text = lines[f["line_id"]]
                self.assertIs(type(f["start"]), int)
                self.assertIs(type(f["end"]), int)
                self.assertTrue(0 <= f["start"] < f["end"] <= len(text))
                self.assertEqual(text[f["start"]:f["end"]], f["literal"])
                if i:
                    prev = fragments[i - 1]
                    self.assertEqual(expected_order.index(f["line_id"]),
                                     expected_order.index(prev["line_id"]) + 1)
                    self.assertEqual(prev["end"], len(lines[prev["line_id"]]))
                    self.assertEqual(f["start"], 0)
                for pos in range(f["start"], f["end"]):
                    key = (entry["note_region_id"], f["line_id"], pos)
                    self.assertNotIn(key, covered, "logical note entries overlap")
                    covered[key] = entry["id"]
        # The reviewed physical regions must be partitioned exactly; no
        # unnoticed unassigned note continuation or duplicated note text.
        reviewed = {e["note_region_id"] for e in entries.values()}
        self.assertEqual(set(covered), {
            (rid, line["id"], i) for rid in reviewed
            for line in regions[rid]["lines"] for i in range(len(line["text"]))
        })
        expected = {(lid, m.start(), m.end(), m.group())
                    for lid, text in body_lines.items()
                    for m in re.finditer(r"\*+\)", text)}
        actual, resolved = set(), set()
        for link in page["links"]:
            marker = link["marker"]
            key = (marker["line_id"], marker["start"], marker["end"], marker["literal"])
            self.assertIn(key, expected)
            self.assertNotIn(key, actual)
            actual.add(key)
            if link["status"] == "resolved":
                entry = entries[link["target_entry_id"]]
                self.assertEqual(entry["label"], marker["literal"])
                resolved.add(entry["id"])
                self.assertNotIn("reason", link)
            else:
                self.assertEqual(link["status"], "unresolved_marker_mismatch")
                self.assertIsNone(link["target_entry_id"])
                self.assertTrue(link["reason"].strip())
        self.assertEqual(actual, expected)
        self.assertEqual(set(page["unlinked_entry_ids"]), set(entries) - resolved)
        self.assertEqual(len(page["unlinked_entry_ids"]), len(set(page["unlinked_entry_ids"])))

    def test_logical_note_entries_on_real_scans(self):
        fixture = self.load_fixture()
        self.assertEqual(fixture["schema_version"], "printed-note-entry-annotation-v1")
        self.assertEqual(fixture["status"], "agent_unverified")
        self.assertEqual(fixture["volume"], "1")
        self.assertEqual([p["scan_page"] for p in fixture["pages"]],
                         [157, 188, 199, 200, 204, 211, 216])
        ids = [e["id"] for page in fixture["pages"] for e in page["entries"]]
        self.assertEqual(len(ids), len(set(ids)), "note IDs must be unique across pages")
        for page, count in zip(fixture["pages"], [2, 2, 4, 3, 2, 2, 2]):
            with self.subTest(scan=page["scan_page"]):
                source = self.load_source(page)
                self.check_page(page, source)
                self.assertEqual(len(page["entries"]), count)
                self.assertEqual(len(page["links"]), count)
                self.assertEqual(len(page["unlinked_entry_ids"]),
                                 int(page["scan_page"] == 157))
        pages = {p["scan_page"]: p for p in fixture["pages"]}
        self.assertEqual([len(e["fragments"]) for e in pages[211]["entries"]], [1, 4])
        self.assertEqual([len(e["fragments"]) for e in pages[216]["entries"]], [4, 1])
        unresolved = [link for p in pages.values() for link in p["links"]
                      if link["status"] != "resolved"]
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0]["marker"]["line_id"], "abraham-barisat-continuation-l038")

    def test_note_entry_adversarial_mutations(self):
        import copy
        page = next(p for p in self.load_fixture()["pages"] if p["scan_page"] == 211)
        source = self.load_source(page)
        self.check_page(page, source)
        # Annotation-only metadata updates do not invalidate exact text anchors.
        meta = copy.deepcopy(source)
        meta["reading"]["language_annotation"] = {"test": True}
        self.check_page(page, meta)
        mutations = [
            lambda p: p["entries"][1]["fragments"].pop(),
            lambda p: p["entries"][1]["fragments"].append(p["entries"][0]["fragments"][0]),
            lambda p: p["links"][1].update(target_entry_id=p["entries"][0]["id"]),
            lambda p: p["links"][1]["marker"].update(start=p["links"][1]["marker"]["start"] + 1),
            lambda p: p["links"].pop(),
        ]
        for change in mutations:
            bad = copy.deepcopy(page)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_page(bad, source)
        bad_source = copy.deepcopy(source)
        note = next(r for r in bad_source["reading"]["regions"]
                    if r["id"] == page["entries"][1]["note_region_id"])
        note["lines"][-1]["text"] += "!"
        with self.assertRaises(AssertionError):
            self.check_page(page, bad_source)


class NumberedApparatusTests(unittest.TestCase):
    LABEL = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+\)")
    DIGITS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

    def load_fixture(self):
        path = ROOT / "pilot/structure/vol1_noah_a_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def load_sources(self, block):
        return {p["scan_page"]: json.loads(
            (ROOT / p["source_pilot_path"]).read_text(encoding="utf-8"))
            for p in block["pages"]}

    def check_block(self, block, sources, *, paired=False, repeated=False,
                    occurrence_labels=False):
        self.assertTrue(not repeated or paired)
        self.assertTrue(not occurrence_labels or repeated)
        self.assertEqual(block["schema_version"], "printed-apparatus-annotation-v1")
        self.assertEqual(block["status"], "agent_unverified")
        self.assertEqual(block["volume"], "1")
        pages = block["pages"]
        scans = [p["scan_page"] for p in pages]
        self.assertEqual(scans, sorted(set(scans)))
        self.assertEqual(set(scans), set(sources))
        body, apparatus, regions = {}, {}, {}
        for page in pages:
            scan = page["scan_page"]
            source = sources[scan]
            self.assertEqual(source["volume"], block["volume"])
            self.assertEqual(source["scan_page"], scan)
            self.assertEqual(source["printed_page_observed"], page["printed_page"])
            self.assertEqual(source["reading"]["reader_id"], page["source_reader_id"])
            self.assertEqual(source["source_image_sha256"], page["source_image_sha256"])
            self.assertEqual(page["source_pilot_path"],
                             f"pilot/vol{block['volume']}_scan{scan:05d}_single_reading.json")
            self.assertRegex(page["source_record_commit"], r"^[0-9a-f]{40}$")
            self.assertRegex(page["source_record_blob"], r"^[0-9a-f]{40}$")
            rs = {r["id"]: r for r in source["reading"]["regions"]}
            for field, kind, output in [("body_region_ids", "body", body),
                                        ("apparatus_region_ids", "note", apparatus)]:
                ids = page[field]
                self.assertEqual(ids, [r["id"] for r in source["reading"]["regions"]
                                       if r["id"] in ids])
                for rid in ids:
                    region = rs[rid]
                    self.assertEqual(region["kind"], kind)
                    for line in region["lines"]:
                        key = (scan, line["id"])
                        self.assertNotIn(key, output)
                        output[key] = line["text"]
            regions[scan] = rs

        def check_boundary(anchor):
            region = regions[anchor["scan_page"]][anchor["region_id"]]
            self.assertEqual(region["kind"], "heading")
            self.assertEqual([l["text"] for l in region["lines"]], anchor["lines"])
        check_boundary(block["scope"]["heading"])
        check_boundary(block["scope"]["next_heading"])
        # Scope boundaries refer to separate witness blocks.
        self.assertNotEqual(block["scope"]["heading"], block["scope"]["next_heading"])

        # Flatten physical code-point coordinates, not text: no newline is
        # fabricated and line-final hyphens/spacing remain literal.
        expected = [(scan, lid, i) for (scan, lid), raw in apparatus.items()
                    for i in range(len(raw))]
        actual, entries = [], {}
        # Paired notation is a single printed apparatus label, not two entries.
        label_pattern = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+(?:—[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?\)") if paired else self.LABEL
        marker_pattern = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+[)—]?") if paired else self.LABEL
        note_labels = [(scan, lid, m.start(), m.end(), m.group())
                       for (scan, lid), raw in apparatus.items()
                       for m in label_pattern.finditer(raw)]
        seen_labels = []
        label_counts = {}
        for entry in block["entries"]:
            number = entry["number"]
            label_counts[number] = label_counts.get(number, 0) + 1
            if occurrence_labels:
                self.assertEqual(entry["id"], f"{block['id']}-entry-{number:03d}-{label_counts[number]:02d}")
            else:
                self.assertEqual(label_counts[number], 1)
            self.assertNotIn(entry["id"], entries)
            entries[entry["id"]] = entry
            self.assertTrue(entry["id"].startswith(block["id"] + "-"))
            fragments = entry["fragments"]
            self.assertTrue(fragments)
            first = fragments[0]
            m = label_pattern.match(first["literal"])
            self.assertIsNotNone(m)
            self.assertEqual(m.group(), entry["label"])
            if "body_pair_evidence" in entry:
                self.assertTrue(occurrence_labels)
                self.assertNotIn("—", entry["label"])
                self.assertTrue(entry["body_pair_evidence"].strip())
            numbers = entry["label"][:-1].translate(self.DIGITS).split("—")
            self.assertTrue(all(int(n) == entry["number"] for n in numbers))
            seen_labels.append((first["scan_page"], first["line_id"], first["start"],
                                first["start"] + len(entry["label"]), entry["label"]))
            for f in fragments:
                key = (f["scan_page"], f["line_id"])
                self.assertIn(key, apparatus)
                raw = apparatus[key]
                self.assertIs(type(f["start"]), int)
                self.assertIs(type(f["end"]), int)
                self.assertTrue(0 <= f["start"] < f["end"] <= len(raw))
                self.assertEqual(raw[f["start"]:f["end"]], f["literal"])
                actual.extend((*key, i) for i in range(f["start"], f["end"]))
        self.assertEqual(actual, expected, "apparatus partition must preserve exact ordered text")
        self.assertEqual(seen_labels, note_labels, "every printed entry start must be retained")
        expected_markers = [(scan, lid, m.start(), m.end(), m.group())
                            for (scan, lid), raw in body.items()
                            for m in marker_pattern.finditer(raw)]
        markers, targets = [], []
        roles = {}
        for link in block["links"]:
            marker = link["marker"]
            key = (marker["scan_page"], marker["line_id"], marker["start"],
                   marker["end"], marker["literal"])
            markers.append(key)
            if paired and link["status"] != "resolved":
                number = int(marker["literal"].rstrip(")—").translate(self.DIGITS))
                if link["status"] == "unresolved_missing_entry":
                    self.assertTrue(occurrence_labels)
                    self.assertNotIn(number, label_counts,
                                     "missing-entry status requires an absent article number")
                else:
                    self.assertEqual(link["status"], "unresolved_marker_mismatch")
                    self.assertIn(number, label_counts,
                                  "marker mismatch differs from a missing printed entry")
                self.assertIsNone(link["target_entry_id"])
                self.assertEqual(link["role"], "unresolved")
                self.assertTrue(link["reason"].strip())
                continue
            self.assertEqual(link["status"], "resolved")
            self.assertIn(link["target_entry_id"], entries)
            entry = entries[link["target_entry_id"]]
            if paired:
                self.assertNotIn("reason", link)
                number = int(marker["literal"].rstrip(")—").translate(self.DIGITS))
                self.assertEqual(number, entry["number"])
                if occurrence_labels and label_counts[number] > 1:
                    self.assertTrue(link.get("disambiguation", "").strip(),
                                    "duplicate printed number requires explicit source evidence")
                else:
                    self.assertNotIn("disambiguation", link)
                role = link["role"]
                if "body_pair_evidence" in entry:
                    self.assertIn(role, ("range_start", "range_end"))
                    # Explicit printed dash at the start; bare closing
                    # marker or closing parenthesis at the end.
                    if role == "range_start":
                        self.assertTrue(marker["literal"].endswith("—"))
                    else:
                        self.assertFalse(marker["literal"].endswith("—"))
                elif "—" in entry["label"]:
                    self.assertIn(role, ("range_start", "range_end"))
                    # Some printed starts have a bare number or a closing
                    # parenthesis; the role is separate from the literal.
                    if role == "range_end" or not repeated:
                        self.assertTrue(marker["literal"].endswith("—" if role == "range_start" else ")"))
                else:
                    self.assertIn(role, ("single", "repeated_reference") if repeated else ("single",))
                    self.assertFalse(marker["literal"].endswith("—"))
                roles.setdefault(entry["id"], []).append(role)
            else:
                self.assertEqual(entry["label"], marker["literal"])
            targets.append(entry["id"])
        self.assertEqual(markers, expected_markers)
        if paired:
            self.assertEqual(block["unlinked_entry_ids"],
                             [eid for eid in entries if eid not in targets])
            incomplete = []
            for eid, observed_roles in roles.items():
                if "body_pair_evidence" in entries[eid]:
                    self.assertEqual(observed_roles, ["range_start", "range_end"])
                elif "—" in entries[eid]["label"]:
                    if repeated and (observed_roles == ["range_start"] or
                                     occurrence_labels and observed_roles == ["range_end"]):
                        incomplete.append(eid)
                    else:
                        self.assertEqual(observed_roles, ["range_start", "range_end"])
                elif repeated and len(observed_roles) > 1:
                    self.assertEqual(observed_roles, ["repeated_reference"] * len(observed_roles))
                else:
                    self.assertEqual(observed_roles, ["single"])
            self.assertTrue(all(eid in roles for eid, e in entries.items()
                                if "body_pair_evidence" in e))
            if repeated:
                self.assertEqual(block["incomplete_range_entry_ids"],
                                 [eid for eid in entries if eid in incomplete])
            else:
                self.assertNotIn("incomplete_range_entry_ids", block)
        else:
            self.assertEqual(targets, list(entries), "one-to-one order is observed in this scope")

    def test_noah_a_complete_numbered_apparatus(self):
        block = self.load_fixture()
        sources = self.load_sources(block)
        self.check_block(block, sources)
        self.assertEqual(block["id"], "v1-noah-viii-a")
        self.assertEqual([p["scan_page"] for p in block["pages"]], [140, 141, 142, 143])
        self.assertEqual([p["body_region_ids"] for p in block["pages"]], [
            ["noah-generations", "noah-giants", "noah-iniquity"],
            ["noah-ark", "noah-summoning", "noah-flood-start"],
            ["noah-flood-continuation"], []])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], [
            [], [], ["noah-apparatus-start"], ["noah-apparatus-continuation"]])
        self.assertEqual(block["scope"]["heading"]["region_id"], "witness-a-heading")
        self.assertEqual(block["scope"]["next_heading"]["region_id"], "witness-b-label")
        self.assertEqual([e["number"] for e in block["entries"]], list(range(1, 64)))
        self.assertEqual([e["fragments"][0]["scan_page"] for e in block["entries"]],
                         [142] * 7 + [143] * 56)
        self.assertEqual([l["marker"]["scan_page"] for l in block["links"]],
                         [140] * 27 + [141] * 22 + [142] * 14)
        # Real multiline cases, including editorial prose inside the apparatus.
        entries = {e["number"]: e for e in block["entries"]}
        self.assertEqual(len(entries[3]["fragments"]), 2)
        self.assertEqual(len(entries[46]["fragments"]), 3)
        self.assertEqual(len(entries[49]["fragments"]), 3)
        self.assertIn("vacat", "".join(f["literal"] for f in entries[46]["fragments"]))
        self.assertIn("після", "".join(f["literal"] for f in entries[49]["fragments"]))

    def test_numbered_apparatus_adversarial_mutations(self):
        import copy
        block = self.load_fixture()
        sources = self.load_sources(block)
        self.check_block(block, sources)
        mutations = [
            lambda b: b["entries"][2]["fragments"].pop(),
            lambda b: b["entries"][3]["fragments"].append(b["entries"][2]["fragments"][0]),
            lambda b: b["entries"][0].update(label="²)"),
            lambda b: b["links"][0].update(target_entry_id=b["entries"][1]["id"]),
            lambda b: b["links"][0]["marker"].update(scan_page=143),
            lambda b: b["links"].pop(),
            lambda b: b["entries"].reverse(),
        ]
        for change in mutations:
            bad = copy.deepcopy(block)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_block(bad, sources)
        bad = copy.deepcopy(sources)
        note = next(r for r in bad[143]["reading"]["regions"]
                    if r["id"] == "noah-apparatus-continuation")
        note["lines"][-1]["text"] += "!"
        with self.assertRaises(AssertionError):
            self.check_block(block, bad)


    def test_noah_c_paired_and_unresolved_markers(self):
        block = json.loads((ROOT / "pilot/structure/vol1_noah_c_apparatus.json").read_text(
            encoding="utf-8"))
        sources = self.load_sources(block)
        self.check_block(block, sources, paired=True)
        self.assertEqual(block["id"], "v1-noah-viii-c")
        self.assertEqual([p["scan_page"] for p in block["pages"]], [147, 148, 149])
        self.assertEqual([p["body_region_ids"] for p in block["pages"]], [
            ["witness-c-covenant", "witness-c-vineyard", "witness-c-prophecy"],
            ["witness-c-prophecy-end"], []])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]],
                         [[], ["witness-c-apparatus"], []])
        self.assertEqual(block["scope"]["heading"]["region_id"], "witness-c-label")
        self.assertEqual(block["scope"]["next_heading"]["region_id"], "section-ix")
        self.assertEqual([e["number"] for e in block["entries"]], list(range(1, 25)))
        self.assertEqual(block["entries"][4]["label"], "⁵—⁵)")
        self.assertEqual(len(block["links"]), 24)
        pair = [l for l in block["links"] if l["target_entry_id"] ==
                block["entries"][4]["id"]]
        self.assertEqual([l["role"] for l in pair], ["range_start", "range_end"])
        self.assertEqual([l["marker"]["literal"] for l in pair], ["⁵—", "⁵)"])
        bare = next(l for l in block["links"] if l["marker"]["literal"] == "¹²")
        self.assertEqual(bare["target_entry_id"], block["entries"][11]["id"])
        self.assertEqual(bare["role"], "single")
        self.assertEqual(block["unlinked_entry_ids"],
                         [block["entries"][9]["id"], block["entries"][15]["id"]])
        unresolved = [l for l in block["links"] if l["status"] != "resolved"]
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0]["marker"]["literal"], "¹⁰)")
        self.assertIsNone(unresolved[0]["target_entry_id"])

    def test_paired_apparatus_adversarial_mutations(self):
        import copy
        block = json.loads((ROOT / "pilot/structure/vol1_noah_c_apparatus.json").read_text(
            encoding="utf-8"))
        sources = self.load_sources(block)
        self.check_block(block, sources, paired=True)
        def pair_end(b):
            return next(l for l in b["links"] if l["role"] == "range_end")
        def unresolved(b):
            return next(l for l in b["links"] if l["status"] != "resolved")
        mutations = [
            lambda b: pair_end(b).update(role="range_start"),
            lambda b: pair_end(b).update(target_entry_id=b["entries"][3]["id"]),
            lambda b: unresolved(b).update(target_entry_id=b["entries"][9]["id"]),
            lambda b: b["unlinked_entry_ids"].pop(),
            lambda b: b["entries"][4].update(label="⁵)"),
            lambda b: b["links"].pop(),
        ]
        for change in mutations:
            bad = copy.deepcopy(block)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_block(bad, sources, paired=True)


    def test_noah_b_repeated_and_incomplete_apparatus(self):
        block = json.loads((ROOT / "pilot/structure/vol1_noah_b_apparatus.json").read_text(
            encoding="utf-8"))
        sources = self.load_sources(block)
        self.check_block(block, sources, paired=True, repeated=True)
        self.assertEqual(block["id"], "v1-noah-viii-b")
        self.assertEqual([p["scan_page"] for p in block["pages"]], [143, 144, 145, 146, 147])
        self.assertEqual([p["body_region_ids"] for p in block["pages"]], [
            ["witness-b-flood"], ["witness-b-flood-continuation"],
            ["witness-b-flood-continuation"], ["witness-b-flood-end"], []])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]],
                         [[], [], [], ["witness-b-apparatus"], []])
        self.assertEqual(block["scope"]["heading"]["region_id"], "witness-b-label")
        self.assertEqual(block["scope"]["next_heading"]["region_id"], "witness-c-label")
        entries = {e["number"]: e for e in block["entries"]}
        self.assertEqual(list(entries), list(range(1, 83)))
        self.assertEqual(len(block["links"]), 112)
        self.assertEqual([sum(l["marker"]["scan_page"] == n for l in block["links"])
                          for n in (143, 144, 145, 146)], [0, 66, 39, 7])
        def links_to(n):
            return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
        for n, count in [(8, 31), (41, 2), (65, 2)]:
            self.assertEqual([l["role"] for l in links_to(n)], ["repeated_reference"] * count)
        self.assertIn("vac.", "".join(f["literal"] for f in entries[8]["fragments"]))
        for n in (56, 64):
            self.assertEqual([l["role"] for l in links_to(n)], ["range_start", "range_end"])
            self.assertFalse(links_to(n)[0]["marker"]["literal"].endswith(")"))
        self.assertEqual([l["role"] for l in links_to(43)], ["range_start"])
        self.assertEqual(block["incomplete_range_entry_ids"], [entries[43]["id"]])
        self.assertEqual(block["unlinked_entry_ids"],
                         [entries[n]["id"] for n in (6, 37, 44, 47, 48, 73, 80)])
        unresolved = [l for l in block["links"] if l["status"] != "resolved"]
        self.assertEqual([(l["marker"]["scan_page"], l["marker"]["literal"]) for l in unresolved],
                         [(144, "³⁷)"), (145, "⁴⁴)"), (145, "⁴⁸)")])

    def test_repeated_apparatus_adversarial_mutations(self):
        import copy
        block = json.loads((ROOT / "pilot/structure/vol1_noah_b_apparatus.json").read_text(
            encoding="utf-8"))
        sources = self.load_sources(block)
        self.check_block(block, sources, paired=True, repeated=True)
        def repeated(b):
            return next(l for l in b["links"] if l["role"] == "repeated_reference")
        def unresolved(b):
            return next(l for l in b["links"] if l["status"] != "resolved")
        def range_start(b):
            return next(l for l in b["links"] if l["role"] == "range_start")
        mutations = [
            lambda b: repeated(b).update(role="single"),
            lambda b: repeated(b).update(target_entry_id=b["entries"][8]["id"]),
            lambda b: b["incomplete_range_entry_ids"].clear(),
            lambda b: b["incomplete_range_entry_ids"].append(b["entries"][55]["id"]),
            lambda b: range_start(b).update(role="range_end"),
            lambda b: unresolved(b).update(target_entry_id=b["entries"][36]["id"]),
            lambda b: b["links"].remove(repeated(b)),
            lambda b: b["unlinked_entry_ids"].pop(),
        ]
        for change in mutations:
            bad = copy.deepcopy(block)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_block(bad, sources, paired=True, repeated=True)


    def test_section_ix_apparatus_scopes(self):
        for suffix, total, markers, resolved, unlinked, incomplete in [
                ("a", 57, 59, 58, 3, 0), ("b", 28, 29, 27, 4, 1),
                ("c", 9, 12, 12, 0, 0)]:
            with self.subTest(witness=suffix):
                block = json.loads((ROOT / f"pilot/structure/vol1_section_ix_{suffix}_apparatus.json"
                                    ).read_text(encoding="utf-8"))
                self.check_block(block, self.load_sources(block), paired=True, repeated=True,
                                 occurrence_labels=True)
                self.assertEqual(block["id"], f"v1-section-ix-{suffix}")
                self.assertEqual(len(block["entries"]), total)
                self.assertEqual(len(block["links"]), markers)
                self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), resolved)
                self.assertEqual(len(block["unlinked_entry_ids"]), unlinked)
                self.assertEqual(len(block["incomplete_range_entry_ids"]), incomplete)
                expected = {
                    "a": ([149, 150, 152], [["babel", "munt-nimrod"], ["first-wars"], []],
                          [[], ["witness-a-apparatus"], []], "witness-a-label", "witness-b-label",
                          [54], [52, 53, 54]),
                    "b": ([152, 153], [["witness-b-eber", "witness-b-babel"], ["witness-b-babel-end"]],
                          [[], ["witness-b-apparatus"]], "witness-b-label", "witness-c-label",
                          [3, 20], [3, 7, 18, 20]),
                    "c": ([153, 154], [["witness-c-serug-nahor"], []],
                          [[], ["witness-c-apparatus"]], "witness-c-label", "witness-d-label",
                          [], []),
                }[suffix]
                scans, body, apparatus, start, end, disputed, missing = expected
                self.assertEqual([p["scan_page"] for p in block["pages"]], scans)
                self.assertEqual([p["body_region_ids"] for p in block["pages"]], body)
                self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], apparatus)
                self.assertEqual(block["scope"]["heading"]["region_id"], start)
                self.assertEqual(block["scope"]["next_heading"]["region_id"], end)
                self.assertEqual([e["number"] for e in block["entries"]],
                                 list(range(1, 22)) + [18] + list(range(22, 28))
                                 if suffix == "b" else list(range(1, total + 1)))
                self.assertEqual([int(l["marker"]["literal"].rstrip(")—").translate(self.DIGITS))
                                  for l in block["links"] if l["status"] != "resolved"], disputed)
                self.assertEqual(sorted(e["number"] for e in block["entries"]
                                        if e["id"] in block["unlinked_entry_ids"]), missing)
                if suffix == "b":
                    self.check_ix_b_duplicate(block)
                    self.assertEqual(block["incomplete_range_entry_ids"],
                                     [block["entries"][0]["id"]])
                if suffix == "c":
                    self.assertEqual(block["scope"]["next_heading"]["region_id"], "witness-d-label")
                    self.assertTrue(block["scope"]["heading"]["lines"][0].startswith("В."))
                    self.assertTrue(block["scope"]["next_heading"]["lines"][0].startswith("В."))

    def check_ix_b_duplicate(self, block):
        """Independent local evidence distinguishes the two printed 18s."""
        duplicate = [e for e in block["entries"] if e["number"] == 18]
        self.assertEqual(len(duplicate), 2)
        self.assertNotEqual(duplicate[0]["id"], duplicate[1]["id"])
        self.assertIn("приближениемъ", duplicate[0]["fragments"][0]["literal"])
        self.assertIn("язык", duplicate[1]["fragments"][0]["literal"])
        self.assertIn(duplicate[1]["id"], block["unlinked_entry_ids"])
        linked = [l for l in block["links"] if l["target_entry_id"] == duplicate[0]["id"]]
        self.assertEqual(len(linked), 1)
        self.assertEqual(linked[0]["marker"]["line_id"], "witness-b-babel-l020")
        self.assertTrue(linked[0]["disambiguation"].strip())

    def test_duplicate_apparatus_adversarial_mutations(self):
        import copy
        block = json.loads((ROOT / "pilot/structure/vol1_section_ix_b_apparatus.json")
                           .read_text(encoding="utf-8"))
        sources = self.load_sources(block)
        self.check_block(block, sources, paired=True, repeated=True, occurrence_labels=True)
        duplicates = [e for e in block["entries"] if e["number"] == 18]
        def duplicate_link(b):
            return next(l for l in b["links"] if l["target_entry_id"] == duplicates[0]["id"])
        mutations = [
            lambda b: duplicate_link(b).pop("disambiguation"),
            lambda b: b["entries"][b["entries"].index(duplicates[1])].update(id=duplicates[0]["id"]),
            lambda b: next(l for l in b["links"] if l["status"] != "resolved").update(
                target_entry_id=duplicates[1]["id"]),
            lambda b: b["unlinked_entry_ids"].remove(duplicates[1]["id"]),
            lambda b: b["incomplete_range_entry_ids"].clear(),
        ]
        for change in mutations:
            bad = copy.deepcopy(block)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_block(bad, sources, paired=True, repeated=True, occurrence_labels=True)
        # Swapping equal printed labels and fixing the accounting would pass
        # a number-only check. The real source-specific guard must reject it.
        wrong = copy.deepcopy(block)
        duplicate_link(wrong)["target_entry_id"] = duplicates[1]["id"]
        wrong["unlinked_entry_ids"] = [e["id"] for e in wrong["entries"]
                                      if not any(l["target_entry_id"] == e["id"]
                                                 for l in wrong["links"])]
        self.check_block(wrong, sources, paired=True, repeated=True, occurrence_labels=True)
        with self.assertRaises(AssertionError):
            self.check_ix_b_duplicate(wrong)


    def test_section_x_a_and_g_apparatus(self):
        for suffix, total, markers, scans, body, apparatus, start, end in [
            ("a", 62, 81, [155, 156, 157, 158, 159, 160, 161],
             [["abraham-idols"], ["abraham-idols-continuation", "abraham-reflection"],
              ["abraham-barisat-continuation"],
              ["abraham-elements", "abraham-burning-idols", "abraham-call"],
              ["abraham-call-end", "abraham-dialogue", "abraham-wisdom", "abraham-death"], [], []],
             [[], [], [], [], ["witness-a-apparatus-start"], ["witness-a-apparatus-end"], []],
             "witness-a-label", "witness-b-label"),
            ("g", 9, 13, [165, 166, 167], [["witness-g-cross-tree"], [], []],
             [[], ["witness-g-apparatus"], []], "witness-g-label", "section-xi"),
        ]:
            with self.subTest(witness=suffix):
                block = json.loads((ROOT / f"pilot/structure/vol1_section_x_{suffix}_apparatus.json"
                                    ).read_text(encoding="utf-8"))
                self.check_block(block, self.load_sources(block), paired=True, repeated=True,
                                 occurrence_labels=True)
                self.assertEqual(block["id"], f"v1-section-x-{suffix}")
                self.assertEqual([p["scan_page"] for p in block["pages"]], scans)
                self.assertEqual([p["body_region_ids"] for p in block["pages"]], body)
                self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], apparatus)
                self.assertEqual(block["scope"]["heading"]["region_id"], start)
                self.assertEqual(block["scope"]["next_heading"]["region_id"], end)
                self.assertEqual(len(block["entries"]), total)
                self.assertEqual(len(block["links"]), markers)
                self.assertTrue(all(l["status"] == "resolved" for l in block["links"]))
                self.assertEqual(block["unlinked_entry_ids"], [])
                self.assertEqual(block["incomplete_range_entry_ids"], [])
                self.assertEqual([e["number"] for e in block["entries"]],
                                 list(range(1, 50)) + [49] + list(range(50, 62))
                                 if suffix == "a" else list(range(1, 10)))
                if suffix == "a":
                    self.check_x_a_special_cases(block)
                    entry31 = next(e for e in block["entries"] if e["number"] == 31)
                    self.assertEqual(sorted({f["scan_page"] for f in entry31["fragments"]}),
                                     [159, 160])
                else:
                    for n in (5, 6, 8, 9):
                        eid = next(e["id"] for e in block["entries"] if e["number"] == n)
                        self.assertEqual([l["role"] for l in block["links"]
                                          if l["target_entry_id"] == eid],
                                         ["repeated_reference"] * 2)

    def check_x_a_special_cases(self, block):
        duplicate = [e for e in block["entries"] if e["number"] == 49]
        self.assertEqual(len(duplicate), 2)
        for e, word, line in zip(duplicate, ("Зоухиемъ", "искореневалъ"),
                                 ("abraham-barisat-continuation-l027",
                                  "abraham-barisat-continuation-l030")):
            self.assertIn(word, e["fragments"][0]["literal"])
            links = [l for l in block["links"] if l["target_entry_id"] == e["id"]]
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0]["marker"]["line_id"], line)
            self.assertTrue(links[0]["disambiguation"].strip())
        entry55 = next(e for e in block["entries"] if e["number"] == 55)
        self.assertEqual(entry55["label"], "⁵⁵)")
        self.assertTrue(entry55["body_pair_evidence"].strip())
        pair = [l for l in block["links"] if l["target_entry_id"] == entry55["id"]]
        self.assertEqual([l["role"] for l in pair], ["range_start", "range_end"])
        self.assertEqual([l["marker"]["literal"] for l in pair], ["⁵⁵—", "⁵⁵"])
        self.assertEqual([l["marker"]["line_id"] for l in pair],
                         ["abraham-barisat-continuation-l037",
                          "abraham-barisat-continuation-l038"])

    def test_section_x_a_adversarial_mutations(self):
        import copy
        block = json.loads((ROOT / "pilot/structure/vol1_section_x_a_apparatus.json")
                           .read_text(encoding="utf-8"))
        sources = self.load_sources(block)
        self.check_block(block, sources, paired=True, repeated=True, occurrence_labels=True)
        self.check_x_a_special_cases(block)
        def entry55(b):
            return next(e for e in b["entries"] if e["number"] == 55)
        def end55(b):
            return next(l for l in b["links"] if l["target_entry_id"] == entry55(b)["id"]
                        and l["role"] == "range_end")
        for change in (
                lambda b: entry55(b).pop("body_pair_evidence"),
                lambda b: entry55(b).update(body_pair_evidence=""),
                lambda b: end55(b).update(role="range_start"),
                lambda b: end55(b)["marker"].update(literal="⁵⁵)"),
                lambda b: end55(b).update(target_entry_id=b["entries"][0]["id"])):
            bad = copy.deepcopy(block)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_block(bad, sources, paired=True, repeated=True, occurrence_labels=True)
        wrong = copy.deepcopy(block)
        ids = [e["id"] for e in wrong["entries"] if e["number"] == 49]
        for link in wrong["links"]:
            if link["target_entry_id"] in ids:
                link["target_entry_id"] = ids[1 - ids.index(link["target_entry_id"])]
        self.check_block(wrong, sources, paired=True, repeated=True, occurrence_labels=True)
        with self.assertRaises(AssertionError):
            self.check_x_a_special_cases(wrong)


    def test_section_x_b_missing_printed_entry(self):
        block = json.loads((ROOT / "pilot/structure/vol1_section_x_b_apparatus.json")
                           .read_text(encoding="utf-8"))
        self.check_block(block, self.load_sources(block), paired=True, repeated=True,
                         occurrence_labels=True)
        self.assertEqual(block["id"], "v1-section-x-b")
        self.assertEqual([p["scan_page"] for p in block["pages"]], [161, 162, 163, 164, 165])
        self.assertEqual([p["body_region_ids"] for p in block["pages"]], [
            ["witness-b-hospitality"], ["witness-b-hospitality-continuation", "witness-b-lot"],
            ["witness-b-lot-continuation"], [], []])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], [
            [], [], ["witness-b-apparatus-start"], ["witness-b-apparatus-end"], []])
        self.assertEqual(block["scope"]["heading"]["region_id"], "witness-b-label")
        self.assertEqual(block["scope"]["next_heading"]["region_id"], "witness-c-label")
        entries = {e["number"]: e for e in block["entries"]}
        self.assertEqual(list(entries), list(range(1, 100)))
        self.assertEqual(len(block["links"]), 130)
        self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), 126)
        self.assertEqual(block["unlinked_entry_ids"], [entries[n]["id"] for n in (12, 42)])
        self.assertEqual(block["incomplete_range_entry_ids"], [])
        self.assertEqual([l["marker"]["literal"] for l in block["links"]
                          if l["status"] == "unresolved_marker_mismatch"], ["¹²)", "⁴²)"])
        missing = [l for l in block["links"] if l["status"] == "unresolved_missing_entry"]
        self.assertEqual([l["marker"]["literal"] for l in missing], ["¹⁰⁰)", "¹⁰⁰)"])
        self.assertEqual([l["marker"]["line_id"] for l in missing],
                         ["witness-b-lot-continuation-l005", "witness-b-lot-continuation-l006"])
        self.assertTrue(all(l["target_entry_id"] is None for l in missing))
        self.assertTrue(entries[99]["fragments"][-1]["literal"].endswith("Далї vacat."))
        self.assertEqual(sorted({f["scan_page"] for f in entries[19]["fragments"]}), [163, 164])
        self.assertEqual([l["role"] for l in block["links"]
                          if l["target_entry_id"] == entries[91]["id"]],
                         ["repeated_reference", "repeated_reference"])

    def test_missing_entry_adversarial_mutations(self):
        import copy
        block = json.loads((ROOT / "pilot/structure/vol1_section_x_b_apparatus.json")
                           .read_text(encoding="utf-8"))
        sources = self.load_sources(block)
        self.check_block(block, sources, paired=True, repeated=True, occurrence_labels=True)
        def missing(b):
            return next(l for l in b["links"] if l["status"] == "unresolved_missing_entry")
        def mismatch(b):
            return next(l for l in b["links"] if l["status"] == "unresolved_marker_mismatch")
        mutations = [
            lambda b: missing(b).update(target_entry_id=b["entries"][-1]["id"]),
            lambda b: missing(b).update(status="resolved", role="single",
                                        target_entry_id=b["entries"][-1]["id"]),
            lambda b: missing(b).update(status="unresolved_marker_mismatch"),
            lambda b: mismatch(b).update(status="unresolved_missing_entry"),
            lambda b: b["links"].remove(missing(b)),
            lambda b: b["entries"][-1]["fragments"].pop(),
            lambda b: missing(b).update(reason=""),
        ]
        for change in mutations:
            bad = copy.deepcopy(block)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_block(bad, sources, paired=True, repeated=True, occurrence_labels=True)
