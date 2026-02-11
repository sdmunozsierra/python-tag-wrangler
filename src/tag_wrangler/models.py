"""Data models for notes and tags."""

from __future__ import annotations

import dataclasses
from pathlib import Path


@dataclasses.dataclass
class Note:
    """Represents a single Obsidian markdown note."""

    path: Path
    title: str
    frontmatter: dict
    tags: list[str]
    body: str

    @property
    def relative_path(self) -> str:
        return str(self.path)

    def get_frontmatter_value(self, key: str):
        return self.frontmatter.get(key)


@dataclasses.dataclass
class TagInfo:
    """Aggregated information about a single tag across the vault."""

    name: str
    count: int
    notes: list[Path]

    @property
    def parts(self) -> list[str]:
        """Split nested tag into parts (e.g. 'project/work' -> ['project', 'work'])."""
        return self.name.strip("#").split("/")

    @property
    def is_nested(self) -> bool:
        return "/" in self.name

    @property
    def root(self) -> str:
        """Return the top-level tag (e.g. 'project' from 'project/work')."""
        return self.parts[0]
