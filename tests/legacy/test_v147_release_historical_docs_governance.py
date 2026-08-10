from __future__ import annotations

import json
from pathlib import Path

from beacon.utils import release_scorecard as release_scorecard_module


VERSION = "v1.0.0"
FEATURE = "legacy-feature"
SLUG = "legacy-feature"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_release_baseline(root: Path) -> None:
    docs_root = root / "docs" / "beacon" / VERSION
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (docs_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (docs_root / "execution" / "index.md").mkdir(parents=True, exist_ok=True)


def _patch_passing_world(monkeypatch) -> None:
    monkeypatch.setattr(release_scorecard_module, "resolve_target_version", lambda *_args, **_kwargs: VERSION)
    monkeypatch.setattr(release_scorecard_module, "resolve_runtime_version", lambda *_args, **_kwargs: "v1.4.6")
    monkeypatch.setattr(release_scorecard_module, "runtime_feature_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(release_scorecard_module, "version_requires_prototype", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(release_scorecard_module, "implementation_plan_supported", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(
        release_scorecard_module,
        "validate_evidence_manifest",
        lambda *_args, **_kwargs: {"status": "pass", "blocked": False, "issues": [], "blocked_count": 0},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_qa_status",
        lambda *_args, **_kwargs: {
            "feature": FEATURE,
            "version": VERSION,
            "status": "passed",
            "evidence_done": True,
            "release_ready": True,
            "project_profile_gate": {"status": "pass"},
        },
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_exhaustiveness_report",
        lambda *_args, **_kwargs: {"status": "passed", "score": 1.0, "threshold": 0.8},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_feature_qa_scorecard",
        lambda *_args, **_kwargs: {
            "feature": FEATURE,
            "feature_slug": SLUG,
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "unresolved_closure_outcomes": [],
            "project_profile_gate_status": "pass",
            "review_required_count": 0,
            "needs_replay_count": 0,
            "coverage_current": {
                "required_scenarios": 1,
                "executed_scenarios": 1,
                "coverage_rate": 1.0,
            },
        },
    )
    monkeypatch.setattr(release_scorecard_module, "load_implementation_plan_progress", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(release_scorecard_module, "load_latest_evo_experiment", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(release_scorecard_module, "list_implementation_git_workflow_contracts", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        release_scorecard_module,
        "load_revision_state",
        lambda *_args, **_kwargs: {
            "revision_id": "R1",
            "source_revision_id": "",
            "doc_status": "frozen",
            "delivery_status": "accepted",
        },
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
    monkeypatch.setattr(
        release_scorecard_module,
        "build_requirement_completeness_gate",
        lambda *_args, **_kwargs: {"status": "pass"},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_requirement_clarity_gate_payload",
        lambda *_args, **_kwargs: {"status": "pass", "blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_requirement_clarity_state",
        lambda *_args, **_kwargs: {"status": "pass", "finding_count": 0},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_technical_review_gate_payload",
        lambda *_args, **_kwargs: {"status": "pass", "blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_technical_review_state",
        lambda *_args, **_kwargs: {"review_status": "approved"},
    )
    monkeypatch.setattr(release_scorecard_module, "evaluate_semantic_contract", lambda *_args, **_kwargs: {"status": "blocked", "reason_code": "semantic_should_not_apply"})
    monkeypatch.setattr(
        release_scorecard_module,
        "build_test_contract_gate_payload",
        lambda *_args, **_kwargs: {"release_gate": {"status": "pass", "blocked": False, "reason_codes": []}},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_acceptance_kit_projection",
        lambda *_args, **_kwargs: {"summary": {"all_layers_passed": True}},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "acceptance_projection_transaction_contract",
        lambda *_args, **_kwargs: {"status": "pass", "reason_code": ""},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_delivery_read_model",
        lambda *_args, **_kwargs: {
            "implement": {
                "prompt_boundary": {
                    "required": True,
                    "status": "blocked",
                    "blocked": True,
                    "classification": "requirement_change",
                    "reason_code": "prompt_should_not_apply",
                    "surface": "host_prompt",
                },
                "delivery_contract": {},
            },
            "qa": {"delivery_contract": {}},
            "release": {"release_ready": True},
            "traceability": {},
            "risk_flags": [],
        },
    )


def test_v147_release_scorecard_should_not_apply_new_release_governance_to_historical_docs_line(
    tmp_path: Path,
    monkeypatch,
) -> None:
    docs_root = tmp_path / "docs" / "beacon" / VERSION
    (tmp_path / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    docs_root.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (docs_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (docs_root / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (docs_root / ".machine" / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "change" / f"{VERSION}.json").write_text(
        json.dumps({"version": VERSION, "features": [{"feature_slug": SLUG}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (docs_root / "change" / f"{VERSION}.md").write_text("# change\n", encoding="utf-8")
    _write_json(
        tmp_path / ".beacon" / "state" / "project-onboarding.json",
        {
            "schema_version": "1.0",
            "project_mode": "takeover",
            "docs_version": VERSION,
            "runtime_version": "v1.4.6",
            "qa_managed": False,
            "gate_managed": False,
            "runtime_capability_lines": ["v1.3.3", "v1.3.7", "v1.3.9", "v1.4.6"],
        },
    )
    _write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {"status": "Pass", "version": VERSION, "run_id": "run-123", "issues": []},
    )
    _patch_passing_world(monkeypatch)

    payload = release_scorecard_module.build_release_scorecard(tmp_path, version=VERSION)

    assert payload["release_ready"] is True
    assert payload["gate"]["status"] == "Pass"
    assert payload["semantic"] == {}
    assert payload["prompt_boundary"]["status"] in {"blocked", "not_required", "missing", "pass"}
    assert "semantic_should_not_apply" not in payload["host_native_delivery"]["reason_codes"]
    assert "prompt_should_not_apply" not in payload["host_native_delivery"]["reason_codes"]
