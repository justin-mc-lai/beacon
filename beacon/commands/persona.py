"""Beacon persona command - User persona"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="persona", help="User persona")


@app.command()
def create(
    name: str = typer.Argument(..., help="Persona name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a user persona document"""
    project_root = Path(project) if project else Path.cwd()

    md_content = f"""# 用户画像: {name}

**版本**: 1.0
**创建日期**: {datetime.now().strftime('%Y-%m-%d')}
**产品经理**: TBD

---

## 基本信息

| 字段 | 内容 |
|------|------|
| 姓名 | {name} |
| 年龄 | TBD |
| 性别 | TBD |
| 职业 | TBD |
| 收入 | TBD |
| 地区 | TBD |
| 学历 | TBD |
| 婚恋状态 | TBD |

---

## 用户特征

### 人口统计特征
TBD

### 行为特征
- 使用频率: TBD
- 使用场景: TBD
- 渠道偏好: TBD
- 设备偏好: TBD

### 心理特征
- 价值观: TBD
- 兴趣爱好: TBD
- 生活方式: TBD

---

## 目标与动机

### 核心目标
| 目标 | 优先级 | 痛点 |
|------|--------|------|
| TBD | P0 | TBD |

### 动机
- 内在动机: TBD
- 外在动机: TBD

---

## 痛点

### 主要痛点
| 痛点 | 影响 | 当前解决方案 |
|------|------|-------------|
| TBD | TBD | TBD |

### 阻碍因素
- TBD

---

## 使用场景

### 场景 1: TBD
- **时间**: TBD
- **地点**: TBD
- **触发**: TBD
- **行为**: TBD
- **阻碍**: TBD

---

## 需求与期望

### 功能需求
| 需求 | 优先级 | 理由 |
|------|--------|------|
| TBD | P0 | TBD |

### 服务期望
- TBD

---

## 触点与渠道

### 主要触点
| 触点 | 频率 | 满意度 |
|------|------|--------|
| TBD | TBD | TBD |

### 偏好渠道
- 线上: TBD
- 线下: TBD
- 客服: TBD

---

## Quotes

> "TBD"
> - {name}

---

## 设计建议

### 界面偏好
- 风格: TBD
- 配色: TBD
- 交互: TBD

### 功能优先级
1. TBD
2. TBD
3. TBD

---

## 验证

### 调研方法
- [ ] 用户访谈 (N=5)
- [ ] 问卷调查 (N=100)
- [ ] 数据分析
- [ ] 竞品分析

### 验证结果
TBD
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / "personas" / f"{name.lower().replace(' ', '-')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ User persona created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all user personas"""
    project_root = Path(project) if project else Path.cwd()
    personas_dir = project_root / "docs" / "product" / "personas"

    if not personas_dir.exists():
        typer.echo("No user personas found")
        return

    personas = list(personas_dir.glob("*.md"))
    typer.echo(f"User Personas ({len(personas)} found):")
    for persona in personas:
        typer.echo(f"  - {persona.name}")


if __name__ == "__main__":
    app()
