"""Tag Wrangler - Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from tag_wrangler.app.state import init_state, load_vault


def main() -> None:
    st.set_page_config(
        page_title="Tag Wrangler",
        page_icon=":label:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_state()
    _sidebar()
    _home()


def _sidebar() -> None:
    with st.sidebar:
        st.title("Tag Wrangler")
        st.caption("Obsidian vault tag management")
        st.divider()

        vault_dir = st.text_input(
            "Vault path",
            value=str(st.session_state.vault_path or ""),
            placeholder="/path/to/your/obsidian/vault",
        )
        if st.button("Load vault", use_container_width=True):
            if vault_dir:
                with st.spinner("Scanning vault..."):
                    if load_vault(vault_dir):
                        st.success(
                            f"Loaded {len(st.session_state.notes)} notes "
                            f"with {len(st.session_state.tag_index)} unique tags"
                        )

        if st.session_state.notes:
            st.divider()
            st.metric("Notes", len(st.session_state.notes))
            st.metric("Unique tags", len(st.session_state.tag_index))


def _home() -> None:
    st.title("Welcome to Tag Wrangler")
    st.markdown(
        """
Manage, organise, and standardise the tags in your Obsidian vault.

**Use the sidebar** to point at your vault directory, then explore the pages:

| Page | What it does |
|---|---|
| **Dashboard** | High-level stats, tag frequency charts, health overview |
| **Tag Explorer** | Browse every tag, see which notes use it, view hierarchy |
| **Standardiser** | Find similar / duplicate tags, create rename rules |
| **Bulk Operations** | Add, remove, rename, or merge tags across many notes at once |
| **Note Browser** | Browse individual notes, inspect and edit their frontmatter |
"""
    )

    if not st.session_state.notes:
        st.info(
            "Enter the path to your Obsidian vault in the sidebar and "
            "click **Load vault** to begin."
        )


if __name__ == "__main__":
    main()
