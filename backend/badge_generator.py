def _badge(label, message, color, target=None):
    safe_label = str(label).replace("-", "--").replace("_", "__").replace(" ", "_")
    safe_message = str(message).replace("-", "--").replace("_", "__").replace(" ", "_")
    image = f"https://img.shields.io/badge/{safe_label}-{safe_message}-{color}"
    return f"[![{label}]({image})]({target})" if target else f"![{label}]({image})"


def generate(repository, analysis):
    badges = []
    owner = repository.get("owner")
    name = repository.get("name")
    repo_url = repository.get("url") or (f"https://github.com/{owner}/{name}" if owner and name else None)
    if repo_url and owner and name:
        badges.extend([
            f"[![GitHub stars](https://img.shields.io/github/stars/{owner}/{name}?style=flat)]({repo_url}/stargazers)",
            f"[![GitHub forks](https://img.shields.io/github/forks/{owner}/{name}?style=flat)]({repo_url}/network/members)",
        ])
    if repository.get("license"):
        badges.append(_badge("license", repository["license"], "blue", repo_url))
    if analysis.get("languages"):
        badges.append(_badge("language", analysis["languages"][0], "informational"))
    if analysis.get("ci_workflows") and owner and name:
        workflow = analysis["ci_workflows"][0]
        badges.append(
            f"[![CI](https://github.com/{owner}/{name}/actions/workflows/{workflow}/badge.svg)]"
            f"({repo_url}/actions/workflows/{workflow})"
        )
    return badges
