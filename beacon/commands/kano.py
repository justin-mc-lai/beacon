"""Beacon kano command - KANO model analysis"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="kano", help="KANO model analysis")


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature or product for KANO analysis"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a KANO model analysis document"""
    project_root = Path(project) if project else Path.cwd()

    md_content = f"""# KANO 模型分析: {feature}

使用 KANO 模型对功能进行分类分析，理解用户满意度与功能实现的关系。

---

## KANO 框架

### 5 类需求

| 类型 | 含义 | 用户满意度 | 例子 |
|------|------|-----------|------|
| **Must-be** | 必备型 | 有→满意，无→不满意 | 基础功能、安全性 |
| **One-dimensional** | 期望型 | 有→满意，无→不满意 | 性能、响应速度 |
| **Attractive** | 兴奋型 | 有→惊喜，无→无影响 | 创新功能、彩蛋 |
| **Indifferent** | 无差异型 | 有无都无所谓 | 冗余功能 |
| **Reverse** | 反向型 | 有→不满意，无→满意 | 强制弹窗、复杂流程 |

---

## 用户反应矩阵

| 功能\期望 | 我喜欢 | 理应如此 | 无所谓 | 勉强接受 | 我不喜欢 |
|----------|-------|---------|-------|---------|---------|
| **有该功能** | Q | A | A | O | M |
| **无该功能** | R | I | I | M | Q |

### 分类结果
- **A (Attractive)**: 兴奋型需求
- **O (One-dimensional)**: 期望型需求
- **M (Must-be)**: 必备型需求
- **I (Indifferent)**: 无差异需求
- **R (Reverse)**: 反向需求
- **Q (Questionable)**: 可疑结果（需重新调研）

---

## 功能列表

| 功能 | 假设类型 | 优先级 |
|------|---------|--------|
| TBD | Must-be | P0 |
| TBD | One-dimensional | P1 |
| TBD | Attractive | P2 |

---

## 问卷设计

### 正向问题
如果该功能可用，您的感受是？
- [ ] 我喜欢
- [ ] 理应如此
- [ ] 无所谓
- [ ] 勉强接受
- [ ] 我不喜欢

### 负向问题
如果该功能不可用，您的感受是？
- [ ] 我喜欢
- [ ] 理应如此
- [ ] 无所谓
- [ ] 勉强接受
- [ ] 我不喜欢

---

## 分析结果

| 功能 | A% | O% | M% | I% | R% | Q% | 分类 |
|------|-----|-----|-----|-----|-----|-----|------|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

---

## KANO 分析报告

### Must-be (必备型)
| 功能 | 影响 | 建议 |
|------|------|------|
| TBD | 满意度大幅下降 | 必须实现 |

### One-dimensional (期望型)
| 功能 | 满意度曲线 | 建议 |
|------|-------------|------|
| TBD | 线性相关 | 尽量实现 |

### Attractive (兴奋型)
| 功能 | 惊喜程度 | 建议 |
|------|---------|------|
| TBD | 高 | 尽量实现 |

### Indifferent (无差异)
| 功能 | 处理建议 |
|------|---------|
| TBD | 可考虑不做 |

### Reverse (反向)
| 功能 | 问题 | 建议 |
|------|------|------|
| TBD | TBD | 避免实现 |

---

## 决策建议

1. **Must-be 优先**: 必须满足，否则用户不满意
2. **关注 O/A**: 投入产出比最高
3. **避免 R**: 用户反感的功能不做
4. **简化 I**: 无差异功能可不做

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Draft
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / "latest" / "kano" / f"{feature.lower().replace(' ', '-')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ KANO analysis created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all KANO analyses"""
    project_root = Path(project) if project else Path.cwd()
    kano_dir = project_root / "docs" / "product" / "latest" / "kano"

    if not kano_dir.exists():
        typer.echo("No KANO analyses found")
        return

    analyses = list(kano_dir.glob("*.md"))
    typer.echo(f"KANO Analyses ({len(analyses)} found):")
    for analysis in analyses:
        typer.echo(f"  - {analysis.name}")


if __name__ == "__main__":
    app()
