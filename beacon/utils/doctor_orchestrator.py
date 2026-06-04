"""Internal orchestration helpers for doctor command domains."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import change_docs_file, change_file_output
from beacon.utils.doctor_diagnostics import collect_runtime_info
from beacon.utils.doctor_setup import resolve_bin_dir
from beacon.utils.doctor_registry import get_doctor_handler
from beacon.utils.test_contract_governance import build_test_contract_gate_payload, build_test_contract_index
from beacon.utils.technical_review_contract import technical_review_contract_json_path, technical_review_contract_markdown_path
from beacon.utils.version_aggregate_projection import (
    PROJECTION_ROLE,
    write_feature_change_projection,
)
from beacon.utils.versioning import describe_project_version_context, resolve_target_version
from beacon.utils.writeback import acceptance_projection_transaction_contract
from beacon.utils.workflow_memory import backfill_workflow_memory


@dataclass(frozen=True)
class DoctorExecutionContext:
    """Resolved execution context shared across doctor handlers."""

    project_root: Path
    runtime_info: dict[str, Any]
    runtime_version: str
    version: str | None = None
    version_context: dict[str, Any] | None = None
    strict: bool = False
    dry_run: bool = False


@dataclass(frozen=True)
class DoctorExecutionResult:
    """Standard execution result returned to CLI adapters."""

    payload: dict[str, Any]
    exit_code: int


def resolve_doctor_project_root(project_root: str) -> Path:
    """Resolve a doctor project root with CLI-compatible fallback."""
    root = Path(project_root) if project_root else Path.cwd()
    return root.expanduser().resolve()


def resolve_doctor_runtime_version(runtime_info: dict[str, Any] | None = None) -> str:
    """Resolve the active runtime/toolkit version used for doctor flows."""
    runtime = runtime_info or collect_runtime_info()
    return str(runtime.get("toolkit_version") or runtime.get("package_version") or "v1.0.0")


def build_doctor_execution_context(
    project_root: str | Path,
    *,
    version: str | None = None,
    strict: bool = False,
    dry_run: bool = False,
    include_version_context: bool = True,
) -> DoctorExecutionContext:
    """Build the shared execution context consumed by doctor handlers."""
    root = (Path(project_root) if isinstance(project_root, Path) else resolve_doctor_project_root(project_root)).expanduser().resolve()
    runtime_info = collect_runtime_info()
    runtime_version = resolve_doctor_runtime_version(runtime_info)
    version_context = None
    if include_version_context:
        version_context = describe_project_version_context(
            root,
            docs_version=version or None,
            runtime_version=runtime_version,
        )
    return DoctorExecutionContext(
        project_root=root,
        runtime_info=runtime_info,
        runtime_version=runtime_version,
        version=version,
        version_context=version_context,
        strict=strict,
        dry_run=dry_run,
    )


def merge_check_statuses(checks: list[dict[str, Any]], *, strict: bool = False) -> str:
    """Merge doctor checks into pass/warn/fail with strict semantics."""
    statuses = [str(item.get("status", "warn")).lower() for item in checks if isinstance(item, dict)]
    if any(status == "fail" for status in statuses):
        return "fail"
    if any(status == "warn" for status in statuses):
        return "fail" if strict else "warn"
    return "pass"


def _semver_tuple(value: str | None) -> tuple[int, int, int]:
    text = str(value or "").strip().lower()
    if text.startswith("v"):
        text = text[1:]
    parts = text.split(".")
    numbers: list[int] = []
    for part in parts[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        numbers.append(int(digits or "0"))
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers[:3])


def build_single_check_payload(
    *,
    action: str,
    project_root: Path,
    version: str | None,
    strict: bool,
    check: dict[str, Any],
) -> dict[str, Any]:
    """Wrap one logical verification result into the standard doctor JSON envelope."""
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


def run_doctor_handler(key: str, /, **kwargs: Any) -> dict[str, Any]:
    """Execute one registered doctor handler by key."""
    return get_doctor_handler(key).handler(**kwargs)


def resolve_launcher_source_path(launcher_source: str) -> Path:
    """Resolve launcher source path with runtime fallback semantics."""
    if launcher_source:
        return Path(launcher_source).expanduser().resolve()
    runtime = collect_runtime_info()
    candidate = Path(str(runtime.get("launcher_path", "")).strip())
    if candidate.exists():
        return candidate
    return (Path(__file__).resolve().parents[2] / "beacon-cli").resolve()


def _map_verify_status(status: str) -> str:
    return {"pass": "PASS", "warn": "WARN", "fail": "BLOCKED"}.get(str(status).lower(), str(status).upper())


def _delivery_payload(action: str, result: dict[str, Any], *, strict: bool) -> DoctorExecutionResult:
    payload = {
        "schema_version": "2.0",
        "action": action,
        "status": str(result.get("status", "warn")).upper(),
        "result": result,
    }
    if strict and payload["status"] == "WARN":
        payload["status"] = "BLOCKED"
    exit_code = 2 if payload.get("status") in {"FAIL", "BLOCKED"} else 0
    return DoctorExecutionResult(payload=payload, exit_code=exit_code)


def run_doctor_diagnose(
    *,
    project_root: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Run the top-level doctor diagnostics payload."""
    ctx = build_doctor_execution_context(project_root, strict=strict, include_version_context=False)
    payload = run_doctor_handler(
        "diagnostics.run.payload",
        project_root=ctx.project_root,
        strict=strict,
    )
    return DoctorExecutionResult(payload=payload, exit_code=2 if payload.get("overall") == "BLOCKED" else 0)


def run_doctor_advise(
    *,
    project_root: str,
    version: str,
    feature: str,
    run_id: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Run the doctor advice payload."""
    ctx = build_doctor_execution_context(project_root, version=version or None, strict=strict, include_version_context=False)
    payload = run_doctor_handler(
        "diagnostics.advise.next-step",
        project_root=ctx.project_root,
        version=version or None,
        feature=feature or None,
        run_id=run_id or None,
        strict=strict,
    )
    return DoctorExecutionResult(payload=payload, exit_code=2 if payload.get("status") == "BLOCKED" else 0)


def run_context_setup(
    *,
    project_root: str,
    version: str | None = None,
    dry_run: bool,
    force: bool,
    sync_materials: bool,
    feature: str,
    all_features: bool,
    overwrite_test_doc: bool,
    with_claude: bool,
    with_agents: bool,
    with_gitignore: bool,
) -> DoctorExecutionResult:
    """Run the context setup orchestration."""
    ctx = build_doctor_execution_context(project_root, version=version or None, dry_run=dry_run)
    version_context = ctx.version_context or {}
    result = run_doctor_handler(
        "context.setup.managed-files",
        project_root=ctx.project_root,
        runtime_version=ctx.runtime_version,
        docs_version=str(version_context.get("docs_version", "") or ctx.runtime_version),
        dry_run=dry_run,
        force=force,
        with_claude=with_claude,
        with_agents=with_agents,
    )
    result_actions = result.get("actions") if isinstance(result.get("actions"), list) else []

    if with_gitignore:
        gitignore_result = run_doctor_handler(
            "context.sync.gitignore",
            project_root=ctx.project_root,
            runtime_version=ctx.runtime_version,
            dry_run=dry_run,
        )
        result_actions.append(
            {
                "file": ".gitignore",
                "path": str(Path(str(gitignore_result.get("path", ""))).relative_to(ctx.project_root)),
                "force": False,
                "merge_mode": str(gitignore_result.get("merge_mode", "")),
                "action": str(gitignore_result.get("action", "unchanged")),
                "changed": bool(gitignore_result.get("changed", False)),
                "backup_path": gitignore_result.get("backup_path"),
            }
        )

    onboarding_result = run_doctor_handler(
        "context.setup.onboarding-state",
        project_root=ctx.project_root,
        docs_version=str(version_context.get("docs_version", "") or ""),
        runtime_version=ctx.runtime_version,
        dry_run=dry_run,
    )
    result_actions.append(
        {
            "file": str(Path(str(onboarding_result.get("path", ""))).relative_to(ctx.project_root)),
            "action": str(onboarding_result.get("action", "planned")),
            "merge_mode": str(onboarding_result.get("merge_mode", "state-refresh")),
            "changed": bool(onboarding_result.get("changed", True)),
            "backup_path": onboarding_result.get("backup_path"),
        }
    )
    result["actions"] = result_actions

    material_sync_result = None
    if sync_materials:
        docs_version = str(version_context.get("docs_version", "") or "")
        if docs_version:
            material_sync_result = run_doctor_handler(
                "materials.sync.requirement-materials",
                project_root=ctx.project_root,
                version=docs_version,
                feature=feature,
                all_features=all_features,
                dry_run=dry_run,
                overwrite_test_doc=overwrite_test_doc,
            )

    payload = {
        "schema_version": "2.0",
        "action": "setup-context",
        "status": "PASS",
        "docs_version": version_context.get("docs_version", ""),
        "runtime_version": ctx.runtime_version,
        "version_context": version_context,
        "version_semantics": version_context.get("version_semantics", {}),
        "result": result,
        "material_sync": material_sync_result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_context_verify(
    *,
    project_root: str,
    strict: bool,
    with_gitignore: bool,
) -> DoctorExecutionResult:
    """Run the context verify orchestration."""
    ctx = build_doctor_execution_context(project_root, strict=strict)
    version_context = ctx.version_context or {}
    result = run_doctor_handler(
        "context.verify.managed-files",
        project_root=ctx.project_root,
        runtime_version=ctx.runtime_version,
        strict=strict,
    )
    checks = result.get("checks") if isinstance(result.get("checks"), list) else []
    if with_gitignore:
        checks.append(
            run_doctor_handler(
                "context.verify.gitignore",
                project_root=ctx.project_root,
                runtime_version=ctx.runtime_version,
            )
        )
        result["checks"] = checks
        result["status"] = merge_check_statuses(checks, strict=False)
    status_map = {"pass": "PASS", "warn": "WARN", "fail": "BLOCKED"}
    payload = {
        "schema_version": "2.0",
        "action": "verify-context",
        "status": status_map.get(str(result.get("status", "warn")).lower(), "WARN"),
        "docs_version": version_context.get("docs_version", ""),
        "runtime_version": ctx.runtime_version,
        "version_context": version_context,
        "version_semantics": version_context.get("version_semantics", {}),
        "result": result,
    }
    if strict and payload["status"] == "WARN":
        payload["status"] = "BLOCKED"
    return DoctorExecutionResult(payload=payload, exit_code=2 if payload["status"] == "BLOCKED" else 0)


def run_gitignore_setup(
    *,
    project_root: str,
    dry_run: bool,
) -> DoctorExecutionResult:
    """Run the gitignore sync handler through the doctor registry."""
    ctx = build_doctor_execution_context(project_root, dry_run=dry_run, include_version_context=False)
    result = run_doctor_handler(
        "context.sync.gitignore",
        project_root=ctx.project_root,
        runtime_version=ctx.runtime_version,
        dry_run=dry_run,
    )
    payload = {
        "schema_version": "2.0",
        "action": "sync-gitignore",
        "status": "PASS",
        "runtime_version": ctx.runtime_version,
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_gitignore_verify(
    *,
    project_root: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Run the gitignore verify handler through the doctor registry."""
    ctx = build_doctor_execution_context(project_root, strict=strict, include_version_context=False)
    result = run_doctor_handler(
        "context.verify.gitignore",
        project_root=ctx.project_root,
        runtime_version=ctx.runtime_version,
    )
    payload = build_single_check_payload(
        action="verify-gitignore",
        project_root=ctx.project_root,
        version=None,
        strict=strict,
        check=result,
    )
    return DoctorExecutionResult(payload=payload, exit_code=2 if payload.get("status") == "BLOCKED" else 0)


def run_materials_sync(
    *,
    project_root: str,
    version: str,
    feature: str,
    all_features: bool,
    dry_run: bool,
    overwrite_test_doc: bool,
) -> DoctorExecutionResult:
    """Run the material sync handler through the doctor registry."""
    ctx = build_doctor_execution_context(project_root, version=version, dry_run=dry_run)
    result = run_doctor_handler(
        "materials.sync.requirement-materials",
        project_root=ctx.project_root,
        version=version,
        feature=feature,
        all_features=all_features,
        dry_run=dry_run,
        overwrite_test_doc=overwrite_test_doc,
    )
    payload = {
        "schema_version": "2.0",
        "action": "sync-materials",
        "status": "PASS",
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_materials_verify(
    *,
    project_root: str,
    version: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Run the material verify handler through the doctor registry."""
    ctx = build_doctor_execution_context(project_root, version=version or None, strict=strict)
    result = run_doctor_handler(
        "materials.verify.material-audit",
        project_root=ctx.project_root,
        version=version or None,
        strict=strict,
    )
    payload = {
        "schema_version": "2.0",
        "action": "verify-materials",
        "status": str(result.get("status", "warn")).upper(),
        "result": result,
    }
    if strict and payload["status"] == "WARN":
        payload["status"] = "BLOCKED"
    exit_code = 2 if payload.get("status") in {"FAIL", "BLOCKED"} else 0
    return DoctorExecutionResult(payload=payload, exit_code=exit_code)


def run_requirement_clarity_sync(
    *,
    project_root: str,
    version: str,
    feature: str,
) -> DoctorExecutionResult:
    """Materialize requirement clarity report and writeback state."""
    ctx = build_doctor_execution_context(project_root, version=version)
    result = run_doctor_handler(
        "materials.sync.requirement-clarity",
        project_root=ctx.project_root,
        version=version,
        feature=feature,
    )
    payload = {
        "schema_version": "2.0",
        "action": "sync-requirement-clarity",
        "status": "PASS",
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_technical_review_contract_sync(
    *,
    project_root: str,
    version: str,
    feature: str,
    revision_id: str,
    review_status: str,
    approved_by: str,
    reviewed_at: str,
    force_refresh: bool,
) -> DoctorExecutionResult:
    """Materialize deterministic technical review contract payload and derived paths."""
    ctx = build_doctor_execution_context(project_root, version=version)
    payload = run_doctor_handler(
        "materials.sync.technical-review-contract",
        project_root=ctx.project_root,
        version=version,
        feature=feature,
        revision_id=revision_id,
        force_refresh=force_refresh,
        review_status=review_status,
        approved_by=approved_by,
        reviewed_at=reviewed_at,
    )
    version_value = str(payload.get("version", "") or version)
    result = {
        "schema_version": "1.0",
        "feature": feature,
        "version": version_value,
        "review_status": str(payload.get("review_status", "") or ""),
        "contract_json_path": str(technical_review_contract_json_path(ctx.project_root, version_value, feature).relative_to(ctx.project_root)),
        "contract_markdown_path": str(technical_review_contract_markdown_path(ctx.project_root, version_value, feature).relative_to(ctx.project_root)),
        "state_path": str((payload.get("writeback", {}) or {}).get("state_path", "") or ""),
        "payload": payload,
    }
    output = {
        "schema_version": "2.0",
        "action": "sync-technical-review-contract",
        "status": "PASS",
        "result": result,
    }
    return DoctorExecutionResult(payload=output, exit_code=0)


def run_test_contract_index_build(
    *,
    project_root: str,
    version: str,
    feature: str,
) -> DoctorExecutionResult:
    ctx = build_doctor_execution_context(project_root, version=version)
    result = build_test_contract_index(ctx.project_root, version=version, feature=feature, write=True)
    output = {
        "schema_version": "2.0",
        "action": "build-test-contract-index",
        "status": "PASS" if not result.get("blocked") else "BLOCKED",
        "result": result,
    }
    return DoctorExecutionResult(payload=output, exit_code=2 if result.get("blocked") else 0)


def run_test_contract_index_verify(
    *,
    project_root: str,
    version: str,
    feature: str,
    strict: bool,
) -> DoctorExecutionResult:
    ctx = build_doctor_execution_context(project_root, version=version, strict=strict)
    result = build_test_contract_gate_payload(ctx.project_root, version=version, feature=feature)
    status = str(result.get("status") or "blocked").lower()
    blocked = status == "blocked" or status == "fail" or (strict and status == "warn")
    output = {
        "schema_version": "2.0",
        "action": "verify-test-contract-index",
        "status": "BLOCKED" if blocked else status.upper(),
        "result": {
            "schema_version": "1.0",
            "action": "verify-test-contract-index",
            "project_root": str(ctx.project_root),
            "version": str(result.get("version") or version or ""),
            "feature": feature,
            "strict": strict,
            "status": "fail" if blocked else status,
            "ok": not blocked,
            "checks": [
                {
                    "name": "test_contract_index",
                    "status": "fail" if blocked else "pass",
                    "details": result,
                }
            ],
            "gate": result,
        },
    }
    return DoctorExecutionResult(payload=output, exit_code=2 if blocked else 0)


def run_version_aggregate_projection_repair(
    *,
    project_root: str,
    version: str,
    feature: str,
    overwrite_feature_projection: bool,
) -> DoctorExecutionResult:
    ctx = build_doctor_execution_context(project_root, version=version)
    resolved_version = resolve_target_version(ctx.project_root, version)
    feature_projection = write_feature_change_projection(
        ctx.project_root,
        version=resolved_version,
        feature=feature,
        overwrite=overwrite_feature_projection,
    )

    from beacon.commands import release as release_command

    version_payload = release_command._build_version_change_payload(ctx.project_root, version=resolved_version)
    version_payload = release_command._stabilize_version_change_payload(
        ctx.project_root,
        version=resolved_version,
        payload=version_payload,
    )
    version_change_md = change_docs_file(ctx.project_root, resolved_version, f"{resolved_version}.md")
    version_change_json = change_file_output(ctx.project_root, resolved_version, f"{resolved_version}.json")
    version_change_md.parent.mkdir(parents=True, exist_ok=True)
    version_change_json.parent.mkdir(parents=True, exist_ok=True)
    version_change_md.write_text(release_command._render_version_change_markdown(version_payload), encoding="utf-8")
    version_change_json.write_text(
        json.dumps(version_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    test_index = build_test_contract_index(ctx.project_root, version=resolved_version, feature=feature, write=True)
    test_gate = build_test_contract_gate_payload(ctx.project_root, version=resolved_version, feature=feature)
    blocked = bool(test_index.get("blocked")) or str(test_gate.get("status") or "").lower() == "blocked"
    output = {
        "schema_version": "2.0",
        "action": "repair-version-aggregate-projection",
        "status": "BLOCKED" if blocked else "PASS",
        "result": {
            "schema_version": "1.0",
            "action": "repair-version-aggregate-projection",
            "project_root": str(ctx.project_root),
            "version": resolved_version,
            "feature": feature,
            "projection_role": dict(PROJECTION_ROLE),
            "truth_authority": False,
            "lifecycle_stage": False,
            "release_publish_action": False,
            "feature_projection": feature_projection,
            "version_aggregate_projection": {
                "markdown_path": str(version_change_md.relative_to(ctx.project_root)),
                "json_path": str(version_change_json.relative_to(ctx.project_root)),
                "feature_count": int(version_payload.get("feature_count") or 0),
                "feature_slugs": [
                    str(item.get("feature_slug") or "")
                    for item in version_payload.get("features", [])
                    if isinstance(item, dict) and str(item.get("feature_slug") or "")
                ],
                "implementation_order": version_payload.get("implementation_order")
                if isinstance(version_payload.get("implementation_order"), dict)
                else {},
            },
            "test_contract_index": test_index,
            "test_contract_verify": test_gate,
        },
    }
    return DoctorExecutionResult(payload=output, exit_code=2 if blocked else 0)


def run_subagent_runtime_verify(
    *,
    project_root: str,
    host_runtime: str,
) -> DoctorExecutionResult:
    """Verify host-native subagent runtime readiness."""
    ctx = build_doctor_execution_context(project_root, include_version_context=False)
    result = run_doctor_handler(
        "runtime.verify.subagent-runtime",
        project_root=ctx.project_root,
        host_runtime=host_runtime,
    )
    payload = {
        "schema_version": "2.0",
        "action": "verify-subagent-runtime",
        "status": "PASS" if str(result.get("status")) == "pass" else "BLOCKED",
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0 if payload["status"] == "PASS" else 2)


def run_subagent_delegation_verify(
    *,
    project_root: str,
    version: str,
    feature: str,
) -> DoctorExecutionResult:
    """Verify feature-level subagent delegation readiness."""
    ctx = build_doctor_execution_context(project_root, version=version, include_version_context=False)
    result = run_doctor_handler(
        "runtime.verify.subagent-delegation",
        project_root=ctx.project_root,
        feature=feature,
        version=version,
    )
    payload = {
        "schema_version": "2.0",
        "action": "verify-subagent-delegation",
        "status": "PASS" if str(result.get("status")) == "pass" else "BLOCKED",
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0 if payload["status"] == "PASS" else 2)


def run_runtime_ledger_verify(
    *,
    project_root: str,
    version: str,
    feature: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Verify runtime-ledger determinism and control-plane readiness."""
    ctx = build_doctor_execution_context(project_root, version=version or None, strict=strict)
    result = run_doctor_handler(
        "projection.verify.runtime-ledger",
        project_root=ctx.project_root,
        version=version or None,
        feature=feature or None,
    )
    status = str(result.get("status", "warn")).lower()
    payload = {
        "schema_version": "2.0",
        "action": "verify-runtime-ledger",
        "status": _map_verify_status("fail" if strict and status == "warn" else status),
        "version_context": ctx.version_context or {},
        "version_semantics": (ctx.version_context or {}).get("version_semantics", {}),
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0 if payload["status"] != "BLOCKED" else 2)


def run_runtime_ledger_export(
    *,
    project_root: str,
    label: str,
) -> DoctorExecutionResult:
    """Export runtime-ledger artifacts for backup."""
    ctx = build_doctor_execution_context(project_root, include_version_context=False)
    result = run_doctor_handler(
        "projection.export.runtime-ledger",
        label=label or None,
    )
    payload = {
        "schema_version": "2.0",
        "action": "export-runtime-ledger",
        "status": "PASS",
        "project_root": str(ctx.project_root),
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_runtime_ledger_rebuild(
    *,
    project_root: str,
    version: str,
    feature: str,
) -> DoctorExecutionResult:
    """Rebuild runtime-ledger projection from local truth."""
    ctx = build_doctor_execution_context(project_root, version=version or None)
    result = run_doctor_handler(
        "projection.rebuild.runtime-ledger",
        project_root=ctx.project_root,
        version=version or None,
        feature=feature or None,
    )
    payload = {
        "schema_version": "2.0",
        "action": "rebuild-runtime-ledger",
        "status": _map_verify_status(str(result.get("status", "warn")).lower()),
        "version_context": ctx.version_context or {},
        "version_semantics": (ctx.version_context or {}).get("version_semantics", {}),
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0 if payload["status"] != "BLOCKED" else 2)


def run_delivery_verify(
    *,
    project_root: str,
    version: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Verify execution-layer delivery artifacts for a version."""
    ctx = build_doctor_execution_context(project_root, version=version, strict=strict, include_version_context=False)
    result = run_doctor_handler(
        "delivery.verify.audit",
        project_root=ctx.project_root,
        version=version or None,
        strict=strict,
    )
    resolved_version = resolve_target_version(ctx.project_root, version or None)
    if _semver_tuple(resolved_version) >= (1, 3, 9):
        from beacon.utils.release_scorecard import build_release_scorecard

        release_scorecard = build_release_scorecard(ctx.project_root, version=resolved_version)
        acceptance = release_scorecard.get("acceptance") if isinstance(release_scorecard.get("acceptance"), dict) else {}
        qa_summary = release_scorecard.get("qa") if isinstance(release_scorecard.get("qa"), dict) else {}
        acceptance_feature = str(acceptance.get("feature") or qa_summary.get("feature") or "").strip()
        contract = acceptance_projection_transaction_contract(
            ctx.project_root,
            version=resolved_version,
            feature=acceptance_feature,
        ) if acceptance_feature else {
            "status": "warn",
            "reason_code": "acceptance_feature_missing",
            "details": {},
        }
        checks = result.get("checks") if isinstance(result.get("checks"), list) else []
        checks.append(
            {
                "name": "acceptance_projection_transaction_contract",
                "status": str(contract.get("status") or "warn"),
                "details": contract,
            }
        )
        result["checks"] = checks
        result["status"] = merge_check_statuses(checks, strict=False)
    return _delivery_payload("verify-delivery", result, strict=strict)


def run_config_verify(
    *,
    project_root: str,
    version: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Verify execution config/source metadata artifacts for a version."""
    ctx = build_doctor_execution_context(project_root, version=version, strict=strict, include_version_context=False)
    audit = run_doctor_handler(
        "delivery.verify.audit",
        project_root=ctx.project_root,
        version=version or None,
        strict=strict,
    )
    target_checks = [
        item
        for item in audit.get("checks", [])
        if str(item.get("name")) in {"execution_required_files_present", "execution_config_schema", "execution_source_schema"}
    ]
    worst = merge_check_statuses(target_checks, strict=False)
    merged_check = {
        "name": "verify_config",
        "status": worst,
        "details": {"checks": target_checks},
    }
    payload = build_single_check_payload(
        action="verify-config",
        project_root=ctx.project_root,
        version=version or None,
        strict=strict,
        check=merged_check,
    )
    return DoctorExecutionResult(payload=payload, exit_code=2 if payload.get("status") == "BLOCKED" else 0)


def run_git_alignment_verify(
    *,
    project_root: str,
    version: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Verify execution git-alignment artifact for a version."""
    ctx = build_doctor_execution_context(project_root, version=version, strict=strict, include_version_context=False)
    audit = run_doctor_handler(
        "delivery.verify.audit",
        project_root=ctx.project_root,
        version=version or None,
        strict=strict,
    )
    git_check = next(
        (item for item in audit.get("checks", []) if str(item.get("name")) == "execution_git_alignment_schema"),
        {"name": "execution_git_alignment_schema", "status": "fail", "details": {"missing": True}},
    )
    workflow_check = next(
        (item for item in audit.get("checks", []) if str(item.get("name")) == "execution_git_workflow_contract"),
        {"name": "execution_git_workflow_contract", "status": "pass", "details": {"required": False}},
    )
    alignment_check = next(
        (item for item in audit.get("checks", []) if str(item.get("name")) == "delivery_manifest_git_workflow_alignment"),
        {"name": "delivery_manifest_git_workflow_alignment", "status": "pass", "details": {"branch_mismatches": []}},
    )
    statuses = [str(git_check.get("status", "fail")).lower()]
    for item in (workflow_check, alignment_check):
        statuses.append(str(item.get("status", "pass")).lower())
    merged_status = merge_check_statuses([{"status": status} for status in statuses], strict=False)
    check = {
        "name": "execution_git_alignment_schema",
        "status": merged_status,
        "details": {
            "git_alignment": git_check.get("details", {}),
            "git_workflow_contract": workflow_check.get("details", {}),
            "manifest_alignment": alignment_check.get("details", {}),
        },
    }
    payload = build_single_check_payload(
        action="verify-git-alignment",
        project_root=ctx.project_root,
        version=version or None,
        strict=strict,
        check=check,
    )
    return DoctorExecutionResult(payload=payload, exit_code=2 if payload.get("status") == "BLOCKED" else 0)


def run_package_repair(
    *,
    project_root: str,
    version: str,
    dry_run: bool,
) -> DoctorExecutionResult:
    """Repair a delivery package into the v1.1.5 layered structure."""
    ctx = build_doctor_execution_context(project_root, version=version, dry_run=dry_run, include_version_context=False)
    result = run_doctor_handler(
        "package.repair.v115-delivery",
        project_root=ctx.project_root,
        version=version,
        apply=not dry_run,
    )
    payload = {
        "schema_version": "2.0",
        "action": "repair-package",
        "status": "PASS",
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_package_upgrade(
    *,
    project_root: str,
    version: str,
    dry_run: bool,
) -> DoctorExecutionResult:
    """Upgrade an older Beacon version package cumulatively."""
    ctx = build_doctor_execution_context(project_root, version=version, dry_run=dry_run, include_version_context=False)
    result = run_doctor_handler(
        "package.upgrade.version-package",
        project_root=ctx.project_root,
        version=version,
        apply=not dry_run,
    )
    resolved_version = resolve_target_version(ctx.project_root, version)
    source_arch_status = run_doctor_handler(
        "package.verify.source-architecture-status",
        project_root=ctx.project_root,
        version=resolved_version,
    )
    payload = {
        "schema_version": "2.0",
        "action": "upgrade-package",
        "status": "PASS",
        "result": result,
        "source_architecture_status": source_arch_status,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_workflow_memory_sync(
    *,
    project_root: str,
    version: str,
    feature: str,
    run_id: str,
) -> DoctorExecutionResult:
    """Backfill workflow-memory surfaces for a completed run."""
    ctx = build_doctor_execution_context(project_root, version=version, include_version_context=False)
    result = backfill_workflow_memory(
        ctx.project_root,
        version=version,
        feature=feature,
        run_id=run_id,
    )
    payload = {
        "schema_version": "2.0",
        "action": "sync-workflow-memory",
        "status": "PASS",
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_launcher_setup(
    *,
    bin_dir: str,
    launcher_source: str,
    force: bool,
    dry_run: bool,
) -> DoctorExecutionResult:
    """Install doctor-managed launchers."""
    resolved_bin_dir = resolve_bin_dir(bin_dir).resolve()
    source = resolve_launcher_source_path(launcher_source)
    result = run_doctor_handler(
        "launcher.setup.install",
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
    return DoctorExecutionResult(payload=payload, exit_code=2 if status == "BLOCKED" else 0)


def run_launcher_uninstall(
    *,
    bin_dir: str,
    force: bool,
    dry_run: bool,
) -> DoctorExecutionResult:
    """Uninstall doctor-managed launchers."""
    resolved_bin_dir = resolve_bin_dir(bin_dir).resolve()
    result = run_doctor_handler(
        "launcher.uninstall.remove",
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
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_quiet_worktree(
    *,
    project_root: str,
    mode: str,
) -> DoctorExecutionResult:
    """Manage local skip-worktree and exclude quieting."""
    ctx = build_doctor_execution_context(project_root, include_version_context=False)
    normalized = mode.strip().lower()
    try:
        result = run_doctor_handler(
            "host.quiet-worktree.manage",
            project_root=ctx.project_root,
            mode=normalized,
        )
    except (ValueError, RuntimeError) as exc:
        payload = {
            "schema_version": "2.0",
            "action": "quiet-worktree",
            "status": "BLOCKED",
            "mode": normalized,
            "result": {
                "project_root": str(ctx.project_root.resolve()),
                "error": str(exc),
            },
        }
        return DoctorExecutionResult(payload=payload, exit_code=2)

    payload = {
        "schema_version": "2.0",
        "action": "quiet-worktree",
        "status": "PASS",
        "mode": normalized,
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_codex_hud_hook_setup(
    *,
    project_root: str,
    version: str,
    events: str,
    apply: bool,
) -> DoctorExecutionResult:
    """Generate or apply Codex fixed HUD hook wiring."""
    ctx = build_doctor_execution_context(project_root, version=version, include_version_context=False)
    resolved_version = resolve_target_version(ctx.project_root, version)
    result = run_doctor_handler(
        "host.setup.codex-hud-hook",
        project_root=ctx.project_root,
        version=resolved_version,
        apply=apply,
        events=events,
    )
    payload = {
        "schema_version": "2.0",
        "action": "setup-codex-hud-hook",
        "status": "PASS",
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_codex_hud_hook_verify(
    *,
    project_root: str,
    version: str,
    events: str,
) -> DoctorExecutionResult:
    """Verify doctor-managed Codex HUD hook wiring."""
    ctx = build_doctor_execution_context(project_root, version=version, include_version_context=False)
    resolved_version = resolve_target_version(ctx.project_root, version)
    result = run_doctor_handler(
        "host.verify.codex-hud-hook",
        project_root=ctx.project_root,
        version=resolved_version,
        events=events,
    )
    payload = {
        "schema_version": "2.0",
        "action": "verify-codex-hud-hook",
        "status": (
            "PASS"
            if result.get("status") == "pass"
            else "WARN"
            if result.get("status") == "warn"
            else "BLOCKED"
        ),
        "result": result,
    }
    exit_code = 0 if payload["status"] in {"PASS", "WARN"} else 2
    return DoctorExecutionResult(payload=payload, exit_code=exit_code)


def run_agent_surface_setup(
    *,
    project_root: str,
    version: str,
    agent: str,
    dry_run: bool,
    force: bool,
) -> DoctorExecutionResult:
    """Materialize project-local Beacon agent surface files."""
    ctx = build_doctor_execution_context(project_root, version=version or None, dry_run=dry_run)
    version_context = ctx.version_context or {}
    docs_version = str(version_context.get("docs_version", "") or ctx.runtime_version)
    result = run_doctor_handler(
        "host.setup.agent-surface",
        project_root=ctx.project_root,
        agent=agent,
        runtime_version=ctx.runtime_version,
        docs_version=docs_version,
        dry_run=dry_run,
        force=force,
    )
    payload = {
        "schema_version": "2.0",
        "action": "setup-agent-surface",
        "status": "PASS",
        "runtime_version": ctx.runtime_version,
        "docs_version": docs_version,
        "version_context": version_context,
        "version_semantics": version_context.get("version_semantics", {}),
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_agent_surface_verify(
    *,
    project_root: str,
    version: str,
    agent: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Verify project-local Beacon agent surface files."""
    ctx = build_doctor_execution_context(project_root, version=version or None, strict=strict)
    result = run_doctor_handler(
        "host.verify.agent-surface",
        project_root=ctx.project_root,
        agent=agent,
        runtime_version=ctx.runtime_version,
        strict=strict,
    )
    payload = {
        "schema_version": "2.0",
        "action": "verify-agent-surface",
        "status": _map_verify_status(str(result.get("status", "warn")).lower()),
        "runtime_version": ctx.runtime_version,
        "docs_version": str((ctx.version_context or {}).get("docs_version", "") or ctx.runtime_version),
        "version_context": ctx.version_context or {},
        "version_semantics": (ctx.version_context or {}).get("version_semantics", {}),
        "result": result,
    }
    if strict and payload["status"] == "WARN":
        payload["status"] = "BLOCKED"
    return DoctorExecutionResult(payload=payload, exit_code=0 if payload["status"] != "BLOCKED" else 2)


def run_version_surfaces_sync(
    *,
    project_root: str,
    dry_run: bool,
) -> DoctorExecutionResult:
    """Sync Beacon self-repo version surfaces from canonical version truth."""
    ctx = build_doctor_execution_context(project_root, dry_run=dry_run)
    result = run_doctor_handler(
        "host.sync.version-surfaces",
        project_root=ctx.project_root,
        dry_run=dry_run,
    )
    payload = {
        "schema_version": "2.0",
        "action": "sync-version-surfaces",
        "status": "PASS",
        "runtime_version": str(result.get("manifest", {}).get("runtime_version", "") or ctx.runtime_version),
        "docs_version": str(result.get("manifest", {}).get("docs_default_line", "") or ""),
        "version_context": ctx.version_context or {},
        "version_semantics": (ctx.version_context or {}).get("version_semantics", {}),
        "result": result,
    }
    return DoctorExecutionResult(payload=payload, exit_code=0)


def run_version_surfaces_verify(
    *,
    project_root: str,
    strict: bool,
) -> DoctorExecutionResult:
    """Verify Beacon self-repo version surfaces against canonical version truth."""
    ctx = build_doctor_execution_context(project_root, strict=strict)
    result = run_doctor_handler(
        "host.verify.version-surfaces",
        project_root=ctx.project_root,
        strict=strict,
    )
    payload = {
        "schema_version": "2.0",
        "action": "verify-version-surfaces",
        "status": _map_verify_status(str(result.get("status", "warn")).lower()),
        "runtime_version": str(result.get("manifest", {}).get("runtime_version", "") or ctx.runtime_version),
        "docs_version": str(result.get("manifest", {}).get("docs_default_line", "") or ""),
        "version_context": ctx.version_context or {},
        "version_semantics": (ctx.version_context or {}).get("version_semantics", {}),
        "result": result,
    }
    if strict and payload["status"] == "WARN":
        payload["status"] = "BLOCKED"
    return DoctorExecutionResult(payload=payload, exit_code=0 if payload["status"] != "BLOCKED" else 2)


def run_doctor_fix_flow(project_root: str) -> None:
    """Apply the existing doctor --fix composite flow via doctor orchestration."""
    root = resolve_doctor_project_root(project_root)
    if not root.exists():
        return
    (root / ".beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "skills").mkdir(parents=True, exist_ok=True)

    run_context_setup(
        project_root=str(root),
        dry_run=False,
        force=False,
        sync_materials=False,
        feature="",
        all_features=True,
        overwrite_test_doc=False,
        with_claude=True,
        with_agents=True,
        with_gitignore=True,
    )
    run_package_upgrade(
        project_root=str(root),
        version="latest-docs",
        dry_run=False,
    )
