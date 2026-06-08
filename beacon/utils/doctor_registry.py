"""Internal doctor handler registry for doctor orchestration domains."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from beacon.utils.codex_hud_hook import setup_codex_hud_hook, verify_codex_hud_hook
from beacon.utils.agent_surface import setup_agent_surface, verify_agent_surface
from beacon.utils.context_files import setup_context_files, verify_context_files
from beacon.utils.doctor_diagnostics import build_doctor_payload
from beacon.utils.doctor_setup import install_launchers, uninstall_launchers
from beacon.utils.gitignore_policy import setup_beacon_gitignore, verify_beacon_gitignore
from beacon.utils.help_navigation import build_doctor_advise_payload
from beacon.utils.material_audit import build_delivery_audit, build_material_audit
from beacon.utils.material_sync import sync_project_requirement_materials
from beacon.utils.requirement_clarity import materialize_requirement_clarity
from beacon.utils.runtime_projection_store import export_runtime_ledger, rebuild_runtime_ledger, verify_runtime_ledger
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.source_architecture import current_source_architecture_status
from beacon.utils.subagent_readiness import delegation_readiness_precheck, runtime_readiness_precheck
from beacon.utils.technical_review_contract import materialize_technical_review_contract
from beacon.utils.version_surface import sync_version_surfaces, verify_version_surfaces
from beacon.utils.v115_delivery import repair_v115_delivery_package
from beacon.utils.versioning import load_project_onboarding_state, runtime_capability_lines
from beacon.utils.version_package_upgrade import upgrade_version_package
from beacon.utils.worktree_quiet import apply_quiet_worktree, quiet_worktree_status, restore_quiet_worktree

DoctorHandler = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class DoctorHandlerSpec:
    """Registry metadata for one doctor capability handler."""

    key: str
    domain: str
    action: str
    handler_id: str
    description: str
    handler: DoctorHandler = field(repr=False, compare=False)
    reads: tuple[str, ...] = ()
    writes: tuple[str, ...] = ()
    safe_by_default: bool = True
    supports_dry_run: bool = False
    supports_json: bool = True
    participates_in_parent_flows: tuple[str, ...] = ()


def _context_setup_managed_files(
    *,
    project_root: Path,
    runtime_version: str,
    docs_version: str,
    dry_run: bool,
    force: bool,
    with_claude: bool,
    with_agents: bool,
) -> dict[str, Any]:
    return setup_context_files(
        project_root=project_root,
        runtime_version=runtime_version,
        docs_version=docs_version,
        dry_run=dry_run,
        force=force,
        with_claude=with_claude,
        with_agents=with_agents,
    )


def _context_refresh_onboarding_state(
    *,
    project_root: Path,
    docs_version: str,
    runtime_version: str,
    dry_run: bool,
) -> dict[str, Any]:
    onboarding_state_path = project_root / ".beacon" / "state" / "project-onboarding.json"
    onboarding_state = load_project_onboarding_state(project_root)
    onboarding_exists = onboarding_state_path.exists()
    refreshed = {
        **onboarding_state,
        "schema_version": str(onboarding_state.get("schema_version", "") or "1.0"),
        "docs_version": str(docs_version or onboarding_state.get("docs_version", "") or ""),
        "runtime_version": runtime_version,
        "runtime_capability_lines": runtime_capability_lines(),
        "updated_at": now_iso(),
    }
    current_content = onboarding_state_path.read_text(encoding="utf-8") if onboarding_exists else ""
    next_content = json.dumps(refreshed, ensure_ascii=False, indent=2) + "\n"
    changed = current_content != next_content
    if not dry_run:
        write_json(onboarding_state_path, refreshed)
    return {
        "path": str(onboarding_state_path),
        "action": "planned" if dry_run else "updated" if onboarding_exists else "created",
        "merge_mode": "state-refresh",
        "changed": changed or not onboarding_exists,
        "backup_path": None,
        "docs_version": refreshed["docs_version"],
    }


def _context_verify_managed_files(
    *,
    project_root: Path,
    runtime_version: str,
    strict: bool,
) -> dict[str, Any]:
    return verify_context_files(
        project_root=project_root,
        runtime_version=runtime_version,
        strict=strict,
    )


def _context_sync_gitignore(
    *,
    project_root: Path,
    runtime_version: str,
    dry_run: bool,
) -> dict[str, Any]:
    return setup_beacon_gitignore(
        project_root,
        runtime_version=runtime_version,
        dry_run=dry_run,
    )


def _context_verify_gitignore(
    *,
    project_root: Path,
    runtime_version: str,
) -> dict[str, Any]:
    return verify_beacon_gitignore(
        project_root,
        runtime_version=runtime_version,
    )


def _materials_sync(
    *,
    project_root: Path,
    version: str,
    feature: str,
    all_features: bool,
    dry_run: bool,
    overwrite_test_doc: bool,
) -> dict[str, Any]:
    return sync_project_requirement_materials(
        project_root,
        version=version,
        feature=feature,
        all_features=all_features if not feature else False,
        dry_run=dry_run,
        overwrite_test_doc=overwrite_test_doc,
    )


def _materials_verify(
    *,
    project_root: Path,
    version: str | None,
    strict: bool,
) -> dict[str, Any]:
    return build_material_audit(project_root, version=version, strict=strict)


def _diagnostics_diagnose(
    *,
    project_root: Path,
    strict: bool,
) -> dict[str, Any]:
    return build_doctor_payload(project_root, strict=strict)


def _diagnostics_advise(
    *,
    project_root: Path,
    version: str | None,
    feature: str | None,
    run_id: str | None,
    strict: bool,
) -> dict[str, Any]:
    return build_doctor_advise_payload(
        project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        strict=strict,
    )


def _launcher_setup(
    *,
    bin_dir: Path,
    launcher_source: Path,
    force: bool,
    dry_run: bool,
) -> dict[str, Any]:
    return install_launchers(
        bin_dir=bin_dir,
        launcher_source=launcher_source,
        force=force,
        dry_run=dry_run,
    )


def _launcher_uninstall(
    *,
    bin_dir: Path,
    force: bool,
    dry_run: bool,
) -> dict[str, Any]:
    return uninstall_launchers(
        bin_dir=bin_dir,
        force=force,
        dry_run=dry_run,
    )


def _materials_sync_requirement_clarity(
    *,
    project_root: Path,
    version: str,
    feature: str,
) -> dict[str, Any]:
    return materialize_requirement_clarity(
        project_root,
        version=version,
        feature=feature,
        source="doctor.sync-requirement-clarity",
    )


def _materials_sync_technical_review_contract(
    *,
    project_root: Path,
    version: str,
    feature: str,
    revision_id: str,
    force_refresh: bool,
    review_status: str,
    approved_by: str,
    reviewed_at: str,
) -> dict[str, Any]:
    return materialize_technical_review_contract(
        project_root,
        version=version,
        feature=feature,
        revision_id=revision_id,
        force_refresh=force_refresh,
        contract_overrides={
            "review_status": review_status,
            "approved_by": approved_by,
            "reviewed_at": reviewed_at,
        },
        source="doctor.sync-technical-review-contract",
    )


def _runtime_verify_subagent_runtime(
    *,
    project_root: Path,
    host_runtime: str,
) -> dict[str, Any]:
    return runtime_readiness_precheck(project_root, host_runtime=host_runtime)


def _runtime_verify_subagent_delegation(
    *,
    project_root: Path,
    feature: str,
    version: str,
) -> dict[str, Any]:
    return delegation_readiness_precheck(project_root, feature=feature, version=version)


def _projection_verify_runtime_ledger(
    *,
    project_root: Path,
    version: str | None,
    feature: str | None,
) -> dict[str, Any]:
    return verify_runtime_ledger(
        project_root=project_root,
        docs_version=version or None,
        feature=feature or None,
    )


def _projection_export_runtime_ledger(
    *,
    label: str | None,
) -> dict[str, Any]:
    return export_runtime_ledger(label=label or None)


def _projection_rebuild_runtime_ledger(
    *,
    project_root: Path,
    version: str | None,
    feature: str | None,
) -> dict[str, Any]:
    return rebuild_runtime_ledger(
        project_root=project_root,
        docs_version=version or None,
        feature=feature or None,
    )


def _delivery_verify_audit(
    *,
    project_root: Path,
    version: str | None,
    strict: bool,
) -> dict[str, Any]:
    return build_delivery_audit(project_root, version=version, strict=strict)


def _package_repair(
    *,
    project_root: Path,
    version: str,
    apply: bool,
) -> dict[str, Any]:
    return repair_v115_delivery_package(project_root, version=version, apply=apply)


def _package_upgrade(
    *,
    project_root: Path,
    version: str,
    apply: bool,
) -> dict[str, Any]:
    return upgrade_version_package(project_root, version=version, apply=apply)


def _package_source_architecture_status(
    *,
    project_root: Path,
    version: str,
) -> dict[str, Any]:
    return current_source_architecture_status(project_root, version=version)


def _host_quiet_worktree(
    *,
    project_root: Path,
    mode: str,
) -> dict[str, Any]:
    normalized = mode.strip().lower()
    actions = {
        "status": quiet_worktree_status,
        "apply": apply_quiet_worktree,
        "restore": restore_quiet_worktree,
    }
    action = actions.get(normalized)
    if action is None:
        raise ValueError("mode must be one of: status, apply, restore")
    return action(project_root)


def _host_setup_codex_hud_hook(
    *,
    project_root: Path,
    version: str,
    apply: bool,
    events: str,
) -> dict[str, Any]:
    return setup_codex_hud_hook(project_root, version=version, apply=apply, events=events)


def _host_verify_codex_hud_hook(
    *,
    project_root: Path,
    version: str,
    events: str,
) -> dict[str, Any]:
    return verify_codex_hud_hook(project_root, version=version, events=events)


def _host_setup_agent_surface(
    *,
    project_root: Path,
    agent: str,
    runtime_version: str,
    docs_version: str,
    dry_run: bool,
    force: bool,
) -> dict[str, Any]:
    return setup_agent_surface(
        project_root,
        agent=agent,
        runtime_version=runtime_version,
        docs_version=docs_version,
        dry_run=dry_run,
        force=force,
    )


def _host_verify_agent_surface(
    *,
    project_root: Path,
    agent: str,
    runtime_version: str,
    docs_version: str,
    strict: bool,
) -> dict[str, Any]:
    return verify_agent_surface(
        project_root,
        agent=agent,
        runtime_version=runtime_version,
        docs_version=docs_version,
        strict=strict,
    )


def _host_sync_version_surfaces(
    *,
    project_root: Path,
    dry_run: bool,
) -> dict[str, Any]:
    return sync_version_surfaces(project_root, dry_run=dry_run)


def _host_verify_version_surfaces(
    *,
    project_root: Path,
    strict: bool,
) -> dict[str, Any]:
    return verify_version_surfaces(project_root, strict=strict)


@lru_cache(maxsize=1)
def get_doctor_registry() -> dict[str, DoctorHandlerSpec]:
    """Return the doctor execution registry."""
    specs = [
        DoctorHandlerSpec(
            key="diagnostics.run.payload",
            domain="diagnostics",
            action="verify",
            handler_id="payload",
            description="Build the top-level doctor diagnostics payload.",
            reads=("project_root",),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("doctor", "diagnose"),
            handler=_diagnostics_diagnose,
        ),
        DoctorHandlerSpec(
            key="diagnostics.advise.next-step",
            domain="diagnostics",
            action="advise",
            handler_id="next-step",
            description="Build doctor advice payload with next-step recommendation.",
            reads=("project_root", "version", "feature", "run_id"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("advise",),
            handler=_diagnostics_advise,
        ),
        DoctorHandlerSpec(
            key="launcher.setup.install",
            domain="launcher",
            action="setup",
            handler_id="install",
            description="Install doctor-managed beacon launchers into a PATH bin directory.",
            reads=("bin_dir", "launcher_source"),
            writes=("bin_dir/beacon", "bin_dir/beacon-cli"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("setup",),
            handler=_launcher_setup,
        ),
        DoctorHandlerSpec(
            key="launcher.uninstall.remove",
            domain="launcher",
            action="repair",
            handler_id="remove",
            description="Uninstall doctor-managed beacon launchers from a PATH bin directory.",
            reads=("bin_dir",),
            writes=("bin_dir/beacon", "bin_dir/beacon-cli"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("uninstall",),
            handler=_launcher_uninstall,
        ),
        DoctorHandlerSpec(
            key="context.setup.managed-files",
            domain="context",
            action="setup",
            handler_id="managed-files",
            description="Create or refresh managed CLAUDE.md/AGENTS.md/global boundaries blocks.",
            reads=("project_root", "runtime_version", "docs_version"),
            writes=("CLAUDE.md", "AGENTS.md", "docs/beacon/global-boundaries.md"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("setup-context", "doctor --fix"),
            handler=_context_setup_managed_files,
        ),
        DoctorHandlerSpec(
            key="context.setup.onboarding-state",
            domain="context",
            action="setup",
            handler_id="onboarding-state",
            description="Refresh Beacon onboarding state projection for runtime/docs context.",
            reads=("project_root", "docs_version", "runtime_version"),
            writes=(".beacon/state/project-onboarding.json",),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("setup-context", "doctor --fix"),
            handler=_context_refresh_onboarding_state,
        ),
        DoctorHandlerSpec(
            key="context.verify.managed-files",
            domain="context",
            action="verify",
            handler_id="managed-files",
            description="Verify managed CLAUDE.md/AGENTS.md/global boundaries integrity and version drift.",
            reads=("project_root", "runtime_version"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-context",),
            handler=_context_verify_managed_files,
        ),
        DoctorHandlerSpec(
            key="context.sync.gitignore",
            domain="context",
            action="sync",
            handler_id="gitignore",
            description="Create or refresh the Beacon-managed .gitignore block.",
            reads=("project_root", "runtime_version"),
            writes=(".gitignore",),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("setup-context", "sync-gitignore", "doctor --fix"),
            handler=_context_sync_gitignore,
        ),
        DoctorHandlerSpec(
            key="context.verify.gitignore",
            domain="context",
            action="verify",
            handler_id="gitignore",
            description="Verify Beacon-managed .gitignore integrity and version drift.",
            reads=("project_root", "runtime_version"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-context", "verify-gitignore"),
            handler=_context_verify_gitignore,
        ),
        DoctorHandlerSpec(
            key="materials.sync.requirement-materials",
            domain="materials",
            action="sync",
            handler_id="requirement-materials",
            description="Project human requirement docs into machine story and QA artifacts.",
            reads=("project_root", "version", "feature"),
            writes=("docs/beacon/<version>/.machine/user-story", "docs/beacon/<version>/.machine/qa"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("sync-materials", "setup-context"),
            handler=_materials_sync,
        ),
        DoctorHandlerSpec(
            key="materials.sync.requirement-clarity",
            domain="materials",
            action="sync",
            handler_id="requirement-clarity",
            description="Materialize requirement clarity report and writeback state.",
            reads=("project_root", "version", "feature"),
            writes=("docs/beacon/<version>/execution", ".beacon/state"),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("sync-requirement-clarity",),
            handler=_materials_sync_requirement_clarity,
        ),
        DoctorHandlerSpec(
            key="materials.sync.technical-review-contract",
            domain="materials",
            action="sync",
            handler_id="technical-review-contract",
            description="Materialize deterministic technical review contract and writeback state.",
            reads=("project_root", "version", "feature", "revision_id"),
            writes=("docs/beacon/<version>/execution", ".beacon/state"),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("sync-technical-review-contract",),
            handler=_materials_sync_technical_review_contract,
        ),
        DoctorHandlerSpec(
            key="materials.verify.material-audit",
            domain="materials",
            action="verify",
            handler_id="material-audit",
            description="Verify main-chain requirement material completeness.",
            reads=("project_root", "version"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-materials",),
            handler=_materials_verify,
        ),
        DoctorHandlerSpec(
            key="runtime.verify.subagent-runtime",
            domain="runtime",
            action="verify",
            handler_id="subagent-runtime",
            description="Verify host-native subagent runtime readiness.",
            reads=("project_root", "host_runtime"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-subagent-runtime",),
            handler=_runtime_verify_subagent_runtime,
        ),
        DoctorHandlerSpec(
            key="runtime.verify.subagent-delegation",
            domain="runtime",
            action="verify",
            handler_id="subagent-delegation",
            description="Verify feature-level delegation readiness for subagent execution.",
            reads=("project_root", "feature", "version"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-subagent-delegation",),
            handler=_runtime_verify_subagent_delegation,
        ),
        DoctorHandlerSpec(
            key="projection.verify.runtime-ledger",
            domain="projection",
            action="verify",
            handler_id="runtime-ledger",
            description="Verify deterministic runtime-ledger projection and PocketBase control-plane health.",
            reads=("project_root", "version", "feature"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-runtime-ledger",),
            handler=_projection_verify_runtime_ledger,
        ),
        DoctorHandlerSpec(
            key="projection.export.runtime-ledger",
            domain="projection",
            action="export",
            handler_id="runtime-ledger",
            description="Export runtime-ledger SQLite/projection/PocketBase artifacts for backup.",
            reads=("runtime_ledger_root",),
            writes=("runtime-ledger-export",),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("export-runtime-ledger",),
            handler=_projection_export_runtime_ledger,
        ),
        DoctorHandlerSpec(
            key="projection.rebuild.runtime-ledger",
            domain="projection",
            action="repair",
            handler_id="runtime-ledger",
            description="Rebuild runtime-ledger projection from local Beacon truth.",
            reads=("project_root", "version", "feature"),
            writes=("runtime-ledger.sqlite3", "pocketbase/collections", "runtime-ledger/projections"),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("rebuild-runtime-ledger",),
            handler=_projection_rebuild_runtime_ledger,
        ),
        DoctorHandlerSpec(
            key="delivery.verify.audit",
            domain="delivery",
            action="verify",
            handler_id="audit",
            description="Verify execution-layer delivery artifacts and audit checks.",
            reads=("project_root", "version"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-delivery", "verify-config", "verify-git-alignment"),
            handler=_delivery_verify_audit,
        ),
        DoctorHandlerSpec(
            key="package.repair.v115-delivery",
            domain="package",
            action="repair",
            handler_id="v115-delivery",
            description="Repair legacy delivery package into v1.1.5 layered structure.",
            reads=("project_root", "version"),
            writes=("docs/beacon/<version>/execution", "docs/beacon/<version>/.machine", ".beacon/state/eval-lab"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("repair-package",),
            handler=_package_repair,
        ),
        DoctorHandlerSpec(
            key="package.upgrade.version-package",
            domain="package",
            action="repair",
            handler_id="version-package",
            description="Upgrade older Beacon version package to current runtime-compatible material structure.",
            reads=("project_root", "version"),
            writes=("docs/beacon/<version>", "docs/beacon/<version>/.machine"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("upgrade-package", "doctor --fix"),
            handler=_package_upgrade,
        ),
        DoctorHandlerSpec(
            key="package.verify.source-architecture-status",
            domain="package",
            action="verify",
            handler_id="source-architecture-status",
            description="Read current source architecture status for upgraded package reporting.",
            reads=("project_root", "version"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("upgrade-package",),
            handler=_package_source_architecture_status,
        ),
        DoctorHandlerSpec(
            key="host.quiet-worktree.manage",
            domain="host",
            action="repair",
            handler_id="quiet-worktree",
            description="Manage local skip-worktree and exclude quieting for Beacon runtime churn.",
            reads=("project_root", "mode"),
            writes=(".git/info/exclude", "git-index"),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("quiet-worktree",),
            handler=_host_quiet_worktree,
        ),
        DoctorHandlerSpec(
            key="host.setup.codex-hud-hook",
            domain="host",
            action="setup",
            handler_id="codex-hud-hook",
            description="Generate or apply Codex fixed HUD hook wiring.",
            reads=("project_root", "version", "events"),
            writes=("plugins/beacon-fixed-hud", ".agents/plugins/marketplace.json"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("setup-codex-hud-hook",),
            handler=_host_setup_codex_hud_hook,
        ),
        DoctorHandlerSpec(
            key="host.verify.codex-hud-hook",
            domain="host",
            action="verify",
            handler_id="codex-hud-hook",
            description="Verify Codex fixed HUD hook wiring and runtime activation proof.",
            reads=("project_root", "version", "events"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-codex-hud-hook",),
            handler=_host_verify_codex_hud_hook,
        ),
        DoctorHandlerSpec(
            key="host.setup.agent-surface",
            domain="host",
            action="setup",
            handler_id="agent-surface",
            description="Materialize Beacon host-visible skills into a project-local agent surface.",
            reads=("project_root", "agent", "runtime_version", "docs_version"),
            writes=(".trae/skills", ".trae/rules/project_rules.md", ".beacon/state/agent-surfaces.json"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("setup-agent-surface",),
            handler=_host_setup_agent_surface,
        ),
        DoctorHandlerSpec(
            key="host.verify.agent-surface",
            domain="host",
            action="verify",
            handler_id="agent-surface",
            description="Verify project-local Beacon agent surface materialization and drift.",
            reads=("project_root", "agent", "runtime_version"),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-agent-surface",),
            handler=_host_verify_agent_surface,
        ),
        DoctorHandlerSpec(
            key="host.sync.version-surfaces",
            domain="host",
            action="sync",
            handler_id="version-surfaces",
            description="Sync Beacon self-repo version surfaces from the canonical release manifest.",
            reads=("project_root",),
            writes=("beacon/version-truth.json", "beacon/__init__.py", "skills/beacon/metadata.json", "SKILL.md", ".trae/rules/project_rules.md", ".beacon/state/agent-surfaces.json"),
            safe_by_default=True,
            supports_dry_run=True,
            participates_in_parent_flows=("sync-version-surfaces",),
            handler=_host_sync_version_surfaces,
        ),
        DoctorHandlerSpec(
            key="host.verify.version-surfaces",
            domain="host",
            action="verify",
            handler_id="version-surfaces",
            description="Verify Beacon self-repo version surfaces against the canonical release manifest.",
            reads=("project_root",),
            writes=(),
            safe_by_default=True,
            supports_dry_run=False,
            participates_in_parent_flows=("verify-version-surfaces",),
            handler=_host_verify_version_surfaces,
        ),
    ]
    return {spec.key: spec for spec in specs}


def get_doctor_handler(key: str) -> DoctorHandlerSpec:
    """Lookup one doctor handler spec by registry key."""
    try:
        return get_doctor_registry()[key]
    except KeyError as exc:  # pragma: no cover - defensive only
        raise KeyError(f"unknown doctor handler: {key}") from exc
