"""Governed registry for legacy, fallback, compatibility, and deprecated surfaces.

The registry is deliberately read-only governance data for v1.4.11. It does
not change runtime behavior; later retirement features can consume it when
they need explicit admission or default-policy changes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_REGISTRY_FIELDS = (
    "compat_id",
    "surface",
    "owner",
    "reason",
    "introduced_before",
    "allowed_version_range",
    "default_behavior",
    "current_replacement",
    "retirement_route",
    "evidence_required",
)

VALID_CLASSIFICATIONS = {
    "current_compatible",
    "deprecated",
    "explicit_admission_only",
    "historical",
    "internal",
}

COMPATIBILITY_REGISTRY: tuple[dict[str, Any], ...] = (
    {
        "compat_id": "command-catalog-compat-deprecated-aliases",
        "surface": "command",
        "owner": "compatibility-registry",
        "reason": "Keep older command names discoverable while the current mainline remains compact.",
        "introduced_before": "v1.4.11",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "hidden_callable",
        "current_replacement": "current/support command surfaces in beacon.command_catalog",
        "retirement_route": "command-catalog-validation-then-explicit-retirement-feature",
        "evidence_required": ["catalog-coverage-test", "help-snapshot-test"],
        "classification": "deprecated",
        "command_aliases": ("think", "workflow", "gate", "verify", "auto-test", "prompt", "save", "work"),
    },
    {
        "compat_id": "cli-factory-hidden-compat-registrations",
        "surface": "command",
        "owner": "command-catalog",
        "reason": "Register hidden compatibility commands without promoting them as default next routes.",
        "introduced_before": "v1.4.11",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "hidden_callable",
        "current_replacement": "layered command catalog and explicit advanced/labs planes",
        "retirement_route": "compatibility-registry-controlled-command-registration",
        "evidence_required": ["cli-command-registration-test", "compat-registry-coverage-test"],
        "classification": "current_compatible",
    },
    {
        "compat_id": "implement-legacy-cli-loader",
        "surface": "implement",
        "owner": "implement-package-migration",
        "reason": "Keep public beacon implement commands working while package migration is incomplete.",
        "introduced_before": "v1.4.11",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "enabled_internal_bridge",
        "current_replacement": "beacon.commands.implement package command modules",
        "retirement_route": "implement-package-legacy-loader-retirement-contract",
        "evidence_required": ["implement-cli-smoke-test", "legacy-loader-static-scan"],
        "classification": "internal",
    },
    {
        "compat_id": "qa-auto-test-status-legacy-mirror",
        "surface": "qa",
        "owner": "qa-legacy-mirror-policy",
        "reason": "Preserve historical auto-test status mirror while canonical QA status is adopted.",
        "introduced_before": "v1.1.8",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "enabled_legacy_mirror",
        "current_replacement": ".beacon/qa/status.json",
        "retirement_route": "qa-prd-legacy-mirror-retirement-contract",
        "evidence_required": ["canonical-qa-status-test", "legacy-only-qa-blocking-test"],
        "classification": "historical",
    },
    {
        "compat_id": "prd-legacy-machine-mirror",
        "surface": "prd",
        "owner": "prd-legacy-mirror-policy",
        "reason": "Keep legacy PRD mirror drift visible while Markdown-first truth and projections converge.",
        "introduced_before": "v1.3.0",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "audited_legacy_mirror",
        "current_replacement": "docs/beacon/<version>/prd/*.md plus .machine/prd projection",
        "retirement_route": "qa-prd-legacy-mirror-retirement-contract",
        "evidence_required": ["material-audit-projection-vs-compat-test"],
        "classification": "historical",
    },
    {
        "compat_id": "prototype-legacy-wireframe-source",
        "surface": "prototype",
        "owner": "prototype-legacy-inspector",
        "reason": "Keep older single-file prototype artifacts inspectable without treating them as current closure.",
        "introduced_before": "v1.4.8",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "read_only_legacy_inspection",
        "current_replacement": "prototype design-result adapter binding",
        "retirement_route": "prototype-legacy-inspector-split",
        "evidence_required": ["prototype-status-compat-test", "release-gate-boundary-test"],
        "classification": "historical",
    },
    {
        "compat_id": "browser-fallback-command-name",
        "surface": "browser",
        "owner": "browser-adapter-boundary",
        "reason": "Preserve explicit deterministic project command execution while browser runtimes are optional.",
        "introduced_before": "v1.3.2",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "explicit_command_only",
        "current_replacement": "deterministic_command / explicit_project_command evidence naming",
        "retirement_route": "browser-fallback-rename-contract",
        "evidence_required": ["browser-evidence-snapshot-test", "compat-alias-test"],
        "classification": "explicit_admission_only",
    },
    {
        "compat_id": "memory-legacy-projection",
        "surface": "memory",
        "owner": "memory-migration-boundary",
        "reason": "Migrate older memory rows into memory-v1 when the v1 projection is absent.",
        "introduced_before": "v1.4.3",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "migration_when_v1_absent",
        "current_replacement": "memory-v1 evidence-bound projection",
        "retirement_route": "memory-intent-historical-migration-boundary",
        "evidence_required": ["memory-migration-transaction-test"],
        "classification": "historical",
    },
    {
        "compat_id": "intent-legacy-router",
        "surface": "intent",
        "owner": "intent-compat-boundary",
        "reason": "Preserve the legacy public intent API for older imports and tests.",
        "introduced_before": "v1.1.0",
        "allowed_version_range": "<=v1.4.x",
        "default_behavior": "backward_compatible_facade",
        "current_replacement": "governed intent routing and support-surface routing",
        "retirement_route": "memory-intent-historical-migration-boundary",
        "evidence_required": ["intent-current-route-test", "legacy-router-admission-test"],
        "classification": "current_compatible",
    },
)


def registry_by_id(entries: tuple[dict[str, Any], ...] | list[dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    source = COMPATIBILITY_REGISTRY if entries is None else entries
    return {
        str(item.get("compat_id") or "").strip(): dict(item)
        for item in source
        if isinstance(item, dict) and str(item.get("compat_id") or "").strip()
    }


def command_aliases_from_registry(entries: tuple[dict[str, Any], ...] | list[dict[str, Any]] | None = None) -> set[str]:
    aliases: set[str] = set()
    source = COMPATIBILITY_REGISTRY if entries is None else entries
    for item in source:
        if not isinstance(item, dict):
            continue
        for alias in item.get("command_aliases") or ():
            text = str(alias or "").strip()
            if text:
                aliases.add(text)
    return aliases


def required_registry_ids_from_baseline(project_root: Path, *, version: str) -> set[str]:
    path = project_root / "docs" / "beacon" / version / ".machine" / "execution" / "legacy-burden-baseline-inventory.json"
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return set()
    items = payload.get("items") if isinstance(payload.get("items"), list) else []
    required: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        compat_id = str(item.get("compat_id") or "").strip()
        surface = str(item.get("surface_category") or "").strip()
        phase = str(item.get("proposed_phase") or "").strip()
        if compat_id and surface != "authority" and phase != "phase-1":
            required.add(compat_id)
    return required


def _entry_issues(item: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    compat_id = str(item.get("compat_id") or "<missing>")
    for field in REQUIRED_REGISTRY_FIELDS:
        value = item.get(field)
        if value is None or value == "" or value == []:
            issues.append(f"{compat_id}:missing_field:{field}")
    evidence = item.get("evidence_required")
    if not isinstance(evidence, (list, tuple)) or not all(str(x).strip() for x in evidence):
        issues.append(f"{compat_id}:invalid_evidence_required")
    classification = str(item.get("classification") or "").strip()
    if classification not in VALID_CLASSIFICATIONS:
        issues.append(f"{compat_id}:invalid_classification:{classification or '<missing>'}")
    return issues


def validate_compatibility_registry(
    *,
    entries: tuple[dict[str, Any], ...] | list[dict[str, Any]] | None = None,
    required_ids: set[str] | None = None,
) -> dict[str, Any]:
    source = list(COMPATIBILITY_REGISTRY if entries is None else entries)
    ids = registry_by_id(source)
    issues: list[str] = []
    if len(ids) != len(source):
        issues.append("duplicate_or_missing_compat_id")
    for item in source:
        if isinstance(item, dict):
            issues.extend(_entry_issues(item))
        else:
            issues.append("invalid_entry_type")
    missing = sorted((required_ids or set()) - set(ids))
    issues.extend([f"missing_required_registry_entry:{compat_id}" for compat_id in missing])
    return {
        "schema_version": "1.0",
        "status": "pass" if not issues else "blocked",
        "blocked": bool(issues),
        "entry_count": len(source),
        "required_count": len(required_ids or set()),
        "missing_required_ids": missing,
        "issues": issues,
    }
