"""Parse ReqIF XML back into Document model."""
from __future__ import annotations
import re
from xml.etree import ElementTree as ET
from md2reqif.model import Document, Section, Requirement, Attribute

XHTML_NS = "http://www.w3.org/1999/xhtml"


def _tag(el: ET.Element) -> str:
    return re.sub(r'\{[^}]+\}', '', el.tag)


def read(text: str) -> Document:
    root = ET.fromstring(text)

    title = ""
    for el in root.iter():
        if _tag(el) == "TITLE":
            title = el.text or ""
            break

    doc = Document(title=title)

    attr_defs: dict[str, str] = {}
    for el in root.iter():
        if _tag(el) in ("ATTRIBUTE-DEFINITION-STRING", "ATTRIBUTE-DEFINITION-XHTML"):
            ident = el.get("IDENTIFIER", "")
            name = el.get("LONG-NAME", "")
            if ident:
                attr_defs[ident] = name

    obj_map: dict[str, tuple[str, str, list[Attribute]]] = {}
    for el in root.iter():
        if _tag(el) != "SPEC-OBJECT":
            continue
        obj_id = el.get("IDENTIFIER", "")
        long_name = el.get("LONG-NAME", "")
        description = ""
        attrs: list[Attribute] = []

        for val in el.iter():
            vtag = _tag(val)
            if vtag == "ATTRIBUTE-VALUE-XHTML":
                for p in val.iter(f"{{{XHTML_NS}}}p"):
                    if p.text:
                        description = (description + "\n" + p.text).strip()
                for p in val.iter("p"):
                    if p.text:
                        description = (description + "\n" + p.text).strip()
            elif vtag == "ATTRIBUTE-VALUE-STRING":
                val_text = val.get("THE-VALUE", "")
                for ref in val.iter():
                    if _tag(ref) == "ATTRIBUTE-DEFINITION-STRING-REF":
                        attr_name = attr_defs.get(ref.text or "", "")
                        if attr_name and attr_name.lower() != "reqif.text":
                            attrs.append(Attribute(attr_name, val_text))
                        break

        obj_map[obj_id] = (long_name, description, attrs)

    default_section = Section(title="Requirements", level=2)
    doc.sections.append(default_section)
    req_counter = 0

    def _walk(parent: ET.Element, section: Section) -> None:
        nonlocal req_counter
        for child in parent:
            if _tag(child) != "SPEC-HIERARCHY":
                continue
            obj_ref = None
            sub_children = None
            for sub in child:
                st = _tag(sub)
                if st == "OBJECT":
                    for ref in sub:
                        if _tag(ref) == "SPEC-OBJECT-REF":
                            obj_ref = ref.text
                elif st == "CHILDREN":
                    sub_children = sub
            if obj_ref and obj_ref in obj_map:
                req_counter += 1
                long_name, desc, attrs = obj_map[obj_ref]
                req_id = long_name or f"REQ-{req_counter:03d}"
                lines = desc.split("\n", 1)
                req_title = lines[0].strip() if lines else req_id
                req_desc = lines[1].strip() if len(lines) > 1 else ""
                section.requirements.append(Requirement(id=req_id, title=req_title, description=req_desc, attributes=attrs))
            if sub_children is not None:
                _walk(sub_children, section)

    for spec in root.iter():
        if _tag(spec) != "SPECIFICATION":
            continue
        for sub in spec:
            if _tag(sub) == "CHILDREN":
                _walk(sub, default_section)
                break

    return doc
