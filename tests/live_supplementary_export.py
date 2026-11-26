"""Actual pinned images, official TEI P5 and real TF roundtrip for photo subset."""
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from lxml import etree
from tf.fabric import Fabric
from franko_tei.pilot_batch import fetch_selected_images, _download
from franko_tei.pilot_tei import extract_transcribed_lines, TEI, XML
from franko_tei.supplementary import supplementary_pages, export_supplementary

ROOT=Path(__file__).resolve().parents[1]
REV=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
NS={"t":TEI}
ID="{"+XML+"}id"


def main():
    pages=supplementary_pages(ROOT/"pilot",REV)
    with TemporaryDirectory() as tmp:
        work=Path(tmp)
        images=work/"images"
        fetch_selected_images([ROOT/path for path in pages],images)
        rng=work/"tei_all.rng"
        _download("https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_all.rng",rng)
        schema=etree.RelaxNG(etree.parse(str(rng)))
        output=work/"export"
        export_supplementary(ROOT,REV,images,output)
        api=Fabric(locations=str(output/"tf"),silent="deep").load(
            "glyph codepoint teiId pageKey status lang script regionKind sourceNoteTarget")
        assert api
        assert len(api.F.otype.s("page"))==6
        line_nodes={api.F.teiId.v(n):n for n in api.F.otype.s("line")}
        for path,page in pages.items():
            xml=(output/"tei"/(Path(path).stem+".xml")).read_text(encoding="utf-8")
            schema.assertValid(etree.fromstring(xml.encode("utf-8")))
            source=json.loads((ROOT/path).read_bytes())
            expected=extract_transcribed_lines(xml)
            root=ET.fromstring(xml)
            ids=[lb.get(ID) for lb in root.findall(".//t:lb",NS)]
            assert ["".join(api.F.glyph.v(s) for s in api.L.d(line_nodes[i],otype="char"))
                    for i in ids]==expected
            assert len(ids)==sum(len(r["lines"]) for r in source["reading"]["regions"])
            assert not root.findall(".//t:gap",NS)
            if (page["volume"],page["scan"])==("4",18):
                note=root.find(".//t:note[@type='source-footnote']",NS)
                marker=line_nodes["lb-v4-s00018-preface-line-05"]
                assert api.F.sourceNoteTarget.v(marker)==note.get(ID)
                note_node=next(n for n in api.F.otype.s("region") if api.F.teiId.v(n)==note.get(ID))
                assert api.F.regionKind.v(note_node)=="note"
            print("PASS native image + P5 + TF actual source text:",path)
        assert all(api.F.status.v(n)=="agent_unverified" for n in api.F.otype.s("page"))
        # No successful export after image bytes are changed.
        source=json.loads((ROOT/next(iter(pages))).read_bytes())
        image=images/source["source_image_path"]
        image.write_bytes(image.read_bytes()+b"tamper")
        try:
            export_supplementary(ROOT,REV,images,work/"invalid")
        except ValueError:
            pass
        else:
            raise AssertionError("tampered source accepted")
        assert not (work/"invalid").exists()


if __name__=="__main__":
    main()
