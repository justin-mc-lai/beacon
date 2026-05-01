"""Beacon ui-spec command - UI Design Specification"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="ui-spec", help="UI Design Specification")


@app.command()
def create(
    name: str = typer.Argument(..., help="UI specification name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a UI Design Specification document"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)

    md_content = f"""# UI Design Specification: {name}

Apple-inspired UI 设计规范文档，默认作为 Beacon 项目的设计基线。

---

## 1. Visual Theme & Atmosphere

- 设计方向：Apple-inspired clarity
- 关键词：克制、安静、精密、可信
- 视觉气质：大留白、弱装饰、内容优先、交互反馈轻但明确
- 适用产品：管理台、工作台、文档浏览、需要长期使用的专业工具
- 不采用：营销站式夸张渐变、过度发光、卡片堆叠、噪音型装饰

---

## 2. Color Palette & Roles

### 2.1 Core Roles

- Canvas: `#F5F5F7`
- Surface Primary: `#FFFFFF`
- Surface Secondary: `#FBFBFD`
- Border Subtle: `#D2D2D7`
- Border Strong: `#C7C7CC`

### 2.2 Text Roles

- Text Primary: `#1D1D1F`
- Text Secondary: `#6E6E73`
- Text Tertiary: `#86868B`
- Text On Accent: `#FFFFFF`

### 2.3 Accent Roles

- Accent Primary: `#0071E3`
- Accent Hover: `#0077ED`
- Accent Pressed: `#0068D1`
- Success: `#2D9D78`
- Warning: `#B26A00`
- Error: `#D92D20`

### 2.4 Usage Rules

- 默认以中性色做大面，强调色只留给关键操作和选中态。
- 不允许使用大面积高饱和渐变当作默认品牌面。
- 不允许纯黑 `#000000` 和纯白 `#FFFFFF` 直接对冲，优先使用带轻微层次的 Apple 风格中性色。

---

## 3. Typography Rules

- 字体栈：`SF Pro Display`, `SF Pro Text`, `-apple-system`, `BlinkMacSystemFont`, `"Helvetica Neue"`, sans-serif
- 字号策略：产品 UI 使用固定 `rem` 层级，不使用 viewport 缩放字级
- 字重策略：以 `400 / 500 / 600` 为主，避免大面积超粗字重

### 3.1 Hierarchy

- H1: `32px / 600 / 1.2`
- H2: `24px / 600 / 1.25`
- H3: `20px / 600 / 1.3`
- Body Large: `16px / 400 / 1.5`
- Body: `14px / 400 / 1.5`
- Caption: `12px / 400 / 1.45`
- Label: `12px / 500 / 1.3`

### 3.2 Typography Rules

- 标题优先短句，不追求密集堆叠。
- 产品型页面正文单行宽度控制在 `65-75ch`。
- 中文界面避免同时混用过多字重和装饰性字体。

---

## 4. Component Stylings

### 4.1 Buttons

- Primary Button
  - Background: `#0071E3`
  - Text: `#FFFFFF`
  - Radius: `999px`
  - Height: `36px`
  - Padding: `0 16px`
- Secondary Button
  - Background: `#FFFFFF`
  - Text: `#1D1D1F`
  - Border: `1px solid #D2D2D7`
  - Radius: `999px`
- Ghost Button
  - Background: `transparent`
  - Text: `#0071E3`
  - Border: `none`

### 4.2 Inputs

- Background: `#FFFFFF`
- Border: `1px solid #D2D2D7`
- Focus Border: `#0071E3`
- Radius: `12px`
- Height: `40px`
- Padding: `0 12px`

### 4.3 Cards / Panels

- Background: `#FFFFFF`
- Border: `1px solid rgba(29,29,31,0.08)`
- Radius: `16px`
- Shadow: `0 8px 24px rgba(15, 23, 42, 0.06)`
- Padding: `16px / 20px / 24px` according to density

### 4.4 Navigation

- 顶部导航保持低噪音，优先使用文字与轻图标。
- 侧栏只在信息架构确实需要多层浏览时出现。
- 当前激活态依靠背景层次和文字权重，不依赖夸张色块。

---

## 5. Layout Principles

### 5.1 Grid & Width

- 基础栅格：`4px`
- 常用间距级别：`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64`
- 内容最大宽度：`1280px`
- 桌面工作台推荐内容宽度：`1180px - 1320px`

### 5.2 Spacing Philosophy

- 信息分组靠留白，不靠过多边框。
- 关键模块之间要有明确呼吸感，避免一屏塞满相同视觉权重的卡片。
- 默认不把整页内容都装进卡片；页面区块优先用无框结构。

---

## 6. Depth & Elevation

- Elevation 0: 页面底色与普通阅读面
- Elevation 1: 普通面板、工具条、列表行 hover
- Elevation 2: 重点浮层、粘性操作区
- 阴影要轻，重心在层级分离，不在“悬浮感炫技”

---

## 7. Do's and Don'ts

### Do

- 让首屏先回答用户当前最重要的问题
- 保持图标、文字、分隔和间距的一致节奏
- 用少量强调色驱动操作层级
- 让 loading / empty / error 状态保持同一套视觉语言

### Don't

- 不要默认做深色霓虹、紫蓝渐变、玻璃拟态
- 不要在工作台里堆满悬浮卡片和营销式大 Hero
- 不要把 runtime / machine / debug 噪音提升成主视觉内容
- 不要用粗重描边和高对比色块破坏安静基调

---

## 8. Responsive Behavior

- Mobile: `< 768px`
  - 单列优先
  - 顶部摘要先于复杂表格
- Tablet: `768px - 1024px`
  - 双栏可选
  - 侧栏按需折叠
- Desktop: `> 1024px`
  - 用宽度换扫描效率，不用宽度堆装饰

- 最小点击热区：`44x44`
- 过渡建议：`120ms - 180ms ease-out`
- respect `prefers-reduced-motion`

---

## 9. Agent Prompt Guide

- Prompt seed:
  - `Use an Apple-inspired product UI baseline: quiet neutral surfaces, SF Pro/system typography, restrained blue accent, large whitespace, subtle depth, rounded-but-not-playful controls, and content-first hierarchy.`
- For Beacon workbench pages:
  - `Prioritize scanability over decoration.`
  - `Homepage answers what needs attention first.`
  - `Project detail builds context before actions.`
  - `Runtime and diagnostics are drill-down surfaces, not the main narrative.`

---

## 10. Metadata

- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Status**: Draft
- **Version**: 1.0.0
"""

    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "product" / resolved_version / "design" / f"ui-spec-{name.lower().replace(' ', '-')}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ UI Specification created: {output_path}")


@app.command("list")
def _list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all UI Design Specifications"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)
    design_dir = project_root / "docs" / "product" / resolved_version / "design"

    if not design_dir.exists():
        typer.echo("No UI Specification documents found")
        return

    docs = list(design_dir.glob("ui-spec-*.md"))
    if not docs:
        typer.echo("No UI Specification documents found")
        return

    typer.echo(f"UI Specifications ({len(docs)} found):")
    for doc in docs:
        typer.echo(f"  - {doc.name}")


if __name__ == "__main__":
    app()
