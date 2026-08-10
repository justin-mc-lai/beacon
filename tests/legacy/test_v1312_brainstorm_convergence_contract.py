from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.revision_state import freeze_revision_state


runner = CliRunner()
VERSION = "v1.3.12"
FEATURE = "Beacon Brainstorm Convergence Contract"
SLUG = "beacon-brainstorm-convergence-contract"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text(
        "# PRD\n\n## 目标\n- 深挖 PRD 周边缺口并路由到 brainstorm / change / supplement。\n",
        encoding="utf-8",
    )
    (base / "user-story" / f"{SLUG}.md").write_text("# User Story\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")


def test_v1312_help_should_surface_brainstorm_convergence_route(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    result = _invoke(["help", "--json", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["requirement_gap_digest"]["human_followup_needed"] is True
    assert payload["requirement_gap_digest"]["recommended_route"] in {"beacon-brainstorm", "beacon-change"}
    assert payload["brainstorm_hint"]["recommended_route"] in {"beacon-brainstorm", "beacon-change"}


def test_v1312_status_should_surface_convergence_route_and_hint(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    result = _invoke(["status", "--board", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE])
    assert result.exit_code == 0, result.stdout
    assert "requirement_gap:" in result.stdout
    assert "brainstorm_hint:" in result.stdout


def test_v1312_status_should_surface_supplement_and_refreeze_projection(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    _invoke(
        [
            "user-story",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    result = _invoke(["status", "--board", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE])
    assert result.exit_code == 0, result.stdout
    assert "supplement_task:" in result.stdout
    assert "re_freeze_transaction:" in result.stdout


def test_v1312_brainstorm_should_consume_convergence_contract_and_emit_supplement_task(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    result = _invoke(
        [
            "brainstorm",
            "run",
            "补齐 role / state / boundary gap",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["recommended_route"] in {"beacon-user-story", "beacon-test-case", "beacon-change"}
    assert payload["convergence_contract"]["route_reason"]
    assert isinstance(payload["next_route"], str)
    if payload["supplement_task"]["target_artifact"]:
        assert payload["supplement_task"]["audit_trail_required"] is True
        assert payload["supplement_task"]["candidate_kind"] == "supplement_task"
        assert payload["supplement_task"]["recommended_route"] == payload["recommended_route"]
        text = (tmp_path / payload["output_path"]).read_text(encoding="utf-8")
        assert "## convergence_contract" in text
        assert "## supplement_task" in text
