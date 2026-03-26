from md2reqif.md_parser import parse as md_parse
from md2reqif.reqif_writer import write as reqif_write
from md2reqif.reqif_reader import read as reqif_read
from md2reqif.md_writer import write as md_write


def test_round_trip_req_count(simple_md):
    doc1 = md_parse(simple_md)
    xml = reqif_write(doc1)
    doc2 = reqif_read(xml)
    c1 = len([r for s in doc1.sections for r in s.requirements])
    c2 = len([r for s in doc2.sections for r in s.requirements])
    assert c1 == c2


def test_round_trip_req_ids(simple_md):
    doc1 = md_parse(simple_md)
    xml = reqif_write(doc1)
    doc2 = reqif_read(xml)
    ids1 = {r.id for s in doc1.sections for r in s.requirements}
    ids2 = {r.id for s in doc2.sections for r in s.requirements}
    assert ids1 == ids2


def test_md_output_contains_ids(simple_md):
    doc = md_parse(simple_md)
    xml = reqif_write(doc)
    doc2 = reqif_read(xml)
    md_out = md_write(doc2)
    assert "REQ-BRAKE-001" in md_out
    assert "REQ-BRAKE-002" in md_out
    assert "REQ-BRAKE-003" in md_out
