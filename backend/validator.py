import re
from urllib.parse import urlparse


def validate(markdown, repository, analysis):
    findings = []

    def check(name, passed, explanation, evidence=None):
        findings.append({"check": name, "status": "passed" if passed else "failed",
                         "explanation": explanation, "evidence": evidence})

    check("heading", bool(re.search(r"^#\s+\S+", markdown, re.M)), "README has a top-level title.")
    check("markdown_fences", markdown.count("```") % 2 == 0,
          "Markdown code fences are balanced.")
    for dependency in analysis.get("dependencies", []):
        check("dependency", dependency.lower() in markdown.lower(),
              f"Dependency `{dependency}` is documented.", next(iter(analysis.get("manifests", [])), None))
    for route in analysis.get("routes", []):
        check("route", route in markdown, f"Detected route `{route}` is documented.")
    urls = re.findall(r"\]\((https?://[^)\s]+)\)", markdown)
    check("links", all(bool(urlparse(url).netloc) for url in urls),
          "Documented external links have valid URL syntax.")
    headings = re.findall(r"^#{1,6}\s+(.+)$", markdown, re.M)
    check("duplicate_headings", len(headings) == len(set(headings)),
          "README headings are not duplicated.")
    check("unsupported_claims", "100% standard compliance" not in markdown.lower()
          and "placeholder" not in markdown.lower(),
          "README does not contain known fabricated claim language.")
    check("installation_usage",
          "## Installation" in markdown and "## Usage" in markdown
          and "No executable entry point was verified" not in markdown,
          "Installation and usage guidance is actionable or clearly evidence-backed.")
    if repository.get("url"):
        check("badges", "shields.io" in markdown,
              "Repository badges are included only when repository metadata supports them.")
    if not findings:
        findings.append({"check": "structure", "status": "passed",
                         "explanation": "README validation completed."})
    return findings
