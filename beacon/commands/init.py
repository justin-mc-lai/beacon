"""Beacon init command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.artifact_paths import (
    execution_file_output,
    human_execution_file,
    machine_execution_dir,
    machine_qa_dir,
    uses_machine_surface,
)
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.v115_delivery import ensure_eval_lab_skeleton, ensure_human_primary_indexes, refresh_evidence_manifest
from beacon.utils.versioning import describe_project_version_context, resolve_docs_version, resolve_runtime_version, runtime_capability_lines
from beacon.utils.global_boundaries import sync_project_global_boundaries

app = typer.Typer(
    name="init",
    help="Initialize Beacon project",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _write_if_apply(path: Path, content: str, apply: bool, force: bool = False) -> str:
    if path.exists() and not force:
        return "unchanged" if apply else "planned"
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return "created" if not force else "refreshed"
    return "planned"


def _init_impl(
    project_root: str,
    version: str,
    dry_run: bool,
    force: bool,
    project_mode: str,
    runtime_version: str,
    with_claude: bool,
    with_agents: bool,
    with_context_guidance: bool,
) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    apply = not dry_run
    docs_version = resolve_docs_version(root, version or None)
    effective_runtime_version = resolve_runtime_version(root, runtime_version)
    project_mode = str(project_mode or "greenfield").strip().lower()
    if project_mode not in {"greenfield", "takeover"}:
        typer.echo(json.dumps({"status": "failed", "reason_code": "invalid_project_mode", "project_mode": project_mode}, ensure_ascii=False, indent=2))
        return 2
    actions: list[dict[str, str]] = []

    docs_paths = [
        root / "docs" / "beacon" / docs_version,
        root / "docs" / "beacon" / docs_version / "prd",
        root / "docs" / "beacon" / docs_version / "user-story",
        root / "docs" / "beacon" / docs_version / "qa" / "test-cases",
        root / "docs" / "beacon" / docs_version / "release",
        root / "docs" / "beacon" / docs_version / "execution",
    ]
    if uses_machine_surface(docs_version, runtime_version=effective_runtime_version):
        docs_paths.extend(
            [
                machine_execution_dir(root, docs_version),
                machine_qa_dir(root, docs_version),
            ]
        )
    for p in docs_paths:
        if apply:
            p.mkdir(parents=True, exist_ok=True)
        actions.append({"scope": "docs", "action": "created" if apply else "planned", "path": str(p.relative_to(root))})

    global_boundaries_result = sync_project_global_boundaries(root, dry_run=dry_run)
    actions.append(
        {
            "scope": "docs",
            "action": str(global_boundaries_result.get("action", "updated")),
            "path": str(Path(str(global_boundaries_result.get("path", ""))).relative_to(root)) if str(global_boundaries_result.get("path", "")).startswith(str(root)) else str(global_boundaries_result.get("path", "")),
        }
    )

    if with_context_guidance and (with_claude or with_agents):
        from beacon.utils.context_files import setup_context_files

        context_setup = setup_context_files(
            project_root=root,
            runtime_version=effective_runtime_version,
            dry_run=dry_run,
            force=force,
            with_claude=with_claude,
            with_agents=with_agents,
        )
        for entry in context_setup.get("actions", []):
            action = dict(entry)
            action_name = str(action.pop("action", "updated"))
            path_value = str(action.pop("path", ""))
            file_name = str(action.get("file", ""))
            try:
                rel_path = str(Path(path_value).relative_to(root)) if path_value else ""
            except Exception:  # noqa: BLE001
                rel_path = path_value
            if apply and rel_path:
                file_path = root / rel_path
                if file_path.exists():
                    current = file_path.read_text(encoding="utf-8")
                    normalized = current.rstrip("\n") + "\n"
                    if normalized != current:
                        file_path.write_text(normalized, encoding="utf-8")
                        action_name = "updated" if action_name in {"unchanged", "created"} else action_name
            actions.append(
                {
                    "scope": "context",
                    "action": action_name,
                    "path": rel_path,
                    "context_setup": "true",
                    "target_file": file_name,
                    **{str(k): str(v) for k, v in action.items()},
                }
            )
    else:
        if with_claude:
            status = _write_if_apply(root / "CLAUDE.md", "# CLAUDE\n\n<!-- BEACON-MANAGED -->\n", apply, force=False)
            actions.append({"scope": "base", "action": status, "path": "CLAUDE.md"})
        if with_agents:
            status = _write_if_apply(root / "AGENTS.md", "# AGENTS\n\n<!-- BEACON-MANAGED -->\n", apply, force=False)
            actions.append({"scope": "base", "action": status, "path": "AGENTS.md"})

    if apply:
        (root / ".beacon").mkdir(parents=True, exist_ok=True)

    summary_path = root / "docs" / "beacon" / docs_version / "SUMMARY.md"
    summary_content = "# Beacon Summary\n\n- status: draft\n"
    summary_status = _write_if_apply(summary_path, summary_content, apply, force=False)
    actions.append({"scope": "docs", "action": summary_status, "path": str(summary_path.relative_to(root))})

    boundaries_path = root / "docs" / "beacon" / docs_version / "execution" / "boundaries.md"
    boundaries_content = "# Boundaries\n\n- status: draft\n"
    boundaries_status = _write_if_apply(boundaries_path, boundaries_content, apply, force=False)
    actions.append({"scope": "docs", "action": boundaries_status, "path": str(boundaries_path.relative_to(root))})

    architecture_path = root / "docs" / "beacon" / docs_version / "execution" / "architecture-blueprint.md"
    architecture_content = (
        "# Architecture Blueprint\n\n"
        f"- status: draft\n- project_mode: {project_mode}\n\n"
        "## Scope\n- system positioning\n- module/service map\n- data flow\n- boundaries\n"
    )
    architecture_status = _write_if_apply(architecture_path, architecture_content, apply, force=False)
    actions.append({"scope": "docs", "action": architecture_status, "path": str(architecture_path.relative_to(root))})
    if project_mode == "takeover":
        service_map_path = root / "docs" / "beacon" / docs_version / "execution" / "current-state-service-map.md"
        service_map_content = (
            "# Current-State Service Map\n\n"
            "- status: draft\n"
            "- capture existing service ownership, contracts, and dependencies before delivery changes.\n"
        )
        service_map_status = _write_if_apply(service_map_path, service_map_content, apply, force=False)
        actions.append({"scope": "docs", "action": service_map_status, "path": str(service_map_path.relative_to(root))})

        refactor_boundaries_path = root / "docs" / "beacon" / docs_version / "execution" / "refactor-boundaries.md"
        refactor_boundaries_content = (
            "# Refactor Boundaries\n\n"
            "- status: draft\n"
            "- record protected boundaries, risky modules, and allowed change slices for takeover work.\n"
        )
        refactor_boundaries_status = _write_if_apply(refactor_boundaries_path, refactor_boundaries_content, apply, force=False)
        actions.append({"scope": "docs", "action": refactor_boundaries_status, "path": str(refactor_boundaries_path.relative_to(root))})

    version_blueprint_path = root / "docs" / "beacon" / docs_version / "execution" / "version-evolution-blueprint.md"
    version_blueprint_content = (
        "# Version Evolution Blueprint\n\n"
        f"- status: draft\n- version: {docs_version}\n- runtime_version: {effective_runtime_version}\n- project_mode: {project_mode}\n\n"
        "## Capability Map\n- planned\n- implemented\n- deprecated\n"
    )
    version_blueprint_status = _write_if_apply(version_blueprint_path, version_blueprint_content, apply, force=False)
    actions.append({"scope": "docs", "action": version_blueprint_status, "path": str(version_blueprint_path.relative_to(root))})

    archive_index_path = root / "docs" / "beacon" / docs_version / "execution" / "implementation-archive-index.md"
    archive_index_content = (
        "# Implementation Archive Index\n\n"
        "- status: draft\n"
        "- technical implementation archives will be listed here by feature.\n"
    )
    archive_index_status = _write_if_apply(archive_index_path, archive_index_content, apply, force=False)
    actions.append({"scope": "docs", "action": archive_index_status, "path": str(archive_index_path.relative_to(root))})

    onboarding_doc_path = root / "docs" / "beacon" / docs_version / "execution" / "project-lifecycle-onboarding.md"
    onboarding_doc_content = (
        "# Project Lifecycle Onboarding\n\n"
        f"- docs_version: `{docs_version}`\n"
        f"- runtime_version: `{effective_runtime_version}`\n"
        f"- project_mode: `{project_mode}`\n"
        "- lifecycle_adoption_level: `2`\n"
        "- recommended reading order:\n"
        "  1. SUMMARY.md\n  2. execution/index.md\n  3. execution/architecture-blueprint.md\n"
        "  4. prd/ user-story/ qa/test-cases/\n  5. .machine/\n"
    )
    onboarding_doc_status = _write_if_apply(onboarding_doc_path, onboarding_doc_content, apply, force=False)
    actions.append({"scope": "docs", "action": onboarding_doc_status, "path": str(onboarding_doc_path.relative_to(root))})

    release_path = root / "docs" / "beacon" / docs_version / "release" / f"{docs_version}.md"
    release_content = f"# Release: {docs_version}\n"
    release_status = _write_if_apply(release_path, release_content, apply, force=False)
    actions.append({"scope": "docs", "action": release_status, "path": str(release_path.relative_to(root))})

    if uses_machine_surface(docs_version, runtime_version=effective_runtime_version):
        actions.extend(
            {
                "scope": "docs",
                "action": item["action"],
                "path": item["path"],
            }
            for item in ensure_human_primary_indexes(root, version=docs_version, apply=apply)
        )
        actions.extend(
            {
                "scope": "state",
                "action": item["action"],
                "path": item["path"],
            }
            for item in ensure_eval_lab_skeleton(root, apply=apply)
        )

    onboarding_state_path = root / ".beacon" / "state" / "project-onboarding.json"
    onboarding_state = {
        "schema_version": "1.0",
        "project_mode": project_mode,
        "lifecycle_adoption_level": 2,
        "docs_version": docs_version,
        "runtime_version": effective_runtime_version,
        "runtime_capability_lines": runtime_capability_lines(),
        "architecture_blueprint_ready": apply or architecture_path.exists(),
        "version_blueprint_ready": apply or version_blueprint_path.exists(),
        "implementation_archive_enabled": False,
        "qa_managed": False,
        "gate_managed": False,
        "takeover_baseline_status": "draft" if project_mode == "takeover" else "not_applicable",
        "takeover_baseline_frozen_at": "",
        "next_recommended_stage": "think" if project_mode == "greenfield" else "architecture-current-state",
        "updated_at": now_iso(),
    }
    if apply:
        write_json(onboarding_state_path, onboarding_state)
    actions.append({"scope": "state", "action": "created" if apply else "planned", "path": str(onboarding_state_path.relative_to(root))})

    version_context = describe_project_version_context(
        root,
        docs_version=docs_version,
        runtime_version=effective_runtime_version,
    )

    payload = {
        "schema_version": "1.0",
        "command": "beacon init",
        "docs_version": docs_version,
        "version": docs_version,
        "runtime_version": effective_runtime_version,
        "version_context": version_context,
        "version_semantics": version_context.get("version_semantics", {}),
        "project_mode": project_mode,
        "project_root": str(root),
        "dry_run": dry_run,
        "force": force,
        "with_context_guidance": with_context_guidance,
        "status": "completed",
        "started_at": now_iso(),
        "ended_at": now_iso(),
        "actions": actions,
        "conflicts": [],
    }

    report_json = execution_file_output(root, docs_version, "init-report.json")
    report_md = human_execution_file(root, docs_version, "init-report.md")
    if apply:
        write_json(report_json, payload)
        report_md.parent.mkdir(parents=True, exist_ok=True)
        report_md.write_text("# Beacon Init Report\n\n- status: completed\n", encoding="utf-8")
        refresh_evidence_manifest(
            root,
            refs=[
                str(report_json.relative_to(root)),
                str(report_md.relative_to(root)),
            ],
            version=docs_version,
        )
    payload["report_files"] = {
        "json": str(report_json.relative_to(root)),
        "markdown": str(report_md.relative_to(root)),
        "written": apply,
    }

    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


@app.callback(invoke_without_command=True)
def init_callback(
    ctx: typer.Context,
    project_root: Optional[str] = typer.Option("", "--project", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target project docs version (auto=project latest docs semver)"),
    runtime_version: str = typer.Option("auto", "--runtime-version", help="Beacon runtime version for managed context guidance (default: active toolkit version)"),
    project_mode: str = typer.Option("greenfield", "--project-mode", help="Project mode: greenfield|takeover"),
    dry_run: bool = typer.Option(False, "--dry-run/--apply", help="Preview or apply"),
    force: bool = typer.Option(False, "--force", help="Force append managed blocks"),
    with_claude: bool = typer.Option(True, "--with-claude/--without-claude", help="Manage CLAUDE.md"),
    with_agents: bool = typer.Option(True, "--with-agents/--without-agents", help="Manage AGENTS.md"),
    with_context_guidance: bool = typer.Option(
        True,
        "--with-context-guidance/--without-context-guidance",
        help="Manage context guidance blocks in CLAUDE.md/AGENTS.md",
    ),
):
    """Initialize project directly (PTK flat syntax compatibility)."""
    if ctx.invoked_subcommand is None:
        code = _init_impl(
            project_root=project_root or "",
            version=version,
            dry_run=dry_run,
            force=force,
            project_mode=project_mode,
            runtime_version=runtime_version,
            with_claude=with_claude,
            with_agents=with_agents,
            with_context_guidance=with_context_guidance,
        )
        raise typer.Exit(code=code)


@app.command()
def run(
    project_root: Optional[str] = typer.Option("", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target project docs version (auto=project latest docs semver)"),
    runtime_version: str = typer.Option("auto", "--runtime-version", help="Beacon runtime version for managed context guidance (default: active toolkit version)"),
    project_mode: str = typer.Option("greenfield", "--project-mode", help="Project mode: greenfield|takeover"),
    dry_run: bool = typer.Option(False, "--dry-run/--apply", help="Preview or apply"),
    force: bool = typer.Option(False, "--force", help="Force append managed blocks"),
    with_claude: bool = typer.Option(True, "--with-claude/--without-claude", help="Manage CLAUDE.md"),
    with_agents: bool = typer.Option(True, "--with-agents/--without-agents", help="Manage AGENTS.md"),
    with_context_guidance: bool = typer.Option(
        True,
        "--with-context-guidance/--without-context-guidance",
        help="Manage context guidance blocks in CLAUDE.md/AGENTS.md",
    ),
):
    """Initialize Beacon project structure."""
    code = _init_impl(
        project_root=project_root or "",
        version=version,
        dry_run=dry_run,
        force=force,
        project_mode=project_mode,
        runtime_version=runtime_version,
        with_claude=with_claude,
        with_agents=with_agents,
        with_context_guidance=with_context_guidance,
    )
    raise typer.Exit(code=code)


@app.command("init-project")
def init_project(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target project docs version (auto=project latest docs semver)"),
    runtime_version: str = typer.Option("auto", "--runtime-version", help="Beacon runtime version for managed context guidance (default: active toolkit version)"),
    project_mode: str = typer.Option("greenfield", "--project-mode", help="Project mode: greenfield|takeover"),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Preview or apply"),
    force: bool = typer.Option(False, "--force", help="Force append managed blocks"),
    with_claude: bool = typer.Option(True, "--with-claude/--without-claude", help="Manage CLAUDE.md"),
    with_agents: bool = typer.Option(True, "--with-agents/--without-agents", help="Manage AGENTS.md"),
    with_context_guidance: bool = typer.Option(
        True,
        "--with-context-guidance/--without-context-guidance",
        help="Manage context guidance blocks in CLAUDE.md/AGENTS.md",
    ),
):
    """Initialize Beacon project structure (alias)."""
    code = _init_impl(
        project_root=project_root,
        version=version,
        dry_run=dry_run,
        force=force,
        project_mode=project_mode,
        runtime_version=runtime_version,
        with_claude=with_claude,
        with_agents=with_agents,
        with_context_guidance=with_context_guidance,
    )
    raise typer.Exit(code=code)


if __name__ == "__main__":
    app()
