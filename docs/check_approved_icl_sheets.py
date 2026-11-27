"""Validate bounded approved-atlas sheets (local, no source redistribution)."""
import json
import sys
from pathlib import Path
from PIL import Image

def check_sheets(directory, atlas_path=None):
    directory = Path(directory)
    atlas_path = Path(atlas_path) if atlas_path else Path(__file__).with_name("monomakh-icl-approved-atlas.json")
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    index = json.loads((directory / "index.json").read_text(encoding="utf-8"))
    assert index["schema"] == "franko-approved-icl-sheets-v1"
    all_ids = [r["id"] for r in atlas["examples"]]
    native = [r["id"] for r in atlas["examples"] if "source" in r]
    expected = all_ids if index["previews_included"] else native
    assert index["omitted_ids"] == [x for x in all_ids if x not in expected]
    seen = []
    for i, sheet in enumerate(index["sheets"], 1):
        assert sheet["file"] == f"sheet-{i:02d}.png"
        assert 1 <= len(sheet["ids"]) <= 8
        seen.extend(sheet["ids"])
        with Image.open(directory / sheet["file"]) as im:
            assert im.format == "PNG"
            assert im.width <= 1200 and im.height <= 1200
            assert im.size == (sheet["width"], sheet["height"])
            im.verify()
    assert seen == expected
    assert len(seen) == len(set(seen))
    assert set(directory.glob("sheet-*.png")) == {directory / s["file"] for s in index["sheets"]}
    print(f"Verified {len(seen)} approved examples on {len(index['sheets'])} bounded PNGs; omitted {len(index['omitted_ids'])}")
    return index

if __name__ == "__main__":
    check_sheets(sys.argv[1])
