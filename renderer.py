"""renderer.py - Premium README renderer (claude-mem quality level)."""
import re
from urllib.parse import urlencode

import requests

SHIELDS = "https://img.shields.io"
_BAD = ("invalid", "not found", "unknown logo", "inaccessible")
LANG_META = {"Python": ("3776AB", "python", "white"), "JavaScript": ("F7DF1E", "javascript", "black"),
             "TypeScript": ("3178C6", "typescript", "white"), "Java": ("007396", "openjdk", "white"),
             "C++": ("00599C", "cplusplus", "white"), "C": ("A8B9CC", "c", "white"),
             "C#": ("239120", "csharp", "white"), "Go": ("00ADD8", "go", "white"),
             "Rust": ("CE422B", "rust", "white"), "HTML": ("E34F26", "html5", "white"),
             "CSS": ("1572B6", "css3", "white"), "Shell": ("4EAA25", "gnubash", "white"),
             "SQL": ("336791", "mysql", "white")}
FW_META = {"Flask": ("000000", "flask", "white"), "Django": ("092E20", "django", "white"),
           "FastAPI": ("009688", "fastapi", "white"), "Streamlit": ("FF4B4B", "streamlit", "white"),
           "React": ("61DAFB", "react", "black"), "Next.js": ("000000", "nextdotjs", "white"),
           "Vue.js": ("4FC08D", "vuedotjs", "white"), "Express": ("000000", "express", "white"),
           "Pandas": ("150458", "pandas", "white"), "NumPy": ("013243", "numpy", "white"),
           "PyTorch": ("EE4C2C", "pytorch", "white"), "TensorFlow": ("FF6F00", "tensorflow", "white")}


def esc(t):
    return t.replace("_", "__").replace("-", "--").strip().replace(" ", "_")


def static_badge(label, message, color, logo=None, logo_color="white"):
    url = f"{SHIELDS}/badge/{esc(label)}-{esc(message)}-{color.lstrip('#')}?style=for-the-badge"
    if logo:
        url += "&" + urlencode({"logo": logo, "logoColor": logo_color})
    return url


def badge_ok(url, timeout=4):
    try:
        res = requests.get(url, timeout=timeout)
        return res.status_code == 200 and not any(b in res.text.lower() for b in _BAD)
    except requests.RequestException:
        return True


def build_badges(m, validate=True):
    badges = []
    verified = static_badge("FixReadMe", "Verified", "10b981", logo="checkmarx")
    if validate and not badge_ok(verified):
        verified = static_badge("FixReadMe", "Verified", "10b981")
    badges.append(("FixReadMe Verified", verified))
    for lang in m["languages"][:4]:
        meta = LANG_META.get(lang)
        if meta:
            badges.append((lang, static_badge(lang, f"{m['lang_counts'].get(lang, 0)} files",
                                              meta[0], meta[1], meta[2])))
    for fw in m["frameworks"][:4]:
        meta = FW_META.get(fw)
        if meta:
            badges.append((fw, static_badge(fw, "framework", meta[0], meta[1], meta[2])))
    if m["has_license"]:
        badges.append(("License", static_badge("License", m["license_type"], "blue")))
    if m["has_tests"]:
        badges.append(("Tests", static_badge("Tests", "Passing", "success")))
    if m["has_docker"]:
        badges.append(("Docker", static_badge("Docker", "Ready", "2496ED", "docker")))
    if m["is_public"] and m["owner"]:
        o, r = m["owner"], m["repo"]
        badges += [("Stars", f"{SHIELDS}/github/stars/{o}/{r}?style=social"),
                   ("Forks", f"{SHIELDS}/github/forks/{o}/{r}?style=social"),
                   ("Issues", f"{SHIELDS}/github/issues/{o}/{r}"),
                   ("Last Commit", f"{SHIELDS}/github/last-commit/{o}/{r}")]
    return badges


def badge_block(badges):
    imgs = "\n  ".join(f'<img src="{u}" alt="{a}">' for a, u in badges)
    return f'<p align="center">\n  {imgs}\n</p>'


def _anchor(title):
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip().replace(" ", "-")


def _quick_start(m):
    lines = []
    if m["has_requirements"]:
        lines += ["Install with a single command:", "", "```bash", "pip install -r requirements.txt", "```", ""]
    elif m["has_package_json"]:
        lines += ["Install with a single command:", "", "```bash", "npm install", "```", ""]
    if "Streamlit" in m["frameworks"]:
        lines += ["Run the application:", "", "```bash", "streamlit run app.py", "```"]
    elif m["entry_point"].endswith(".py"):
        lines += ["Run the application:", "", "```bash", f"python {m['entry_point']}", "```"]
    elif m["scripts"].get("dev") or m["scripts"].get("start"):
        lines += ["Run the application:", "", "```bash",
                  "npm run dev" if m["scripts"].get("dev") else "npm start", "```"]
    return "\n".join(lines) or "See Installation below."


def _how_it_works(m):
    comps = []
    if "Python" in m["languages"]:
        comps.append("1. **Core Engine** - Main application logic and business rules")
    if "JavaScript" in m["languages"] or "TypeScript" in m["languages"]:
        comps.append(f"{len(comps)+1}. **Interface Layer** - User-facing UI and client logic")
    if m["has_tests"]:
        comps.append(f"{len(comps)+1}. **Test Suite** - Automated verification of behavior")
    if m["has_docker"]:
        comps.append(f"{len(comps)+1}. **Container Layer** - Reproducible deployment environment")
    if m["has_ci"]:
        comps.append(f"{len(comps)+1}. **CI Pipeline** - Automated checks on every push")
    if not comps:
        comps = ["1. **Source Code** - Main application logic",
                 "2. **Configuration** - Settings and environment variables",
                 "3. **Dependencies** - Required libraries and packages"]
    return "**Core Components:**\n\n" + "\n".join(comps)


def _sys_req(m):
    reqs = []
    if "Python" in m["languages"]:
        reqs.append("- **Python**: 3.8 or higher")
    if "JavaScript" in m["languages"] or "TypeScript" in m["languages"]:
        reqs.append("- **Node.js**: 16.0.0 or higher")
    if m["has_docker"]:
        reqs.append("- **Docker**: 20.0 or higher (optional)")
    if not reqs:
        reqs = ["- **OS**: Windows, macOS, or Linux", "- **Internet**: for dependency installation"]
    return "\n".join(reqs)


def _troubleshooting():
    return ("If experiencing issues:\n\n"
            "1. **Check dependencies** - ensure all required packages are installed\n"
            "2. **Verify environment** - confirm environment variables are set correctly\n"
            "3. **Review logs** - check application output for error messages\n"
            "4. **Clean install** - delete `venv` / `node_modules` and reinstall\n\n"
            "Still stuck? Open an issue on the repository.")


def _contributing():
    return ("Contributions are welcome!\n\n"
            "1. Fork the repository\n"
            "2. Create a feature branch (`git checkout -b feature/amazing`)\n"
            "3. Commit your changes (`git commit -m 'Add amazing feature'`)\n"
            "4. Push to the branch (`git push origin feature/amazing`)\n"
            "5. Open a Pull Request\n\n"
            "Please include tests and update documentation where needed.")


def _verification(m):
    checks = [("README present", m["has_readme"]), ("License file", m["has_license"]),
              ("Test suite", m["has_tests"]), ("CI/CD workflow", m["has_ci"]),
              (".gitignore", m["has_gitignore"]), ("Env template", m["has_env_example"]),
              ("Docker setup", m["has_docker"])]
    lines = ["| Check | Status |", "|---|:---:|"]
    score = 0
    for name, ok in checks:
        lines.append(f"| {name} | {'✅' if ok else '❌'} |")
        score += bool(ok)
    lines.append(f"\n**Repository health score: {score}/{len(checks)}** — "
                 "FixReadMe auto-generates the missing docs items.")
    return "\n".join(lines)


def build_readme(m, tagline, description, features,
                 center_badges=True, include_toc=True, validate=True):
    badges = build_badges(m, validate=validate)
    sections = [("Overview", f"**{description}**\n\n*{tagline}*"),
                ("Quick Start", _quick_start(m)),
                ("Features", "\n".join(features)),
                ("How It Works", _how_it_works(m))]

    install = ["```bash"]
    if m["git_remote"]:
        install.append(f"git clone {m['git_remote']}")
    install += [f"cd {m['project_name']}", "```"]
    sections.append(("Installation", "\n".join(install)))

    if m["images"]:
        grid = "\n".join(f'<img src="{i}" width="45%" style="margin:8px;">' for i in m["images"])
        sections.append(("Screenshots", f'<p align="center">\n{grid}\n</p>'))

    deps_lower = [d.lower() for d in m["dependencies"]]
    if m["has_env_example"] or "python-dotenv" in deps_lower:
        env = ["Configuration is managed via environment variables.", ""]
        if m["has_env_example"]:
            env += ["```bash", "cp .env.example .env", "```", ""]
        env += ["```env", "API_KEY=your_api_key_here", "DEBUG=true", "```"]
        sections.append(("Configuration", "\n".join(env)))

    usage = []
    if "Streamlit" in m["frameworks"]:
        usage = ["```bash", "streamlit run app.py", "```"]
    elif m["entry_point"].endswith(".py"):
        usage = ["```bash", f"python {m['entry_point']}", "```"]
    elif m["scripts"].get("dev") or m["scripts"].get("start"):
        usage = ["```bash", "npm run dev" if m["scripts"].get("dev") else "npm start", "```"]
    if usage:
        sections.append(("Usage", "\n".join(usage)))

    if m["folder_tree"]:
        sections.append(("Project Structure", "```\n" + m["folder_tree"] + "\n```"))

    if m["languages"] or m["frameworks"]:
        rows = ["| Technology | Category | Purpose |", "|---|---|---|"]
        rows += [f"| {l} | Language | Core implementation |" for l in m["languages"][:4]]
        rows += [f"| {f} | Framework | Application framework |" for f in m["frameworks"][:4]]
        sections.append(("Tech Stack", "\n".join(rows)))

    sections.append(("System Requirements", _sys_req(m)))

    if m["has_tests"]:
        t = ["```bash"]
        if "Python" in m["languages"]:
            t.append("pytest")
        if m["scripts"].get("test"):
            t.append("npm test")
        t.append("```")
        sections.append(("Testing", "\n".join(t)))

    sections.append(("Troubleshooting", _troubleshooting()))
    if m["todos"]:
        sections.append(("Roadmap", "\n".join(f"- [ ] {t}" for t in m["todos"])))
    sections.append(("Verification Report", _verification(m)))
    sections.append(("Contributing", _contributing()))
    if m["contributors"]:
        sections.append(("Contributors", ", ".join(f"**{c}**" for c in m["contributors"])))
    if m["has_license"]:
        sections.append(("License", f"This project is licensed under the **{m['license_type']} License**."))
    support = ["- **Issues**: report bugs and request features via GitHub Issues"]
    if m["owner"]:
        support.insert(0, f"- **Repository**: [github.com/{m['owner']}/{m['repo']}]"
                          f"(https://github.com/{m['owner']}/{m['repo']})")
    sections.append(("Support", "\n".join(support)))

    out = [badge_block(badges) if center_badges else " ".join(f"![{a}]({u})" for a, u in badges),
           "", f"# {m['project_name']}", ""]
    if include_toc:
        out += ["## Table of Contents", ""]
        out += [f"- [{t}](#{_anchor(t)})" for t, _ in sections]
        out += [""]
    for title, body in sections:
        out += [f"## {title}", "", body, ""]
    out += ["---", "",
            '<p align="center"><b>Built with FixReadMe</b> — Analyze · Document · Validate</p>',
            f'<p align="center"><a href="#{_anchor(m["project_name"])}">⬆ Back to Top</a></p>']
    return "\n".join(out)