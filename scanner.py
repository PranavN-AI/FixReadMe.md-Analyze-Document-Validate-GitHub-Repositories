"""scanner.py - FixReadMe repository analyzer."""
import os
import re
import json
import subprocess
from pathlib import Path

import requests

SKIP_DIRS = {".git", "venv", "env", ".venv", "node_modules", "__pycache__",
             ".vscode", ".idea", "dist", "build", ".streamlit"}

EXT_LANG = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".jsx": "JavaScript", ".tsx": "TypeScript", ".java": "Java",
    ".c": "C", ".cpp": "C++", ".cs": "C#", ".go": "Go", ".rs": "Rust",
    ".php": "PHP", ".rb": "Ruby", ".html": "HTML", ".css": "CSS",
    ".sql": "SQL", ".sh": "Shell", ".ipynb": "Jupyter Notebook",
}

FRAMEWORK_HINTS = {
    "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
    "streamlit": "Streamlit", "react": "React", "next": "Next.js",
    "vue": "Vue.js", "express": "Express", "pandas": "Pandas",
    "numpy": "NumPy", "torch": "PyTorch", "tensorflow": "TensorFlow",
    "selenium": "Selenium", "pytest": "Pytest",
}

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")
ENTRY_CANDIDATES = ["main.py", "app.py", "run.py", "manage.py", "server.py",
                    "cli.py", "index.js", "server.js", "index.html"]


def _walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            yield Path(dirpath) / name


def scan_repository(repo_path: str) -> dict:
    path = Path(repo_path).resolve()
    m = {
        "project_name": path.name, "path": str(path),
        "languages": [], "lang_counts": {}, "frameworks": [],
        "dependencies": [], "scripts": {},
        "has_package_json": False, "has_requirements": False,
        "has_license": False, "license_type": "Unknown",
        "has_tests": False, "has_ci": False, "has_env_example": False,
        "has_docker": False, "has_readme": False, "has_gitignore": False,
        "images": [], "todos": [], "file_count": 0,
        "git_repo": False, "git_remote": "", "owner": "", "repo": "",
        "is_public": False, "contributors": [], "folder_tree": "",
        "project_type": "Software Project", "entry_point": "",
    }

    text_files_scanned = 0
    for file in _walk(path):
        m["file_count"] += 1
        ext = file.suffix.lower()
        if ext in EXT_LANG:
            lang = EXT_LANG[ext]
            m["lang_counts"][lang] = m["lang_counts"].get(lang, 0) + 1
            if lang not in m["languages"]:
                m["languages"].append(lang)
        if ext in IMAGE_EXTS and len(m["images"]) < 6:
            m["images"].append(file.relative_to(path).as_posix())
        if ext in (".py", ".js", ".ts", ".md", ".txt") and text_files_scanned < 150:
            text_files_scanned += 1
            try:
                for line in file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if re.search(r"\b(TODO|FIXME)\b", line, re.I) and len(m["todos"]) < 8:
                        todo = re.sub(r".*(TODO|FIXME)[:\s]*", "", line, flags=re.I).strip()
                        if todo:
                            m["todos"].append(todo)
            except OSError:
                pass

    m["languages"].sort(key=lambda l: m["lang_counts"].get(l, 0), reverse=True)

    m["has_package_json"] = (path / "package.json").is_file()
    m["has_requirements"] = (path / "requirements.txt").is_file()
    m["has_license"] = any((path / n).is_file() for n in ("LICENSE", "LICENSE.md", "LICENCE"))
    m["has_gitignore"] = (path / ".gitignore").is_file()
    m["has_readme"] = (path / "README.md").is_file()
    m["has_env_example"] = any((path / n).is_file() for n in (".env.example", ".env.sample", ".env.template"))
    m["has_docker"] = (path / "Dockerfile").is_file() or (path / "docker-compose.yml").is_file()
    m["has_ci"] = (path / ".github" / "workflows").is_dir()
    m["has_tests"] = ((path / "tests").is_dir() or (path / "test").is_dir() or
                      any(f.name.startswith("test_") or f.name.endswith(".test.js") for f in _walk(path)))

    if m["has_package_json"]:
        try:
            pkg = json.loads((path / "package.json").read_text(encoding="utf-8"))
            m["dependencies"] = (list(pkg.get("dependencies", {})) +
                                 list(pkg.get("devDependencies", {})))[:15]
            m["scripts"] = pkg.get("scripts", {})
        except Exception:
            pass
    if m["has_requirements"]:
        try:
            for line in (path / "requirements.txt").read_text(encoding="utf-8").splitlines():
                dep = re.split(r"[=><!\[]", line.strip())[0]
                if dep:
                    m["dependencies"].append(dep)
        except OSError:
            pass

    for dep in m["dependencies"]:
        fw = FRAMEWORK_HINTS.get(dep.lower())
        if fw and fw not in m["frameworks"]:
            m["frameworks"].append(fw)

    if m["has_license"]:
        for name in ("LICENSE", "LICENSE.md", "LICENCE"):
            lp = path / name
            if lp.is_file():
                text = lp.read_text(encoding="utf-8", errors="ignore").lower()
                if "mit" in text[:200]:
                    m["license_type"] = "MIT"
                elif "apache" in text:
                    m["license_type"] = "Apache-2.0"
                elif "gnu general public" in text:
                    m["license_type"] = "GPL-3.0"
                break

    for cand in ENTRY_CANDIDATES:
        if (path / cand).is_file():
            m["entry_point"] = cand
            break

    fws = [f.lower() for f in m["frameworks"]]
    if "streamlit" in fws:
        m["project_type"] = "Streamlit Web App"
    elif any(f in fws for f in ("react", "next.js", "vue.js")):
        m["project_type"] = "Web Frontend"
    elif any(f in fws for f in ("flask", "django", "fastapi", "express")):
        m["project_type"] = "Web API / Backend"
    elif "Jupyter Notebook" in m["languages"]:
        m["project_type"] = "Data / ML Project"
    elif (path / "index.html").is_file() and not m["has_package_json"]:
        m["project_type"] = "Static Website"
    elif m["entry_point"] == "cli.py":
        m["project_type"] = "CLI Tool"

    m.update(_git_metadata(path))

    tree = []
    try:
        for item in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            if item.name in SKIP_DIRS or item.name.startswith("."):
                continue
            if item.is_dir():
                tree.append(f"📁 {item.name}/")
                for sub in sorted(item.iterdir())[:6]:
                    if sub.name not in SKIP_DIRS and not sub.name.startswith("."):
                        tree.append(f"   {'📁' if sub.is_dir() else '📄'} {sub.name}")
            else:
                tree.append(f"📄 {item.name}")
            if len(tree) > 30:
                break
    except OSError:
        pass
    m["folder_tree"] = "\n".join(tree)
    return m


def _git_metadata(path: Path) -> dict:
    out = {"git_repo": False, "git_remote": "", "owner": "", "repo": "",
           "is_public": False, "contributors": []}
    try:
        r = subprocess.run(["git", "-C", str(path), "remote", "get-url", "origin"],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            out["git_repo"] = True
            out["git_remote"] = r.stdout.strip()
            match = re.search(r"github\.com[:/](?P<o>[^/]+)/(?P<r>[^/]+?)(?:\.git)?/?$",
                              out["git_remote"])
            if match:
                out["owner"], out["repo"] = match.group("o"), match.group("r")
                try:
                    api = requests.get(
                        f"https://api.github.com/repos/{out['owner']}/{out['repo']}", timeout=5)
                    out["is_public"] = api.status_code == 200 and not api.json().get("private", True)
                except requests.RequestException:
                    out["is_public"] = False
        r2 = subprocess.run(["git", "-C", str(path), "shortlog", "-sn", "HEAD"],
                            capture_output=True, text=True, timeout=5)
        if r2.returncode == 0:
            for line in r2.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) == 2:
                    out["contributors"].append(parts[1].strip())
    except (subprocess.SubprocessError, OSError):
        pass
    return out