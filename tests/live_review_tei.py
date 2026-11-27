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
from franko_tei.native_collation import load_native_collation
from franko_tei.pilot_tf import build_tf_graph, verify_graph_roundtrip
from franko_tei.review_tf import save_current_tf
from tf.fabric import Fabric

ROOT=Path(__file__).resolve().parents[1]
REF=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
NS={"t":TEI}
ID="{"+XML+"}id"
PAGES=("pilot/vol1_scan00104_single_reading.json","pilot/vol1_scan00316_single_reading.json",
       "pilot/vol4_scan00068_single_reading.json")


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
        expected=[]
        for path in PAGES:
            raw=loader(REF,path)
            rows=project_lines(raw,path,ledger,source_loader=loader,projection_commit=REF,
                               collation=load_native_collation(ROOT,REF,path))
            accepted=[r for r in rows if r["status"]!="agent_unverified"]
            assert accepted, path
            xml=verified_editorial_tei(ROOT,path,images,REF)
            schema.assertValid(etree.fromstring(xml.encode("utf-8")))
            assert extract_transcribed_lines(xml)==[r["text"] for r in rows]
            expected.extend(extract_transcribed_lines(xml))
            root=ET.fromstring(xml)
            assert not root.findall(".//t:note[@type='editorial-review']",NS)
            assert not root.findall(".//t:note[@type='agent-reading-uncertainty']",NS)
            assert root.find(".//t:editionStmt/t:edition",NS).get("n")==REF
            for row in accepted:
                for key in ("event_id","bundle_id","issue_url","evidence_url","collation_reason"):
                    if row.get(key):
                        assert row[key] not in xml
            graph=build_tf_graph(xml)
            assert verify_graph_roundtrip(graph)==[r["text"] for r in rows]
            assert set(graph.node_features.get("noteText",{}).values()) <= {
                "Reading requires verification against the printed source."}
            if "00104" in path:
                assert any("Сиѳъ" in r["text"] and "Сидъ" in r["original"]
                           for r in accepted), "actual Seth correction missing"
            if "00316" in path:
                assert len(accepted)==2
                assert any("понавицею" in r["text"] for r in accepted)
                assert any("понавица" in r["text"] for r in accepted)
            if "00068" in path:
                assert sum(r["text"].startswith("Ѿвѣт:") for r in rows)==7
                assert any(r["text"]=="Ѿвѣт: О́̓сифъ бл҃гоѡбразный." for r in rows)
            assert (ROOT/path).read_bytes()==raw
            print(f"PASS native image + TEI P5 + {len(accepted)} accepted line decisions: {path}")
        # Production path writes one corpus containing two genuine selected pages.
        output=work/"current-tf"
        merged=save_current_tf(ROOT,reversed(PAGES),images,REF,output)
        assert verify_graph_roundtrip(merged)==expected
        assert merged.metadata["otext"]["editionRevision"]==REF
        api=Fabric(locations=str(output),silent="deep").load(
            "glyph codepoint teiId pageKey volume scanPage status regionKind lang noteText")
        assert api, "TF could not load the current text"
        lines=api.F.otype.s("line")
        assert ["".join(api.F.glyph.v(s) for s in api.L.d(n,otype="char")) for n in lines]==expected
        assert [api.F.pageKey.v(n) for n in api.F.otype.s("page")]==["v1-s00104","v1-s00316","v4-s00068"]
        assert all(api.F.status.v(n)=="agent_unverified" for n in api.F.otype.s("page"))
        hits=[n for n in lines if "Сиѳъ" in "".join(api.F.glyph.v(s) for s in api.L.d(n,otype="char"))]
        assert hits and any(api.F.teiId.v(n).endswith("witness-e-death-adam-l003") for n in hits)
        assert sum(t.startswith("Ѿвѣт:") for t in expected)==7
        assert sum("понавицею" in t or "понавица" in t for t in expected)==2
        assert any(api.F.regionKind.v(n)=="note" for n in api.F.otype.s("region"))
        assert any(api.F.lang.v(n)=="cu" for n in api.F.otype.s("languageSpan"))
        assert not any("review" in name.lower() or "contributor" in name.lower()
                       for name in merged.node_features)
        for paths in ([PAGES[0],PAGES[0]], [PAGES[0]]):
            try:
                save_current_tf(ROOT,paths,images,REF,work/"invalid")
            except ValueError:
                pass
            else:
                raise AssertionError("invalid page selection accepted")
        print("PASS real Text-Fabric load and selected-text query on I/104 + I/316 + IV/68")
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
