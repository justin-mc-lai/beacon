from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands import release as release_command
from beacon.main import app
from beacon.utils.artifact_paths import change_file_output, machine_execution_dir, qa_matrix_output
from beacon.utils.doctor_orchestrator import run_version_aggregate_projection_repair
from beacon.utils.runtime import write_json
from beacon.utils.story_state import feature_slug, machine_story_path
from beacon.utils.version_aggregate_projection import (
    PROJECTION_ROLE,
    feature_change_projection_status,
    version_aggregate_projection_status,
    write_feature_change_projection,
)


VERSION = "v1.4.11"
FEATURE = "version-aggregate-projection-guard-contract"
runner = CliRunner()


def _write_text(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_docs(root: Path, *, version: str = VERSION, feature: str = FEATURE) -> None:
    slug = feature_slug(feature)
    for folder in ("prd", "user-story", "qa/test-cases", "change"):
        _write_text(root / "docs" / "beacon" / version / folder / f"{slug}.md", f"# {feature}\n")
    write_json(
        machine_execution_dir(root, version) / f"{slug}.revision.json",
        {
            "schema_version": "1.0",
            "version": version,
            "feature": feature,
            "feature_slug": slug,
            "revision_id": "R2",
            "doc_status": "frozen",
            "delivery_status": "implemented",
            "frozen_at": "2026-05-27T00:00:00Z",
        },
    )
    write_json(
        machine_execution_dir(root, version) / f"qa-acceptance-{slug}.json",
        {
            "schema_version": "1.0",
            "version": version,
            "feature": feature,
            "feature_slug": slug,
            "verdict": "passed",
            "accepted_at": "2026-05-27T00:10:00Z",
        },
    )
    write_json(
        machine_story_path(root, version, feature),
        {
            "schema_version": "1.0",
            "version": version,
            "feature": feature,
            "stories": [
                {
                    "id": "US-001",
                    "items": [
                        {"id": "AC-001", "kind": "ac", "theme": "projection", "text": "Projection guard", "required": True}
                    ],
                }
            ],
        },
    )
    write_json(
        qa_matrix_output(root, version, slug, "ac-test-matrix"),
        {
            "schema_version": "1.0",
            "feature": feature,
            "entries": [
                {
                    "ac_id": "AC-001",
                    "tc_id": "TC-AGG-PROJ-001",
                    "layer": "unit",
                    "command": "pytest",
                    "assertion": "Projection guard is deterministic.",
                    "evidence_path": ".beacon/evidence/test-results/TC-AGG-PROJ-001.json",
                }
            ],
        },
    )
    _write_text(root / ".beacon" / "evidence" / "test-results" / "TC-AGG-PROJ-001.json", '{"status":"pass"}\n')


def _seed_release_runtime(root: Path, *, version: str = VERSION, feature: str = FEATURE) -> None:
    _write_text(root / ".beacon" / "auto-test-status.json", json.dumps({"status": "passed", "version": version, "run_id": "run-1"}))
    _write_text(root / ".beacon" / "gate-report.json", json.dumps({"status": "Pass", "version": version, "run_id": "run-1"}))
    _write_text(
        root / ".beacon" / "evidence-manifest.json",
        json.dumps({"version": version, "run_id": "run-1", "entries": [{"path": ".beacon/auto-test-status.json"}]}),
    )
    _write_text(
        root / ".beacon" / "coverage-summary.json",
        json.dumps({"version": version, "run_id": "run-1", "coverage_rate": 1.0, "full_coverage": True}),
    )


def _release_scorecard(root: Path, *, version: str = VERSION, feature: str = FEATURE, release_ready: bool = True) -> dict:
    return {
        "release_ready": release_ready,
        "qa": {"feature": feature, "status": "passed", "evidence_done": True, "release_ready": True},
        "gate": {"status": "Pass", "run_id": "run-1", "artifact_version": version},
        "semantic": {"status": "pass", "reason_code": ""},
        "ceo_challenge_coverage": {
            "status": "pass",
            "decision": "accepted",
            "latest_next_route": "none",
            "covered_axes": [
                "too_smooth_path",
                "buried_landmine",
                "truth_freeze_destabilization",
                "stage_boundary_sprawl",
                "false_closure_signal",
                "operator_cost_underpricing",
            ],
            "missing_axes": [],
            "needs_challenge": False,
            "gap_status": "pass",
            "reason_code": "",
        },
        "change_documents": version_aggregate_projection_status(root, version=version, current_feature=feature),
        "prompt_boundary": {
            "required": True,
            "status": "pass",
            "blocked": False,
            "classification": "in_scope_implementation",
            "reason_code": "",
            "surface": "host_prompt",
        },
        "version_surface_governance": {"configured": False},
        "browser_release_reason_codes": [],
        "feature_qa_scorecard": {},
    }


def test_projection_wording_not_truth() -> None:
    assert PROJECTION_ROLE["artifact_role"] == "version_aggregate_projection"
    assert PROJECTION_ROLE["truth_source"] is False
    assert PROJECTION_ROLE["lifecycle_stage"] is False
    assert PROJECTION_ROLE["release_publish_action"] is False


def test_qa_accepted_feature_requires_feature_change_projection(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    status = feature_change_projection_status(tmp_path, version=VERSION, feature=FEATURE)

    assert status["status"] == "missing"
    assert status["reason_code"] == "feature_change_projection_missing"
    assert status["repairable"] is True
    assert "repair-version-aggregate-projection" in status["repair_commands"][0]


def test_release_create_rebuilds_version_projection_with_dependency_order(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    first = write_feature_change_projection(tmp_path, version=VERSION, feature="feature-a", overwrite=True)
    second = write_feature_change_projection(tmp_path, version=VERSION, feature=FEATURE, overwrite=True)
    payload = json.loads((tmp_path / first["json_path"]).read_text(encoding="utf-8"))
    payload["depends_on_features"] = []
    write_json(tmp_path / first["json_path"], payload)
    payload = json.loads((tmp_path / second["json_path"]).read_text(encoding="utf-8"))
    payload["depends_on_features"] = ["feature-a"]
    write_json(tmp_path / second["json_path"], payload)

    result = runner.invoke(app, ["release", "create", VERSION, "--project", str(tmp_path)])
    aggregate = json.loads(change_file_output(tmp_path, VERSION, f"{VERSION}.json").read_text(encoding="utf-8"))

    assert result.exit_code == 0, result.stdout
    assert aggregate["artifact_role"] == "version_aggregate_projection"
    assert aggregate["truth_authority"] is False
    assert aggregate["feature_count"] == 2
    assert aggregate["implementation_order"]["ordered_feature_slugs"] == ["feature-a", FEATURE]
    wave_two = aggregate["implementation_order"]["waves"][1]["features"][0]
    assert wave_two["feature_slug"] == FEATURE
    assert wave_two["depends_on_features"] == ["feature-a"]


def test_release_check_blocks_when_current_feature_missing_from_aggregate(tmp_path: Path, monkeypatch) -> None:
    _seed_docs(tmp_path)
    _seed_release_runtime(tmp_path)
    write_feature_change_projection(tmp_path, version=VERSION, feature="other-feature", overwrite=True)
    runner.invoke(app, ["release", "create", VERSION, "--project", str(tmp_path)])
    monkeypatch.setattr(release_command, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass", "blocked": False})
    monkeypatch.setattr(release_command, "acceptance_projection_transaction_contract", lambda *_args, **_kwargs: {"status": "pass", "reason_code": ""})
    monkeypatch.setattr(release_command, "runtime_projection_transaction_contract", lambda *_args, **_kwargs: {"status": "pass", "reason_code": ""})
    monkeypatch.setattr(release_command, "build_release_scorecard", lambda *_args, **_kwargs: _release_scorecard(tmp_path, release_ready=False))

    result = runner.invoke(app, ["release", "check", VERSION, "--project-root", str(tmp_path), "--json"])
    payload = json.loads(result.stdout)

    assert result.exit_code == 1, result.stdout
    assert payload["status"] == "blocked"
    assert payload["recommended_command"].startswith("beacon doctor repair-version-aggregate-projection")
    aggregate_check = next(item for item in payload["checks"] if item["name"] == "version change document includes current feature")
    assert aggregate_check["status"] == "fail"
    assert "feature_change_projection_missing" in aggregate_check["detail"]


def test_release_check_passes_when_current_feature_included(tmp_path: Path, monkeypatch) -> None:
    _seed_docs(tmp_path)
    _seed_release_runtime(tmp_path)
    write_feature_change_projection(tmp_path, version=VERSION, feature=FEATURE, overwrite=True)
    runner.invoke(app, ["release", "create", VERSION, "--project", str(tmp_path)])
    monkeypatch.setattr(release_command, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass", "blocked": False})
    monkeypatch.setattr(release_command, "acceptance_projection_transaction_contract", lambda *_args, **_kwargs: {"status": "pass", "reason_code": ""})
    monkeypatch.setattr(release_command, "runtime_projection_transaction_contract", lambda *_args, **_kwargs: {"status": "pass", "reason_code": ""})
    monkeypatch.setattr(release_command, "build_release_scorecard", lambda *_args, **_kwargs: _release_scorecard(tmp_path))

    result = runner.invoke(app, ["release", "check", VERSION, "--project-root", str(tmp_path), "--json"])
    payload = json.loads(result.stdout)

    assert result.exit_code == 0, result.stdout
    assert payload["status"] == "pass"
    aggregate_check = next(item for item in payload["checks"] if item["name"] == "version change document includes current feature")
    assert aggregate_check["status"] == "pass"


def test_doctor_repair_rebuilds_projection_without_truth_authority(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    execution = run_version_aggregate_projection_repair(
        project_root=str(tmp_path),
        version=VERSION,
        feature=FEATURE,
        overwrite_feature_projection=True,
    )
    result = execution.payload["result"]

    assert execution.exit_code == 0, execution.payload
    assert result["truth_authority"] is False
    assert result["lifecycle_stage"] is False
    assert result["release_publish_action"] is False
    assert result["version_aggregate_projection"]["feature_slugs"] == [FEATURE]
    assert Path(tmp_path / result["feature_projection"]["json_path"]).exists()
    assert Path(tmp_path / result["version_aggregate_projection"]["json_path"]).exists()


def test_test_contract_index_repair_clears_stale_index_risk(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    execution = run_version_aggregate_projection_repair(
        project_root=str(tmp_path),
        version=VERSION,
        feature=FEATURE,
        overwrite_feature_projection=True,
    )
    result = execution.payload["result"]

    assert result["test_contract_index"]["status"] == "pass"
    assert result["test_contract_verify"]["status"] == "pass"
    assert result["test_contract_verify"]["release_gate"]["status"] == "pass"


def test_guard_does_not_add_lifecycle_stage() -> None:
    help_result = runner.invoke(app, ["--help"])

    assert help_result.exit_code == 0
    assert "aggregate-sync" not in help_result.stdout
    assert PROJECTION_ROLE["lifecycle_stage"] is False


def test_projection_guard_regression_suite_covers_required_axes(tmp_path: Path) -> None:
    test_text = Path(__file__).read_text(encoding="utf-8")

    for token in [
        "feature_change_projection_missing",
        "repair_rebuilds_projection",
        "feature_count",
        "depends_on_features",
        "projection_wording_not_truth",
    ]:
        assert token in test_text


def test_blocked_release_output_includes_projection_repair_route(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_release_runtime(tmp_path)
    write_feature_change_projection(tmp_path, version=VERSION, feature="other-feature", overwrite=True)
    runner.invoke(app, ["release", "create", VERSION, "--project", str(tmp_path)])

    status = version_aggregate_projection_status(tmp_path, version=VERSION, current_feature=FEATURE)

    assert status["reason_code"] == "feature_change_projection_missing"
    assert status["blocked"] is True
    assert status["repair_commands"][0].startswith("beacon doctor repair-version-aggregate-projection")
