"""Beacon version command - Version planning and traceability."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.learning_loop import run_evo_experiment
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import discover_versions, normalize_version, resolve_target_version

app = typer.Typer(name="version", help="Version planning and evolution traceability")

_SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class VersionSelection:
    target_version: str
    base_version: str
    strategy: str


def _parse_semver(value: str) -> tuple[int, int, int]:
    match = _SEMVER.match(str(value or "").strip())
    if not match:
        raise ValueError(f"Invalid semver: {value}")
    return tuple(int(x) for x in match.groups())


def _format_semver(parts: tuple[int, int, int]) -> str:
    return f"v{parts[0]}.{parts[1]}.{parts[2]}"


def _bump_semver(version: str, bump: str) -> str:
    major, minor, patch = _parse_semver(version)
    normalized = (bump or "").strip().lower()
    if normalized == "major":
        return _format_semver((major + 1, 0, 0))
    if normalized == "minor":
        return _format_semver((major, minor + 1, 0))
    if normalized == "patch":
        return _format_semver((major, minor, patch + 1))
    raise ValueError(f"Unsupported bump type: {bump}")


def _resolve_version_selection(
    *,
    project_root: Path,
    requested_version: str | None,
    bump: str | None,
    base_version: str | None,
) -> VersionSelection:
    normalized_requested = normalize_version(requested_version)
    normalized_base = normalize_version(base_version)
    normalized_bump = (bump or "").strip().lower()

    if normalized_requested and normalized_requested not in {"auto", "latest"} and normalized_bump:
        raise typer.BadParameter("Cannot use --version together with --bump. Use --base-version + --bump.")

    if normalized_bump:
        if normalized_bump not in {"patch", "minor", "major"}:
            raise typer.BadParameter("--bump must be one of: patch, minor, major")
        baseline = normalized_base or resolve_target_version(project_root, "auto")
        target = _bump_semver(baseline, normalized_bump)
        return VersionSelection(target_version=target, base_version=baseline, strategy=f"bump:{normalized_bump}")

    if normalized_requested and normalized_requested not in {"auto", "latest"}:
        return VersionSelection(
            target_version=normalized_requested,
            base_version=normalized_requested,
            strategy="manual",
        )

    auto = resolve_target_version(project_root, "auto")
    return VersionSelection(target_version=auto, base_version=auto, strategy="auto")


def _slug(text: str) -> str:
    return "-".join([x for x in (text or "").strip().lower().replace("_", " ").split(" ") if x]) or "version-plan"


def _version_plan_roots(project_root: Path, version: str) -> list[Path]:
    return [
        project_root / "docs" / "beacon" / version / "version",
    ]


def _write_version_plan_markdown(
    *,
    path: Path,
    feature: str,
    selection: VersionSelection,
    rationale: str,
    owner: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# 版本规划：{feature}",
                "",
                "## 版本定位",
                "",
                f"- target_version: `{selection.target_version}`",
                f"- base_version: `{selection.base_version}`",
                f"- strategy: `{selection.strategy}`",
                f"- owner: `{owner}`",
                f"- generated_at: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}`",
                "",
                "## 目标与范围",
                "",
                f"- 主题：{feature}",
                f"- 目标：{rationale}",
                "- 范围：对齐 think/user-story/prd/test-case/workflow/gate 闭环",
                "",
                "## 版本演进规则",
                "",
                "1. 默认 `--version auto` 取当前最大语义版本。",
                "2. 指定 `--base-version + --bump` 计算下一目标版本。",
                "3. 指定 `--version vX.Y.Z` 走手动版本锁定。",
                "",
                "## 追溯",
                "",
                "- 推荐随后执行：",
                f"  - `beacon evolution-summary create {selection.target_version}`",
                f"  - `beacon workflow start \"{feature}\" --version {selection.target_version}`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    version: Optional[str] = typer.Option("auto", "--version", "-v", help="Target version or auto/latest"),
    bump: Optional[str] = typer.Option(None, "--bump", help="Version bump type: patch, minor, major"),
    base_version: Optional[str] = typer.Option(
        None,
        "--base-version",
        help="Base version used together with --bump (e.g., v1.2.3)",
    ),
    rationale: str = typer.Option("迭代改进", "--rationale", help="Version objective summary"),
    owner: str = typer.Option("TBD", "--owner", help="Version owner"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Explicit output markdown path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Create version planning artifacts with traceability metadata."""
    project_root = Path(project) if project else Path.cwd()
    selection = _resolve_version_selection(
        project_root=project_root,
        requested_version=version,
        bump=bump,
        base_version=base_version,
    )
    slug = _slug(feature)
    created_files: list[str] = []

    if output:
        output_path = Path(output)
        _write_version_plan_markdown(
            path=output_path,
            feature=feature,
            selection=selection,
            rationale=rationale,
            owner=owner,
        )
        created_files.append(str(output_path))
    else:
        for root in _version_plan_roots(project_root, selection.target_version):
            target = root / f"{slug}.md"
            _write_version_plan_markdown(
                path=target,
                feature=feature,
                selection=selection,
                rationale=rationale,
                owner=owner,
            )
            created_files.append(str(target))

    metadata = {
        "schema_version": "1.0",
        "feature": feature,
        "slug": slug,
        "target_version": selection.target_version,
        "base_version": selection.base_version,
        "strategy": selection.strategy,
        "requested_version": version or "",
        "bump": (bump or "").strip().lower(),
        "rationale": rationale,
        "owner": owner,
        "artifacts": created_files,
        "created_at": now_iso(),
    }
    metadata_path = (
        project_root
        / ".beacon"
        / "state"
        / "version-plans"
        / selection.target_version
        / f"{slug}.json"
    )
    write_json(metadata_path, metadata)
    created_files.append(str(metadata_path))

    if json_output:
        typer.echo(json.dumps({"status": "ok", "version_plan": metadata}, ensure_ascii=False, indent=2))
        return

    typer.echo("✓ Version plan created")
    typer.echo(f"  target_version: {selection.target_version}")
    typer.echo(f"  strategy: {selection.strategy}")
    for path in created_files:
        typer.echo(f"  - {path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version filter"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """List version planning artifacts across versions."""
    project_root = Path(project) if project else Path.cwd()
    versions = discover_versions(project_root)
    if version:
        versions = [resolve_target_version(project_root, version)]
    if not versions:
        versions = [resolve_target_version(project_root, "auto")]

    records: list[dict[str, Any]] = []
    for ver in versions:
        for docs_type in ("beacon", "product"):
            root = project_root / "docs" / docs_type / ver / "version"
            if not root.exists():
                continue
            for path in sorted(root.glob("*.md")):
                records.append(
                    {
                        "version": ver,
                        "docs_type": docs_type,
                        "file": str(path),
                    }
                )

    if json_output:
        typer.echo(json.dumps({"count": len(records), "items": records}, ensure_ascii=False, indent=2))
        return

    if not records:
        typer.echo("No version plan documents found")
        return

    typer.echo(f"Version Plans ({len(records)} found):")
    for item in records:
        typer.echo(
            f"  - [{item['version']}] ({item['docs_type']}) {Path(item['file']).name}"
        )


@app.command("experiment")
def experiment(
    label: str = typer.Argument("Beacon v1.1.10 evo harness", help="Experiment label"),
    version: Optional[str] = typer.Option("auto", "--version", "-v", help="Target docs version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    max_runtime_minutes: int = typer.Option(0, "--max-runtime-minutes", help="Budget override"),
    max_iterations: int = typer.Option(0, "--max-iterations", help="Budget override"),
    max_command_count: int = typer.Option(0, "--max-command-count", help="Budget override"),
    max_evidence_budget: int = typer.Option(0, "--max-evidence-budget", help="Budget override"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Run a fixed-budget evo experiment over the current keep/discard engine."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    budget_overrides = {
        key: value
        for key, value in {
            "max_runtime_minutes": max_runtime_minutes,
            "max_iterations": max_iterations,
            "max_command_count": max_command_count,
            "max_evidence_budget": max_evidence_budget,
        }.items()
        if int(value or 0) > 0
    }
    payload = run_evo_experiment(
        project_root,
        version=resolved_version,
        experiment_label=label,
        budget_overrides=budget_overrides,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("✓ Evo experiment completed")
    typer.echo(f"  run_id: {payload['run_id']}")
    typer.echo(f"  verdict: {payload['verdict']}")
    typer.echo(f"  main_kpi_score: {payload['main_kpi_score']}")
    typer.echo(f"  false_complete_rate: {payload['metrics']['false_complete_rate']}")
    typer.echo(f"  path: {payload['path']}")


if __name__ == "__main__":
    app()
