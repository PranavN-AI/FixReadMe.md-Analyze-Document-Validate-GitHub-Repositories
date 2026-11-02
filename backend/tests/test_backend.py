from fastapi.testclient import TestClient

from backend.github_client import parse_repository_url
from backend.analyzer import outline
from backend.badge_generator import generate as generate_badges
from backend.main import app
from backend.repository_scanner import _is_relevant
from backend.readme_generator import generate
from backend.scoring import score
from backend.validator import validate


def test_parse_repository_url():
    ref = parse_repository_url("https://github.com/owner/project.git/")
    assert (ref.owner, ref.name) == ("owner", "project")


def test_invalid_repository_url():
    client = TestClient(app)
    response = client.post("/api/analyze", json={"repository_url": "https://gitlab.com/a/b"})
    assert response.status_code == 400


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scanner_keeps_readme_without_extension_and_skips_builds():
    assert _is_relevant("README")
    assert _is_relevant("src/main.py")
    assert not _is_relevant("dist/bundle.js")


def test_generator_uses_repository_evidence_and_verified_sections():
    repository = {
        "name": "sample-api", "owner": "owner", "description": "A sample API",
        "language": "Python", "license": "MIT", "url": "https://github.com/owner/sample-api",
        "stars": 2,
    }
    analysis = {
        "project_type": "REST API", "languages": ["Python"], "frameworks": ["FastAPI"],
        "dependencies": ["fastapi"], "features": ["Exposes 1 detected HTTP route(s)."],
        "structure": ["main.py", "requirements.txt"], "files_scanned": 2,
        "entry_points": ["main.py"], "routes": ["/health"], "manifests": ["requirements.txt"],
        "ci_workflows": [], "configuration_files": [], "environment_variables": [],
        "scripts": {},
    }
    markdown = generate(repository, analysis, [])
    assert "sample-api" in markdown
    assert "/health" in markdown
    assert "shields.io" in markdown
    assert "```mermaid" in markdown


def test_validation_and_score_penalize_broken_markdown():
    analysis = {"dependencies": ["fastapi"], "routes": ["/health"], "manifests": ["requirements.txt"]}
    findings = validate("# Demo\n\n```python\nbroken", {}, analysis)
    result = score(findings)
    assert any(item["status"] == "failed" for item in findings)
    assert result["score"] < 100


def test_outline_is_repository_specific():
    repository = {"owner": "o", "name": "api", "license": None}
    api = {"project_type": "REST API", "languages": ["Python"], "frameworks": ["FastAPI"],
           "dependencies": ["fastapi"], "features": [], "structure": ["main.py"],
           "entry_points": ["main.py"], "routes": ["/health"], "environment_variables": [],
           "configuration_files": [], "ci_workflows": [], "manifests": []}
    library = {"project_type": "Python package", "languages": ["Python"], "frameworks": [],
               "dependencies": [], "features": [], "structure": ["package.py"],
               "entry_points": [], "routes": [], "environment_variables": [],
               "configuration_files": [], "ci_workflows": [], "manifests": []}
    assert "API" in outline(repository, api)
    assert "API" not in outline(repository, library)
    assert outline(repository, api) != outline(repository, library)


def test_badges_are_deduplicated_and_repository_specific():
    repository = {"owner": "o", "name": "project", "license": "MIT", "language": "Python"}
    badges = generate_badges(repository, {})
    assert len(badges) == len(set(badges))
    assert all("o/project" in badge or "license" in badge or "language" in badge for badge in badges)
