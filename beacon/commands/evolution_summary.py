"""Beacon evolution-summary command - Version evolution summary."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.versioning import discover_versions, normalize_version, resolve_target_version

app = typer.Typer(name="evolution-summary", help="Version evolution summary")


def _semver_key(version: str) -> tuple[int, int, int]:
    raw = (version or "").strip().lstrip("v")
    parts = raw.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _infer_previous_version(project_root: Path, current_version: str) -> str:
    versions = discover_versions(project_root)
    current_key = _semver_key(current_version)
    older = [v for v in versions if _semver_key(v) < current_key]
    if not older:
        return "N/A"
    return sorted(older, key=_semver_key)[-1]


@app.command()
def create(
    version: str = typer.Argument(..., help="Version number (e.g., v1.0.1 or auto)"),
    previous: Optional[str] = typer.Option(None, "--previous", help="Previous version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a version evolution summary document."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    previous_version = (
        normalize_version(previous) if previous else _infer_previous_version(project_root, resolved_version)
    ) or "N/A"

    md_content = f"""# 演进总结: {resolved_version}

自动生成版本演进总结，包含需求变更、用户故事状态、测试覆盖变化与自反馈记录。

---

## 版本信息

- 上一版本: {previous_version}
- 当前版本: {resolved_version}
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

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_content, encoding="utf-8")
        typer.echo(f"✓ Version evolution summary created: {output_path}")
        return

    output_paths = [
        project_root / "docs" / "beacon" / resolved_version / "SUMMARY.md",
        project_root / "docs" / "product" / resolved_version / "SUMMARY.md",
    ]
    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_content, encoding="utf-8")

    typer.echo(f"✓ Version evolution summary created: {output_paths[0]}")
    typer.echo(f"✓ Version evolution summary created: {output_paths[1]}")


@app.command("list")
def list_summaries(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all version evolution summaries."""
    project_root = Path(project) if project else Path.cwd()
    summaries: dict[str, Path] = {}
    for docs_type in ("beacon", "product"):
        root = project_root / "docs" / docs_type
        if not root.exists():
            continue
        for version_dir in root.iterdir():
            if not version_dir.is_dir():
                continue
            summary_file = version_dir / "SUMMARY.md"
            if summary_file.exists():
                summaries[version_dir.name] = summary_file

    if not summaries:
        typer.echo("No version evolution summaries found")
        return

    ordered = sorted(summaries.items(), key=lambda x: _semver_key(normalize_version(x[0]) or "v0.0.0"))
    typer.echo(f"Version Evolution Summaries ({len(ordered)} found):")
    for version_name, summary_file in ordered:
        typer.echo(f"  - {version_name}/SUMMARY.md ({summary_file.parent.parent.name})")


if __name__ == "__main__":
    app()
