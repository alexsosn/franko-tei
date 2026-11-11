"""Source inventory. A catalogue URL is not evidence of downloaded/verified bytes."""
from importlib.resources import files
import json
import re

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load_catalog(path=None):
    raw = (files("franko_tei") / "sources.json").read_text(encoding="utf-8") if path is None else open(path, encoding="utf-8").read()
    catalog = json.loads(raw)
    volumes = catalog.get("volumes", [])
    if len(volumes) != 5 or [v.get("id") for v in volumes] != [str(i) for i in range(1, 6)]:
        raise ValueError("Expected unique, ordered volumes 1–5")
    for volume in volumes:
        for field in ("landing_url", "pdf_url"):
            if not volume.get(field, "").startswith("https://dimfranka.lviv.ua/"):
                raise ValueError(f"Invalid {field} for volume {volume['id']}")
        count = volume.get("scan_pages")
        if count is not None and (not isinstance(count, int) or isinstance(count, bool) or count < 1):
            raise ValueError("scan_pages must be a positive integer or null")
        checksum = volume.get("sha256")
        if checksum is not None and not _SHA256.fullmatch(checksum):
            raise ValueError("sha256 must contain 64 lowercase hex characters")
    return catalog


def get_volume(catalog, identifier):
    try:
        return next(v for v in catalog["volumes"] if v["id"] == str(identifier))
    except StopIteration as exc:
        raise ValueError(f"Unknown volume {identifier}") from exc
