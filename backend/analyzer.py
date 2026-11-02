def outline(repository, analysis):
    sections = ["Overview"]
    if repository.get("owner") and repository.get("name"):
        sections.append("Badges")
    if analysis.get("features"):
        sections.append("Features")
    if analysis.get("frameworks") or analysis.get("dependencies"):
        sections.append("Technology")
    if analysis.get("structure"):
        sections.append("Structure")
    if analysis.get("frameworks") or analysis.get("entry_points"):
        sections.append("Architecture")
    sections += ["Prerequisites", "Installation"]
    if analysis.get("environment_variables") or analysis.get("configuration_files"):
        sections.append("Configuration")
    sections.append("Usage")
    if analysis.get("project_type") == "REST API" and analysis.get("routes"):
        sections.append("API")
    if analysis.get("project_type") in {"Machine learning project", "Research project"}:
        sections.append("Workflow")
    if analysis.get("examples"):
        sections.append("Examples")
    if any("test" in path.lower() for path in analysis.get("structure", [])):
        sections.append("Testing")
    if analysis.get("ci_workflows"):
        sections.append("Deployment")
    if repository.get("license"):
        sections.append("License")
    sections.append("Contributing")
    return sections
