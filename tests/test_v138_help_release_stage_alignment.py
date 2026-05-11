from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.help_support import build_help_payload
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json


VERSION = "v1.3.8"
FEATURE = "V138 Help Release Alignment Feature"
SLUG = "v138-help-release-alignment-feature"


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text("# User Story\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    write_json(base / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json", {"entries": []})


def _seed_execution_state(root: Path) -> None:
    write_json(
        root / ".beacon" / "qa" / "features" / SLUG / "scorecard.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "run_id": "run-qa-001",
            "continue_decision": "ready_for_release",
            "release_ready": True,
            "unresolved_closure_outcomes": [],
            "coverage_current": {"required_scenarios": 1, "executed_scenarios": 1, "coverage_rate": 1.0},
        },
    )
    write_json(
        root / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "passed",
            "execution_mode": "story-exhaustive",
            "evidence_done": True,
        },
    )


def test_v138_help_should_project_release_stage_when_release_gate_is_blocked(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    from beacon.utils import help_support as help_support_module

    monkeypatch.setattr(
        help_support_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "gate": {
                "status": "Blocked",
                "blocked_count": 1,
                "reason_codes": ["evidence_sha256_manifest_mismatch"],
            },
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["current_stage"] == "release"
    assert payload["blocked"] is True
    assert "release_gate_blocked" in payload["blocking_reasons_raw"]
    assert "evidence_sha256_manifest_mismatch" in payload["blocking_reasons_raw"]
    assert payload["next_step"]["action"] == "release-check"
    assert payload["release_summary"]["gate_status"] == "Blocked"


def test_v138_help_should_not_block_release_ready_feature_when_feature_arg_is_slug(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    from beacon.utils import help_support as help_support_module
    from beacon.utils.revision_state import load_revision_state, save_revision_state
    from beacon.utils.runtime import write_json

    revision_state = load_revision_state(tmp_path, version=VERSION, feature=FEATURE, create_if_missing=True)
    revision_state["delivery_status"] = "accepted"
    save_revision_state(tmp_path, version=VERSION, feature=FEATURE, state=revision_state)

    write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"deterministic-implementation-contract-{SLUG}.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "revision_id": "R1",
            "base_branch": "main",
            "target_branch": "beacon/v1.3.8",
            "branch_prefix": "beacon/",
            "worktree_root": str(tmp_path),
            "environment_mode": "local-dev",
            "isolation_strategy": "repo-local isolation",
            "review_status": "approved",
            "approved_by": "codex",
            "reviewed_at": "2026-04-30T00:00:00+00:00",
            "use_git_worktree": False,
            "service_directories": ["."],
            "writable_services": ["."],
            "reference_only_services": ["docs"],
        },
    )

    monkeypatch.setattr(
        help_support_module,
        "build_implementation_plan_gate_payload",
        lambda *_args, **_kwargs: {
            "status": "blocked",
            "blocked": True,
            "reason_code": "technical_review_contract_invalid",
        },
    )
    monkeypatch.setattr(
        help_support_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": True,
            "gate": {"status": "Pass", "blocked_count": 0, "reason_codes": []},
            "qa": {"status": "passed", "release_ready": True, "evidence_done": True},
            "acceptance": {"status": "pass", "release_ready": True, "continue_decision": "ready_for_release"},
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=SLUG)

    assert payload["feature"] == FEATURE
    assert payload["blocked"] is False
    assert "technical_review_contract_invalid" not in payload["blocking_reasons_raw"]
    assert payload["next_step"]["action"] == "release-check"


def test_v138_help_should_route_browser_session_blocker_to_qa_session(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    from beacon.utils import help_support as help_support_module

    write_json(
        tmp_path / ".beacon" / "qa" / "features" / SLUG / "scorecard.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "run_id": "run-qa-browser-001",
            "continue_decision": "stop_for_repair",
            "release_ready": False,
            "stop_reasons": ["protected_surface_session_bridge_missing"],
            "resume_command": f'beacon help --project-root {tmp_path} --version {VERSION} --feature "{FEATURE}"',
        },
    )
    write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "blocked",
            "execution_mode": "story-exhaustive",
            "evidence_done": False,
        },
    )

    monkeypatch.setattr(
        help_support_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "gate": {"status": "Blocked", "blocked_count": 0, "reason_codes": []},
            "qa": {"status": "blocked", "release_ready": False, "evidence_done": False},
            "acceptance": {"status": "blocked", "release_ready": False, "continue_decision": "stop_for_repair"},
        },
    )

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["blocked"] is True
    assert payload["next_step"]["action"] == "qa-session"
    assert "beacon qa session list" in payload["next_step"]["command"]
