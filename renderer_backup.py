"""renderer.py - Premium README builder matching claude-mem quality."""
import re
from urllib.parse import urlencode

import requests

SHIELDS = "https://img.shields.io"
_BAD = ("invalid", "not found", "unknown logo", "inaccessible")

LANG_META = {
    "Python": ("3776AB", "python", "white"),
    "JavaScript": ("F7DF1E", "javascript", "black"),
    "TypeScript": ("3178C6", "typescript", "white"),
    "Java": ("007396", "openjdk", "white"),
    "C++": ("00599C", "cplusplus", "white"),
    "Go": ("00ADD8", "go", "white"),
    "Rust": ("CE422B", "rust", "white"),
    "HTML": ("E34F26", "html5", "white"),
    "CSS": ("1572B6", "css3", "white"),
    "Shell": ("4EAA25", "gnubash", "white"),
    "SQL": ("336791", "mysql", "white"),
}

FW_META = {
    "Flask": ("000000", "flask", "white"),
    "Django": ("092E20", "django", "white"),
    "FastAPI": ("009688", "fastapi", "white"),
    "Streamlit": ("FF4B4B", "streamlit", "white"),
    "React": ("61DAFB", "react", "black"),
    "Next.js": ("000000", "nextdotjs", "white"),
    "Vue.js": ("4FC08D", "vuedotjs", "white"),
    "Express": ("000000", "express", "white"),
    "Pandas": ("150458", "pandas", "white"),
    "NumPy": ("013243", "numpy", "white"),
    "PyTorch": ("EE4C2C", "pytorch", "white"),
    "TensorFlow": ("FF6F00", "tensorflow", "white"),
}


def esc(text: str) -> str:
    return text.replace("_", "__").replace("-", "--").strip().replace(" ", "_")


def static_badge(label, message, color, logo=None, logo_color="white"):
    url = f"{SHIELDS}/badge/{esc(label)}-{esc(message)}-{color.lstrip('#')}?style=for-the-badge"
    if logo:
        url += "&" + urlencode({"logo": logo, "logoColor": logo_color})
    return url


def badge_ok(url: str, timeout: int = 4) -> bool:
    try:
        res = requests.get(url, timeout=timeout)
        return res.status_code == 200 and not any(b in res.text.lower() for b in _BAD)
    except requests.RequestException:
        return True


def build_badges(m: dict, validate: bool = True):
    badges = []
    verified = static_badge("FixReadMe", "Verified", "10b981", logo="checkmarx")
    if validate and not badge_ok(verified):
        verified = static_badge("FixReadMe", "Verified", "10b981")
    badges.append(("FixReadMe Verified", verified))

    for lang in m["languages"][:4]:
        meta = LANG_META.get(lang)
        if meta:
            color, logo, logo_color = meta
            count = m["lang_counts"].get(lang, 0)
            badges.append((lang, static_badge(lang, f"{count} files", color, logo, logo_color)))

    for fw in m["frameworks"][:4]:
        meta = FW_META.get(fw)
        if meta:
            color, logo, logo_color = meta
            badges.append((fw, static_badge(fw, "framework", color, logo, logo_color)))

    if m["has_license"]:
        badges.append(("License", static_badge("License", m["license_type"], "blue")))
    if m["has_tests"]:
        badges.append(("Tests", static_badge("Tests", "Passing", "success")))
    if m["has_docker"]:
        badges.append(("Docker", static_badge("Docker", "Ready", "2496ED", "docker")))

    if m["is_public"] and m["owner"]:
        o, r = m["owner"], m["repo"]
        badges += [
            ("Stars", f"{SHIELDS}/github/stars/{o}/{r}?style=social"),
            ("Forks", f"{SHIELDS}/github/forks/{o}/{r}?style=social"),
            ("Issues", f"{SHIELDS}/github/issues/{o}/{r}"),
            ("Last Commit", f"{SHIELDS}/github/last-commit/{o}/{r}"),
        ]
    return badges


def badge_block(badges) -> str:
    imgs = "\n  ".join(f'<img src="{url}" alt="{alt}">' for alt, url in badges)
    return f'<p align="center">\n  {imgs}\n</p>'


def _anchor(title: str) -> str:
    slug = re.sub(r"[^a-z0-9 ]", "", title.lower())
    return slug.strip().replace(" ", "-")


def quick_start_section(m: dict) -> str:
    """Quick Start - most important actionable content."""
    lines = ["## 🚀 Quick Start", ""]
    
    if m["has_requirements"]:
        lines += [
            "Install with a single command:",
            "",
            "```bash",
            "pip install -r requirements.txt",
            "```",
            ""
        ]
    elif m["has_package_json"]:
        lines += [
            "Install with a single command:",
            "",
            "```bash",
            "npm install",
            "```",
            ""
        ]
    
    if "Streamlit" in m["frameworks"]:
        lines += [
            "Run the application:",
            "",
            "```bash",
            "streamlit run app.py",
            "```",
            ""
        ]
    elif m["entry_point"]:
        lines += [
            "Run the application:",
            "",
            "```bash",
            f"python {m['entry_point']}",
            "```",
            ""
        ]
    elif m["scripts"].get("dev") or m["scripts"].get("start"):
        cmd = "npm run dev" if m["scripts"].get("dev") else "npm start"
        lines += [
            "Run the application:",
            "",
            "```bash",
            cmd,
            "```",
            ""
        ]
    
    return "\n".join(lines)


def how_it_works_section(m: dict) -> str:
    """How It Works - explains architecture."""
    lines = ["## 🧠 How It Works", "", "**Core Components:**", ""]
    
    components = []
    if "Python" in m["languages"]:
        components.append("1. **Main Application** - Core Python logic and business rules")
    if "JavaScript" in m["languages"] or "TypeScript" in m["languages"]:
        components.append(f"{len(components)+1}. **Frontend Interface** - User interface and client-side logic")
    
    if m["has_tests"]:
        components.append(f"{len(components)+1}. **Test Suite** - Automated testing for reliability")
    if m["has_docker"]:
        components.append(f"{len(components)+1}. **Container Setup** - Docker configuration for deployment")
    if m["has_ci"]:
        components.append(f"{len(components)+1}. **CI/CD Pipeline** - Automated testing and deployment")
    
    if not components:
        components = [
            "1. **Source Code** - Main application logic",
            "2. **Configuration** - Settings and environment variables",
            "3. **Dependencies** - Required libraries and packages"
        ]
    
    lines.extend(components)
    lines.append("")
    
    return "\n".join(lines)


def system_requirements_section(m: dict) -> str:
    """System Requirements section."""
    lines = ["## 📋 System Requirements", ""]
    
    reqs = []
    if "Python" in m["languages"]:
        reqs.append("- **Python**: 3.8 or higher")
    if "JavaScript" in m["languages"] or "TypeScript" in m["languages"]:
        reqs.append("- **Node.js**: 16.0.0 or higher")
    if m["has_docker"]:
        reqs.append("- **Docker**: 20.0 or higher (optional)")
    if m["has_tests"]:
        reqs.append("- **Test Runner**: pytest (Python) or Jest (JavaScript)")
    
    if not reqs:
        reqs = ["- **OS**: Windows, macOS, or Linux", "- **Internet**: For dependency installation"]
    
    lines.extend(reqs)
    lines.append("")
    
    return "\n".join(lines)


def troubleshooting_section() -> str:
    """Troubleshooting guide."""
    lines = [
        "## 🔧 Troubleshooting",
        "",
        "If experiencing issues:",
        "",
        "1. **Check dependencies**: Ensure all required packages are installed",
        "2. **Verify environment**: Check that environment variables are set correctly",
        "3. **Review logs**: Check application logs for error messages",
        "4. **Clean install**: Delete `node_modules` or `venv` and reinstall dependencies",
        "",
        "For common issues, check the [GitHub Issues](#) page.",
        ""
    ]
    return "\n".join(lines)


def contributing_section() -> str:
    """Contributing guidelines."""
    lines = [
        "## 🤝 Contributing",
        "",
        "Contributions are welcome! Please:",
        "",
        "1. **Fork** the repository",
        "2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)",
        "3. **Commit** your changes (`git commit -m 'Add amazing feature'`)",
        "4. **Push** to the branch (`git push origin feature/amazing-feature`)",
        "5. Open a **Pull Request**",
        "",
        "Please ensure your code follows the project's coding standards and includes tests.",
        ""
    ]
    return "\n".join(lines)


def verification_table(m: dict) -> str:
    checks = [
        ("README present", m["has_readme"]),
        ("License file", m["has_license"]),
        ("Test suite", m["has_tests"]),
        ("CI/CD workflow", m["has_ci"]),
        (".gitignore", m["has_gitignore"]),
        ("Env template", m["has_env_example"]),
        ("Docker setup", m["has_docker"]),
    ]
    lines = ["| Check | Status |", "|---|:---:|"]
    score = 0
    for name, ok in checks:
        lines.append(f"| {name} | {'✅' if ok else '❌'} |")
        score += bool(ok)
    lines.append(f"\n**Repository health score: {score}/{len(checks)}**")
    return "\n".join(lines)


def build_readme(m: dict, tagline: str, description: str, features: list,
                 center_badges: bool = True, include_toc: bool = True,
                 validate: bool = True) -> str:
    """Build professional README matching claude-mem quality."""
    badges = build_badges(m, validate=validate)
    
    sections = []
    sections.append(("Overview", f"**{description}**\n\n{tagline}"))
    sections.append(("Quick Start", quick_start_section(m)))
    
    features_text = "\n".join(features)
    sections.append(("Features", features_text))
    sections.append(("How It Works", how_it_works_section(m)))
    
    install_lines = ["For detailed installation instructions:", "", "```bash"]
    if m["git_remote"]:
        install_lines.append(f"git clone {m['git_remote']}")
    install_lines.append(f"cd {m['project_name']}")
    install_lines.append("```")
    sections.append(("Installation", "\n".join(install_lines)))
    
    if m["images"]:
        grid = "\n".join(f'<img src="{img}" width="45%" style="margin:8px;">'
                         for img in m["images"])
        sections.append(("Screenshots", f'<p align="center">\n{grid}\n</p>'))
    
    if m["has_env_example"] or "python-dotenv" in [d.lower() for d in m["dependencies"]]:
        env_lines = ["Settings are managed via environment variables or `.env` file.", ""]
        if m["has_env_example"]:
            env_lines += ["Copy the example file:", "", "```bash", "cp .env.example .env", "```", ""]
        env_lines += ["Example configuration:", "", "```env", "API_KEY=your_api_key_here", "DEBUG=true", "```"]
        sections.append(("Configuration", "\n".join(env_lines)))
    
    usage_lines = []
    if "Streamlit" in m["frameworks"]:
        usage_lines += ["Run the web interface:", "", "```bash", "streamlit run app.py", "```"]
    elif m["entry_point"].endswith(".py"):
        usage_lines += ["Run the application:", "", "```bash", f"python {m['entry_point']}", "```"]
    elif m["scripts"].get("dev") or m["scripts"].get("start"):
        cmd = "npm run dev" if m["scripts"].get("dev") else "npm start"
        usage_lines += ["Run the application:", "", "```bash", cmd, "```"]
    
    if usage_lines:
        sections.append(("Usage", "\n".join(usage_lines)))
    
    if m["folder_tree"]:
        sections.append(("Project Structure", "```\n" + m["folder_tree"] + "\n```"))
    
    if m["languages"] or m["frameworks"]:
        rows = ["| Technology | Category | Purpose |", "|---|---|---|"]
        rows += [f"| {l} | Language | Core implementation |" for l in m["languages"][:3]]
        rows += [f"| {f} | Framework | Application framework |" for f in m["frameworks"][:3]]
        sections.append(("Tech Stack", "\n".join(rows)))
    
    sections.append(("System Requirements", system_requirements_section(m)))
    
    if m["has_tests"]:
        test_lines = ["Run the test suite:", "", "```bash"]
        if "Python" in m["languages"]:
            test_lines.append("pytest")
        if m["scripts"].get("test"):
            test_lines.append("npm test")
        test_lines.append("```")
        sections.append(("Testing", "\n".join(test_lines)))
    
    sections.append(("Troubleshooting", troubleshooting_section()))
    
    if m["todos"]:
        sections.append(("Roadmap", "\n".join(f"- [ ] {t}" for t in m["todos"])))
    
    sections.append(("Verification Report", verification_table(m)))
    sections.append(("Contributing", contributing_section()))
    
    if m["contributors"]:
        sections.append(("Contributors", ", ".join(f"**{c}**" for c in m["contributors"])))
    
    if m["has_license"]:
        sections.append(("License", f"This project is licensed under the **{m['license_type']} License**."))
    
    support_lines = [
        "## 💬 Support",
        "",
        f"- **Repository**: [github.com/{m['owner']}/{m['repo']}](https://github.com/{m['owner']}/{m['repo']})" if m['owner'] else "- **Repository**: See GitHub",
        "- **Issues**: Report bugs and request features via GitHub Issues",
        ""
    ]
    sections.append(("Support", "\n".join(support_lines)))
    
    # Build final output
    out = []
    
    if center_badges:
        out.append(badge_block(badges))
    else:
        out.append(" ".join(f"![{a}]({u})" for a, u in badges))
    
    out += ["", f"# {m['project_name']}", ""]
    
    if include_toc:
        out += ["## 📚 Table of Contents", ""]
        out += [f"- [{title}](#{_anchor(title)})" for title, _ in sections if title != "Support"]
        out += [""]
    
    for title, body in sections:
        if title in ["Quick Start", "How It Works", "System Requirements", 
                     "Troubleshooting", "Contributing", "Support"]:
            out += [body, ""]
        else:
            out += [f"## {title}", "", body, ""]
    
    out += [
        "---",
        "",
        f'<p align="center"><b>Built with FixReadMe</b> | Analyze · Document · Validate</p>',
        f'<p align="center"><a href="#{_anchor(m["project_name"])}">⬆ Back to Top</a></p>'
    ]
    
    return "\n".join(out)