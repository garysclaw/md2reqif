from md2reqif.md_parser import parse


def test_parses_title(simple_md):
    doc = parse(simple_md)
    assert doc.title == "Braking System Requirements"


def test_parses_sections(simple_md):
    doc = parse(simple_md)
    assert len(doc.sections) >= 2
    titles = [s.title for s in doc.sections]
    assert "Functional Requirements" in titles


def test_parses_requirement_count(simple_md):
    doc = parse(simple_md)
    all_reqs = [r for s in doc.sections for r in s.requirements]
    assert len(all_reqs) == 3


def test_requirement_ids(simple_md):
    doc = parse(simple_md)
    ids = {r.id for s in doc.sections for r in s.requirements}
    assert "REQ-BRAKE-001" in ids
    assert "REQ-BRAKE-002" in ids
    assert "REQ-BRAKE-003" in ids


def test_requirement_attributes(simple_md):
    doc = parse(simple_md)
    req = next(r for s in doc.sections for r in s.requirements if r.id == "REQ-BRAKE-001")
    assert req.get("Status") == "Draft"
    assert req.get("Priority") == "High"
    assert req.get("Type") == "Functional"


def test_requirement_description(simple_md):
    doc = parse(simple_md)
    req = next(r for s in doc.sections for r in s.requirements if r.id == "REQ-BRAKE-001")
    assert "100ms" in req.description


def test_front_matter(simple_md):
    doc = parse(simple_md)
    assert doc.module == "Safety Requirements"
    assert doc.author == "ACME Systems"


def test_no_front_matter():
    md = "# My Reqs\n\n## Section\n\n### REQ-001: Do something\n\nDescription here.\n"
    doc = parse(md)
    assert doc.title == "My Reqs"
    reqs = [r for s in doc.sections for r in s.requirements]
    assert len(reqs) == 1
    assert reqs[0].description == "Description here."
