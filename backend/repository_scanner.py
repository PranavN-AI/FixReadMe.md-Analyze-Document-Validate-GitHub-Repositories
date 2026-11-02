import json
import re
from pathlib import PurePosixPath
try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

IMPORTANT = {
    "README", "README.md", "README.rst", "pyproject.toml", "requirements.txt", "package.json", "Cargo.toml",
    "go.mod", "pom.xml", "build.gradle", "Dockerfile", "docker-compose.yml",
    ".env.example", "Makefile",
}
SKIP = {".git", "node_modules", "dist", "build", "coverage", ".venv", "venv"}
SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java"}


def _is_relevant(path):
    parts = PurePosixPath(path).parts
    if any(part in SKIP for part in parts):
        return False
    name = PurePosixPath(path).name
    return name.upper() in {item.upper() for item in IMPORTANT} or \
        PurePosixPath(path).suffix in SOURCE_EXTENSIONS or "test" in name.lower()


def _dependency_names(files):
    result = []
    for path, text in files.items():
        name = PurePosixPath(path).name
        if name == "package.json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            result.extend((data.get("dependencies") or {}).keys())
            result.extend((data.get("devDependencies") or {}).keys())
        elif name == "requirements.txt":
            result.extend(re.split(r"[<>=!~]", line.strip())[0] for line in text.splitlines()
                          if line.strip() and not line.lstrip().startswith("#"))
        elif name == "pyproject.toml":
            if tomllib is not None:
                try:
                    document = tomllib.loads(text)
                except tomllib.TOMLDecodeError:
                    document = {}
                project = document.get("project") or {}
                for dependency in project.get("dependencies") or []:
                    result.append(re.split(r"[<>=!~;\\[]", str(dependency), maxsplit=1)[0].strip())
                for group in (project.get("optional-dependencies") or {}).values():
                    for dependency in group or []:
                        result.append(re.split(r"[<>=!~;\\[]", str(dependency), maxsplit=1)[0].strip())
        elif name == "go.mod":
            result.extend(re.findall(r"(?m)^\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+)\s+v", text))
        elif name == "Cargo.toml":
            section = False
            for line in text.splitlines():
                if line.strip() == "[dependencies]":
                    section = True
                elif line.startswith("["):
                    section = False
                elif section and "=" in line:
                    result.append(line.split("=", 1)[0].strip())
    return sorted({item for item in result if item})


def scan(ref, client):
    metadata = client.repository(ref)
    paths = client.tree(ref, metadata["default_branch"])
    relevant = [path for path in paths if _is_relevant(path)]
    selected = sorted(relevant, key=lambda path: (
        0 if PurePosixPath(path).name.upper() in {item.upper() for item in IMPORTANT} else 1,
        path.lower(),
    ))[:80]
    files = {}
    for path in selected:
        try:
            files[path] = client.file(ref, metadata["default_branch"], path)[:80000]
        except Exception:
            continue
    language_map = {"py": "Python", "js": "JavaScript", "ts": "TypeScript",
                    "go": "Go", "rs": "Rust", "java": "Java"}
    languages = sorted({language_map[PurePosixPath(path).suffix[1:]]
                        for path in paths if PurePosixPath(path).suffix[1:] in language_map})
    dependencies = _dependency_names(files)
    manifest_names = sorted({PurePosixPath(path).name for path in files
                             if PurePosixPath(path).name in {
                                 "package.json", "requirements.txt", "pyproject.toml",
                                 "setup.py", "Cargo.toml", "go.mod", "pom.xml", "build.gradle"}})
    ci_workflows = sorted(
        PurePosixPath(path).name for path in files
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))
    )
    configuration_files = sorted(
        path for path in files
        if PurePosixPath(path).name in {".env.example", "Dockerfile", "docker-compose.yml",
                                       "Makefile", "setup.cfg", "tox.ini", "pytest.ini"}
        or path.startswith(".github/")
    )
    env_vars = sorted(set(re.findall(r"(?m)^\s*([A-Z][A-Z0-9_]{2,})\s*=", "\n".join(
        text for path, text in files.items() if ".env" in PurePosixPath(path).name
    ))))
    scripts = {}
    if "package.json" in {PurePosixPath(path).name for path in files}:
        for path, text in files.items():
            if PurePosixPath(path).name == "package.json":
                try:
                    scripts = (json.loads(text).get("scripts") or {})
                except json.JSONDecodeError:
                    scripts = {}
                break
    existing_readme = next((text for path, text in files.items()
                            if PurePosixPath(path).name.lower() in {"readme", "readme.md", "readme.rst"}), "")
    frameworks = []
    code_blob = "\n".join(
        text for path, text in files.items()
        if PurePosixPath(path).suffix in SOURCE_EXTENSIONS or PurePosixPath(path).name == "package.json"
    ).lower()
    dependency_blob = " ".join(dependencies).lower()
    framework_patterns = (
        ("fastapi", "FastAPI", r"(?:from|import)\s+fastapi\b"),
        ("flask", "Flask", r"(?:from|import)\s+flask\b"),
        ("django", "Django", r"(?:from|import)\s+django\b"),
        ("express", "Express", r"(?:require\(\s*['\"]express|from\s+['\"]express)"),
        ("react", "React", r"(?:from\s+['\"]react|require\(\s*['\"]react)"),
        ("next", "Next.js", r"(?:from\s+['\"]next|require\(\s*['\"]next)"),
        ("streamlit", "Streamlit", r"(?:from|import)\s+streamlit\b"),
    )
    for needle, framework, pattern in framework_patterns:
        if needle in dependency_blob or re.search(pattern, code_blob):
            frameworks.append(framework)
    examples = sorted(path for path in paths if "example" in path.lower() or "demo" in path.lower())[:10]
    routes = sorted(set(re.findall(r"""(?:app|router)\.(?:get|post|put|delete|patch)\(\s*["']([^"']+)""",
                                   code_blob))) if any(item in frameworks for item in
                                                   ("FastAPI", "Flask", "Django", "Express")) else []
    entry_points = [path for path in selected if PurePosixPath(path).name in
                    {"main.py", "app.py", "server.py", "index.js", "src/index.ts", "src/main.py"}]
    ml_markers = {"torch", "tensorflow", "scikit-learn", "scikit_learn", "transformers", "pandas"}
    cli_markers = {"click", "typer", "argparse", "commander", "yargs"}
    has_ml = bool(ml_markers.intersection(set(dependency_blob.replace("-", "_").split())))
    has_cli = bool(cli_markers.intersection(set(dependency_blob.replace("-", "_").split())))
    project_type = "REST API" if routes or any(item in frameworks for item in ("FastAPI", "Flask", "Django", "Express")) \
        else "Frontend application" if any(item in frameworks for item in ("React", "Next.js")) \
        else "Machine learning project" if has_ml else "CLI tool" if has_cli \
        else "Python package" if "Python" in languages else "Developer tool"
    features = []
    if routes:
        features.append(f"Exposes {len(routes)} detected HTTP route(s).")
    if any("test" in path.lower() for path in paths):
        features.append("Includes automated test files.")
    return {
        "files_scanned": len(files), "languages": languages, "frameworks": frameworks,
        "dependencies": dependencies, "features": features,
        "structure": selected[:30], "evidence": [{"file": path, "excerpt": text[:500]}
                                                  for path, text in files.items()],
        "entry_points": entry_points, "routes": routes, "project_type": project_type,
        "manifests": manifest_names, "ci_workflows": ci_workflows,
        "configuration_files": configuration_files, "environment_variables": env_vars,
        "scripts": scripts, "examples": examples, "existing_readme": bool(existing_readme),
    }
