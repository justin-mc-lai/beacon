from __future__ import annotations

import importlib
from pathlib import Path

from beacon.commands.gate import GateMode, check_v137_implement_prompt_boundary_contract
from beacon.utils import release_scorecard as release_scorecard_module
from beacon.utils.delivery_kernel import build_delivery_read_model
from beacon.utils.release_scorecard import build_release_scorecard


FEATURE = "Prompt Boundary Feature"
VERSION = "v1.3.7"
gate_module = importlib.import_module("beacon.commands.gate")


def _patch_passing_release_scorecard_world(monkeypatch, *, prompt_boundary: dict | None) -> None:
    def _fake_load_json(path: Path):
        if path.name == "gate-report.json":
            return {"status": "Pass", "version": VERSION, "run_id": "run-qa-001", "issues": []}
        if path.name == "latest.json" and "scorecards" in path.parts:
            return {"counts": {}, "main_kpi": "false_complete_rate", "candidates": []}
        if path.name == "latest.json" and "experiments" in path.parts:
            return {}
        return {}

    monkeypatch.setattr(release_scorecard_module, "_load_json", _fake_load_json)
    monkeypatch.setattr(release_scorecard_module, "resolve_runtime_version", lambda *_args, **_kwargs: VERSION)
    monkeypatch.setattr(
        release_scorecard_module,
        "load_qa_status",
        lambda _root: {
            "feature": FEATURE,
            "status": "passed",
            "evidence_done": True,
            "execution_mode": "feature-aware",
            "version": VERSION,
        },
    )
    monkeypatch.setattr(release_scorecard_module, "_resolve_scorecard_feature", lambda *_args, **_kwargs: FEATURE)
    monkeypatch.setattr(release_scorecard_module, "load_exhaustiveness_report", lambda *_args, **_kwargs: {"status": "passed"})
    monkeypatch.setattr(
        release_scorecard_module,
        "load_feature_qa_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "unresolved_closure_outcomes": [],
        },
    )
    monkeypatch.setattr(release_scorecard_module, "implementation_plan_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        release_scorecard_module,
        "load_implementation_plan_progress",
        lambda *_args, **_kwargs: {"status": "completed", "next_task_id": "", "blocked_task_ids": []},
    )
    monkeypatch.setattr(release_scorecard_module, "list_implementation_git_workflow_contracts", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        release_scorecard_module,
        "load_revision_state",
        lambda *_args, **_kwargs: {"revision_id": "R1", "source_revision_id": "", "baseline_hash": "baseline-hash"},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "_revision_binding",
        lambda *_args, **_kwargs: {
            "status": "pass",
            "reason_code": "",
            "gate_bound_to_latest_revision": True,
        },
    )
    monkeypatch.setattr(release_scorecard_module, "_feature_change_payload", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(release_scorecard_module, "_delivery_type", lambda *_args, **_kwargs: "initial")
    monkeypatch.setattr(
        release_scorecard_module,
        "build_requirement_clarity_gate_payload",
        lambda *_args, **_kwargs: {"status": "pass", "blocked": False, "findings": []},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_requirement_clarity_state",
        lambda *_args, **_kwargs: {"finding_count": 0, "state_path": ".beacon/clarity.json"},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_technical_review_gate_payload",
        lambda *_args, **_kwargs: {"status": "pass", "blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_technical_review_state",
        lambda *_args, **_kwargs: {
            "review_status": "approved",
            "approved_by": "tech-lead",
            "state_path": ".beacon/review.json",
        },
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "_version_change_status",
        lambda *_args, **_kwargs: {
            "status": "pass",
            "markdown_exists": True,
            "json_exists": True,
            "version_match": True,
            "includes_current_feature": True,
            "feature_count": 1,
            "current_feature_slug": "prompt-boundary-feature",
        },
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "evaluate_semantic_contract",
        lambda *_args, **_kwargs: {"status": "pass", "reason_code": "semantic_contract_ok"},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "project_runtime_feature_enabled",
        lambda _project_root, feature_version, **_kwargs: feature_version in {"v1.3.3", "v1.3.7"},
    )
    monkeypatch.setattr(release_scorecard_module, "runtime_feature_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(release_scorecard_module, "load_latest_evo_experiment", lambda *_args, **_kwargs: {})

    qa_payload = {
        "feature": FEATURE,
        "version": VERSION,
        "status": "passed",
        "release_ready": True,
        "execution_mode": "feature-aware",
        "feature_scorecard": {"continue_decision": "ready_for_release"},
    }
    implement_payload = {
        "feature": FEATURE,
        "version": VERSION,
        "status": "completed",
        "mode": "team",
        "runner": "codex-subagents",
        "adapter_type": "native",
    }
    if prompt_boundary is not None:
        implement_payload["prompt_boundary"] = prompt_boundary
    monkeypatch.setattr(
        release_scorecard_module,
        "load_delivery_read_model",
        lambda _project_root, *, version, feature, release_payload=None: build_delivery_read_model(
            feature=feature,
            version=version,
            implement_payload=implement_payload,
            qa_payload=qa_payload,
            release_payload=release_payload,
        ),
    )


def test_v137_delivery_read_model_should_require_prompt_boundary_for_supported_versions() -> None:
    payload = build_delivery_read_model(
        feature=FEATURE,
        version=VERSION,
        implement_payload={"feature": FEATURE, "version": VERSION, "status": "completed"},
        release_payload={"release_ready": True},
    )

    assert payload["implement"]["prompt_boundary"]["required"] is True
    assert payload["implement"]["prompt_boundary"]["status"] == "missing"
    assert payload["implement"]["prompt_boundary"]["blocked"] is True
    assert payload["implement"]["prompt_boundary"]["reason_code"] == "implement_prompt_boundary_missing"
    assert "implement_prompt_boundary_missing" in payload["risk_flags"]


def test_v137_release_scorecard_should_block_release_when_prompt_boundary_missing(monkeypatch, tmp_path: Path) -> None:
    _patch_passing_release_scorecard_world(monkeypatch, prompt_boundary=None)

    payload = build_release_scorecard(tmp_path, version=VERSION)

    assert payload["release_ready"] is False
    assert payload["prompt_boundary"]["status"] == "missing"
    assert payload["prompt_boundary"]["reason_code"] == "implement_prompt_boundary_missing"
    assert "implement_prompt_boundary_missing" in payload["host_native_delivery"]["reason_codes"]


def test_v137_release_scorecard_should_allow_release_when_prompt_boundary_passes(monkeypatch, tmp_path: Path) -> None:
    _patch_passing_release_scorecard_world(
        monkeypatch,
        prompt_boundary={
            "required": True,
            "status": "pass",
            "blocked": False,
            "classification": "in_scope_implementation",
            "reason_code": "",
            "surface": "host_prompt",
        },
    )

    payload = build_release_scorecard(tmp_path, version=VERSION)

    assert payload["release_ready"] is True
    assert payload["prompt_boundary"]["status"] == "pass"
    assert payload["prompt_boundary"]["classification"] == "in_scope_implementation"


def test_v137_gate_prompt_boundary_contract_should_block_when_verdict_not_release_safe(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gate_module, "resolve_runtime_version", lambda *_args, **_kwargs: VERSION)
    monkeypatch.setattr(
        gate_module,
        "project_runtime_feature_enabled",
        lambda _project_root, feature_version, **_kwargs: feature_version == "v1.3.7",
    )
    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "qa": {"feature": FEATURE},
            "prompt_boundary": {
                "required": True,
                "status": "missing",
                "blocked": True,
                "classification": "",
                "reason_code": "implement_prompt_boundary_missing",
                "surface": "host_prompt",
            },
        },
    )

    issues = check_v137_implement_prompt_boundary_contract(tmp_path, GateMode.STRICT, "release", version=VERSION)

    assert len(issues) == 1
    assert issues[0]["reason_code"] == "implement_prompt_boundary_missing"
    assert issues[0]["blocked"] is True
