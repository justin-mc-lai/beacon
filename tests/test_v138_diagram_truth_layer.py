from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload
from beacon.utils.technical_review_contract import technical_review_contract_json_path


runner = CliRunner()
VERSION = "v1.3.8"
FEATURE = "V138 Diagram Truth Feature"
SLUG = "v138-diagram-truth-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", f"beacon/{VERSION}"], cwd=root, check=True, capture_output=True, text=True)


def _seed_base(root: Path) -> None:
    _init_git_repo(root)
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "research").mkdir(parents=True, exist_ok=True)
    (base / "source-architecture").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "source-architecture" / "index.md").write_text("# Source Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")


def _write_requirement_docs(root: Path, *, prd_text: str, user_story_text: str) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "prd" / f"{SLUG}.md").write_text(prd_text, encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text(user_story_text, encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json").write_text('{"scenarios":[]}\n', encoding="utf-8")


def _write_contract(root: Path) -> None:
    path = technical_review_contract_json_path(root, VERSION, FEATURE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "revision_id": "R1",
                "base_branch": "main",
                "target_branch": f"beacon/{VERSION}",
                "branch_prefix": "beacon/",
                "use_git_worktree": False,
                "worktree_root": str(root),
                "environment_mode": "local-dev",
                "isolation_strategy": "repo-local isolation",
                "service_directories": ["."],
                "writable_services": ["."],
                "reference_only_services": ["docs"],
                "review_status": "approved",
                "approved_by": "tech-lead",
                "reviewed_at": "2026-04-24T10:00:00+08:00",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_research_closure(root: Path, *, include_decision_priority: bool = True) -> None:
    base = root / "docs" / "beacon" / VERSION / "research"
    sections = [
        "# Research Closure",
        "",
        "## Architecture",
        "- explain service/module boundaries",
        "",
        "## Business Flow",
        "- explain the end-to-end business flow",
        "",
        "## State Machine",
        "- relation: draft -> active -> revoked",
        "- sale: pending -> confirmed -> canceled",
        "",
    ]
    if include_decision_priority:
        sections.extend(
            [
                "## Decision Priority",
                "- eligibility override beats stale local cache",
                "",
            ]
        )
    (base / f"{SLUG}.md").write_text("\n".join(sections), encoding="utf-8")


def test_v138_requirement_clarity_should_block_complex_feature_without_diagram_truth(tmp_path: Path):
    _seed_base(tmp_path)
    _write_requirement_docs(
        tmp_path,
        prd_text=(
            "# PRD\n\n"
            "## 功能需求\n\n"
            "- FR-001 复杂业务资格切换，需要处理多状态轴、资格、归属和结算。\n"
            "- FR-002 后续实现需要 relation / sale 口径一致。\n"
        ),
        user_story_text=(
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n| --- | --- | --- |\n"
            "| AC-001 | Complex | complex feature spans relation and sale state axes |\n"
        ),
    )

    payload = build_requirement_clarity_gate_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["blocked"] is True
    assert payload["reason_code"] == "requirement_clarity_open"
    kinds = {item["kind"] for item in payload["findings"]}
    assert "diagram_truth_missing" in kinds or "state_axis_missing" in kinds


def test_v138_requirement_clarity_should_block_complex_feature_without_human_closure_package(tmp_path: Path):
    _seed_base(tmp_path)
    _write_requirement_docs(
        tmp_path,
        prd_text=(
            "# PRD\n\n"
            "## 功能需求\n\n"
            "- FR-001 Complex branch handling across relation and sale.\n\n"
            "## 11. Diagram Truth Layer\n\n"
            "### 11.1 Diagram Types\n"
            "- `branch-flow`\n"
            "- `state-machine`\n"
            "- `decision-priority`\n\n"
            "### 11.2 State Axes\n"
            "- `relation`\n"
            "- `sale`\n"
        ),
        user_story_text=(
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n| --- | --- | --- |\n"
            "| AC-001 | Branch | preserve branch flow and state transitions |\n"
        ),
    )

    payload = build_requirement_clarity_gate_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["blocked"] is True
    kinds = {item["kind"] for item in payload["findings"]}
    assert "research_artifact_missing" in kinds


def test_v138_freeze_should_pass_when_human_closure_package_is_complete(tmp_path: Path):
    _seed_base(tmp_path)
    _write_requirement_docs(
        tmp_path,
        prd_text=(
            "# PRD\n\n"
            "## 功能需求\n\n"
            "- FR-001 Complex branch handling\n"
            "- FR-002 Preserve transition safety\n\n"
            "## 11. Diagram Truth Layer\n\n"
            "### 11.1 Diagram Types\n"
            "- `branch-flow`\n"
            "- `state-machine`\n"
            "- `decision-priority`\n\n"
            "### 11.2 State Axes\n"
            "- `relation`\n"
            "- `sale`\n"
        ),
        user_story_text=(
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n| --- | --- | --- |\n"
            "| AC-001 | Branch | Preserve branch-flow decisions |\n"
            "| AC-002 | State | Preserve state transitions across relation and sale |\n"
        ),
    )
    _write_research_closure(tmp_path)

    result = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout


def test_v138_prd_create_should_append_diagram_truth_section(tmp_path: Path):
    _seed_base(tmp_path)

    result = _invoke(
        [
            "prd",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "rule",
            "--include-diagrams",
            "branch-flow",
            "--include-diagrams",
            "state-machine",
            "--include-diagrams",
            "decision-priority",
            "--state-axis",
            "relation",
            "--state-axis",
            "sale",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    prd_path = tmp_path / "docs" / "beacon" / VERSION / "prd" / f"{SLUG}.md"
    text = prd_path.read_text(encoding="utf-8")
    assert "## 11. Diagram Truth Layer" in text
    assert "`branch-flow`" in text
    assert "`state-machine`" in text
    assert "`decision-priority`" in text
    assert "`relation`" in text
    assert "`sale`" in text


def test_v138_implement_plan_should_propagate_diagram_truth_into_tasks(tmp_path: Path):
    _seed_base(tmp_path)
    _write_requirement_docs(
        tmp_path,
        prd_text=(
            "# PRD\n\n"
            "## 功能需求\n\n"
            "- FR-001 Complex branch handling\n"
            "- FR-002 Preserve transition safety\n\n"
            "## 11. Diagram Truth Layer\n\n"
            "### 11.1 Diagram Types\n"
            "- `branch-flow`\n"
            "- `state-machine`\n"
            "- `decision-priority`\n\n"
            "### 11.2 State Axes\n"
            "- `relation`\n"
            "- `sale`\n"
        ),
        user_story_text=(
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n| --- | --- | --- |\n"
            "| AC-001 | Branch | Preserve branch-flow decisions |\n"
            "| AC-002 | State | Preserve state transitions across relation and sale |\n"
        ),
    )
    _write_research_closure(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_contract(tmp_path)

    result = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["diagram_truth"]["ready"] is True
    plan_path = tmp_path / payload["plan_path"]
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["diagram_truth"]["state_axes"] == ["relation", "sale"]
    assert plan["source_refs"]["research_projection"].endswith(f"{SLUG}.json")
    assert plan["research_projection"]["present"] is True
    assert "business_flow" in (plan["research_projection"]["sections"] or {})
    assert plan["research_projection"]["source_artifact"].endswith(f".machine/user-story/{SLUG}.json")
    assert plan["review_gates"]
    assert all(task["diagram_review_gates"] for task in plan["tasks"])
