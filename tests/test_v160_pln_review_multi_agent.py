from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.planner_review_runtime import (
    ALWAYS_ON_REVIEWERS,
    build_planner_review_runtime_artifact,
    select_reviewers,
    synthesize_findings,
)
from beacon.utils.skill_eval_kit import run_skill_eval_benchmark


FEATURE = "beacon-pln-review-runtime-multi-agent-v160"
VERSION = "v1.6.0"


def _artifact(tmp_path: Path, prompt: str | None = None) -> dict:
    return build_planner_review_runtime_artifact(
        project_root=tmp_path,
        feature=FEATURE,
        version=VERSION,
        prompt=prompt
        or "完整复刻 source parity，同时覆盖 security permission、performance long-running、design flow、brownfield migration、evidence benchmark、founder challenge、ADR 和 context drift。",
        truth_refs=[f"docs/beacon/v1.6.0/features/{FEATURE}/truth.md"],
        source_refs=["https://example.test/source"],
        evidence_refs=[f"docs/beacon/v1.6.0/features/{FEATURE}/tests.md"],
        host_runtime="codex",
        subagent_runtime_available=False,
    )


def test_runtime_artifact_contains_required_multi_agent_fields(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)

    for field in (
        "review_id",
        "execution_mode",
        "host_runtime",
        "fallback_reason",
        "selected_reviewers",
        "reviewer_lanes",
        "findings",
        "synthesis",
        "evidence_paths",
    ):
        assert payload.get(field) not in ("", None, [], {})


def test_always_on_reviewers_produce_lanes(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)
    lane_reviewers = {lane["reviewer"] for lane in payload["reviewer_lanes"]}

    for reviewer in [item["reviewer"] for item in ALWAYS_ON_REVIEWERS]:
        assert reviewer in lane_reviewers


def test_conditional_reviewers_are_selected_from_prompt_signals() -> None:
    reviewers = {
        item["reviewer"]
        for item in select_reviewers(
            prompt=(
                "source parity defer permission long-running design brownfield evidence "
                "simplify founder challenge ADR context"
            )
        )
    }

    expected = {
        "source-parity",
        "deferral-sovereignty",
        "security-boundary",
        "performance-boundary",
        "design-flow",
        "brownfield-contract",
        "evidence-proof-shape",
        "simplification-risk",
        "founder-business",
        "adversarial-doubt",
        "adr-documentation",
        "context-engineering",
    }
    assert expected <= reviewers


def test_each_lane_has_finding_or_no_findings_status(tmp_path: Path) -> None:
    payload = _artifact(tmp_path, prompt="普通 planner review，不要求写代码。")

    assert payload["reviewer_lanes"]
    for lane in payload["reviewer_lanes"]:
        assert lane["output_status"] in {"finding", "no_findings"}
        if lane["output_status"] == "finding":
            assert lane["finding_ids"]
        else:
            assert lane["finding_ids"] == []


def test_synthesis_merges_dedups_and_preserves_conflicts() -> None:
    findings = [
        {
            "finding_id": "f1",
            "lane_id": "lane-intent",
            "severity": "P2",
            "authority_level": "runtime_evidence",
            "confidence": 50,
            "recommended_route": "beacon-eval-qa",
            "dedup_key": "truth:route:intent",
            "user_decision_required": False,
        },
        {
            "finding_id": "f2",
            "lane_id": "lane-source",
            "severity": "P1",
            "authority_level": "user_quote",
            "confidence": 75,
            "recommended_route": "beacon-gen-change",
            "dedup_key": "truth:route:intent",
            "user_decision_required": True,
        },
        {
            "finding_id": "f3",
            "lane_id": "lane-qa",
            "severity": "P2",
            "authority_level": "package_truth",
            "confidence": 50,
            "recommended_route": "beacon-eval-qa",
            "dedup_key": "qa:route:coverage",
            "user_decision_required": False,
        },
    ]

    synthesis = synthesize_findings(findings)

    assert synthesis["recommended_route"] == "beacon-gen-change"
    assert synthesis["highest_severity"] == "P1"
    assert synthesis["conflict_groups"]
    merged = [item for item in synthesis["merged_findings"] if item["dedup_key"] == "truth:route:intent"][0]
    assert set(merged["merged_from"]) == {"lane-intent", "lane-source"}


def test_fallback_transparency_blocks_fake_parallel_claims(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)

    assert payload["subagent_runtime_available"] is False
    assert payload["execution_mode"] == "single_process_multi_reviewer"
    assert payload["fallback_reason"]
    assert payload["execution_mode"] != "parallel_subagent_review"


def test_planner_boundary_flags_forbid_truth_code_machine_and_verdict_writes(tmp_path: Path) -> None:
    boundary = _artifact(tmp_path)["planner_boundary"]

    assert boundary == {
        "truth_write_allowed": False,
        "code_write_allowed": False,
        "machine_write_allowed": False,
        "qa_verdict_allowed": False,
        "release_verdict_allowed": False,
    }


def test_runtime_evidence_has_no_truth_or_verdict_authority(tmp_path: Path) -> None:
    payload = _artifact(tmp_path)

    assert payload["runtime_evidence_only"] is True
    assert payload["requirement_truth"] is False
    assert payload["formal_verdict_authority"] is False
    assert payload["release_verdict_authority"] is False


def test_review_state_machine_contract_is_materialized(tmp_path: Path) -> None:
    state_model = _artifact(tmp_path)["state_model"]

    assert state_model["required"] is True
    for state in ("ReviewRequested", "ContextResolved", "ReviewerSelection", "LaneExecution", "FindingSynthesis", "RouteRecommendation", "Terminal"):
        assert state in state_model["states"]
    assert "fallback->parallel_subagent_claim" in state_model["invalid_transitions"]


def test_skill_reference_documents_multi_agent_runtime_contract() -> None:
    root = Path("skills/beacon/beacon-pln-review")
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    reference = (root / "references/multi-agent-runtime.md").read_text(encoding="utf-8")

    assert "references/multi-agent-runtime.md" in skill
    assert "single_process_multi_reviewer" in reference
    assert "not requirement truth" in reference
    assert "not formal QA verdict" in reference


def test_skill_eval_benchmark_covers_multi_agent_review_cases(tmp_path: Path) -> None:
    payload = run_skill_eval_benchmark(tmp_path, version=VERSION)

    assert payload["status"] == "pass"
    covered = set(payload["covered_tc_ids"])
    assert {"TC-021", "TC-022", "TC-023", "TC-024", "TC-025"} <= covered
    root = tmp_path / payload["root"]
    grading = (root / "grading" / "tc-024-pln-review-fallback-transparency.with_skill.json").read_text(encoding="utf-8")
    assert "fallback_transparency_verified" in grading
    assert "fake_parallel_claim_blocked" in grading


def test_implementation_evidence_marker_is_imported_without_reopening() -> None:
    marker_path = Path(".beacon/state") / f"implementation-{FEATURE}.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))

    assert marker["feature_slug"] == FEATURE
    assert marker["version"] == VERSION
    assert marker["status"] == "completed"
    assert marker["imported"] is True
    assert marker["summary_ref"] == f"docs/beacon/{VERSION}/execution/implementation-summary-{FEATURE}.md"

    changed_files = set(marker["changed_files"])
    assert "beacon/utils/planner_review_runtime.py" in changed_files
    assert "tests/test_v160_pln_review_multi_agent.py" in changed_files
    assert f"docs/beacon/{VERSION}/features/{FEATURE}/tests.md" in changed_files

    source_refs = "\n".join(marker["source_refs"])
    assert "tests/test_v160_pln_review_multi_agent.py tests/test_v160_skill_harness_taxonomy.py ->" in source_refs
    assert "beacon skill eval-kit benchmark --version v1.6.0 --json -> pass" in source_refs
