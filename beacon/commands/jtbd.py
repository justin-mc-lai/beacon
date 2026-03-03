"""Beacon jtbd command - Jobs-to-be-Done framework"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="jtbd", help="Jobs-to-be-Done framework")


@app.command()
def create(
    product: str = typer.Argument(..., help="Product or service for JTBD analysis"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a JTBD analysis document"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)

    md_content = f"""# JTBD 分析: {product}

理解用户"雇佣"产品来完成的工作，而不仅仅是产品功能。

---

## 核心任务

**问题**：用户雇佣这个产品来完成什么工作？

**格式**：
> 当我想要 [要完成的进度] 时，我会使用 [产品] 来帮助我 [预期的解决方案]。

---

## 任务维度

### 功能性任务 (Functional Jobs)
- 用户需要完成什么具体任务？
- 有什么痛点需要解决？
- 效率如何提升？

### 情感性任务 (Emotional Jobs)
- 用户希望感受到什么？
- 希望别人如何看待自己？
- 想要避免什么负面情绪？

### 社会性任务 (Social Jobs)
- 用户希望如何在他人面前展示自己？
- 想要融入哪个群体？
- 想要区别于哪个群体？

---

## 用户旅程

| 阶段 | 用户想法 | 痛点 | 机会点 |
|------|---------|------|-------|
| 开始前 | | | |
| 寻找中 | | | |
| 选择时 | | | |
| 使用中 | | | |
| 使用后 | | | |

---

## 竞争对手

**问题**：用户现在用什么替代方案？

| 替代方案 | 用户为什么选择它？ | 它的缺点是什么？ |
|---------|-----------------|----------------|
| 竞品A | | |
| 竞品B | | |
| 自己动手 | | |
| 凑合不用 | | |
| 完全不做 | | |

---

## 推动力与阻碍

**推动力**（让用户选择你的产品）：
- TBD
- TBD

**阻碍**（让用户不选择你的产品）：
- TBD
- TBD

---

## 输出模板

### 核心任务
[一句话描述用户要完成的工作]

### 任务维度
- 功能性任务：TBD
- 情感性任务：TBD
- 社会性任务：TBD

### 用户画像
- 典型用户：TBD
- 使用场景：TBD

### 竞争格局
- 直接竞品：TBD
- 间接竞品：TBD
- 替代方案：TBD

### 产品机会
- 核心机会1：TBD
- 核心机会2：TBD

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Draft
"""

    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "product" / resolved_version / "jtbd" / f"{product.lower().replace(' ', '-')}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ JTBD analysis created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all JTBD analyses"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)
    jtbd_dir = project_root / "docs" / "product" / resolved_version / "jtbd"

    if not jtbd_dir.exists():
        typer.echo("No JTBD analyses found")
        return

    analyses = list(jtbd_dir.glob("*.md"))
    typer.echo(f"JTBD Analyses ({len(analyses)} found):")
    for analysis in analyses:
        typer.echo(f"  - {analysis.name}")


if __name__ == "__main__":
    app()
