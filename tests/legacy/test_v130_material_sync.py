from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.material_sync import sync_feature_requirement_materials


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_friend_match_docs(root: Path, version: str = "v1.0.0") -> None:
    base = root / "docs" / "beacon" / version
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "research").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{version}.md").write_text("# Release\n", encoding="utf-8")
    # Package-authoritative truth (feature_package_authoritative is always on).
    feat = base / "features" / "friend-match"
    feat.mkdir(parents=True, exist_ok=True)
    (feat / "truth.md").write_text(
        f"""---
slug: friend-match
version: {version}
status: frozen
language: zh
package_maturity: filled
parser_contract: beacon-feature-package-v2
canonical_refs:
  prd: docs/beacon/{version}/features/friend-match/truth.md
  user_story: docs/beacon/{version}/features/friend-match/truth.md
  test_case: docs/beacon/{version}/features/friend-match/tests.md
---
# 人话

好友匹配功能

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | 用户可以创建比赛 |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| idle | create | ok | done | create match |
""",
        encoding="utf-8",
    )
    (feat / "tests.md").write_text(
        "| TC ID | AC ID | Command | Assertion |\n|----|----|----|----|\n"
        "| TC-001 | AC-001 | `python3 -m pytest -q -k match` | pass |\n",
        encoding="utf-8",
    )
    (feat / "tasks.md").write_text(
        "- [ ] TASK-001 Implement AC-001 · ac=AC-001 · evidence=.beacon/evidence/x.json\n",
        encoding="utf-8",
    )
    (feat / "evidence.md").write_text(
        "| surface | authority |\n|---|---|\n| tests | acceptance_truth |\n",
        encoding="utf-8",
    )
    (base / "user-story" / "friend-match.md").write_text(
        "\n".join(
            [
                "# Friend Match",
                "",
                "## US-001：创建比赛",
                "",
                "### 验收标准",
                "",
                "- [ ] 用户可以创建比赛",
                "",
                "## US-002：加入比赛",
                "",
                "### 验收标准",
                "",
                "- [ ] 用户可以通过邀请码加入比赛",
                "",
                "## CR-DB-001：MySQL 主库切换",
                "",
                "### 验收标准",
                "",
                "- [ ] 新版服务使用 MySQL",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "prd" / "friend-match.md").write_text("# PRD\n", encoding="utf-8")
    (base / "research" / "friend-match.md").write_text(
        "\n".join(
            [
                "# Research",
                "",
                "## Business Flow",
                "- 创建比赛后必须可以邀请朋友加入。",
                "",
                "## State Machine",
                "- match state: draft -> open -> active -> completed",
                "",
                "## Decision Priority",
                "- 当邀请码无效时，优先提示错误而不是继续进入房间。",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / "friend-match.md").write_text(
        "\n".join(
            [
                "# QA",
                "",
                "## 1. Cases",
                "",
                "| TC ID | 类型 | 场景 | 关键步骤 | 预期结果 | 执行方式 |",
                "|---|---|---|---|---|---|",
                "| TC-US001-01 | 功能 | 创建比赛 | 首页进入创建流程 | 成功进入创建页 | agent-browser |",
                "| TC-US002-01 | 功能 | 邀请码加入 | 输入邀请码并确认 | 成功加入比赛 | agent-browser |",
                "| TC-DB001-01 | 契约 | MySQL 切换 | 检查配置与文档 | 新版服务目标数据库为 MySQL | Doc Review |",
                "| TC-RG010-01 | 回归 | 模板回归 | 选择模板并继续 | 模板链路可用 | agent-browser |",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_doctor_sync_materials_should_rebuild_machine_story_and_qa_from_section_style_docs(tmp_path: Path):
    _seed_friend_match_docs(tmp_path)

    result = _invoke(
        [
            "doctor",
            "sync-materials",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.0.0",
            "--feature",
            "friend-match",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"

    story = json.loads((tmp_path / "docs" / "beacon" / "v1.0.0" / ".machine" / "user-story" / "friend-match.json").read_text(encoding="utf-8"))
    active_story = next(item for item in story["stories"] if item["revision_id"] == story["current_revision_id"])
    ac_items = [item for item in active_story["items"] if item["kind"] == "ac"]
    test_items = [item for item in active_story["items"] if item["kind"] == "test"]
    assert [item["story_id"] for item in ac_items] == ["US-001", "US-002", "CR-DB-001", "RG-010"]
    assert len(test_items) == 4
    assert (active_story.get("research_projection") or {}).get("present") is True
    assert "business_flow" in ((active_story.get("research_projection") or {}).get("sections") or {})

    matrix = json.loads((tmp_path / "docs" / "beacon" / "v1.0.0" / ".machine" / "qa" / "friend-match.ac-test-matrix.json").read_text(encoding="utf-8"))
    assert [item["tc_id"] for item in matrix["entries"]] == ["TC-US001-01", "TC-US002-01", "TC-DB001-01", "TC-RG010-01"]
    assert [item["ac_id"] for item in matrix["entries"]] == ["AC-001", "AC-002", "AC-003", "AC-004"]
    assert (matrix.get("research_projection") or {}).get("present") is True

    scenario_map = json.loads((tmp_path / "docs" / "beacon" / "v1.0.0" / ".machine" / "qa" / "friend-match.story-scenario-map.json").read_text(encoding="utf-8"))
    scenario_source_tc_ids = {item["source_tc_id"] for item in scenario_map["scenarios"]}
    assert {"TC-US001-01", "TC-US002-01", "TC-DB001-01", "TC-RG010-01"} <= scenario_source_tc_ids
    assert (scenario_map.get("research_projection") or {}).get("present") is True


def test_sync_feature_requirement_materials_should_pass_explicit_defaults_to_test_case_create(tmp_path: Path):
    _seed_friend_match_docs(tmp_path)

    result = sync_feature_requirement_materials(
        tmp_path,
        version="v1.0.0",
        feature="friend-match",
    )

    assert result["status"] == "synced"
    assert (tmp_path / "docs" / "beacon" / "v1.0.0" / ".machine" / "qa" / "friend-match.ac-test-matrix.json").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.0.0" / ".machine" / "qa" / "friend-match.story-scenario-map.json").exists()


def test_doctor_setup_context_with_sync_materials_should_include_sync_summary(tmp_path: Path):
    _seed_friend_match_docs(tmp_path)

    result = _invoke(
        [
            "doctor",
            "setup-context",
            "--project-root",
            str(tmp_path),
            "--sync-materials",
            "--feature",
            "friend-match",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    material_sync = payload.get("material_sync", {})
    assert material_sync.get("feature_count") == 1
    assert material_sync.get("results", [])[0]["feature"] == "friend-match"
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.0.0" / ".machine" / "user-story" / "friend-match.json").exists()
