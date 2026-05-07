from __future__ import annotations

import hashlib
import importlib
import json

gate_module = importlib.import_module("beacon.commands.gate")
from beacon.utils.artifact_paths import execution_file_output
from beacon.utils import release_scorecard as release_scorecard_module


def test_v138_release_scorecard_should_block_when_evidence_manifest_hash_drift_exists(
    tmp_path,
    monkeypatch,
):
    version = "v1.3.8"
    docs_root = tmp_path / "docs" / "beacon" / version
    execution_root = docs_root / "execution"
    execution_root.mkdir(parents=True, exist_ok=True)
    tracked_doc = execution_root / "index.md"
    tracked_doc.write_text("# initial\n", encoding="utf-8")
    tracked_sha = hashlib.sha256(tracked_doc.read_bytes()).hexdigest()

    beacon_dir = tmp_path / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-123", "issues": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": "run-123",
                "entries": [
                    {
                        "path": f"docs/beacon/{version}/execution/index.md",
                        "sha256": tracked_sha,
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    change_machine = docs_root / ".machine" / "change"
    change_machine.mkdir(parents=True, exist_ok=True)
    (change_machine / f"{version}.json").write_text(
        json.dumps(
            {
                "version": version,
                "features": [{"feature_slug": "feature-a"}],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    change_docs = docs_root / "change"
    change_docs.mkdir(parents=True, exist_ok=True)
    (change_docs / f"{version}.md").write_text("# release\n", encoding="utf-8")

    tracked_doc.write_text("# drifted\n", encoding="utf-8")

    monkeypatch.setattr(release_scorecard_module, "resolve_target_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "resolve_runtime_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "runtime_feature_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(release_scorecard_module, "project_runtime_feature_enabled", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(release_scorecard_module, "version_requires_prototype", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(release_scorecard_module, "implementation_plan_supported", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(
        release_scorecard_module,
        "load_qa_status",
        lambda *_args, **_kwargs: {
            "feature": "feature-a",
            "version": version,
            "status": "passed",
            "evidence_done": True,
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
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "unresolved_closure_outcomes": [],
            "project_profile_gate_status": "not_configured",
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
            "delivery_status": "verified",
        },
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_requirement_clarity_gate_payload",
        lambda *_args, **_kwargs: {"blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_requirement_clarity_state",
        lambda *_args, **_kwargs: {"status": "pass", "finding_count": 0},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_technical_review_gate_payload",
        lambda *_args, **_kwargs: {"blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_technical_review_state",
        lambda *_args, **_kwargs: {"review_status": "approved"},
    )
    monkeypatch.setattr(release_scorecard_module, "evaluate_semantic_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        release_scorecard_module,
        "load_delivery_read_model",
        lambda *_args, **_kwargs: {
            "implement": {
                "prompt_boundary": {
                    "required": True,
                    "status": "pass",
                    "blocked": False,
                    "classification": "in_scope_implementation",
                    "reason_code": "",
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

    payload = release_scorecard_module.build_release_scorecard(tmp_path, version=version)

    assert payload["gate"]["status"] == "Blocked"
    assert "evidence_sha256_manifest_mismatch" in payload["gate"]["reason_codes"]
    assert payload["evidence_manifest"]["status"] == "blocked"
    assert payload["release_ready"] is False


def test_v138_release_scorecard_should_prefer_authoritative_summary_prompt_boundary(tmp_path, monkeypatch):
    version = "v1.3.8"
    feature = "feature-a"
    docs_root = tmp_path / "docs" / "beacon" / version
    execution_root = docs_root / "execution"
    execution_root.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (docs_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (execution_root / "index.md").write_text("# Execution\n", encoding="utf-8")
    (docs_root / "release").mkdir(parents=True, exist_ok=True)
    (docs_root / "release" / f"{version}.md").write_text("# Release\n", encoding="utf-8")
    change_machine = docs_root / ".machine" / "change"
    change_machine.mkdir(parents=True, exist_ok=True)
    (change_machine / f"{version}.json").write_text(
        json.dumps({"version": version, "features": [{"feature_slug": "feature-a"}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    change_docs = docs_root / "change"
    change_docs.mkdir(parents=True, exist_ok=True)
    (change_docs / f"{version}.md").write_text("# change\n", encoding="utf-8")

    summary_path = execution_file_output(tmp_path, version, "implementation-summary-feature-a.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(
            {
                "feature": feature,
                "feature_slug": "feature-a",
                "version": version,
                "status": "completed",
                "prompt_boundary": {
                    "required": True,
                    "status": "pass",
                    "blocked": False,
                    "classification": "in_scope_implementation",
                    "reason_code": "",
                    "surface": "host_prompt",
                },
                "delivery_contract": {
                    "feature": feature,
                    "version": version,
                    "requirement_binding": {},
                    "traceability_refs": [],
                    "risk_flags": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    runtime_state = tmp_path / ".beacon" / "implement" / "run-123" / "state.json"
    runtime_state.parent.mkdir(parents=True, exist_ok=True)
    runtime_state.write_text(
        json.dumps(
            {
                "feature": feature,
                "feature_slug": "feature-a",
                "version": version,
                "status": "blocked",
                "reason_code": "revision_cleanup_delta_missing",
                "run_id": "run-123",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-123", "issues": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    monkeypatch.setattr(release_scorecard_module, "resolve_target_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "resolve_runtime_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "runtime_feature_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(release_scorecard_module, "project_runtime_feature_enabled", lambda *_args, **_kwargs: True)
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
            "feature": feature,
            "version": version,
            "status": "passed",
            "evidence_done": True,
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
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "unresolved_closure_outcomes": [],
            "project_profile_gate_status": "not_configured",
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
            "delivery_status": "verified",
        },
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_requirement_clarity_gate_payload",
        lambda *_args, **_kwargs: {"blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_requirement_clarity_state",
        lambda *_args, **_kwargs: {"status": "pass", "finding_count": 0},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_technical_review_gate_payload",
        lambda *_args, **_kwargs: {"blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_technical_review_state",
        lambda *_args, **_kwargs: {"review_status": "approved"},
    )
    monkeypatch.setattr(release_scorecard_module, "evaluate_semantic_contract", lambda *_args, **_kwargs: {})

    payload = release_scorecard_module.build_release_scorecard(tmp_path, version=version)

    assert payload["prompt_boundary"]["status"] == "pass"
    assert payload["prompt_boundary"]["blocked"] is False


def test_v138_release_scorecard_should_prefer_latest_release_ready_feature_over_stale_global_qa_feature(
    tmp_path,
    monkeypatch,
):
    version = "v1.3.8"
    docs_root = tmp_path / "docs" / "beacon" / version
    (docs_root / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "change" / f"{version}.json").write_text(
        json.dumps({"version": version, "features": [{"feature_slug": "admin-merchandising-analytics"}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (docs_root / "change" / f"{version}.md").write_text("# change\n", encoding="utf-8")
    (tmp_path / ".beacon" / "qa" / "features" / "admin-merchandising-analytics").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "qa" / "features" / "admin-merchandising-analytics" / "scorecard.json").write_text(
        json.dumps(
            {
                "feature": "admin-merchandising-analytics",
                "feature_slug": "admin-merchandising-analytics",
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "unresolved_closure_outcomes": [],
                "updated_at": "2026-05-03T10:00:00Z",
                "coverage_current": {
                    "required_scenarios": 2,
                    "executed_scenarios": 2,
                    "coverage_rate": 1.0,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-123", "issues": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    monkeypatch.setattr(release_scorecard_module, "resolve_target_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "resolve_runtime_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "runtime_feature_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(release_scorecard_module, "project_runtime_feature_enabled", lambda *_args, **_kwargs: True)
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
            "feature": "evis-supply-website-core",
            "version": version,
            "status": "passed",
            "evidence_done": True,
        },
    )
    monkeypatch.setattr(release_scorecard_module, "load_exhaustiveness_report", lambda *_args, **_kwargs: {"status": "passed"})
    monkeypatch.setattr(
        release_scorecard_module,
        "load_feature_qa_scorecard",
        lambda _project_root, feature=None, **_kwargs: json.loads(
            (
                tmp_path / ".beacon" / "qa" / "features" / (feature or "") / "scorecard.json"
            ).read_text(encoding="utf-8")
        )
        if feature == "admin-merchandising-analytics"
        else {},
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
            "delivery_status": "verified",
        },
    )
    monkeypatch.setattr(release_scorecard_module, "build_requirement_clarity_gate_payload", lambda *_args, **_kwargs: {"blocked": False})
    monkeypatch.setattr(release_scorecard_module, "load_requirement_clarity_state", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(release_scorecard_module, "build_technical_review_gate_payload", lambda *_args, **_kwargs: {"blocked": False})
    monkeypatch.setattr(release_scorecard_module, "load_technical_review_state", lambda *_args, **_kwargs: {"review_status": "approved"})
    monkeypatch.setattr(release_scorecard_module, "evaluate_semantic_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        release_scorecard_module,
        "load_delivery_read_model",
        lambda *_args, **_kwargs: {
            "implement": {"prompt_boundary": {"required": False, "status": "not_required", "blocked": False}, "delivery_contract": {}},
            "qa": {"delivery_contract": {}},
            "release": {"release_ready": True},
            "traceability": {},
            "risk_flags": [],
        },
    )

    payload = release_scorecard_module.build_release_scorecard(tmp_path, version=version)

    assert payload["qa"]["feature"] == "admin-merchandising-analytics"
    assert payload["change_documents"]["current_feature_slug"] == "admin-merchandising-analytics"


def test_v138_release_scorecard_should_prefer_latest_revision_feature_for_version_scoped_release_checks(
    tmp_path,
    monkeypatch,
):
    version = "v1.3.8"
    docs_root = tmp_path / "docs" / "beacon" / version
    (docs_root / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "change" / f"{version}.json").write_text(
        json.dumps({"version": version, "features": [{"feature_slug": "latest-version-feature"}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (docs_root / "change" / f"{version}.md").write_text("# change\n", encoding="utf-8")
    (docs_root / ".machine" / "execution" / "latest-version-feature.revision.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": "latest-version-feature",
                "feature_slug": "latest-version-feature",
                "version": version,
                "revision_id": "R1",
                "doc_status": "frozen",
                "delivery_status": "verified",
                "lifecycle_status": "frozen",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "qa" / "features" / "stale-global-feature").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "qa" / "features" / "stale-global-feature" / "scorecard.json").write_text(
        json.dumps(
            {
                "feature": "stale-global-feature",
                "feature_slug": "stale-global-feature",
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "unresolved_closure_outcomes": [],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(release_scorecard_module, "resolve_target_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "resolve_runtime_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "runtime_feature_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(release_scorecard_module, "project_runtime_feature_enabled", lambda *_args, **_kwargs: True)
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
            "feature": "stale-global-feature",
            "version": version,
            "status": "passed",
            "evidence_done": True,
            "release_ready": True,
            "continue_decision": "ready_for_release",
        },
    )
    monkeypatch.setattr(release_scorecard_module, "load_exhaustiveness_report", lambda *_args, **_kwargs: {"status": "passed"})
    monkeypatch.setattr(
        release_scorecard_module,
        "load_feature_qa_scorecard",
        lambda _project_root, feature=None, **_kwargs: {
            "feature": feature or "stale-global-feature",
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "unresolved_closure_outcomes": [],
            "review_required_count": 0,
            "needs_replay_count": 0,
            "release_confidence_min": 1.0,
            "coverage_current": {},
        }
        if feature == "latest-version-feature"
        else {
            "feature": "stale-global-feature",
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "unresolved_closure_outcomes": [],
            "review_required_count": 0,
            "needs_replay_count": 0,
            "release_confidence_min": 1.0,
            "coverage_current": {},
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
            "delivery_status": "verified",
        },
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_requirement_clarity_gate_payload",
        lambda *_args, **_kwargs: {"blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_requirement_clarity_state",
        lambda *_args, **_kwargs: {"status": "pass", "finding_count": 0},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "build_technical_review_gate_payload",
        lambda *_args, **_kwargs: {"blocked": False},
    )
    monkeypatch.setattr(
        release_scorecard_module,
        "load_technical_review_state",
        lambda *_args, **_kwargs: {"review_status": "approved"},
    )
    monkeypatch.setattr(release_scorecard_module, "evaluate_semantic_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        release_scorecard_module,
        "load_delivery_read_model",
        lambda *_args, **_kwargs: {
            "implement": {
                "prompt_boundary": {
                    "required": True,
                    "status": "pass",
                    "blocked": False,
                    "classification": "in_scope_implementation",
                    "reason_code": "",
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

    payload = release_scorecard_module.build_release_scorecard(tmp_path, version=version)

    assert payload["feature_qa_scorecard"]["feature"] == "latest-version-feature"
    assert payload["qa"]["feature"] == "latest-version-feature"


def test_v138_release_scorecard_should_not_mark_v139_release_ready_without_acceptance_transaction(
    tmp_path,
    monkeypatch,
):
    version = "v1.3.9"
    feature = "feature-a"
    docs_root = tmp_path / "docs" / "beacon" / version
    (docs_root / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "change" / f"{version}.json").write_text(
        json.dumps({"version": version, "features": [{"feature_slug": feature}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (docs_root / "change" / f"{version}.md").write_text("# change\n", encoding="utf-8")
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-123", "issues": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    monkeypatch.setattr(release_scorecard_module, "resolve_target_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "resolve_runtime_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(release_scorecard_module, "runtime_feature_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(release_scorecard_module, "project_runtime_feature_enabled", lambda *_args, **_kwargs: True)
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
            "feature": feature,
            "version": version,
            "status": "passed",
            "release_ready": True,
            "evidence_done": False,
            "project_profile_gate": {"status": "pass"},
        },
    )
    monkeypatch.setattr(release_scorecard_module, "load_exhaustiveness_report", lambda *_args, **_kwargs: {"status": "passed"})
    monkeypatch.setattr(release_scorecard_module, "load_feature_qa_scorecard", lambda *_args, **_kwargs: {})
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
            "delivery_status": "verified",
        },
    )
    monkeypatch.setattr(release_scorecard_module, "build_requirement_clarity_gate_payload", lambda *_args, **_kwargs: {"blocked": False})
    monkeypatch.setattr(release_scorecard_module, "load_requirement_clarity_state", lambda *_args, **_kwargs: {"status": "pass", "finding_count": 0})
    monkeypatch.setattr(release_scorecard_module, "build_technical_review_gate_payload", lambda *_args, **_kwargs: {"blocked": False})
    monkeypatch.setattr(release_scorecard_module, "load_technical_review_state", lambda *_args, **_kwargs: {"review_status": "approved"})
    monkeypatch.setattr(release_scorecard_module, "evaluate_semantic_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        release_scorecard_module,
        "load_delivery_read_model",
        lambda *_args, **_kwargs: {
            "implement": {"prompt_boundary": {"required": False, "status": "not_required", "blocked": False}, "delivery_contract": {}},
            "qa": {"delivery_contract": {}},
            "release": {"release_ready": True},
            "traceability": {},
            "risk_flags": [],
        },
    )

    payload = release_scorecard_module.build_release_scorecard(tmp_path, version=version)

    assert payload["acceptance"]["source"] == "qa_status"
    assert payload["acceptance"]["status"] == "pass"
    assert payload["qa"]["release_ready"] is True
    assert payload["acceptance_transaction"]["status"] == "warn"
    assert payload["release_ready"] is False


def test_v138_gate_precision_contract_should_consume_converged_release_acceptance_truth_for_v139(
    tmp_path,
    monkeypatch,
):
    version = "v1.3.9"
    monkeypatch.setattr(gate_module, "_resolved_gate_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "qa": {
                "feature": "feature-a",
                "project_profile_gate_status": "pass",
            },
            "acceptance": {
                "source": "qa_status",
                "feature": "feature-a",
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "project_profile_gate_status": "pass",
                "unresolved_closure_outcomes": [],
                "review_required_count": 0,
                "needs_replay_count": 0,
                "release_confidence_min": 0.95,
            },
        },
    )

    issues = gate_module.check_v110_precision_contract(
        tmp_path,
        gate_module.GateMode.STRICT,
        "release",
        version,
    )

    assert issues == []


def test_v138_gate_precision_contract_should_report_version_surface_governance_drift_for_v140(
    tmp_path,
    monkeypatch,
):
    version = "v1.4.0"
    monkeypatch.setattr(gate_module, "_resolved_gate_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "qa": {
                "feature": "feature-a",
                "project_profile_gate_status": "pass",
            },
            "acceptance": {
                "source": "qa_status",
                "feature": "feature-a",
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "project_profile_gate_status": "pass",
                "unresolved_closure_outcomes": [],
                "review_required_count": 0,
                "needs_replay_count": 0,
                "release_confidence_min": 0.95,
            },
            "version_surface_governance": {
                "configured": True,
                "status": "fail",
                "blocked": True,
                "reason_code": "version_surface_governance_drift",
                "manifest_path": "beacon/version-truth.json",
            },
        },
    )

    issues = gate_module.check_v110_precision_contract(
        tmp_path,
        gate_module.GateMode.STRICT,
        "release",
        version,
    )

    reason_codes = {item["reason_code"] for item in issues}
    assert "version_surface_governance_drift" in reason_codes
