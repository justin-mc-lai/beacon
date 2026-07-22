"""Beacon doctor command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.branch_governance import render_branch_governance_markdown, resolve_branch_governance_view
from beacon.utils.doctor_orchestrator import (
    run_agent_surface_setup,
    run_agent_surface_verify,
    run_legacy_beacon_skills_cleanup,
    run_codex_hud_hook_setup,
    run_codex_hud_hook_verify,
    run_config_verify,
    run_context_setup,
    run_context_verify,
    run_delivery_verify,
    run_doctor_advise,
    run_doctor_diagnose,
    run_doctor_fix_flow,
    run_git_alignment_verify,
    run_gitignore_setup,
    run_gitignore_verify,
    run_launcher_setup,
    run_launcher_uninstall,
    run_materials_sync,
    run_materials_verify,
    run_package_repair,
    run_package_upgrade,
    run_quiet_worktree,
    run_requirement_clarity_sync,
    run_truth_integrity_verify,
    run_runtime_ledger_export,
    run_runtime_ledger_rebuild,
    run_runtime_ledger_verify,
    run_subagent_delegation_verify,
    run_subagent_runtime_verify,
    run_workflow_memory_sync,
    run_technical_review_contract_sync,
    run_test_contract_index_build,
    run_test_contract_index_verify,
    run_version_aggregate_projection_repair,
    run_version_surfaces_sync,
    run_version_surfaces_verify,
)
from beacon.utils.project_governance import (
    archive_version_contract,
    migrate_json_to_governance_md,
    prune_archived_contracts,
)
from beacon.utils.project_metadata import (
    create_or_update_project_metadata,
    delete_project_metadata,
    load_project_metadata,
    resolve_project_metadata_view,
    verify_project_metadata,
)

app = typer.Typer(
    name="doctor",
    help="Run environment diagnostics",
    invoke_without_command=True,
    no_args_is_help=False,
)
metadata_app = typer.Typer(name="metadata", help="Manage project topology and version metadata.")
branch_governance_app = typer.Typer(name="branch-governance", help="Inspect branch-governance contracts.")
app.add_typer(metadata_app, name="metadata")
app.add_typer(branch_governance_app, name="branch-governance")


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
        run_doctor_fix_flow(str(root))

    execution = run_doctor_diagnose(
        project_root=str(root),
        strict=strict,
    )
    payload = execution.payload

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_doctor_report(payload)

    return execution.exit_code


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
    projection = payload.get("support_surface_projection") if isinstance(payload.get("support_surface_projection"), dict) else {}
    typer.echo(f"operator_doc    : {projection.get('primary_operator_doc_ref') or 'N/A'}")
    release_research = payload.get("release_research") if isinstance(payload.get("release_research"), dict) else {}
    if release_research:
        typer.echo(
            f"release_research: present={bool(release_research.get('present'))} "
            f"sections={','.join(release_research.get('sections', [])) if isinstance(release_research.get('sections'), list) else ''} "
            f"count={release_research.get('section_count', 0)}"
        )

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


def _print_runtime_ledger_result(title: str, payload: dict[str, Any]) -> None:
    typer.echo(title)
    typer.echo("=" * len(title))
    typer.echo(f"status: {payload.get('status', '')}")
    if payload.get("project_root"):
        typer.echo(f"project_root: {payload.get('project_root')}")
    if payload.get("db_path"):
        typer.echo(f"db_path: {payload.get('db_path')}")
    if payload.get("envelope_path"):
        typer.echo(f"envelope_path: {payload.get('envelope_path')}")
    control_plane = payload.get("control_plane") if isinstance(payload.get("control_plane"), dict) else {}
    if control_plane:
        typer.echo(f"pocketbase_status: {control_plane.get('status', '')}")
        typer.echo(f"pocketbase_binary: {control_plane.get('binary_status', '')}")
        typer.echo(f"pocketbase_admin_ui: {control_plane.get('admin_ui', '')}")
    for item in payload.get("checks", []):
        typer.echo(f"- {str(item.get('status', 'warn')).upper()}: {item.get('name')} ({json.dumps(item.get('details', {}), ensure_ascii=False)})")


def _print_codex_hud_hook_setup_result(payload: dict[str, Any]) -> None:
    typer.echo("Beacon Doctor Codex HUD Hook Setup")
    typer.echo("=" * 34)
    typer.echo(f"mode            : {payload.get('mode', 'dry-run')}")
    typer.echo(f"plugin_root     : {payload.get('plugin_root', '')}")
    typer.echo(f"events          : {', '.join(payload.get('events', []))}")
    typer.echo(f"restart_required: {bool(payload.get('restart_required', False))}")
    typer.echo(f"diagnostics     : {payload.get('diagnostics_path', '')}")
    for item in payload.get("actions", []):
        typer.echo(f"- {item.get('action')}: {item.get('path')}")


def _print_codex_hud_hook_verify_result(payload: dict[str, Any]) -> None:
    typer.echo("Beacon Doctor Codex HUD Hook Verify")
    typer.echo("=" * 35)
    typer.echo(f"status       : {payload.get('status', 'blocked')}")
    typer.echo(f"plugin_root  : {payload.get('plugin_root', '')}")
    typer.echo(f"events       : {', '.join(payload.get('events', []))}")
    runtime = payload.get("runtime") if isinstance(payload.get("runtime"), dict) else {}
    if runtime:
        typer.echo(f"runtime      : {runtime.get('state', 'unknown')}")
        typer.echo(f"last_seen    : {runtime.get('last_activation', {}).get('generated_at', '') or 'N/A'}")
    typer.echo(f"diagnostics  : {payload.get('diagnostics_path', '')}")
    for item in payload.get("checks", []):
        if item.get("ok"):
            state = "PASS"
        elif item.get("required", True):
            state = "BLOCKED"
        else:
            state = "WARN"
        typer.echo(f"- {state}: {item.get('name')} ({item.get('detail')})")


def _print_agent_surface_result(title: str, payload: dict[str, Any]) -> None:
    typer.echo(title)
    typer.echo("=" * len(title))
    typer.echo(f"agent          : {payload.get('agent', '')}")
    typer.echo(f"surface_root   : {payload.get('surface_root', '')}")
    typer.echo(f"rules_path     : {payload.get('rules_path', '') or 'N/A'}")
    installed = payload.get("installed", [])
    typer.echo(f"installed      : {len(installed)}")
    for item in installed:
        if not isinstance(item, dict):
            continue
        typer.echo(f"- {item.get('id')}: {item.get('action')} ({item.get('path')})")
    removed = payload.get("removed", [])
    if removed:
        typer.echo(f"removed        : {len(removed)}")
        for item in removed:
            typer.echo(f"- {item}")
    skipped = payload.get("skipped", [])
    if skipped:
        typer.echo(f"skipped        : {len(skipped)}")
        for item in skipped:
            typer.echo(f"- {item.get('id')}: {item.get('reason')}")
    for warning in payload.get("warnings", []):
        typer.echo(f"⚠ {warning}")


def _print_agent_surface_verify_result(payload: dict[str, Any]) -> None:
    typer.echo("Beacon Doctor Agent Surface Verify")
    typer.echo("=" * 33)
    typer.echo(f"agent        : {payload.get('agent', '')}")
    typer.echo(f"surface_root : {payload.get('surface_root', '')}")
    for item in payload.get("checks", []):
        status = str(item.get("status", "warn")).upper()
        typer.echo(f"- {status}: {item.get('name')} ({json.dumps(item.get('details', {}), ensure_ascii=False)})")
    typer.echo(f"Overall: {str(payload.get('status', 'warn')).upper()}")


def _print_version_surface_sync_result(payload: dict[str, Any]) -> None:
    typer.echo("Beacon Doctor Version Surface Sync")
    typer.echo("=" * 34)
    typer.echo(f"manifest_path : {payload.get('manifest_path', '')}")
    manifest = payload.get("manifest") if isinstance(payload.get("manifest"), dict) else {}
    if manifest:
        typer.echo(f"package_version: {manifest.get('package_version', '')}")
        typer.echo(f"runtime_version: {manifest.get('runtime_version', '')}")
        typer.echo(f"docs_version   : {manifest.get('docs_default_line', '')}")
    for item in payload.get("surfaces", []):
        typer.echo(f"- {item.get('id')}: {item.get('action')} ({item.get('path')})")


def _print_version_surface_verify_result(payload: dict[str, Any]) -> None:
    typer.echo("Beacon Doctor Version Surface Verify")
    typer.echo("=" * 36)
    typer.echo(f"manifest_path : {payload.get('manifest_path', '')}")
    for item in payload.get("checks", []):
        status = str(item.get("status", "warn")).upper()
        typer.echo(f"- {status}: {item.get('name')} ({json.dumps(item.get('details', {}), ensure_ascii=False)})")
    typer.echo(f"Overall: {str(payload.get('status', 'warn')).upper()}")


def _print_project_metadata_result(title: str, result: dict[str, Any]) -> None:
    typer.echo(title)
    typer.echo("=" * len(title))
    typer.echo(f"project_root: {result.get('project_root', '')}")
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    if summary:
        typer.echo(f"transaction_id: {summary.get('transaction_id', '')}")
        typer.echo(f"machine_path: {summary.get('payload_abs_path', '')}")
        typer.echo(f"human_path: {summary.get('markdown_abs_path', '')}")
    resolved = result.get("resolved_metadata_view") if isinstance(result.get("resolved_metadata_view"), dict) else {}
    if resolved:
        typer.echo(f"topology_kind: {resolved.get('topology_kind', '')}")
        typer.echo(f"default_execution_service: {resolved.get('default_execution_service', '')}")
        typer.echo(f"selected_service: {resolved.get('selected_service', '')}")
        typer.echo(f"selected_branch: {resolved.get('selected_branch', '')}")


def _print_branch_governance_result(title: str, result: dict[str, Any]) -> None:
    typer.echo(title)
    typer.echo("=" * len(title))
    typer.echo(render_branch_governance_markdown(result).rstrip())


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


@metadata_app.command("show")
def metadata_show(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version-scoped resolved view"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Show current project-version metadata and resolved view."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = {
        "project_root": str(root),
        "payload": load_project_metadata(root),
        "resolved_metadata_view": resolve_project_metadata_view(root, version=version),
    }
    payload = {"schema_version": "1.0", "action": "doctor-metadata-show", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_project_metadata_result("Beacon Doctor Metadata Show", result)
    raise typer.Exit(code=0)


@metadata_app.command("list")
def metadata_list(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """List service bindings and version contracts."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    current = load_project_metadata(root)
    result = {
        "project_root": str(root),
        "service_bindings": current.get("global_project_metadata", {}).get("service_bindings", []),
        "version_scoped_metadata": current.get("version_scoped_metadata", {}),
    }
    payload = {"schema_version": "1.0", "action": "doctor-metadata-list", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    raise typer.Exit(code=0)


@metadata_app.command("create")
@metadata_app.command("update")
def metadata_upsert(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    topology_kind: str = typer.Option("", "--topology-kind", help="single_repo|monorepo"),
    default_execution_service: str = typer.Option("", "--default-execution-service", help="Default service key"),
    service_key: str = typer.Option("", "--service-key", help="Service key"),
    repo_root: str = typer.Option("", "--repo-root", help="Service repo root"),
    role: str = typer.Option("service", "--role", help="Service role"),
    writable: bool = typer.Option(True, "--writable/--reference-only", help="Writable or reference-only binding"),
    worktree_path_policy: str = typer.Option("follow-repo-root", "--worktree-path-policy", help="Worktree path policy"),
    version: str = typer.Option("", "--version", "-v", help="Version contract key"),
    branch: str = typer.Option("", "--branch", help="Canonical branch for the service under the version"),
    branch_guard_mode: str = typer.Option("strict", "--branch-guard-mode", help="Branch guard mode"),
    validation_state: str = typer.Option("active", "--validation-state", help="Validation state"),
    branch_governance_template: str = typer.Option("", "--branch-governance-template", help="Governance template name"),
    previous_version_baseline_branch: str = typer.Option("", "--previous-version-baseline-branch", help="Previous-version baseline branch"),
    next_version_feature_branch: str = typer.Option("", "--next-version-feature-branch", help="Next-version feature branch"),
    hotfix_branch_naming_rule: str = typer.Option("", "--hotfix-branch-naming-rule", help="Hotfix branch naming rule"),
    allow_worktree_when_feature_dirty: Optional[bool] = typer.Option(None, "--allow-worktree-when-feature-dirty/--disallow-worktree-when-feature-dirty", help="Whether worktree use is allowed when the feature lane is dirty"),
    merge_direction_policy: list[str] = typer.Option(None, "--merge-direction-policy", help="Allowed merge direction, repeatable"),
    forbidden_directions: list[str] = typer.Option(None, "--forbidden-direction", help="Forbidden direction, repeatable"),
    evidence_contract: list[str] = typer.Option(None, "--evidence-contract", help="Required evidence field, repeatable"),
    evidence_field: list[str] = typer.Option(None, "--evidence-field", help="Evidence value in key=value form, repeatable"),
    worktree_mode: str = typer.Option("", "--worktree-mode", help="branch-only|dedicated-worktree"),
    worktree_path: str = typer.Option("", "--worktree-path", help="Expected governed worktree path"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Create or update project-version metadata."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = create_or_update_project_metadata(
        root,
        topology_kind=topology_kind,
        default_execution_service=default_execution_service,
        service_key=service_key,
        repo_root=repo_root,
        role=role,
        writable=writable,
        worktree_path_policy=worktree_path_policy,
        version=version,
        branch=branch,
        branch_guard_mode=branch_guard_mode,
        validation_state=validation_state,
        branch_governance_template=branch_governance_template,
        previous_version_baseline_branch=previous_version_baseline_branch,
        next_version_feature_branch=next_version_feature_branch,
        hotfix_branch_naming_rule=hotfix_branch_naming_rule,
        allow_worktree_when_feature_dirty=allow_worktree_when_feature_dirty,
        merge_direction_policy=list(merge_direction_policy or []),
        forbidden_directions=list(forbidden_directions or []),
        evidence_contract=list(evidence_contract or []),
        evidence={
            key.strip(): value.strip()
            for item in (evidence_field or [])
            if "=" in str(item)
            for key, value in [str(item).split("=", 1)]
            if key.strip()
        },
        worktree_mode=worktree_mode,
        worktree_path=worktree_path,
        event_type="update",
    )
    payload = {"schema_version": "1.0", "action": "doctor-metadata-upsert", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        rendered = dict(result)
        rendered["resolved_metadata_view"] = resolve_project_metadata_view(root, version=version)
        _print_project_metadata_result("Beacon Doctor Metadata Upsert", rendered)
    raise typer.Exit(code=0)


@metadata_app.command("delete")
def metadata_delete(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    service_key: str = typer.Option("", "--service-key", help="Service key to delete"),
    version: str = typer.Option("", "--version", "-v", help="Version contract to delete"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Delete a service binding and/or version contract."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = delete_project_metadata(root, service_key=service_key, version=version)
    payload = {"schema_version": "1.0", "action": "doctor-metadata-delete", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        rendered = dict(result)
        rendered["resolved_metadata_view"] = resolve_project_metadata_view(root, version=version)
        _print_project_metadata_result("Beacon Doctor Metadata Delete", rendered)
    raise typer.Exit(code=0)


@metadata_app.command("migrate-to-governance-md")
def metadata_migrate_to_governance_md(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Import legacy project-version JSON into governance Markdown and remove governance JSON."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = migrate_json_to_governance_md(root)
    verify = verify_project_metadata(root)
    payload = {
        "schema_version": "1.0",
        "action": "doctor-metadata-migrate-to-governance-md",
        "result": result,
        "verify": verify,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Migrate status: {result.get('status')}")
        if result.get("summary"):
            typer.echo(json.dumps(result["summary"], ensure_ascii=False, indent=2))
        typer.echo(f"Verify status: {verify.get('status')}")
    exit_code = 0
    if result.get("status") == "fail" or verify.get("status") == "fail":
        exit_code = 2
    raise typer.Exit(code=exit_code)


@metadata_app.command("archive-version")
def metadata_archive_version(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option(..., "--version", "-v", help="Version contract to archive"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Mark a version contract as archived in governance Markdown."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = archive_version_contract(root, version=version)
    payload = {"schema_version": "1.0", "action": "doctor-metadata-archive-version", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Archive status: {result.get('status')}")
        if result.get("summary"):
            typer.echo(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    raise typer.Exit(code=0 if result.get("status") == "ok" else 2)


@metadata_app.command("prune-archived")
def metadata_prune_archived(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    apply: bool = typer.Option(False, "--apply", help="Remove archived version blocks from governance MD"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Remove archived version contract blocks from governance Markdown (dry-run by default)."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = prune_archived_contracts(root, dry_run=not apply)
    if apply and result.get("status") == "ok":
        verify = verify_project_metadata(root)
        result = {**result, "verify": verify}
    payload = {"schema_version": "1.0", "action": "doctor-metadata-prune-archived", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Prune status: {result.get('status')} dry_run={not apply}")
        if result.get("removed_versions"):
            typer.echo(f"Removed versions: {', '.join(result['removed_versions'])}")
        if result.get("verify"):
            typer.echo(f"Verify status: {result['verify'].get('status')}")
    exit_code = 0
    if result.get("status") != "ok":
        exit_code = 2
    elif apply and isinstance(result.get("verify"), dict) and result["verify"].get("status") == "fail":
        exit_code = 2
    raise typer.Exit(code=exit_code)


@metadata_app.command("verify")
def metadata_verify(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version contract to verify"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify current runtime state against project-version metadata contract."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = verify_project_metadata(root, version=version)
    payload = {"schema_version": "1.0", "action": "doctor-metadata-verify", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Metadata Verify", result)
    raise typer.Exit(code=0 if result.get("status") != "fail" else 2)


@branch_governance_app.command("show")
def branch_governance_show(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version contract key"),
    feature: str = typer.Option("", "--feature", help="Optional feature name"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Show the resolved branch-governance human surface."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    view = resolve_project_metadata_view(root, version=version)
    result = (
        resolve_branch_governance_view(project_root=root, version=version, feature=feature, metadata_view=view)
        if feature
        else view.get("branch_governance")
        if isinstance(view.get("branch_governance"), dict)
        else {}
    )
    payload = {"schema_version": "1.0", "action": "doctor-branch-governance-show", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_branch_governance_result("Beacon Doctor Branch Governance Show", result)
    raise typer.Exit(code=0)


@branch_governance_app.command("verify")
def branch_governance_verify(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version contract key"),
    feature: str = typer.Option("", "--feature", help="Optional feature name"),
    strict: bool = typer.Option(False, "--strict", help="Treat branch/worktree mismatches as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify the resolved branch-governance contract."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    view = resolve_project_metadata_view(root, version=version)
    result = (
        resolve_branch_governance_view(project_root=root, version=version, feature=feature, metadata_view=view)
        if feature
        else view.get("branch_governance")
        if isinstance(view.get("branch_governance"), dict)
        else {}
    )
    if strict and isinstance(result, dict):
        from beacon.utils.branch_governance import evaluate_branch_governance

        result = evaluate_branch_governance(result, strict=True)
    payload = {"schema_version": "1.0", "action": "doctor-branch-governance-verify", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_branch_governance_result("Beacon Doctor Branch Governance Verify", result)
    raise typer.Exit(code=0 if not result.get("blocked") else 2)


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


@app.command("loop-audit")
def loop_audit(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Beacon version"),
    strict: bool = typer.Option(False, "--strict", help="Block when score is below threshold"),
    threshold: int = typer.Option(80, "--threshold", help="Minimum score for strict pass"),
    suggest: bool = typer.Option(True, "--suggest/--no-suggest", help="Include ordered repair suggestions"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Aggregate loop-readiness signals into one advisory score."""
    from beacon.utils.loop_readiness import build_loop_readiness_audit
    from beacon.utils.versioning import resolve_target_version

    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    payload = build_loop_readiness_audit(
        root,
        version=resolved_version,
        strict=strict,
        threshold=threshold,
        suggest=suggest,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Loop Audit")
        typer.echo(f"status: {payload.get('status')}")
        typer.echo(f"score: {payload.get('score')} level={payload.get('level')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
        for signal in payload.get("signals", []):
            if isinstance(signal, dict):
                typer.echo(f"- {signal.get('id')}: {signal.get('status')} ({signal.get('reason_code', '')})")
    raise typer.Exit(code=2 if payload.get("blocked") else 0)


@app.command("setup")
def setup(
    bin_dir: str = typer.Option("", "--bin-dir", help="Install directory for launchers"),
    launcher_source: str = typer.Option("", "--launcher-source", help="Path to beacon-cli launcher source"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    force: bool = typer.Option(False, "--force", help="Overwrite unmanaged launchers"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Install `beacon` and `beacon-cli` launchers to system PATH directory."""
    execution = run_launcher_setup(
        bin_dir=bin_dir,
        launcher_source=launcher_source,
        force=force,
        dry_run=dry_run,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_action_result("Beacon Doctor Setup", result)

    raise typer.Exit(execution.exit_code)


@app.command("uninstall")
def uninstall(
    bin_dir: str = typer.Option("", "--bin-dir", help="Launcher directory to clean"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without deleting files"),
    force: bool = typer.Option(False, "--force", help="Remove unmanaged launchers too"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Uninstall launchers created by `beacon doctor setup`."""
    execution = run_launcher_uninstall(
        bin_dir=bin_dir,
        force=force,
        dry_run=dry_run,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_action_result("Beacon Doctor Uninstall", result)

    raise typer.Exit(execution.exit_code)


@app.command("setup-context")
def setup_context(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version to anchor into managed context"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    force: bool = typer.Option(False, "--force", help="Append managed blocks when markers are missing"),
    sync_materials: bool = typer.Option(False, "--sync-materials/--no-sync-materials", help="Sync machine requirement materials after context refresh."),
    feature: str = typer.Option("", "--feature", help="Sync only one feature when --sync-materials is enabled."),
    all_features: bool = typer.Option(True, "--all-features/--single-feature", help="When syncing materials, operate on all features in the target version."),
    overwrite_test_doc: bool = typer.Option(False, "--overwrite-test-doc", help="Allow sync to overwrite human QA markdown."),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    with_claude: bool = typer.Option(True, "--with-claude/--without-claude", help="Manage CLAUDE.md"),
    with_agents: bool = typer.Option(True, "--with-agents/--without-agents", help="Manage AGENTS.md"),
    with_gitignore: bool = typer.Option(True, "--with-gitignore/--without-gitignore", help="Manage Beacon standard .gitignore block"),
):
    """Create or refresh managed Beacon context blocks in CLAUDE.md/AGENTS.md."""
    execution = run_context_setup(
        project_root=project_root,
        version=version,
        dry_run=dry_run,
        force=force,
        sync_materials=sync_materials,
        feature=feature,
        all_features=all_features,
        overwrite_test_doc=overwrite_test_doc,
        with_claude=with_claude,
        with_agents=with_agents,
        with_gitignore=with_gitignore,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    material_sync = payload.get("material_sync") if isinstance(payload.get("material_sync"), dict) else None
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

    raise typer.Exit(code=execution.exit_code)


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
    execution = run_materials_sync(
        project_root=project_root,
        version=version,
        feature=feature,
        all_features=all_features,
        dry_run=dry_run,
        overwrite_test_doc=overwrite_test_doc,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Material Sync")
        typer.echo("=" * 27)
        typer.echo(f"version: {result.get('version')}")
        typer.echo(f"features: {result.get('feature_count')}")
        for item in result.get("results", []):
            typer.echo(f"- {item.get('feature')}: {item.get('status')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("sync-requirement-clarity")
def sync_requirement_clarity(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Materialize requirement clarity report and state before freeze."""
    execution = run_requirement_clarity_sync(
        project_root=project_root,
        version=version,
        feature=feature,
    )
    output = execution.payload
    result = output.get("result", {}) if isinstance(output.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        gate = result.get("gate", {}) if isinstance(result.get("gate"), dict) else {}
        report = result.get("report", {}) if isinstance(result.get("report"), dict) else {}
        writeback = result.get("writeback", {}) if isinstance(result.get("writeback"), dict) else {}
        typer.echo("Beacon Doctor Requirement Clarity")
        typer.echo("=" * 33)
        typer.echo(f"feature: {feature}")
        typer.echo(f"status: {gate.get('status', '')}")
        typer.echo(f"blocked: {gate.get('blocked', False)}")
        typer.echo(f"json: {report.get('json', '')}")
        typer.echo(f"markdown: {report.get('markdown', '')}")
        typer.echo(f"state: {writeback.get('state_path', '')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-truth-integrity")
def verify_truth_integrity(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    mode: str = typer.Option("audit", "--mode", help="Gate mode: audit or block"),
    strict: bool = typer.Option(False, "--strict", help="Treat audit findings as blocking"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify feature package truth integrity (TIG) before freeze or for audit."""
    execution = run_truth_integrity_verify(
        project_root=project_root,
        version=version,
        feature=feature,
        mode=mode,
        strict=strict,
    )
    output = execution.payload
    result = output.get("result", {}) if isinstance(output.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Truth Integrity")
        typer.echo("=" * 30)
        typer.echo(f"feature: {feature}")
        typer.echo(f"status: {result.get('status', '')}")
        typer.echo(f"blocked: {result.get('blocked', False)}")
        typer.echo(f"finding_count: {result.get('finding_count', 0)}")
        typer.echo(f"reason_code: {result.get('reason_code', '')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-truth-quality")
def verify_truth_quality(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    mode: str = typer.Option("audit", "--mode", help="Gate mode: audit or block"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify truth determinism quality (TIG-DC): placeholder words and hollow templates."""
    from beacon.utils.truth_integrity import build_truth_integrity_gate

    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    gate = build_truth_integrity_gate(root, version=version, feature=feature, mode=mode)
    dc_findings = [
        f for f in gate.get("findings", [])
        if isinstance(f, dict)
        and str(f.get("reason_code", "")) in {
            "TRUTH_DETERMINISM_PLACEHOLDER",
            "TRUTH_DETERMINISM_HOLLOW_TEMPLATE",
        }
    ]
    determinism = gate.get("determinism_check", {})
    result = {
        "feature": feature,
        "version": gate.get("version", version),
        "mode": mode,
        "status": gate.get("status", ""),
        "blocked": gate.get("blocked", False),
        "placeholder_count": determinism.get("placeholder_count", 0),
        "hollow_template_count": determinism.get("hollow_template_count", 0),
        "findings": dc_findings,
        "finding_count": len(dc_findings),
    }
    payload = {"schema_version": "1.0", "action": "doctor-verify-truth-quality", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Truth Quality (TIG-DC)")
        typer.echo("=" * 37)
        typer.echo(f"feature: {feature}")
        typer.echo(f"status: {result['status']}")
        typer.echo(f"blocked: {result['blocked']}")
        typer.echo(f"placeholder_count: {result['placeholder_count']}")
        typer.echo(f"hollow_template_count: {result['hollow_template_count']}")
        if dc_findings:
            typer.echo("\nFindings")
            typer.echo("-" * 37)
            for f in dc_findings:
                kind = str(f.get("kind", ""))
                line = int(f.get("line", 0))
                text = str(f.get("text", "")).strip()
                typer.echo(f"- {kind} (L{line}): {text[:80]}")
    exit_code = 2 if result["blocked"] else 0
    raise typer.Exit(code=exit_code)


@app.command("sync-technical-review-contract")
def sync_technical_review_contract(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    revision_id: str = typer.Option("", "--revision-id", help="Revision id to stamp into the draft contract"),
    review_status: str = typer.Option("draft", "--review-status", help="Contract status: draft/approved/accepted"),
    approved_by: str = typer.Option("", "--approved-by", help="Reviewer/approver id or name"),
    reviewed_at: str = typer.Option("", "--reviewed-at", help="Reviewed timestamp"),
    force_refresh: bool = typer.Option(False, "--force-refresh", help="Regenerate the draft contract from current seed/config"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Materialize a draft deterministic implementation contract for human technical review."""
    execution = run_technical_review_contract_sync(
        project_root=project_root,
        version=version,
        feature=feature,
        revision_id=revision_id,
        review_status=review_status,
        approved_by=approved_by,
        reviewed_at=reviewed_at,
        force_refresh=force_refresh,
    )
    output = execution.payload
    result = output.get("result", {}) if isinstance(output.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Technical Review Contract")
        typer.echo("=" * 39)
        typer.echo(f"feature: {feature}")
        typer.echo(f"version: {result['version']}")
        typer.echo(f"review_status: {result['review_status']}")
        typer.echo(f"json: {result['contract_json_path']}")
        typer.echo(f"markdown: {result['contract_markdown_path']}")
        typer.echo(f"state: {result['state_path']}")
    raise typer.Exit(code=execution.exit_code)


@app.command("build-test-contract-index")
def build_test_contract_index(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Build the machine-readable Test Contract Index from frozen requirement truth."""
    execution = run_test_contract_index_build(
        project_root=project_root,
        version=version,
        feature=feature,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Test Contract Index")
        typer.echo("=" * 33)
        typer.echo(f"feature: {feature}")
        typer.echo(f"version: {result.get('version', version)}")
        typer.echo(f"status: {result.get('status', '')}")
        typer.echo(f"index: {result.get('index_path', '')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-test-contract-index")
def verify_test_contract_index(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify Test Contract Index freshness, lane coverage, and release-facing safety."""
    execution = run_test_contract_index_verify(
        project_root=project_root,
        version=version,
        feature=feature,
        strict=strict,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    gate = result.get("gate", {}) if isinstance(result.get("gate"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Test Contract Verify")
        typer.echo("=" * 35)
        typer.echo(f"feature: {feature}")
        typer.echo(f"version: {result.get('version', version)}")
        typer.echo(f"status: {gate.get('status', '')}")
        typer.echo(f"reason_codes: {gate.get('reason_codes', [])}")
        typer.echo(f"index: {gate.get('index_path', '')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("repair-version-aggregate-projection")
def repair_version_aggregate_projection(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    overwrite_feature_projection: bool = typer.Option(False, "--overwrite-feature-projection", help="Overwrite existing feature projection"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Repair release-facing projection/read-model artifacts without changing requirement truth."""
    execution = run_version_aggregate_projection_repair(
        project_root=project_root,
        version=version,
        feature=feature,
        overwrite_feature_projection=overwrite_feature_projection,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    aggregate = (
        result.get("version_aggregate_projection")
        if isinstance(result.get("version_aggregate_projection"), dict)
        else {}
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Version Aggregate Projection Repair")
        typer.echo("=" * 50)
        typer.echo(f"feature: {feature}")
        typer.echo(f"version: {result.get('version', version)}")
        typer.echo(f"status: {payload.get('status', '')}")
        typer.echo(f"feature_projection: {result.get('feature_projection', {}).get('json_path', '')}")
        typer.echo(f"version_projection: {aggregate.get('json_path', '')}")
        typer.echo(f"feature_count: {aggregate.get('feature_count', 0)}")
        typer.echo("truth_authority: false")
        typer.echo("lifecycle_stage: false")
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-subagent-runtime")
def verify_subagent_runtime(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    host_runtime: str = typer.Option("unknown", "--host-runtime", help="Host runtime: codex|claude"),
    require_agents: bool = typer.Option(
        False, "--require-agents", help="Also require curated minimal pack under .codex/agents or .claude/agents"
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify host-native subagent runtime readiness for Codex/Claude skill execution."""
    from pathlib import Path as _Path

    from beacon.utils.host_subagent_pack import verify_subagent_agents

    execution = run_subagent_runtime_verify(
        project_root=project_root,
        host_runtime=host_runtime,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    exit_code = execution.exit_code
    if require_agents:
        root = _Path(project_root).expanduser().resolve() if project_root else _Path.cwd()
        host = str(result.get("host_runtime") or host_runtime or "codex")
        if host == "unknown":
            host = "codex"
        agents = verify_subagent_agents(root, host_runtime=host, require_pack=True)
        result = dict(result)
        result["agents_pack"] = agents
        for item in agents.get("checks") or []:
            result.setdefault("checks", []).append(item)
        if agents.get("status") != "pass":
            result["status"] = "fail"
            result["reason_code"] = agents.get("reason_code") or "pack_roles_missing"
            if agents.get("recommended_command"):
                result["recommended_command"] = agents["recommended_command"]
            payload["status"] = "BLOCKED"
            exit_code = 2
        payload["result"] = result
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Subagent Runtime")
        typer.echo("=" * 31)
        typer.echo(f"host_runtime: {result.get('host_runtime', '')}")
        typer.echo(f"status: {result.get('status', '')}")
        for item in result.get("checks", []):
            typer.echo(f"- {item.get('name')}: {item.get('ok')} ({item.get('detail')})")
        if result.get("recommended_command"):
            typer.echo(f"recommended_command: {result.get('recommended_command')}")
    raise typer.Exit(code=exit_code)


@app.command("install-subagent-pack")
def install_subagent_pack_cmd(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    host_runtime: str = typer.Option("codex", "--host-runtime", help="Host runtime: codex|claude"),
    pack: str = typer.Option("minimal", "--pack", help="Pack id: minimal | plan-review"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Install curated host subagent pack (minimal=6 or plan-review=10) into .codex/agents or .claude/agents."""
    from pathlib import Path as _Path

    from beacon.utils.host_subagent_pack import install_subagent_pack

    root = _Path(project_root).expanduser().resolve() if project_root else _Path.cwd()
    result = install_subagent_pack(root, host_runtime=host_runtime, pack=pack)
    payload = {
        "schema_version": "2.0",
        "action": "install-subagent-pack",
        "status": "PASS" if result.get("status") == "ok" else "BLOCKED",
        "result": result,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Install Subagent Pack")
        typer.echo("=" * 36)
        typer.echo(f"status: {payload['status']}")
        typer.echo(f"host_runtime: {result.get('host_runtime')}")
        typer.echo(f"roles: {result.get('roles')}")
        for path in result.get("written") or []:
            typer.echo(f"- wrote {path}")
    raise typer.Exit(code=0 if payload["status"] == "PASS" else 2)


@app.command("verify-subagent-delegation")
def verify_subagent_delegation(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify feature-level delegation readiness before host-native team subagent use."""
    execution = run_subagent_delegation_verify(
        project_root=project_root,
        version=version,
        feature=feature,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Subagent Delegation")
        typer.echo("=" * 34)
        typer.echo(f"feature: {feature}")
        typer.echo(f"version: {result.get('version', '')}")
        typer.echo(f"status: {result.get('status', '')}")
        for item in result.get("checks", []):
            typer.echo(f"- {item.get('name')}: {item.get('ok')} ({item.get('detail')})")
        if result.get("recommended_command"):
            typer.echo(f"recommended_command: {result.get('recommended_command')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-runtime-ledger")
def verify_runtime_ledger(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    feature: str = typer.Option("", "--feature", help="Feature name"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify runtime-ledger determinism and PocketBase control-plane readiness."""
    execution = run_runtime_ledger_verify(
        project_root=project_root,
        version=version,
        feature=feature,
        strict=strict,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_runtime_ledger_result("Beacon Doctor Runtime Ledger Verify", result)
        typer.echo(f"Overall: {payload.get('status')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("export-runtime-ledger")
def export_runtime_ledger(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    label: str = typer.Option("", "--label", help="Optional export label"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Export runtime-ledger SQLite, projection envelopes, and PocketBase scaffold."""
    execution = run_runtime_ledger_export(
        project_root=project_root,
        label=label,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Runtime Ledger Export")
        typer.echo("=" * 35)
        typer.echo(f"export_root: {result.get('export_root', '')}")
        copied = result.get("copied", {}) if isinstance(result.get("copied"), dict) else {}
        for key, value in copied.items():
            typer.echo(f"- {key}: {value}")
    raise typer.Exit(code=execution.exit_code)


@app.command("rebuild-runtime-ledger")
def rebuild_runtime_ledger(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    feature: str = typer.Option("", "--feature", help="Feature name"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Rebuild runtime-ledger projection from local Beacon truth."""
    execution = run_runtime_ledger_rebuild(
        project_root=project_root,
        version=version,
        feature=feature,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    sync_payload = result.get("sync", {}) if isinstance(result.get("sync"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Runtime Ledger Rebuild")
        typer.echo("=" * 36)
        typer.echo(f"project_root: {result.get('project_root', '')}")
        typer.echo(f"status: {result.get('status', '')}")
        typer.echo(f"docs_version: {result.get('docs_version', '')}")
        typer.echo(f"project_key: {result.get('project_key', '')}")
        typer.echo(f"envelope_path: {result.get('envelope_path', '')}")
        typer.echo(f"sqlite_status: {sync_payload.get('sqlite_status', '')}")
        typer.echo(f"pocketbase_status: {sync_payload.get('pocketbase_status', '')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-context")
def verify_context(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    with_gitignore: bool = typer.Option(True, "--with-gitignore/--without-gitignore", help="Verify Beacon standard .gitignore block"),
):
    """Verify managed Beacon context blocks in CLAUDE.md/AGENTS.md."""
    execution = run_context_verify(
        project_root=project_root,
        strict=strict,
        with_gitignore=with_gitignore,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    status_map = {"pass": "PASS", "warn": "WARN", "fail": "BLOCKED"}
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

    raise typer.Exit(code=execution.exit_code)


@app.command("verify-materials")
def verify_materials(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify version material completeness for research/main-chain artifacts."""
    execution = run_materials_verify(
        project_root=project_root,
        version=version,
        strict=strict,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Materials Verify", result)
    raise typer.Exit(code=execution.exit_code)


@app.command("sync-gitignore")
def sync_gitignore(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Create or refresh the Beacon-managed .gitignore block."""
    execution = run_gitignore_setup(
        project_root=project_root,
        dry_run=dry_run,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Gitignore Sync")
        typer.echo("=" * 28)
        typer.echo(f"runtime_version: {payload.get('runtime_version')}")
        typer.echo(f"path: {result.get('path', '')}")
        typer.echo(f"action: {result.get('action', '')}")
        typer.echo(f"merge_mode: {result.get('merge_mode', '')}")
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-gitignore")
def verify_gitignore(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify the Beacon-managed .gitignore block."""
    execution = run_gitignore_verify(
        project_root=project_root,
        strict=strict,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Gitignore Verify", payload["result"])
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-delivery")
def verify_delivery(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify execution-layer delivery artifacts for a version."""
    execution = run_delivery_verify(
        project_root=project_root,
        version=version,
        strict=strict,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Delivery Verify", result)
    raise typer.Exit(code=execution.exit_code)


@app.command("repair-package")
def repair_package(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Repair a delivery package into the v1.1.5 human/machine layered layout."""
    execution = run_package_repair(
        project_root=project_root,
        version=version,
        dry_run=dry_run,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_action_result("Beacon Doctor Repair Package", {"installed": [], "removed": [], "skipped": [], "warnings": []})
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    raise typer.Exit(code=execution.exit_code)


@app.command("sync-workflow-memory")
def sync_workflow_memory(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    feature: str = typer.Option("", "--feature", help="Feature name"),
    run_id: str = typer.Option("", "--run-id", help="Workflow run id"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Backfill workflow-memory surfaces for an already-completed feature run."""
    execution = run_workflow_memory_sync(
        project_root=project_root,
        version=version,
        feature=feature,
        run_id=run_id,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_action_result("Beacon Doctor Sync Workflow Memory", {"installed": [], "removed": [], "skipped": [], "warnings": []})
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    raise typer.Exit(code=execution.exit_code)


@app.command("upgrade-package")
def upgrade_package(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("latest-docs", "--version", "-v", help="Target docs version"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Cumulatively upgrade an older Beacon version package to newer runtime-compatible material structure."""
    execution = run_package_upgrade(
        project_root=project_root,
        version=version,
        dry_run=dry_run,
    )
    payload = execution.payload
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
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
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-config")
def verify_config(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify execution config/source metadata artifacts for a version."""
    execution = run_config_verify(
        project_root=project_root,
        version=version,
        strict=strict,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Config Verify", payload["result"])
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-git-alignment")
def verify_git_alignment(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify execution git-alignment artifact for a version."""
    execution = run_git_alignment_verify(
        project_root=project_root,
        version=version,
        strict=strict,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_verification_result("Beacon Doctor Git Alignment Verify", payload["result"])
    raise typer.Exit(code=execution.exit_code)


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
        sync_materials=False,
        feature="",
        all_features=True,
        overwrite_test_doc=False,
        json_output=json_output,
        with_claude=True,
        with_agents=True,
        with_gitignore=True,
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
        with_gitignore=True,
    )


@app.command("quiet-worktree")
def quiet_worktree(
    mode: str = typer.Argument("status", help="One of: status, apply, restore"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Manage local skip-worktree/exclude quieting for Beacon runtime churn."""
    execution = run_quiet_worktree(
        project_root=project_root,
        mode=mode,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload.get("status") == "BLOCKED":
            typer.echo(f"Beacon Doctor Quiet Worktree\n{'=' * 28}\nerror: {payload.get('result', {}).get('error', '')}")
        else:
            _print_quiet_worktree_result(payload.get("result", {}))
    raise typer.Exit(code=execution.exit_code)


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
    execution = run_doctor_advise(
        project_root=project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        strict=strict,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_advise_result(payload)
    raise typer.Exit(code=execution.exit_code)


@app.command("setup-codex-hud-hook")
def setup_codex_hud_hook_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target docs version"),
    events: str = typer.Option(
        ",".join(("UserPromptSubmit", "SessionStart", "SessionResume", "SessionRefresh")),
        "--events",
        help="Comma-separated hook event names",
    ),
    apply: bool = typer.Option(False, "--apply", help="Write hook wiring into ~/.codex"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Generate or apply Codex fixed HUD hook wiring."""
    execution = run_codex_hud_hook_setup(
        project_root=project_root,
        version=version,
        events=events,
        apply=apply,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_codex_hud_hook_setup_result(payload.get("result", {}))
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-codex-hud-hook")
def verify_codex_hud_hook_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target docs version"),
    events: str = typer.Option(
        ",".join(("UserPromptSubmit", "SessionStart", "SessionResume", "SessionRefresh")),
        "--events",
        help="Comma-separated hook event names expected in wiring",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify Codex fixed HUD hook wiring managed by doctor."""
    execution = run_codex_hud_hook_verify(
        project_root=project_root,
        version=version,
        events=events,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_codex_hud_hook_verify_result(payload.get("result", {}))
    raise typer.Exit(code=execution.exit_code)


@app.command("setup-agent-surface")
def setup_agent_surface_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target docs version"),
    agent: str = typer.Option("trae", "--agent", help="Agent host: trae|claude|codex|cursor|windsurf"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    force: bool = typer.Option(False, "--force", help="Overwrite unmanaged Beacon skill directories if needed"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Materialize Beacon host-visible skills into a project-local agent surface."""
    execution = run_agent_surface_setup(
        project_root=project_root,
        version=version,
        agent=agent,
        dry_run=dry_run,
        force=force,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_agent_surface_result("Beacon Doctor Agent Surface Setup", payload.get("result", {}))
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-agent-surface")
def verify_agent_surface_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target docs version"),
    agent: str = typer.Option("trae", "--agent", help="Agent host: trae|claude|codex|cursor|windsurf"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify Beacon host-visible skills on a project-local agent surface."""
    execution = run_agent_surface_verify(
        project_root=project_root,
        version=version,
        agent=agent,
        strict=strict,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_agent_surface_verify_result(payload.get("result", {}))
    raise typer.Exit(code=execution.exit_code)


@app.command("cleanup-legacy-beacon-skills")
def cleanup_legacy_beacon_skills_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target docs version"),
    agent: str = typer.Option("all", "--agent", help="Agent host filter: trae|claude|codex|cursor|windsurf|all"),
    scope: str = typer.Option("all", "--scope", help="Cleanup scope: project|global|all"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview removals without deleting files"),
    force: bool = typer.Option(False, "--force", help="Also remove unexpected beacon-* directories outside expected taxonomy"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Remove v1.6.0 backup trees and pre-taxonomy Beacon skill aliases from agent skill roots."""
    execution = run_legacy_beacon_skills_cleanup(
        project_root=project_root,
        version=version,
        agent=agent,
        scope=scope,
        dry_run=dry_run,
        force=force,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        result = payload.get("result", {})
        typer.echo("Beacon Doctor Legacy Beacon Skill Cleanup")
        typer.echo(f"scope: {result.get('scope')} agent: {result.get('agent')} removed: {result.get('removed_count', 0)}")
        for item in result.get("removed", [])[:20]:
            typer.echo(f"  - [{item.get('kind')}] {item.get('path')}")
        if int(result.get("removed_count", 0) or 0) > 20:
            typer.echo(f"  ... and {int(result.get('removed_count', 0)) - 20} more")
    raise typer.Exit(code=execution.exit_code)


@app.command("sync-version-surfaces")
def sync_version_surfaces_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing files"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Sync Beacon self-repo version surfaces from the canonical release manifest."""
    execution = run_version_surfaces_sync(
        project_root=project_root,
        dry_run=dry_run,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_version_surface_sync_result(payload.get("result", {}))
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-version-surfaces")
def verify_version_surfaces_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as blocked"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify Beacon self-repo version surfaces against the canonical release manifest."""
    execution = run_version_surfaces_verify(
        project_root=project_root,
        strict=strict,
    )
    payload = execution.payload
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_version_surface_verify_result(payload.get("result", {}))
    raise typer.Exit(code=execution.exit_code)


@app.command("verify-version-truth-catalog")
def verify_version_truth_catalog_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    strict: bool = typer.Option(False, "--strict", help="Fail closed when catalog MD, projection, or paths drift"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify version-truth-catalog MD against machine projection and on-disk truth roots."""
    from beacon.utils.version_truth_catalog import verify_version_truth_catalog

    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = verify_version_truth_catalog(root, strict=strict)
    payload = {"schema_version": "1.0", "action": "doctor-verify-version-truth-catalog", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Version Truth Catalog Verify")
        typer.echo(f"status: {result.get('status')}")
        if result.get("reason_code"):
            typer.echo(f"reason_code: {result.get('reason_code')}")
        for check in result.get("checks") or []:
            if isinstance(check, dict):
                typer.echo(f"- {check.get('name')}: {check.get('status')} ({check.get('reason_code', '')})")
    exit_code = 0
    if result.get("status") == "fail":
        exit_code = 2
    elif strict and result.get("status") == "skipped":
        exit_code = 2
    raise typer.Exit(code=exit_code)


@app.command("sync-catalog")
def sync_catalog_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview sync without writing"),
    active_window: int = typer.Option(0, "--active-window", help="Override active delivery window (0 = use catalog default)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Discover version dirs under docs/beacon/ and sync them into version-truth-catalog."""
    from beacon.utils.version_truth_catalog import sync_catalog_versions

    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    result = sync_catalog_versions(root, dry_run=dry_run, active_window=active_window)
    payload = {"schema_version": "1.0", "action": "doctor-sync-catalog", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Sync Catalog")
        typer.echo(f"status: {result.get('status')}")
        typer.echo(f"discovered: {result.get('discovered_count')}")
        if result.get("added"):
            typer.echo(f"added: {', '.join(result['added'])}")
        if result.get("archived_by_window"):
            typer.echo(f"archived by window: {', '.join(result['archived_by_window'])}")
        typer.echo(f"skipped (already registered): {len(result.get('skipped_already_registered') or [])}")
        typer.echo(f"active window: {result.get('active_window')}")
    raise typer.Exit(code=0)


@app.command("verify-agent-eval-admission")
def verify_agent_eval_admission_command(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target docs version"),
    strict: bool = typer.Option(False, "--strict", help="Fail when admission file is missing"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Verify agent-eval live runner admission JSON for v1.6.1 agent eval."""
    from beacon.utils.agent_eval_kit import verify_agent_eval_admission
    from beacon.utils.versioning import resolve_target_version

    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    result = verify_agent_eval_admission(root, version=resolved_version)
    payload = {"schema_version": "1.0", "action": "doctor-verify-agent-eval-admission", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor Agent Eval Admission Verify")
        typer.echo(f"status: {result.get('status')}")
        if result.get("reason_code"):
            typer.echo(f"reason_code: {result.get('reason_code')}")
        if result.get("path"):
            typer.echo(f"path: {result.get('path')}")
    exit_code = 0
    if result.get("status") == "fail":
        exit_code = 2
    elif strict and result.get("status") == "skipped":
        exit_code = 2
    raise typer.Exit(code=exit_code)


@app.command("repair-evidence-manifest")
def repair_evidence_manifest_cmd(
    project: Optional[str] = typer.Option(None, "--project-root", "--project", "-p"),
    version: str = typer.Option("v1.6.8", "--version", "-v"),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Recompute .beacon/evidence-manifest.json hashes (v1.6.8 self-heal)."""
    from beacon.utils.prod_ops_v168 import repair_evidence_manifest

    root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    result = repair_evidence_manifest(root, version=version)
    payload = {"schema_version": "1.0", "action": "repair-evidence-manifest", "status": "PASS" if result.get("ok") else "FAIL", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"repair-evidence-manifest: entries={result.get('entry_count')} dropped={result.get('dropped_count')}")
    raise typer.Exit(0 if result.get("ok") else 2)


@app.command("align-run-id")
def align_run_id_cmd(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project-root", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Align run_id across status/coverage/manifest/signature chain."""
    from beacon.utils.prod_ops_v168 import align_run_id

    root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    result = align_run_id(root, run_id=run_id)
    payload = {"schema_version": "1.0", "action": "align-run-id", "status": "PASS" if result.get("ok") else "FAIL", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"align-run-id: {result.get('run_id')} updated={len(result.get('updated') or [])}")
    raise typer.Exit(0 if result.get("ok") else 2)




@app.command("diagnose-runtime")
def diagnose_runtime(
    project_root: str = typer.Option(".", "--project-root", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json", "-j"),
):
    """Diagnose CLI / version-truth / git HEAD install drift (v1.6.8)."""
    from beacon.utils.runtime_install_truth import diagnose_runtime_install

    root = Path(project_root).expanduser().resolve()
    result = diagnose_runtime_install(root)
    payload = {
        "schema_version": "1.0",
        "action": "diagnose-runtime",
        "status": "PASS" if result.get("ok") else "FAIL",
        "result": result,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"diagnose-runtime: {payload['status']} reason={result.get('reason_code') or '-'}")
        pkg = result.get("package") or {}
        vt = result.get("version_truth") or {}
        git = result.get("git") or {}
        typer.echo(f"  package={pkg.get('version')} toolkit={pkg.get('toolkit_version')}")
        typer.echo(f"  truth.current={vt.get('current_runtime_release_line')} package_version={vt.get('package_version')}")
        typer.echo(f"  git.branch={git.get('branch')} head={(git.get('head') or '')[:12]}")
        if result.get("recommended_command"):
            typer.echo(f"  repair: {result.get('recommended_command')}")
    if not result.get("ok"):
        raise typer.Exit(code=2)


@app.command("init-dual-version")
def init_dual_version_cmd(
    previous_baseline: str = typer.Option(..., "--previous-baseline"),
    next_feature: str = typer.Option(..., "--next-feature"),
    hotfix_rule: str = typer.Option("hotfix/*", "--hotfix-rule"),
    project: Optional[str] = typer.Option(None, "--project-root", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Initialize dual-version hotfix forward-port contract (v1.6.8)."""
    from beacon.utils.prod_ops_v168 import init_dual_version

    root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    result = init_dual_version(root, previous_baseline=previous_baseline, next_feature=next_feature, hotfix_rule=hotfix_rule)
    payload = {"schema_version": "1.0", "action": "init-dual-version", "status": "PASS", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"init-dual-version: {result.get('path')}")
    raise typer.Exit(0)


@app.command("verify-dual-version")
def verify_dual_version_cmd(
    project: Optional[str] = typer.Option(None, "--project-root", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Verify dual-version contract is complete."""
    from beacon.utils.prod_ops_v168 import verify_dual_version

    root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    result = verify_dual_version(root)
    payload = {"schema_version": "1.0", "action": "verify-dual-version", "status": "PASS" if result.get("ok") else "FAIL", "result": result}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"verify-dual-version: {'ok' if result.get('ok') else result.get('reason_code')}")
    raise typer.Exit(0 if result.get("ok") else 2)

@app.command("setup-git-hooks")
def setup_git_hooks_command(
    project_root: str = typer.Option(".", "--project-root", "--project", "-p"),
    force: bool = typer.Option(True, "--force/--no-force"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Install pre-commit/pre-push implement-lane enforcement hooks (UD-ENF-006)."""
    from beacon.utils.implement_lane_enforcement import setup_git_hooks

    payload = setup_git_hooks(Path(project_root), force=force)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"status: {payload.get('status')} hooks_dir: {payload.get('hooks_dir')}")
        for row in payload.get("written") or []:
            typer.echo(f"  {row.get('action')}: {row.get('path')}")
    raise typer.Exit(0 if payload.get("status") == "ok" else 1)


@app.command("verify-git-hooks")
def verify_git_hooks_command(
    project_root: str = typer.Option(".", "--project-root", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Verify implement-lane git hooks are installed and executable."""
    from beacon.utils.implement_lane_enforcement import verify_git_hooks

    payload = verify_git_hooks(Path(project_root))
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"status: {payload.get('status')}")
        for c in payload.get("checks") or []:
            typer.echo(f"  {c.get('hook')}: {c.get('status')} {c.get('reason_code') or ''}")
    raise typer.Exit(0 if payload.get("ok") else 1)


@app.command("verify-implement-lane")
def verify_implement_lane_command(
    project_root: str = typer.Option(".", "--project-root", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
    strict: bool = typer.Option(False, "--strict"),
) -> None:
    """Check current checkout is not main+dirty business implement paths."""
    from beacon.utils.implement_lane_enforcement import check_working_tree_lane

    payload = check_working_tree_lane(Path(project_root))
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"status: {payload.get('status')} branch: {payload.get('branch')}")
        if payload.get("message"):
            typer.echo(payload["message"])
        for f in payload.get("dirty_business_files") or []:
            typer.echo(f"  dirty-business: {f}")
    bad = payload.get("status") in {"blocked", "fail"} or (strict and payload.get("status") == "warn")
    raise typer.Exit(1 if bad else 0)


@app.command("check-main-implement-commit")
def check_main_implement_commit_command(
    project_root: str = typer.Option(".", "--project-root", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Simulate pre-commit: block business paths staged on main/master."""
    from beacon.utils.implement_lane_enforcement import check_main_implement_commit

    payload = check_main_implement_commit(Path(project_root))
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"status: {payload.get('status')} reason: {payload.get('reason_code')}")
        if payload.get("message"):
            typer.echo(payload["message"])
    raise typer.Exit(1 if payload.get("blocked") else 0)

