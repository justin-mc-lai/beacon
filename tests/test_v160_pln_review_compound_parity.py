from __future__ import annotations

from pathlib import Path

from beacon.utils.planner_review_runtime import build_planner_review_runtime_artifact, synthesize_findings
from beacon.utils.skill_eval_kit import run_skill_eval_benchmark


FEATURE = "beacon-pln-review-compound-parity-v160"
VERSION = "v1.6.0"


def _artifact(tmp_path: Path, prompt: str | None = None) -> dict:
    return build_planner_review_runtime_artifact(
        project_root=tmp_path,
        feature=FEATURE,
        version=VERSION,
        prompt=prompt
        or (
            "参考 compound-engineering-plugin 完整复刻同等能力，不要 MVP。"
            "同时 review PR diff worktree generated projection release install canary rollback "
            "QA benchmark browser compatibility junit assertion fake runner placeholder evidence。"
            "还要覆盖 auth permission secret security、performance long-running concurrency cache、"
            "API CLI schema command contract、adversarial challenge 高风险。"
        ),
        truth_refs=[f"docs/beacon/v1.6.0/features/{FEATURE}/truth.md"],
        source_refs=["/Users/apple/.codex/skills/compound-engineering/ce-code-review/SKILL.md"],
        evidence_refs=[f"docs/beacon/v1.6.0/features/{FEATURE}/tests.md"],
        host_runtime="codex",
        subagent_runtime_available=False,
    )


def test_compound_review_contract_reference_exists() -> None:
    # 1+6 merge: pln-review materials live under the beacon-plan core.
    root = Path("skills/beacon/beacon-plan")
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    reference = (root / "references/pln-review/compound-parity-review.md").read_text(encoding="utf-8")

    assert "references/pln-review/" in skill
    for field in (
        "intent_snapshot",
        "scope_mode",
        "diff_scope",
        "source_capability_inventory",
        "parity_matrix",
        "coverage_mapping",
        "deferral_ledger",
        "autofix_routing",
        "release_ops_review",
        "qa_evidence_hygiene",
    ):
        assert field in reference


def test_reviewer_catalog_covers_compound_and_beacon_reviewers(tmp_path: Path) -> None:
    reviewers = set(_artifact(tmp_path)["selected_reviewers"])

    expected = {
        "correctness-reviewer",
        "testing-reviewer",
        "maintainability-reviewer",
        "project-standards-reviewer",
        "intent-fidelity",
        "route-boundary",
        "source-parity-reviewer",
        "diff-scope-reviewer",
        "security-reviewer",
        "performance-reviewer",
        "api-contract-reviewer",
        "reliability-reviewer",
        "browser-ops-reviewer",
        "release-ops-reviewer",
        "adversarial-reviewer",
        "state-machine",
    }
    assert expected <= reviewers


def test_full_parity_prompt_requires_source_inventory_and_parity_matrix(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)

    assert payload["scope_mode"] == "full_parity"
    assert payload["source_capability_inventory"]
    assert payload["parity_matrix"]
    assert payload["coverage_mapping"]
    assert payload["intent_snapshot"]["silent_scope_change_allowed"] is False


def test_unapproved_mvp_downgrade_is_blocked(tmp_path: Path) -> None:
    payload = _artifact(tmp_path, prompt="完整复刻 source，但是先降级 MVP defer 六个能力，没有用户确认。")

    assert payload["scope_mode"] == "full_parity"
    assert payload["deferral_ledger"]
    assert payload["deferral_ledger"][0]["user_decision_required"] is True
    assert payload["synthesis"]["highest_severity"] in {"P0", "P1"}


def test_finding_schema_contains_synthesis_and_routing_fields(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)
    finding = payload["findings"][0]

    for field in (
        "severity",
        "confidence",
        "authority_level",
        "dedup_key",
        "merged_from",
        "conflict_group",
        "owner",
        "autofix_class",
        "requires_verification",
        "recommended_route",
    ):
        assert field in finding


def test_synthesis_dedups_conflicts_and_selects_conservative_route() -> None:
    synthesis = synthesize_findings(
        [
            {
                "finding_id": "a",
                "lane_id": "lane-a",
                "severity": "P2",
                "authority_level": "runtime_evidence",
                "confidence": 50,
                "recommended_route": "beacon-eval-qa",
                "dedup_key": "truth:route:compound",
                "user_decision_required": False,
                "owner": "evaluator",
            },
            {
                "finding_id": "b",
                "lane_id": "lane-b",
                "severity": "P1",
                "authority_level": "user_quote",
                "confidence": 75,
                "recommended_route": "beacon-gen-change",
                "dedup_key": "truth:route:compound",
                "user_decision_required": True,
                "owner": "generator",
            },
            {
                "finding_id": "c",
                "lane_id": "lane-c",
                "severity": "P2",
                "authority_level": "package_truth",
                "confidence": 50,
                "recommended_route": "beacon-gov-doctor",
                "dedup_key": "ops:route:release",
                "user_decision_required": False,
                "owner": "governor",
            },
        ]
    )

    assert synthesis["recommended_route"] == "beacon-gen-change"
    assert synthesis["highest_severity"] == "P1"
    assert synthesis["conflict_groups"]


def test_planner_autofix_classification_does_not_execute_repairs(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)
    routing = payload["autofix_routing"]

    assert routing["planner_executes_repairs"] is False
    assert routing["generator_required_for_safe_auto"] is True
    assert set(routing["buckets"]) >= {"safe_auto", "gated_auto", "manual", "advisory", "human", "release"}
    assert payload["planner_boundary"]["code_write_allowed"] is False


def test_diff_scope_review_records_worktree_surfaces(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)
    diff_scope = payload["diff_scope"]

    for field in (
        "base_ref",
        "changed_files",
        "untracked_files",
        "generated_projection_files",
        "deleted_files",
        "high_risk_file_categories",
        "scope_confidence",
    ):
        assert field in diff_scope
    assert diff_scope["degraded"] is True


def test_release_ops_review_routes_install_and_projection_gaps(tmp_path: Path) -> None:
    review = _artifact(tmp_path)["release_ops_review"]

    assert review["triggered"] is True
    assert "global_agent_skill_projection" in review["checks"]
    assert "rollback_or_cleanup_route" in review["checks"]
    assert review["release_ready_authority"] is False


def test_qa_evidence_hygiene_flags_junit_assertion_and_placeholder_gaps(tmp_path: Path) -> None:
    hygiene = _artifact(tmp_path)["qa_evidence_hygiene"]

    assert hygiene["triggered"] is True
    assert "junit_xml" in hygiene["checks"]
    assert "assertion_count_gt_zero" in hygiene["checks"]
    assert "benchmark_metadata_grading_analysis" in hygiene["checks"]
    assert {"junit_required", "assertion_count_required", "fake_runner_blocked", "placeholder_evidence_blocked"} <= set(hygiene["reason_codes"])


def test_compound_parity_state_machine_contract_is_materialized(tmp_path: Path) -> None:
    state_model = _artifact(tmp_path)["state_model"]

    for state in ("ScopeResolved", "SourceParityResolved", "ReviewerSelection", "LaneExecution", "FindingSynthesis", "RouteRecommendation"):
        assert state in state_model["states"]
    assert "SourceParityResolved->RouteRecommendation" in state_model["invalid_transitions"]
    assert "review_degraded_scope_unknown" in state_model["terminal_states"]


def test_planner_review_artifact_has_no_truth_or_verdict_authority(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)

    assert payload["runtime_evidence_only"] is True
    assert payload["requirement_truth"] is False
    assert payload["formal_verdict_authority"] is False
    assert payload["release_verdict_authority"] is False
    assert payload["planner_boundary"] == {
        "truth_write_allowed": False,
        "code_write_allowed": False,
        "machine_write_allowed": False,
        "qa_verdict_allowed": False,
        "release_verdict_allowed": False,
    }


def test_skill_eval_benchmark_covers_compound_parity_cases(tmp_path: Path) -> None:
    payload = run_skill_eval_benchmark(tmp_path, version=VERSION)

    assert payload["status"] == "pass"
    covered = set(payload["covered_tc_ids"])
    assert {"TC-026", "TC-027", "TC-028", "TC-029", "TC-030", "TC-031", "TC-032", "TC-033"} <= covered
    root = tmp_path / payload["root"]
    grading = (root / "grading" / "tc-033-compound-qa-evidence-hygiene.with_skill.json").read_text(encoding="utf-8")
    assert "qa_evidence_hygiene_verified" in grading
    assert "benchmark_metadata_grading_analysis_required" in grading
