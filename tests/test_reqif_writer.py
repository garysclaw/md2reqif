from xml.etree import ElementTree as ET
from md2reqif.md_parser import parse
from md2reqif.reqif_writer import write


def test_produces_valid_xml(simple_md):
    doc = parse(simple_md)
    result = write(doc)
    root = ET.fromstring(result)
    assert root is not None


def test_has_spec_objects(simple_md):
    doc = parse(simple_md)
    result = write(doc)
    root = ET.fromstring(result)
    all_tags = [el.tag for el in root.iter()]
    spec_obj_tags = [t for t in all_tags if "SPEC-OBJECT" in t and "TYPE" not in t and "REF" not in t]
    assert len(spec_obj_tags) == 3


def test_req_identifiers_in_output(simple_md):
    doc = parse(simple_md)
    result = write(doc)
    assert "REQ-BRAKE-001" in result
    assert "REQ-BRAKE-002" in result
    assert "REQ-BRAKE-003" in result


def test_req_description_in_output(simple_md):
    doc = parse(simple_md)
    result = write(doc)
    assert "100ms" in result


def test_has_datatypes(simple_md):
    doc = parse(simple_md)
    result = write(doc)
    assert "DATATYPES" in result
    assert "DATATYPE-DEFINITION-STRING" in result
