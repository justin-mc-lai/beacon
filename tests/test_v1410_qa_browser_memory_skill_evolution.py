from __future__ import annotations

from pathlib import Path

from beacon.utils.browser_task_compiler import build_browser_task
from beacon.utils.qa_browser_memory import (
    admit_browser_memory,
    audit_skill_evolution_proposal,
    build_browser_memory_candidate,
    build_memory_influence,
    build_qa_memory_release_support,
    build_skill_evolution_proposal,
    classify_reflection_family,
    retrieve_browser_memory,
)
from beacon.utils.release_scorecard import summarize_release_scorecard


def _browser_evidence(**overrides):
    payload = {
        "run_id": "run-browser-001",
        "source_command": "npx playwright test tests/e2e/create-match.spec.ts --reporter=json",
        "runner": "playwright",
        "browser": "chromium",
        "target_url": "http://localhost:3000/matches/create",
        "result_status": "passed",
        "accepted_test_ids": ["TC-QA-MEM-001"],
        "evidence_refs": [
            "playwright-report/results.json",
            "test-results/create-match/function-screenshot.png",
            "test-results/create-match/ui-screenshot.png",
            "test-results/create-match/ux-trace.zip",
            "test-results/create-match/compatibility-chromium.json",
            "test-results/create-match/session-storage-state.json",
            "test-results/create-match/state_data-network.json",
        ],
        "axes": ["function", "ui", "ux", "compatibility", "session", "state_data"],
        "auth_mode": "storage_state",
        "session_ref": "test-results/create-match/session-storage-state.json",
    }
    payload.update(overrides)
    return payload


def _admitted_memory():
    candidate = build_browser_memory_candidate(
        _browser_evidence(),
        feature="qa-browser-memory-and-skill-evolution-advisory-loop",
        version="v1.4.10",
        project_id="beacon",
        ac_ids=["AC-001"],
        test_ids=["TC-QA-MEM-001"],
        selector_hints=["button:has-text('Create')"],
        action_hints=["fill match name before submit"],
        task_hints=["verify ranking state after completion"],
    )
    return admit_browser_memory(candidate)


def test_browser_memory_capture_requires_current_browser_evidence() -> None:
    memory = _admitted_memory()

    assert memory["admission_status"] == "admitted"
    assert memory["feature"] == "qa-browser-memory-and-skill-evolution-advisory-loop"
    assert memory["target_host"] == "localhost:3000"
    assert memory["runner"] == "playwright"
    assert memory["browser"] == "chromium"
    assert memory["auth_mode"] == "storage_state"
    assert memory["ac_ids"] == ["AC-001"]
    assert memory["test_ids"] == ["TC-QA-MEM-001"]
    assert memory["evidence_refs"]
    assert memory["truth_authority"] is False


def test_browser_memory_admission_rejects_non_acceptance_evidence() -> None:
    cases = [
        _browser_evidence(source_command="npx playwright test --list", evidence_refs=["playwright-list.txt"]),
        _browser_evidence(source_command="npx playwright test --dry-run", evidence_refs=["dry-run.txt"]),
        _browser_evidence(notes="documentation only", evidence_refs=["docs.md"]),
        _browser_evidence(target_url="", evidence_refs=[]),
    ]

    for evidence in cases:
        memory = admit_browser_memory(
            build_browser_memory_candidate(
                evidence,
                feature="qa-browser-memory-and-skill-evolution-advisory-loop",
                version="v1.4.10",
                project_id="beacon",
                ac_ids=["AC-002"],
                test_ids=["TC-QA-MEM-002"],
            )
        )
        assert memory["admission_status"] == "rejected"
        assert memory["validation"]["blocked"] is True


def test_admitted_memory_is_retrieved_for_matching_qa_context() -> None:
    memory = _admitted_memory()

    result = retrieve_browser_memory(
        [memory],
        feature="qa-browser-memory-and-skill-evolution-advisory-loop",
        version="v1.4.10",
        target_host="localhost:3000",
        browser="chromium",
        runner="playwright",
        auth_mode="storage_state",
    )

    assert result["status"] == "matched"
    assert result["matches"][0]["memory_id"] == memory["memory_id"]


def test_memory_influence_guides_runner_session_selector_and_task_hints(tmp_path: Path) -> None:
    memory = _admitted_memory()
    influence = build_memory_influence(memory)

    task = build_browser_task(
        item={"feature": "qa-browser-memory-and-skill-evolution-advisory-loop", "tc_id": "TC-QA-MEM-004"},
        qa_type="functional",
        mode="qa",
        project_root=tmp_path,
        browser_memory=memory,
    )

    assert "runner" in influence["influence_fields"]
    assert "session_bridge" in influence["influence_fields"]
    assert "selector_hints" in influence["influence_fields"]
    assert task["runner_contract"]["memory_runner_hint"] == "playwright"
    assert task["session"]["memory_session_ref"] == "test-results/create-match/session-storage-state.json"
    assert "button:has-text('Create')" in task["memory_hints"]


def test_memory_influence_has_no_truth_or_verdict_authority() -> None:
    influence = build_memory_influence(_admitted_memory())

    assert influence["support_evidence_only"] is True
    assert influence["runtime_evidence_only"] is True
    assert influence["truth_authority"] is False
    assert influence["verdict_authority"] is False
    assert influence["release_pass_evidence"] is False
    assert influence["counts_as_pass_evidence"] is False


def test_stale_conflicting_or_mismatched_memory_downgrades_or_blocks_reuse() -> None:
    memory = _admitted_memory()

    result = retrieve_browser_memory(
        [memory],
        feature="qa-browser-memory-and-skill-evolution-advisory-loop",
        version="v1.4.10",
        target_host="example.com",
        browser="firefox",
        runner="playwright",
        auth_mode="storage_state",
    )

    assert result["blocked"] is True
    assert "browser_memory_target_host_mismatch" in result["reason_codes"]
    assert "browser_memory_browser_mismatch" in result["reason_codes"]


def test_skill_evolution_classifies_reflection_family() -> None:
    assert classify_reflection_family("new route discovered") == "Discovery"
    assert classify_reflection_family("reuse selector to optimize session") == "Optimization"
    assert classify_reflection_family("skill instruction missed runner admission rule") == "SkillDefect"
    assert classify_reflection_family("execution timeout forgot retry") == "ExecutionLapse"


def test_skill_evolution_outputs_proposal_only_without_mutation(tmp_path: Path) -> None:
    skill_file = tmp_path / "skills" / "beacon-qa" / "SKILL.md"
    skill_file.parent.mkdir(parents=True)
    skill_file.write_text("original", encoding="utf-8")

    proposal = build_skill_evolution_proposal(
        observation="skill instruction missed runner admission rule",
        failure_family="skill_defect",
        trace_refs=["trace.zip"],
        affected_ac_ids=["AC-008"],
        affected_test_ids=["TC-QA-MEM-008"],
        evidence_refs=["playwright-report/results.json"],
        target_surface="skill_patch_draft",
        patch_draft_refs=[".beacon/proposals/skill.patch"],
    )

    assert proposal["reflection_family"] == "SkillDefect"
    assert proposal["mutation_executed"] is False
    assert proposal["audit"]["status"] == "pass"
    assert skill_file.read_text(encoding="utf-8") == "original"


def test_skill_evolution_proposal_binds_trace_ac_test_evidence_route_and_risk() -> None:
    proposal = build_skill_evolution_proposal(
        observation="optimization candidate",
        failure_family="execution_lapse",
        trace_refs=["trace.zip"],
        affected_ac_ids=["AC-009"],
        affected_test_ids=["TC-QA-MEM-009"],
        evidence_refs=["report.json"],
        target_surface="runner_admission_rule",
        risk="high",
    )

    assert proposal["trace_refs"] == ["trace.zip"]
    assert proposal["affected_ac_ids"] == ["AC-009"]
    assert proposal["affected_test_ids"] == ["TC-QA-MEM-009"]
    assert proposal["evidence_refs"] == ["report.json"]
    assert proposal["recommended_route"] == "beacon-change/refreeze"
    assert proposal["risk"] == "high"


def test_independent_auditor_blocks_authority_bypass_and_overfit() -> None:
    proposal = build_skill_evolution_proposal(
        observation="skill instruction",
        failure_family="skill_defect",
        trace_refs=[],
        affected_ac_ids=[],
        affected_test_ids=[],
        evidence_refs=[],
        target_surface="qa_verdict",
    )
    proposal["truth_authority"] = True
    proposal["single_project_overfit"] = True

    audit = audit_skill_evolution_proposal(proposal)
    reason_codes = set(audit["reason_codes"])

    assert audit["blocked"] is True
    assert "authority_bypass" in reason_codes
    assert "missing_evidence_binding" in reason_codes
    assert "missing_ac_test_binding" in reason_codes
    assert "lifecycle_stage_sprawl" in reason_codes
    assert "single_project_overfitting" in reason_codes


def test_accepted_proposals_route_to_change_refreeze_before_implementation() -> None:
    accepted = build_skill_evolution_proposal(
        observation="skill instruction missed route",
        failure_family="skill_defect",
        trace_refs=["trace.zip"],
        affected_ac_ids=["AC-011"],
        affected_test_ids=["TC-QA-MEM-011"],
        evidence_refs=["report.json"],
        target_surface="skill_patch_draft",
        status="accepted_for_change",
    )
    rejected = dict(accepted)
    rejected["lifecycle_status"] = "rejected"
    rejected["recommended_route"] = "support-evidence-only"

    assert accepted["recommended_route"] == "beacon-change/refreeze"
    assert rejected["recommended_route"] == "support-evidence-only"


def test_release_consumes_formal_current_qa_closure_not_memory_or_proposals() -> None:
    memory = _admitted_memory()
    proposal = build_skill_evolution_proposal(
        observation="skill instruction missed route",
        failure_family="skill_defect",
        trace_refs=["trace.zip"],
        affected_ac_ids=["AC-012"],
        affected_test_ids=["TC-QA-MEM-012"],
        evidence_refs=["report.json"],
        target_surface="skill_patch_draft",
        status="accepted_for_change",
    )
    support = build_qa_memory_release_support(memories=[memory], proposals=[proposal], formal_qa_closure={})

    assert support["release_pass_evidence"] is False
    assert support["formal_qa_release_ready"] is False

    summary = summarize_release_scorecard(
        {
            "release_ready": False,
            "feature_qa_scorecard": {"release_ready": False},
            "qa_browser_memory_release_support": support,
        }
    )

    assert summary["release_ready"] is False
    assert summary["qa_browser_memory_count"] == 1
    assert summary["qa_skill_evolution_proposal_count"] == 1
    assert summary["qa_browser_memory_release_pass_evidence"] is False
