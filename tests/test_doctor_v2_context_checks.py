"""Doctor v2 context compatibility checks."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon import __toolkit_version__
from beacon.main import app
from beacon.utils.context_files import (
    MANAGED_BLOCK_END,
    build_default_agents_managed_block,
    build_default_claude_managed_block,
)
from beacon.utils.runtime import write_json


runner = CliRunner()
VERSION = "v1.5.2"
FEATURE = "doctor-truth-source-demo"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _prepare_basic_project(tmp_path: Path) -> None:
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "skills").mkdir(parents=True, exist_ok=True)


def _managed_context(version: str) -> tuple[str, str]:
    return (
        build_default_agents_managed_block(version),
        build_default_claude_managed_block(version),
    )


def _incompatibility_names(payload: dict[str, object]) -> set[str]:
    return {str(item.get("name")) for item in payload.get("incompatibilities", []) if isinstance(item, dict)}


def test_missing_context_files_should_trigger_presence_incompatibility(tmp_path: Path):
    _prepare_basic_project(tmp_path)

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert "context_files_presence" in _incompatibility_names(payload)


def test_malformed_markers_should_trigger_integrity_incompatibility(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    agents, claude = _managed_context("v3.8.4")
    (tmp_path / "AGENTS.md").write_text(agents.replace(MANAGED_BLOCK_END, ""), encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(claude, encoding="utf-8")

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert "managed_block_integrity" in _incompatibility_names(payload)


def test_version_marker_drift_should_trigger_version_drift_incompatibility(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    agents, _ = _managed_context("v3.8.4")
    _, claude = _managed_context("v3.8.3")
    (tmp_path / "AGENTS.md").write_text(agents, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(claude, encoding="utf-8")

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert "managed_block_version_drift" in _incompatibility_names(payload)


def test_clean_managed_files_should_not_trigger_new_context_incompatibilities(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    runtime_version = str(__toolkit_version__)
    agents, claude = _managed_context(runtime_version)
    (tmp_path / "AGENTS.md").write_text(agents, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(claude, encoding="utf-8")

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    names = _incompatibility_names(json.loads(result.stdout))

    assert "context_files_presence" not in names
    assert "managed_block_integrity" not in names
    assert "managed_block_version_drift" not in names


def test_doctor_should_report_dual_versions_and_warn_on_suspicious_runtime_named_docs_root(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    runtime_version = str(__toolkit_version__)
    docs_root = tmp_path / "docs" / "beacon"
    (docs_root / "v0.1.0" / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / runtime_version / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / runtime_version / "SUMMARY.md").write_text("# Beacon Summary\n", encoding="utf-8")
    write_json(
        tmp_path / ".beacon" / "state" / "project-onboarding.json",
        {
            "schema_version": "1.0",
            "docs_version": "v0.1.0",
            "runtime_version": runtime_version,
        },
    )
    agents, claude = _managed_context(runtime_version)
    (tmp_path / "AGENTS.md").write_text(agents, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(claude, encoding="utf-8")

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert payload["docs_version"] == "v0.1.0"
    assert payload["runtime_version"] == runtime_version
    assert payload["project"]["active_docs_version"] == "v0.1.0"
    assert payload["project"]["active_runtime_version"] == runtime_version
    assert "docs_runtime_separation_integrity" not in _incompatibility_names(payload)
    assert "suspicious_runtime_named_docs_root" in _incompatibility_names(payload)


def test_doctor_should_report_truth_source_mismatch_and_repair_routes(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    runtime_version = str(__toolkit_version__)
    agents, claude = _managed_context(runtime_version)
    (tmp_path / "AGENTS.md").write_text(agents, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(claude, encoding="utf-8")
    _write(tmp_path, "docs/beacon/global-boundaries.md", "# Global Boundaries\n")
    _write(tmp_path, f"docs/beacon/{VERSION}/SUMMARY.md", "# Summary\n")
    _write(tmp_path, f"docs/beacon/{VERSION}/execution/boundaries.md", "# Boundaries\n")
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/features/{FEATURE}/truth.md",
        "\n".join(
            [
                "---",
                f"slug: {FEATURE}",
                f"version: {VERSION}",
                "status: frozen",
                "language: en",
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
                "| AC-001 | demo | Demo acceptance. |",
            ]
        )
        + "\n",
    )
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/features/{FEATURE}/tests.md",
        "\n".join(
            [
                "# Tests",
                "",
                "| AC ID | TC ID | Layer | Assertion |",
                "|---|---|---|---|",
                "| AC-001 | TC-001 | unit | Demo covered. |",
            ]
        )
        + "\n",
    )
    _write(tmp_path, f"docs/beacon/{VERSION}/features/{FEATURE}/tasks.md", "# Tasks\n\n- [ ] TASK-001 Demo\n")
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/features/{FEATURE}/evidence.md",
        "# Evidence\n\n| Surface | Authority | Canonical Artifact | Status | Route |\n|---|---|---|---|---|\n",
    )
    write_json(
        tmp_path / f"docs/beacon/{VERSION}/.machine/requirement/{FEATURE}.truth-map.json",
        {
            "schema_version": "1.0",
            "truth_map_contract": "beacon-truth-map-v1",
            "truth_source_model": "feature_package_authoritative",
            "truth_package_contract": "beacon-feature-package-v2",
            "machine_json_role": "generated_state_not_truth",
            "generated_by": "beacon.truth_map.resolver",
            "feature": FEATURE,
            "feature_slug": FEATURE,
            "version": VERSION,
            "truth_authority": "markdown_feature_package",
            "json_authority": False,
            "source_hashes": {
                "truth": "stale",
                "tests": "stale",
                "tasks": "stale",
                "evidence": "stale",
            },
        },
    )

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    mismatch = next(item for item in payload["incompatibilities"] if item["name"] == "truth_source_mismatch")

    assert mismatch["status"] == "FAIL"
    assert "machine_json_source_hash_stale" in json.dumps(mismatch["evidence"], ensure_ascii=False)
    repair_text = "\n".join(mismatch["repair"])
    assert f"beacon truth-map verify {FEATURE}" in repair_text
    assert f"beacon truth-map rebuild-machine {FEATURE}" in repair_text
    assert f"beacon truth-cutover run {FEATURE}" in repair_text
    assert f"beacon validate-feature-package {FEATURE}" in repair_text
