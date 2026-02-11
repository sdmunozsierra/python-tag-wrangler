"""Vault scanning and loading."""

from __future__ import annotations

from pathlib import Path

from tag_wrangler.models import Note, TagInfo
from tag_wrangler.parser import parse_note


def scan_vault(vault_path: Path) -> list[Note]:
    """Recursively scan a vault directory and parse all markdown files."""
    vault_path = vault_path.resolve()
    notes: list[Note] = []
    for md in sorted(vault_path.rglob("*.md")):
        # Skip hidden directories (like .obsidian, .trash)
        parts = md.relative_to(vault_path).parts
        if any(p.startswith(".") for p in parts):
            continue
        try:
            notes.append(parse_note(md, vault_path))
        except Exception:
            # Skip files that can't be parsed
            continue
    return notes


def build_tag_index(notes: list[Note]) -> dict[str, TagInfo]:
    """Build an index of tag -> TagInfo from parsed notes."""
    index: dict[str, TagInfo] = {}
    for note in notes:
        for tag in note.tags:
            if tag not in index:
                index[tag] = TagInfo(name=tag, count=0, notes=[])
            index[tag].count += 1
            index[tag].notes.append(note.path)
    return index
