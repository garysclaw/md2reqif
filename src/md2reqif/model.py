"""Internal data model for requirements documents."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Attribute:
    name: str
    value: str


@dataclass
class Requirement:
    id: str
    title: str
    description: str = ""
    attributes: list[Attribute] = field(default_factory=list)

    def get(self, name: str, default: str = "") -> str:
        for a in self.attributes:
            if a.name.lower() == name.lower():
                return a.value
        return default


@dataclass
class Section:
    title: str
    level: int
    requirements: list[Requirement] = field(default_factory=list)


@dataclass
class Document:
    title: str
    module: str = ""
    version: str = "1.0"
    author: str = ""
    date: str = ""
    sections: list[Section] = field(default_factory=list)
