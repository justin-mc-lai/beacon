"""Beacon PRD command surface."""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.versioning import resolve_operational_docs_version, resolve_target_version

app = typer.Typer(name="prd", help="Generate Product Requirements Document")

_TOOLING_KEYWORDS = (
    "toolkit",
    "skill",
    "friction",
    "generation",
    "generator",
    "template",
    "bootstrap",
    "doctor",
    "surface",
    "surfacing",
    "memory",
)
_RUNTIME_KEYWORDS = (
    "runtime",
    "projection",
    "control-plane",
    "control_plane",
    "pocketbase",
    "sqlite",
    "ledger",
    "board",
    "dashboard",
    "multi-project",
)


def _slugify(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip().lower())
    return text.strip("-") or "untitled-prd"


def _existing_prd_names(project_root: Path, version: str, *, exclude_slug: str) -> list[str]:
    prd_dir = project_root / "docs" / "beacon" / version / "prd"
    if not prd_dir.exists():
        return []
    names: list[str] = []
    for path in sorted(prd_dir.glob("*.md")):
        if path.stem == exclude_slug:
            continue
        names.append(path.stem)
    return names


def _classify_prd(feature: str, *, existing_prds: list[str]) -> dict[str, str]:
    slug = _slugify(feature)
    track = "parallel" if existing_prds else "main"

    if any(keyword in slug for keyword in _TOOLING_KEYWORDS):
        family = "tooling_surface"
    elif any(keyword in slug for keyword in _RUNTIME_KEYWORDS):
        family = "runtime_control_plane"
    else:
        family = "general"

    label = {
        ("main", "runtime_control_plane"): "主 PRD / runtime-control-plane",
        ("parallel", "runtime_control_plane"): "并行 PRD / runtime-control-plane",
        ("main", "tooling_surface"): "主 PRD / tooling-surface",
        ("parallel", "tooling_surface"): "并行 PRD / tooling-surface",
        ("main", "general"): "主 PRD / general",
        ("parallel", "general"): "并行 PRD / general",
    }[(track, family)]
    return {"track": track, "family": family, "label": label, "slug": slug}


def _context_block(version: str, *, existing_prds: list[str]) -> str:
    existing = ", ".join(f"`{name}`" for name in existing_prds) if existing_prds else "none"
    return "\n".join(
        [
            "## Context",
            "",
            f"- Global boundaries: `docs/beacon/global-boundaries.md`",
            f"- Version summary: `docs/beacon/{version}/SUMMARY.md`",
            f"- Execution index: `docs/beacon/{version}/execution/index.md`",
            f"- Existing PRDs in line: {existing}",
            "",
        ]
    )


def _main_problem_lines(family: str) -> list[str]:
    if family == "runtime_control_plane":
        return [
            "## 1. 问题",
            "",
            "### 1.1 当前运行态 / requirement 断层",
            "- 待补充：当前版本线为什么需要引入 runtime / projection / control-plane 能力。",
            "",
            "### 1.2 真实环境触发信号",
            "- 待补充：列出来自真实项目、真实 run、真实 debug 的摩擦输入。",
            "",
            "### 1.3 为什么现在做",
            "- 待补充：说明若不处理会如何影响版本主线与后续验收。",
            "",
        ]
    return [
        "## 1. 问题",
        "",
        "### 1.1 当前缺口",
        "- 待补充：当前 Beacon / 项目在 requirement、实现或交付上的真实缺口。",
        "",
        "### 1.2 触发背景",
        "- 待补充：为什么这个问题在当前版本线被正式提出。",
        "",
        "### 1.3 为什么现在做",
        "- 待补充：说明延期的代价、当前窗口期与版本必要性。",
        "",
    ]


def _parallel_problem_lines(family: str, existing_prds: list[str]) -> list[str]:
    anchor = f"`{existing_prds[0]}`" if existing_prds else "`<main-prd>`"
    if family == "tooling_surface":
        return [
            "## 1. 问题",
            "",
            f"本并行 PRD 依附主线 {anchor}，用于补齐命令面、skill surface、模板生成或 friction repair 的结构性缺口。",
            "",
            "### 1.1 当前断层",
            "- 待补充：当前命令行为 / skill 暴露 / 文档承诺之间的不一致。",
            "",
            "### 1.2 为什么不能继续人工兜底",
            "- 待补充：说明 generic template、隐藏入口或恢复策略不清带来的真实成本。",
            "",
            "### 1.3 本线与主 PRD 的边界",
            "- 待补充：明确这是补强主线，不是另起一条产品真相。",
            "",
        ]
    return [
        "## 1. 问题",
        "",
        f"本并行 PRD 依附主线 {anchor}，用于补齐一个必须单独冻结的实现/治理切面。",
        "",
        "### 1.1 当前补强点",
        "- 待补充：这条并行线解决的具体缺口。",
        "",
        "### 1.2 与主 PRD 的冲突风险",
        "- 待补充：若该线不冻结，主线会出现什么漂移或落空。",
        "",
        "### 1.3 为什么独立成并行 PRD",
        "- 待补充：说明为什么它不能只作为主 PRD 的一小段备注。",
        "",
    ]


def _goal_lines(family: str) -> list[str]:
    base = [
        "## 2. 目标",
        "",
        "### 2.1 主要目标",
        "- 待补充：定义本 PRD 真正要关闭的业务/产品/系统缺口。",
        "",
        "### 2.2 非目标",
        "- 待补充：明确当前版本不会承担的内容，防止范围漂移。",
        "",
    ]
    if family == "runtime_control_plane":
        base.extend(
            [
                "### 2.3 Truth 与 Projection 边界",
                "- 待补充：明确 docs/.beacon 与投影层的职责边界。",
                "",
            ]
        )
    elif family == "tooling_surface":
        base.extend(
            [
                "### 2.3 命令面 / skill 面一致性目标",
                "- 待补充：说明哪些 surface 需要被正式补齐并保持一致。",
                "",
            ]
        )
    return base


def _principle_lines(family: str) -> list[str]:
    lines = [
        "## 3. 设计原则",
        "",
        "### 3.1 保持产品边界稳定",
        "- 待补充：说明哪些东西必须保留为正式真相，哪些只能做投影或辅助面。",
        "",
        "### 3.2 机器复杂度默认内收",
        "- 待补充：优先把复杂度放在系统内部，不把治理成本长期转嫁给人类操作。",
        "",
    ]
    if family == "runtime_control_plane":
        lines.extend(
            [
                "### 3.3 Projection 必须确定性且可解释",
                "- 待补充：明确 normalize / preflight / write 的链路与回退策略。",
                "",
            ]
        )
    elif family == "tooling_surface":
        lines.extend(
            [
                "### 3.3 文档承诺必须有可达入口",
                "- 待补充：进入版本包叙事的 toolkit / skill / command 必须保持宿主可达。",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "### 3.3 最小闭环优先",
                "- 待补充：优先交付能被真实项目验证的最小闭环，而不是铺大面。",
                "",
            ]
        )
    return lines


def _scope_lines(family: str) -> list[str]:
    in_scope = [
        "- 待补充：当前版本必须交付的最小正确能力。",
        "- 待补充：需要被纳入真实验收的关键路径。",
    ]
    out_scope = [
        "- 待补充：不在当前版本承担的扩展项。",
        "- 待补充：应继续留在兼容层或后续版本处理的事项。",
    ]
    if family == "tooling_surface":
        in_scope.insert(0, "- 待补充：命令面、skill 暴露、模板骨架与文档的一致性修复。")
    elif family == "runtime_control_plane":
        in_scope.insert(0, "- 待补充：project/run/status/projection 的最小管理与观察闭环。")
    return [
        "## 4. 范围",
        "",
        "### In scope",
        *in_scope,
        "",
        "### Out of scope",
        *out_scope,
        "",
    ]


def _functional_requirement_lines(family: str) -> list[str]:
    if family == "runtime_control_plane":
        return [
            "## 5. 功能需求",
            "",
            "### FR-001 真实项目输入必须可被注册 / 投影",
            "- 待补充：说明项目注册、workspace 边界和 runtime 来源。",
            "",
            "### FR-002 Projection 写入前必须预校验",
            "- 待补充：说明 truth snapshot、preflight、drift check 与失败语义。",
            "",
            "### FR-003 人类看板必须优先呈现生命周期进度",
            "- 待补充：说明 overview/detail/runtime drilldown 的展示优先级。",
            "",
        ]
    if family == "tooling_surface":
        return [
            "## 5. 功能需求",
            "",
            "### FR-001 `prd create` 必须生成结构化骨架",
            "- 待补充：说明版本感知、场景感知与 Beacon 风格章节要求。",
            "",
            "### FR-002 已承诺 toolkit 必须有宿主可达入口",
            "- 待补充：说明 skill surface、命令路由和 optional 定位。",
            "",
            "### FR-003 文档与 skill surface 必须保持一致",
            "- 待补充：说明如何避免再次出现承诺/入口漂移。",
            "",
        ]
    return [
        "## 5. 功能需求",
        "",
        "### FR-001 主路径能力",
        "- 待补充：定义当前版本最关键的功能闭环。",
        "",
        "### FR-002 稳定性 / 恢复能力",
        "- 待补充：说明异常、断点恢复、回退和继续执行要求。",
        "",
        "### FR-003 可观测与验收面",
        "- 待补充：说明人类如何确认当前能力真的交付完成。",
        "",
    ]


def _data_lines(family: str) -> list[str]:
    if family == "runtime_control_plane":
        return [
            "## 6. 数据 / 状态 / 集成",
            "",
            "### 6.1 Truth 来源",
            "- 待补充：docs/beacon、.beacon、git/worktree、session 引用等来源。",
            "",
            "### 6.2 Projection Envelope",
            "- 待补充：统一字段、确定性生成规则、source priority 与回退状态。",
            "",
            "### 6.3 外部集成",
            "- 待补充：SQLite、PocketBase、备份与恢复链路。",
            "",
        ]
    if family == "tooling_surface":
        return [
            "## 6. 数据 / 状态 / 集成",
            "",
            "### 6.1 模板输入",
            "- 待补充：feature、version、existing PRDs、memory context 等输入项。",
            "",
            "### 6.2 输出物",
            "- 待补充：PRD 骨架、skill surface、测试覆盖与文档更新。",
            "",
            "### 6.3 演进接口",
            "- 待补充：后续如何继续增加模板或 toolkit，而不重写主命令。",
            "",
        ]
    return [
        "## 6. 数据 / 状态 / 集成",
        "",
        "### 6.1 输入",
        "- 待补充：当前能力依赖的主要输入与上下文。",
        "",
        "### 6.2 输出",
        "- 待补充：当前能力最终产出的文档、状态或接口。",
        "",
        "### 6.3 集成点",
        "- 待补充：外部系统、CLI surface、脚本或数据流。",
        "",
    ]


def _risk_lines() -> list[str]:
    return [
        "## 7. 风险与缓解",
        "",
        "| 风险 | 影响 | 缓解 |",
        "|------|------|------|",
        "| 待补充 | 中 | 待补充 |",
        "",
    ]


def _acceptance_lines(family: str) -> list[str]:
    if family == "runtime_control_plane":
        return [
            "## 8. 验收标准",
            "",
            "### AC-001 真实项目态可被正确投影",
            "- 待补充：至少列出需要通过的真实项目与展示语义。",
            "",
            "### AC-002 Projection 多写不漂移",
            "- 待补充：同一 truth snapshot 写入结果必须稳定可解释。",
            "",
            "### AC-003 缺失投影层时仍可继续",
            "- 待补充：明确断库、恢复、重新开始的验收口径。",
            "",
        ]
    if family == "tooling_surface":
        return [
            "## 8. 验收标准",
            "",
            "### AC-001 `prd create` 不再输出 generic 模板",
            "- 待补充：新 PRD 必须直接包含 Beacon 风格结构化章节。",
            "",
            "### AC-002 生成器能区分主 PRD / 并行 PRD",
            "- 待补充：说明 track 判定和骨架差异的验收方式。",
            "",
            "### AC-003 toolkit skill 在宿主面可发现",
            "- 待补充：说明 host-visible skill、optional 定位和回归检查。",
            "",
        ]
    return [
        "## 8. 验收标准",
        "",
        "### AC-001 主路径通过",
        "- 待补充：说明用户/项目如何确认主路径已闭环。",
        "",
        "### AC-002 异常路径可恢复",
        "- 待补充：说明关键异常或中断下的恢复口径。",
        "",
        "### AC-003 文档与实现一致",
        "- 待补充：说明如何验证 requirement 与实际交付没有漂移。",
        "",
    ]


def _metric_lines() -> list[str]:
    return [
        "## 9. 成功指标",
        "",
        "- 待补充：1 个能反映真实闭环的主指标。",
        "- 待补充：1 个能反映稳定性/效率改善的辅助指标。",
        "",
    ]


def _relationship_lines(track: str, existing_prds: list[str]) -> list[str]:
    if track == "parallel":
        anchor = f"`{existing_prds[0]}`" if existing_prds else "`<main-prd>`"
        return [
            "## 10. 与主 PRD 的关系",
            "",
            f"- 主线锚点：{anchor}",
            "- 待补充：说明本并行 PRD 补强哪一段主线能力。",
            "- 待补充：说明哪些内容回写主 PRD，哪些保持独立冻结。",
            "",
        ]
    return [
        "## 10. 依赖与开放问题",
        "",
        "- 待补充：当前主线依赖的外部条件、真实项目输入或待确认问题。",
        "- 待补充：需要后续并行 PRD 单独冻结的切面。",
        "",
    ]


def _render_prd(
    feature: str,
    *,
    version: str,
    memory_context_path: str,
    track: str,
    family: str,
    label: str,
    existing_prds: list[str],
    slug: str,
) -> str:
    sections: list[str] = [
        f"# PRD：{feature}",
        "",
        f"**Feature**: `{slug}`  ",
        f"**Version**: `{version}`  ",
        f"**Date**: `{datetime.now().strftime('%Y-%m-%d')}`  ",
        f"**Status**: `draft skeleton`  ",
        f"**Track**: `{track}`  ",
        f"**Scenario**: `{family}`  ",
        f"**Template**: `{label}`  ",
        "",
        _context_block(version, existing_prds=existing_prds),
    ]

    sections.extend(_main_problem_lines(family) if track == "main" else _parallel_problem_lines(family, existing_prds))
    sections.extend(_goal_lines(family))
    sections.extend(_principle_lines(family))
    sections.extend(_scope_lines(family))
    sections.extend(_functional_requirement_lines(family))
    sections.extend(_data_lines(family))
    sections.extend(_risk_lines())
    sections.extend(_acceptance_lines(family))
    sections.extend(_metric_lines())
    sections.extend(_relationship_lines(track, existing_prds))
    sections.extend(
        [
            "---",
            "",
            f"**Created**: {datetime.now().strftime('%Y-%m-%d')}  ",
            f"**Version**: {version}  ",
            f"**Status**: draft skeleton  ",
            f"**Memory Context**: {memory_context_path or 'N/A'}",
            "",
        ]
    )
    return "\n".join(sections)


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a PRD"""
    project_root = Path(project) if project else Path.cwd()
    try:
        resolved_version = resolve_operational_docs_version(
            project_root,
            version,
            command_name="prd create",
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)

    memory_context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()
    slug = _slugify(feature)
    existing_prds = _existing_prd_names(project_root, resolved_version, exclude_slug=slug)
    template = _classify_prd(feature, existing_prds=existing_prds)
    md_content = _render_prd(
        feature,
        version=resolved_version,
        memory_context_path=memory_context_path,
        track=template["track"],
        family=template["family"],
        label=template["label"],
        existing_prds=existing_prds,
        slug=slug,
    )

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_content)
    else:
        output_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{slug}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_content)

    typer.echo(f"✓ PRD created: {output_path}")


@app.command("list")
def list_prds(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """List all PRDs"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    roots = [project_root / "docs" / "beacon" / resolved_version / "prd"]
    prds = []
    for prds_dir in roots:
        if prds_dir.exists():
            prds.extend(prds_dir.glob("*.md"))
    if not prds:
        typer.echo("No PRDs found")
        return
    unique = {p.name: p for p in prds}
    typer.echo(f"PRDs ({len(unique)} found):")
    for prd in sorted(unique.values(), key=lambda p: p.name):
        typer.echo(f"  - {prd.name}")


if __name__ == "__main__":
    app()
