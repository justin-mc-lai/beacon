"""Beacon evolution-summary command - version evolution insights from real artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.cli_version_guard import resolve_target_version_guarded
from beacon.utils.versioning import discover_versions, normalize_version
from beacon.utils.workflow_memory import compute_memory_metrics, load_lifecycle_events

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


def _collect_feature_slugs(project_root: Path, version: str, doc_type: str, section: str) -> set[str]:
    root = project_root / "docs" / doc_type / version / section
    if not root.exists():
        return set()
    return {path.stem for path in root.glob("*.md")}


def _load_run_state_items(project_root: Path, version: str) -> list[dict[str, Any]]:
    runs_dir = project_root / ".beacon" / "runs"
    if not runs_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for run_dir in runs_dir.iterdir():
        state_file = run_dir / "state.json"
        if not state_file.exists():
            continue
        try:
            payload = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(payload, dict):
            continue
        if str(payload.get("version", "")).strip() != version:
            continue
        out.append(payload)
    out.sort(key=lambda x: str(x.get("ended_at") or x.get("started_at") or ""))
    return out


@dataclass
class EvidenceStats:
    entries: int
    missing_files: int


def _evidence_stats(project_root: Path) -> EvidenceStats:
    manifest = project_root / ".beacon" / "evidence-manifest.json"
    if not manifest.exists():
        return EvidenceStats(entries=0, missing_files=0)
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return EvidenceStats(entries=0, missing_files=0)
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return EvidenceStats(entries=0, missing_files=0)
    valid = [x for x in entries if isinstance(x, dict) and str(x.get("path", "")).strip()]
    missing = 0
    for item in valid:
        ref = str(item.get("path"))
        if not (project_root / ref).exists():
            missing += 1
    return EvidenceStats(entries=len(valid), missing_files=missing)


def _release_events_for_version(project_root: Path, version: str) -> list[dict[str, Any]]:
    events = load_lifecycle_events(project_root, stage="release")
    out = []
    for event in events:
        details = event.get("details")
        if not isinstance(details, dict):
            continue
        if str(details.get("version", "")).strip() == version:
            out.append(event)
    return out


def _delta(current: int, previous: int) -> str:
    sign = "+" if current - previous >= 0 else "-"
    return f"{sign}{abs(current - previous)}"


def _build_summary_payload(
    *,
    project_root: Path,
    version: str,
    previous_version: str,
) -> dict[str, Any]:
    current_coverage = compute_coverage_metrics(project_root, version=version)
    previous_coverage = (
        compute_coverage_metrics(project_root, version=previous_version)
        if previous_version != "N/A"
        else None
    )
    current_memory = compute_memory_metrics(project_root, version=version)
    previous_memory = (
        compute_memory_metrics(project_root, version=previous_version)
        if previous_version != "N/A"
        else None
    )
    run_items = _load_run_state_items(project_root, version)
    run_status_count: dict[str, int] = {}
    for item in run_items:
        status = str(item.get("status", "unknown"))
        run_status_count[status] = run_status_count.get(status, 0) + 1

    user_story_current = (
        _collect_feature_slugs(project_root, version, "product", "user-story")
        | _collect_feature_slugs(project_root, version, "beacon", "user-story")
    )
    user_story_previous = (
        (
            _collect_feature_slugs(project_root, previous_version, "product", "user-story")
            | _collect_feature_slugs(project_root, previous_version, "beacon", "user-story")
        )
        if previous_version != "N/A"
        else set()
    )

    added_stories = sorted(user_story_current - user_story_previous)
    inherited_stories = sorted(user_story_current & user_story_previous)
    removed_stories = sorted(user_story_previous - user_story_current) if previous_version != "N/A" else []

    evidence = _evidence_stats(project_root)
    releases = _release_events_for_version(project_root, version)

    return {
        "schema_version": "1.0",
        "current_version": version,
        "previous_version": previous_version,
        "generated_at": now_iso(),
        "runs": {
            "count": len(run_items),
            "status_count": run_status_count,
            "latest_run_id": str(run_items[-1].get("run_id", "")) if run_items else "",
            "latest_status": str(run_items[-1].get("status", "")) if run_items else "",
        },
        "stories": {
            "current_total": len(user_story_current),
            "previous_total": len(user_story_previous),
            "added": added_stories,
            "inherited": inherited_stories,
            "removed": removed_stories,
        },
        "coverage": {
            "current": current_coverage,
            "previous": previous_coverage,
            "delta": {
                "implemented_story": _delta(
                    int(current_coverage.get("implemented_story", 0)),
                    int(previous_coverage.get("implemented_story", 0)) if previous_coverage else 0,
                ),
                "tested_ac": _delta(
                    int(current_coverage.get("tested_ac", 0)),
                    int(previous_coverage.get("tested_ac", 0)) if previous_coverage else 0,
                ),
                "executed_tc": _delta(
                    int(current_coverage.get("executed_tc", 0)),
                    int(previous_coverage.get("executed_tc", 0)) if previous_coverage else 0,
                ),
            },
        },
        "memory": {
            "current": current_memory,
            "previous": previous_memory,
            "delta_writebacks": _delta(
                int(current_memory.get("writebacks", 0)),
                int(previous_memory.get("writebacks", 0)) if previous_memory else 0,
            ),
            "delta_feedback_assimilations": _delta(
                int(current_memory.get("feedback_assimilations", 0)),
                int(previous_memory.get("feedback_assimilations", 0)) if previous_memory else 0,
            ),
        },
        "evidence": {
            "manifest_entries": evidence.entries,
            "manifest_missing_files": evidence.missing_files,
        },
        "release_profile": {
            "events": len(releases),
            "last_status": str(releases[-1].get("details", {}).get("status", "")) if releases else "",
            "last_reason": str(releases[-1].get("details", {}).get("reason", "")) if releases else "",
        },
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    current_version = payload.get("current_version", "")
    previous_version = payload.get("previous_version", "")
    stories = payload.get("stories", {})
    coverage = payload.get("coverage", {})
    coverage_current = coverage.get("current", {})
    coverage_delta = coverage.get("delta", {})
    memory = payload.get("memory", {})
    memory_current = memory.get("current", {})
    runs = payload.get("runs", {})
    evidence = payload.get("evidence", {})
    release_profile = payload.get("release_profile", {})

    added = stories.get("added", [])
    removed = stories.get("removed", [])
    inherited = stories.get("inherited", [])

    def _list(values: list[str], empty: str = "- 无") -> list[str]:
        if not values:
            return [empty]
        return [f"- {item}" for item in values]

    lines = [
        f"# 演进总结: {current_version}",
        "",
        f"- 上一版本: {previous_version}",
        f"- 当前版本: {current_version}",
        f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 运行闭环状态",
        "",
        f"- 关联 run 数: {runs.get('count', 0)}",
        f"- 最新 run: `{runs.get('latest_run_id', '-')}` ({runs.get('latest_status', '-')})",
        f"- release 记忆事件: {release_profile.get('events', 0)}",
        f"- release 最近状态: `{release_profile.get('last_status', '-')}` / `{release_profile.get('last_reason', '-')}`",
        "",
        "## 需求与用户故事演进",
        "",
        f"- 当前故事总数: {stories.get('current_total', 0)}",
        f"- 上版故事总数: {stories.get('previous_total', 0)}",
        "",
        "### 新增故事",
        *_list(added),
        "",
        "### 继承故事",
        *_list(inherited),
        "",
        "### 移除故事",
        *_list(removed),
        "",
        "## 测试覆盖变化",
        "",
        "| 指标 | 当前 | 变化 |",
        "|------|------|------|",
        f"| Implemented Story | {coverage_current.get('implemented_story', 0)}/{coverage_current.get('planned_story', 0)} | {coverage_delta.get('implemented_story', '0')} |",
        f"| Tested AC | {coverage_current.get('tested_ac', 0)}/{coverage_current.get('total_ac', 0)} | {coverage_delta.get('tested_ac', '0')} |",
        f"| Executed TC | {coverage_current.get('executed_tc', 0)}/{coverage_current.get('total_tc', 0)} | {coverage_delta.get('executed_tc', '0')} |",
        f"| Full Coverage | {coverage_current.get('full_coverage', False)} | - |",
        "",
        "## 记忆体与证据流",
        "",
        f"- recall_injections: {memory_current.get('recall_injections', 0)}",
        f"- writebacks: {memory_current.get('writebacks', 0)} ({memory.get('delta_writebacks', '0')})",
        f"- feedback_assimilations: {memory_current.get('feedback_assimilations', 0)} ({memory.get('delta_feedback_assimilations', '0')})",
        f"- evidence manifest entries: {evidence.get('manifest_entries', 0)}",
        f"- evidence missing refs: {evidence.get('manifest_missing_files', 0)}",
        "",
        "## 后续建议",
        "",
        "- 若 `full_coverage=false`，优先执行 `beacon auto-test create ... --matrix-path ...` 补齐证据。",
        "- 若 release 最近状态为 blocked，执行 `beacon workflow continue --auto` 续跑闭环。",
        "",
    ]
    return "\n".join(lines) + "\n"


@app.command()
def create(
    version: str = typer.Argument(..., help="Version number (e.g., v1.0.1 or auto)"),
    previous: Optional[str] = typer.Option(None, "--previous", help="Previous version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output markdown path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Create a version evolution summary document from real run/memory/evidence data."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version_guarded(
        project_root,
        version,
        command_name="beacon evolution-summary",
    )
    previous_version = (
        normalize_version(previous) if previous else _infer_previous_version(project_root, resolved_version)
    ) or "N/A"

    payload = _build_summary_payload(
        project_root=project_root,
        version=resolved_version,
        previous_version=previous_version,
    )
    markdown = _render_markdown(payload)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        write_json(output_path.with_suffix(".json"), payload)
        typer.echo(f"✓ Version evolution summary created: {output_path}")
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    output_path = project_root / "docs" / "beacon" / resolved_version / "SUMMARY.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    state_json = project_root / ".beacon" / "state" / "evolution-summary" / f"{resolved_version}.json"
    write_json(state_json, payload)

    typer.echo(f"✓ Version evolution summary created: {output_path}")
    typer.echo(f"✓ Evolution summary state created: {state_json}")
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("list")
def list_summaries(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all version evolution summaries."""
    project_root = Path(project) if project else Path.cwd()
    summaries: dict[str, Path] = {}
    root = project_root / "docs" / "beacon"
    if root.exists():
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
