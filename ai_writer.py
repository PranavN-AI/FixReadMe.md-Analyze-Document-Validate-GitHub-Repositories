"""ai_writer.py - LLM content writer with offline fallback."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("FIXREADME_MODEL", "llama-3.3-70b-versatile")


def _call_llm(prompt: str, max_tokens: int = 350):
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return None
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": MODEL, "temperature": 0.6, "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=20,
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except requests.RequestException:
        return None


def write_tagline_and_description(m: dict):
    prompt = f"""You write documentation for GitHub repositories.
Project name: {m['project_name']}
Type: {m['project_type']}
Languages: {', '.join(m['languages']) or 'unknown'}
Frameworks: {', '.join(m['frameworks']) or 'none'}
Key dependencies: {', '.join(m['dependencies'][:8]) or 'none'}
Folder snapshot:
{m['folder_tree'][:600]}

Return EXACTLY two lines, nothing else:
TAGLINE: one punchy sentence (max 14 words)
DESCRIPTION: professional 2-3 sentence paragraph explaining what it does and who it helps"""
    out = _call_llm(prompt)
    tagline, description = "", ""
    if out:
        for line in out.splitlines():
            up = line.upper()
            if up.startswith("TAGLINE:"):
                tagline = line.split(":", 1)[1].strip()
            elif up.startswith("DESCRIPTION:"):
                description = line.split(":", 1)[1].strip()
    if not tagline:
        tagline = "Analyze, document and validate code repositories in seconds."
    if not description:
        langs = ", ".join(m["languages"][:3]) or "modern tooling"
        description = (f"{m['project_name']} is a {m['project_type'].lower()} built with {langs}. "
                       "It solves a real-life workflow problem with a clean, maintainable "
                       "codebase and a developer-first experience.")
    return tagline, description


def write_features(m: dict):
    prompt = f"""List exactly 5 markdown bullet features for this project. Start each line with "- ".
Project: {m['project_name']} ({m['project_type']})
Languages: {', '.join(m['languages'])}
Frameworks: {', '.join(m['frameworks'])}
Capabilities detected: tests={m['has_tests']}, ci={m['has_ci']}, docker={m['has_docker']}, env_config={m['has_env_example']}"""
    out = _call_llm(prompt, max_tokens=200)
    if out:
        feats = [l.strip() for l in out.splitlines() if l.strip().startswith("- ")]
        if len(feats) >= 3:
            return feats[:6]
    feats = []
    if m["has_tests"]:
        feats.append("- 🧪 Automated test suite for reliability")
    if m["has_ci"]:
        feats.append("- 🔄 CI/CD workflows ready for GitHub Actions")
    if m["has_docker"]:
        feats.append("- 🐳 Containerized setup with Docker")
    if m["has_env_example"]:
        feats.append("- 🔐 Safe environment configuration template")
    for lang in m["languages"][:2]:
        feats.append(f"- 💻 Clean, idiomatic {lang} codebase")
    if m["frameworks"]:
        feats.append(f"- ⚙️ Powered by {', '.join(m['frameworks'][:2])}")
    return feats or ["- 🚀 Simple setup and developer-friendly workflow"]