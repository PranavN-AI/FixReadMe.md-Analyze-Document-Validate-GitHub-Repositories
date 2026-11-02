"""build_dataset.py - Build the best-repos knowledge base (with checkpoint + resume)."""
import argparse
import json
import os
import time
from datetime import datetime

from repo_collector import collect_all_repos
from repo_analyzer import analyze_readme, fetch_readme
from scorer import score_readme

DATASET_FILE = os.path.join("data", "best_repos.json")


def process_repo(repo):
    content = fetch_readme(repo["owner"], repo["name"])
    if not content:
        return None
    analysis = analyze_readme(content)
    scores = score_readme(analysis["features"], analysis["metrics"])
    return {
        "repo": repo,
        "features": analysis["features"],
        "metrics": analysis["metrics"],
        "scores": scores,
        "readme_preview": content[:2000],
        "readme_length": len(content),
        "processed_at": datetime.now().isoformat(),
    }


def save_partial(processed):
    os.makedirs("data", exist_ok=True)
    with open(DATASET_FILE, "w", encoding="utf-8") as fh:
        json.dump({"metadata": {"partial": True}, "repos": processed}, fh, ensure_ascii=False)


def build_dataset(target_per_category=100, resume=False):
    os.makedirs("data", exist_ok=True)
    repos = collect_all_repos(target_per_category=target_per_category)

    done = set()
    if resume and os.path.exists(DATASET_FILE):
        try:
            with open(DATASET_FILE, encoding="utf-8") as fh:
                old = json.load(fh).get("repos", [])
            done = {r["repo"]["full_name"] for r in old}
            print(f"⏩ Resuming — skipping {len(done)} already-processed repos")
        except Exception:
            done = set()

    print(f"\n🔍 Processing {len(repos)} repositories...\n" + "=" * 60)
    processed, failed = [], 0

    for i, repo in enumerate(repos, 1):
        if repo["full_name"] in done:
            continue
        print(f"[{i}/{len(repos)}] {repo['full_name']}...", end=" ")
        try:
            result = process_repo(repo)
            if result:
                processed.append(result)
                print(f"✅ {result['scores']['total']}/100 ({result['scores']['grade']})")
                if len(processed) % 25 == 0:
                    save_partial(processed)
                    print(f"   💾 Checkpoint saved ({len(processed)} repos)")
            else:
                failed += 1
                print("⚠️ no README")
        except Exception as e:
            failed += 1
            print(f"❌ {e}")
        time.sleep(0.5)

    processed.sort(key=lambda x: x["scores"]["total"], reverse=True)

    if not processed:
        print("❌ Nothing processed. Check your GITHUB_TOKEN / internet.")
        return None

    scores = [r["scores"]["total"] for r in processed]
    stats = {
        "total_processed": len(processed),
        "total_failed": failed,
        "average_score": round(sum(scores) / len(scores), 2),
        "best_score": max(scores),
        "worst_score": min(scores),
        "median_score": sorted(scores)[len(scores) // 2],
        "grade_distribution": {},
        "built_at": datetime.now().isoformat(),
    }
    for r in processed:
        g = r["scores"]["grade"]
        stats["grade_distribution"][g] = stats["grade_distribution"].get(g, 0) + 1

    with open(DATASET_FILE, "w", encoding="utf-8") as fh:
        json.dump({"metadata": stats, "repos": processed}, fh, ensure_ascii=False)

    print("\n" + "=" * 60 + "\n📊 DATASET SUMMARY\n" + "=" * 60)
    print(f"  Processed: {stats['total_processed']}   Failed: {stats['total_failed']}")
    print(f"  AVERAGE score: {stats['average_score']}/100")
    print(f"  BEST score:    {stats['best_score']}/100")
    print(f"  WORST score:   {stats['worst_score']}/100")
    print(f"  Median score:  {stats['median_score']}/100")
    print("  Grades: " + "  ".join(f"{g}:{c}" for g, c in sorted(stats["grade_distribution"].items())))
    print("\n  Top 5:")
    for r in processed[:5]:
        print(f"    • {r['repo']['full_name']} — {r['scores']['total']}/100 ({r['scores']['grade']})")
    print("  Bottom 5:")
    for r in processed[-5:]:
        print(f"    • {r['repo']['full_name']} — {r['scores']['total']}/100 ({r['scores']['grade']})")
    print(f"\n✅ Saved: {DATASET_FILE} ({os.path.getsize(DATASET_FILE)/1024:.1f} KB)")
    return {"metadata": stats, "repos": processed}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build best-repos dataset")
    ap.add_argument("--target", type=int, default=100, help="repos per category")
    ap.add_argument("--resume", action="store_true", help="skip already-processed repos")
    args = ap.parse_args()
    build_dataset(target_per_category=args.target, resume=args.resume)