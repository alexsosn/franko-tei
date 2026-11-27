"""Conservative, line-local lexical contractions in the diplomatic working text.

A proposed expansion is annotation, not an accepted correction, a numeric
value or a normalized spelling. No slots are created for supplied letters.
"""
import unicodedata
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

TEI = "http://www.tei-c.org/ns/1.0"
ID = "{http://www.w3.org/XML/1998/namespace}id"
TITLO = "\u0483"
# Only used as a conservative numeric exclusion in this first slice.
# The annotation author must still distinguish lexical forms from numbers.
CYRILLIC_NUMERALS = set("авгдєезѕиѳіклмнѯопчрстуфхѱѡцшщѫѵ")


def tag(name):
    return f"{{{TEI}}}{name}"


def word_char(char):
    return unicodedata.category(char)[0] in "LM"


def _letters(value):
    return [c for c in value if unicodedata.category(c).startswith("L")]


def _source(value):
    if (not isinstance(value, str) or not value.startswith("https://")
            or any(c.isspace() or unicodedata.category(c).startswith("C")
                   for c in value)):
        raise ValueError("abbreviation expansion needs an HTTPS evidence URL")
    try:
        if not urlsplit(value).hostname:
            raise ValueError("missing hostname")
    except ValueError as exc:
        raise ValueError("invalid abbreviation evidence URL") from exc


def validate_pair(literal, expansion, text=None, start=None, end=None):
    """Narrow single-word titlo pilot, with no silent spelling normalization."""
    if (not isinstance(literal, str) or not literal or TITLO not in literal
            or not all(word_char(c) for c in literal)
            or not isinstance(expansion, str) or not expansion
            or TITLO in expansion or not all(word_char(c) for c in expansion)):
        raise ValueError("abbreviation must be a lexical titlo token with an expanded word")
    old, new = _letters(literal), _letters(expansion)
    if (not unicodedata.category(literal[0]).startswith("L")
            or not unicodedata.category(expansion[0]).startswith("L")
            or any(not unicodedata.name(c, "").startswith("CYRILLIC")
                   for c in old + new)):
        raise ValueError("abbreviation pilot requires Cyrillic words without leading combining marks")
    if len(old) < 2 or len(new) <= len(old):
        raise ValueError("single-letter/numeric or non-expanding abbreviation")
    # Supplied letters may be inserted, never substituted for visible letters.
    it = iter(new)
    if not all(any(c == visible for c in it) for visible in old):
        raise ValueError("expansion changes visible letters")
    if text is not None:
        if (type(start) is not int or type(end) is not int
                or not 0 <= start < end <= len(text) or text[start:end] != literal):
            raise ValueError("abbreviation literal is stale")
        if ((start and word_char(text[start-1]))
                or (end < len(text) and word_char(text[end]))):
            raise ValueError("abbreviation must cover an entire token")
        if (all(c.casefold() in CYRILLIC_NUMERALS for c in old)
                and end < len(text) and text[end] in ".-"):
            raise ValueError("ambiguous Cyrillic numeral; defer lexical expansion")


def validate_abbreviation_spans(line, reader_id):
    """Return checked spans on the exact frozen line and one language interval."""
    spans = line.get("abbreviation_spans", [])
    if not isinstance(spans, list):
        raise ValueError("abbreviation_spans must be a list")
    if not spans:
        return spans
    text = line["text"]
    language = line.get("language_spans")
    if not isinstance(language, list):
        raise ValueError("abbreviation requires language attribution")
    prev = 0
    for span in spans:
        if not isinstance(span, dict) or set(span) != {
                "text_version", "start", "end", "literal", "expansion",
                "uncertain", "source"}:
            raise ValueError("invalid abbreviation span fields")
        a, b = span["start"], span["end"]
        if (span["text_version"] != reader_id or type(a) is not int
                or type(b) is not int or not prev <= a < b <= len(text)):
            raise ValueError("stale, overlapping or out-of-range abbreviation span")
        if (unicodedata.category(text[a]).startswith("M")
                or (b < len(text) and unicodedata.category(text[b]).startswith("M"))):
            raise ValueError("abbreviation boundary splits a combining sequence")
        if type(span["uncertain"]) is not bool:
            raise ValueError("abbreviation uncertainty must be explicit")
        _source(span["source"])
        validate_pair(span["literal"], span["expansion"], text, a, b)
        if len([s for s in language if s["start"] <= a < b <= s["end"]]) != 1:
            raise ValueError("abbreviation must fit within one language span")
        if line.get("unreadable_suffix") and b > len(text)-1:
            raise ValueError("abbreviation cannot include an editorial gap")
        prev = b
    return spans


def read_choice(choice):
    """Fail closed for all but the supported abbr/expan alternative."""
    if (choice.tag != tag("choice") or len(choice) != 2 or choice.text
            or choice[0].tag != tag("abbr") or choice[1].tag != tag("expan")):
        raise ValueError("unsupported abbreviation choice")
    abbr, expan = choice
    if (len(abbr) or len(expan) or abbr.tail or expan.tail
            or not abbr.text or not expan.text
            or expan.get("cert") not in {"low", "high"}):
        raise ValueError("invalid abbreviation choice content")
    source = expan.get("source")
    _source(source)
    validate_pair(abbr.text, expan.text)
    return abbr.text, expan.text, expan.get("cert") == "low", source


def diplomatic_text(element):
    """Retain the literal branch and all surrounding text/tails."""
    if element.tag == tag("choice"):
        return read_choice(element)[0]
    return (element.text or "") + "".join(
        diplomatic_text(child) + (child.tail or "") for child in element)


def insert_choices(seg, spans, base, prefix):
    """Decorate only original text chunks, leaving disjoint structural markup.

    A source-note ref or heading continuation must not be split by an
    abbreviation. Refuse rather than lose either annotation.
    """
    if not spans:
        return
    original = diplomatic_text(seg)
    chunks = [(seg, "text", base, base+len(seg.text or ""))]
    offset = chunks[0][3]
    for child in list(seg):
        offset += len(diplomatic_text(child))
        end = offset + len(child.tail or "")
        chunks.append((child, "tail", offset, end))
        offset = end
    buckets = [[] for _ in chunks]
    for span in spans:
        a, b = span["start"], span["end"]
        matches = [i for i, (_, _, start, end) in enumerate(chunks)
                   if start <= a < b <= end]
        if len(matches) != 1:
            raise ValueError("abbreviation overlaps structural inline markup")
        buckets[matches[0]].append(span)
    for (owner, attr, start, end), choices in zip(chunks, buckets):
        if not choices:
            continue
        printed = getattr(owner, attr) or ""
        setattr(owner, attr, printed[:choices[0]["start"]-start])
        pos = 0 if owner is seg else list(seg).index(owner)+1
        for i, span in enumerate(choices):
            a, b = span["start"], span["end"]
            choice = ET.Element(tag("choice"), {ID: f"{prefix}-{a:05d}"})
            ET.SubElement(choice, tag("abbr")).text = span["literal"]
            ET.SubElement(choice, tag("expan"), {
                "cert": "low" if span["uncertain"] else "high",
                "source": span["source"],
            }).text = span["expansion"]
            next_a = choices[i+1]["start"] if i+1 < len(choices) else end
            choice.tail = printed[b-start:next_a-start]
            seg.insert(pos, choice)
            pos += 1
    if diplomatic_text(seg) != original:
        raise ValueError("abbreviation rendering changed diplomatic text")
