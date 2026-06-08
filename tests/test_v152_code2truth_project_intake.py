from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import SUPPORT_COMMANDS, SUPPORTED_SUBCOMMANDS
from beacon.main import app
from beacon.utils.code2truth import run_code2truth_intake
from beacon.utils.feature_package import validate_feature_package
from beacon.utils.implement_adapters import build_default_task_prompt
from beacon.utils.implement_prompt_boundary import evaluate_implement_prompt_boundary
from beacon.utils.subagent_readiness import delegation_readiness_precheck


VERSION = "v1.5.2"
FEATURE = "code2truth-project-intake"


runner = CliRunner()


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_beacon_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# Global Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# Summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/execution/project-skill-qa-evolution-blueprint.md", "# Skill Blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/index.md", "# Source Architecture\n")
    _write(root, f"docs/beacon/{VERSION}/release/{VERSION}.md", "# Release\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/features/{FEATURE}/truth.md",
        "\n".join(
            [
                "---",
                f"slug: {FEATURE}",
                f"version: {VERSION}",
                "status: frozen",
                "language: zh",
                "canonical_refs:",
                f"  prd: docs/beacon/{VERSION}/features/{FEATURE}/truth.md",
                f"  user_story: docs/beacon/{VERSION}/features/{FEATURE}/truth.md",
                f"  test_case: docs/beacon/{VERSION}/features/{FEATURE}/tests.md",
                "parser_contract: beacon-feature-package-v1",
                "truth_source_model: feature_package_authoritative",
                "truth_map_contract: beacon-truth-map-v1",
                "---",
                "",
                "# Feature Truth",
                "",
                "## Acceptance Criteria",
                "",
                "| AC ID | Theme | Description |",
                "|---|---|---|",
                "| AC-001 | source-inventory | Intake builds source inventory. |",
                "| AC-002 | provider-boundary | Providers are evidence only. |",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/features/{FEATURE}/tests.md",
        "\n".join(
            [
                "# Tests",
                "",
                "## Coverage Matrix",
                "",
                "| AC ID | TC ID | Layer | Assertion |",
                "|---|---|---|---|",
                "| AC-001 | TC-001 | integration | Inventory exists. |",
                "| AC-002 | TC-002 | contract | Provider is not truth. |",
            ]
        )
        + "\n",
    )
    _write(root, f"docs/beacon/{VERSION}/features/{FEATURE}/tasks.md", "# Tasks\n\n- [ ] TASK-001 Intake\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/features/{FEATURE}/evidence.md",
        "\n".join(
            [
                "# Evidence",
                "",
                "| Surface | Authority | Canonical Artifact | Status | Route |",
                "|---|---|---|---|---|",
                f"| feature-package | requirement_truth | docs/beacon/{VERSION}/features/{FEATURE}/truth.md | authoritative | truth |",
                f"| package-tests | test_truth | docs/beacon/{VERSION}/features/{FEATURE}/tests.md | authoritative | test-case |",
            ]
        )
        + "\n",
    )


def _seed_existing_project(root: Path) -> None:
    _write(root, "README.md", "# Existing Project\n")
    _write(root, "skills/demo/SKILL.md", "---\nname: demo\n---\n# Demo\n")
    _write(root, "src/cli.py", "def main():\n    return 'ok'\n")
    _write(root, "tests/test_cli.py", "def test_cli():\n    assert True\n")
    _write(root, ".beacon/state/runtime.json", json.dumps({"status": "runtime"}, ensure_ascii=False))
    _write(root, ".omc/state/session.json", json.dumps({"status": "runtime"}, ensure_ascii=False))
    _write(
        root,
        ".understand-anything/knowledge-graph.json",
        json.dumps({"nodes": [{"id": "src/cli.py"}], "edges": []}, ensure_ascii=False),
    )
    _write(root, ".understand-anything/graph-build-report.json", json.dumps({"status": "ok"}, ensure_ascii=False))


def test_code2truth_command_is_support_surface() -> None:
    assert "code2truth" in SUPPORT_COMMANDS
    assert "code2truth" in SUPPORTED_SUBCOMMANDS


def test_code2truth_intake_builds_candidate_truth_without_authority(tmp_path: Path) -> None:
    beacon_root = tmp_path / "beacon"
    target = tmp_path / "existing"
    _seed_beacon_docs(beacon_root)
    _seed_existing_project(target)

    payload = run_code2truth_intake(
        beacon_root,
        target_project_root=target,
        version=VERSION,
        feature=FEATURE,
        use_lighthouse=False,
    )

    assert payload["status"] == "candidate"
    assert payload["truth_authority"] is False
    assert payload["promotion_gate"]["user_confirmation_required"] is True
    assert payload["promotion_gate"]["direct_package_write_allowed"] is False
    assert payload["source_inventory"]["counts"]["skill"] == 1
    assert payload["source_inventory"]["counts"]["test"] == 1
    inventory_paths = {item["path"] for item in payload["source_inventory"]["files"]}
    assert ".beacon/state/runtime.json" not in inventory_paths
    assert ".omc/state/session.json" not in inventory_paths
    assert ".understand-anything/knowledge-graph.json" not in inventory_paths
    assert payload["providers"]["understand_anything"]["available"] is True
    assert payload["providers"]["understand_anything"]["truth_authority"] is False
    assert payload["candidate_truth"]["claims"]
    assert (beacon_root / ".beacon" / "code2truth" / FEATURE / "intake.json").exists()
    assert (beacon_root / ".beacon" / "code2truth" / FEATURE / "intake.md").exists()


def test_code2truth_cli_emits_json_and_keeps_package_truth_authoritative(tmp_path: Path) -> None:
    beacon_root = tmp_path / "beacon"
    target = tmp_path / "existing"
    _seed_beacon_docs(beacon_root)
    _seed_existing_project(target)

    result = runner.invoke(
        app,
        [
            "code2truth",
            "intake",
            str(target),
            "--project",
            str(beacon_root),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--no-lighthouse",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["authority"] == "support_evidence_only"
    assert payload["truth_map_verify"]["status"] == "pass"
    assert payload["promotion_gate"]["package_truth_paths"]["truth"].endswith(f"features/{FEATURE}/truth.md")
    package_validation = validate_feature_package(beacon_root, version=VERSION, feature=FEATURE)
    assert package_validation["status"] == "pass"


def test_package_authoritative_delegation_does_not_require_legacy_triptych(tmp_path: Path) -> None:
    _seed_beacon_docs(tmp_path)
    execution_root = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution"
    execution_root.mkdir(parents=True)
    (execution_root / f"implementation-plan-{FEATURE}.json").write_text("{}", encoding="utf-8")
    (execution_root / f"git-workflow-{FEATURE}.json").write_text("{}", encoding="utf-8")

    payload = delegation_readiness_precheck(tmp_path, feature=FEATURE, version=VERSION)
    checks = {item["name"]: item for item in payload["checks"]}

    assert payload["status"] == "pass"
    assert checks["package_truth_present"]["ok"] is True
    assert checks["package_tests_present"]["ok"] is True
    assert checks["truth_map_verify_pass"]["ok"] is True
    assert "prd_present" not in checks
    assert "qa_baseline_bundle_present" not in payload["blocked_checks"]


def test_package_root_task_prompt_does_not_duplicate_feature_path() -> None:
    prompt = build_default_task_prompt(
        feature=FEATURE,
        version=VERSION,
        source_of_truth_root=f"docs/beacon/{VERSION}/features/{FEATURE}",
        feature_slug=FEATURE,
        result_file=".beacon/implement/run-001/result.json",
    )

    assert f"docs/beacon/{VERSION}/features/{FEATURE}/truth.md" in prompt
    assert f"features/{FEATURE}/features/{FEATURE}" not in prompt


def test_prompt_boundary_frozen_refs_use_feature_package_for_v152(tmp_path: Path) -> None:
    _seed_beacon_docs(tmp_path)

    payload = evaluate_implement_prompt_boundary(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        host_prompt=build_default_task_prompt(
            feature=FEATURE,
            version=VERSION,
            project_root=tmp_path,
            source_of_truth_root=f"docs/beacon/{VERSION}/features/{FEATURE}",
            feature_slug=FEATURE,
            result_file=".beacon/implement/run-001/result.json",
        ),
    )

    assert payload["status"] == "pass"
    assert payload["frozen_refs"] == [
        f"docs/beacon/{VERSION}/features/{FEATURE}/truth.md",
        f"docs/beacon/{VERSION}/features/{FEATURE}/tests.md",
        f"docs/beacon/{VERSION}/features/{FEATURE}/tasks.md",
        f"docs/beacon/{VERSION}/features/{FEATURE}/evidence.md",
    ]


def test_freeze_accepts_relative_project_root(tmp_path: Path) -> None:
    _seed_beacon_docs(tmp_path)
    previous_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["freeze", FEATURE, "--project", ".", "--version", VERSION, "--json"])
    finally:
        os.chdir(previous_cwd)

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "frozen"
    assert payload["requirement_clarity_report"]["json"].startswith(f"docs/beacon/{VERSION}/.machine/execution/")
