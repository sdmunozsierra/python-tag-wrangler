"""Tag operations: rename, merge, delete, bulk update."""

from __future__ import annotations

from pathlib import Path

from tag_wrangler.models import Note
from tag_wrangler.parser import write_frontmatter


def rename_tag(
    notes: list[Note], vault_root: Path, old_tag: str, new_tag: str
) -> int:
    """Rename a tag across all notes. Returns count of modified notes."""
    old_tag = old_tag.lower().strip()
    new_tag = new_tag.lower().strip()
    modified = 0
    for note in notes:
        if old_tag in note.tags:
            _replace_tag_in_note(note, vault_root, old_tag, new_tag)
            modified += 1
    return modified


def merge_tags(
    notes: list[Note],
    vault_root: Path,
    source_tags: list[str],
    target_tag: str,
) -> int:
    """Merge multiple source tags into a single target tag."""
    source_set = {t.lower().strip() for t in source_tags}
    target_tag = target_tag.lower().strip()
    modified = 0
    for note in notes:
        overlap = source_set & set(note.tags)
        if overlap:
            for old in overlap:
                _replace_tag_in_note(note, vault_root, old, target_tag)
            modified += 1
    return modified


def delete_tag(notes: list[Note], vault_root: Path, tag: str) -> int:
    """Remove a tag from all notes."""
    tag = tag.lower().strip()
    modified = 0
    for note in notes:
        if tag in note.tags:
            _remove_tag_from_note(note, vault_root, tag)
            modified += 1
    return modified


def add_tag_to_notes(
    notes: list[Note], vault_root: Path, tag: str, target_notes: list[Note]
) -> int:
    """Add a tag to a specific set of notes."""
    tag = tag.lower().strip()
    modified = 0
    for note in target_notes:
        if tag not in note.tags:
            _add_tag_to_note(note, vault_root, tag)
            modified += 1
    return modified


def _replace_tag_in_note(
    note: Note, vault_root: Path, old_tag: str, new_tag: str
) -> None:
    """Replace a tag in the note's frontmatter."""
    fm = dict(note.frontmatter)
    tags = _get_fm_tags(fm)
    updated = []
    seen = set()
    for t in tags:
        replacement = new_tag if t.lower() == old_tag else t.lower()
        if replacement not in seen:
            updated.append(replacement)
            seen.add(replacement)
    fm["tags"] = updated
    # Clean up legacy key
    fm.pop("tag", None)
    write_frontmatter(note, vault_root, fm)
    note.frontmatter = fm
    note.tags = sorted(set(updated))


def _remove_tag_from_note(note: Note, vault_root: Path, tag: str) -> None:
    """Remove a tag from the note's frontmatter."""
    fm = dict(note.frontmatter)
    tags = _get_fm_tags(fm)
    updated = [t for t in tags if t.lower() != tag]
    fm["tags"] = updated
    fm.pop("tag", None)
    write_frontmatter(note, vault_root, fm)
    note.frontmatter = fm
    note.tags = sorted(set(updated))


def _add_tag_to_note(note: Note, vault_root: Path, tag: str) -> None:
    """Add a tag to the note's frontmatter."""
    fm = dict(note.frontmatter)
    tags = _get_fm_tags(fm)
    if tag not in [t.lower() for t in tags]:
        tags.append(tag)
    fm["tags"] = tags
    fm.pop("tag", None)
    write_frontmatter(note, vault_root, fm)
    note.frontmatter = fm
    note.tags = sorted(set(tags))


def _get_fm_tags(fm: dict) -> list[str]:
    """Extract tag list from frontmatter, handling various formats."""
    tags = fm.get("tags") or fm.get("tag") or []
    if isinstance(tags, str):
        import re
        tags = [t.strip() for t in re.split(r"[,\s]+", tags) if t.strip()]
    return list(tags)
