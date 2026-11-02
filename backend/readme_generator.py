try:
    from .badge_generator import generate as generate_badges
except ImportError:
    from badge_generator import generate as generate_badges


def _table(rows):
    return ["| Item | Details |", "| --- | --- |"] + [f"| {key} | {value} |" for key, value in rows]


def _mermaid(analysis):
    if not analysis.get("frameworks") and not analysis.get("entry_points"):
        return []
    lines = ["```mermaid", "flowchart LR", "    repo[Repository] --> source[Source modules]"]
    if analysis.get("frameworks"):
        lines.append(f"    source --> framework[{', '.join(analysis['frameworks'])}]")
    if analysis.get("routes"):
        lines.append("    framework --> api[HTTP routes]")
    if analysis.get("entry_points"):
        lines.append("    source --> entry[Entry points]")
    lines.append("```")
    return lines


def generate(repository, analysis, sections=None):
    selected = set(sections or outline_fallback(repository, analysis))
    title = repository.get("name") or "Repository"
    description = repository.get("description") or "Repository documentation generated from scanned project evidence."
    lines = [f"# {title}", "", description, ""]
    badges = generate_badges(repository, analysis)
    if badges and "Badges" in selected:
        lines += [" ".join(badges), ""]
    lines += ["## Overview", "", *_table([
        ("Project type", analysis.get("project_type", "Unavailable")),
        ("Primary language", (analysis.get("languages") or [repository.get("language") or "Unavailable"])[0]),
        ("Repository", f"[View on GitHub]({repository.get('url')})" if repository.get("url") else "Unavailable"),
        ("Files scanned", str(analysis.get("files_scanned", 0))),
    ]), ""]
    if analysis.get("features") and "Features" in selected:
        lines += ["## Features", ""] + [f"- {feature}" for feature in analysis["features"]] + [""]
    if (analysis.get("frameworks") or analysis.get("dependencies")) and "Technology" in selected:
        lines += ["## Technology stack", ""]
        rows = []
        if analysis.get("frameworks"):
            rows.append(("Frameworks", ", ".join(analysis["frameworks"])))
        if analysis.get("dependencies"):
            rows.append(("Dependencies", ", ".join(f"`{item}`" for item in analysis["dependencies"][:30])))
        lines += _table(rows) + [""]
    if analysis.get("structure") and "Structure" in selected:
        lines += ["## Project structure", "", *_table([
            (f"`{path}`", "Scanned repository file") for path in analysis["structure"][:20]
        ]), ""]
    if (analysis.get("frameworks") or analysis.get("entry_points")) and "Architecture" in selected:
        lines += ["## Architecture", "", *_mermaid(analysis), ""]
    if "Prerequisites" in selected:
        lines += ["## Prerequisites", "", f"- A working {((analysis.get('languages') or ['runtime'])[0])} development environment."]
    else:
        lines += []
    if analysis.get("dependencies"):
        lines.append("- Access to the package manager used by the repository manifests.")
    lines.append("")
    if "Installation" in selected:
        lines += ["## Installation", ""]
        manifests = set(analysis.get("manifests") or analysis.get("structure") or [])
        if "requirements.txt" in manifests:
            lines += ["```bash", "python -m pip install -r requirements.txt", "```"]
        elif "pyproject.toml" in manifests:
            lines += ["```bash", "python -m pip install -e .", "```"]
        elif "package.json" in manifests:
            lines += ["```bash", "npm install", "```"]
        elif "Cargo.toml" in manifests:
            lines += ["```bash", "cargo build", "```"]
        elif "go.mod" in manifests:
            lines += ["```bash", "go mod download", "```"]
        else:
            lines.append("Installation commands were not identified in the scanned manifests.")
        lines.append("")
    if ("Configuration" in selected
            and (analysis.get("environment_variables") or analysis.get("configuration_files"))):
        lines += ["## Configuration", ""]
        if analysis.get("environment_variables"):
            lines += _table([(f"`{name}`", "Environment variable referenced by repository configuration")
                             for name in analysis["environment_variables"]]) + [""]
        if analysis.get("configuration_files"):
            lines += ["Configuration files: " + ", ".join(f"`{path}`" for path in analysis["configuration_files"]) + ".", ""]
    if "Usage" in selected:
        lines += ["## Usage", ""]
        if analysis.get("scripts"):
            lines += ["Run a detected package script:", "", "```bash", f"npm run {next(iter(analysis['scripts']))}", "```"]
        elif analysis.get("entry_points"):
            lines += ["Detected entry points:", ""] + [f"- `{path}`" for path in analysis["entry_points"][:10]]
        else:
            lines.append("No executable entry point was verified in the scanned files.")
        lines.append("")
    if analysis.get("routes") and "API" in selected:
        lines += ["## API", "", *_table([("Detected route", f"`{route}`") for route in analysis["routes"]]), ""]
    if analysis.get("project_type") in {"Machine learning project", "Research project"} and "Workflow" in selected:
        lines += ["## Workflow", "", "The repository contains machine-learning or research dependencies; inspect the scanned entry points and examples for the verified execution flow.", ""]
    if analysis.get("ci_workflows") and "Deployment" in selected:
        lines += ["## Deployment and CI", "", "GitHub Actions workflows detected:",
                  ""] + [f"- `{workflow}`" for workflow in analysis["ci_workflows"]] + [""]
    if any("test" in path.lower() for path in analysis.get("structure", [])) and "Testing" in selected:
        lines += ["## Testing", "", "Test files were detected. Use the repository's configured test runner; no command is asserted without manifest evidence.", ""]
    if repository.get("license") and "License" in selected:
        lines += ["## License", "", f"This project declares the **{repository['license']}** license.", ""]
    if "Contributing" in selected:
        lines += ["## Contributing", "", "Contributions should follow the repository's existing review and testing conventions.", ""]
    return "\n".join(lines).rstrip() + "\n"


def outline_fallback(repository, analysis):
    selected = ["Overview", "Badges", "Prerequisites", "Installation", "Usage", "Contributing"]
    if analysis.get("features"):
        selected.append("Features")
    if analysis.get("frameworks") or analysis.get("dependencies"):
        selected.append("Technology")
    if analysis.get("structure"):
        selected.append("Structure")
    if analysis.get("frameworks") or analysis.get("entry_points"):
        selected.append("Architecture")
    if analysis.get("environment_variables") or analysis.get("configuration_files"):
        selected.append("Configuration")
    if analysis.get("routes"):
        selected.append("API")
    if analysis.get("ci_workflows"):
        selected.append("Deployment")
    if repository.get("license"):
        selected.append("License")
    return selected
