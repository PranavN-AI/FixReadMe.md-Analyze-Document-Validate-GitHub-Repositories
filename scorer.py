"""scorer.py - Hard 100-point scoring system using 100+ features."""
from typing import Dict


def score_readme(features: Dict, metrics: Dict) -> Dict:
    """
    Score a README on 100-point scale across 10 dimensions.
    Each dimension uses multiple features for granular grading.
    """
    scores = {}
    
    # === 1. VISUAL APPEAL (0-15) ===
    visual = 0
    visual += 2 if features.get("has_badges") else 0
    visual += min(2, metrics.get("badge_count", 0) // 5)
    visual += 2 if features.get("has_many_badges") else 0
    visual += 1 if features.get("has_images") else 0
    visual += 1 if features.get("has_many_images") else 0
    visual += 1 if features.get("has_gifs") else 0
    visual += 1 if features.get("has_screenshots") else 0
    visual += 1 if features.get("has_centered_content") else 0
    visual += 1 if features.get("has_aligned_images") else 0
    visual += 1 if features.get("has_banner") else 0
    visual += 1 if features.get("has_html_formatting") else 0
    visual += 1 if features.get("has_emojis") else 0
    scores["visual_appeal"] = min(15, visual)
    
    # === 2. STRUCTURE (0-12) ===
    structure = 0
    structure += 1 if features.get("has_h1") else 0
    structure += 2 if features.get("has_h2") else 0
    structure += 1 if features.get("has_h3") else 0
    structure += 1 if features.get("has_multiple_h2") else 0
    structure += 1 if features.get("has_multiple_h3") else 0
    structure += 2 if features.get("has_toc") else 0
    structure += 1 if features.get("has_back_to_top") else 0
    structure += 1 if features.get("has_navigation") else 0
    structure += 1 if features.get("has_blockquotes") else 0
    structure += 1 if features.get("has_note_boxes") else 0
    scores["structure"] = min(12, structure)
    
    # === 3. ACTIONABILITY (0-15) ===
    action = 0
    action += 3 if features.get("has_installation") else 0
    action += 2 if features.get("has_quick_start") else 0
    action += 2 if features.get("has_prerequisites") else 0
    action += 1 if features.get("has_docker_instructions") else 0
    action += 1 if features.get("has_env_setup") else 0
    action += 2 if features.get("has_usage") else 0
    action += 1 if features.get("has_basic_example") else 0
    action += 1 if features.get("has_advanced_example") else 0
    action += 1 if features.get("has_multiple_examples") else 0
    action += 1 if features.get("has_demo") else 0
    scores["actionability"] = min(15, action)
    
    # === 4. CODE QUALITY (0-15) ===
    code_q = 0
    code_q += 2 if features.get("has_code_examples") else 0
    code_q += min(2, metrics.get("code_block_count", 0) // 5)
    code_q += 1 if features.get("has_many_code_blocks") else 0
    code_q += 1 if features.get("has_bash_examples") else 0
    code_q += 1 if features.get("has_python_examples") else 0
    code_q += 1 if features.get("has_javascript_examples") else 0
    code_q += 1 if features.get("has_json_examples") else 0
    code_q += 1 if features.get("has_yaml_examples") else 0
    code_q += 2 if features.get("has_tables") else 0
    code_q += 1 if features.get("has_multiple_tables") else 0
    code_q += 1 if features.get("has_bullets") else 0
    code_q += 1 if features.get("has_many_bullets") else 0
    scores["code_quality"] = min(15, code_q)
    
    # === 5. DOCUMENTATION DEPTH (0-15) ===
    depth = 0
    depth += 2 if features.get("has_api_docs") else 0
    depth += 1 if features.get("has_endpoint_list") else 0
    depth += 1 if features.get("has_parameters") else 0
    depth += 1 if features.get("has_response_format") else 0
    depth += 1 if features.get("has_error_handling") else 0
    depth += 2 if features.get("has_architecture") else 0
    depth += 1 if features.get("has_design_decisions") else 0
    depth += 1 if features.get("has_flow_diagram") else 0
    depth += 1 if features.get("has_changelog") else 0
    depth += 1 if features.get("has_roadmap") else 0
    depth += 1 if features.get("has_troubleshooting") else 0
    depth += 1 if features.get("has_faq") else 0
    scores["doc_depth"] = min(15, depth)
    
    # === 6. COMMUNITY READINESS (0-10) ===
    community = 0
    community += 2 if features.get("has_contributing") else 0
    community += 1 if features.get("has_code_of_conduct") else 0
    community += 2 if features.get("has_license_section") else 0
    community += 1 if features.get("has_support") else 0
    community += 1 if features.get("has_discord") else 0
    community += 1 if features.get("has_slack") else 0
    community += 1 if features.get("has_task_lists") else 0
    community += 1 if features.get("has_rich_links") else 0
    scores["community"] = min(10, community)
    
    # === 7. PROFESSIONAL POLISH (0-10) ===
    polish = 0
    polish += 1 if features.get("has_ci_badge") else 0
    polish += 1 if features.get("has_version_badge") else 0
    polish += 1 if features.get("has_coverage_badge") else 0
    polish += 1 if features.get("has_downloads_badge") else 0
    polish += 1 if features.get("has_stars_badge") else 0
    polish += 1 if features.get("has_language_badge") else 0
    polish += 1 if features.get("has_comprehensive_docs") else 0
    polish += 1 if features.get("has_extensive_docs") else 0
    polish += 1 if features.get("has_code_heavy") else 0
    polish += 1 if features.get("has_details_summary") else 0
    scores["polish"] = min(10, polish)
    
    # === 8. TRUST SIGNALS (0-8) ===
    trust = 0
    trust += 1 if features.get("has_ci_badge") else 0
    trust += 1 if features.get("has_license_section") else 0
    trust += 1 if features.get("has_author_info") else 0
    trust += 1 if features.get("has_version_info") else 0
    trust += 1 if features.get("has_status_info") else 0
    trust += 1 if features.get("has_citations") else 0
    trust += 1 if features.get("has_alt_text") else 0
    trust += 1 if features.get("has_descriptive_alt") else 0
    scores["trust"] = min(8, trust)
    
    # === 9. ADVANCED FEATURES (0-7) ===
    advanced = 0
    advanced += 2 if features.get("has_mermaid") else 0
    advanced += 1 if features.get("has_flowchart") else 0
    advanced += 1 if features.get("has_sequence_diagram") else 0
    advanced += 1 if features.get("has_multilang") else 0
    advanced += 1 if features.get("has_translation_links") else 0
    advanced += 1 if features.get("has_video_demo") else 0
    scores["advanced"] = min(7, advanced)
    
    # === 10. DEPLOYMENT & TESTING (0-3) ===
    deploy = 0
    deploy += 1 if features.get("has_deployment") else 0
    deploy += 1 if features.get("has_testing") else 0
    deploy += 1 if features.get("has_test_commands") else 0
    scores["deployment_testing"] = min(3, deploy)
    
    # === TOTAL ===
    total = sum(scores.values())
    
    # Determine grade
    if total >= 90:
        grade = "S"
    elif total >= 80:
        grade = "A"
    elif total >= 70:
        grade = "B"
    elif total >= 60:
        grade = "C"
    elif total >= 45:
        grade = "D"
    else:
        grade = "F"
    
    scores["total"] = total
    scores["grade"] = grade
    
    return scores