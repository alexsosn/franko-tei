"""Typed source-heading continuation: no synthetic physical rows or silent first-reader edits."""
import copy
import json
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET

from franko_tei.pilot_tei import (
    TEI, validate_heading_overlay, render_pilot_tei, extract_transcribed_lines,
)

ROOT = Path(__file__).parents[1]
PAGE48 = ROOT / "pilot" / "vol1_scan00048_single_reading.json"
OVERLAY = ROOT / "pilot" / "overlays" / "vol1_scan00048_heading_continuation.json"
XML = "{http://www.w3.org/XML/1998/namespace}id"


class TestI48HeadingOverlay(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(PAGE48.read_text(encoding="utf-8"))
        self.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

    def test_original_image_bound_heading_and_body_still_one_physical_line(self):
        validate_heading_overlay(self.d, self.overlay)
        xml = render_pilot_tei(self.d, 1190, 1700, heading_overlay=self.overlay)
        root = ET.fromstring(xml)
        source = [l["text"] for r in self.d["reading"]["regions"] for l in r["lines"]]
        self.assertEqual(extract_transcribed_lines(xml), source)
        self.assertEqual(len(root.findall(f".//{{{TEI}}}lb")), 42)
        self.assertEqual(len(root.findall(f".//{{{TEI}}}pb")), 1)
        spans = [s for s in root.iter(f"{{{TEI}}}seg")
                 if s.get("type") == "printed-heading-continuation"]
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].text, "д а н ь  с т а р о з а в і т н и х.")
        self.assertEqual(spans[0].get("corresp"),
                         "#ab-v1-s00048-section_ix_heading_source_row")
        self.assertEqual(spans[0].get("cert"), "low")
        self.assertTrue(spans[0].get(XML))
        self.assertEqual(self.d["status"], "agent_unverified")

    def test_overlay_never_changes_frozen_first_reader_text(self):
        reading_before = json.dumps(self.d["reading"], sort_keys=True, ensure_ascii=False)
        validate_heading_overlay(self.d, self.overlay)
        render_pilot_tei(self.d, 1190, 1700, heading_overlay=self.overlay)
        self.assertEqual(json.dumps(self.d["reading"], sort_keys=True, ensure_ascii=False),
                         reading_before)
        self.assertEqual(self.d["reading"]["raw_response"].count("\n"), 41)

    def test_source_coordinates_and_provenance_fail_closed(self):
        variations = {
            "image mismatch": lambda o: o.update(source_image_sha256="f"*64),
            "reader mismatch": lambda o: o.update(source_reader_id="forged-reader"),
            "page mismatch": lambda o: o.update(scan_page=49),
            "fake text": lambda o: o["continuations"][0].update(
                literal="д а н ь  с т а р о з а в і т н и х?"),
            "off by one": lambda o: o["continuations"][0].update(end=33),
            "boolean end": lambda o: o["continuations"][0].update(end=True),
            "wrong body line": lambda o: o["continuations"][0].update(line_id="main-line-13"),
            "missing heading": lambda o: o["continuations"][0].update(
                heading_region_id="not-real"),
            "wrong heading source": lambda o: o["continuations"][0].update(
                heading_region_id="sumtsov_veselovsky_dragomanov"),
            "duplicate": lambda o: o["continuations"].append(copy.deepcopy(o["continuations"][0])),
            "impossible prefix": lambda o: o["continuations"][0].update(literal="Збиранє"),
            "promoted status": lambda o: o.update(status="verified"),
        }
        for name, mutate in variations.items():
            with self.subTest(name=name):
                value = copy.deepcopy(self.overlay)
                mutate(value)
                with self.assertRaises(ValueError):
                    validate_heading_overlay(self.d, value)
                with self.assertRaises(ValueError):
                    render_pilot_tei(self.d, 1190, 1700, heading_overlay=value)

    def test_default_serializer_is_unchanged_without_opt_in_overlay(self):
        xml = render_pilot_tei(self.d, 1190, 1700)
        root = ET.fromstring(xml)
        self.assertEqual(len([s for s in root.iter(f"{{{TEI}}}seg")
                              if s.get("type") == "printed-heading-continuation"]), 0)
        self.assertEqual(extract_transcribed_lines(xml),
                         [l["text"] for r in self.d["reading"]["regions"]
                          for l in r["lines"]])


if __name__ == "__main__":
    unittest.main()
