from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.4.3"
FEATURE = "beacon-v1.4.3-design-review-surface-and-prototype-governance"
SLUG = "beacon-v1.4.3-design-review-surface-and-prototype-governance"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_feature_docs(root: Path, *, ui_required: bool) -> None:
    ui_flags = "ui_visualization_required: true\nprototype_freeze_required: true\n" if ui_required else ""
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        (
            "# PRD\n"
            f"{ui_flags}"
            "页面层级：项目详情页、状态面板、决策入口。\n"
            "角色权限：管理员可以审批，普通用户只读。\n"
            "审计日志：所有敏感操作写入审计记录。\n"
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        (
            "# User Story\n"
            f"{ui_flags}"
            "状态：loading / empty / success / error。\n"
            "交互：点击详情、提交审批、返回概览。\n"
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        (
            "# Test Cases\n"
            f"{ui_flags}"
            "验证页面状态切换、审批交互与回退路径。\n"
        ),
    )


def test_v143_design_review_surface_exists_and_is_support_only(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path, ui_required=False)

    result = _invoke(["review", "design", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    txn = payload["support_surface_transaction"]
    assert txn["surface"] == "beacon-design-review"
    assert txn["decision"] == "prototype_not_required"
    assert txn["next_route"]["target_surface"] == "beacon-implement"


def test_v143_design_review_evaluates_hierarchy_state_interaction(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path, ui_required=True)

    result = _invoke(["review", "design", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    review = payload["requirement_design_review"]
    assert review["ui_surface_detected"] is True
    assert review["hierarchy_signal"] is True
    assert review["state_signal"] is True
    assert review["interaction_signal"] is True


def test_v143_design_review_precedes_prototype_when_needed(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path, ui_required=True)

    result = _invoke(["review", "design", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    txn = payload["support_surface_transaction"]
    assert payload["prototype_required"] is True
    assert txn["decision"] == "ready_for_prototype"
    assert "beacon prototype" in txn["next_route"]["command"]
