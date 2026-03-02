"""Beacon moscow command - MoSCoW prioritization"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="moscow", help="MoSCoW prioritization")


@app.command()
def create(
    feature: str = typer.Argument("default", help="Feature or requirement for prioritization"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a MoSCoW prioritization document"""
    project_root = Path(project) if project else Path.cwd()

    md_content = f"""# MoSCoW 优先级排序: {feature}

使用 MoSCoW 方法对需求进行优先级排序。

---

## MoSCoW 框架

| 优先级 | 比例 | 定义 | 含义 |
|--------|------|------|------|
| **Must** | 20-30% | 必须做 | 上线阻塞项，没有这个功能产品无法发布 |
| **Should** | 30-40% | 应该做 | 重要非阻塞，强烈建议实现 |
| **Could** | 20-30% | 可以做 | 锦上添花，有时间再做 |
| **Won't** | 10% | 不做 | 本期不实现，未来可能考虑 |

---

## 快速判断方法

### 问题法
1. **没有这个功能能上线吗？**
   - 不能 → Must
   - 能 → 继续

2. **不做用户会流失吗？**
   - 会 → Should
   - 不会 → 继续

3. **做了用户体验会显著提升吗？**
   - 会 → Could
   - 不会 → Won't

---

## MoSCoW 优先级排序

### Must (必须做) - 0 项
| ID | 需求 | 理由 |
|----|------|------|
| TBD | TBD | TBD |

### Should (应该做) - 0 项
| ID | 需求 | 理由 |
|----|------|------|
| TBD | TBD | TBD |

### Could (可以做) - 0 项
| ID | 需求 | 理由 |
|----|------|------|
| TBD | TBD | TBD |

### Won't (本期不做) - 0 项
| ID | 需求 | 理由 |
|----|------|------|
| TBD | TBD | TBD |

---

## 决策记录

### 争议项讨论
| 需求 | 分歧点 | 决策 | 决策人 |
|------|--------|------|--------|
| TBD | TBD | TBD | TBD |

### 优先级变更历史
| 日期 | 需求 | 原优先级 | 新优先级 | 变更原因 |
|------|------|----------|----------|----------|
| TBD | TBD | TBD | TBD | TBD |

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Draft
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / "latest" / "moscow" / f"{feature.lower().replace(' ', '-')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ MoSCoW prioritization created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all MoSCoW documents"""
    project_root = Path(project) if project else Path.cwd()
    moscow_dir = project_root / "docs" / "product" / "latest" / "moscow"

    if not moscow_dir.exists():
        typer.echo("No MoSCoW documents found")
        return

    documents = list(moscow_dir.glob("*.md"))
    typer.echo(f"MoSCoW Documents ({len(documents)} found):")
    for doc in documents:
        typer.echo(f"  - {doc.name}")


if __name__ == "__main__":
    app()
