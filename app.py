"""app.py - FixReadMe Streamlit UI (local folder + GitHub URL)."""
from pathlib import Path

import streamlit as st

from ai_writer import write_features, write_tagline_and_description
from renderer import build_readme
from scanner import scan_repository

st.set_page_config(page_title="FixReadMe", page_icon="📝", layout="wide")
st.title("📝 FixReadMe")
st.caption("Analyze · Document · Validate — perfect README for local folders & GitHub repos")

st.sidebar.header("⚙️ Options")
center_badges = st.sidebar.checkbox("Center badge header", True)
include_toc = st.sidebar.checkbox("Include table of contents", True)
validate_badges = st.sidebar.checkbox("Validate badges online", True)

mode = st.radio("Input source", ["📁 Local folder", "🔗 GitHub URL"], horizontal=True)
use_github = mode.startswith("🔗")

if use_github:
    input_path = st.text_input("GitHub repository URL", "https://github.com/owner/repo")
else:
    input_path = st.text_input("Repository folder path", str(Path.cwd()))

go = st.button("🚀 Analyze & Generate", type="primary", use_container_width=True)

if go:
    if use_github and not (input_path.startswith("http") and "github.com" in input_path):
        st.error("❌ Enter a valid GitHub URL")
        st.stop()
    if not use_github and not Path(input_path.strip().strip('"')).is_dir():
        st.error("❌ Path does not exist or is not a folder.")
        st.stop()

    try:
        with st.spinner("📥 Cloning..." if use_github else "🔍 Scanning..."):
            meta = scan_repository(input_path.strip().strip('"'))
        with st.spinner("🤖 Writing AI sections..."):
            tagline, description = write_tagline_and_description(meta)
            features = write_features(meta)
        with st.spinner("🎨 Rendering README, badges & verification report..."):
            readme = build_readme(meta, tagline, description, features,
                                  center_badges=center_badges, include_toc=include_toc,
                                  validate=validate_badges)
    except Exception as e:
        st.error(f"❌ {e}")
        st.stop()

    st.success(f"Scanned **{meta['file_count']} files** • {len(meta['languages'])} languages • "
               f"{len(meta['frameworks'])} frameworks • {meta['project_type']}")

    t1, t2, t3 = st.tabs(["📄 Preview", "🧾 Raw Markdown", "🔍 Metadata"])
    with t1:
        st.markdown(readme)
    with t2:
        st.code(readme, language="markdown")
    with t3:
        st.json(meta)

    c1, c2, _ = st.columns([1, 1, 2])
    c1.download_button("💾 Download README.md", readme, file_name="README.md",
                       mime="text/markdown", use_container_width=True)
    if not use_github:
        target = Path(input_path.strip().strip('"')) / "README.md"
        if c2.button("📥 Save into repository", use_container_width=True):
            if target.exists():
                target.replace(target.parent / "README_backup.md")
            target.write_text(readme, encoding="utf-8")
            st.success(f"✅ Saved to {target} (old README kept as README_backup.md)")
    else:
        st.info("💡 GitHub mode: download the README and commit it to your repo.")