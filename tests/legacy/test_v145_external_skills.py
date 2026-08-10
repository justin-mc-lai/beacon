from __future__ import annotations

from beacon.utils.project_skills import (
    list_capability_sources,
    load_capability_learning_map,
    select_capability_composition,
    write_capability_learning_event,
)


def test_external_sources_are_first_class_capabilities(tmp_path) -> None:
    rows = list_capability_sources(tmp_path)
    baoyu = next(item for item in rows if item["source_id"] == "baoyu-skills")
    assert baoyu["kind"] == "external-governed-source"
    assert baoyu["governance_status"] == "canonical-sample"
    assert baoyu["source_identity"]["label"] == "core-skills/baoyu-skills"


def test_baoyu_skills_is_canonical_sample(tmp_path) -> None:
    rows = list_capability_sources(tmp_path)
    baoyu = next(item for item in rows if item["source_id"] == "baoyu-skills")
    assert "content" in baoyu["intended_domains"]
    assert "travel" in baoyu["intended_domains"]


def test_business_goal_without_explicit_chain_is_supported(tmp_path) -> None:
    payload = select_capability_composition(
        tmp_path,
        goal="整理航空公司出行提醒文章",
        output_shape="wechat-post",
    )
    assert payload["task_type"] == "travel-notice"
    assert payload["selected_source_id"] == "baoyu-skills"
    assert payload["candidate_skill_chain"]


def test_capability_selection_and_composition_contract_exists(tmp_path) -> None:
    payload = select_capability_composition(
        tmp_path,
        goal="产出行业分析长文骨架",
        output_shape="longform-markdown",
    )
    assert payload["selection_contract"]["user_declares_business_goal_not_chain"] is True
    assert payload["selection_contract"]["compatibility"]["admission_mode"] == "philosophy-first"


def test_success_failure_and_adoption_are_written_back(tmp_path) -> None:
    write_capability_learning_event(
        tmp_path,
        task_type="travel-notice",
        source_id="baoyu-skills",
        skill_chain=["baoyu-translate", "baoyu-post-to-wechat"],
        output_shape="wechat-post",
        outcome="success",
        human_adoption="adopted",
    )
    write_capability_learning_event(
        tmp_path,
        task_type="travel-notice",
        source_id="baoyu-skills",
        skill_chain=["baoyu-translate", "baoyu-post-to-wechat"],
        output_shape="wechat-post",
        outcome="fallback",
        fallback_path="manual-edit",
    )
    mapping = load_capability_learning_map(tmp_path)
    row = next(item for item in mapping["mappings"] if item["task_type"] == "travel-notice")
    assert row["success_count"] == 1
    assert row["fallback_count"] == 1


def test_task_type_to_chain_to_output_mapping_is_reusable(tmp_path) -> None:
    write_capability_learning_event(
        tmp_path,
        task_type="content-outline",
        source_id="baoyu-skills",
        skill_chain=["baoyu-article-illustrator", "baoyu-format-markdown"],
        output_shape="markdown-outline",
        outcome="success",
    )
    mapping = load_capability_learning_map(tmp_path)
    row = next(item for item in mapping["mappings"] if item["task_type"] == "content-outline")
    assert row["skill_chain"] == ["baoyu-article-illustrator", "baoyu-format-markdown"]
    assert row["output_shape"] == "markdown-outline"


def test_external_source_governance_preserves_boundaries(tmp_path) -> None:
    payload = select_capability_composition(
        tmp_path,
        goal="做内容投放策略分析",
        output_shape="longform-markdown",
    )
    assert payload["boundary_checks"]["truth_boundary_preserved"] is True
    assert payload["boundary_checks"]["guidance_boundary_preserved"] is True
    assert payload["boundary_checks"]["runtime_boundary_preserved"] is True


def test_philosophy_first_admission_preserves_strategy_tool_fact_layers(tmp_path) -> None:
    rows = list_capability_sources(tmp_path)
    baoyu = next(item for item in rows if item["source_id"] == "baoyu-skills")
    philosophy = baoyu["skill_philosophy"]
    assert philosophy["strategy_philosophy"]
    assert philosophy["minimum_complete_tools"]
    assert philosophy["necessary_factual_grounding"]
