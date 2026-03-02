"""Beacon roadmap command - Product roadmap"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="roadmap", help="Product roadmap")


@app.command()
def create(
    product: str = typer.Argument(..., help="Product name"),
    period: Optional[str] = typer.Option(None, "--period", "-t", help="Time period (e.g., 2024-Q1)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a product roadmap document"""
    project_root = Path(project) if project else Path.cwd()
    period_str = period if period else datetime.now().strftime('%Y-Q%m')

    md_content = f"""# 产品路线图: {product}

**版本**: 1.0
**周期**: {period_str}
**产品经理**: TBD

---

## 愿景

> TBD (一句话描述产品愿景)

---

## 战略目标

| 目标 | 衡量指标 | 时间范围 |
|------|---------|---------|
| TBD | TBD | TBD |

---

## 版本规划

### Q1

| 版本 | 主题 | 关键功能 | 日期 |
|------|------|---------|------|
| v1.0 | MVP | TBD | TBD |
| v1.1 | 优化 | TBD | TBD |

### Q2

| 版本 | 主题 | 关键功能 | 日期 |
|------|------|---------|------|
| v1.2 | TBD | TBD | TBD |
| v1.3 | TBD | TBD | TBD |

---

## 路线图视图

### 时间轴视图

```
Q1 ---------------------
  v1.0 [========]
  v1.1      [====]
Q2 -----------------------
  v1.2            [====]
  v1.3                 [====]
```

### 功能视图

| 功能 | 状态 | Q1 | Q2 | Q3 | Q4 |
|------|------|----|----|----|---|
| TBD | 规划 | ✓ | | | |
| TBD | 开发中 | | ✓ | | |
| TBD | 完成 | | | ✓ | |

---

## 里程碑

| 里程碑 | 日期 | 交付物 | 状态 |
|--------|------|--------|------|
| TBD | TBD | TBD | TBD |

---

## 依赖与风险

### 技术依赖
| 依赖项 | 负责方 | 完成时间 |
|--------|-------|---------|
| TBD | TBD | TBD |

### 风险
| 风险 | 影响 | 应对措施 |
|------|------|---------|
| TBD | TBD | TBD |

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Draft
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / "latest" / "roadmap" / f"{product.lower().replace(' ', '-')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ Product roadmap created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all product roadmaps"""
    project_root = Path(project) if project else Path.cwd()
    roadmap_dir = project_root / "docs" / "product" / "latest" / "roadmap"

    if not roadmap_dir.exists():
        typer.echo("No product roadmaps found")
        return

    roadmaps = list(roadmap_dir.glob("*.md"))
    typer.echo(f"Product Roadmaps ({len(roadmaps)} found):")
    for roadmap in roadmaps:
        typer.echo(f"  - {roadmap.name}")


if __name__ == "__main__":
    app()
