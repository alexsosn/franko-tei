"""Convert one explicitly UNVERIFIED pilot TEI page to a real TF feature graph.

No OCR or manuscript witness values are synthesized. All character slots are
copied code point for code point from physical lb-anchored lines in the TEI.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import re
from xml.etree import ElementTree as ET

TEI='http://www.tei-c.org/ns/1.0'
XML='http://www.w3.org/XML/1998/namespace'
ID=f'{{{XML}}}id'
LANG=f'{{{XML}}}lang'

def tag(name):
    return f'{{{TEI}}}{name}'

@dataclass
class Graph:
    node_features: dict
    edge_features: dict
    metadata: dict


def _required_id(element, label, seen):
    identifier=element.get(ID)
    if not identifier or identifier in seen:
        raise ValueError(f'missing/duplicate {label} TEI xml:id')
    seen.add(identifier)
    return identifier


def _zones(surface):
    """Validate native image bounds and explicit region→line zone nesting."""
    seen=set(); zones={}
    try:
        sx0,sy0,sx1,sy1=[int(surface.get(k)) for k in ('ulx','uly','lrx','lry')]
    except (ValueError,TypeError) as exc:
        raise ValueError('malformed facsimile surface bounds') from exc
    if sx0<0 or sy0<0 or sx1<=sx0 or sy1<=sy0:
        raise ValueError('invalid facsimile surface bounds')
    def collect(zone,parent_id,parent_bounds):
        ident=_required_id(zone,'zone',seen)
        try:
            raw=[zone.get(k) for k in ('ulx','uly','lrx','lry')]
            x0,y0,x1,y1=[Decimal(value) for value in raw]
        except (ValueError,InvalidOperation,TypeError) as exc:
            raise ValueError('malformed facsimile zone coordinates') from exc
        if not all(value.is_finite() for value in (x0,y0,x1,y1)):
            raise ValueError('nonfinite facsimile zone coordinates')
        if (x0<parent_bounds[0] or y0<parent_bounds[1]
                or x1>parent_bounds[2] or y1>parent_bounds[3]
                or x1<=x0 or y1<=y0):
            raise ValueError('facsimile zone outside parent bounds')
        if zone.get('type') not in ('estimated','measured'):
            raise ValueError('facsimile zone type must be estimated or measured')
        zones[ident]={'x':raw[0],'y':raw[1],'w':str(x1-x0),'h':str(y1-y0),
                      'estimated':zone.get('type')=='estimated',
                      'parent':parent_id}
        if parent_id is not None and zone.findall(tag('zone')):
            raise ValueError('facsimile zone nesting deeper than region/line')
        for nested in zone:
            if nested.tag != tag('zone'):
                raise ValueError('unsupported facsimile zone child')
            collect(nested,ident,(x0,y0,x1,y1))
    for region_zone in surface:
        if region_zone.tag==tag('graphic'):
            continue
        if region_zone.tag!=tag('zone'):
            raise ValueError('unsupported facsimile surface child')
        collect(region_zone,None,(sx0,sy0,sx1,sy1))
    return zones


def _get_text_lines(ab, seen):
    if ab.text and ab.text.strip():
        raise ValueError('unanchored transcription text before line break')
    lines=[]; current=None
    for child in ab:
        if child.tag==tag('lb'):
            if list(child) or child.text:
                raise ValueError('physical lb must be an empty element')
            if current is not None:
                lines.append(current)
            current={'id':_required_id(child,'line',seen),
                     'facs':child.get('facs'), 'parts':[]}
            if child.tail:
                current['parts'].append({'text':child.tail,'seg':None})
        elif child.tag==tag('seg'):
            if current is None:
                raise ValueError('segment without physical line anchor')
            if list(child):
                raise ValueError('nested markup in pilot language span is not supported')
            sid=_required_id(child,'language span',seen)
            if child.get('type')!='language-attribution':
                raise ValueError('unexpected language span type')
            if not child.text:
                raise ValueError('empty language span')
            current['parts'].append({'text':child.text,'seg':{
                'id':sid,'lang':child.get(LANG), 'script':child.get('subtype'),
                'uncertain':int(child.get('cert')=='low')}})
            if child.tail:
                current['parts'].append({'text':child.tail,'seg':None})
        else:
            raise ValueError('unexpected transcribed element; refusing silent text loss')
    if current is not None:
        lines.append(current)
    if not lines:
        raise ValueError('region has no physical line anchors')
    for line in lines:
        if not any(part['text'] for part in line['parts']):
            raise ValueError('empty text line cannot become TF slot container')
    return lines


def _read_source(root):
    headers=root.findall(tag('teiHeader'))
    if len(headers)!=1:
        raise ValueError('missing TEI header')
    pub=' '.join(''.join(x.itertext()) for x in root.findall(f'.//{tag("publicationStmt")}'))
    if 'agent_unverified' not in pub:
        raise ValueError('only agent_unverified pilot TEI is accepted')
    identifiers={el.get('type'):el.text for el in root.findall(f'.//{tag("sourceDesc")}//{tag("idno")}')}
    image_sha=identifiers.get('Image-SHA256-claim')
    pdf_sha=identifiers.get('PDF-SHA256-claim')
    if not all(isinstance(h,str) and re.fullmatch(r'[0-9a-fA-F]{64}',h)
               for h in (image_sha,pdf_sha)):
        raise ValueError('missing explicit image/PDF checksums from TEI sourceDesc')
    return image_sha,pdf_sha


def build_tf_graph(xml):
    root=ET.fromstring(xml)
    if root.tag!=tag('TEI'):
        raise ValueError('expected TEI P5 namespace')
    image_sha,pdf_sha=_read_source(root)
    surfs=root.findall(f'.//{tag("facsimile")}/{tag("surface")}')
    pages=root.findall(f'.//{tag("body")}/{tag("div")}')
    if len(surfs)!=1 or len(pages)!=1:
        raise ValueError('minimal pilot currently accepts exactly one facsimile/page')
    surf,page=surfs[0],pages[0]
    seen=set()
    surface_id=_required_id(surf,'surface',seen)
    page_id=_required_id(page,'page',seen)
    if page.get('type')!='page' or page.get('facs')!='#'+surface_id:
        raise ValueError('page must refer to its facsimile surface')
    pbs=page.findall(tag('pb'))
    if len(pbs)!=1 or pbs[0].get('facs')!='#'+surface_id:
        raise ValueError('physical page break/facsimile mismatch')
    try:
        scan=int(page.get('n'))
    except (ValueError,TypeError) as exc:
        raise ValueError('invalid physical scan index') from exc
    if scan<1 or pbs[0].get('n')!=str(scan) or surf.get('n')!=str(scan):
        raise ValueError('scan page index mismatch')
    images=surf.findall(tag('graphic'))
    if len(images)!=1 or not images[0].get('url','').startswith('https://raw.githubusercontent.com/alexsosn/franko-tei/'):
        raise ValueError('missing pinned image URL')
    zones=_zones(surf)
    if page.text and page.text.strip():
        raise ValueError('unanchored page transcription text')
    for child in page:
        if child.tail and child.tail.strip():
            raise ValueError('unanchored transcription text after a page element')
        if child.tag==tag('pb') and (child.text or len(child)):
            raise ValueError('physical page break must not contain transcription text')
    children=[ch for ch in page if ch.tag==tag('ab')]
    if not children or any(ch.tag not in (tag('ab'),tag('pb'),tag('note')) for ch in page):
        raise ValueError('unsupported page structure')
    # First collect glyph slots, then allocate non-slot nodes in type groups.
    glyph={}; codepoint={}; span_entries=[]; line_entries=[]; region_entries=[]
    line_by_id={}; page_slots=[]
    for ab in children:
        region_id=_required_id(ab,'region',seen)
        kind=ab.get('type')
        if not kind or not ab.get('facs','').startswith('#'):
            raise ValueError('region type/facsimile reference required')
        zone_id=ab.get('facs')[1:]
        if zone_id not in zones or zones[zone_id]['parent'] is not None:
            raise ValueError('region facsimile zone must be a top-level zone')
        region_slots=[]
        for line in _get_text_lines(ab,seen):
            line_zone=line['facs'][1:] if line['facs'] and line['facs'].startswith('#') else None
            if line_zone not in zones or zones[line_zone]['parent'] != zone_id:
                raise ValueError('physical line facsimile zone must belong to its region parent')
            begin=len(glyph)+1
            for part in line['parts']:
                start=len(glyph)+1
                for ch in part['text']:
                    n=len(glyph)+1
                    glyph[n]=ch
                    codepoint[n]=ord(ch)
                end=len(glyph)
                if part['seg'] is not None:
                    if end < start:
                        raise ValueError('empty segment lost all character slots')
                    span_entries.append({'slots':set(range(start,end+1)),**part['seg']})
            end=len(glyph)
            line_slots=set(range(begin,end+1))
            if not line_slots:
                raise ValueError('line with zero slots')
            line_entries.append({'id':line['id'],'slots':line_slots,'zone':zones[line_zone]})
            line_by_id[line['id']]=line_slots
            region_slots.extend(range(begin,end+1))
        if not region_slots:
            raise ValueError('region without text slots')
        region_entries.append({'id':region_id,'slots':set(region_slots),'kind':kind,'zone':zones[zone_id]})
        page_slots.extend(region_slots)
    if not page_slots or len(page_slots)!=len(glyph):
        raise ValueError('source slots are not contiguous')
    notes=[]
    for note in page.findall(tag('note')):
        nid=_required_id(note,'agent uncertainty',seen)
        if note.get('type')!='agent-reading-uncertainty' or not note.get('corresp','').startswith('#'):
            raise ValueError('invalid uncertainty note')
        reference=note.get('corresp')[1:]
        if reference not in line_by_id or not (note.text or '').strip():
            raise ValueError('uncertainty note has no source line')
        notes.append({'id':nid,'slots':line_by_id[reference],'text':note.text})
    # Remove any ambiguity about what the printed page label signifies.
    page_label_nodes=[x for x in region_entries if x['kind']=='page_number']
    label=''.join(glyph[n] for n in sorted(page_label_nodes[0]['slots'])) if len(page_label_nodes)==1 else None
    node_features={'otype':{n:'char' for n in glyph}, 'glyph':glyph,
                   'codepoint':codepoint}
    edge_features={'oslots':{}}
    def feature(name,node,value):
        if value is not None:
            node_features.setdefault(name,{})[node]=value
    def non_slot(type_,entry):
        n=len(node_features['otype'])+1
        node_features['otype'][n]=type_
        edge_features['oslots'][n]=entry['slots']
        feature('teiId',n,entry['id'])
        return n
    for entry in span_entries:
        n=non_slot('languageSpan',entry)
        feature('lang',n,entry['lang'])
        feature('script',n,entry['script'])
        feature('languageUncertain',n,entry['uncertain'])
    for entry in notes:
        n=non_slot('uncertainty',entry)
        feature('noteText',n,entry['text'])
    for entry in line_entries:
        n=non_slot('line',entry)
        feature('lineId',n,entry['id'])
        for key in ('x','y','w','h'):
            feature(key,n,entry['zone'][key])
        feature('geometryEstimated',n,int(entry['zone']['estimated']))
    for entry in region_entries:
        n=non_slot('region',entry)
        feature('regionId',n,entry['id'])
        feature('regionKind',n,entry['kind'])
        for key in ('x','y','w','h'):
            feature(key,n,entry['zone'][key])
        feature('geometryEstimated',n,int(entry['zone']['estimated']))
    n=non_slot('page',{'id':page_id,'slots':set(page_slots)})
    feature('scanPage',n,scan)
    feature('observedPrintedPage',n,label)
    feature('status',n,'agent_unverified')
    feature('imageSha',n,image_sha)
    feature('pdfShaClaim',n,pdf_sha)
    feature('imageUrl',n,images[0].get('url'))
    metadata={
        'otext':{'fmt:text-orig-full':'{glyph}',
                 'sectionTypes':'page,region,line',
                 'sectionFeatures':'scanPage,regionId,lineId',
                 'structureTypes':'page,region,line',
                 'structureFeatures':'teiId'},
        'otype':{'valueType':'str'},
        'oslots':{'valueType':'int'},
    }
    integer_features={'codepoint','languageUncertain','scanPage','geometryEstimated'}
    for name in node_features:
        if name not in metadata:
            metadata[name]={'valueType':'int' if name in integer_features else 'str'}
    return Graph(node_features=node_features,edge_features=edge_features,metadata=metadata)


def verify_graph_roundtrip(graph):
    """Reconstruct original physical lines using only node slots and codepoints."""
    features=graph.node_features
    nodes=[n for n,k in features['otype'].items() if k=='line']
    output=[]
    for node in nodes:
        chars=[]
        for slot in sorted(graph.edge_features['oslots'][node]):
            codepoint=features['codepoint'][slot]
            glyph=features['glyph'][slot]
            if glyph!=chr(codepoint):
                raise ValueError('codepoint/glyph disagreement')
            chars.append(glyph)
        output.append(''.join(chars))
    return output



def verify_source_gated_pilot(xml_path, evidence_path, images_root):
    """Verify actual image bytes and immutable one-context TEI before TF graph.

    Independent context review is not part of this pilot; successful checks
    never change the immutable agent_unverified status.
    """
    from .pilot_tei import validate_single_draft, render_pilot_tei

    payload=json.loads(Path(evidence_path).read_text(encoding='utf8'))
    dimensions=validate_single_draft(payload,Path(images_root))
    xml=Path(xml_path).read_text(encoding='utf8')
    regenerated=render_pilot_tei(payload,dimensions['width'],dimensions['height'])
    if xml!=regenerated:
        raise ValueError('TEI does not exactly match source-checked single-reader draft')
    graph=build_tf_graph(xml)
    if '\n'.join(verify_graph_roundtrip(graph)) != payload['reading']['raw_response']:
        raise ValueError('TEI physical line order is not the original raw first reading')
    features=graph.node_features
    pages=[n for n,kind in features['otype'].items() if kind=='page']
    if len(pages)!=1:
        raise ValueError('pilot TF export requires exactly one page')
    p=pages[0]
    if (features['imageSha'][p]!=dimensions['image_sha256']
            or features['pdfShaClaim'][p]!=payload['source_pdf_sha256_claimed_by_manifest']
            or features['scanPage'][p]!=payload['scan_page']
            or features['observedPrintedPage'].get(p)!=payload.get('printed_page_observed')
            or features['status'][p]!='agent_unverified'):
        raise ValueError('TEI/TF source provenance or status mismatch')
    return graph


def save_pilot_tf(xml_path, output, evidence_path, images_root):
    """Atomically create TF feature files; never overwrite prior content."""
    from tf.fabric import Fabric
    output=Path(output)
    if output.exists():
        raise FileExistsError(f'refusing to overwrite {output}')
    graph=verify_source_gated_pilot(xml_path,evidence_path,images_root)
    output.parent.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(prefix='.pilot-tf-',dir=output.parent) as tempdir:
        staging=Path(tempdir)/'tf'
        staging.mkdir()
        fabric=Fabric(locations=str(staging),silent='deep')
        if fabric.save(nodeFeatures=graph.node_features,
                       edgeFeatures=graph.edge_features,metaData=graph.metadata,silent='deep') is not True:
            raise RuntimeError('Text-Fabric refused to write features')
        staging.rename(output)
    return graph


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tei',required=True,type=Path)
    parser.add_argument('--evidence',required=True,type=Path,
                        help='Original single-reader JSON, never reconstructed from OCR')
    parser.add_argument('--images',required=True,type=Path,
                        help='Native source images plus source SHA256 manifest')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(argv)
    try:
        graph=save_pilot_tf(args.tei,args.output,args.evidence,args.images)
    except (ValueError,OSError,RuntimeError,KeyError,ET.ParseError) as exc:
        parser.error(str(exc))
    counts={type_:list(graph.node_features['otype'].values()).count(type_) for type_ in set(graph.node_features['otype'].values())}
    print(f'Wrote source-anchored agent_unverified Text-Fabric pilot to {args.output}: {counts}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
