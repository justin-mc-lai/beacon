"""Beacon v1.0.2 closure feature tests."""

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


def _extract_json_payload(stdout: str) -> dict:
    start = stdout.find("{")
    assert start >= 0, stdout
    return json.loads(stdout[start:])


def test_think_start_should_emit_qa_strategy(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "think",
            "start",
            "qa9 closure",
            "--project",
            str(tmp_path),
            "--version",
            "v1.0.2",
        ],
    )
    assert result.exit_code == 0, result.stdout
    progress_path = tmp_path / ".beacon" / "state" / "think-progress" / "v1.0.2.json"
    payload = json.loads(progress_path.read_text(encoding="utf-8"))
    strategy = payload.get("qa_strategy")
    assert isinstance(strategy, dict)
    for key in ("project_type", "qa_applicability", "runner_policy", "command_baseline"):
        assert key in strategy


def test_test_case_create_should_map_each_ac_and_cover_required_qa_types(tmp_path: Path):
    feature = "QA9 closure"
    slug = "qa9-closure"
    us_dir = tmp_path / "docs" / "beacon" / "v1.0.2" / "user-story"
    us_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / f"{slug}.md").write_text(
        "\n".join(
            [
                "| AC | Desc |",
                "| AC-001 | 登录页面可打开 |",
                "| AC-002 | 接口返回200 |",
                "| AC-003 | 错误提示可见 |",
            ]
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "test-case",
            "create",
            feature,
            "--project",
            str(tmp_path),
            "--version",
            "v1.0.2",
            "--qa-profile",
            "web-full",
            "--ui-runner",
            "browser-use",
        ],
    )
    assert result.exit_code == 0, result.stdout
    qa9_path = qa_matrix_output(tmp_path, "v1.0.2", slug, "qa9-matrix")
    payload = json.loads(qa9_path.read_text(encoding="utf-8"))
    entries = payload["entries"]
    qa_types = payload["qa_types"]
    represented_ac = {str(item.get("ac_id")) for item in entries}
    assert {"AC-001", "AC-002", "AC-003"}.issubset(represented_ac)
    represented_qa_types = {str(item.get("qa_type")) for item in entries}
    assert set(qa_types).issubset(represented_qa_types)
    assert any("browser_use_runner" in str(item.get("command", "")) for item in entries if item.get("qa_type") == "functional")


def test_auto_test_should_backfill_qa9_summary_and_sync_progress(tmp_path: Path):
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
        ],
    )
    assert result.exit_code == 0, result.stdout
    status_payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    summary = status_payload.get("qa9", {}).get("summary", {})
    assert summary.get("cases_total") == 2
    assert summary.get("passed") == 2

    sync_result = runner.invoke(app, ["test-progress", "sync", "--project", str(tmp_path)])
    assert sync_result.exit_code == 0, sync_result.stdout
    progress_payload = json.loads((tmp_path / ".beacon" / "test-progress.json").read_text(encoding="utf-8"))
    assert progress_payload["total"] == 2
    assert progress_payload["passed"] == 2


def test_gate_should_block_expired_waiver_and_missing_pair_execution(tmp_path: Path):
    root = tmp_path / "docs" / "beacon" / "v1.0.2"
    (root / "execution").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (root / "prd").mkdir(parents=True, exist_ok=True)
    (root / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "release").mkdir(parents=True, exist_ok=True)
    (root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (root / "prd" / "qa9-feature.md").write_text("# PRD\n", encoding="utf-8")
    (root / "user-story" / "qa9-feature.md").write_text("# US\n", encoding="utf-8")
    (root / "release" / "v1.0.2.md").write_text("# Release\n", encoding="utf-8")
    matrix_path = qa_matrix_output(tmp_path, "v1.0.2", "qa9-feature", "qa9-matrix")
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    (root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / "qa" / "test-cases" / "qa9-feature.md").write_text("# Test Cases\n", encoding="utf-8")
    matrix_payload = {
        "schema_version": "1.0.2",
        "feature": "QA9 Feature",
        "feature_slug": "qa9-feature",
        "version": "v1.0.2",
        "qa_profile": "web-full",
        "qa_types": ["compatibility"],
        "llm_plan": {"mode": "rule", "model": "beacon-rule-llm-v1", "project_scan": {"language": "python"}},
        "qa_requirements": [
            {
                "qa_type": "functional",
                "required": False,
                "automation_required": False,
                "min_cases": 0,
                "applicability": "na",
                "waiver": {"ticket": "T-1", "approved_by": "qa", "expires_at": "2020-01-01T00:00:00Z"},
            }
        ],
        "entries": [
            {
                "tc_id": "TC-001",
                "ac_id": "AC-001",
                "qa_type": "compatibility",
                "automation": "auto",
                "command": "python3 -c \"print('1 passed')\"",
                "assertion": "compat assertion",
                "evidence_path": ".beacon/evidence/test-results/qa9-feature/{run_id}/TC-001.json",
                "status": "pending",
            }
        ],
        "compatibility_matrix": {
            "browsers": ["chromium"],
            "devices": ["desktop"],
            "required_pairs": [{"browser": "chromium", "device": "desktop"}],
        },
    }
    matrix_path.write_text(json.dumps(matrix_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # mock auto-test status with compatibility pass but no pair execution evidence
    status_payload = {
        "scope": "qa9",
        "status": "passed",
        "quality_issues": [],
        "execution": {
            "run_id": "run-test",
            "layers": [
                {
                    "layer": "compatibility",
                    "status": "passed",
                    "execution_fingerprint": "fp-1",
                    "started_at": "2026-03-04T00:00:00+00:00",
                    "ended_at": "2026-03-04T00:00:01+00:00",
                }
            ],
        },
        "qa9": {
            "compatibility": {
                "required_pairs": [{"browser": "chromium", "device": "desktop"}],
                "executed_pairs": [],
            }
        },
    }
    beacon_dir = tmp_path / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "auto-test-status.json").write_text(json.dumps(status_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (beacon_dir / "evidence-signature-chain.json").write_text(
        json.dumps(
            [
                {
                    "run_id": "run-test",
                    "summary_path": ".beacon/auto-test-status.json",
                    "summary_sha256": "",
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

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
            "--project-root",
            str(tmp_path),
            "--json",
        ],
    )
    assert result.exit_code == 2, result.stdout
    payload = _extract_json_payload(result.stdout)
    reason_codes = {item.get("reason_code") for item in payload.get("issues", [])}
    assert "manual_waiver_unapproved" in reason_codes
    assert "compatibility_execution_missing" in reason_codes


def test_workflow_auto_should_require_explicit_implementation_command(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "workflow",
            "start",
            "workflow-noop",
            "--project",
            str(tmp_path),
            "--version",
            "v1.0.2",
            "--auto",
            "--verify-scope",
            "unit",
            "--verify-unit-command",
            "python3 -c \"print('BEACON_ASSERTIONS=1')\"",
        ],
    )
    assert result.exit_code == 2, result.stdout
    assert "implementation stage requires explicit external command execution" in result.stdout
