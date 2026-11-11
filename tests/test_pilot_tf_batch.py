"""RED-first tests for multi-page, still-unverified TF pilot composition.

All input text comes from the IV/100 single-reader fixture; the second page is
deliberately SYNTHETIC and is not evidence of a transcription of volume V.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from franko_tei.pilot_tei import render_pilot_tei
from franko_tei.pilot_tf import build_tf_graph, verify_graph_roundtrip
from franko_tei.pilot_tf_batch import (
    merge_pilot_graphs, verify_source_gated_batch, save_pilot_tf_batch,
)

BASE = Path(__file__).resolve().parents[1]
DRAFT = json.loads((BASE / "pilot/vol4_scan00100_single_reading.json").read_text("utf8"))


def synthetic_second_page():
    p = copy.deepcopy(DRAFT)
    p["volume"] = "5"
    p["scan_page"] = 10
    p["source_image_path"] = "vol5/page-00010.jpg"
    p["source_image_sha256"] = "a" * 64
    p["source_pdf_sha256_claimed_by_manifest"] = "b" * 64
    # Reuse the pilot text only for a synthetic structural fixture.
    # Never describe this as a reading of V/10.
    line = p["reading"]["regions"][0]["lines"][0]
    line["text"] = "ѣ́  & <ἔ> ꙗ"
    line["language_spans"] = []
    p["printed_page_observed"] = "ѣ́  & <ἔ> ꙗ"
    p["reading"]["raw_response"] = "\n".join(
        line["text"]
        for region in p["reading"]["regions"]
        for line in region["lines"]
    )
    return p


def fake_manifest(p, image_bytes):
    sha = hashlib.sha256(image_bytes).hexdigest()
    p["source_image_sha256"] = sha
    volume = p["volume"]
    page = p["scan_page"]
    pages = [
        {"scan_page": i, "printed_page": None, "width": 1190,
         "height": 1794, "artifacts": []}
        for i in range(1, page)
    ]
    pages.append({
        "scan_page": page, "printed_page": None, "width": 1190,
        "height": 1794,
        "artifacts": [{"role": "page_image",
                       "path": p["source_image_path"],
                       "sha256": sha}],
    })
    return {"volume": volume, "page_count": page,
            "source_sha256": p["source_pdf_sha256_claimed_by_manifest"],
            "pages": pages}


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.first = copy.deepcopy(DRAFT)
        self.second = synthetic_second_page()
        self.first_graph = build_tf_graph(render_pilot_tei(self.first, 1190, 1794))
        self.second_graph = build_tf_graph(render_pilot_tei(self.second, 1190, 1794))

    def test_two_pages_have_distinct_keys_and_exact_codepoint_lines(self):
        merged = merge_pilot_graphs([
            ("4", 100, self.first_graph),
            ("5", 10, self.second_graph),
        ])
        f = merged.node_features
        types = f["otype"]
        pages = [n for n, typ in types.items() if typ == "page"]
        self.assertEqual(len(pages), 2)
        self.assertEqual([f["pageKey"][n] for n in pages], [
            "v4-s00100", "v5-s00010"])
        self.assertEqual([f["volume"][n] for n in pages], ["4", "5"])
        self.assertEqual([f["status"][n] for n in pages], [
            "agent_unverified", "agent_unverified"])
        self.assertEqual(
            merged.metadata["otext"]["sectionFeatures"],
            "pageKey,regionId,lineId",
        )
        lines = [n for n, typ in types.items() if typ == "line"]
        for page_n, original in zip(pages, (self.first, self.second)):
            slots = merged.edge_features["oslots"][page_n]
            lines_in_page = [
                n for n in lines
                if merged.edge_features["oslots"][n].issubset(slots)
            ]
            reconstructed = [
                "".join(f["glyph"][s]
                        for s in sorted(merged.edge_features["oslots"][line_n]))
                for line_n in lines_in_page
            ]
            self.assertEqual("\n".join(reconstructed), original["reading"]["raw_response"])
        self.assertTrue(all(f["glyph"][s] == chr(f["codepoint"][s])
                            for s, typ in types.items() if typ == "char"))
        self.assertEqual(list(types), list(range(1, len(types) + 1)))
        self.assertEqual(verify_graph_roundtrip(merged), [
            *verify_graph_roundtrip(self.first_graph),
            *verify_graph_roundtrip(self.second_graph),
        ])

    def test_duplicate_page_and_duplicate_source_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate|same"):
            merge_pilot_graphs([
                ("4", 100, self.first_graph), ("4", 100, self.first_graph)])
        # A source URL copied from the first page into the second is forged.
        forged = copy.deepcopy(self.second_graph)
        p = next(n for n, k in forged.node_features["otype"].items()
                 if k == "page")
        first_p = next(n for n, k in self.first_graph.node_features["otype"].items()
                       if k == "page")
        forged.node_features["imageUrl"][p] = (
            self.first_graph.node_features["imageUrl"][first_p])
        with self.assertRaisesRegex(ValueError, "source|image|duplicate"):
            merge_pilot_graphs([
                ("4", 100, self.first_graph), ("5", 10, forged)])

    def test_malformed_payloads_fail_with_value_error_not_type_errors(self):
        # Adversarial: user-controlled JSON root and volume may be lists.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            evidence = root / "malformed.json"
            tei = root / "unused.xml"
            for value in ([], {"volume": []}, {"volume": {}}):
                evidence.write_text(json.dumps(value), encoding="utf8")
                with self.subTest(value=value), self.assertRaises(ValueError):
                    verify_source_gated_batch(
                        [(evidence, tei), (evidence, tei)], root / "images")
        with self.assertRaises(ValueError):
            merge_pilot_graphs([
                ([], 100, self.first_graph),
                ("5", 10, self.second_graph)])

    def test_rejects_promoted_graph_and_wrong_scan_dimension(self):
        promoted = copy.deepcopy(self.second_graph)
        n = next(n for n, t in promoted.node_features["otype"].items()
                 if t == "page")
        promoted.node_features["status"][n] = "verified"
        with self.assertRaisesRegex(ValueError, "unverified"):
            merge_pilot_graphs([("4", 100, self.first_graph), ("5", 10, promoted)])
        with self.assertRaisesRegex(ValueError, "scan"):
            merge_pilot_graphs([
                ("4", 100, self.first_graph), ("5", 11, self.second_graph)])

    def _write_source_pair(self, root, p, suffix):
        p = copy.deepcopy(p)
        image_bytes = ("SYNTHETIC-" + suffix).encode("ascii")
        img = root / "images" / p["source_image_path"]
        img.parent.mkdir(parents=True, exist_ok=True)
        img.write_bytes(image_bytes)
        manifest = fake_manifest(p, image_bytes)
        (img.parent / "manifest.json").write_text(json.dumps(manifest))
        evidence = root / (suffix + ".json")
        tei = root / (suffix + ".xml")
        evidence.write_text(json.dumps(p), encoding="utf8")
        tei.write_text(render_pilot_tei(p, 1190, 1794), encoding="utf8")
        return evidence, tei, img

    def test_batch_checks_actual_image_and_regenerated_tei_before_merge(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ev1, tei1, img1 = self._write_source_pair(root, self.first, "one")
            ev2, tei2, img2 = self._write_source_pair(root, self.second, "two")
            pairs = [(ev1, tei1), (ev2, tei2)]
            # Production must reject even mutually consistent forged local
            # image+manifest bytes: these are not the pinned Git manifests.
            with self.assertRaisesRegex(ValueError, "manifest.*pinned|pinned.*manifest"):
                verify_source_gated_batch(pairs, root / "images")
            # Only in synthetic unit tests, mock the upstream trust anchor to
            # exercise the *separate* image and deterministic TEI checks.
            with patch("franko_tei.pilot_tf_batch._verify_pinned_manifest"):
                graph = verify_source_gated_batch(pairs, root / "images")
                self.assertEqual(
                    sum(t == "page" for t in graph.node_features["otype"].values()), 2)
                img2.write_bytes(b"corrupted synthetic scan")
                with self.assertRaisesRegex(ValueError, "checksum"):
                    verify_source_gated_batch(pairs, root / "images")
                img2.write_bytes(b"SYNTHETIC-two")
                tei2.write_text(tei2.read_text("utf8").replace("ѣ́", "е", 1), encoding="utf8")
                with self.assertRaisesRegex(ValueError, "TEI|match"):
                    verify_source_gated_batch(pairs, root / "images")

    def test_refuses_to_overwrite_and_rejects_single_entry(self):
        with self.assertRaisesRegex(ValueError, "two|multiple"):
            merge_pilot_graphs([("4", 100, self.first_graph)])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ev1, tei1, _ = self._write_source_pair(root, self.first, "one")
            ev2, tei2, _ = self._write_source_pair(root, self.second, "two")
            out = root / "existing-output"
            out.mkdir()
            with self.assertRaises(FileExistsError):
                save_pilot_tf_batch(
                    [(ev1, tei1), (ev2, tei2)], root / "images", out)


if __name__ == "__main__":
    unittest.main()
