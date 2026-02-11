"""Shared Streamlit session state helpers."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from tag_wrangler.vault import build_tag_index, scan_vault


def init_state() -> None:
    """Initialise session state defaults."""
    if "vault_path" not in st.session_state:
        st.session_state.vault_path = None
    if "notes" not in st.session_state:
        st.session_state.notes = []
    if "tag_index" not in st.session_state:
        st.session_state.tag_index = {}


def load_vault(path: str) -> bool:
    """Load (or reload) a vault from *path*. Returns True on success."""
    vault = Path(path).expanduser().resolve()
    if not vault.is_dir():
        st.error(f"Directory not found: {vault}")
        return False
    notes = scan_vault(vault)
    if not notes:
        st.warning("No markdown files found in this directory.")
        return False
    st.session_state.vault_path = vault
    st.session_state.notes = notes
    st.session_state.tag_index = build_tag_index(notes)
    return True


def reload_vault() -> None:
    """Re-scan the currently loaded vault."""
    if st.session_state.vault_path:
        load_vault(str(st.session_state.vault_path))


def require_vault() -> bool:
    """Show warning if no vault is loaded. Returns True when vault is ready."""
    if not st.session_state.notes:
        st.info("Load a vault from the sidebar to get started.")
        return False
    return True
