# Tag Wrangler

Streamlit application to manage, organise, and standardise tags in your Obsidian vault frontmatter.

## Features

- **Dashboard** - Vault overview with tag frequency charts, distribution histograms, orphan tag detection, and co-occurrence analysis
- **Tag Explorer** - Browse all tags with search/filter, view nested tag hierarchy, inspect which notes use each tag
- **Standardiser** - Fuzzy-match similar tags to find duplicates, rename individual tags, merge multiple tags, apply batch rename rules
- **Bulk Operations** - Add/remove/replace tags across filtered sets of notes (by tag, folder, or untagged)
- **Note Browser** - Browse notes, inspect frontmatter, preview content, and edit frontmatter YAML directly

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

## Quick start

```bash
# Install dependencies
uv sync

# Run the app
uv run streamlit run src/tag_wrangler/app/main.py

# Or use the entry point
uv run tag-wrangler
```

A sample vault is included in `sample_vault/` for testing.

## Project structure

```
src/tag_wrangler/
  models.py        # Note and TagInfo data models
  parser.py        # Markdown/frontmatter parsing
  vault.py         # Vault scanning and tag indexing
  operations.py    # Tag rename, merge, delete, bulk add
  analyzer.py      # Similarity detection, stats, co-occurrence
  app/
    main.py        # Streamlit entry point and sidebar
    state.py       # Session state management
    pages/
      1_Dashboard.py
      2_Tag_Explorer.py
      3_Standardiser.py
      4_Bulk_Operations.py
      5_Note_Browser.py
```

## Future plans

- LLM integration to read note content and suggest appropriate tags from an approved tag list
- Tag governance: define an approved tag taxonomy and flag violations
- Export/import tag mappings
- Undo/redo support for bulk operations
