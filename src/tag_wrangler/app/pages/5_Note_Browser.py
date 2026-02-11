"""Note Browser - inspect individual notes and edit their frontmatter."""

from __future__ import annotations

import pandas as pd
import streamlit as st
import yaml

from tag_wrangler.app.state import init_state, reload_vault, require_vault
from tag_wrangler.parser import write_frontmatter

init_state()
st.title("Note Browser")

if not require_vault():
    st.stop()

notes = st.session_state.notes
tag_index = st.session_state.tag_index
vault_root = st.session_state.vault_path

# ---- Filter / search ----
col_search, col_filter = st.columns([2, 1])
with col_search:
    search = st.text_input("Search notes", placeholder="Filter by title or path...")
with col_filter:
    filter_tag = st.selectbox(
        "Filter by tag",
        ["(all)"] + sorted(tag_index.keys()),
        key="note_filter_tag",
    )

filtered = notes
if search:
    q = search.lower()
    filtered = [
        n for n in filtered if q in n.title.lower() or q in str(n.path).lower()
    ]
if filter_tag != "(all)":
    filtered = [n for n in filtered if filter_tag in n.tags]

st.write(f"**{len(filtered)}** note(s)")

# ---- Note list ----
if filtered:
    note_options = {f"{n.title}  ({n.path})": i for i, n in enumerate(filtered)}
    selected_label = st.selectbox(
        "Select a note",
        options=list(note_options.keys()),
        index=None,
        placeholder="Choose a note...",
    )

    if selected_label is not None:
        note = filtered[note_options[selected_label]]

        st.divider()

        # ---- Note detail ----
        st.subheader(note.title)
        st.caption(str(note.path))

        detail_left, detail_right = st.columns(2)

        with detail_left:
            st.markdown("**Tags**")
            if note.tags:
                st.write(", ".join(f"`{t}`" for t in note.tags))
            else:
                st.write("*(no tags)*")

            st.markdown("**Frontmatter**")
            st.code(yaml.dump(note.frontmatter, default_flow_style=False), language="yaml")

        with detail_right:
            st.markdown("**Body preview**")
            body_preview = note.body[:2000]
            if len(note.body) > 2000:
                body_preview += "\n\n... (truncated)"
            st.text_area(
                "Content",
                value=body_preview,
                height=350,
                disabled=True,
                label_visibility="collapsed",
            )

        # ---- Edit frontmatter ----
        st.divider()
        st.subheader("Edit frontmatter")
        st.caption(
            "Edit the YAML below and click Save. "
            "Changes are written directly to the file."
        )

        fm_yaml = yaml.dump(note.frontmatter, default_flow_style=False)
        edited_yaml = st.text_area(
            "Frontmatter YAML",
            value=fm_yaml,
            height=200,
            key=f"edit_fm_{note.path}",
        )

        if st.button("Save frontmatter"):
            try:
                new_fm = yaml.safe_load(edited_yaml) or {}
                if not isinstance(new_fm, dict):
                    st.error("Frontmatter must be a YAML mapping (key: value pairs).")
                else:
                    write_frontmatter(note, vault_root, new_fm)
                    reload_vault()
                    st.success("Frontmatter saved.")
                    st.rerun()
            except yaml.YAMLError as e:
                st.error(f"Invalid YAML: {e}")

    # ---- Bulk view table ----
    st.divider()
    st.subheader("All notes")
    all_df = pd.DataFrame(
        [
            {
                "Title": n.title,
                "Path": str(n.path),
                "Tags": ", ".join(n.tags),
                "# Tags": len(n.tags),
            }
            for n in filtered
        ]
    )
    st.dataframe(all_df, use_container_width=True, hide_index=True, height=400)
