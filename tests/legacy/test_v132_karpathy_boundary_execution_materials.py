from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
FEATURE = "beacon-v1.3.2-karpathy-boundary-defaults"
SLUG = FEATURE
VERSION = "v1.3.2"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    for path in (
        base / "prd",
        base / "user-story",
        base / "qa" / "test-cases",
        base / "execution",
    ):
        path.mkdir(parents=True, exist_ok=True)

    (base / "prd" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## Functional Requirements",
                "",
                "### FR-001 Explicit assumptions",
                "- require explicit assumptions before implement or QA",
                "",
                "### FR-005 No external dependency",
                "- keep Karpathy rules inside Beacon-owned defaults",
                "",
                "### FR-006 Source and target inheritance",
                "- sync global boundaries into project context",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "user-story" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# User Story",
                "",
                "## Acceptance",
                "- 关键需求不明时必须回到 `prd / user-story` 收口",
                "- 默认采用最小正确改动",
                "- 非平凡任务必须保留验证证据",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# QA\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")


def test_karpathy_execution_materials_should_include_boundary_principles(tmp_path: Path):
    _seed_docs(tmp_path)

    freeze = _invoke(["freeze", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    sync = _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--revision-id",
            "R1",
            "--review-status",
            "approved",
            "--approved-by",
            "test",
            "--reviewed-at",
            "2026-04-16",
            "--json",
        ]
    )
    assert sync.exit_code == 0, sync.stdout

    plan = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan.exit_code == 0, plan.stdout

    contract_payload = json.loads(
        (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"deterministic-implementation-contract-{SLUG}.json").read_text(encoding="utf-8")
    )
    plan_payload = json.loads(
        (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"implementation-plan-{SLUG}.json").read_text(encoding="utf-8")
    )

    assert [item["id"] for item in contract_payload["boundary_principles"]] == [
        "explicit_assumptions",
        "simplicity_first",
        "surgical_changes",
        "goal_driven_execution",
        "trivial_task_exception",
    ]
    assert [item["id"] for item in plan_payload["boundary_principles"]] == [
        "explicit_assumptions",
        "simplicity_first",
        "surgical_changes",
        "goal_driven_execution",
        "trivial_task_exception",
    ]

    contract_markdown = (
        tmp_path / "docs" / "beacon" / VERSION / "execution" / f"deterministic-implementation-contract-{SLUG}.md"
    ).read_text(encoding="utf-8")
    plan_markdown = (
        tmp_path / "docs" / "beacon" / VERSION / "execution" / f"implementation-plan-{SLUG}.md"
    ).read_text(encoding="utf-8")
    assert "## Boundary Principles" in contract_markdown
    assert "## Boundary Principles" in plan_markdown
