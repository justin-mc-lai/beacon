"""Beacon wireframe command - Wireframe/Storyboard"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="wireframe", help="Wireframe/Storyboard design")


@app.command()
def create(
    name: str = typer.Argument(..., help="Wireframe name or page name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a Wireframe description document"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)

    md_content = f"""# Wireframe: {name}

线框图/草稿图设计文档，描述页面布局和交互结构。

---

## 1. 概述

**页面名称**: {name}
**类型**: [列表页 / 详情页 / 表单页 / 弹窗 / 其他]
**目标用户**: [待填写]
**核心功能**: [待填写]

---

## 2. 布局结构

```
+------------------------------------------+
|              Header (顶部)              |
+------------------------------------------+
|  Sidebar  |       Main Content          |
|  (侧边栏)  |       (主内容区)            |
|            |                             |
|            |                             |
+------------------------------------------+
|              Footer (底部)              |
+------------------------------------------+
```

### 2.1 区域定义

| 区域 | 描述 | 优先级 |
|------|------|--------|
| Header | 导航栏、Logo、用户信息 | 必须 |
| Sidebar | 菜单、筛选器 | 可选 |
| Main | 核心内容展示 | 必须 |
| Footer | 版权、链接 | 可选 |

---

## 3. 元素清单

### 3.1 头部区域

- [ ] Logo
- [ ] 导航菜单
- [ ] 用户头像/登录
- [ ] 搜索框

### 3.2 内容区域

- [ ] 标题
- [ ] 面包屑
- [ ] 功能按钮
- [ ] 数据列表
- [ ] 分页控件

### 3.3 交互元素

| 元素 | 行为 | 状态 |
|------|------|------|
| 按钮 | 点击执行操作 | default/hover/active/disabled |
| 链接 | 跳转页面 | default/hover/visited |
| 输入框 | 输入内容 | default/focus/error/disabled |
| 复选框 | 选择/取消 | checked/unchecked |

---

## 4. 信息架构

### 4.1 数据字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 唯一标识 |
| name | string | 是 | 名称 |
| status | enum | 否 | 状态 |

### 4.2 列表字段

- 序号
- 名称/标题
- 状态
- 创建时间
- 操作

---

## 5. 视觉标注

### 5.1 颜色

- 主色: #3B82F6
- 背景: #FFFFFF
- 边框: #E5E7EB

### 5.2 间距

- 组件间距: 16px
- 内边距: 12px / 16px / 24px

### 5.3 圆角

- 按钮: 6px
- 卡片: 8px
- 输入框: 6px

---

## 6. 响应式设计

| 断点 | 布局变化 |
|------|----------|
| < 768px | 隐藏侧边栏，堆叠布局 |
| 768-1024px | 侧边栏可折叠 |
| > 1024px | 完整布局 |

---

## 7. 状态

- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Status**: Draft
- **Version**: 1.0.0
"""

    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "product" / resolved_version / "design" / f"wireframe-{name.lower().replace(' ', '-')}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ Wireframe document created: {output_path}")


@app.command("list")
def _list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all Wireframe documents"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)
    design_dir = project_root / "docs" / "product" / resolved_version / "design"

    if not design_dir.exists():
        typer.echo("No Wireframe documents found")
        return

    docs = list(design_dir.glob("wireframe-*.md"))
    if not docs:
        typer.echo("No Wireframe documents found")
        return

    typer.echo(f"Wireframes ({len(docs)} found):")
    for doc in docs:
        typer.echo(f"  - {doc.name}")


if __name__ == "__main__":
    app()
