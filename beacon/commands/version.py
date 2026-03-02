"""Beacon version command - Product version planning"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="version", help="Product version planning")


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version number (e.g., 1.0.0)"),
    bump: Optional[str] = typer.Option(None, "--bump", help="Version bump type: patch, minor, major"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a version planning document"""
    project_root = Path(project) if project else Path.cwd()

    # Determine version
    version_str = version if version else "1.0.0"
    if bump:
        parts = version_str.split('.')
        if len(parts) == 3:
            major, minor, patch = map(int, parts)
            if bump == "major":
                major += 1
                minor = 0
                patch = 0
            elif bump == "minor":
                minor += 1
                patch = 0
            elif bump == "patch":
                patch += 1
            version_str = f"{major}.{minor}.{patch}"

    md_content = f"""# 版本规划: {feature}

## 版本信息

- **版本**: {version_str}
- **主题**: TBD
- **目标**: TBD

### 时间范围
- 开始: TBD
- 结束: TBD

### 资源
- PM: TBD
- Dev: TBD
- Design: TBD
- QA: TBD

---

## 用户故事

### US-001: TBD

**版本**: {version_str}
**优先级**: Must
**状态**: New

**用户故事**: 作为 [用户类型]，我希望 [功能]，以便 [价值]。

**验收标准**:
- [ ] TBD

**技术备注**:
- API: TBD
- 数据模型: TBD

**测试重点**: TBD

---

## MoSCoW 优先级

| 优先级 | 比例 | 定义 |
|--------|------|------|
| Must | 20-30% | 上线阻塞项 |
| Should | 30-40% | 重要非阻塞 |
| Could | 20-30% | 锦上添花 |
| Won't | 10% | 本期不实现 |

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Draft
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / "latest" / "version" / f"{feature.lower().replace(' ', '-')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ Version planning document created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all version planning documents"""
    project_root = Path(project) if project else Path.cwd()
    version_dir = project_root / "docs" / "product" / "latest" / "version"

    if not version_dir.exists():
        typer.echo("No version planning documents found")
        return

    documents = list(version_dir.glob("*.md"))
    typer.echo(f"Version Planning Documents ({len(documents)} found):")
    for doc in documents:
        typer.echo(f"  - {doc.name}")


if __name__ == "__main__":
    app()
