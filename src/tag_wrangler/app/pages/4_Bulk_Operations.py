"""Bulk Operations - add, remove, and manipulate tags across many notes."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from tag_wrangler.app.state import init_state, reload_vault, require_vault
from tag_wrangler.operations import add_tag_to_notes, delete_tag, rename_tag

init_state()
st.title("Bulk Operations")

if not require_vault():
    st.stop()

notes = st.session_state.notes
tag_index = st.session_state.tag_index
vault_root = st.session_state.vault_path

# ---- Filter notes ----
st.subheader("Select notes")
st.caption("Filter notes to target for bulk operations.")

filter_mode = st.radio(
    "Filter by",
    ["All notes", "Notes with specific tag", "Notes in folder", "Untagged notes"],
    horizontal=True,
)

target_notes = list(notes)

if filter_mode == "Notes with specific tag":
    filter_tag = st.selectbox(
        "Tag", sorted(tag_index.keys()), index=None, placeholder="Choose tag..."
    )
    if filter_tag:
        target_notes = [n for n in notes if filter_tag in n.tags]
elif filter_mode == "Notes in folder":
    folders = sorted(
        set(str(n.path.parent) for n in notes if str(n.path.parent) != ".")
    )
    folder = st.selectbox(
        "Folder", ["(root)"] + folders, index=None, placeholder="Choose folder..."
    )
    if folder:
        if folder == "(root)":
            target_notes = [n for n in notes if str(n.path.parent) == "."]
        else:
            target_notes = [
                n for n in notes if str(n.path.parent).startswith(folder)
            ]
elif filter_mode == "Untagged notes":
    target_notes = [n for n in notes if not n.tags]

st.write(f"**{len(target_notes)}** note(s) selected")

if target_notes:
    with st.expander("Preview selected notes"):
        preview_df = pd.DataFrame(
            [
                {
                    "Note": n.title,
                    "Path": str(n.path),
                    "Tags": ", ".join(n.tags) or "(none)",
                }
                for n in target_notes[:100]
            ]
        )
        st.dataframe(preview_df, use_container_width=True, hide_index=True)
        if len(target_notes) > 100:
            st.caption(f"Showing first 100 of {len(target_notes)}")

st.divider()

# ---- Operations ----
operation = st.selectbox(
    "Operation",
    ["Add tag", "Remove tag", "Find & replace tag"],
)

if operation == "Add tag":
    tag_to_add = st.text_input("Tag to add")
    if st.button("Add to selected notes", disabled=not tag_to_add):
        count = add_tag_to_notes(notes, vault_root, tag_to_add, target_notes)
        reload_vault()
        st.success(f"Added `{tag_to_add}` to {count} note(s).")
        st.rerun()

elif operation == "Remove tag":
    tag_to_remove = st.selectbox(
        "Tag to remove",
        sorted(tag_index.keys()),
        index=None,
        placeholder="Select tag...",
        key="bulk_remove",
    )
    if st.button("Remove from all notes", disabled=not tag_to_remove):
        count = delete_tag(notes, vault_root, tag_to_remove)
        reload_vault()
        st.success(f"Removed `{tag_to_remove}` from {count} note(s).")
        st.rerun()

elif operation == "Find & replace tag":
    col1, col2 = st.columns(2)
    with col1:
        find_tag = st.selectbox(
            "Find tag",
            sorted(tag_index.keys()),
            index=None,
            placeholder="Select tag...",
            key="bulk_find",
        )
    with col2:
        replace_tag = st.text_input("Replace with", key="bulk_replace")
    if st.button("Replace", disabled=not (find_tag and replace_tag)):
        count = rename_tag(notes, vault_root, find_tag, replace_tag)
        reload_vault()
        st.success(
            f"Replaced `{find_tag}` with `{replace_tag}` in {count} note(s)."
        )
        st.rerun()
