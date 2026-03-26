"""Parse structured Markdown into Document model."""
from __future__ import annotations
import re
import yaml
from md2reqif.model import Document, Section, Requirement, Attribute

_HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$')
_REQ_ID_RE = re.compile(r'^(REQ-[\w-]+|[\w]+-\d+):\s*(.+)$')
_LIST_ITEM_RE = re.compile(r'^[-*]\s+(.+)$')
_KV_RE = re.compile(r'^([^:]+):\s*(.+)$')


def _auto_id(section_title: str, counter: int) -> str:
    slug = re.sub(r'[^A-Za-z0-9]', '', section_title.upper().replace(' ', ''))[:4]
    return f"{slug}-{counter:03d}" if slug else f"REQ-{counter:03d}"


def parse(text: str) -> Document:
    lines = text.splitlines()
    idx = 0

    front: dict = {}
    if lines and lines[0].strip() == '---':
        end = next((i for i, ln in enumerate(lines[1:], 1) if ln.strip() == '---'), None)
        if end:
            try:
                front = yaml.safe_load('\n'.join(lines[1:end])) or {}
            except Exception:
                pass
            idx = end + 1

    doc = Document(
        title=str(front.get('title', '')),
        module=str(front.get('module', '')),
        version=str(front.get('version', '1.0')),
        author=str(front.get('author', '')),
        date=str(front.get('date', '')),
    )

    current_section: Section | None = None
    req_counter = 0
    i = idx

    while i < len(lines):
        line = lines[i]
        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            heading = m.group(2).strip()

            if level == 1 and not doc.title:
                doc.title = heading
                i += 1
                continue

            rid_m = _REQ_ID_RE.match(heading)
            if rid_m or level >= 3:
                req_counter += 1
                if rid_m:
                    req_id = rid_m.group(1)
                    req_title = rid_m.group(2).strip()
                else:
                    req_id = _auto_id(current_section.title if current_section else '', req_counter)
                    req_title = heading

                i += 1
                attrs: list[Attribute] = []
                while i < len(lines) and _LIST_ITEM_RE.match(lines[i]):
                    item = _LIST_ITEM_RE.match(lines[i]).group(1)
                    kv = _KV_RE.match(item)
                    if kv:
                        attrs.append(Attribute(kv.group(1).strip(), kv.group(2).strip()))
                    i += 1

                desc_lines: list[str] = []
                while i < len(lines) and not _HEADING_RE.match(lines[i]):
                    desc_lines.append(lines[i])
                    i += 1
                description = '\n'.join(desc_lines).strip()

                req = Requirement(id=req_id, title=req_title, description=description, attributes=attrs)
                if current_section is None:
                    default_sec = Section(title='Requirements', level=2)
                    doc.sections.append(default_sec)
                    current_section = default_sec
                current_section.requirements.append(req)
                continue
            else:
                section = Section(title=heading, level=level)
                doc.sections.append(section)
                current_section = section
                i += 1
                continue
        i += 1

    if not doc.title:
        doc.title = doc.module or 'Requirements Document'

    return doc
