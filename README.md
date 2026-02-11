# Tag Wrangler

Streamlit application to manage, organise, and standardise tags in your Obsidian vault frontmatter.

If your vault has hundreds of tags that have grown organically into an inconsistent mess, Tag Wrangler helps you understand what you have, find duplicates, and clean everything up in bulk.

## Features

| Page | What it does |
|---|---|
| **Dashboard** | Vault-wide stats, tag frequency charts, distribution histograms, orphan tag detection, co-occurrence analysis |
| **Tag Explorer** | Browse all tags with search/filter, sort by name or count, view nested tag hierarchy, inspect which notes use each tag |
| **Standardiser** | Fuzzy-match similar tags to find duplicates, rename individual tags, merge multiple tags into one, apply batch rename rules |
| **Bulk Operations** | Add/remove/replace tags across filtered sets of notes (by tag, folder, or untagged) |
| **Note Browser** | Browse notes, inspect frontmatter, preview content, and edit frontmatter YAML directly |

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- (Optional) [just](https://github.com/casey/just) command runner

## Quick start

```bash
# Install dependencies
uv sync

# Run the app
uv run streamlit run src/tag_wrangler/app/main.py

# --- or with just ---
just setup
just run
```

A sample vault is included in `sample_vault/` for testing. After the app opens, paste `sample_vault` into the **Vault path** field in the sidebar and click **Load vault**.

## Just recipes

Run `just` to see all available commands:

```
just setup           # Install dependencies
just run             # Start the Streamlit app
just demo            # Start the app (reminder to load sample_vault)
just run-port 9000   # Run on a custom port
just lint            # Run ruff linter
just lint-fix        # Lint + auto-fix
just fmt             # Format code with ruff
just check           # Lint + format check + tests
just test            # Run pytest
just smoke-test      # Quick CLI scan of the sample vault
just clean           # Remove generated files
just deps            # Show dependency tree
just add <pkg>       # Add a runtime dependency
just add-dev <pkg>   # Add a dev dependency
just lock            # Rebuild the lock file
```

---

## Usage guide

### Loading your vault

1. Start the app (`just run` or `uv run streamlit run src/tag_wrangler/app/main.py`).
2. In the **sidebar**, enter the absolute path to your Obsidian vault (e.g. `/home/user/my-vault` or `~/Documents/Obsidian/MyVault`).
3. Click **Load vault**. The app recursively scans all `.md` files, skipping hidden directories like `.obsidian` and `.trash`.
4. The sidebar shows the total note and tag counts. Navigate to any page using the left navigation.

Tags are collected from two sources:
- **Frontmatter** `tags:` or `tag:` fields (YAML lists or comma/space-separated strings)
- **Inline** `#tags` in the note body

All tags are normalised to lowercase.

### Dashboard

The Dashboard gives you an at-a-glance overview:

- **Metrics row** - Total notes, unique tags, notes with/without tags, average tags per note.
- **Tag frequency chart** - Horizontal bar chart of the 30 most-used tags.
- **Tag distribution histogram** - How many notes have 0 tags, 1 tag, 2 tags, etc.
- **Rare tags table** - Tags that appear in only 1 note (cleanup candidates).
- **Co-occurrence table** - Tag pairs that frequently appear together (helps spot redundancy).

### Tag Explorer

Use this page to understand what tags exist and how they're used:

- **Search** - Type any substring to filter the tag list in real time.
- **Sort** - Toggle between count (ascending/descending) and alphabetical.
- **Tag detail** - Select any tag from the dropdown to see the full list of notes that use it.
- **Hierarchy view** - Nested tags (e.g. `project/web`, `project/mobile`) are grouped under their root in collapsible sections.

### Standardiser

This is the primary cleanup tool. Use it when your vault has duplicate or inconsistent tags.

#### Finding duplicates

1. Navigate to the **Standardiser** page.
2. The **Similar tags** section automatically runs fuzzy matching on every tag pair.
3. Adjust the **Similarity threshold** slider (default 80%). Lower values surface more candidates; higher values are stricter.
4. The results table shows Tag A, Tag B, and a similarity percentage. For example:
   - `javascript` / `js` at 50% (won't show at default threshold)
   - `code-review` / `review` at 70%
   - `project` / `project/web` at 78%

#### Renaming a single tag

1. Under **Rename a tag**, select the tag to rename from the dropdown.
2. Type the new name in the text field.
3. Click **Rename**. Every note that had the old tag will be updated in its frontmatter on disk.
4. The vault reloads automatically so you see the new state immediately.

Example: rename `js` to `javascript` to consolidate all JavaScript-related notes under one tag.

#### Merging multiple tags

1. Under **Merge tags**, use the multi-select to pick all the source tags you want to consolidate (e.g. `js`, `javascript`, `ecmascript`).
2. Type the target tag name (e.g. `javascript`).
3. Click **Merge**. All source tags are replaced by the target in every affected note.

This is the fastest way to collapse a cluster of synonyms into a single canonical tag.

#### Batch rename rules

For large-scale cleanup, define many renames at once:

1. Under **Batch rename rules**, enter one rule per line in the format `old_tag -> new_tag`:
   ```
   js -> javascript
   py -> python
   ml -> machine-learning
   devops -> dev-ops
   react-native -> react/native
   ```
2. Click **Apply rules**. Each rule is processed in order. The app reports how many notes were modified total.

Tips:
- Rules that reference a tag not present in the vault are silently skipped (no error).
- If a rule is malformed (no `->` separator), it shows a warning but continues processing the rest.
- You can paste the same rule set repeatedly - it's idempotent once applied.

### Bulk Operations

Use this page when you need to add, remove, or replace a tag across many notes at once.

#### Step 1: Filter which notes to target

Choose a filter mode at the top:

| Filter | What it selects |
|---|---|
| **All notes** | Every note in the vault |
| **Notes with specific tag** | Only notes that already have a particular tag |
| **Notes in folder** | Only notes within a specific vault subfolder |
| **Untagged notes** | Notes with no tags at all |

After selecting a filter, the page shows how many notes matched. Expand **Preview selected notes** to verify the selection before applying any operation.

#### Step 2: Choose and apply an operation

| Operation | Use case | How it works |
|---|---|---|
| **Add tag** | Tag a batch of notes at once | Type any tag name and click **Add to selected notes**. Notes that already have the tag are skipped. |
| **Remove tag** | Clean up an unwanted tag | Select the tag from the dropdown and click **Remove from all notes**. The tag is deleted from every note's frontmatter. |
| **Find & replace tag** | Rename a tag within the filtered set | Select the tag to find, type the replacement, and click **Replace**. Works like Standardiser rename but scoped to your filtered notes. |

#### Example workflows

**Tag all untagged notes:**
1. Filter by "Untagged notes"
2. Operation: "Add tag"
3. Tag: `needs-review`
4. Click **Add to selected notes**

**Remove a deprecated tag from a specific folder:**
1. Filter by "Notes in folder" and select `projects/`
2. Operation: "Remove tag"
3. Select `deprecated-tag` and click **Remove from all notes**

**Rename a tag only in daily notes:**
1. Filter by "Notes in folder" and select `daily/`
2. Operation: "Find & replace tag"
3. Find `standup`, Replace with `meeting/standup`
4. Click **Replace**

### Note Browser

Browse individual notes, inspect their frontmatter, and make direct edits:

1. Use the **search bar** to filter by title or path, or the **tag dropdown** to filter by a specific tag.
2. Select a note from the dropdown to see its detail view:
   - **Tags** listed as code badges
   - **Frontmatter** displayed as formatted YAML
   - **Body preview** (first 2000 characters)
3. To edit frontmatter, modify the YAML in the **Edit frontmatter** text area and click **Save frontmatter**. Changes are written directly to the file on disk.
4. The **All notes** table at the bottom gives a sortable overview of every matched note.

---

## Project structure

```
src/tag_wrangler/
  __init__.py
  models.py        # Note and TagInfo data models
  parser.py        # Markdown/frontmatter parsing, inline #tag extraction
  vault.py         # Vault scanning and tag indexing
  operations.py    # Tag rename, merge, delete, bulk add
  analyzer.py      # Similarity detection, stats, co-occurrence, hierarchy
  app/
    __init__.py
    main.py        # Streamlit entry point, sidebar, home page
    state.py       # Session state management (load/reload vault)
    pages/
      1_Dashboard.py
      2_Tag_Explorer.py
      3_Standardiser.py
      4_Bulk_Operations.py
      5_Note_Browser.py
```

## How it works

- **Frontmatter parsing** uses the `python-frontmatter` library to extract YAML metadata from `---` fenced blocks.
- **Inline tags** are detected with a regex that matches `#TagName` (alphanumeric, hyphens, underscores, slashes) while ignoring headings.
- **Fuzzy matching** uses `rapidfuzz` (C-backed, fast) to compute Levenshtein similarity between all tag pairs.
- **Write-back** serialises updated frontmatter with `python-frontmatter` and overwrites the original file, preserving the note body.
- All operations modify the `tags` frontmatter key. If a note uses the legacy `tag` key it's migrated to `tags` on first write.

## Important notes

- **Back up your vault** before running bulk operations. Changes are written directly to disk and there is no undo (yet).
- The app does **not** modify inline `#tags` in the note body - only frontmatter `tags:` fields.
- Hidden directories (`.obsidian`, `.trash`, etc.) are automatically skipped during scanning.

## Future plans

- LLM integration to read note content and suggest appropriate tags from an approved tag list
- Tag governance: define an approved tag taxonomy and flag violations
- Export/import tag mappings and rename rule files
- Undo/redo support for bulk operations
- Inline tag rewriting (not just frontmatter)
