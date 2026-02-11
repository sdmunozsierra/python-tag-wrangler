"""Dashboard - vault overview and tag statistics."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from tag_wrangler.analyzer import (
    orphan_tags,
    tag_co_occurrence,
    tag_frequency,
    vault_stats,
)
from tag_wrangler.app.state import init_state, require_vault

init_state()
st.title("Dashboard")

if not require_vault():
    st.stop()

notes = st.session_state.notes
tag_index = st.session_state.tag_index
stats = vault_stats(notes, tag_index)

# ---- Key metrics row ----
cols = st.columns(5)
cols[0].metric("Total notes", stats["total_notes"])
cols[1].metric("Unique tags", stats["total_unique_tags"])
cols[2].metric("Notes with tags", stats["notes_with_tags"])
cols[3].metric("Untagged notes", stats["notes_without_tags"])
cols[4].metric("Avg tags / note", stats["avg_tags_per_note"])

st.divider()

# ---- Tag frequency chart ----
left, right = st.columns(2)

with left:
    st.subheader("Tag frequency (top 30)")
    freq = tag_frequency(notes)
    top = freq.most_common(30)
    if top:
        df = pd.DataFrame(top, columns=["Tag", "Count"])
        fig = px.bar(
            df,
            x="Count",
            y="Tag",
            orientation="h",
            height=max(400, len(top) * 22),
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=0))
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Tag distribution")
    tag_counts = [len(n.tags) for n in notes]
    if tag_counts:
        df_dist = pd.DataFrame({"tags_per_note": tag_counts})
        fig2 = px.histogram(
            df_dist,
            x="tags_per_note",
            nbins=max(max(tag_counts), 1),
            labels={"tags_per_note": "Tags per note"},
        )
        fig2.update_layout(margin=dict(l=0))
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---- Orphan / rare tags ----
st.subheader("Rare tags (used once)")
orphans = orphan_tags(tag_index, threshold=1)
if orphans:
    st.write(f"Found **{len(orphans)}** tags that appear in only 1 note:")
    orphan_df = pd.DataFrame(
        [{"Tag": o.name, "Note": str(o.notes[0])} for o in orphans]
    )
    st.dataframe(orphan_df, use_container_width=True, hide_index=True)
else:
    st.success("No orphan tags found.")

# ---- Co-occurrence ----
st.subheader("Tag co-occurrence (top 20)")
co = tag_co_occurrence(notes, min_count=2)
if co:
    sorted_co = sorted(co.items(), key=lambda x: x[1], reverse=True)[:20]
    co_df = pd.DataFrame(
        [{"Tag A": a, "Tag B": b, "Count": c} for (a, b), c in sorted_co]
    )
    st.dataframe(co_df, use_container_width=True, hide_index=True)
else:
    st.info("Not enough data for co-occurrence analysis.")
