"""Single-reader *unverified* pilot TEI with facsimile zones; never a released edition.

Unlike `agent_evidence` this deliberately accepts ONE image reading so that
honest first drafts can be persisted without fabricating independent reviewers.
The final version must pass a genuinely separate reader/reviewer gate.
"""
from datetime import date
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

from .ocr_candidates import _get_page_image, _read_manifest
from .agent_evidence import _box, _inside, _required_text, validate_language_spans

TEI = "http://www.tei-c.org/ns/1.0"
XML = "http://www.w3.org/XML/1998/namespace"
PINNED_ASSET_COMMIT = "e871f32537e81f81896f6ce9a6658aba667db9c5"
SOURCE_REPO = "https://raw.githubusercontent.com/alexsosn/franko-tei"
ET.register_namespace("", TEI)


def tag(name):
    return f"{{{TEI}}}{name}"


def xml_id(element, identifier):
    element.set(f"{{{XML}}}id", identifier)


def _id(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", value):
        raise ValueError(f"{label}: invalid XML identifier")
    return value


def _valid_xml_text(text):
    if (not isinstance(text, str) or not text or
            any(not (c in '\t\n\r' or 0x20 <= ord(c) <= 0xD7FF or
                     0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF)
                for c in text)):
        raise ValueError("line is empty or contains an invalid XML character")
    if '\n' in text or '\r' in text:
        raise ValueError("a physical line cannot contain embedded newline")


def validate_single_draft(payload, images_root):
    """Validate first image draft; only actual image bytes authorize its source link.

    This is NOT `validate_evidence`: no peer reading, review or attestation.
    """
    if not isinstance(payload, dict) or payload.get('schema_version') != 'single-image-draft-v0':
        raise ValueError('unsupported single-draft schema')
    if payload.get('status') != 'agent_unverified':
        raise ValueError('single draft must remain agent_unverified')
    if payload.get('asset_commit') != PINNED_ASSET_COMMIT:
        raise ValueError('source asset commit mismatch')
    if payload.get('review') is not None or payload.get('readings') is not None:
        raise ValueError('single-draft path cannot present review or a blind pair')
    volume, page = payload.get('volume'), payload.get('scan_page')
    if volume not in {'1', '2', '3', '4', '5'} or type(page) is not int or page < 1:
        raise ValueError('invalid volume or physical scan page')
    manifest = _read_manifest(Path(images_root), volume)
    if page > manifest['page_count'] or manifest['pages'][page-1].get('scan_page') != page:
        raise ValueError('missing or misindexed scan page')
    entry = manifest['pages'][page-1]
    image_path, image_sha = _get_page_image(Path(images_root), volume, entry)
    if payload.get('source_image_path') != str(image_path.relative_to(Path(images_root))):
        raise ValueError('source image path mismatch')
    if payload.get('source_image_sha256') != image_sha:
        raise ValueError('source image checksum mismatch')
    if payload.get('source_pdf_sha256_claimed_by_manifest') != manifest.get('source_sha256'):
        raise ValueError('source PDF checksum claim mismatch')
    width, height = entry.get('width'), entry.get('height')
    if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
        raise ValueError('invalid image dimensions')
    reading = payload.get('reading')
    for key in ('reader_id', 'model_id', 'context_id', 'instructions', 'raw_response'):
        _required_text(reading, key)
    if 'run_id' not in reading or (reading['run_id'] is not None and
                                    not isinstance(reading['run_id'], str)):
        raise ValueError('run_id must be explicitly null (unknown) or a string')
    if 'model_version' not in reading or (reading['model_version'] is not None and
                                          not isinstance(reading['model_version'], str)):
        raise ValueError('model_version must be explicitly null (unknown) or a string')
    if reading.get('context_independence') != 'single-working-draft':
        raise ValueError('single-working-draft is not independent review')
    if reading.get('source_original_ocr_visible') is not False or reading.get('peer_readings_visible') is not False:
        raise ValueError('draft must preserve image-only first reading conditions')
    coverage = reading.get('coverage')
    if not isinstance(coverage, dict) or coverage.get('entire_image_inspected') is not True:
        raise ValueError('entire page coverage must be declared')
    nontext = coverage.get('nontext_areas')
    if not isinstance(nontext, list):
        raise ValueError('nontext areas must be explicitly listed')
    for area in nontext:
        _box(area.get('bbox_xywh'), width, height, 'nontext area')
        _required_text(area, 'description')
    regions = reading.get('regions')
    if not isinstance(regions, list) or not regions:
        raise ValueError('first reading must include regions')
    region_ids, line_ids = set(), set()
    page_number_texts = []
    line_text_by_id = {}
    raw_lines = []
    for region in regions:
        name = _id(_required_text(region, 'id'), 'region')
        if name in region_ids:
            raise ValueError('duplicate region ID')
        region_ids.add(name)
        if region.get('kind') not in {'body', 'note', 'caption', 'heading', 'page_number', 'facsimile', 'other'}:
            raise ValueError('unknown region kind')
        box = _box(region.get('bbox_xywh'), width, height, 'region')
        if type(region.get('geometry_estimated')) is not bool:
            raise ValueError('region geometry_estimated flag required')
        lines = region.get('lines')
        if not isinstance(lines, list) or not lines:
            raise ValueError('region lines must be nonempty')
        for line in lines:
            identifier = _id(_required_text(line, 'id'), 'line')
            if identifier in line_ids:
                raise ValueError('duplicate line ID')
            line_ids.add(identifier)
            if not _inside(_box(line.get('bbox_xywh'), width, height, 'line'), box):
                raise ValueError('line box outside region')
            if type(line.get('geometry_estimated')) is not bool:
                raise ValueError('line geometry_estimated flag required')
            text = _required_text(line, 'text')
            _valid_xml_text(text)
            line_text_by_id[identifier] = text
            raw_lines.append(text)
            validate_language_spans(text, line.get('language_spans'), reading['reader_id'])
            if region['kind'] == 'page_number':
                page_number_texts.append(text)
    label = payload.get('printed_page_observed')
    if label is not None and (not isinstance(label, str) or not label.strip()):
        raise ValueError('printed_page_observed must be a string or null')
    if label is not None and page_number_texts != [label]:
        raise ValueError('printed page number must match single observed page-number line')
    if reading['raw_response'] != '\n'.join(raw_lines):
        raise ValueError('raw_response differs from initial physical lines; preserve any edits as separate derivations')
    notes = reading.get('uncertainty_notes')
    if not isinstance(notes, list):
        raise ValueError('uncertainty_notes must be explicitly listed, even if empty')
    seen_notes = set()
    for item in notes:
        line_id = _required_text(item, 'line_id')
        source_reading = _required_text(item, 'reading')
        _required_text(item, 'reason')
        key = (line_id, source_reading)
        if key in seen_notes or line_id not in line_text_by_id or source_reading not in line_text_by_id[line_id]:
            raise ValueError('uncertainty note must link to a unique literal reading on an existing line')
        seen_notes.add(key)
    return {'width':width,'height':height,'image_sha256':image_sha}


def _sub(parent, name, text=None, attrs=None):
    el = ET.SubElement(parent, tag(name), attrs or {})
    if text is not None:
        el.text = text
    return el


def _facs_id(volume, page, group, identifier):
    return f"zone-v{volume}-s{page:05d}-{group}-{identifier}"


def _zone(parent, region, volume, page, group, identifier):
    x, y, w, h = region['bbox_xywh']
    zone = _sub(parent, 'zone', attrs={
        'ulx':str(x),'uly':str(y),'lrx':str(x+w),'lry':str(y+h),
        'type': 'estimated' if region['geometry_estimated'] else 'measured'
    })
    xml_id(zone, _facs_id(volume,page,group,identifier))
    return zone


def _append_line(parent, line, volume, page, reading_id):
    lb = _sub(parent,'lb',attrs={'facs':f"#{_facs_id(volume,page,'line',line['id'])}"})
    xml_id(lb, f"lb-v{volume}-s{page:05d}-{line['id']}")
    raw = line['text']
    spans = line['language_spans']
    previous, current = 0, lb
    for span_index, span in enumerate(spans, 1):
        start, end = span['start'], span['end']
        current.tail = (current.tail or '') + raw[previous:start]
        attrs = {'type': 'language-attribution'}
        if span['language'] is not None:
            attrs[f'{{{XML}}}lang'] = span['language']
        if span['script'] is not None:
            attrs['subtype'] = span['script']
        if span['uncertain']:
            attrs['cert'] = 'low'
        seg = _sub(parent,'seg',raw[start:end],attrs)
        xml_id(seg, f"seg-v{volume}-s{page:05d}-{line['id']}-{span_index:03d}")
        current = seg
        previous = end
    current.tail = (current.tail or '') + raw[previous:]


def render_pilot_tei(payload, image_width, image_height):
    """Serialize a separately validated draft; not a verification operation."""
    if payload.get('schema_version') != 'single-image-draft-v0' or payload.get('status') != 'agent_unverified':
        raise ValueError('refusing non-draft or promoted TEI input')
    volume, page = payload['volume'], payload['scan_page']
    draft = payload['reading']
    title = f"Franko, Апокріфи і лєґенди — vol. {volume}, scan {page} (unverified pilot)"
    root = ET.Element(tag('TEI'))
    xml_id(root, f"franko-pilot-v{volume}-s{page:05d}")
    header = _sub(root,'teiHeader')
    fd = _sub(header,'fileDesc')
    ts = _sub(fd,'titleStmt')
    _sub(ts,'title',title)
    resp = _sub(ts,'respStmt')
    _sub(resp,'resp','Single image-reading working draft; no independent blind review')
    _sub(resp,'name',draft['model_id'])
    pub=_sub(fd,'publicationStmt')
    _sub(pub,'p','Unreleased, agent_unverified development artifact. Not an edition release.')
    src=_sub(fd,'sourceDesc')
    bibl=_sub(src,'bibl')
    _sub(bibl,'author','Іван Франко')
    _sub(bibl,'title','Апокріфи і лєґенди з українських рукописів')
    _sub(bibl,'biblScope',f"Printed volume {volume}; scan index {page}; manuscript witnesses not encoded")
    _sub(bibl,'idno',payload['source_pdf_sha256_claimed_by_manifest'],{'type':'PDF-SHA256-claim'})
    _sub(bibl,'idno',payload['source_image_sha256'],{'type':'Image-SHA256-claim'})
    enc=_sub(header,'encodingDesc')
    _sub(enc,'p','Physical line transcription retains original code points and line endings; page geometry is estimated; printed page labels are image observations. No OCR-based corrections or manuscript variants. Unverified first reading only.')
    rev=_sub(header,'revisionDesc')
    _sub(rev,'change','One-context working draft created; no independent second reading.',{'when':'2026-11-11'})
    facs=_sub(root,'facsimile')
    surf=_sub(facs,'surface',attrs={'n':str(page),'ulx':'0','uly':'0','lrx':str(image_width),'lry':str(image_height)})
    xml_id(surf,f"surface-v{volume}-s{page:05d}")
    _sub(surf,'graphic',attrs={'url':f"{SOURCE_REPO}/{PINNED_ASSET_COMMIT}/images/{payload['source_image_path']}"})
    for region in draft['regions']:
        rz=_zone(surf,region,volume,page,'region',region['id'])
        for line in region['lines']:
            _zone(rz,line,volume,page,'line',line['id'])
    text=_sub(root,'text')
    body=_sub(text,'body')
    div=_sub(body,'div',attrs={'type':'page','n':str(page),'facs':f"#surface-v{volume}-s{page:05d}"})
    xml_id(div,f"page-v{volume}-s{page:05d}")
    _sub(div,'pb',attrs={'n':str(page),'facs':f"#surface-v{volume}-s{page:05d}"})
    for region in draft['regions']:
        ab=_sub(div,'ab',attrs={'type':region['kind'], 'facs':f"#{_facs_id(volume,page,'region',region['id'])}"})
        xml_id(ab,f"ab-v{volume}-s{page:05d}-{region['id']}")
        for line in region['lines']:
            _append_line(ab,line,volume,page,draft['reader_id'])
    for index, note in enumerate(draft['uncertainty_notes'], 1):
        n = _sub(div, 'note', f"{note['reading']}: {note['reason']}",
                 {'type': 'agent-reading-uncertainty',
                  'corresp': f"#lb-v{volume}-s{page:05d}-{note['line_id']}"})
        xml_id(n, f"agent-note-v{volume}-s{page:05d}-{index:03d}")
    return '<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(root,encoding='unicode')+'\n'


def extract_transcribed_lines(xml):
    """Losslessly reconstruct physical line strings, with no normalization."""
    root=ET.fromstring(xml)
    result=[]
    for ab in root.findall(f'.//{{{TEI}}}body//{{{TEI}}}ab'):
        current=None
        for child in ab:
            if child.tag == tag('lb'):
                if current is not None:
                    result.append(current)
                current=child.tail or ''
            elif child.tag == tag('seg'):
                if current is None:
                    raise ValueError('segment without line-break anchor')
                current += ''.join(child.itertext()) + (child.tail or '')
            else:
                raise ValueError('unexpected transcribed inline element')
        if current is not None:
            result.append(current)
    return result


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--images',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        payload=json.loads(args.input.read_text(encoding='utf8'))
        dimensions=validate_single_draft(payload,args.images)
        xml=render_pilot_tei(payload,dimensions['width'],dimensions['height'])
        expected=[l['text'] for r in payload['reading']['regions'] for l in r['lines']]
        if extract_transcribed_lines(xml) != expected:
            raise ValueError('exact text roundtrip failed')
        if args.output.exists():
            raise ValueError('refusing to overwrite existing pilot XML')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(xml,encoding='utf8')
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.error(str(exc))
    print(f"Wrote {args.output}; single-reader agent_unverified TEI pilot only")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
