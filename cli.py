"""cli.py - one-command README generation (local path or GitHub URL)."""
import argparse
from pathlib import Path

from ai_writer import write_features, write_tagline_and_description
from renderer import build_readme
from scanner import scan_repository


def main():
    ap = argparse.ArgumentParser(description="FixReadMe - generate a professional README.md")
    ap.add_argument("path", nargs="?", default=".", help="local folder or GitHub URL")
    ap.add_argument("--no-save", action="store_true", help="print only, don't write a file")
    args = ap.parse_args()

    meta = scan_repository(args.path)
    tagline, description = write_tagline_and_description(meta)
    features = write_features(meta)
    readme = build_readme(meta, tagline, description, features)

    if args.no_save:
        print(readme)
    elif meta.get("is_github_clone"):
        out = Path.cwd() / f"{meta['project_name']}_README.md"
        out.write_text(readme, encoding="utf-8")
        print(f"✅ GitHub mode: README saved to {out}")
    else:
        out = Path(meta["path"]) / "README.md"
        if out.exists():
            out.replace(out.parent / "README_backup.md")
        out.write_text(readme, encoding="utf-8")
        print(f"✅ README.md written to: {out}")
    print(f"📊 Done: {meta['project_name']} ({meta['project_type']})")


if __name__ == "__main__":
    main()