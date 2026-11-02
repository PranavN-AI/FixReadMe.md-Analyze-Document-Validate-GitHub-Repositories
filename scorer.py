"""scorer.py - Hard 100-point scoring across 10 dimensions."""


def score_readme(f, m):
    s = {}

    v = 0
    v += 2 if f.get("has_badges") else 0
    v += min(2, m.get("badge_count", 0) // 5)
    v += 2 if f.get("has_many_badges") else 0
    v += 1 if f.get("has_images") else 0
    v += 1 if f.get("has_many_images") else 0
    v += 1 if f.get("has_gifs") else 0
    v += 1 if f.get("has_screenshots") else 0
    v += 1 if f.get("has_centered_content") else 0
    v += 1 if f.get("has_aligned_images") else 0
    v += 1 if f.get("has_banner") else 0
    v += 1 if f.get("has_html_formatting") else 0
    v += 1 if f.get("has_emojis") else 0
    s["visual_appeal"] = min(15, v)

    v = 0
    v += 1 if f.get("has_h1") else 0
    v += 2 if f.get("has_h2") else 0
    v += 1 if f.get("has_h3") else 0
    v += 1 if f.get("has_multiple_h2") else 0
    v += 1 if f.get("has_multiple_h3") else 0
    v += 2 if f.get("has_toc") else 0
    v += 1 if f.get("has_back_to_top") else 0
    v += 1 if f.get("has_navigation") else 0
    v += 1 if f.get("has_blockquotes") else 0
    v += 1 if f.get("has_note_boxes") else 0
    s["structure"] = min(12, v)

    v = 0
    v += 3 if f.get("has_installation") else 0
    v += 2 if f.get("has_quick_start") else 0
    v += 2 if f.get("has_prerequisites") else 0
    v += 1 if f.get("has_docker_instructions") else 0
    v += 1 if f.get("has_env_setup") else 0
    v += 2 if f.get("has_usage") else 0
    v += 1 if f.get("has_basic_example") else 0
    v += 1 if f.get("has_advanced_example") else 0
    v += 1 if f.get("has_multiple_examples") else 0
    v += 1 if f.get("has_demo") else 0
    s["actionability"] = min(15, v)

    v = 0
    v += 2 if f.get("has_code_examples") else 0
    v += min(2, m.get("code_block_count", 0) // 5)
    v += 1 if f.get("has_many_code_blocks") else 0
    v += 1 if f.get("has_bash_examples") else 0
    v += 1 if f.get("has_python_examples") else 0
    v += 1 if f.get("has_javascript_examples") else 0
    v += 1 if f.get("has_json_examples") else 0
    v += 1 if f.get("has_yaml_examples") else 0
    v += 2 if f.get("has_tables") else 0
    v += 1 if f.get("has_multiple_tables") else 0
    v += 1 if f.get("has_bullets") else 0
    v += 1 if f.get("has_many_bullets") else 0
    s["code_quality"] = min(15, v)

    v = 0
    v += 2 if f.get("has_api_docs") else 0
    v += 1 if f.get("has_endpoint_list") else 0
    v += 1 if f.get("has_parameters") else 0
    v += 1 if f.get("has_response_format") else 0
    v += 1 if f.get("has_error_handling") else 0
    v += 2 if f.get("has_architecture") else 0
    v += 1 if f.get("has_design_decisions") else 0
    v += 1 if f.get("has_flow_diagram") else 0
    v += 1 if f.get("has_changelog") else 0
    v += 1 if f.get("has_roadmap") else 0
    v += 1 if f.get("has_troubleshooting") else 0
    v += 1 if f.get("has_faq") else 0
    s["doc_depth"] = min(15, v)

    v = 0
    v += 2 if f.get("has_contributing") else 0
    v += 1 if f.get("has_code_of_conduct") else 0
    v += 2 if f.get("has_license_section") else 0
    v += 1 if f.get("has_support") else 0
    v += 1 if f.get("has_discord") else 0
    v += 1 if f.get("has_slack") else 0
    v += 1 if f.get("has_task_lists") else 0
    v += 1 if f.get("has_rich_links") else 0
    s["community"] = min(10, v)

    v = 0
    v += 1 if f.get("has_ci_badge") else 0
    v += 1 if f.get("has_version_badge") else 0
    v += 1 if f.get("has_coverage_badge") else 0
    v += 1 if f.get("has_downloads_badge") else 0
    v += 1 if f.get("has_stars_badge") else 0
    v += 1 if f.get("has_language_badge") else 0
    v += 1 if f.get("has_comprehensive_docs") else 0
    v += 1 if f.get("has_extensive_docs") else 0
    v += 1 if f.get("has_code_heavy") else 0
    v += 1 if f.get("has_details_summary") else 0
    s["polish"] = min(10, v)

    v = 0
    v += 1 if f.get("has_ci_badge") else 0
    v += 1 if f.get("has_license_section") else 0
    v += 1 if f.get("has_author_info") else 0
    v += 1 if f.get("has_version_info") else 0
    v += 1 if f.get("has_status_info") else 0
    v += 1 if f.get("has_citations") else 0
    v += 1 if f.get("has_alt_text") else 0
    v += 1 if f.get("has_descriptive_alt") else 0
    s["trust"] = min(8, v)

    v = 0
    v += 2 if f.get("has_mermaid") else 0
    v += 1 if f.get("has_flowchart") else 0
    v += 1 if f.get("has_sequence_diagram") else 0
    v += 1 if f.get("has_multilang") else 0
    v += 1 if f.get("has_translation_links") else 0
    v += 1 if f.get("has_video_demo") else 0
    s["advanced"] = min(7, v)

    v = 0
    v += 1 if f.get("has_deployment") else 0
    v += 1 if f.get("has_testing") else 0
    v += 1 if f.get("has_test_commands") else 0
    s["deployment_testing"] = min(3, v)

    total = sum(s.values())
    grade = ("S" if total >= 90 else "A" if total >= 80 else "B" if total >= 70
             else "C" if total >= 60 else "D" if total >= 45 else "F")
    s["total"] = total
    s["grade"] = grade
    return s