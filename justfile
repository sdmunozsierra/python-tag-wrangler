# Tag Wrangler - common recipes
# Install just: https://github.com/casey/just#installation
# Run `just` to see all available recipes

# Default: list available recipes
default:
    @just --list

# Install all dependencies
setup:
    uv sync

# Run the Streamlit app
run:
    uv run streamlit run src/tag_wrangler/app/main.py

# Run the app pointed at the sample vault (opens browser)
demo:
    @echo "Starting Tag Wrangler with sample vault at sample_vault/"
    @echo "Load 'sample_vault' in the sidebar when the browser opens."
    uv run streamlit run src/tag_wrangler/app/main.py

# Run the app on a custom port
run-port port="8501":
    uv run streamlit run src/tag_wrangler/app/main.py --server.port {{port}}

# Run linter
lint:
    uv run ruff check src/

# Run linter and auto-fix issues
lint-fix:
    uv run ruff check --fix src/

# Format code
fmt:
    uv run ruff format src/

# Check formatting without writing changes
fmt-check:
    uv run ruff format --check src/

# Run tests
test:
    uv run pytest

# Run tests with verbose output
test-verbose:
    uv run pytest -v

# Lint + format + test
check: lint fmt-check test

# Quick smoke test: scan the sample vault from the CLI
smoke-test:
    uv run python -c "\
    from tag_wrangler.vault import scan_vault, build_tag_index; \
    from tag_wrangler.analyzer import vault_stats, find_similar_tags; \
    from pathlib import Path; \
    notes = scan_vault(Path('sample_vault')); \
    idx = build_tag_index(notes); \
    stats = vault_stats(notes, idx); \
    print(f'Notes: {stats[\"total_notes\"]}'); \
    print(f'Tags:  {stats[\"total_unique_tags\"]}'); \
    print(f'Avg tags/note: {stats[\"avg_tags_per_note\"]}'); \
    similar = find_similar_tags(idx, 70); \
    print(f'Similar pairs: {len(similar)}'); \
    print('Smoke test passed.')"

# Clean generated files
clean:
    rm -rf .venv __pycache__ .pytest_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Show project dependency tree
deps:
    uv tree

# Add a new dependency
add dep:
    uv add {{dep}}

# Add a new dev dependency
add-dev dep:
    uv add --dev {{dep}}

# Rebuild the lock file from scratch
lock:
    uv lock
