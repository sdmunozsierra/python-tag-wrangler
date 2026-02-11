"""Tag analysis: similarity detection, statistics, clustering."""

from __future__ import annotations

from collections import Counter

from rapidfuzz import fuzz

from tag_wrangler.models import Note, TagInfo


def find_similar_tags(
    tag_index: dict[str, TagInfo], threshold: int = 80
) -> list[tuple[str, str, int]]:
    """Find pairs of tags that look similar (possible duplicates).

    Returns list of (tag_a, tag_b, similarity_score) sorted by score descending.
    """
    tag_names = sorted(tag_index.keys())
    pairs: list[tuple[str, str, int]] = []
    for i, a in enumerate(tag_names):
        for b in tag_names[i + 1 :]:
            score = fuzz.ratio(a, b)
            if score >= threshold:
                pairs.append((a, b, score))
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs


def tag_frequency(notes: list[Note]) -> Counter:
    """Return tag -> usage count."""
    counter: Counter = Counter()
    for note in notes:
        counter.update(note.tags)
    return counter


def tag_co_occurrence(notes: list[Note], min_count: int = 2) -> dict[tuple[str, str], int]:
    """Find tags that frequently appear together."""
    co: Counter = Counter()
    for note in notes:
        tags = sorted(note.tags)
        for i, a in enumerate(tags):
            for b in tags[i + 1 :]:
                co[(a, b)] += 1
    return {pair: count for pair, count in co.items() if count >= min_count}


def orphan_tags(tag_index: dict[str, TagInfo], threshold: int = 1) -> list[TagInfo]:
    """Tags used in very few notes (potential cleanup candidates)."""
    return sorted(
        [t for t in tag_index.values() if t.count <= threshold],
        key=lambda t: t.name,
    )


def tag_hierarchy(tag_index: dict[str, TagInfo]) -> dict[str, list[str]]:
    """Build a tree of nested tags (e.g. project/work -> {project: [work]})."""
    tree: dict[str, list[str]] = {}
    for tag_name in sorted(tag_index.keys()):
        parts = tag_name.split("/")
        if len(parts) > 1:
            root = parts[0]
            child = "/".join(parts[1:])
            tree.setdefault(root, []).append(child)
    return tree


def vault_stats(notes: list[Note], tag_index: dict[str, TagInfo]) -> dict:
    """Compute summary statistics for the vault."""
    total_notes = len(notes)
    total_tags = len(tag_index)
    notes_with_tags = sum(1 for n in notes if n.tags)
    notes_without_tags = total_notes - notes_with_tags
    avg_tags = (
        sum(len(n.tags) for n in notes) / total_notes if total_notes else 0
    )
    most_common = tag_frequency(notes).most_common(10)
    orphans = orphan_tags(tag_index)

    return {
        "total_notes": total_notes,
        "total_unique_tags": total_tags,
        "notes_with_tags": notes_with_tags,
        "notes_without_tags": notes_without_tags,
        "avg_tags_per_note": round(avg_tags, 1),
        "top_tags": most_common,
        "orphan_count": len(orphans),
    }
