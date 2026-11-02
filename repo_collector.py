"""repo_collector.py - Scrape top & trending GitHub repositories."""
import requests
import time
from typing import List, Dict
from bs4 import BeautifulSoup

GITHUB_API = "https://api.github.com"

# Categories with search queries
CATEGORIES = {
    "web_frontend": "topic:frontend stars:>1000 language:javascript OR language:typescript",
    "web_backend": "topic:backend stars:>1000 language:python OR language:javascript OR language:go",
    "cli_tools": "topic:cli stars:>500",
    "ml_ai": "topic:machine-learning stars:>2000",
    "devtools": "topic:developer-tools stars:>1000",
    "mobile": "topic:mobile stars:>1000",
    "games": "topic:game-engine stars:>500",
    "frameworks": "topic:framework stars:>5000",
    "utilities": "topic:utility stars:>1000",
    "educational": "topic:education stars:>500",
}


def fetch_trending_repos(language: str = "", since: str = "daily") -> List[Dict]:
    """Fetch trending repos from GitHub trending page."""
    repos = []
    
    url = f"https://github.com/trending/{language}?since={since}"
    
    try:
        res = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        if res.status_code != 200:
            print(f"  ❌ Failed to fetch trending: {res.status_code}")
            return repos
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Find repo rows
        articles = soup.find_all("article", class_="Box-row")
        
        for article in articles:
            try:
                # Extract repo name
                h2 = article.find("h2")
                if not h2:
                    continue
                
                link = h2.find("a")
                if not link:
                    continue
                
                full_name = link.get("href", "").strip("/")
                if not full_name or "/" not in full_name:
                    continue
                
                owner, name = full_name.split("/", 1)
                
                # Extract description
                desc = article.find("p", class_="col-9")
                description = desc.get_text(strip=True) if desc else ""
                
                # Extract language
                lang_span = article.find("span", itemprop="programmingLanguage")
                language_name = lang_span.get_text(strip=True) if lang_span else "Unknown"
                
                # Extract stars
                stars_link = article.find("a", href=lambda x: x and "stargazers" in x if x else False)
                stars = 0
                if stars_link:
                    stars_text = stars_link.get_text(strip=True).replace(",", "")
                    try:
                        stars = int(stars_text)
                    except:
                        stars = 0
                
                repos.append({
                    "name": name,
                    "full_name": full_name,
                    "owner": owner,
                    "stars": stars,
                    "forks": 0,
                    "language": language_name,
                    "description": description,
                    "html_url": f"https://github.com/{full_name}",
                    "clone_url": f"https://github.com/{full_name}.git",
                    "category": "trending",
                    "has_wiki": False,
                    "has_pages": False,
                    "license": None,
                    "topics": ["trending"],
                })
                
            except Exception as e:
                continue
        
        print(f"  ✅ Trending ({language or 'all'}): fetched {len(repos)} repos")
        
    except Exception as e:
        print(f"  ❌ Exception in trending: {e}")
    
    return repos


def fetch_top_repos(category: str, query: str, per_page: int = 100, max_pages: int = 3) -> List[Dict]:
    """Fetch top repos for a category."""
    repos = []
    
    for page in range(1, max_pages + 1):
        url = f"{GITHUB_API}/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }
        
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 403:
                print(f"  ⚠️ Rate limited on {category}, waiting 60s...")
                time.sleep(60)
                continue
            if res.status_code != 200:
                print(f"  ❌ Error fetching {category}: {res.status_code}")
                break
            
            data = res.json()
            items = data.get("items", [])
            if not items:
                break
            
            for item in items:
                repos.append({
                    "name": item["name"],
                    "full_name": item["full_name"],
                    "owner": item["owner"]["login"],
                    "stars": item["stargazers_count"],
                    "forks": item["forks_count"],
                    "language": item.get("language", "Unknown"),
                    "description": item.get("description", ""),
                    "html_url": item["html_url"],
                    "clone_url": item["clone_url"],
                    "category": category,
                    "has_wiki": item.get("has_wiki", False),
                    "has_pages": item.get("has_pages", False),
                    "license": item.get("license", {}).get("name") if item.get("license") else None,
                    "topics": item.get("topics", []),
                })
            
            print(f"  ✅ {category}: fetched {len(items)} repos (page {page})")
            time.sleep(6)
            
        except Exception as e:
            print(f"  ❌ Exception in {category}: {e}")
            break
    
    return repos


def collect_all_repos(target_per_category: int = 100, include_trending: bool = True) -> List[Dict]:
    """Collect repos from all categories + trending."""
    all_repos = []
    per_page = min(target_per_category, 100)
    max_pages = (target_per_category + 99) // 100
    
    print(f"🚀 Collecting top & trending repos from GitHub...")
    print(f"   Target: {target_per_category} per category × {len(CATEGORIES)} categories")
    if include_trending:
        print(f"   Plus: Trending repos (daily, weekly, monthly)")
    print()
    
    # Collect trending repos
    if include_trending:
        print(f"🔥 Category: trending")
        for lang in ["", "python", "javascript", "typescript", "go", "rust"]:
            for since in ["daily", "weekly"]:
                trending = fetch_trending_repos(language=lang, since=since)
                all_repos.extend(trending)
                time.sleep(2)
        print()
    
    # Collect category repos
    for category, query in CATEGORIES.items():
        print(f"📦 Category: {category}")
        repos = fetch_top_repos(category, query, per_page=per_page, max_pages=max_pages)
        all_repos.extend(repos)
        print()
    
    # Deduplicate
    seen = set()
    unique = []
    for r in all_repos:
        if r["full_name"] not in seen:
            seen.add(r["full_name"])
            unique.append(r)
    
    print(f"✅ Total unique repos collected: {len(unique)}")
    return unique