"""RED-first: heterogeneous real pages have compatible but nonidentical TF feature metadata.

All strings used in this test are synthetic transformations of a saved unverified
IV/100 draft; this is a schema regression, not a new historical transcription.
"""
import copy
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import render_pilot_tei
from franko_tei.pilot_tf import build_tf_graph
from franko_tei.pilot_tf_batch import merge_pilot_graphs

ROOT=Path(__file__).resolve().parents[1]
SAMPLE=json.loads((ROOT/"pilot/vol4_scan00100_single_reading.json").read_text("utf8"))

def graphs():
    original=copy.deepcopy(SAMPLE)
    other=copy.deepcopy(SAMPLE)
    other["volume"]="3"
    other["scan_page"]=130
    other["source_image_path"]="vol3/page-00130.jpg"
    # Intentionally synthetic second page with different optional features.
    for region in other["reading"]["regions"]:
        for line in region["lines"]:
            line["language_spans"]=[]
    other["reading"]["uncertainty_notes"]=[]
    return (build_tf_graph(render_pilot_tei(original,1190,1794)),
            build_tf_graph(render_pilot_tei(other,1190,1794)))

class HeterogeneousMetadataTests(unittest.TestCase):
    def test_union_optional_features_without_erasing_metadata(self):
        first,second=graphs()
        self.assertNotEqual(first.metadata,second.metadata)
        merged=merge_pilot_graphs([("4",100,first),("3",130,second)])
        self.assertIn("noteText",merged.metadata)
        self.assertIn("languageUncertain",merged.metadata)
        self.assertEqual(merged.metadata["noteText"],first.metadata["noteText"])
        self.assertEqual(merged.metadata["languageUncertain"],
                         first.metadata["languageUncertain"])
        self.assertEqual(set(merged.node_features["pageKey"].values()),
                         {"v4-s00100","v3-s00130"})

    def test_conflicting_value_types_still_fail_closed(self):
        first,second=graphs()
        second.metadata["glyph"]["valueType"]="int"
        with self.assertRaisesRegex(ValueError,"incompatible|metadata|valueType"):
            merge_pilot_graphs([("4",100,first),("3",130,second)])

    def test_conflicting_section_metadata_still_fail_closed(self):
        first,second=graphs()
        second.metadata["otext"]["sectionTypes"]="another section convention"
        with self.assertRaisesRegex(ValueError,"incompatible|metadata|section"):
            merge_pilot_graphs([("4",100,first),("3",130,second)])

if __name__=="__main__":
    unittest.main()
