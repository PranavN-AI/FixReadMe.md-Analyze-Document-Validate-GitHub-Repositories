import re
from dataclasses import dataclass

import requests

try:
    from .config import GITHUB_TOKEN, REQUEST_TIMEOUT
except ImportError:
    from config import GITHUB_TOKEN, REQUEST_TIMEOUT

GITHUB_URL = re.compile(r"^https?://github\.com/([^/]+)/([^/?#]+?)(?:\.git)?/?$")


class GitHubError(RuntimeError):
    """A safe, user-facing GitHub retrieval error."""


@dataclass(frozen=True)
class RepositoryRef:
    owner: str
    name: str


def parse_repository_url(url: str) -> RepositoryRef:
    match = GITHUB_URL.match((url or "").strip())
    if not match:
        raise ValueError("Enter a public GitHub repository URL such as https://github.com/owner/repository.")
    return RepositoryRef(match.group(1), match.group(2))


class GitHubClient:
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/vnd.github+json", "User-Agent": "FixReadMe/1.0"})
        if GITHUB_TOKEN:
            self.session.headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    def _get(self, url):
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            raise GitHubError("GitHub could not be reached. Check the network and try again.") from exc
        if response.status_code == 404:
            raise GitHubError("Repository not found or it is private.")
        if response.status_code == 403 and "rate" in response.text.lower():
            raise GitHubError("GitHub API rate limit reached. Add a GitHub token or try again later.")
        if response.status_code >= 400:
            raise GitHubError(f"GitHub returned HTTP {response.status_code}.")
        return response.json()

    def repository(self, ref: RepositoryRef):
        data = self._get(f"https://api.github.com/repos/{ref.owner}/{ref.name}")
        license_data = data.get("license") or {}
        return {
            "name": data.get("name") or ref.name,
            "owner": (data.get("owner") or {}).get("login") or ref.owner,
            "description": data.get("description") or "",
            "language": data.get("language") or "",
            "stars": data.get("stargazers_count", 0),
            "license": license_data.get("spdx_id") or license_data.get("name") or "",
            "url": data.get("html_url") or f"https://github.com/{ref.owner}/{ref.name}",
            "default_branch": data.get("default_branch") or "main",
            "topics": data.get("topics") or [],
            "created_at": data.get("created_at") or "",
            "updated_at": data.get("updated_at") or "",
        }

    def tree(self, ref: RepositoryRef, branch: str):
        data = self._get(f"https://api.github.com/repos/{ref.owner}/{ref.name}/git/trees/{branch}?recursive=1")
        return [item["path"] for item in data.get("tree", []) if item.get("type") == "blob"]

    def file(self, ref: RepositoryRef, branch: str, path: str):
        data = self._get(f"https://api.github.com/repos/{ref.owner}/{ref.name}/contents/{path}?ref={branch}")
        if data.get("encoding") != "base64":
            return ""
        import base64
        return base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
