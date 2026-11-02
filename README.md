# FixReadMe.md

FixReadMe.md analyzes a GitHub repository and creates an evidence-based `README.md`. It detects languages, frameworks, dependencies, entry points, routes, tests, and license information, then returns the generated Markdown with validation findings and a quality score.

## Run locally

Create or activate the included virtual environment, then install the backend dependencies:

```powershell
python -m pip install -r backend/requirements.txt
```

Start the API with the supported command:

```powershell
python -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
```

In another terminal, serve the frontend:

```powershell
python -m http.server 5500 --directory frontend
```

Open <http://127.0.0.1:5500>. Paste a public GitHub URL, select **Analyze & Create README**, and use the Preview, Code, Copy Markdown, or Download README.md controls.

## Configuration

The backend reads `GITHUB_TOKEN` from the root `.env` when available. A token is optional for public repositories but increases GitHub API rate limits. Secrets remain server-side and are never sent to the browser.

## API

- `GET /health` checks that the API is running.
- `POST /api/analyze` accepts `{ "repository_url": "https://github.com/owner/repository" }` and returns repository metadata, extracted analysis, generated Markdown, validation findings, and scoring.

## Tests

```powershell
python -m pytest -q
```
