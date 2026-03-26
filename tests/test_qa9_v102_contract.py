"""QA9 v1.0.2 contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.utils.artifact_paths import qa_matrix_output
from beacon.main import app


runner = CliRunner()

PASS_WITH_JUNIT_AND_ASSERT = (
    "python3 -c \"import os,pathlib; "
    "p=pathlib.Path(os.environ.get('BEACON_JUNIT_PATH','.beacon/junit.xml')); "
    "p.parent.mkdir(parents=True,exist_ok=True); "
    "p.write_text('<testsuite tests=\\\"1\\\" failures=\\\"0\\\"></testsuite>', encoding='utf-8'); "
    "print('BEACON_ASSERTIONS=1')\""
)


def _extract_json_from_stdout(text: str) -> dict:
    start = text.find("{")
    assert start >= 0, f"JSON payload missing in output: {text}"
    return json.loads(text[start:])


def test_test_case_create_should_generate_qa9_matrix(tmp_path: Path):
    feature = "QA9 Feature"
    slug = "qa9-feature"

    us_dir = tmp_path / "docs" / "beacon" / "v1.0.2" / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / "v1.0.2" / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / f"{slug}.md").write_text("| ID | 标准 |\n| AC-001 | 功能工作 |\n", encoding="utf-8")
    (prd_dir / f"{slug}.md").write_text("| ID | 标准 |\n| AC-002 | 接口返回200 |\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["test-case", "create", feature, "--project", str(tmp_path), "--version", "v1.0.2"],
    )
    assert result.exit_code == 0, result.stdout

    qa9_path = qa_matrix_output(tmp_path, "v1.0.2", slug, "qa9-matrix")
    payload = json.loads(qa9_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0.2"
    assert len(payload["qa_types"]) == 9
    assert isinstance(payload.get("llm_plan"), dict)
    assert isinstance(payload.get("qa_requirements"), list)
    assert isinstance(payload.get("entries"), list) and payload["entries"]


def test_auto_test_qa9_should_execute_and_write_matrix_evidence(tmp_path: Path):
    matrix_path = qa_matrix_output(tmp_path, "v1.0.2", "qa9-feature", "qa9-matrix")
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_payload = {
        "schema_version": "1.0.2",
        "feature": "QA9 Feature",
        "feature_slug": "qa9-feature",
        "version": "v1.0.2",
        "qa_profile": "web-full",
        "qa_types": ["unit", "interface"],
        "llm_plan": {
            "mode": "rule",
            "model": "beacon-rule-llm-v1",
            "project_scan": {"language": "python", "framework": "pytest", "frontend": "web", "api_spec_refs": [], "risk_points": []},
            "generated_at": "2026-03-03T00:00:00Z",
            "prompt_ref": "test",
        },
        "qa_requirements": [
            {"qa_type": "unit", "required": True, "automation_required": True, "min_cases": 1, "applicability": "required", "waiver": {}},
            {"qa_type": "interface", "required": True, "automation_required": True, "min_cases": 1, "applicability": "required", "waiver": {}},
        ],
        "entries": [
            {
                "tc_id": "TC-001",
                "ac_id": "AC-001",
                "qa_type": "unit",
                "automation": "auto",
                "command": PASS_WITH_JUNIT_AND_ASSERT,
                "assertion": "unit assertion",
                "evidence_path": ".beacon/evidence/test-results/qa9-feature/{run_id}/TC-001.json",
                "status": "pending",
            },
            {
                "tc_id": "TC-002",
                "ac_id": "AC-002",
                "qa_type": "interface",
                "automation": "auto",
                "command": PASS_WITH_JUNIT_AND_ASSERT,
                "assertion": "interface assertion",
                "evidence_path": ".beacon/evidence/test-results/qa9-feature/{run_id}/TC-002.json",
                "status": "pending",
            },
        ],
        "compatibility_matrix": {"browsers": ["chromium"], "devices": ["desktop"], "required_pairs": [{"browser": "chromium", "device": "desktop"}]},
    }
    matrix_path.write_text(json.dumps(matrix_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "qa9",
            "--project",
            str(tmp_path),
            "--qa-matrix-path",
            str(matrix_path),
            "--require-fresh-evidence",
        ],
    )
    assert result.exit_code == 0, result.stdout

    status_payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert status_payload["status"] == "passed"
    assert status_payload["selected_layers"] == ["unit", "interface"]
    matrix_report = status_payload["execution"]["matrix_report"]
    assert matrix_report["status"] == "ok"
    assert matrix_report["evidence_generated"] >= 2


def test_gate_check_release_should_report_qa9_matrix_missing(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "gate",
            "check",
            "release",
            "--mode",
            "strict",
            "--qa-policy",
            "qa9-strict",
            "--json",
            "--project-root",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 2, result.stdout
    payload = _extract_json_from_stdout(result.stdout)
    reason_codes = {item.get("reason_code") for item in payload.get("issues", [])}
    assert "qa9_matrix_missing" in reason_codes


def test_gate_check_json_should_output_pure_json_without_prefix(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "gate",
            "check",
            "release",
            "--mode",
            "strict",
            "--qa-policy",
            "qa9-strict",
            "--json",
            "--project-root",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 2, result.stdout
    assert result.stdout.lstrip().startswith("{"), result.stdout
    payload = json.loads(result.stdout)
    assert payload.get("stage") == "release"
