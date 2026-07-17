"""Beacon design command - support-only design truth and route contracts."""
from __future__ import annotations

import json
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

from beacon.utils.design_contract import (
    bootstrap_design_capabilities,
    build_design_plan,
    build_design_route_payload,
    design_route_contract,
    design_truth_contract,
    write_version_design_contracts,
)
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="design", help="Support-only Beacon design capability routes and contracts")


def _emit(payload: dict, *, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"status: {payload.get('status', '')}")
    if payload.get("route"):
        typer.echo(f"route: {payload.get('route')}")
    if payload.get("upstream"):
        typer.echo(f"upstream: {payload.get('upstream')}")


@app.command("contract")
def contract(
    feature: str = typer.Argument("", help="Optional feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show Beacon design support route and truth contract."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = design_route_contract(project_root, resolved_version, feature=feature)
    _emit(payload, json_output=json_output)


@app.command("truth")
def truth(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    write: bool = typer.Option(False, "--write", help="Create missing version-wide design truth drafts"),
    include_project_truth: bool = typer.Option(
        False,
        "--include-project-truth",
        help="Also create missing root-level PRODUCT.md and DESIGN.md when used with --write",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite design truth drafts when used with --write"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show or create version-wide design truth draft surfaces."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = write_version_design_contracts(
        project_root,
        resolved_version,
        force=force,
        include_project_truth=include_project_truth,
    ) if write else {
        **design_truth_contract(project_root, resolved_version),
        "status": "ready",
    }
    _emit(payload, json_output=json_output)


@app.command("route")
def route(
    intent: str = typer.Argument(..., help="Design intent: explore/system/review/polish/extract/library/bootstrap"),
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Resolve a Beacon design support route for a feature."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = build_design_route_payload(project_root, resolved_version, feature, intent=intent)
    _emit(payload, json_output=json_output)
    if payload.get("status") == "blocked":
        raise typer.Exit(2)


@app.command("plan")
def plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Build a support-only design plan against Beacon truth contracts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = build_design_plan(project_root, resolved_version, feature)
    _emit(payload, json_output=json_output)


@app.command("bootstrap")
def bootstrap(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Check Beacon design upstream skill/mirror availability."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = bootstrap_design_capabilities(project_root, resolved_version)
    _emit(payload, json_output=json_output)



@app.command("baseline")
def baseline(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    preset: str = typer.Option(
        "restrained-product",
        "--preset",
        help="Visual preset: restrained-product|operator-console|editorial-calm",
    ),
    write: bool = typer.Option(True, "--write/--dry-run", help="Write DESIGN.md / fine-tune proposal"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing DESIGN.md"),
    product_name: str = typer.Option("", "--product-name", help="Product display name for DESIGN.md title"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Unattended complete DESIGN.md baseline (open-source UI agent principles absorbed).

    If DESIGN.md is missing: write a full reusable visual contract.
    If DESIGN.md exists and --force is not set: preserve it and write fine-tune-proposal.md
    so secondary polish can merge without discarding project identity.
    """
    from beacon.utils.design_baseline import (
        render_complete_design_md,
        resolve_design_preset,
        synthesize_unattended_design_baseline,
    )

    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    if not write:
        tokens = resolve_design_preset(preset)
        body = render_complete_design_md(
            product_name=product_name or project_root.name or "Product",
            preset=tokens["preset"],
            version=resolved_version,
            mode="baseline",
        )
        payload = {
            "schema_version": "1.0",
            "status": "dry_run",
            "version": resolved_version,
            "preset": tokens["preset"],
            "design_md_preview_chars": len(body),
        }
        _emit(payload, json_output=json_output)
        if not json_output:
            typer.echo(body)
        return

    payload = synthesize_unattended_design_baseline(
        project_root,
        resolved_version,
        preset=preset,
        force=force,
        write_version_contracts=True,
        product_name=product_name,
    )
    _emit(payload, json_output=json_output)


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature or problem to design"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a legacy Design Thinking document."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)

    md_content = f"""# Design Thinking: {feature}

以用户为中心的创新方法论，5 阶段系统化解决复杂问题。

---

## 阶段 1: Empathize 同理心

**目标**：深入理解用户

**问题**：
- 目标用户是谁？他们的日常生活是什么样的？
- 用户的核心痛点是什么？
- 用户现在用什么方式解决这个问题？
- 用户的情感和期望是什么？

**输出**：用户画像、痛点列表、用户旅程图

---

## 阶段 2: Define 定义问题

**目标**：提炼真正要解决的问题

**问题**：
- 从同理心阶段发现了什么洞察？
- 真正的问题是什么？
- 如何用一句话描述这个问题？
- 问题的本质是什么？

**输出**：问题陈述 (Problem Statement)

---

## 阶段 3: Ideate 创意

**目标**：产出大量创意点子

**问题**：
- 可能的解决方案有哪些？（至少 10 个）
- 如果没有任何限制，会怎么做？
- 竞品是怎么解决的？
- 可以从其他行业借鉴什么？

**工具**：
- 头脑风暴
- 思维导图
- SCAMPER 奔驰法

**输出**：创意清单、MoSCoW 优先级

---

## 阶段 4: Prototype 原型

**目标**：快速验证想法

**问题**：
- 最简单的验证方式是什么？
- 需要做什么样的原型？
- 如何以最小成本测试核心假设？

**原型类型**：
- 纸质原型
- 流程图
- 线框图
- 交互原型

**输出**：原型方案

---

## 阶段 5: Test 测试

**目标**：验证解决方案

**问题**：
- 用户对原型的反馈是什么？
- 哪些设计有效？哪些需要改进？
- 需要迭代哪些部分？
- 学到了什么新洞察？

**输出**：测试反馈、迭代建议

---

## 完整工作流

```
Design Thinking (第0轮，可选)
        ↓
产品思考 5 轮追问 (第1-5轮)
        ↓
用户故事 + 测试用例
```

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Draft
"""

    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "product" / resolved_version / "design" / f"{feature.lower().replace(' ', '-')}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ Design Thinking document created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all legacy Design Thinking documents."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)
    design_dir = project_root / "docs" / "product" / resolved_version / "design"

    if not design_dir.exists():
        typer.echo("No Design Thinking documents found")
        return

    documents = list(design_dir.glob("*.md"))
    typer.echo(f"Design Thinking Documents ({len(documents)} found):")
    for doc in documents:
        typer.echo(f"  - {doc.name}")


if __name__ == "__main__":
    app()
