from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.technical_review_contract import technical_review_contract_json_path


runner = CliRunner()
VERSION = "v1.3.8"
FEATURE = "Takeover Delivery Blueprint Feature"
SLUG = "takeover-delivery-blueprint-feature"


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


def _seed_takeover_project(root: Path) -> None:
    _init_git_repo(root)
    base = root / "docs" / "beacon" / VERSION
    for path in (
        base / "prd",
        base / "user-story",
        base / "qa" / "test-cases",
        base / "execution",
        base / "release",
        base / ".machine" / "qa",
    ):
        path.mkdir(parents=True, exist_ok=True)

    (root / ".beacon" / "state").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state" / "project-onboarding.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "project_mode": "takeover",
                "docs_version": VERSION,
                "runtime_version": VERSION,
                "takeover_baseline_frozen": True,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture Blueprint\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")

    (base / "execution" / "current-state-service-map.md").write_text(
        "\n".join(
            [
                "# Current-State Service Map",
                "",
                "- status: frozen",
                "- project_mode: takeover",
                f"- version: {VERSION}",
                f"- feature: {SLUG}",
                "",
                "## Primary Systems",
                "",
                "- `marketing_sys`",
                "  - 后台审核、客户归属与聚合读模型事实源",
                "- `marketing_primary_fe`",
                "  - 营销后台审批页、详情页和配置页前端承载",
                "- `marketing_distributor_fe`",
                "  - 合伙人 H5 首页、客户列表与详情页承载",
                "- `order-svr`",
                "  - 订单归因快照与 outbox 投递",
                "",
                "## Current Fact Sources",
                "",
                "### 1. 审核与身份",
                "- `marketing_sys`:",
                "  - `App\\Http\\Admin\\Controller\\Marketing\\PartnerController`",
                "  - `App\\Model\\Marketing\\Partner`",
                "- `marketing_primary_fe`:",
                "  - `src/modules/marketing/views/PartnerApply/index.vue`",
                "",
                "### 2. H5 与首页业绩",
                "- `marketing_distributor_fe`:",
                "  - `src/api/modules/home.ts`",
                "  - `src/api/modules/customer.ts`",
                "- `order-svr`:",
                "  - `internal/service/order_service.go`",
                "",
                "## Target Handoff for Implement",
                "",
                "- 后台审批与分成配置必须切到服务端显式合同。",
                "- H5 与后台都不得自行反推奖励类明细。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (base / "execution" / "refactor-boundaries.md").write_text(
        "\n".join(
            [
                "# Refactor Boundaries",
                "",
                "- status: frozen",
                "- project_mode: takeover",
                f"- version: {VERSION}",
                f"- feature: {SLUG}",
                "",
                "## Must Change",
                "- 后台审核通过时必须选择合伙人等级。",
                "- H5 业绩详情只展示线上允许的收益类型。",
                "",
                "## Can Reuse",
                "- 现有后台详情页和 H5 列表骨架。",
                "",
                "## Must Not Change",
                "- 不新建独立 partner service。",
                "",
                "## Compatibility Rules",
                "- 历史 DIRECT / INDIRECT 仍保留为底层归因事实。",
                "",
                "## Delivery Constraints",
                "- 发布必须包含 migration 和接口交付文档。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (base / "prd" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## 3. 功能范围",
                "",
                "### 3.1 F1 审核与直属推荐关系建立",
                "- 后台审核通过时必须选择 `partner_level`。",
                "- 推荐合伙人按原型可选。",
                "",
                "### 3.2 F2 H5 业绩详情与手机号动态可见",
                "- 合伙人 H5 详情页只展示线上允许的收益类型。",
                "- 间接绑定客户首单前后遵循不同手机号展示策略。",
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
                "| AC ID | Theme | Description |",
                "| --- | --- | --- |",
                "| AC-001 | 审核 | 审核通过时必须选择 partner_level |",
                "| AC-002 | 推荐关系 | 推荐合伙人可选且不自动反推 |",
                "| AC-003 | H5 详情 | H5 详情只展示线上允许的收益类型 |",
                "| AC-004 | 手机号策略 | 间接绑定客户首单前后展示策略不同 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# QA\n", encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"ac_id": "AC-001", "tc_id": "TC-001"},
                    {"ac_id": "AC-002", "tc_id": "TC-002"},
                    {"ac_id": "AC-003", "tc_id": "TC-003"},
                    {"ac_id": "AC-004", "tc_id": "TC-004"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (base / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json").write_text(
        json.dumps(
            {
                "scenarios": [
                    {"scenario_id": "SC-001", "ac_id": "AC-001", "source_tc_id": "TC-001"},
                    {"scenario_id": "SC-002", "ac_id": "AC-003", "source_tc_id": "TC-003"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (base / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"id": "QA9-001", "ac_id": "AC-001", "tc_id": "TC-001"},
                    {"id": "QA9-003", "ac_id": "AC-003", "tc_id": "TC-003"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


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
                "branch_strategy": "workspace-multi-service",
                "use_git_worktree": False,
                "worktree_root": str(root),
                "workspace_root": str(root),
                "environment_mode": "local-dev",
                "isolation_strategy": "repo-local isolation",
                "service_directories": [
                    "marketing_sys",
                    "marketing_primary_fe",
                    "marketing_distributor_fe",
                    "order-svr",
                ],
                "writable_services": [
                    "marketing_sys",
                    "marketing_primary_fe",
                ],
                "reference_only_services": [
                    "docs",
                    "commission-svr",
                ],
                "review_status": "approved",
                "approved_by": "test",
                "reviewed_at": "2026-04-26T12:00:00+08:00",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_v138_takeover_implementation_materials_should_render_technical_delta_and_concrete_tasks(tmp_path: Path):
    _seed_takeover_project(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_contract(tmp_path)

    result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    plan = json.loads((tmp_path / payload["plan_path"]).read_text(encoding="utf-8"))
    blueprint = (tmp_path / "docs" / "beacon" / VERSION / "execution" / "architecture-blueprint.md").read_text(encoding="utf-8")

    assert "## Technical Delta Blueprint" in blueprint
    assert "#### F1 审核与直属推荐关系建立" in blueprint
    assert "#### F2 H5 业绩详情与手机号动态可见" in blueprint
    assert "- write_path:" in blueprint
    assert "- storage_changes:" in blueprint
    assert "- verification_focus:" in blueprint
    assert "```mermaid" in blueprint
    assert "### Must Change" in blueprint
    assert "current_state_service_map" in blueprint
    assert "### Available Entry Surfaces" in blueprint
    assert "## Implementation Delivery Baseline" in blueprint
    assert "target_modules:" not in blueprint
    assert "  - modules:" not in blueprint

    assert plan["architecture_blueprint_ref"].endswith("execution/architecture-blueprint.md")
    assert plan["task_mapping_source"] == "prd-sections"
    assert [task["title"] for task in plan["tasks"][:2]] == [
        "F1 审核与直属推荐关系建立",
        "F2 H5 业绩详情与手机号动态可见",
    ]
    assert plan["tasks"][0]["target_modules"]
    assert "marketing_sys" in plan["tasks"][0]["direct_delivery_services"]
    assert any(
        module in plan["tasks"][0]["target_modules"]
        for module in ["App\\Http\\Admin\\Controller\\Marketing\\PartnerController", "marketing_sys"]
    )
    assert "marketing_distributor_fe" in plan["tasks"][1]["direct_delivery_services"]
    assert plan["tasks"][1]["mapped_test_ids"] == ["TC-003", "TC-004"]


def test_v138_implement_plan_should_refresh_existing_blueprint_projection(tmp_path: Path):
    _seed_takeover_project(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_contract(tmp_path)

    first = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert first.exit_code == 0, first.stdout

    blueprint_path = tmp_path / "docs" / "beacon" / VERSION / "execution" / "architecture-blueprint.md"
    blueprint_path.write_text(
        "\n".join(
            [
                "# Architecture Blueprint",
                "",
                "<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:START -->",
                "## Technical Delta Blueprint",
                "- target_modules: legacy/path.py",
                "<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:END -->",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    second = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert second.exit_code == 0, second.stdout
    blueprint = blueprint_path.read_text(encoding="utf-8")

    assert "- write_path:" in blueprint
    assert "```mermaid" in blueprint
    assert "target_modules:" not in blueprint
