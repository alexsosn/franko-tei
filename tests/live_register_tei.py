"""Native JPEG hash, TEI P5 RNG and exact source round-trip for register pages."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from lxml import etree

from franko_tei.pilot_tei import render_pilot_tei, validate_single_draft
from franko_tei.pilot_batch import fetch_selected_images, _download
from franko_tei.register_tei import render_source_gated_register_tei, extract_register_source_lines

ROOT = Path(__file__).resolve().parents[1]
NS = {"t": "http://www.tei-c.org/ns/1.0"}


def main():
    files = [ROOT / f"pilot/vol3_scan{s:05d}_single_reading.json" for s in (34,72,73,74,86)]
    with TemporaryDirectory() as tmp:
        work = Path(tmp)
        images = work/"images"
        fetch_selected_images(files, images)
        rng = work/"tei_all.rng"
        _download("https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_all.rng", rng)
        schema = etree.RelaxNG(etree.parse(str(rng)))
        outputs = {}
        for file in files:
            raw = file.read_bytes()
            source = json.loads(raw)
            scan = source["scan_page"]
            if scan == 86:
                measured = validate_single_draft(source,images)
                xml = render_pilot_tei(source,measured["width"],measured["height"])
                root = etree.fromstring(xml.encode())
                schema.assertValid(root)
                outputs[scan] = root
                continue
            name = "vol3_apostle_register_34" if scan == 34 else "vol3_disciple_register_72_74"
            annotation = json.loads((ROOT/f"pilot/structure/{name}.json").read_bytes())
            xml = render_source_gated_register_tei(raw, annotation, images)
            root = etree.fromstring(xml.encode())
            schema.assertValid(root)
            outputs[scan] = root
            assert extract_register_source_lines(xml) == source["reading"]["raw_response"].split("\n")
            assert len(root.xpath("//t:table",namespaces=NS)) == 1
            assert len(root.xpath("//t:lb",namespaces=NS)) == sum(
                len(r["lines"]) for r in source["reading"]["regions"])
            print("PASS native JPEG + TEI P5 RNG + exact source roundtrip:", scan)
        for scan, root in outputs.items():
            for e in root.xpath("//t:table | //t:link[@type='authorial-erratum']",namespaces=NS):
                refs = [e.get(k) for k in ("prev","next") if e.get(k)]
                refs += e.get("target","").split()
                for ref in refs:
                    file, ident = ref.split("#")
                    target_scan = int(file[6:11]) if file else scan
                    assert len(outputs[target_scan].xpath("//*[@xml:id=$ident]",ident=ident)) == 1, ref
        source = json.loads(raw := files[3].read_bytes())
        annotation = json.loads((ROOT/"pilot/structure/vol3_disciple_register_72_74.json").read_bytes())
        image = images/source["source_image_path"]
        image.write_bytes(image.read_bytes()+b"tamper")
        try:
            render_source_gated_register_tei(raw,annotation,images)
        except ValueError:
            pass
        else:
            raise AssertionError("tampered image accepted")


if __name__ == "__main__":
    main()
