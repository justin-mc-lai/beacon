"""Beacon evolution-summary command - Version evolution summary"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="evolution-summary", help="Version evolution summary")


@app.command()
def create(
    version: str = typer.Argument(..., help="Version number (e.g., v1.0.1)"),
    previous: Optional[str] = typer.Option(None, "--previous", "-p", help="Previous version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a version evolution summary document"""
    project_root = Path(project) if project else Path.cwd()
    previous_version = previous if previous else "v1.0.0"

    md_content = f"""# 演进总结: {version}

自动生成版本演进总结，包含需求变更、用户故事状态、测试覆盖变化与自反馈记录。

---

## 版本信息

- 上一版本: {previous_version}
- 当前版本: {version}
- 版本类型: TBD (patch/minor/major)
- 推进方式: TBD (自动/手动)

---

## 需求变更

### 新增需求
- REQ-001: TBD [NEW]

### 变更需求
- REQ-002: TBD [MODIFIED]

### 废弃需求
- REQ-003: TBD [DEPRECATED]

---

## 用户故事状态

| ID | 标题 | 状态 | 来源 |
|----|------|------|------|
| US-0001 | TBD | [NEW] | - |
| US-0002 | TBD | [INHERITED] | {previous_version} |

---

## 测试覆盖

| 类型 | 数量 | 通过率 |
|------|------|--------|
| [SMOKE] | 0 | - |
| [REGRESSION] | 0 | - |
| [NEW] | 0 | - |
| [FIX] | 0 | - |

---

## 测试自反馈

### 失败用例
- TC-001: TBD → US-0001 → REQ-001
  - 原因: TBD
  - 修复: TBD

### 修复记录
- {datetime.now().strftime('%Y-%m-%d')}: TBD

---

## 自动汇总逻辑

### 版本号推进

- 无参数: 自动 patch+1
- `--bump=minor`: minor+1
- `--bump=major`: major+1

### 用户故事继承

```
新版本用户故事 = 上一版本 [INHERITED]
                + 当前版本新增 [NEW]
                + 当前版本修改 [MODIFIED]
                - 当前版本废弃 [DEPRECATED]
```

### 测试自反馈追溯

```
测试失败 → TC → US → REQ → 修复建议 → 演进总结
```

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Draft
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / version.replace("v", "") / "SUMMARY.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ Version evolution summary created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all version evolution summaries"""
    project_root = Path(project) if project else Path.cwd()
    product_dir = project_root / "docs" / "product"

    if not product_dir.exists():
        typer.echo("No version evolution summaries found")
        return

    # Find all SUMMARY.md files in version directories
    summaries = []
    for d in product_dir.iterdir():
        if d.is_dir():
            summary_file = d / "SUMMARY.md"
            if summary_file.exists():
                summaries.append(summary_file)

    if not summaries:
        typer.echo("No version evolution summaries found")
        return

    typer.echo(f"Version Evolution Summaries ({len(summaries)} found):")
    for summary in summaries:
        typer.echo(f"  - {summary.parent.name}/SUMMARY.md")


if __name__ == "__main__":
    app()
