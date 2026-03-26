"""Export Document model back to Markdown."""
from __future__ import annotations
from md2reqif.model import Document


def write(doc: Document) -> str:
    lines: list[str] = []

    if any([doc.module, doc.author, doc.date, doc.version not in ("", "1.0")]):
        lines += ["---"]
        if doc.module:
            lines.append(f"module: {doc.module}")
        if doc.version:
            lines.append(f"version: {doc.version}")
        if doc.author:
            lines.append(f"author: {doc.author}")
        if doc.date:
            lines.append(f"date: {doc.date}")
        lines += ["---", ""]

    if doc.title:
        lines += [f"# {doc.title}", ""]

    for section in doc.sections:
        lines += [f"## {section.title}", ""]
        for req in section.requirements:
            lines.append(f"### {req.id}: {req.title}")
            for attr in req.attributes:
                lines.append(f"- {attr.name}: {attr.value}")
            lines.append("")
            if req.description:
                lines += [req.description, ""]

    return "\n".join(lines)
