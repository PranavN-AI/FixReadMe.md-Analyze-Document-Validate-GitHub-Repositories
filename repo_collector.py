"""repo_collector.py - Collect top + trending GitHub repos."""
import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
API_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
GITHUB_API = "https://api.github.com"

CATEGORIES = {
    "web_frontend": "topic:frontend stars:>1000",
    "web_backend": "topic:backend stars:>1000",
    "cli_tools": "topic:cli stars:>500",
    "ml_ai": "topic:machine-learning stars:>2000",
    "devtools": "topic:developer-tools stars:>1000",
    "mobile": "topic:mobile stars:>1000",
    "frameworks": "topic:framework stars:>5000",
    "utilities": "topic:utility stars:>1000",
    "educational": "topic:education stars:>500",
    "databases": "topic:database stars:>1000",
}


def fetch_trending_repos(language="", since="daily"):
    repos = []
    url = f"https://github.com/trending/{language}?since={since}"
    try:
        res = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        if res.status_code != 200:
            return repos
        soup = BeautifulSoup(res.text, "html.parser")
        for article in soup.find_all("article", class_="Box-row"):
            h2 = article.find("h2")
            link = h2.find("a") if h2 else None
            if not link:
                continue
            full_name = link.get("href", "").strip("/")
            if not full_name or "/" not in full_name:
                continue
            owner, name = full_name.split("/", 1)
            desc_el = article.find("p")
            lang_el = article.find("span", itemprop="programmingLanguage")
            stars_el = article.find("a", href=lambda h: h and "/stargazers" in h)
            stars = 0
            if stars_el:
                try:
                    stars = int(stars_el.get_text(strip=True).replace(",", ""))
                except ValueError:
                    stars = 0
            repos.append({
                "name": name, "full_name": full_name, "owner": owner,
                "stars": stars, "forks": 0,
                "language": lang_el.get_text(strip=True) if lang_el else "Unknown",
                "description": desc_el.get_text(strip=True) if desc_el else "",
                "html_url": f"https://github.com/{full_name}",
                "clone_url": f"https://github.com/{full_name}.git",
                "category": "trending", "has_wiki": False, "has_pages": False,
                "license": None, "topics": ["trending"],
            })
        print(f"  ✅ trending/{language or 'all'}/{since}: {len(repos)} repos")
    except Exception as e:
        print(f"  ❌ trending error: {e}")
    return repos


def fetch_top_repos(category, query, per_page=100, max_pages=3):
    repos = []
    for page in range(1, max_pages + 1):
        try:
            res = requests.get(f"{GITHUB_API}/search/repositories",
                               params={"q": query, "sort": "stars", "order": "desc",
                                       "per_page": per_page, "page": page},
                               timeout=15, headers=API_HEADERS)
            if res.status_code == 403:
                print("  ⚠️ rate limited, sleeping 60s...")
                time.sleep(60)
                continue
            if res.status_code != 200:
                break
            items = res.json().get("items", [])
            if not items:
                break
            for it in items:
                repos.append({
                    "name": it["name"], "full_name": it["full_name"],
                    "owner": it["owner"]["login"], "stars": it["stargazers_count"],
                    "forks": it["forks_count"], "language": it.get("language") or "Unknown",
                    "description": it.get("description") or "", "html_url": it["html_url"],
                    "clone_url": it["clone_url"], "category": category,
                    "has_wiki": it.get("has_wiki", False), "has_pages": it.get("has_pages", False),
                    "license": (it.get("license") or {}).get("name"),
                    "topics": it.get("topics", []),
                })
            print(f"  ✅ {category} page {page}: {len(items)} repos")
            time.sleep(2 if GITHUB_TOKEN else 6)
        except Exception as e:
            print(f"  ❌ {category} error: {e}")
            break
    return repos


def collect_all_repos(target_per_category=100, include_trending=True):
    all_repos = []
    per_page = min(target_per_category, 100)
    max_pages = max(1, (target_per_category + 99) // 100)
    print("🚀 Collecting repos (top + trending)...")
    if include_trending:
        print("🔥 trending:")
        for lang in ["", "python", "javascript", "typescript", "go", "rust"]:
            for since in ["daily", "weekly"]:
                all_repos.extend(fetch_trending_repos(lang, since))
                time.sleep(1)
    for category, query in CATEGORIES.items():
        print(f"📦 {category}:")
        all_repos.extend(fetch_top_repos(category, query, per_page, max_pages))
    seen, unique = set(), []
    for r in all_repos:
        if r["full_name"] not in seen:
            seen.add(r["full_name"])
            unique.append(r)
    print(f"✅ Unique repos collected: {len(unique)}")
    return unique