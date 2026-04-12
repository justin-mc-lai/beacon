"""Beacon doctor command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from beacon.utils.context_files import setup_context_files, verify_context_files
from beacon.utils.doctor_diagnostics import build_doctor_payload, build_doctor_advice_payload, collect_runtime_info
from beacon.utils.doctor_setup import install_launchers, resolve_bin_dir, uninstall_launchers
from beacon.utils.help_navigation import build_doctor_advise_payload
from beacon.utils.material_sync import sync_project_requirement_materials
from beacon.utils.material_audit import build_delivery_audit, build_material_audit
from beacon.utils.source_architecture import current_source_architecture_status
from beacon.utils.v115_delivery import repair_v115_delivery_package
from beacon.utils.version_package_upgrade import upgrade_version_package
from beacon.utils.versioning import describe_project_version_context, resolve_target_version
from beacon.utils.worktree_quiet import apply_quiet_worktree, quiet_worktree_status, restore_quiet_worktree

app = typer.Typer(
    name="doctor",
    help="Run environment diagnostics",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _print_doctor_report(payload: dict[str, Any]) -> None:
    typer.echo("Beacon Doctor - Environment Diagnostics")
    typer.echo("=" * 40)
    for item in payload.get("checks", []):
        status = str(item.get("status", "WARN")).upper()
        icon = "✓" if status == "PASS" else ("⚠" if status == "WARN" else "✗")
        typer.echo(f"{icon} {status}: {item.get('name')} ({item.get('detail')})")

    runtime = payload.get("runtime", {})
    typer.echo("\nRuntime")
    typer.echo("-" * 40)
    typer.echo(f"active_skill_path : {runtime.get('active_skill_path', '')}")
    typer.echo(f"cli_entry         : {runtime.get('cli_entry', '')}")
    typer.echo(f"package_version   : {runtime.get('package_version', '')}")
    typer.echo(f"toolkit_version   : {runtime.get('toolkit_version', '')}")
    typer.echo(f"skill_md_version  : {runtime.get('skill_md_version', '')}")
    typer.echo(f"version_consistent: {runtime.get('version_consistent', False)}")

    project = payload.get("project", {})
    typer.echo("\nProject Iteration")
    typer.echo("-" * 40)
    typer.echo(f"project_root      : {project.get('project_root', '')}")
    typer.echo(f"docs_version      : {project.get('active_docs_version', project.get('latest_iteration_version', ''))}")
    typer.echo(f"runtime_version   : {project.get('active_runtime_version', '')}")
    typer.echo(f"context_version   : {project.get('context_managed_version', '')}")
    typer.echo(f"docs_source       : {project.get('version_source', '')}")
    typer.echo(f"runtime_source    : {project.get('runtime_version_source', '')}")
    typer.echo(f"onboarding_docs   : {project.get('onboarding_docs_version', '')}")
    typer.echo(f"onboarding_runtime: {project.get('onboarding_runtime_version', '')}")
    typer.echo(f"available_versions: {project.get('available_versions', [])}")

    incompatibilities = payload.get("incompatibilities", [])
    typer.echo("\nCompatibility")
    typer.echo("-" * 40)
    if not incompatibilities:
        typer.echo("✓ PASS: no incompatibilities detected")
    else:
        for item in incompatibilities:
            typer.echo(
                f"⚠ {str(item.get('severity', 'medium')).upper()} "
                f"{item.get('code', '')}: {item.get('summary', '')}"
            )
    typer.echo(f"\nOverall: {payload.get('overall', 'WARN')}")


def _doctor_impl(json_output: bool, project_root: str, fix: bool, upgrade: bool, strict: bool) -> int:
    root = Path(project_root) if project_root else Path.cwd()

    if upgrade:
        typer.echo("Beacon doctor upgrade flow (compat mode)")
        typer.echo("Tip: use `beacon init --apply` after upgrade checks.")
        return 0

    if fix and root.exists():
        (root / ".beacon").mkdir(parents=True, exist_ok=True)
        (root / "docs").mkdir(parents=True, exist_ok=True)
        (root / "skills").mkdir(parents=True, exist_ok=True)
        runtime = collect_runtime_info()
        runtime_version = str(runtime.get("toolkit_version") or runtime.get("package_version") or "v1.0.0")
        setup_context_files(
            project_root=root,
            runtime_version=runtime_version,
            dry_run=False,
            force=False,
            with_claude=True,
            with_agents=True,
        )
        target_version = resolve_target_version(root, "latest-docs")
        upgrade_version_package(root, version=target_version, apply=True)

    payload = build_doctor_payload(root, strict=strict)

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_doctor_report(payload)

    return 2 if payload.get("overall") == "BLOCKED" else 0


def _resolve_launcher_source(launcher_source: str) -> Path:
    if launcher_source:
        return Path(launcher_source).expanduser().resolve()
    runtime = collect_runtime_info()
    candidate = Path(str(runtime.get("launcher_path", "")).strip())
    if candidate.exists():
        return candidate
    return (Path(__file__).resolve().parents[2] / "beacon-cli").resolve()


def _print_action_result(title: str, result: dict[str, Any]) -> None:
    typer.echo(title)
    typer.echo("=" * len(title))
    if result.get("error"):
        typer.echo(f"✗ {result['error']}")
    if result.get("installed") is not None:
        typer.echo(f"installed: {len(result.get('installed', []))}")
        for path in result.get("installed", []):
            typer.echo(f"  - {path}")
    if result.get("removed") is not None:
        typer.echo(f"removed: {len(result.get('removed', []))}")
        for path in result.get("removed", []):
            typer.echo(f"  - {path}")
    skipped = result.get("skipped", [])
    if skipped:
        typer.echo(f"skipped: {len(skipped)}")
        for path in skipped:
            typer.echo(f"  - {path}")
    for warning in result.get("warnings", []):
        typer.echo(f"⚠ {warning}")


def _print_advise_result(payload: dict[str, Any]) -> None:
    typer.echo("Beacon Doctor - Advice")
    typer.echo("=" * 24)
    typer.echo(f"feature         : {payload.get('feature') or 'N/A'}")
    typer.echo(f"docs_version    : {payload.get('docs_version') or payload.get('version') or 'N/A'}")
    typer.echo(f"runtime_version : {payload.get('runtime_version') or 'N/A'}")
    typer.echo(f"context_version : {payload.get('context_managed_version') or 'N/A'}")
    typer.echo(f"run_id          : {payload.get('run_id') or 'N/A'}")
    typer.echo(f"revision_id     : {payload.get('revision_id') or 'N/A'}")
    typer.echo(f"current_stage   : {payload.get('current_stage') or 'N/A'}")
    typer.echo(f"doc_status      : {payload.get('doc_status') or 'N/A'}")
    typer.echo(f"delivery_status : {payload.get('delivery_status') or 'N/A'}")
    typer.echo(f"blocked         : {bool(payload.get('blocked'))}")

    scores = payload.get('scores') if isinstance(payload.get('scores'), dict) else {}
    typer.echo("\nScores")
    typer.echo("-" * 24)
    for key in ("test_score", "closure_score", "readiness_score", "quality_score"):
        typer.echo(f"- {key}: {scores.get(key, 0)}")

    next_step = payload.get('next_step') if isinstance(payload.get('next_step'), dict) else {}
    typer.echo("\nRecommended Action")
    typer.echo("-" * 24)
    typer.echo(f"- action : {next_step.get('action', 'none')}")
    typer.echo(f"- why    : {next_step.get('reason', '')}")
    typer.echo(f"- command: {next_step.get('command', '')}")

    diagnosis = payload.get('diagnosis') if isinstance(payload.get('diagnosis'), list) else []
    typer.echo("\nDiagnosis")
    typer.echo("-" * 24)
    if diagnosis:
        for item in diagnosis:
            if not isinstance(item, dict):
                continue
            typer.echo(f"- {item.get('severity', 'medium')}: {item.get('code', '')} {item.get('summary', '')}")
    else:
        typer.echo("- none")

def _print_verification_result(title: str, result: dict[str, Any]) -> None:
    typer.echo(title)
    typer.echo("=" * len(title))
    for item in result.get("checks", []):
        status = str(item.get("status", "warn")).upper()
        typer.echo(f"- {status}: {item.get('name')} ({json.dumps(item.get('details', {}), ensure_ascii=False)})")
    typer.echo(f"Overall: {str(result.get('status', 'warn')).upper()}")


def _print_quiet_worktree_result(payload: dict[str, Any]) -> None:
    typer.echo("Beacon Doctor Quiet Worktree")
    typer.echo("=" * 28)
    typer.echo(f"mode                : {payload.get('mode', 'status')}")
    typer.echo(f"git_root            : {payload.get('git_root', '')}")
    typer.echo(f"exclude_path        : {payload.get('exclude_path', '')}")
    typer.echo(f"exclude_block       : {bool(payload.get('exclude_block_present'))}")
    typer.echo(f"tracked_candidates  : {payload.get('tracked_candidate_count', 0)}")
    typer.echo(f"skip_worktree_paths : {payload.get('skip_worktree_count', 0)}")

    skipped = payload.get("skip_worktree_paths", [])
    if skipped:
        typer.echo("\nActive skip-worktree")
        typer.echo("-" * 28)
        for path in skipped:
            typer.echo(f"- {path}")

    patterns = payload.get("exclude_patterns", [])
    if patterns:
        typer.echo("\nManaged exclude patterns")
        typer.echo("-" * 28)
        for pattern in patterns:
            typer.echo(f"- {pattern}")


def _single_check_payload(
    *,
    action: str,
    project_root: Path,
    version: str | None,
    strict: bool,
    check: dict[str, Any],
) -> dict[str, Any]:
    status = str(check.get("status", "warn")).lower()
    blocked = status == "fail" or (strict and status == "warn")
    version_context = describe_project_version_context(project_root, docs_version=version or None)
    return {
        "schema_version": "2.0",
        "action": action,
        "status": "BLOCKED" if blocked else status.upper(),
        "version_context": version_context,
        "version_semantics": version_context.get("version_semantics", {}),
        "result": {
            "schema_version": "1.0",
            "action": action,
            "project_root": str(project_root),
            "version": version or "",
            "strict": strict,
            "status": "fail" if blocked else status,
            "ok": not blocked,
            "checks": [check],
        },
    }


@app.callback(invoke_without_command=True)
def doctor_callback(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Auto-fix issues"),
    upgrade: bool = typer.Option(False, "--upgrade", "-u", help="Interactive upgrade"),
    strict: bool = typer.Option(False, "--strict", help="Treat high-severity incompatibilities as BLOCKED"),
):
    """Run diagnostics directly (PTK flat syntax compatibility)."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(
            code=_doctor_impl(
                json_output=json_output,
                project_root=project_root,
                fix=fix,
                upgrade=upgrade,
                strict=strict,
            )
        )


@app.command("diagnose")
def diagnose(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Auto-fix issues"),
    upgrade: bool = typer.Option(False, "--upgrade", "-u", help="Interactive upgrade"),
    strict: bool = typer.Option(False, "--strict", help="Treat high-severity incompatibilities as BLOCKED"),
):
    """Run Beacon diagnostics and health checks."""
    raise typer.Exit(
        code=_doctor_impl(
            json_output=json_output,
            project_root=project_root,
            fix=fix,
            upgrade=upgrade,
            strict=strict,
        )
    )


@app.command("setup")
def setup(
    bin_dir: str = typer.Option("", "--bin-dir", help="Install directory for launchers"),
    launcher_source: str = typer.Option("", "--launcher-source", help="Path to beacon-cli launcher source"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    force: bool = typer.Option(False, "--force", help="Overwrite unmanaged launchers"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Install `beacon` and `beacon-cli` launchers to system PATH directory."""
    resolved_bin_dir = resolve_bin_dir(bin_dir).resolve()
    source = _resolve_launcher_source(launcher_source)

    result = install_launchers(
        bin_dir=resolved_bin_dir,
        launcher_source=source,
        force=force,
        dry_run=dry_run,
    )
    status = "BLOCKED" if result.get("error") else "PASS"
    payload = {
        "schema_version": "2.0",
        "action": "setup",
        "status": status,
        "result": result,
    }

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_action_result("Beacon Doctor Setup", result)

    raise typer.Exit(2 if status == "BLOCKED" else 0)


@app.command("uninstall")
def uninstall(
    bin_dir: str = typer.Option("", "--bin-dir", help="Launcher directory to clean"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without deleting files"),
    force: bool = typer.Option(False, "--force", help="Remove unmanaged launchers too"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Uninstall launchers created by `beacon doctor setup`."""
    resolved_bin_dir = resolve_bin_dir(bin_dir).resolve()

    result = uninstall_launchers(
        bin_dir=resolved_bin_dir,
        force=force,
        dry_run=dry_run,
    )
    payload = {
        "schema_version": "2.0",
        "action": "uninstall",
        "status": "PASS",
        "result": result,
    }

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_action_result("Beacon Doctor Uninstall", result)

    raise typer.Exit(0)


@app.command("setup-context")
def setup_context(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    force: bool = typer.Option(False, "--force", help="Append managed blocks when markers are missing"),
    sync_materials: bool = typer.Option(False, "--sync-materials/--no-sync-materials", help="Sync machine requirement materials after context refresh."),
    feature: str = typer.Option("", "--feature", help="Sync only one feature when --sync-materials is enabled."),
    all_features: bool = typer.Option(True, "--all-features/--single-feature", help="When syncing materials, operate on all features in the target version."),
    overwrite_test_doc: bool = typer.Option(False, "--overwrite-test-doc", help="Allow sync to overwrite human QA markdown."),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    with_claude: bool = typer.Option(True, "--with-claude/--without-claude", help="Manage CLAUDE.md"),
    with_agents: bool = typer.Option(True, "--with-agents/--without-agents", help="Manage AGENTS.md"),
):
    """Create or refresh managed Beacon context blocks in CLAUDE.md/AGENTS.md."""
    root = Path(project_root) if project_root else Path.cwd()
    runtime = collect_runtime_info()
    runtime_version = str(runtime.get("toolkit_version") or runtime.get("package_version") or "v1.0.0")
    version_context = describe_project_version_context(root, runtime_version=runtime_version)
    result = setup_context_files(
        project_root=root,
        runtime_version=runtime_version,
        dry_run=dry_run,
        force=force,
        with_claude=with_claude,
        with_agents=with_agents,
    )
    material_sync = None
    if sync_materials:
        docs_version = str(version_context.get("docs_version") or "")
        if docs_version:
            material_sync = sync_project_requirement_materials(
                root,
                version=docs_version,
                feature=feature,
                all_features=all_features if not feature else False,
                dry_run=dry_run,
                overwrite_test_doc=overwrite_test_doc,
            )
    payload = {
        "schema_version": "2.0",
        "action": "setup-context",
        "status": "PASS",
        "docs_version": version_context.get("docs_version", ""),
        "runtime_version": runtime_version,
        "version_context": version_context,
        "version_semantics": version_context.get("version_semantics", {}),
        "result": result,
        "material_sync": material_sync,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Context Setup")
        typer.echo("=" * 27)
        typer.echo(f"docs_version: {payload.get('docs_version')}")
        typer.echo(f"runtime_version: {payload.get('runtime_version')}")
        for item in result.get("actions", []):
            typer.echo(f"- {item.get('file')}: {item.get('action')} ({item.get('merge_mode')})")
        if isinstance(material_sync, dict):
            typer.echo(f"- material_sync.features: {material_sync.get('feature_count', 0)}")
        typer.echo(f"Overall: {payload.get('status')}")

    raise typer.Exit(code=0)


@app.command("sync-materials")
def sync_materials(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    feature: str = typer.Option("", "--feature", help="Sync only one feature"),
    all_features: bool = typer.Option(True, "--all-features/--single-feature", help="Sync all features under the target version"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    overwrite_test_doc: bool = typer.Option(False, "--overwrite-test-doc", help="Allow overwriting human QA markdown"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Sync machine user-story and QA artifacts from current human requirement docs."""
    root = Path(project_root) if project_root else Path.cwd()
    result = sync_project_requirement_materials(
        root,
        version=version,
        feature=feature,
        all_features=all_features if not feature else False,
        dry_run=dry_run,
        overwrite_test_doc=overwrite_test_doc,
    )
    payload = {
        "schema_version": "2.0",
        "action": "sync-materials",
        "status": "PASS",
        "result": result,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Material Sync")
        typer.echo("=" * 27)
        typer.echo(f"version: {result.get('version')}")
        typer.echo(f"features: {result.get('feature_count')}")
        for item in result.get("results", []):
            typer.echo(f"- {item.get('feature')}: {item.get('status')}")
    raise typer.Exit(code=0)


@app.command("verify-context")
def verify_context(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify managed Beacon context blocks in CLAUDE.md/AGENTS.md."""
    root = Path(project_root) if project_root else Path.cwd()
    runtime = collect_runtime_info()
    runtime_version = str(runtime.get("toolkit_version") or runtime.get("package_version") or "v1.0.0")
    version_context = describe_project_version_context(root, runtime_version=runtime_version)
    result = verify_context_files(
        project_root=root,
        runtime_version=runtime_version,
        strict=strict,
    )
    status_map = {"pass": "PASS", "warn": "WARN", "fail": "BLOCKED"}
    payload = {
        "schema_version": "2.0",
        "action": "verify-context",
        "status": status_map.get(str(result.get("status", "warn")).lower(), "WARN"),
        "docs_version": version_context.get("docs_version", ""),
        "runtime_version": runtime_version,
        "version_context": version_context,
        "version_semantics": version_context.get("version_semantics", {}),
        "result": result,
    }
    if strict and payload["status"] == "WARN":
        payload["status"] = "BLOCKED"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Context Verify")
        typer.echo("=" * 28)
        typer.echo(f"docs_version: {payload.get('docs_version')}")
        typer.echo(f"runtime_version: {payload.get('runtime_version')}")
        for item in result.get("checks", []):
            item_status = status_map.get(str(item.get("status", "warn")).lower(), "WARN")
            typer.echo(
                f"- {item_status}: {item.get('name')} "
                f"({json.dumps(item.get('details', {}), ensure_ascii=False)})"
            )
        typer.echo(f"Overall: {payload.get('status')}")

    raise typer.Exit(code=2 if payload.get("status") == "BLOCKED" else 0)


@app.command("verify-materials")
def verify_materials(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify version material completeness for research/main-chain artifacts."""
    root = Path(project_root) if project_root else Path.cwd()
    result = build_material_audit(root, version=version or None, strict=strict)
    payload = {
        "schema_version": "2.0",
        "action": "verify-materials",
        "status": str(result.get("status", "warn")).upper(),
        "result": result,
    }
    if strict and payload["status"] == "WARN":
        payload["status"] = "BLOCKED"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Materials Verify", result)
    raise typer.Exit(code=2 if payload.get("status") in {"FAIL", "BLOCKED"} else 0)


@app.command("verify-delivery")
def verify_delivery(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify execution-layer delivery artifacts for a version."""
    root = Path(project_root) if project_root else Path.cwd()
    result = build_delivery_audit(root, version=version or None, strict=strict)
    payload = {
        "schema_version": "2.0",
        "action": "verify-delivery",
        "status": str(result.get("status", "warn")).upper(),
        "result": result,
    }
    if strict and payload["status"] == "WARN":
        payload["status"] = "BLOCKED"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Delivery Verify", result)
    raise typer.Exit(code=2 if payload.get("status") in {"FAIL", "BLOCKED"} else 0)


@app.command("repair-package")
def repair_package(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Repair a delivery package into the v1.1.5 human/machine layered layout."""
    root = Path(project_root) if project_root else Path.cwd()
    result = repair_v115_delivery_package(root, version=version, apply=not dry_run)
    payload = {
        "schema_version": "2.0",
        "action": "repair-package",
        "status": "PASS",
        "result": result,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_action_result("Beacon Doctor Repair Package", {"installed": [], "removed": [], "skipped": [], "warnings": []})
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    raise typer.Exit(code=0)


@app.command("upgrade-package")
def upgrade_package(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Cumulatively upgrade an older Beacon version package to newer runtime-compatible material structure."""
    root = Path(project_root) if project_root else Path.cwd()
    result = upgrade_version_package(root, version=version, apply=not dry_run)
    resolved_version = resolve_target_version(root, version)
    source_arch_status = current_source_architecture_status(root, version=resolved_version)
    payload = {
        "schema_version": "2.0",
        "action": "upgrade-package",
        "status": "PASS",
        "result": result,
        "source_architecture_status": source_arch_status,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_action_result("Beacon Doctor Upgrade Package", {"installed": [], "removed": [], "skipped": [], "warnings": []})
        summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
        if summary:
            typer.echo(
                "summary: "
                f"written={summary.get('written', 0)} "
                f"planned={summary.get('planned', 0)} "
                f"unchanged={summary.get('unchanged', 0)} "
                f"steps={summary.get('step_count', 0)}"
            )
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    raise typer.Exit(code=0)


@app.command("verify-config")
def verify_config(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify execution config/source metadata artifacts for a version."""
    root = Path(project_root) if project_root else Path.cwd()
    audit = build_delivery_audit(root, version=version or None, strict=strict)
    target_checks = [
        item
        for item in audit.get("checks", [])
        if str(item.get("name")) in {"execution_required_files_present", "execution_config_schema", "execution_source_schema"}
    ]
    worst = "pass"
    for item in target_checks:
        status = str(item.get("status", "pass")).lower()
        if status == "fail":
            worst = "fail"
            break
        if status == "warn":
            worst = "warn"
    merged_check = {
        "name": "verify_config",
        "status": worst,
        "details": {"checks": target_checks},
    }
    payload = _single_check_payload(
        action="verify-config",
        project_root=root,
        version=version or None,
        strict=strict,
        check=merged_check,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Config Verify", payload["result"])
    raise typer.Exit(code=2 if payload.get("status") == "BLOCKED" else 0)


@app.command("verify-git-alignment")
def verify_git_alignment(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify execution git-alignment artifact for a version."""
    root = Path(project_root) if project_root else Path.cwd()
    audit = build_delivery_audit(root, version=version or None, strict=strict)
    check = next(
        (item for item in audit.get("checks", []) if str(item.get("name")) == "execution_git_alignment_schema"),
        {"name": "execution_git_alignment_schema", "status": "fail", "details": {"missing": True}},
    )
    payload = _single_check_payload(
        action="verify-git-alignment",
        project_root=root,
        version=version or None,
        strict=strict,
        check=check,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Git Alignment Verify", payload["result"])
    raise typer.Exit(code=2 if payload.get("status") == "BLOCKED" else 0)


@app.command("setup-agent-md")
def setup_agent_md(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    force: bool = typer.Option(False, "--force", help="Append managed blocks when markers are missing"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Alias of setup-context focused on agent initialization markdown files."""
    setup_context(
        project_root=project_root,
        dry_run=dry_run,
        force=force,
        json_output=json_output,
        with_claude=True,
        with_agents=True,
    )


@app.command("verify-agent-md")
def verify_agent_md(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Alias of verify-context focused on agent initialization markdown files."""
    verify_context(
        project_root=project_root,
        strict=strict,
        json_output=json_output,
    )


@app.command("quiet-worktree")
def quiet_worktree(
    mode: str = typer.Argument("status", help="One of: status, apply, restore"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Manage local skip-worktree/exclude quieting for Beacon runtime churn."""
    root = Path(project_root) if project_root else Path.cwd()
    normalized = mode.strip().lower()
    actions = {
        "status": quiet_worktree_status,
        "apply": apply_quiet_worktree,
        "restore": restore_quiet_worktree,
    }
    action = actions.get(normalized)
    if action is None:
        raise typer.BadParameter("mode must be one of: status, apply, restore")

    try:
        result = action(root)
    except (ValueError, RuntimeError) as exc:
        payload = {
            "schema_version": "2.0",
            "action": "quiet-worktree",
            "status": "BLOCKED",
            "mode": normalized,
            "result": {
                "project_root": str(root.resolve()),
                "error": str(exc),
            },
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon Doctor Quiet Worktree\n{'=' * 28}\nerror: {exc}")
        raise typer.Exit(code=2)

    payload = {
        "schema_version": "2.0",
        "action": "quiet-worktree",
        "status": "PASS",
        "mode": normalized,
        "result": result,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_quiet_worktree_result(result)
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()


@app.command("advise")
def advise(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature filter"),
    run_id: str = typer.Option("", "--run-id", help="Run id filter"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Diagnose blockers and suggest the safest next action."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = build_doctor_advise_payload(
        root,
        version=version or None,
        feature=feature or None,
        run_id=run_id or None,
        strict=strict,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_advise_result(payload)
    raise typer.Exit(code=2 if payload.get("status") == "BLOCKED" else 0)
