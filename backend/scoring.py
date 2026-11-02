def score(findings):
    categories = {
        "accuracy": ["dependency", "route", "unsupported_claims"],
        "completeness": ["heading"],
        "technical_correctness": ["markdown_fences"],
        "links_badges_diagrams": ["links"],
        "installation_usage": ["installation_usage"],
        "presentation": ["badges"],
        "consistency": ["duplicate_headings"],
    }
    breakdown = {}
    recommendations = []
    for category, checks in categories.items():
        relevant = [item for item in findings if item.get("check") in checks]
        if not relevant:
            breakdown[category] = 0
            continue
        passed = sum(item["status"] == "passed" for item in relevant)
        breakdown[category] = round(100 * passed / len(relevant))
        recommendations.extend(item["explanation"] for item in relevant if item["status"] == "failed")
    applicable = [value for category, value in breakdown.items()
                  if any(item.get("check") in categories[category] for item in findings)]
    score_value = round(sum(applicable) / len(applicable)) if applicable else 0
    return {"score": score_value, "score_breakdown": breakdown,
            "recommendations": recommendations}
