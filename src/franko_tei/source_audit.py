"""Download museum PDF locally and audit its bytes, not the printed content's fidelity.

Never upload the PDF itself: digital-scan redistribution terms are unverified.
"""
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from .ingest import sha256_file

_ALLOWED_HOSTS = {"dimfranka.lviv.ua", "files.dimfranka.com"}


def _trusted_url(url):
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in _ALLOWED_HOSTS and parsed.username is None and parsed.password is None


def download_source(volume, destination, max_bytes=1_000_000_000):
    """Stream explicitly catalogued volume to a local path; return SHA256 and byte count.

    Following a redirect is allowed only between the museum's approved hosts.
    A failed download cannot overwrite the existing destination.
    """
    url = volume["pdf_url"]
    if not _trusted_url(url):
        raise ValueError("Untrusted source URL")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    digest = sha256()
    total = 0
    try:
        with urlopen(url, timeout=120) as response:
            if not _trusted_url(response.geturl()):
                raise ValueError("Download redirected to an untrusted host")
            with temporary.open("wb") as out:
                prefix = b""
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError("Download exceeds size limit")
                    digest.update(chunk)
                    if len(prefix) < 5:
                        prefix += chunk[:5 - len(prefix)]
                    out.write(chunk)
                if not prefix.startswith(b"%PDF-"):
                    raise ValueError("Remote content is not a PDF")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return {"volume": volume["id"], "bytes": total, "sha256": digest.hexdigest(), "source_url": url}


def inspect_pdf(volume, path):
    """Report basic physical PDF properties, never interpret OCR as verified text."""
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PDF audit needs PyMuPDF: pip install -e '.[pdf]'") from exc
    path = Path(path)
    with fitz.open(path) as pdf:
        if not pdf.is_pdf:
            raise ValueError("File is not a PDF")
        chars = [len(page.get_text("text")) for page in pdf]
    return {
        "volume": volume["id"], "source_url": volume["pdf_url"],
        "sha256": sha256_file(path), "bytes": path.stat().st_size,
        "page_count": len(chars), "pages_with_embedded_text": sum(c > 0 for c in chars),
        "embedded_text_chars_by_page": chars,
        "status": "source-metadata-only; neither OCR accuracy nor page alignment verified",
    }
