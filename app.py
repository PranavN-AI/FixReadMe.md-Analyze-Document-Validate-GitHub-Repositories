"""app.py - FixReadMe Streamlit web UI."""
from pathlib import Path

import streamlit as st

from ai_writer import write_features, write_tagline_and_description
from renderer import build_readme
from scanner import scan_repository

DEFAULT_PATH = str(Path.cwd())

st.set_page_config(page_title="FixReadMe", page_icon="📝", layout="wide")

st.title("📝 FixReadMe")
st.caption("Analyze · Document · Validate — a perfect README.md for any repository, in seconds.")

st.sidebar.header("⚙️ Options")
center_badges = st.sidebar.checkbox("Center badge header", True)
include_toc = st.sidebar.checkbox("Include table of contents", True)
validate_badges = st.sidebar.checkbox("Validate badges online", True)

repo_path = st.text_input("Repository folder path", DEFAULT_PATH)
go = st.button("🚀 Analyze & Generate", type="primary", use_container_width=True)

if go:
    p = Path(repo_path.strip().strip('"'))
    if not p.is_dir():
        st.error("❌ Path does not exist or is not a folder.")
        st.stop()

    with st.spinner("🔍 Scanning repository..."):
        meta = scan_repository(str(p))
    with st.spinner("🤖 Writing AI sections..."):
        tagline, description = write_tagline_and_description(meta)
        features = write_features(meta)
    with st.spinner("🎨 Rendering README, badges & verification report..."):
        readme = build_readme(meta, tagline, description, features,
                              center_badges=center_badges, include_toc=include_toc,
                              validate=validate_badges)

    st.success(f"Scanned **{meta['file_count']} files** • {len(meta['languages'])} languages • "
               f"{len(meta['frameworks'])} frameworks • type: {meta['project_type']}")

    tab_view, tab_raw, tab_meta = st.tabs(["📄 Preview", "🧾 Raw Markdown", "🔍 Metadata"])
    with tab_view:
        st.markdown(readme)
    with tab_raw:
        st.code(readme, language="markdown")
    with tab_meta:
        st.json(meta)

    c1, c2, _ = st.columns([1, 1, 2])
    c1.download_button("💾 Download README.md", readme, file_name="README.md",
                       mime="text/markdown", use_container_width=True)
    target = p / "README.md"
    if c2.button("📥 Save into repository", use_container_width=True):
        if target.exists():
            target.replace(p / "README_backup.md")
        target.write_text(readme, encoding="utf-8")
        st.success(f"✅ Saved to {target} (previous README kept as README_backup.md)")