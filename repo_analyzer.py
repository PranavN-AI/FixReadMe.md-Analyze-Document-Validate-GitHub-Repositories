"""repo_analyzer.py - Extract 100+ features from README content."""
import re
import requests
from typing import Dict, List
import base64


def fetch_readme(owner: str, repo: str) -> str:
    """Fetch README content from GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            content = res.json().get("content", "")
            return base64.b64decode(content).decode("utf-8", errors="ignore")
    except Exception:
        pass
    return ""


def analyze_readme(content: str) -> Dict:
    """Analyze README and extract 100+ features."""
    if not content:
        return {"features": {}, "metrics": {}}
    
    content_lower = content.lower()
    features = {}
    metrics = {}
    
    # ===== STRUCTURAL FEATURES (0-25) =====
    h1_count = len(re.findall(r"^# ", content, re.MULTILINE))
    h2_count = len(re.findall(r"^## ", content, re.MULTILINE))
    h3_count = len(re.findall(r"^### ", content, re.MULTILINE))
    h4_count = len(re.findall(r"^#### ", content, re.MULTILINE))
    
    features["has_h1"] = h1_count > 0
    features["has_h2"] = h2_count > 0
    features["has_h3"] = h3_count > 0
    features["has_h4"] = h4_count > 0
    features["has_multiple_h2"] = h2_count > 3
    features["has_multiple_h3"] = h3_count > 5
    
    metrics["h1_count"] = h1_count
    metrics["h2_count"] = h2_count
    metrics["h3_count"] = h3_count
    metrics["h4_count"] = h4_count
    metrics["heading_count"] = h1_count + h2_count + h3_count + h4_count
    
    # Tables
    table_count = len(re.findall(r"\|.*\|", content))
    features["has_tables"] = table_count > 5
    features["has_multiple_tables"] = table_count > 15
    metrics["table_count"] = table_count
    
    # Lists
    bullet_count = len(re.findall(r"^[-*+]\s", content, re.MULTILINE))
    numbered_count = len(re.findall(r"^\d+\.\s", content, re.MULTILINE))
    features["has_bullets"] = bullet_count > 5
    features["has_numbered_lists"] = numbered_count > 3
    features["has_many_bullets"] = bullet_count > 20
    metrics["bullet_count"] = bullet_count
    metrics["numbered_count"] = numbered_count
    
    # Code blocks
    code_blocks = re.findall(r"```[\s\S]*?```", content)
    features["has_code_examples"] = len(code_blocks) > 0
    features["has_many_code_blocks"] = len(code_blocks) > 5
    features["has_bash_examples"] = bool(re.search(r"```bash", content))
    features["has_python_examples"] = bool(re.search(r"```python", content))
    features["has_javascript_examples"] = bool(re.search(r"```javascript", content))
    features["has_json_examples"] = bool(re.search(r"```json", content))
    features["has_yaml_examples"] = bool(re.search(r"```yaml", content))
    metrics["code_block_count"] = len(code_blocks)
    
    # Links
    link_count = len(re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content))
    features["has_links"] = link_count > 5
    features["has_many_links"] = link_count > 20
    features["has_external_links"] = bool(re.search(r"\]\(https?://", content))
    features["has_github_links"] = bool(re.search(r"\]\(https?://github\.com", content))
    features["has_docs_links"] = bool(re.search(r"\]\(https?://\S*docs", content))
    metrics["link_count"] = link_count
    
    # Images/GIFs/Videos
    img_count = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", content))
    features["has_images"] = img_count > 0
    features["has_many_images"] = img_count > 3
    features["has_gifs"] = bool(re.search(r"\.gif", content, re.I))
    features["has_screenshots"] = bool(re.search(r"(screenshot|demo).*\.(png|jpg|gif)", content, re.I))
    features["has_youtube_links"] = bool(re.search(r"youtube\.com|youtu\.be", content, re.I))
    metrics["image_count"] = img_count
    
    # ===== CONTENT SECTIONS (0-30) =====
    # Installation & Setup
    features["has_installation"] = bool(re.search(r"(installation|getting started|setup|install)", content_lower))
    features["has_quick_start"] = bool(re.search(r"quick\s*start", content_lower))
    features["has_prerequisites"] = bool(re.search(r"(prerequisites?|requirements|dependencies)", content_lower))
    features["has_docker_instructions"] = bool(re.search(r"docker", content_lower))
    features["has_env_setup"] = bool(re.search(r"(\.env|environment|env\s*variables?)", content_lower))
    
    # Usage & Examples
    features["has_usage"] = bool(re.search(r"(usage|how to use|examples?)", content_lower))
    features["has_basic_example"] = bool(re.search(r"basic\s*example|simple\s*example", content_lower))
    features["has_advanced_example"] = bool(re.search(r"advanced\s*example|complex\s*example", content_lower))
    features["has_multiple_examples"] = len(re.findall(r"example", content_lower)) > 3
    
    # API & Documentation
    features["has_api_docs"] = bool(re.search(r"(api|endpoint|routes?)", content_lower))
    features["has_endpoint_list"] = bool(re.search(r"(get|post|put|delete)\s+/", content_lower))
    features["has_parameters"] = bool(re.search(r"(parameters?|params?|arguments?)", content_lower))
    features["has_response_format"] = bool(re.search(r"(response|returns?|output)", content_lower))
    features["has_error_handling"] = bool(re.search(r"(error|exception|troubleshoot)", content_lower))
    
    # Configuration
    features["has_configuration"] = bool(re.search(r"(config|configuration|settings)", content_lower))
    features["has_env_vars"] = bool(re.search(r"(env|environment)\s*variable", content_lower))
    features["has_config_file"] = bool(re.search(r"(\.env|config\.json|settings\.yaml)", content_lower))
    
    # Community & Support
    features["has_contributing"] = bool(re.search(r"contributing", content_lower))
    features["has_code_of_conduct"] = bool(re.search(r"code\s*of\s*conduct", content_lower))
    features["has_license_section"] = bool(re.search(r"license", content_lower))
    features["has_changelog"] = bool(re.search(r"changelog", content_lower))
    features["has_roadmap"] = bool(re.search(r"roadmap", content_lower))
    features["has_faq"] = bool(re.search(r"faq", content_lower))
    features["has_troubleshooting"] = bool(re.search(r"(troubleshooting|common\s*issues?)", content_lower))
    features["has_support"] = bool(re.search(r"(support|help|contact)", content_lower))
    features["has_discord"] = bool(re.search(r"discord", content_lower))
    features["has_slack"] = bool(re.search(r"slack", content_lower))
    
    # Architecture & Design
    features["has_architecture"] = bool(re.search(r"architecture", content_lower))
    features["has_design_decisions"] = bool(re.search(r"(design\s*decision|adr|why)", content_lower))
    features["has_flow_diagram"] = bool(re.search(r"(flow|diagram|workflow)", content_lower))
    features["has_system_overview"] = bool(re.search(r"(overview|system|architecture)", content_lower))
    
    # Navigation
    features["has_toc"] = bool(re.search(r"(table of contents|toc|contents)", content_lower))
    features["has_back_to_top"] = bool(re.search(r"back\s*to\s*top", content_lower))
    features["has_navigation"] = bool(re.search(r"(jump to|navigate|skip to)", content_lower))
    
    # Demo & Live
    features["has_demo"] = bool(re.search(r"(demo|live|preview|try it)", content_lower))
    features["has_live_link"] = bool(re.search(r"live\s*demo|deployed|hosted", content_lower))
    features["has_video_demo"] = bool(re.search(r"(video|screencast|tutorial)", content_lower))
    
    # Testing
    features["has_testing"] = bool(re.search(r"(testing|test|tests)", content_lower))
    features["has_test_commands"] = bool(re.search(r"(npm test|pytest|jest)", content_lower))
    features["has_coverage"] = bool(re.search(r"coverage", content_lower))
    
    # Deployment
    features["has_deployment"] = bool(re.search(r"(deploy|deployment|production)", content_lower))
    features["has_vercel"] = bool(re.search(r"vercel", content_lower))
    features["has_heroku"] = bool(re.search(r"heroku", content_lower))
    features["has_aws"] = bool(re.search(r"aws|amazon", content_lower))
    features["has_docker_compose"] = bool(re.search(r"docker\s*compose|docker-compose", content_lower))
    
    # ===== BADGES & VISUAL (0-20) =====
    shields_count = len(re.findall(r"shields\.io|img\.shields", content_lower))
    features["has_badges"] = shields_count > 0
    features["has_many_badges"] = shields_count > 5
    
    # Specific badge types
    features["has_ci_badge"] = bool(re.search(r"(build|ci|test).*pass", content_lower))
    features["has_version_badge"] = bool(re.search(r"version|v\d", content_lower))
    features["has_license_badge"] = bool(re.search(r"license.*badge|badge.*license", content_lower))
    features["has_coverage_badge"] = bool(re.search(r"coverage", content_lower))
    features["has_downloads_badge"] = bool(re.search(r"downloads?", content_lower))
    features["has_stars_badge"] = bool(re.search(r"stars?", content_lower))
    features["has_forks_badge"] = bool(re.search(r"forks?", content_lower))
    features["has_issues_badge"] = bool(re.search(r"issues?", content_lower))
    features["has_language_badge"] = bool(re.search(r"(python|javascript|typescript|java)", content_lower))
    
    metrics["badge_count"] = shields_count
    
    # Centered content
    features["has_centered_content"] = bool(re.search(r"align\s*=\s*['\"]center['\"]", content_lower))
    features["has_aligned_images"] = bool(re.search(r"align.*center.*img|img.*align.*center", content_lower))
    features["has_banner"] = bool(re.search(r"banner|hero|header", content_lower))
    
    # HTML formatting
    features["has_html_formatting"] = bool(re.search(r"<(?:p|div|img|table|br|hr)", content_lower))
    features["has_details_summary"] = bool(re.search(r"<details>|<summary>", content_lower))
    features["has_custom_html"] = bool(re.search(r"<(?:span|kbd|mark|small)", content_lower))
    
    # Blockquotes
    features["has_blockquotes"] = bool(re.search(r"^>\s", content, re.MULTILINE))
    features["has_note_boxes"] = bool(re.search(r">.*note|>.*important|>.*warning", content_lower))
    features["has_tip_boxes"] = bool(re.search(r">.*tip|>.*hint", content_lower))
    
    # Task lists
    features["has_task_lists"] = bool(re.search(r"-\s\[[ x]\]", content))
    features["has_checklist"] = bool(re.search(r"-\s\[x\]", content))
    
    # Emojis
    features["has_emojis"] = bool(re.search(r"[\U0001F300-\U0001F9FF]", content))
    features["has_many_emojis"] = len(re.findall(r"[\U0001F300-\U0001F9FF]", content)) > 10
    
    # Mermaid diagrams
    features["has_mermaid"] = bool(re.search(r"```mermaid", content))
    features["has_flowchart"] = bool(re.search(r"flowchart|graph", content_lower))
    features["has_sequence_diagram"] = bool(re.search(r"sequence", content_lower))
    
    # ===== PROFESSIONAL ELEMENTS (0-15) =====
    # Length metrics
    word_count = len(content.split())
    line_count = len(content.splitlines())
    char_count = len(content)
    
    features["has_substantial_content"] = word_count > 500
    features["has_comprehensive_docs"] = word_count > 1000
    features["has_extensive_docs"] = word_count > 2000
    
    metrics["word_count"] = word_count
    metrics["line_count"] = line_count
    metrics["char_count"] = char_count
    metrics["avg_line_length"] = char_count / max(line_count, 1)
    
    # Code density
    code_lines = sum(1 for block in code_blocks for line in block.split("\n"))
    features["has_code_heavy"] = code_lines > 50
    metrics["code_lines"] = code_lines
    metrics["code_to_text_ratio"] = code_lines / max(line_count, 1)
    
    # Link density
    features["has_rich_links"] = link_count > 10
    features["has_cross_references"] = bool(re.search(r"\]\(#", content))
    
    # Multi-language support
    features["has_multilang"] = bool(re.search(r"(chinese|spanish|french|german|japanese|korean)", content_lower))
    features["has_translation_links"] = bool(re.search(r"(🇨🇳|🇪🇸|🇫🇷|🇩🇪|🇯🇵|🇰🇷)", content))
    
    # Metadata
    features["has_version_info"] = bool(re.search(r"version|v\d+\.\d+", content_lower))
    features["has_author_info"] = bool(re.search(r"(author|maintainer|creator)", content_lower))
    features["has_date_info"] = bool(re.search(r"\d{4}-\d{2}-\d{2}|\d{4}", content))
    features["has_status_info"] = bool(re.search(r"(stable|beta|alpha|deprecated)", content_lower))
    
    # Citations & References
    features["has_citations"] = bool(re.search(r"(citation|reference|cite)", content_lower))
    features["has_footnotes"] = bool(re.search(r"\[\^[^\]]+\]", content))
    features["has_bibliography"] = bool(re.search(r"(bibliography|references?)", content_lower))
    
    # Accessibility
    features["has_alt_text"] = bool(re.search(r"!\[[^\]]+\]", content))
    features["has_descriptive_alt"] = len(re.findall(r"!\[[^\]]{10,}\]", content)) > 3
    
    # SEO-friendly
    features["has_meta_description"] = word_count > 100
    features["has_keywords"] = bool(re.search(r"(keyword|tag|topic)", content_lower))
    
    return {"features": features, "metrics": metrics}