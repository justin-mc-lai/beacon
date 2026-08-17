from __future__ import annotations

import json
from pathlib import Path

from beacon.utils import release_scorecard as release_scorecard_module
from beacon.utils.version_surface import sync_version_surfaces


VERSION = "v1.4.0"
FEATURE = "feature-a"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_version_surface_repo(root: Path) -> None:
    (root / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "skills" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / ".trae" / "rules").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state").mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: beacon",
                "version: 1.3.11",
                "description: test",
                "---",
                "",
                "> **Skill Version**: v1.3.11",
                "> **CLI Version**: v1.3.11",
                "",
                "- **当前发布线**：`v1.3.11`",
                "- **当前包版本**：`1.3.11`",
                "- **最新已接受文档线**：`v1.3.11`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "beacon" / "__init__.py").write_text(
        '__version__ = "1.3.11"\n__toolkit_version__ = "v1.3.11"\n',
        encoding="utf-8",
    )
    _write_json(
        root / "beacon" / "version-truth.json",
        {
            "schema_version": "1.0",
            "package_version": "1.4.0",
            "runtime_version": VERSION,
            "docs_default_line": VERSION,
            "current_runtime_release_line": VERSION,
            "planning_lines": [],
            "partial_runtime_supplement_lines": [],
            "lines": {
                "v1.3.11": {"status": "historical_release"},
                VERSION: {"status": "current_runtime_release"},
            },
        },
    )
    _write_json(
        root / "skills" / "beacon" / "metadata.json",
        {
            "name": "beacon",
            "version": "1.3.11",
            "skills": "./",
        },
    )
    (root / ".trae" / "rules" / "project_rules.md").write_text(
        "\n".join(
            [
                "<!-- BEACON:AGENT_SURFACE:START -->",
                "<!-- BEACON:VERSION:v1.3.11 -->",
                "<!-- BEACON:DOCS_VERSION:v1.3.11 -->",
                "# Beacon Trae Project Rules",
                "<!-- BEACON:AGENT_SURFACE:END -->",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _write_json(
        root / ".beacon" / "state" / "agent-surfaces.json",
        {
            "schema_version": "1.0",
            "runtime_version": "v1.3.11",
            "docs_version": "v1.3.11",
            "agents": {"trae": {"agent": "trae"}},
        },
    )


def _seed_release_contract_files(root: Path) -> None:
    docs_root = root / "docs" / "beacon" / VERSION
    (docs_root / ".machine" / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / "change").mkdir(parents=True, exist_ok=True)
    pkg = docs_root / "features" / FEATURE
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "truth.md").write_text(
        "---\n"
        f"slug: {FEATURE}\n"
        f"version: {VERSION}\n"
        "status: frozen\n"
        "language: en\n"
        "parser_contract: beacon-feature-package-v2\n"
        "---\n\n"
        "# Feature A\n\n"
        "## Acceptance Criteria\n\n"
        "| AC ID | Desc |\n"
        "|-------|------|\n"
        "| AC-001 | works |\n",
        encoding="utf-8",
    )
    (pkg / "tests.md").write_text(
        "# Tests\n\n"
        "## Executable AC Test Matrix\n\n"
        "| AC ID | TC ID | Layer | Command | Assertion |\n"
        "|-------|-------|-------|---------|-----------|\n"
        '| AC-001 | TC-001 | contract | `python3 -m pytest -q tests/test_demo.py` | pass |\n',
        encoding="utf-8",
    )
    (pkg / "tasks.md").write_text("# tasks\n", encoding="utf-8")
    (pkg / "evidence.md").write_text("# evidence\n", encoding="utf-8")
    _write_json(
        docs_root / ".machine" / "change" / f"{VERSION}.json",
        {
            "version": VERSION,
            "features": [{"feature_slug": FEATURE}],
        },
    )
    (docs_root / "change" / f"{VERSION}.md").write_text("# change\n", encoding="utf-8")
    _write_json(
        root / ".beacon" / "gate-report.json",
        {
            "status": "Pass",
            "version": VERSION,
            "run_id": "run-123",
            "issues": [],
        },
    )


def _patch_release_ready_baseline(monkeypatch) -> None:
    monkeypatch.setattr(release_scorecard_module, "resolve_target_version", lambda *_args, **_kwargs: VERSION)
    monkeypatch.setattr(release_scorecard_module, "resolve_runtime_version", lambda *_args, **_kwargs: VERSION)
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
            "delivery_status": "verified",
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
    monkeypatch.setattr(release_scorecard_module, "evaluate_semantic_contract", lambda *_args, **_kwargs: {})
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
            "implement": {"prompt_boundary": {"required": False, "status": "not_required", "blocked": False}, "delivery_contract": {}},
            "qa": {"delivery_contract": {}},
            "release": {"release_ready": True},
            "traceability": {},
            "risk_flags": [],
        },
    )


def test_release_scorecard_should_fail_closed_when_version_surface_drift_exists(tmp_path: Path, monkeypatch) -> None:
    _seed_version_surface_repo(tmp_path)
    _seed_release_contract_files(tmp_path)
    _patch_release_ready_baseline(monkeypatch)

    payload = release_scorecard_module.build_release_scorecard(tmp_path, version=VERSION)

    assert payload["version_surface_governance"]["configured"] is True
    assert payload["version_surface_governance"]["status"] == "fail"
    assert payload["version_surface_governance"]["blocked"] is True
    assert payload["release_ready"] is False
    assert payload["host_native_delivery"]["status"] == "blocked"
    assert "version_surface_governance_drift" in payload["host_native_delivery"]["reason_codes"]


def test_release_scorecard_should_recover_after_version_surface_sync(tmp_path: Path, monkeypatch) -> None:
    _seed_version_surface_repo(tmp_path)
    _seed_release_contract_files(tmp_path)
    sync_version_surfaces(tmp_path, dry_run=False)
    _patch_release_ready_baseline(monkeypatch)

    payload = release_scorecard_module.build_release_scorecard(tmp_path, version=VERSION)

    assert payload["version_surface_governance"]["configured"] is True
    assert payload["version_surface_governance"]["status"] == "pass"
    assert payload["version_surface_governance"]["blocked"] is False
    assert payload["release_ready"] is True
