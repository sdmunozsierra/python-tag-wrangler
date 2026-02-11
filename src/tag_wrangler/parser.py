"""Parse Obsidian markdown files and extract frontmatter / tags."""

from __future__ import annotations

import re
from pathlib import Path

import frontmatter

from tag_wrangler.models import Note


# Matches inline #tags (but not headings or anchors)
INLINE_TAG_RE = re.compile(
    r"(?:^|(?<=\s))#([A-Za-z][A-Za-z0-9_/\-]*)", re.MULTILINE
)


def parse_note(path: Path, vault_root: Path) -> Note:
    """Parse a single markdown file into a Note."""
    text = path.read_text(encoding="utf-8", errors="replace")
    post = frontmatter.loads(text)

    fm = dict(post.metadata) if post.metadata else {}
    body = post.content

    # Collect tags from frontmatter
    fm_tags = _extract_frontmatter_tags(fm)

    # Collect inline tags from body
    inline_tags = INLINE_TAG_RE.findall(body)

    # Normalise: lowercase, strip leading #, deduplicate, sort
    all_tags = sorted(set(_normalise(t) for t in fm_tags + inline_tags))

    rel = path.relative_to(vault_root)
    title = fm.get("title", path.stem)

    return Note(
        path=rel,
        title=title,
        frontmatter=fm,
        tags=all_tags,
        body=body,
    )


def _extract_frontmatter_tags(fm: dict) -> list[str]:
    """Pull tags from common frontmatter keys."""
    raw: list[str] = []
    for key in ("tags", "tag"):
        val = fm.get(key)
        if val is None:
            continue
        if isinstance(val, list):
            raw.extend(str(v) for v in val)
        elif isinstance(val, str):
            # Comma- or space-separated string
            raw.extend(re.split(r"[,\s]+", val))
    return [t.strip() for t in raw if t.strip()]


def _normalise(tag: str) -> str:
    """Lowercase and strip leading # from a tag."""
    return tag.lstrip("#").lower().strip()


def write_frontmatter(
    note: Note, vault_root: Path, new_frontmatter: dict
) -> None:
    """Write updated frontmatter back to disk (preserves body)."""
    full_path = vault_root / note.path
    text = full_path.read_text(encoding="utf-8", errors="replace")
    post = frontmatter.loads(text)
    post.metadata = new_frontmatter
    full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
