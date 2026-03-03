"""Beacon brainstorm command - Divergent thinking exploration"""
import typer
from typing import Optional
from pathlib import Path

from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="brainstorm", help="Divergent thinking exploration")


@app.command()
def create(
    topic: str = typer.Argument(..., help="Topic for brainstorming"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a brainstorming document"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)

    md_content = f"""# 发散思维: {topic}

通过七维度发散提问，发现隐藏的联系和可能性。

---

## 维度一：用户维度

**问题：这个功能的核心用户是谁？**

| 选项 | 用户类型 | 特征 |
|------|---------|------|
| A | 年轻用户 | 18-25岁，追求新鲜，爱分享 |
| B | 成熟用户 | 26-40岁，注重效率，实用主义 |
| C | 老年用户 | 45+，操作简单，界面清晰 |
| D | 专业用户 | 高频使用，功能全面 |
| E | 休闲用户 | 低频使用，功能简单 |

**扩展问题**：
- 谁还会用？（潜在用户）
- 谁一定不用？（排斥用户）

---

## 维度二：场景维度

**问题：用户会在什么场景下使用？**

| 场景类型 | 是/否 | 具体场景 |
|---------|-------|---------|
| 碎片时间 | 是/否 | 通勤、排队、等电梯 |
| 专注时间 | 是/否 | 晚上、周末、假期 |
| 工作场景 | 是/否 | 上班、开会、外出办公 |
| 生活场景 | 是/否 | 家里、商场、餐厅 |

**触发场景**：用户什么情况下会想到用这个功能？

**连续场景**：
- 使用前一步做什么？
- 使用后一步做什么？

---

## 维度三：业务维度

**问题：这个功能怎么赚钱？**

| 商业模式 | 适合度 | 说明 |
|---------|-------|------|
| 付费会员 | ★★★★★ | 高级功能付费 |
| 广告变现 | ★★★★☆ | 展示广告/信息流 |
| 交易抽成 | ★★★☆☆ | 交易流水抽成 |
| 增值服务 | ★★★☆☆ | 道具/周边付费 |
| 暂不考虑 | ★★☆☆☆ | 先做用户规模 |

**竞品分析**：
- 竞品A：TBD
- 竞品B：TBD
- 差异化机会：TBD

---

## 维度四：技术维度

**问题：技术实现的主要挑战？**

| 挑战类型 | 难度 | 应对方案 |
|---------|-----|---------|
| 性能要求 | 高/中/低 | |
| 实时性 | 高/中/低 | |
| 兼容性 | 高/中/低 | |
| 数据量 | 大/中/小 | |
| 第三方依赖 | 多/少 | |

---

## 维度五：体验维度

**问题：用户使用这个功能的关键体验？**

| 体验点 | 重要度 | 当前方案 |
|-------|-------|---------|
| 操作简单 | ★★★★★ | |
| 反馈及时 | ★★★★☆ | |
| 界面美观 | ★★★☆☆ | |
| 学习成本低 | ★★★★☆ | |
| 成就感 | ★★★☆☆ | |

**用户情绪曲线**：
- 使用前：好奇 / 期待 / 困惑 / 无感
- 使用中：顺畅 / 挫败 / 惊喜 / 耐心
- 使用后：满足 / 失望 / 惊喜 / 无感

---

## 维度六：价值维度

**问题：这个功能的核心价值？**

| 价值类型 | 优先级 | 说明 |
|---------|-------|------|
| 功能价值 | ★★★★★ | 解决实际问题 |
| 情感价值 | ★★★★☆ | 满足情感需求 |
| 社交价值 | ★★★☆☆ | 促进社交互动 |
| 经济价值 | ★★★☆☆ | 省钱/赚钱 |
| 品牌价值 | ★★☆☆☆ | 提升品牌形象 |

---

## 维度七：风险维度

**问题：可能的风险及应对？**

| 风险类型 | 概率 | 影响 | 应对方案 |
|---------|-----|-----|---------|
| 用户不用 | 高/中/低 | 大/小 | |
| 竞品抄袭 | 高/中/低 | 大/小 | |
| 技术问题 | 高/中/低 | 大/小 | |
| 政策风险 | 高/中/低 | 大/小 | |
| 运营压力 | 高/中/低 | 大/小 | |

---

## 工作流

```
核心问题 → 七维发散 → 收集想法 → 分类整理 → 聚类关联 → 收敛优先级 → 形成方案
```
"""

    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "product" / resolved_version / "brainstorm" / f"{topic.lower().replace(' ', '-')}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ Brainstorm document created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all brainstorming documents"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)
    brainstorm_dir = project_root / "docs" / "product" / resolved_version / "brainstorm"

    if not brainstorm_dir.exists():
        typer.echo("No brainstorming documents found")
        return

    documents = list(brainstorm_dir.glob("*.md"))
    typer.echo(f"Brainstorming Documents ({len(documents)} found):")
    for doc in documents:
        typer.echo(f"  - {doc.name}")


if __name__ == "__main__":
    app()
