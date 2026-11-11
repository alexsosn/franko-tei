"""Extract native scan images and untouched Poppler OCR text; never recognize text.

This deliberately narrow exporter requires one scan image per PDF page. It is not
a general page renderer (PDF vector overlays, crops and rotations are not baked in).
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit

from .catalog import load_catalog
from .ingest import sha256_file


def _run(*args):
    return subprocess.check_output([str(a) for a in args])


def split_ocr_pages(raw, count):
    """Remove only page separators; retain empty pages and every other byte."""
    pages = raw.split(b'\f')
    if len(pages) != count + 1 or pages[-1] != b'':
        raise ValueError('OCR page boundaries do not match PDF page count')
    return pages[:-1]


def export_volume(pdf_path, volume, output_root):
    from PIL import Image

    pdf_path, output_root = Path(pdf_path), Path(output_root)
    identifier = str(volume['id'])
    if identifier not in ('1', '2', '3', '4', '5'):
        raise ValueError('Expected volume 1–5')
    destination = output_root / f'vol{identifier}'
    ocr_destination = output_root / 'original_ocr' / f'vol{identifier}'
    if destination.exists() or ocr_destination.exists():
        raise FileExistsError(f'Refusing to overwrite {destination} or {ocr_destination}')
    info = _run('pdfinfo', pdf_path).decode('utf-8')
    count = int(re.search(r'^Pages:\s+(\d+)$', info, re.MULTILINE)[1])
    inventory = _run('pdfimages', '-list', pdf_path).decode('utf-8')
    rows = [line.split() for line in inventory.splitlines()[2:] if line.strip()]
    groups = {page: [] for page in range(1, count + 1)}
    for row in rows:
        groups[int(row[0])].append(row)
    for group in groups.values():
        if ([r[2] for r in group] not in (['image'], ['image', 'smask'])
                or any(r[5] not in ('rgb', 'gray') or r[7] != '8' for r in group)):
            raise ValueError('Expected exactly one image per page, optionally with one soft mask')
    checksum = sha256_file(pdf_path)
    raw_text = _run('pdftotext', '-raw', '-enc', 'UTF-8', '-eol', 'unix', pdf_path, '-')
    texts = split_ocr_pages(raw_text, count)
    output_root.mkdir(parents=True, exist_ok=True)
    # Nothing is published until the entire volume has passed extraction checks.
    with tempfile.TemporaryDirectory(prefix='.page-assets-', dir=output_root) as temp:
        staging = Path(temp)
        images = staging / f'vol{identifier}'
        ocr = staging / 'ocr'
        images.mkdir()
        ocr.mkdir()
        extracted = _run('pdfimages', '-png', '-j', '-p', '-print-filenames',
                         pdf_path, staging / 'extracted').decode('utf-8').splitlines()
        if len(extracted) != len(rows):
            raise ValueError('Extracted image count differs from PDF inventory')
        files = iter(Path(p) for p in extracted)
        (ocr / 'full.txt').write_bytes(raw_text)
        (images / 'pdfinfo.txt').write_text(info, encoding='utf-8')
        (images / 'pdfimages-list.txt').write_text(inventory, encoding='utf-8')
        manifest = {
            'volume': identifier, 'source_file': pdf_path.name,
            'source_url': volume['pdf_url'], 'source_sha256': checksum,
            'source_bytes': pdf_path.stat().st_size, 'page_count': count,
            'status': 'ocr_unchecked', 'scan_redistribution_permission': 'unverified',
            'image_method': 'pdfimages -png -j -p; native JPEG bytes, lossless PNG otherwise; masks preserved',
            'ocr_method': 'pdftotext -raw -enc UTF-8 -eol unix; no correction or normalization',
            'poppler_version': subprocess.run(['pdfimages', '-v'], capture_output=True, text=True, check=True).stderr.splitlines()[0],
            'full_ocr': {'path': f'original_ocr/vol{identifier}/full.txt',
                         'sha256': sha256_file(ocr / 'full.txt')},
            'pages': [],
        }
        for number, group in groups.items():
            base = next(files)
            width, height = map(int, group[0][3:5])
            with Image.open(base) as image:
                if image.size != (width, height):
                    raise ValueError('Extracted image dimensions differ from inventory')
            name = f'page-{number:05d}'
            artifacts = []

            def record(path, relative, role):
                artifacts.append({'path': relative, 'sha256': sha256_file(path), 'role': role})

            if len(group) == 2:
                mask = next(files)
                originals = images / 'original_images'
                originals.mkdir(exist_ok=True)
                base = base.rename(originals / (name + base.suffix))
                mask = mask.rename(originals / (name + '-mask' + mask.suffix))
                record(base, f'vol{identifier}/original_images/{base.name}', 'native_image')
                record(mask, f'vol{identifier}/original_images/{mask.name}', 'native_soft_mask')
                target = images / (name + '.png')
                with Image.open(base) as image, Image.open(mask) as alpha:
                    result = image.convert('RGBA')
                    result.putalpha(alpha.convert('L'))
                    result.save(target)
            else:
                target = base.rename(images / (name + base.suffix))
            record(target, f'vol{identifier}/{target.name}', 'page_image')
            text_path = ocr / (name + '.txt')
            text_path.write_bytes(texts[number - 1])
            record(text_path, f'original_ocr/vol{identifier}/{text_path.name}', 'embedded_ocr')
            manifest['pages'].append({
                'scan_page': number, 'printed_page': None, 'status': 'ocr_unchecked',
                'width': width, 'height': height, 'ocr_bytes': len(texts[number - 1]),
                'artifacts': artifacts,
            })
        if sha256_file(pdf_path) != checksum:
            raise ValueError('Source PDF changed during extraction')
        metadata = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
        (images / 'manifest.json').write_text(metadata, encoding='utf-8')
        (ocr / 'manifest.json').write_text(metadata, encoding='utf-8')
        ocr_destination.parent.mkdir(parents=True, exist_ok=True)
        images.rename(destination)
        ocr.rename(ocr_destination)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=Path('images/source_pdfs'))
    parser.add_argument('--output', type=Path, default=Path('images'))
    args = parser.parse_args()
    volumes = load_catalog()['volumes']
    sources = [args.source_dir / unquote(urlsplit(v['pdf_url']).path.rsplit('/', 1)[-1]) for v in volumes]
    for source, volume in zip(sources, volumes):
        if not source.is_file():
            parser.error(f'Missing source: {source}')
        if (args.output / f"vol{volume['id']}").exists() or (args.output / 'original_ocr' / f"vol{volume['id']}").exists():
            parser.error(f"Volume {volume['id']} already exists; choose an empty output directory")
    for source, volume in zip(sources, volumes):
        result = export_volume(source, volume, args.output)
        print(f"Volume {volume['id']}: {result['page_count']} pages; SHA256 {result['source_sha256']}", flush=True)


if __name__ == '__main__':
    main()
