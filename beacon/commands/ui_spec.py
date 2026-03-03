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

UI设计规范文档，定义界面视觉、交互和组件标准。

---

## 1. 概述

**设计目标**：
- 简洁、直观、一致

**目标用户**：
- [待填写]

**使用场景**：
- [待填写]

---

## 2. 布局规范

### 2.1 网格系统

- 基础网格: 8px
- 容器最大宽度: 1200px
- 响应式断点:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px

### 2.2 间距系统

- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- xxl: 48px

---

## 3. 色彩规范

### 3.1 主色

- Primary: #3B82F6 (蓝色)
- Primary Hover: #2563EB

### 3.2 辅助色

- Success: #10B981
- Warning: #F59E0B
- Error: #EF4444
- Info: #06B6D4

### 3.3 中性色

- Background: #FFFFFF
- Surface: #F9FAFB
- Border: #E5E7EB
- Text Primary: #111827
- Text Secondary: #6B7280
- Text Disabled: #9CA3AF

---

## 4. 字体规范

- 主字体: System UI, -apple-system, sans-serif
- 标题:
  - H1: 32px / Bold
  - H2: 24px / Semibold
  - H3: 20px / Semibold
- 正文: 14px / Regular
- 小字: 12px / Regular

---

## 5. 组件规范

### 5.1 按钮

- Primary: 背景 #3B82F6, 文字 #FFFFFF
- Secondary: 背景 #F3F4F6, 文字 #374151
- Border Radius: 6px
- Height: 36px (默认), 32px (小), 40px (大)

### 5.2 输入框

- Border: 1px solid #E5E7EB
- Border Radius: 6px
- Height: 36px
- Focus: 边框 #3B82F6

### 5.3 卡片

- Border Radius: 8px
- Shadow: 0 1px 3px rgba(0,0,0,0.1)
- Padding: 16px

---

## 6. 交互规范

- Hover 过渡: 150ms ease
- 点击反馈: scale(0.98)
- Loading 状态: 旋转动画

---

## 7. 状态

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
