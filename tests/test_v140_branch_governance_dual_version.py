from __future__ import annotations

from pathlib import Path

from beacon.utils.branch_governance import DUAL_VERSION_TEMPLATE, evaluate_branch_governance, render_branch_governance_markdown


def _dual_version_contract() -> dict:
    return {
        "template_name": DUAL_VERSION_TEMPLATE,
        "repo_root": str(Path.cwd()),
        "service_key": "beacon",
        "base_branch": "feature/v1.3.3-all",
        "current_branch": "hotfix/BUG-1-v1.3.3",
        "target_branch": "hotfix/BUG-1-v1.3.3",
        "previous_version_baseline_branch": "feature/v1.3.3-all",
        "next_version_feature_branch": "feature/v1.3.4-all",
        "hotfix_branch_naming_rule": "hotfix/<ticket>-<version>",
    }


def test_previous_hotfix_forward_port_template() -> None:
    payload = evaluate_branch_governance(_dual_version_contract())
    assert payload["template_name"] == DUAL_VERSION_TEMPLATE
    assert "previous_baseline->hotfix" in payload["merge_direction_policy"]


def test_forbidden_next_feature_first_fix() -> None:
    payload = evaluate_branch_governance(
        {
            **_dual_version_contract(),
            "target_branch": "feature/v1.3.4-all",
        }
    )
    assert payload["blocked"] is True
    assert "branch_governance_forbidden_first_fix_lane" in payload["reason_codes"]


def test_minimum_evidence_fields_required() -> None:
    payload = evaluate_branch_governance(_dual_version_contract())
    assert payload["evidence_contract"] == [
        "source_commit",
        "forward_port_commit",
        "origin_uat_head",
        "pipeline_run_id",
    ]


def test_dual_lane_diagram_visible() -> None:
    text = render_branch_governance_markdown(_dual_version_contract())
    assert "feature/v1.3.3-all" in text
    assert "feature/v1.3.4-all" in text
    assert "-X-> first_production_fix" in text
