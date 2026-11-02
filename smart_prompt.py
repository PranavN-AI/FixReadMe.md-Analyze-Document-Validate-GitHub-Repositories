"""smart_prompt.py - Match user project to best repos, enhance Groq prompt."""
import json
import os
from typing import Dict, List

DATASET_FILE = os.path.join("data", "best_repos.json")


def load_dataset():
    try:
        with open(DATASET_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None


def extract_repo_profile(metadata):
    return {
        "languages": set(metadata.get("languages", [])),
        "frameworks": {f.lower() for f in metadata.get("frameworks", [])},
        "category_hint": metadata.get("project_type", "").lower(),
    }


def calculate_similarity(profile, best_repo):
    score = 0.0
    repo = best_repo["repo"]
    topics = {t.lower() for t in repo.get("topics", [])}
    if repo.get("language") in profile["languages"]:
        score += 30
    score += min(25, len(profile["frameworks"] & topics) * 5)
    if profile["category_hint"] and any(profile["category_hint"].split()[0] in t for t in topics):
        score += 20
    score += min(15, len(profile["languages"] & {repo.get("language", "")}) * 5)
    score += min(10, best_repo["scores"]["total"] / 10)
    return score


def find_similar_repos(metadata, top_k=3):
    dataset = load_dataset()
    if not dataset:
        return []
    profile = extract_repo_profile(metadata)
    scored = [(calculate_similarity(profile, r), r) for r in dataset.get("repos", [])]
    scored.sort(key=lambda x: (x[0], x[1]["scores"]["total"]), reverse=True)
    return [r for _, r in scored[:top_k]]


def build_enhanced_prompt(metadata, tagline, description, features, top_k=3):
    similar = find_similar_repos(metadata, top_k=top_k)
    parts = ["You are an expert technical writer who creates world-class README files "
             "at the level of the top 1% of GitHub repositories."]

    if similar:
        parts.append("\n## REFERENCE EXAMPLES (top-scored repos similar to this project):\n")
        for i, item in enumerate(similar, 1):
            r, sc = item["repo"], item["scores"]
            top_feats = ", ".join(k for k, v in item["features"].items() if v and k.startswith("has_"))[:300]
            parts.append(
                f"### Example {i}: {r['full_name']} (⭐{r['stars']:,}, score {sc['total']}/100 grade {sc['grade']})\n"
                f"Key features: {top_feats}\nREADME excerpt:\n```markdown\n{item['readme_preview'][:800]}\n```\n")

    parts.append(f"""## YOUR TASK
Write a world-class README for:

**Project:** {metadata['project_name']} ({metadata['project_type']})
**Languages:** {', '.join(metadata['languages']) or 'unknown'}
**Frameworks:** {', '.join(metadata['frameworks']) or 'none'}
**Tagline:** {tagline}
**Description:** {description}
**Features:**
{chr(10).join(features)}

Requirements: match the quality of the reference examples; include shields.io badges,
Quick Start with copy-paste commands, Installation, Usage, Tech Stack table,
Table of Contents, Troubleshooting and Contributing sections.
Return ONLY the complete README.md in markdown.""")
    return "\n".join(parts)


def get_dataset_stats():
    dataset = load_dataset()
    return dataset["metadata"] if dataset else None


if __name__ == "__main__":
    stats = get_dataset_stats()
    if not stats:
        print("⚠️ No dataset yet. Run: python build_dataset.py --target 10")
    else:
        print("📊 Dataset Statistics:")
        print(f"  Repos: {stats['total_processed']}")
        print(f"  AVERAGE: {stats['average_score']}/100")
        print(f"  BEST:    {stats['best_score']}/100")
        print(f"  WORST:   {stats['worst_score']}/100")
        print("  Grades: " + "  ".join(f"{g}:{c}" for g, c in sorted(stats.get('grade_distribution', {}).items())))