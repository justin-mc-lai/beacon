"""Beacon init command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import resolve_target_version

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
    dry_run: bool,
    force: bool,
    with_claude: bool,
    with_agents: bool,
    with_context_guidance: bool,
) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    apply = not dry_run
    version = resolve_target_version(root, None)
    actions: list[dict[str, str]] = []

    docs_paths = [
        root / "docs" / "beacon" / version,
        root / "docs" / "beacon" / version / "prd",
        root / "docs" / "beacon" / version / "user-story",
        root / "docs" / "beacon" / version / "qa" / "test-cases",
        root / "docs" / "beacon" / version / "execution",
        root / "docs" / "product" / version,
        root / "docs" / "product" / version / "prd",
        root / "docs" / "product" / version / "user-story",
        root / "docs" / "product" / version / "qa" / "test-cases",
        root / "docs" / "product" / version / "execution",
    ]
    for p in docs_paths:
        if apply:
            p.mkdir(parents=True, exist_ok=True)
        actions.append({"scope": "docs", "action": "created" if apply else "planned", "path": str(p.relative_to(root))})

    if with_context_guidance and (with_claude or with_agents):
        from beacon.utils.context_files import setup_context_files

        context_setup = setup_context_files(
            project_root=root,
            runtime_version=version,
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

    payload = {
        "schema_version": "1.0",
        "command": "beacon init",
        "version": version,
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

    report_dir = root / "docs" / "beacon" / version / "execution"
    report_json = report_dir / "init-report.json"
    report_md = report_dir / "init-report.md"
    if apply:
        write_json(report_json, payload)
        report_md.write_text("# Beacon Init Report\n\n- status: completed\n", encoding="utf-8")
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
            dry_run=dry_run,
            force=force,
            with_claude=with_claude,
            with_agents=with_agents,
            with_context_guidance=with_context_guidance,
        )
        raise typer.Exit(code=code)


@app.command()
def run(
    project_root: Optional[str] = typer.Option("", "--project", "-p", help="Project root path"),
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
        dry_run=dry_run,
        force=force,
        with_claude=with_claude,
        with_agents=with_agents,
        with_context_guidance=with_context_guidance,
    )
    raise typer.Exit(code=code)


@app.command("init-project")
def init_project(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
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
        dry_run=dry_run,
        force=force,
        with_claude=with_claude,
        with_agents=with_agents,
        with_context_guidance=with_context_guidance,
    )
    raise typer.Exit(code=code)


if __name__ == "__main__":
    app()
