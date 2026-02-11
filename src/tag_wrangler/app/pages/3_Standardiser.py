"""Standardiser - find duplicates, similar tags, and create rename rules."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from tag_wrangler.analyzer import find_similar_tags
from tag_wrangler.app.state import init_state, reload_vault, require_vault
from tag_wrangler.operations import merge_tags, rename_tag

init_state()
st.title("Tag Standardiser")

if not require_vault():
    st.stop()

notes = st.session_state.notes
tag_index = st.session_state.tag_index
vault_root = st.session_state.vault_path

# ---- Similar tags ----
st.subheader("Similar tags (possible duplicates)")

threshold = st.slider("Similarity threshold", 50, 100, 80, step=5)

pairs = find_similar_tags(tag_index, threshold=threshold)

if pairs:
    st.write(f"Found **{len(pairs)}** similar pair(s):")
    pair_df = pd.DataFrame(pairs, columns=["Tag A", "Tag B", "Similarity"])
    st.dataframe(pair_df, use_container_width=True, hide_index=True)
else:
    st.success("No similar tags found at this threshold.")

# ---- Rename single tag ----
st.divider()
st.subheader("Rename a tag")

col1, col2 = st.columns(2)
with col1:
    old_name = st.selectbox(
        "Tag to rename",
        options=sorted(tag_index.keys()),
        index=None,
        placeholder="Select tag...",
        key="rename_old",
    )
with col2:
    new_name = st.text_input("New name", key="rename_new")

if st.button("Rename", disabled=not (old_name and new_name)):
    count = rename_tag(notes, vault_root, old_name, new_name)
    reload_vault()
    st.success(f"Renamed `{old_name}` -> `{new_name}` in {count} note(s).")
    st.rerun()

# ---- Merge tags ----
st.divider()
st.subheader("Merge tags")
st.caption("Select multiple source tags to merge into a single target tag.")

source_tags = st.multiselect(
    "Source tags (will be replaced)",
    options=sorted(tag_index.keys()),
    key="merge_sources",
)
target_tag = st.text_input("Target tag (keep this one)", key="merge_target")

if st.button("Merge", disabled=not (source_tags and target_tag)):
    count = merge_tags(notes, vault_root, source_tags, target_tag)
    reload_vault()
    st.success(
        f"Merged {len(source_tags)} tag(s) into `{target_tag}` "
        f"across {count} note(s)."
    )
    st.rerun()

# ---- Batch rename rules ----
st.divider()
st.subheader("Batch rename rules")
st.caption(
    "Define multiple rename rules (one per line, format: `old_tag -> new_tag`), "
    "then apply them all at once."
)

rules_text = st.text_area(
    "Rename rules",
    placeholder="javascript -> js\npython3 -> python\nml -> machine-learning",
    height=150,
)

if st.button("Apply rules"):
    if rules_text.strip():
        total = 0
        errors = []
        for line in rules_text.strip().splitlines():
            line = line.strip()
            if not line or "->" not in line:
                continue
            parts = line.split("->")
            if len(parts) != 2:
                errors.append(f"Invalid rule: {line}")
                continue
            old, new = parts[0].strip(), parts[1].strip()
            count = rename_tag(notes, vault_root, old, new)
            total += count
        reload_vault()
        if errors:
            st.warning("\n".join(errors))
        st.success(f"Applied rules, modified {total} note(s) total.")
        st.rerun()
