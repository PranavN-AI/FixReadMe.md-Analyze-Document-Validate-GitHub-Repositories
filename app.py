"""app.py - FixReadMe Streamlit UI with GitHub URL support."""
from pathlib import Path

import streamlit as st

from ai_writer import write_features, write_tagline_and_description
from renderer import build_readme
from scanner import scan_repository

DEFAULT_PATH = str(Path.cwd())

st.set_page_config(page_title="FixReadMe", page_icon="📝", layout="wide")

st.title("📝 FixReadMe")
st.caption("Analyze · Document · Validate — Perfect README for local folders & GitHub repos")

st.sidebar.header("⚙️ Options")
center_badges = st.sidebar.checkbox("Center badge header", True)
include_toc = st.sidebar.checkbox("Include table of contents", True)
validate_badges = st.sidebar.checkbox("Validate badges online", True)

st.sidebar.markdown("---")
st.sidebar.markdown("**💡 Tips:**")
st.sidebar.markdown("- Enter local folder path OR GitHub URL")
st.sidebar.markdown("- GitHub URLs are cloned temporarily")
st.sidebar.markdown("- Best results with public repos")

# Input section with tabs
tab_local, tab_github = st.tabs(["📁 Local Folder", "🔗 GitHub URL"])

with tab_local:
    repo_path = st.text_input(
        "Repository folder path",
        DEFAULT_PATH,
        help="Enter the full path to your local project folder"
    )

with tab_github:
    github_url = st.text_input(
        "GitHub repository URL",
        "https://github.com/owner/repo",
        help="Enter the GitHub repository URL (e.g., https://github.com/user/project)"
    )

# Determine which input to use
use_github = False
if tab_github._active and github_url != "https://github.com/owner/repo":
    use_github = True
    input_path = github_url
else:
    input_path = repo_path

go = st.button("🚀 Analyze & Generate", type="primary", use_container_width=True)

if go:
    if use_github:
        if not input_path.startswith("http") or "github.com" not in input_path:
            st.error("❌ Please enter a valid GitHub URL")
            st.stop()
        
        with st.spinner("📥 Cloning GitHub repository..."):
            try:
                meta = scan_repository(input_path)
                st.success(f"✅ Cloned successfully!")
            except Exception as e:
                st.error(f"❌ Failed to clone: {e}")
                st.stop()
    else:
        p = Path(input_path.strip().strip('"'))
        if not p.is_dir():
            st.error("❌ Path does not exist or is not a folder.")
            st.stop()
        
        with st.spinner("🔍 Scanning repository..."):
            meta = scan_repository(input_path)
    
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
    
    if not use_github:  # Only allow save for local repos
        target = Path(input_path) / "README.md"
        if c2.button("📥 Save into repository", use_container_width=True):
            if target.exists():
                target.replace(target.parent / "README_backup.md")
            target.write_text(readme, encoding="utf-8")
            st.success(f"✅ Saved to {target} (previous README kept as README_backup.md)")
    else:
        st.info("💡 GitHub repos: Download the README and manually upload it to your repository")