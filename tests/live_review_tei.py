"""Real accepted review ledger + native source image + official TEI P5 RNG.

Run only in a full-history trusted checkout. Does not certify historical glyphs.
"""
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from lxml import etree
from franko_tei.pilot_batch import fetch_selected_images, _download
from franko_tei.pilot_tei import TEI, XML, extract_transcribed_lines
from franko_tei.review_adjudication import project_lines
from franko_tei.review_tei import ledger_at_checkout, verified_editorial_tei
from franko_tei.review_bundle import git_source_loader

ROOT=Path(__file__).resolve().parents[1]
REF=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
NS={"t":TEI}
ID="{"+XML+"}id"
PAGES=("pilot/vol1_scan00104_single_reading.json","pilot/vol4_scan00068_single_reading.json")


def main():
    ledger=ledger_at_checkout(ROOT,REF)
    loader=git_source_loader(ROOT,REF)
    with TemporaryDirectory() as tmp:
        work=Path(tmp)
        images=work/"images"
        fetch_selected_images([ROOT/path for path in PAGES],images)
        rng=work/"tei_all.rng"
        _download("https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_all.rng",rng)
        schema=etree.RelaxNG(etree.parse(str(rng)))
        for path in PAGES:
            raw=loader(REF,path)
            rows=project_lines(raw,path,ledger,source_loader=loader,projection_commit=REF)
            accepted=[r for r in rows if r["status"]!="agent_unverified"]
            assert accepted, path
            xml=verified_editorial_tei(ROOT,path,images,REF)
            schema.assertValid(etree.fromstring(xml.encode("utf-8")))
            assert extract_transcribed_lines(xml)==[r["text"] for r in rows]
            root=ET.fromstring(xml)
            notes={n.get(ID):n for n in root.findall(".//t:note[@type='editorial-review']",NS)}
            assert len(notes)==len(accepted)
            for row in accepted:
                n=notes["review-"+row["event_id"]]
                assert n.find("t:quote",NS).text==row["original"]
                assert n.find("t:seg[@type='review-kind']",NS).text==row["review_kind"]
                assert n.find("t:ref[@type='review-issue']",NS).get("target")==row["issue_url"]
                assert n.get("subtype")==row["status"]
            if "00104" in path:
                assert any("Сиѳъ" in r["text"] and "Сидъ" in r["original"]
                           for r in accepted), "actual Seth correction missing"
            assert (ROOT/path).read_bytes()==raw
            print(f"PASS native image + TEI P5 + {len(accepted)} accepted line decisions: {path}")
        # Native bytes cannot be replaced even when a matching review is present.
        source=json.loads(loader(REF,PAGES[0]))
        image=images/source["source_image_path"]
        image.write_bytes(image.read_bytes()+b"tamper")
        try:
            verified_editorial_tei(ROOT,PAGES[0],images,REF)
        except ValueError:
            pass
        else:
            raise AssertionError("modified source image accepted")


if __name__=="__main__":
    main()
