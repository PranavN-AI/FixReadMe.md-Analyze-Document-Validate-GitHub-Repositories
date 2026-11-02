"""repo_analyzer.py - Extract 100+ README features."""
import os
import re
import base64
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
API_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


def fetch_readme(owner, repo):
    try:
        res = requests.get(f"https://api.github.com/repos/{owner}/{repo}/readme",
                           timeout=10, headers=API_HEADERS)
        if res.status_code == 200:
            return base64.b64decode(res.json().get("content", "")).decode("utf-8", errors="ignore")
    except Exception:
        pass
    return ""


def analyze_readme(content):
    if not content:
        return {"features": {}, "metrics": {}}
    cl = content.lower()
    f, m = {}, {}

    # structure
    m["h1_count"] = len(re.findall(r"^# ", content, re.M))
    m["h2_count"] = len(re.findall(r"^## ", content, re.M))
    m["h3_count"] = len(re.findall(r"^### ", content, re.M))
    m["heading_count"] = m["h1_count"] + m["h2_count"] + m["h3_count"]
    f["has_h1"] = m["h1_count"] > 0
    f["has_h2"] = m["h2_count"] > 0
    f["has_h3"] = m["h3_count"] > 0
    f["has_multiple_h2"] = m["h2_count"] > 3
    f["has_multiple_h3"] = m["h3_count"] > 5
    m["table_count"] = len(re.findall(r"^\|", content, re.M))
    f["has_tables"] = m["table_count"] > 4
    f["has_multiple_tables"] = m["table_count"] > 15
    m["bullet_count"] = len(re.findall(r"^[-*+] ", content, re.M))
    m["numbered_count"] = len(re.findall(r"^\d+\. ", content, re.M))
    f["has_bullets"] = m["bullet_count"] > 5
    f["has_numbered_lists"] = m["numbered_count"] > 3
    f["has_many_bullets"] = m["bullet_count"] > 20
    code_blocks = re.findall(r"```[\s\S]*?```", content)
    m["code_block_count"] = len(code_blocks)
    f["has_code_examples"] = m["code_block_count"] > 0
    f["has_many_code_blocks"] = m["code_block_count"] > 5
    f["has_bash_examples"] = "```bash" in content
    f["has_python_examples"] = "```python" in content
    f["has_javascript_examples"] = "```javascript" in content or "```js" in content
    f["has_json_examples"] = "```json" in content
    f["has_yaml_examples"] = "```yaml" in content
    m["link_count"] = len(re.findall(r"\[[^\]]+\]\([^)]+\)", content))
    f["has_links"] = m["link_count"] > 5
    f["has_many_links"] = m["link_count"] > 20
    f["has_external_links"] = bool(re.search(r"\]\(https?://", content))
    f["has_github_links"] = "](https://github.com" in content
    f["has_docs_links"] = bool(re.search(r"\]\(https?://\S*docs?", cl))
    m["image_count"] = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", content))
    f["has_images"] = m["image_count"] > 0
    f["has_many_images"] = m["image_count"] > 3
    f["has_gifs"] = ".gif" in cl
    f["has_screenshots"] = bool(re.search(r"screenshot|demo.*\.(png|jpg|gif)", cl))
    f["has_youtube_links"] = "youtube.com" in cl or "youtu.be" in cl

    # content sections
    f["has_installation"] = bool(re.search(r"install|setup|getting started", cl))
    f["has_quick_start"] = "quick start" in cl or "quickstart" in cl
    f["has_prerequisites"] = bool(re.search(r"prerequisit|requirement", cl))
    f["has_docker_instructions"] = "docker" in cl
    f["has_env_setup"] = bool(re.search(r"\.env|environment variable", cl))
    f["has_usage"] = bool(re.search(r"usage|how to use|example", cl))
    f["has_basic_example"] = "basic example" in cl or "simple example" in cl
    f["has_advanced_example"] = "advanced" in cl
    f["has_multiple_examples"] = cl.count("example") > 3
    f["has_api_docs"] = bool(re.search(r"\bapi\b|endpoint", cl))
    f["has_endpoint_list"] = bool(re.search(r"(get|post|put|delete) /", cl))
    f["has_parameters"] = bool(re.search(r"parameter|argument", cl))
    f["has_response_format"] = bool(re.search(r"response|returns?", cl))
    f["has_error_handling"] = bool(re.search(r"error|exception", cl))
    f["has_configuration"] = bool(re.search(r"config|settings?", cl))
    f["has_env_vars"] = "environment variable" in cl
    f["has_config_file"] = bool(re.search(r"\.env|config\.(json|yaml|yml|toml)", cl))
    f["has_contributing"] = "contributing" in cl
    f["has_code_of_conduct"] = "code of conduct" in cl
    f["has_license_section"] = "license" in cl
    f["has_changelog"] = "changelog" in cl
    f["has_roadmap"] = "roadmap" in cl
    f["has_faq"] = "faq" in cl
    f["has_troubleshooting"] = "troubleshoot" in cl or "common issues" in cl
    f["has_support"] = bool(re.search(r"support|contact", cl))
    f["has_discord"] = "discord" in cl
    f["has_slack"] = "slack" in cl
    f["has_architecture"] = "architecture" in cl
    f["has_design_decisions"] = "design decision" in cl
    f["has_flow_diagram"] = bool(re.search(r"diagram|flowchart", cl))
    f["has_system_overview"] = "overview" in cl
    f["has_toc"] = "table of contents" in cl or cl.count("](#") > 5
    f["has_back_to_top"] = "back to top" in cl
    f["has_navigation"] = bool(re.search(r"jump to|skip to", cl))
    f["has_demo"] = bool(re.search(r"\bdemo\b|live preview|try it", cl))
    f["has_live_link"] = bool(re.search(r"live demo|deployed|hosted", cl))
    f["has_video_demo"] = bool(re.search(r"video|screencast", cl))
    f["has_testing"] = bool(re.search(r"\btest", cl))
    f["has_test_commands"] = bool(re.search(r"npm test|pytest|jest|cargo test", cl))
    f["has_coverage"] = "coverage" in cl
    f["has_deployment"] = "deploy" in cl
    f["has_vercel"] = "vercel" in cl
    f["has_heroku"] = "heroku" in cl
    f["has_aws"] = "aws" in cl
    f["has_docker_compose"] = "docker-compose" in cl or "docker compose" in cl

    # badges & visual
    m["badge_count"] = len(re.findall(r"shields\.io|img\.shields", cl))
    f["has_badges"] = m["badge_count"] > 0
    f["has_many_badges"] = m["badge_count"] > 5
    f["has_ci_badge"] = bool(re.search(r"(build|ci|tests?).*(passing|status)", cl))
    f["has_version_badge"] = bool(re.search(r"version|release", cl))
    f["has_license_badge"] = bool(re.search(r"license.*shields|shields.*license", cl))
    f["has_coverage_badge"] = "coverage" in cl and m["badge_count"] > 0
    f["has_downloads_badge"] = "downloads" in cl and m["badge_count"] > 0
    f["has_stars_badge"] = "stars" in cl and m["badge_count"] > 0
    f["has_language_badge"] = m["badge_count"] > 0 and bool(re.search(r"python|javascript|typescript", cl))
    f["has_centered_content"] = 'align="center"' in cl or "align='center'" in cl
    f["has_aligned_images"] = f["has_centered_content"] and m["image_count"] > 0
    f["has_banner"] = bool(re.search(r"banner|hero", cl))
    f["has_html_formatting"] = bool(re.search(r"<(p|div|img|table|br|hr)\b", cl))
    f["has_details_summary"] = "<details>" in cl
    f["has_custom_html"] = bool(re.search(r"<(span|kbd|mark|small)\b", cl))
    f["has_blockquotes"] = bool(re.search(r"^> ", content, re.M))
    f["has_note_boxes"] = bool(re.search(r"^> *(note|important|warning)", cl, re.M))
    f["has_tip_boxes"] = bool(re.search(r"^> *(tip|hint)", cl, re.M))
    f["has_task_lists"] = bool(re.search(r"- \[[ x]\]", content))
    f["has_checklist"] = "- [x]" in content
    emoji_count = len(re.findall(r"[\U0001F300-\U0001FAFF]", content))
    f["has_emojis"] = emoji_count > 0
    f["has_many_emojis"] = emoji_count > 10
    f["has_mermaid"] = "```mermaid" in content
    f["has_flowchart"] = "flowchart" in cl or "graph td" in cl or "graph lr" in cl
    f["has_sequence_diagram"] = "sequence diagram" in cl

    # length & density
    m["word_count"] = len(content.split())
    m["line_count"] = len(content.splitlines())
    m["char_count"] = len(content)
    f["has_substantial_content"] = m["word_count"] > 500
    f["has_comprehensive_docs"] = m["word_count"] > 1000
    f["has_extensive_docs"] = m["word_count"] > 2000
    code_lines = sum(b.count("\n") for b in code_blocks)
    m["code_lines"] = code_lines
    f["has_code_heavy"] = code_lines > 50
    f["has_rich_links"] = m["link_count"] > 10
    f["has_cross_references"] = "](#" in content
    f["has_multilang"] = bool(re.search(r"中文|spanish|french|german|日本語|한국어", content))
    f["has_translation_links"] = bool(re.search(r"🇨|🇪|🇫🇷|🇩🇪|🇵|🇰🇷", content))
    f["has_version_info"] = bool(re.search(r"v?\d+\.\d+(\.\d+)?", content))
    f["has_author_info"] = bool(re.search(r"author|maintainer|created by", cl))
    f["has_status_info"] = bool(re.search(r"stable|beta|alpha|deprecated", cl))
    f["has_citations"] = bool(re.search(r"citation|cite", cl))
    f["has_footnotes"] = bool(re.search(r"\[\^", content))
    f["has_alt_text"] = bool(re.search(r"!\[[^\]]+\]", content))
    f["has_descriptive_alt"] = len(re.findall(r"!\[[^\]]{10,}\]", content)) > 2
    return {"features": f, "metrics": m}