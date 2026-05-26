"""Baseline inventory for legacy/fallback/compatibility surfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file
from beacon.utils.authority import classify_artifact_role
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import resolve_target_version


INVENTORY_SCHEMA_VERSION = "1.0"


def baseline_inventory_json_path(project_root: Path, version: str) -> Path:
    return machine_execution_file(project_root, resolve_target_version(project_root, version), "legacy-burden-baseline-inventory.json")


def baseline_inventory_markdown_path(project_root: Path, version: str) -> Path:
    return human_execution_file(project_root, resolve_target_version(project_root, version), "legacy-burden-baseline-inventory.md")


def _exists(project_root: Path, relative_path: str) -> bool:
    return (project_root / relative_path).exists()


def _row(
    *,
    project_root: Path,
    compat_id: str,
    source_file: str,
    symbol: str,
    surface_category: str,
    current_behavior: str,
    risk: str,
    proposed_owner: str,
    proposed_phase: str,
    required_evidence: list[str],
) -> dict[str, Any]:
    return {
        "compat_id": compat_id,
        "source_file": source_file,
        "symbol": symbol,
        "surface_category": surface_category,
        "artifact_role": classify_artifact_role(source_file),
        "current_behavior": current_behavior,
        "risk": risk,
        "proposed_owner": proposed_owner,
        "proposed_phase": proposed_phase,
        "required_evidence": required_evidence,
        "exists": _exists(project_root, source_file),
        "behavior_change_allowed_in_this_slice": False,
    }


def build_legacy_burden_baseline_inventory(project_root: Path, *, version: str = "auto") -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    rows = [
        _row(
            project_root=project_root,
            compat_id="authority-artifact-language-policy",
            source_file="beacon/artifact-language-policy.json",
            symbol="artifact_classes.human_mirrors_of_machine_contracts",
            surface_category="authority",
            current_behavior="Defines artifact language and mirror wording policy.",
            risk="low",
            proposed_owner="authority-vocabulary",
            proposed_phase="phase-1",
            required_evidence=["forbidden-wording-test", "artifact-language-render-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="authority-artifact-language-renderer",
            source_file="beacon/utils/artifact_language.py",
            symbol="render_artifact_language_policy_markdown",
            surface_category="authority",
            current_behavior="Renders the human-readable artifact language policy mirror.",
            risk="low",
            proposed_owner="authority-vocabulary",
            proposed_phase="phase-1",
            required_evidence=["render-snapshot-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="command-catalog-compat-deprecated-aliases",
            source_file="beacon/command_catalog.py",
            symbol="COMPAT_COMMANDS / DEPRECATED_COMMANDS",
            surface_category="command",
            current_behavior="Keeps compatibility and deprecated command names discoverable outside the default user surface.",
            risk="medium",
            proposed_owner="compatibility-registry",
            proposed_phase="phase-2",
            required_evidence=["catalog-coverage-test", "help-snapshot-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="cli-factory-hidden-compat-registrations",
            source_file="beacon/cli_factory.py",
            symbol="build_app",
            surface_category="command",
            current_behavior="Registers hidden compatibility commands and deprecated aliases while keeping the mainline compact.",
            risk="medium",
            proposed_owner="command-catalog",
            proposed_phase="phase-3",
            required_evidence=["cli-command-registration-test", "compat-registry-coverage-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="implement-legacy-cli-loader",
            source_file="beacon/commands/implement/__init__.py",
            symbol="app / run_implement_stage package exports",
            surface_category="implement",
            current_behavior="Retains compatibility registry traceability after the implement package took ownership of the public app without the legacy dynamic loader.",
            risk="high",
            proposed_owner="implement-package-migration",
            proposed_phase="phase-6",
            required_evidence=["implement-cli-smoke-test", "legacy-loader-static-scan"],
        ),
        _row(
            project_root=project_root,
            compat_id="qa-auto-test-status-legacy-mirror",
            source_file="beacon/utils/qa_runtime.py",
            symbol="write_qa_status / load_qa_status",
            surface_category="qa",
            current_behavior="Writes canonical QA status and legacy auto-test status mirror; reads canonical first and legacy second.",
            risk="high",
            proposed_owner="qa-legacy-mirror-policy",
            proposed_phase="phase-4",
            required_evidence=["canonical-qa-status-test", "legacy-only-qa-blocking-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="prd-legacy-machine-mirror",
            source_file="beacon/utils/material_audit.py",
            symbol="legacy_machine_mirror_sync",
            surface_category="prd",
            current_behavior="Audits legacy PRD mirror drift alongside Markdown-first material audit findings.",
            risk="high",
            proposed_owner="prd-legacy-mirror-policy",
            proposed_phase="phase-5",
            required_evidence=["material-audit-projection-vs-compat-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="prototype-legacy-wireframe-source",
            source_file="beacon/utils/prototype_utils.py",
            symbol="evaluate_prototype_status",
            surface_category="prototype",
            current_behavior="Reports legacy single-file prototype source when current prototype bundle is missing.",
            risk="high",
            proposed_owner="prototype-legacy-inspector",
            proposed_phase="phase-7",
            required_evidence=["prototype-status-compat-test", "release-gate-boundary-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="browser-fallback-command-name",
            source_file="beacon/adapters/browser_runner_common.py",
            symbol="write_runner_artifacts",
            surface_category="browser",
            current_behavior="Records fallback command execution mode for browser runner adapters.",
            risk="medium",
            proposed_owner="browser-adapter-boundary",
            proposed_phase="phase-8",
            required_evidence=["browser-evidence-snapshot-test", "compat-alias-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="memory-legacy-projection",
            source_file="beacon/utils/memory.py",
            symbol="_migrate_legacy_to_v1_if_needed",
            surface_category="memory",
            current_behavior="Migrates older memory files into memory-v1 when the v1 file is absent.",
            risk="medium",
            proposed_owner="memory-migration-boundary",
            proposed_phase="phase-9",
            required_evidence=["memory-migration-transaction-test"],
        ),
        _row(
            project_root=project_root,
            compat_id="intent-legacy-router",
            source_file="beacon/utils/intent_router.py",
            symbol="detect_intent / route_intent",
            surface_category="intent",
            current_behavior="Preserves backward-compatible intent detection and routing facade for older importers.",
            risk="medium",
            proposed_owner="intent-compat-boundary",
            proposed_phase="phase-9",
            required_evidence=["intent-current-route-test", "legacy-router-admission-test"],
        ),
    ]
    return {
        "schema_version": INVENTORY_SCHEMA_VERSION,
        "version": resolved_version,
        "feature": "authority-vocabulary-and-baseline-inventory-contract",
        "status": "inventory_generated",
        "behavior_change_allowed": False,
        "generated_at": now_iso(),
        "required_fields": [
            "source_file",
            "symbol",
            "surface_category",
            "current_behavior",
            "risk",
            "proposed_owner",
            "proposed_phase",
            "required_evidence",
        ],
        "summary": {
            "row_count": len(rows),
            "missing_source_files": [row["source_file"] for row in rows if not row["exists"]],
            "high_risk_count": sum(1 for row in rows if row["risk"] == "high"),
        },
        "items": rows,
    }


def render_legacy_burden_baseline_inventory_markdown(payload: dict[str, Any]) -> str:
    rows = payload.get("items") if isinstance(payload.get("items"), list) else []
    lines = [
        "# Legacy Burden Baseline Inventory",
        "",
        f"- version: `{payload.get('version', '')}`",
        f"- feature: `{payload.get('feature', '')}`",
        f"- status: `{payload.get('status', '')}`",
        f"- behavior_change_allowed: `{bool(payload.get('behavior_change_allowed', False))}`",
        f"- generated_at: `{payload.get('generated_at', '')}`",
        "",
        "## Summary",
        "",
        f"- row_count: `{(payload.get('summary') or {}).get('row_count', 0) if isinstance(payload.get('summary'), dict) else 0}`",
        f"- high_risk_count: `{(payload.get('summary') or {}).get('high_risk_count', 0) if isinstance(payload.get('summary'), dict) else 0}`",
        "",
        "## Inventory",
        "",
        "| compat_id | source_file | symbol | category | role | risk | phase | behavior | evidence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        if not isinstance(row, dict):
            continue
        evidence = ", ".join(str(item) for item in row.get("required_evidence", []))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row.get('compat_id', '')}`",
                    f"`{row.get('source_file', '')}`",
                    f"`{row.get('symbol', '')}`",
                    f"`{row.get('surface_category', '')}`",
                    f"`{row.get('artifact_role', '')}`",
                    f"`{row.get('risk', '')}`",
                    f"`{row.get('proposed_phase', '')}`",
                    str(row.get("current_behavior", "")).replace("|", "/"),
                    evidence.replace("|", "/"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This inventory is a pre-change audit artifact.",
            "- It does not retire, disable, or alter runtime compatibility behavior.",
            "- Later compatibility registry and behavior retirement work must cite this inventory.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_legacy_burden_baseline_inventory(project_root: Path, *, version: str = "auto") -> dict[str, Any]:
    payload = build_legacy_burden_baseline_inventory(project_root, version=version)
    json_path = baseline_inventory_json_path(project_root, str(payload["version"]))
    markdown_path = baseline_inventory_markdown_path(project_root, str(payload["version"]))
    write_json(json_path, payload)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_legacy_burden_baseline_inventory_markdown(payload), encoding="utf-8")
    payload["artifact_paths"] = {
        "json": str(json_path.relative_to(project_root)),
        "markdown": str(markdown_path.relative_to(project_root)),
    }
    return payload
