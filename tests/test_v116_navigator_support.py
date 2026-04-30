from __future__ import annotations

import json
from pathlib import Path

from beacon import __toolkit_version__
from beacon.utils.help_support import build_help_payload
from beacon.utils.revision_state import freeze_revision_state, load_revision_state, reopen_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.story_state import load_story_state
from beacon.utils.writeback import (
    acceptance_projection_transaction_contract,
    record_acceptance_writeback,
    record_implementation_writeback,
    record_verification_writeback,
)


FEATURE = "Navigator Feature"
SLUG = "navigator-feature"
VERSION = "v1.1.6"


def _seed_user_story(root: Path) -> None:
    path = root / "docs" / "beacon" / VERSION / "user-story"
    path.mkdir(parents=True, exist_ok=True)
    (path / f"{SLUG}.md").write_text(
        """# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Lifecycle | Freeze before implement |\n| AC-002 | Navigation | Help suggests next step |\n""",
        encoding="utf-8",
    )
    prd = root / "docs" / "beacon" / VERSION / "prd"
    prd.mkdir(parents=True, exist_ok=True)
    (prd / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    qa = root / "docs" / "beacon" / VERSION / "qa" / "test-cases"
    qa.mkdir(parents=True, exist_ok=True)
    (qa / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (root / ".beacon" / "state").mkdir(parents=True, exist_ok=True)


def test_story_and_revision_state_should_support_freeze_reopen_and_writeback(tmp_path: Path):
    _seed_user_story(tmp_path)

    story = load_story_state(tmp_path, version=VERSION, feature=FEATURE, create_if_missing=True)
    item_ids = [item["id"] for item in story["items"]]
    assert item_ids[:2] == ["AC-001", "AC-002"]
    assert "TASK-001" in item_ids
    assert "TEST-001" in item_ids

    frozen = freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    assert frozen["doc_status"] == "frozen"
    assert frozen["baseline_hash"]

    impl = record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001"],
        changed_files=["beacon/commands/help.py"],
    )
    assert impl["story"]["status"] == "implemented"
    implemented = {item["id"]: item["status"] for item in impl["story"]["items"]}
    assert implemented["AC-001"] == "implemented"

    verify = record_verification_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-verify",
        verified_item_ids=["AC-001"],
        failed_item_ids=["AC-002"],
        evidence_ref=[".beacon/auto-test-status.json"],
    )
    statuses = {item["id"]: item["status"] for item in verify["story"]["items"]}
    assert statuses["AC-001"] == "verified"
    assert statuses["AC-002"] == "failed"
    assert verify["revision"]["delivery_status"] == "blocked"

    previous, reopened = reopen_revision_state(tmp_path, version=VERSION, feature=FEATURE, reason="change-request")
    assert previous["doc_status"] == "superseded"
    assert reopened["revision_id"] == "R2"
    assert reopened["source_revision_id"] == "R1"

    import pytest

    with pytest.raises(ValueError, match="acceptance_revision_not_frozen"):
        record_acceptance_writeback(tmp_path, version=VERSION, feature=FEATURE, accepted_by="qa")


def test_partial_verification_writeback_should_not_promote_story_or_revision_to_verified(tmp_path: Path):
    _seed_user_story(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001", "AC-002"],
        changed_files=["beacon/utils/writeback.py"],
    )

    verify = record_verification_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-verify",
        verified_item_ids=["AC-001"],
        failed_item_ids=[],
        evidence_ref=[".beacon/auto-test-status.json"],
    )
    assert verify["story"]["status"] == "implemented"
    assert verify["revision"]["delivery_status"] == "implemented"


def test_acceptance_writeback_should_write_machine_human_and_runtime_projection(tmp_path: Path):
    _seed_user_story(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001", "AC-002", "TEST-001", "TEST-002"],
        changed_files=["beacon/commands/qa.py"],
    )
    record_verification_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-qa",
        verified_item_ids=["AC-001", "AC-002", "TEST-001", "TEST-002"],
        failed_item_ids=[],
        evidence_ref=[".beacon/qa/status.json", "docs/beacon/v1.1.6/qa/test-cases/navigator-feature.md"],
    )
    run_dir = tmp_path / ".beacon" / "runs" / "run-qa"
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        run_dir / "state.json",
        {"workflow": "workflow.start", "run_id": "run-qa", "version": VERSION, "feature": FEATURE},
    )

    result = record_acceptance_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        accepted_by="qa",
        verdict="passed",
        run_id="run-qa",
        evidence_ref=[".beacon/qa/status.json"],
        source_command='beacon qa run "Navigator Feature" --project-root . --version v1.1.6',
    )

    envelope_path = tmp_path / result["machine_path"]
    markdown_path = tmp_path / result["markdown_path"]
    runtime_path = tmp_path / result["runtime_path"]
    assert envelope_path.exists()
    assert markdown_path.exists()
    assert runtime_path.exists()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    assert envelope["artifact"] == "qa_acceptance_envelope"
    assert envelope["verdict"] == "passed"
    assert envelope["transaction_id"]
    assert envelope["canonical_envelope_ref"] == result["machine_path"]
    assert envelope["markdown_ref"] == result["markdown_path"]
    assert envelope["runtime_projection_ref"] == result["runtime_path"]
    assert envelope["transaction_status"] == "applied"
    assert "docs/beacon/v1.1.6/qa/test-cases/navigator-feature.md" in envelope["test_case_refs"]
    assert ".beacon/qa/status.json" in envelope["evidence_refs"]
    assert envelope["transaction_lineage"]["workflow_memory_ref"]
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# QA Acceptance: Navigator Feature" in markdown
    assert "beacon qa run" in markdown
    contract = acceptance_projection_transaction_contract(tmp_path, version=VERSION, feature=FEATURE)
    assert contract["status"] == "pass"
    assert result["revision"]["delivery_status"] == "accepted"


def test_help_payload_should_recommend_freeze_then_implement_then_quality(tmp_path: Path):
    _seed_user_story(tmp_path)

    # Draft state -> freeze
    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["docs_version"] == VERSION
    assert payload["runtime_version"] == __toolkit_version__
    assert payload["version_context"]["docs_version"] == VERSION
    assert payload["version_context"]["runtime_version"] == __toolkit_version__
    assert payload["next_step"]["action"] == "freeze"
    assert payload["blocked"] is True
    assert "revision_not_frozen" in payload["blocking_reasons"]

    # Frozen state -> implement
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["next_step"]["action"] == "implement"
    assert payload["scores"]["readiness_score"] >= 80

    # Implemented + verify complete -> review quality
    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001", "AC-002"],
        changed_files=["beacon/utils/help_support.py"],
    )
    write_json(
        tmp_path / ".beacon" / "auto-test-status.json",
        {"status": "passed", "summary": {"blocked": 0}},
    )
    run_dir = tmp_path / ".beacon" / "runs" / "run-impl"
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        run_dir / "state.json",
        {"workflow": "workflow.start", "run_id": "run-impl", "version": VERSION, "feature": FEATURE},
    )
    write_json(
        tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json",
        {
            "schema_version": "1.0",
            "updated_at": "now",
            "items": [
                {"run_id": "run-impl", "stage": "think", "event": "stage_started", "source": "t", "source_session_id": "run-impl", "evidence_ref": [], "ts": "2026-01-01T00:00:00Z", "event_id": "1"},
                {"run_id": "run-impl", "stage": "think", "event": "stage_context_injected", "source": "t", "source_session_id": "run-impl", "evidence_ref": [], "ts": "2026-01-01T00:00:01Z", "event_id": "2"},
                {"run_id": "run-impl", "stage": "think", "event": "stage_finished", "source": "t", "source_session_id": "run-impl", "evidence_ref": [], "ts": "2026-01-01T00:00:02Z", "event_id": "3"},
                {"run_id": "run-impl", "stage": "think", "event": "memory_writeback", "source": "t", "source_session_id": "run-impl", "evidence_ref": [], "ts": "2026-01-01T00:00:03Z", "event_id": "4"},
            ],
        },
    )
    write_json(tmp_path / ".beacon" / "memory" / "workflow-lifecycle.index.json", {"schema_version": "1.0", "dedupe_keys": [], "updated_at": "now"})
    matrix = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa"
    matrix.mkdir(parents=True, exist_ok=True)
    evidence = tmp_path / ".beacon" / "evidence" / "TC-001.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("{}", encoding="utf-8")
    write_json(
        matrix / f"{SLUG}.ac-test-matrix.json",
        {"entries": [{"ac_id": "AC-001", "tc_id": "TC-001", "evidence_path": str(evidence.relative_to(tmp_path))}]},
    )
    (tmp_path / ".beacon" / "state" / f"implementation-{SLUG}.json").write_text("{}", encoding="utf-8")
    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["scores"]["test_score"] >= 50
    assert payload["scores"]["closure_score"] >= 40


def test_help_payload_should_route_to_new_revision_after_reopen(tmp_path: Path):
    _seed_user_story(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    reopen_revision_state(tmp_path, version=VERSION, feature=FEATURE, reason="change-request")

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["blocked"] is True
    assert payload["revision_id"] == "R2"
    assert "revision_not_frozen" in payload["blocking_reasons"]
    assert payload["next_step"]["action"] == "freeze"


def test_help_payload_should_prefer_release_ready_scorecard_over_stale_ralph_blocker(tmp_path: Path):
    _seed_user_story(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001", "AC-002"],
        changed_files=["beacon/utils/help_support.py"],
    )
    scorecard_path = tmp_path / ".beacon" / "qa" / "features" / SLUG / "scorecard.json"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        scorecard_path,
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "run_id": "run-qa",
            "continue_decision": "ready_for_release",
            "release_ready": True,
            "stop_reasons": [],
            "unresolved_closure_outcomes": [],
            "coverage_current": {"required_scenarios": 1, "executed_scenarios": 1, "coverage_rate": 1.0},
        },
    )
    write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "passed",
            "evidence_done": True,
            "execution_mode": "feature-aware",
            "run_id": "run-qa",
        },
    )
    matrix = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa"
    matrix.mkdir(parents=True, exist_ok=True)
    evidence = tmp_path / ".beacon" / "evidence" / "TC-001.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("{}", encoding="utf-8")
    write_json(
        matrix / f"{SLUG}.ac-test-matrix.json",
        {"entries": [{"ac_id": "AC-001", "tc_id": "TC-001", "evidence_path": str(evidence.relative_to(tmp_path))}]},
    )
    write_json(
        tmp_path / ".beacon" / "state" / f"implementation-{SLUG}.json",
        {"schema_version": "1.0", "run_id": "run-impl", "feature": FEATURE, "feature_slug": SLUG, "version": VERSION, "status": "completed"},
    )
    ralph_dir = tmp_path / ".beacon" / "ralph"
    ralph_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        ralph_dir / f"{SLUG}.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "phase": "completed",
            "stop_state": "human_blocked",
            "current_blocker": "implementation_reopened",
            "next_action": "implement",
            "recommended_command": f'beacon implement run "{FEATURE}" --project {tmp_path} --version {VERSION} --runner native-single',
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["blocked"] is False
    assert payload["blocked_reason"] == ""
    assert payload["next_step"]["action"] == "release-check"


def test_help_payload_should_expose_ralph_round_and_qa_observability(tmp_path: Path):
    _seed_user_story(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    write_json(
        tmp_path / ".beacon" / "ralph" / f"{SLUG}.json",
        {
            "schema_version": "1.1",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "phase": "completed",
            "stop_state": "human_blocked",
            "current_blocker": "fix blocker",
            "next_action": "implement",
            "recommended_command": f'beacon implement run "{FEATURE}" --project {tmp_path} --version {VERSION} --runner native-single',
            "round_count": 2,
            "last_round_ref": f"docs/beacon/{VERSION}/.machine/execution/ralph-round-{SLUG}-round-002.json",
            "failure_streak": 1,
            "no_delta_streak": 0,
        },
    )
    write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "blocked",
            "evidence_done": False,
            "execution_mode": "story-exhaustive",
            "run_id": "run-qa",
        },
    )
    write_json(
        tmp_path / ".beacon" / "qa" / "current-session.json",
        {
            "schema_version": "1.0",
            "session_id": "session-001",
            "runner_type": "browser-use",
            "updated_at": "now",
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    execution = payload["execution_surface"]
    assert execution["ralph_round_count"] == 2
    assert execution["ralph_last_round_ref"].endswith(f"ralph-round-{SLUG}-round-002.json")
    assert execution["ralph_failure_streak"] == 1
    assert execution["qa_execution_mode"] == "story-exhaustive"
    assert execution["qa_current_session_id"] == "session-001"
    assert execution["qa_runner_type"] == "browser-use"


def test_help_payload_should_ignore_stale_handoff_when_completed_native_run_exists(tmp_path: Path):
    _seed_user_story(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-complete",
        implemented_item_ids=["AC-001", "AC-002"],
        changed_files=["beacon/utils/help_support.py"],
    )
    write_json(
        tmp_path / ".beacon" / "implement" / "run-complete" / "state.json",
        {
            "schema_version": "1.0",
            "run_id": "run-complete",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "completed",
            "runner": "native-single",
            "mode": "ralph",
            "generated_at": "2026-04-16T00:00:00+00:00",
        },
    )
    scorecard_path = tmp_path / ".beacon" / "qa" / "features" / SLUG / "scorecard.json"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        scorecard_path,
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "run_id": "run-qa",
            "continue_decision": "stop_for_repair",
            "release_ready": False,
            "stop_reasons": ["implementation_reopened"],
            "repair_handoff": {
                "action": "implement",
                "reason": "implementation_reopened",
                "command": f'beacon implement run "{FEATURE}" --project {tmp_path} --version {VERSION} --runner native-single',
            },
        },
    )
    write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "blocked",
            "evidence_done": False,
            "execution_mode": "feature-aware",
            "run_id": "run-qa",
        },
    )
    write_json(
        tmp_path / ".beacon" / "ralph" / f"{SLUG}.json",
        {
            "schema_version": "1.1",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "active_run_id": "run-handoff",
            "phase": "waiting_for_handoff",
            "stop_state": "human_blocked",
            "current_blocker": "handoff_required",
            "next_action": "handoff_execute",
            "recommended_command": ".beacon/implement/run-handoff/request.md",
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["next_step"]["action"] == "implement"
    assert "request.md" not in payload["next_step"]["command"]
    execution = payload["execution_surface"]
    assert execution["ralph_phase"] == ""
