"""Tag Explorer - browse, search, and inspect tags."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from tag_wrangler.analyzer import tag_hierarchy
from tag_wrangler.app.state import init_state, require_vault

init_state()
st.title("Tag Explorer")

if not require_vault():
    st.stop()

tag_index = st.session_state.tag_index

# ---- Search / filter ----
search = st.text_input("Search tags", placeholder="Type to filter...")

filtered = {
    k: v
    for k, v in tag_index.items()
    if not search or search.lower() in k.lower()
}

st.write(f"Showing **{len(filtered)}** of {len(tag_index)} tags")

# ---- Tag table ----
sort_col = st.radio(
    "Sort by", ["Count (desc)", "Count (asc)", "Name (A-Z)", "Name (Z-A)"],
    horizontal=True,
)

rows = [
    {
        "Tag": info.name,
        "Count": info.count,
        "Nested": info.is_nested,
        "Root": info.root if info.is_nested else "",
    }
    for info in filtered.values()
]

if rows:
    df = pd.DataFrame(rows)
    if sort_col == "Count (desc)":
        df = df.sort_values("Count", ascending=False)
    elif sort_col == "Count (asc)":
        df = df.sort_values("Count", ascending=True)
    elif sort_col == "Name (A-Z)":
        df = df.sort_values("Tag")
    else:
        df = df.sort_values("Tag", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True, height=500)

# ---- Tag detail ----
st.divider()
st.subheader("Tag detail")
selected_tag = st.selectbox(
    "Select a tag to inspect",
    options=sorted(tag_index.keys()),
    index=None,
    placeholder="Choose a tag...",
)

if selected_tag and selected_tag in tag_index:
    info = tag_index[selected_tag]
    st.write(f"**{info.name}** appears in **{info.count}** note(s):")
    for p in info.notes:
        st.write(f"- `{p}`")

# ---- Hierarchy view ----
st.divider()
st.subheader("Tag hierarchy")
tree = tag_hierarchy(tag_index)
if tree:
    for root, children in sorted(tree.items()):
        with st.expander(f"{root}/ ({len(children)} children)"):
            for child in sorted(children):
                count = tag_index.get(f"{root}/{child}", None)
                label = f"`{root}/{child}`"
                if count:
                    label += f" ({count.count})"
                st.write(label)
else:
    st.info("No nested tags found (e.g. `project/work`).")
