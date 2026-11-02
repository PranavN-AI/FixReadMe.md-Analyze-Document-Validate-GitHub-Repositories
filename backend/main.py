from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .analyzer import outline
    from .github_client import GitHubClient, GitHubError, parse_repository_url
    from .readme_generator import generate
    from .repository_scanner import scan
    from .scoring import score
    from .validator import validate
except ImportError:
    from analyzer import outline
    from github_client import GitHubClient, GitHubError, parse_repository_url
    from readme_generator import generate
    from repository_scanner import scan
    from scoring import score
    from validator import validate

app = FastAPI(title="FixReadMe API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class AnalyzeRequest(BaseModel):
    repository_url: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "fixreadme"}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    try:
        ref = parse_repository_url(request.repository_url)
        repository = GitHubClient().repository(ref)
        analysis = scan(ref, GitHubClient())
        sections = outline(repository, analysis)
        markdown = generate(repository, analysis, sections)
        findings = validate(markdown, repository, analysis)
        result = score(findings)
        repository["project_type"] = analysis["project_type"]
        return {"success": True, "repository": repository, "analysis": analysis,
                "readme": {"markdown": markdown, "validation": findings, **result}}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GitHubError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Analysis failed. No README was generated.") from exc
