"""Legacy project cutover preflight and phased migration helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.agent_surface import verify_agent_surface
from beacon.utils.feature_package import materialize_feature_package, package_paths, validate_feature_package
from beacon.utils.project_governance import commit_governance_payload, governance_md_authoritative, load_governance_payload
from beacon.utils.project_metadata import verify_project_metadata
from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_map import feature_package_authoritative, rebuild_machine_json, verify_truth_map
from beacon.utils.versioning import resolve_target_version


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _phase(status: str, *, blocked: bool | None = None, reason_code: str = "", next_command: str = "", **extra: Any) -> dict[str, Any]:
    return {
        "status": status,
        "blocked": status != "pass" if blocked is None else blocked,
        "reason_code": reason_code,
        "next_command": next_command,
        **extra,
    }


def _legacy_triptych_refs(project_root: Path, *, version: str, feature: str) -> list[str]:
    slug = feature_slug(feature)
    refs: list[str] = []
    docs_root = project_root / "docs" / "beacon"
    if not docs_root.exists():
        return refs
    for version_dir in sorted(item for item in docs_root.iterdir() if item.is_dir()):
        if version_dir.name == version:
            continue
        for rel in (
            Path("prd") / f"{slug}.md",
            Path("user-story") / f"{slug}.md",
            Path("qa") / "test-cases" / f"{slug}.md",
        ):
            path = version_dir / rel
            if path.exists():
                refs.append(_rel(project_root, path))
    return refs


def _package_phase(project_root: Path, *, version: str, feature: str, apply: bool) -> dict[str, Any]:
    slug = feature_slug(feature)
    paths = package_paths(project_root, version=version, feature=slug)
    missing = [name for name in ("truth", "tests", "tasks", "evidence") if not paths[name].exists()]
    materialized: dict[str, Any] = {}
    if missing and apply:
        materialized = materialize_feature_package(project_root, version=version, feature=slug)
    validation = validate_feature_package(project_root, version=version, feature=slug, write_report=apply)
    truth_verify = verify_truth_map(project_root, version=version, feature=slug, strict=False)
    machine_rebuild: dict[str, Any] = {}
    if validation.get("status") == "pass" and apply:
        machine_rebuild = rebuild_machine_json(project_root, version=version, feature=slug, strict=True)
        truth_verify = verify_truth_map(project_root, version=version, feature=slug, strict=False)

    blocked = bool(missing and not apply) or validation.get("status") != "pass" or truth_verify.get("status") != "pass"
    reason = ""
    if missing and not apply:
        reason = "feature_package_missing"
    elif validation.get("status") != "pass":
        reason = str(validation.get("reason_code") or "feature_package_validation_failed")
    elif truth_verify.get("status") != "pass":
        reason = "truth_map_verify_failed"

    return _phase(
        "blocked" if blocked else "pass",
        reason_code=reason,
        next_command=f"beacon materialize-feature-package {slug} --project . --version {version} --json" if missing else f"beacon truth-map verify {slug} --project . --version {version} --json",
        missing_surfaces=missing,
        paths={name: _rel(project_root, paths[name]) for name in ("truth", "tests", "tasks", "evidence")},
        validation=validation,
        truth_map_verify=truth_verify,
        materialized=materialized,
        machine_rebuild=machine_rebuild,
    )


def _governance_phase(project_root: Path, *, version: str, apply: bool) -> dict[str, Any]:
    verify = verify_project_metadata(project_root, version=version)
    projection_sync: dict[str, Any] = {}
    if apply and verify.get("status") == "fail" and governance_md_authoritative(project_root):
        failed_names = {
            str(item.get("name") or "")
            for item in verify.get("checks", [])
            if isinstance(item, dict) and str(item.get("status") or "") == "fail"
        }
        if failed_names == {"governance_projection_drift"}:
            projection_sync = commit_governance_payload(
                project_root,
                load_governance_payload(project_root),
                event_type="legacy-cutover-projection-sync",
            )
            verify = verify_project_metadata(project_root, version=version)
    blocked = verify.get("status") == "fail"
    return _phase(
        "blocked" if blocked else "pass",
        reason_code="governance_verify_failed" if blocked else "",
        next_command=f"beacon doctor metadata verify --project-root {project_root} --version {version} --json",
        verify=verify,
        projection_sync=projection_sync,
    )


def _agent_phase(project_root: Path, *, version: str, agent: str) -> dict[str, Any]:
    verify = verify_agent_surface(project_root, agent=agent, runtime_version=version, strict=True)
    blocked = verify.get("status") != "pass"
    return _phase(
        "blocked" if blocked else "pass",
        reason_code="agent_surface_verify_failed" if blocked else "",
        next_command=f"beacon doctor setup-agent-surface --project-root {project_root} --version {version} --agent {agent} --force --json",
        verify=verify,
    )


def should_route_to_legacy_cutover(cutover: dict[str, Any]) -> bool:
    """Return true when a v1.5.2 runtime surface must stop and run cutover."""

    phases = cutover.get("phases") if isinstance(cutover.get("phases"), dict) else {}
    package_phase = phases.get("package") if isinstance(phases.get("package"), dict) else {}
    return bool(cutover.get("legacy_truth_present")) or bool(package_phase.get("blocked"))


def legacy_cutover_route_payload(*, project_root: Path, version: str, feature: str, resume_intent: str = "refreeze") -> dict[str, Any]:
    return {
        "target_surface": "beacon-truth-cutover",
        "command": (
            f'beacon truth-cutover run "{feature}" --project {project_root} '
            f"--version {version} --apply --resume-intent {resume_intent} --json"
        ),
        "why": "legacy or mixed v1.5.2 truth/governance/agent-surface state must pass cutover before continuing",
    }


def build_legacy_cutover_preflight(
    project_root: Path,
    *,
    version: str,
    feature: str,
    resume_intent: str,
    agent: str = "codex",
) -> dict[str, Any]:
    cutover = run_legacy_project_cutover(
        project_root,
        version=version,
        feature=feature,
        apply=False,
        agent=agent,
        resume_intent=resume_intent,
    )
    routed = should_route_to_legacy_cutover(cutover)
    resolved_version = str(cutover.get("version") or resolve_target_version(project_root, version))
    return {
        "schema_version": "1.0",
        "status": "blocked" if routed else "pass",
        "blocked": routed,
        "reason_code": "legacy_cutover_required" if routed else "",
        "version": resolved_version,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "resume_intent": resume_intent,
        "legacy_cutover": cutover,
        "next_route": legacy_cutover_route_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            resume_intent=resume_intent,
        ) if routed else {},
    }


def run_legacy_project_cutover(
    project_root: Path,
    *,
    version: str,
    feature: str,
    apply: bool = False,
    agent: str = "codex",
    resume_intent: str = "refreeze",
) -> dict[str, Any]:
    """Classify and optionally repair a legacy/mixed project before v1.5.2 execution."""

    root = project_root.expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    slug = feature_slug(feature)
    supported = feature_package_authoritative(resolved_version)
    legacy_refs = _legacy_triptych_refs(root, version=resolved_version, feature=slug)

    if not supported:
        return {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "status": "not_required",
            "blocked": False,
            "reason_code": "",
            "supported": False,
            "dry_run": not apply,
            "generated_at": now_iso(),
            "phases": {},
        }

    package = _package_phase(root, version=resolved_version, feature=slug, apply=apply)
    governance = _governance_phase(root, version=resolved_version, apply=apply)
    agent_surface = _agent_phase(root, version=resolved_version, agent=agent)
    inventory_blocked = bool(package["blocked"] or governance["blocked"] or agent_surface["blocked"])
    phases = {
        "inventory": _phase(
            "blocked" if inventory_blocked else "pass",
            reason_code="legacy_or_mixed_truth_state" if inventory_blocked else "",
            legacy_refs=legacy_refs,
        ),
        "package": package,
        "governance": governance,
        "agent_surface": agent_surface,
    }
    blocked = any(bool(phase.get("blocked")) for phase in phases.values())
    resume_command = ""
    if resume_intent == "refreeze":
        resume_command = f'beacon change "{feature}" --project {root} --version {resolved_version} --refreeze-chain'
    elif resume_intent:
        resume_command = f'beacon {resume_intent} "{feature}" --project {root} --version {resolved_version}'
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": "legacy_or_mixed_truth_state" if blocked else "",
        "supported": True,
        "dry_run": not apply,
        "apply": apply,
        "agent": agent,
        "legacy_truth_present": bool(legacy_refs),
        "generated_at": now_iso(),
        "phases": phases,
        "resume": {
            "intent": resume_intent,
            "next_command": resume_command if not blocked else "",
            "blocked_until_cutover_passes": blocked,
        },
    }
