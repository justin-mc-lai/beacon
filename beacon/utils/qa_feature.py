"""Feature-aware QA planning and writeback helpers for Beacon v1.1.10."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from beacon.commands.auto_test import LAYER_NAMES
from beacon.utils.artifact_paths import qa_feature_evidence_contract_candidates, qa_matrix_candidates
from beacon.utils.artifact_update_obligations import blocking_obligations, load_artifact_update_obligations
from beacon.utils.qa9 import QA9_TYPES, default_command_for_qa_type, normalize_qa_type
from beacon.utils.qa_acceptance import BROWSER_QA_LAYER, build_qa_acceptance_capability_summary
from beacon.utils.qa_precision import (
    DEFAULT_AUTO_ACCEPT_THRESHOLD,
    DEFAULT_REVIEW_THRESHOLD,
    load_qa_calibration_model,
    write_feature_qa_ac_closure,
    write_feature_qa_scorecard,
)
from beacon.utils.qa_attribution import summarize_qa_attributions
from beacon.utils.qa_evo_deep import build_deep_absorption_status
from beacon.utils.reconciliation import detect_implementation_first_reconciliation_needed
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_scenarios import (
    _entry_browser_required,
    expand_story_scenarios,
    scenario_map_path as docs_story_scenario_map_path,
)
from beacon.utils.story_state import feature_slug, load_story_state
from beacon.utils.v110_baseline import load_latest_spec_fingerprint
from beacon.utils.versioning import normalize_version, resolve_target_version

FEATURE_QA_SCHEMA = "1.0"
QA_LAYER_SET = set(LAYER_NAMES) | set(QA9_TYPES)
SEMANTIC_QA_TYPE_ALIASES: dict[str, str] = {
    "strategy": "contract",
    "architecture": "contract",
    "overlay": "contract",
    "delivery-plane": "contract",
    "delivery": "integration",
    "recovery": "integration",
    "completion": "smoke",
    "qa": "integration",
    "traceability": "contract",
    "writeback": "integration",
    "learning": "regression",
    "boundary": "exception",
    "workflow": "contract",
    "governance": "contract",
    "scope": "contract",
    "skill-docs": "contract",
    "skill-structure": "contract",
    "operator-entry": "functional",
    "anti-drift-ports": "contract",
    "baseline-contract": "contract",
    "qa-feature-entry": "integration",
    "qa-story-sequence": "integration",
    "qa-evolve": "regression",
    "per-item-writeback": "integration",
    "evolution": "regression",
}
PLACEHOLDER_COMMAND_TOKENS = (
    "implementation-pending",
    "design-review",
    "placeholder",
    "tbd",
)
PLACEHOLDER_COMMAND_VALUES = {
    "",
    "-",
    "n/a",
    "na",
    "none",
    "todo",
    "tbd",
    "placeholder",
    "implementation-pending",
    "design-review",
}


def _real_project_qa_taxonomy_supported(version: str | None) -> bool:
    normalized = normalize_version(version) or ""
    if not normalized.startswith("v"):
        return False
    try:
        major, minor, patch = [int(part) for part in normalized[1:].split(".")]
    except Exception:  # noqa: BLE001
        return False
    return (major, minor, patch) >= (1, 4, 9)


def _implementation_evidence_gate(
    marker: dict[str, Any],
    *,
    version: str,
    archive_payload: dict[str, Any],
) -> dict[str, Any]:
    if not _real_project_qa_taxonomy_supported(version):
        return {"status": "not_applicable", "blocked": False, "reason_codes": []}
    run_id = str(marker.get("run_id") or archive_payload.get("run_id") or "").strip()
    if not run_id:
        return {
            "status": "blocked",
            "blocked": True,
            "reason_codes": ["evidence_binding_missing"],
            "missing_fields": ["run_id"],
        }
    missing_fields: list[str] = []
    if not str(marker.get("summary_ref") or "").strip() and not archive_payload:
        missing_fields.append("summary_ref")
    if not list(marker.get("changed_files") or []) and not list(marker.get("service_dirs") or []) and not list(archive_payload.get("changed_files") or []):
        missing_fields.append("changed_files_or_service_dirs")
    if bool(marker.get("imported")) and not str(marker.get("approved_by") or "").strip():
        missing_fields.append("approved_by")
    return {
        "status": "blocked" if missing_fields else "pass",
        "blocked": bool(missing_fields),
        "reason_codes": ["evidence_binding_missing"] if missing_fields else [],
        "missing_fields": missing_fields,
        "imported": bool(marker.get("imported")),
        "summary_ref": str(marker.get("summary_ref") or "").strip(),
        "source_refs": [str(item).strip() for item in (marker.get("source_refs") or []) if str(item).strip()],
    }


def _matrix_projection_gate(source_matrix: dict[str, Any], *, version: str) -> dict[str, Any]:
    if not _real_project_qa_taxonomy_supported(version):
        return {"status": "not_applicable", "blocked": False, "reason_codes": []}
    contract = source_matrix.get("markdown_matrix_contract") if isinstance(source_matrix.get("markdown_matrix_contract"), dict) else {}
    if str(contract.get("truth_mode") or "").strip() != "markdown":
        return {
            "status": "blocked",
            "blocked": True,
            "reason_codes": ["truth_projection_gap"],
            "contract": contract,
        }
    return {
        "status": "pass",
        "blocked": False,
        "reason_codes": [],
        "contract": contract,
    }


def _qa_outcome_taxonomy(reason_codes: list[str], *, plan_status: str) -> dict[str, Any]:
    codes = {str(item).strip() for item in reason_codes if str(item).strip()}
    blocker_codes = {
        "evidence_binding_missing",
        "truth_projection_gap",
        "runner_admission_blocked",
        "environment_blocked",
        "auth_session_blocked",
        "coverage_gap",
        "project_profile_gate_blocked",
        "auto_test_invocation_failed",
    }
    if codes & blocker_codes:
        category = "admission_blocker"
    elif str(plan_status or "").strip() in {"failed"}:
        category = "product_or_test_failure"
    else:
        category = "pending_or_ready"
    return {
        "category": category,
        "reason_codes": sorted(codes),
        "stable_taxonomy": [
            "product_failed",
            "test_failed",
            "runner_admission_blocked",
            "environment_blocked",
            "auth_session_blocked",
            "evidence_binding_missing",
            "coverage_gap",
            "truth_projection_gap",
        ],
    }


def _classify_qa_failure_item(item: dict[str, Any]) -> str:
    reason_code = str(item.get("reason_code") or "").strip().lower()
    command_text = str(item.get("command") or "").lower()
    stderr_text = str(item.get("stderr") or "").lower()
    stdout_text = str(item.get("stdout") or "").lower()
    evidence_text = " ".join(str(ref) for ref in (item.get("evidence_ref") or []) if str(ref).strip()).lower()
    text = " ".join(
        [
            reason_code,
            command_text,
            stderr_text,
            stdout_text,
            evidence_text,
        ]
    )
    if any(token in text for token in ("docker", "testcontainers", "connection refused", "econnrefused", "timeout", "mysql", "postgres")):
        return "environment_blocked"
    if any(token in text for token in ("command not found", "script missing", "missing script", "no such file", "qa9_command_missing", "layer_command_missing")):
        return "runner_admission_blocked"
    auth_reason_codes = {
        "auth_session_blocked",
        "auth_session_invalid",
        "auth_session_missing",
        "protected_surface_session_bridge_missing",
        "vercel_sso_redirect_no_session_bridge",
    }
    auth_evidence_text = " ".join([command_text, stderr_text, stdout_text, evidence_text])
    browser_or_http_surface = bool(item.get("browser_required")) or any(
        token in auth_evidence_text
        for token in ("http://", "https://", "playwright", "browser", "vercel", "sso")
    )
    has_auth_failure_evidence = any(
        token in auth_evidence_text
        for token in ("401", "403", "unauthorized", "forbidden", "login", "cookie", "jwt")
    )
    if reason_code in auth_reason_codes or (browser_or_http_surface and has_auth_failure_evidence):
        return "auth_session_blocked"
    if reason_code in {"coverage_gap", "evidence_binding_missing", "truth_projection_gap"}:
        return reason_code
    status = str(item.get("status") or item.get("layer_status") or "").strip().lower()
    if status == "blocked":
        return "runner_admission_blocked"
    if status == "failed":
        return "test_failed"
    return ""


def _qa_runtime_taxonomy(qa_status: dict[str, Any]) -> dict[str, Any]:
    qa9 = qa_status.get("qa9") if isinstance(qa_status.get("qa9"), dict) else {}
    tc_results = qa9.get("tc_results") if isinstance(qa9.get("tc_results"), list) else []
    non_passing_results = [
        item
        for item in tc_results
        if isinstance(item, dict)
        and str(item.get("status") or item.get("layer_status") or "").strip().lower()
        in {"blocked", "failed", "review_required"}
    ]
    classes = sorted(
        {
            classification
            for item in non_passing_results
            for classification in [_classify_qa_failure_item(item)]
            if classification
        }
    )
    if not classes:
        return {"status": "not_applicable", "failure_classes": [], "primary_class": ""}
    blocker_classes = {"environment_blocked", "runner_admission_blocked", "auth_session_blocked"}
    primary = next((item for item in classes if item in blocker_classes), classes[0])
    return {
        "status": "blocked" if primary in blocker_classes else "failed",
        "failure_classes": classes,
        "primary_class": primary,
    }


def feature_qa_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "qa" / "features"


def feature_qa_dir(project_root: Path, *, feature: str) -> Path:
    return feature_qa_root(project_root) / feature_slug(feature)


def feature_qa_plan_path(project_root: Path, *, feature: str) -> Path:
    return feature_qa_dir(project_root, feature=feature) / "plan.json"


def feature_qa_status_path(project_root: Path, *, feature: str) -> Path:
    return feature_qa_dir(project_root, feature=feature) / "status.json"


def feature_qa_matrix_path(project_root: Path, *, feature: str) -> Path:
    return feature_qa_dir(project_root, feature=feature) / "matrix.qa9.json"


def feature_qa_scenario_map_path(project_root: Path, *, feature: str) -> Path:
    return feature_qa_dir(project_root, feature=feature) / "story-scenario-map.json"


def load_feature_qa_status(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(feature_qa_status_path(project_root, feature=feature), {})
    return payload if isinstance(payload, dict) else {}


def write_feature_qa_status(project_root: Path, *, feature: str, payload: dict[str, Any]) -> Path:
    path = feature_qa_status_path(project_root, feature=feature)
    write_json(path, payload)
    return path


def _load_json(path: Path) -> dict[str, Any]:
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def _load_source_matrix(project_root: Path, *, version: str, feature: str, story: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    slug = feature_slug(feature)
    normalized_version = normalize_version(version) or ""
    if _real_project_qa_taxonomy_supported(normalized_version):
        for candidate in qa_matrix_candidates(project_root, version, slug, "ac-test-matrix"):
            if candidate.exists():
                payload = _load_json(candidate)
                if isinstance(payload.get("entries"), list):
                    return candidate, payload
    if normalized_version.startswith("v"):
        try:
            major, minor, patch = [int(part) for part in normalized_version[1:].split(".")]
        except Exception:  # noqa: BLE001
            major, minor, patch = (0, 0, 0)
        if (major, minor, patch) >= (1, 2, 0):
            for candidate in qa_matrix_candidates(project_root, version, slug, "qa9-matrix"):
                if candidate.exists():
                    payload = _load_json(candidate)
                    if isinstance(payload.get("entries"), list):
                        return candidate, payload
    for candidate in qa_matrix_candidates(project_root, version, slug, "ac-test-matrix"):
        if candidate.exists():
            payload = _load_json(candidate)
            if isinstance(payload.get("entries"), list):
                return candidate, payload
    entries: list[dict[str, Any]] = []
    ac_items = [item for item in story.get("items", []) if isinstance(item, dict) and str(item.get("kind")) == "ac"]
    for index, item in enumerate(ac_items, start=1):
        ac_id = str(item.get("id") or f"AC-{index:03d}")
        entries.append(
            {
                "ac_id": ac_id,
                "tc_id": f"TC-{index:03d}",
                "layer": "contract",
                "command": "",
                "assertion": str(item.get("text") or item.get("theme") or "verify acceptance criteria"),
                "status": "planned",
            }
        )
    synthetic = {
        "schema_version": FEATURE_QA_SCHEMA,
        "feature": slug,
        "feature_slug": slug,
        "version": version,
        "generated_at": now_iso(),
        "entries": entries,
        "synthetic": True,
    }
    return qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")[0], synthetic


def _load_feature_evidence_contract(project_root: Path, *, version: str, feature: str) -> tuple[Path | None, dict[str, Any]]:
    slug = feature_slug(feature)
    for candidate in qa_feature_evidence_contract_candidates(project_root, version, slug):
        if candidate.exists():
            payload = _load_json(candidate)
            if isinstance(payload, dict):
                return candidate, payload
    return None, {}


def _normalize_entry_command(value: str) -> str:
    command = str(value or "").strip()
    lowered = command.lower()
    if not command:
        return ""
    stripped = lowered.strip("`'\" ")
    if stripped in PLACEHOLDER_COMMAND_VALUES:
        return ""
    if any(stripped.startswith(f"{token}:") for token in PLACEHOLDER_COMMAND_TOKENS):
        return ""
    return command


def _map_entry_qa_type(layer: str) -> str:
    normalized = normalize_qa_type(layer)
    if normalized in QA_LAYER_SET:
        return normalized
    alias = SEMANTIC_QA_TYPE_ALIASES.get(normalized)
    if alias:
        return alias
    return "contract"


def _derived_evidence_path(*, feature: str, tc_id: str) -> str:
    return f".beacon/evidence/qa-feature/{feature_slug(feature)}/{tc_id.lower()}/__RUN_ID__.json"


def _resolve_entry_command(*, qa_type: str, command: str, ui_runner: str) -> str:
    normalized = _normalize_entry_command(command)
    if not normalized:
        return default_command_for_qa_type(qa_type, ui_runner=ui_runner)
    if "beacon.adapters.browser_use_runner" in normalized and qa_type in {"functional", "compatibility"} and ui_runner != "browser-use":
        return default_command_for_qa_type(qa_type, ui_runner=ui_runner)
    return normalized


def _apply_feature_evidence_contract(
    entries: list[dict[str, Any]],
    *,
    contract: dict[str, Any],
    ui_runner: str,
) -> list[dict[str, Any]]:
    overrides_raw = contract.get("tc_overrides") if isinstance(contract.get("tc_overrides"), dict) else {}
    if not overrides_raw:
        return entries
    patched: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        tc_id = str(entry.get("tc_id") or "").strip()
        override = overrides_raw.get(tc_id)
        if not isinstance(override, dict):
            patched.append(entry)
            continue
        item = dict(entry)
        if "layer" in override and str(override.get("layer") or "").strip():
            item["layer"] = str(override.get("layer") or "").strip()
        if "qa_type" in override and str(override.get("qa_type") or "").strip():
            item["qa_type"] = _map_entry_qa_type(str(override.get("qa_type") or "").strip())
        if "browser_required" in override:
            item["browser_required"] = bool(override.get("browser_required"))
        if "replay_required" in override:
            item["replay_required"] = bool(override.get("replay_required"))
        if "exploratory_runner" in override and str(override.get("exploratory_runner") or "").strip():
            item["exploratory_runner"] = str(override.get("exploratory_runner") or "").strip()
        if "deterministic_runner" in override and str(override.get("deterministic_runner") or "").strip():
            item["deterministic_runner"] = str(override.get("deterministic_runner") or "").strip()
        qa_type = str(item.get("qa_type") or item.get("layer") or "contract").strip()
        for key in ("command", "explore_command", "replay_command"):
            if key not in override:
                continue
            value = str(override.get(key) or "").strip()
            if not value:
                item[key] = ""
                continue
            item[key] = _resolve_entry_command(
                qa_type="compatibility" if key == "replay_command" and qa_type == "compatibility" else qa_type,
                command=value,
                ui_runner=ui_runner,
            )
        if "assertion" in override and str(override.get("assertion") or "").strip():
            item["assertion"] = str(override.get("assertion") or "").strip()
        if "target_url" in override and str(override.get("target_url") or "").strip():
            item["target_url"] = str(override.get("target_url") or "").strip()
        patched.append(item)
    return patched


def _derive_entries(feature: str, entries: list[dict[str, Any]], *, ui_runner: str = "playwright") -> list[dict[str, Any]]:
    derived: list[dict[str, Any]] = []
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            continue
        tc_id = str(item.get("tc_id") or f"TC-{index:03d}").strip() or f"TC-{index:03d}"
        ac_id = str(item.get("ac_id") or f"AC-{index:03d}").strip() or f"AC-{index:03d}"
        raw_layer = str(item.get("layer") or item.get("qa_type") or "contract").strip()
        qa_type = _map_entry_qa_type(raw_layer)
        derived.append(
            {
                **item,
                "ac_id": ac_id,
                "tc_id": tc_id,
                "layer": raw_layer or qa_type,
                "qa_type": qa_type,
                "automation": str(item.get("automation") or "auto"),
                "command": _resolve_entry_command(
                    qa_type=qa_type,
                    command=str(item.get("command") or ""),
                    ui_runner=ui_runner,
                ),
                "evidence_path": str(item.get("evidence_path") or _derived_evidence_path(feature=feature, tc_id=tc_id)),
            }
        )
    return derived


def _entries_fingerprint(entries: list[dict[str, Any]]) -> str:
    canonical = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _active_story_items(story: dict[str, Any]) -> list[dict[str, Any]]:
    rows = story.get("items") if isinstance(story.get("items"), list) else []
    return [row for row in rows if isinstance(row, dict)]


def _story_sequence(story: dict[str, Any], entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_ac: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        ac_id = str(entry.get("ac_id") or "").strip()
        if not ac_id:
            continue
        by_ac.setdefault(ac_id, []).append(entry)
    sequence: list[dict[str, Any]] = []
    for item in _active_story_items(story):
        if str(item.get("kind") or "") != "ac":
            continue
        ac_id = str(item.get("id") or "").strip()
        related = by_ac.get(ac_id, [])
        sequence.append(
            {
                "ac_id": ac_id,
                "theme": str(item.get("theme") or "").strip(),
                "text": str(item.get("text") or "").strip(),
                "tc_ids": [str(entry.get("tc_id") or "") for entry in related if str(entry.get("tc_id") or "").strip()],
                "qa_types": sorted({str(entry.get("qa_type") or "") for entry in related if str(entry.get("qa_type") or "").strip()}),
            }
        )
    return sequence


def _build_story_scenario_map(
    project_root: Path,
    *,
    version: str,
    feature: str,
    story_sequence: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    ui_runner: str = "playwright",
) -> dict[str, Any]:
    docs_path = docs_story_scenario_map_path(project_root, version=version, feature=feature)
    if docs_path.exists():
        payload = _load_json(docs_path)
        if isinstance(payload.get("scenarios"), list):
            augmented = _augment_story_scenario_map(
                feature=feature,
                payload=payload,
                story_sequence=story_sequence,
                entries=entries,
                ui_runner=ui_runner,
            )
            if not _scenario_map_needs_regeneration(
                feature=feature,
                payload=augmented,
                story_sequence=story_sequence,
                entries=entries,
            ):
                return augmented
    return expand_story_scenarios(
        feature=feature,
        version=version,
        story_sequence=story_sequence,
        entries=entries,
        expansion_profile="pua-web",
        scenario_depth="standard",
        ui_runner=ui_runner,
    )


def _scenario_map_needs_regeneration(
    *,
    feature: str,
    payload: dict[str, Any],
    story_sequence: list[dict[str, Any]],
    entries: list[dict[str, Any]],
) -> bool:
    scenarios = [dict(item) for item in (payload.get("scenarios") or []) if isinstance(item, dict)]
    if not scenarios:
        return False
    story_by_ac = {
        str(item.get("ac_id") or "").strip(): item
        for item in story_sequence
        if isinstance(item, dict) and str(item.get("ac_id") or "").strip()
    }
    scenarios_by_source_tc_id: dict[str, list[dict[str, Any]]] = {}
    for item in scenarios:
        source_tc_id = str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
        if not source_tc_id:
            continue
        scenarios_by_source_tc_id.setdefault(source_tc_id, []).append(item)

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        source_tc_id = str(entry.get("source_tc_id") or entry.get("tc_id") or "").strip()
        if not source_tc_id:
            continue
        ac_id = str(entry.get("ac_id") or "").strip()
        story_row = story_by_ac.get(ac_id, {})
        expected_browser = _entry_browser_required(
            entry,
            story_text=str(story_row.get("text") or ""),
            feature=feature,
            theme=str(story_row.get("theme") or ""),
        )
        if not expected_browser:
            continue
        related = scenarios_by_source_tc_id.get(source_tc_id, [])
        if not related:
            return True
        if not any(bool(item.get("browser_required")) for item in related):
            return True
        if "happy" not in {str(item.get("scenario_family") or "").strip().lower() for item in related}:
            return True
    return False


def _augment_story_scenario_map(
    *,
    feature: str,
    payload: dict[str, Any],
    story_sequence: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    ui_runner: str = "playwright",
) -> dict[str, Any]:
    normalized = dict(payload)
    scenarios = [dict(item) for item in (payload.get("scenarios") or []) if isinstance(item, dict)]
    stories = [dict(item) for item in (payload.get("stories") or []) if isinstance(item, dict)]
    normalized["scenarios"] = scenarios
    normalized["stories"] = stories
    story_sequence_by_ac = {
        str(item.get("ac_id") or "").strip(): item
        for item in story_sequence
        if isinstance(item, dict) and str(item.get("ac_id") or "").strip()
    }
    entry_by_source_tc_id = {
        str(item.get("source_tc_id") or item.get("tc_id") or "").strip(): item
        for item in entries
        if isinstance(item, dict) and str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
    }

    for scenario in scenarios:
        source_tc_id = str(scenario.get("source_tc_id") or scenario.get("tc_id") or "").strip()
        entry = entry_by_source_tc_id.get(source_tc_id)
        if not isinstance(entry, dict):
            continue
        ac_id = str(entry.get("ac_id") or scenario.get("ac_id") or "").strip()
        story_row = story_sequence_by_ac.get(ac_id, {})
        qa_type = str(entry.get("qa_type") or entry.get("layer") or scenario.get("qa_type") or "contract").strip()
        scenario_family = str(scenario.get("scenario_family") or "primary").strip().lower() or "primary"
        browser_required = _entry_browser_required(
            entry,
            story_text=str(story_row.get("text") or ""),
            feature=feature,
            theme=str(story_row.get("theme") or ""),
        )
        replay_required = bool(scenario.get("replay_required") or entry.get("replay_required"))
        scenario["qa_type"] = qa_type
        scenario["layer"] = str(entry.get("layer") or qa_type).strip() or qa_type
        scenario["browser_required"] = browser_required
        scenario["replay_required"] = replay_required
        scenario["command"] = _resolve_entry_command(
            qa_type=qa_type,
            command=str(entry.get("command") or scenario.get("command") or ""),
            ui_runner=ui_runner,
        )
        if browser_required:
            exploratory_runner = str(scenario.get("exploratory_runner") or entry.get("exploratory_runner") or "").strip().lower()
            if exploratory_runner in {"", "browser-use"} and ui_runner != "browser-use":
                exploratory_runner = ui_runner
            scenario["exploratory_runner"] = exploratory_runner or ui_runner
            scenario["deterministic_runner"] = "playwright"
            scenario["explore_command"] = _resolve_entry_command(
                qa_type=qa_type,
                command=str(entry.get("explore_command") or scenario.get("explore_command") or scenario.get("command") or ""),
                ui_runner=ui_runner,
            )
            replay_qa_type = "compatibility" if scenario_family == "compatibility" else qa_type
            scenario["replay_command"] = default_command_for_qa_type(replay_qa_type, ui_runner="playwright")
        else:
            scenario["exploratory_runner"] = str(scenario.get("exploratory_runner") or entry.get("exploratory_runner") or "native").strip() or "native"
            scenario["deterministic_runner"] = str(scenario.get("deterministic_runner") or entry.get("deterministic_runner") or "native").strip() or "native"
            scenario["explore_command"] = str(scenario.get("explore_command") or entry.get("explore_command") or "").strip()
            scenario["replay_command"] = str(scenario.get("replay_command") or entry.get("replay_command") or "").strip()

    existing_source_tc_ids = {
        str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
        for item in scenarios
        if str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
    }
    story_by_ac = {
        str(item.get("ac_id") or "").strip(): item
        for item in stories
        if str(item.get("ac_id") or "").strip()
    }

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        source_tc_id = str(entry.get("source_tc_id") or entry.get("tc_id") or "").strip()
        if not source_tc_id or source_tc_id in existing_source_tc_ids:
            continue
        ac_id = str(entry.get("ac_id") or "").strip()
        qa_type = str(entry.get("qa_type") or entry.get("layer") or "contract").strip()
        scenario_id = f"SC-AUTO-{source_tc_id}"
        scenario = {
            "scenario_id": scenario_id,
            "source_tc_id": source_tc_id,
            "tc_id": f"{source_tc_id}-PRIMARY",
            "ac_id": ac_id,
            "qa_type": qa_type,
            "layer": str(entry.get("layer") or qa_type).strip() or qa_type,
            "scenario_family": "primary",
            "title": str(entry.get("assertion") or entry.get("title") or source_tc_id).strip(),
            "browser_required": bool(entry.get("browser_required")),
            "replay_required": bool(entry.get("replay_required")),
            "exploratory_runner": str(entry.get("exploratory_runner") or "native").strip() or "native",
            "deterministic_runner": str(entry.get("deterministic_runner") or "native").strip() or "native",
            "explore_command": _resolve_entry_command(
                qa_type=qa_type,
                command=str(entry.get("explore_command") or entry.get("command") or "").strip(),
                ui_runner=ui_runner,
            ) if bool(entry.get("browser_required")) else str(entry.get("explore_command") or "").strip(),
            "replay_command": str(entry.get("replay_command") or "").strip(),
            "coverage_axes": [axis for axis in ("primary", qa_type, "non-browser") if axis],
            "depends_on": list(entry.get("depends_on") or []),
            "stop_on_fail": bool(entry.get("stop_on_fail", False)),
            "automation": str(entry.get("automation") or "auto").strip() or "auto",
            "command": str(entry.get("command") or "").strip(),
            "assertion": str(entry.get("assertion") or "").strip(),
            "priority": str(entry.get("priority") or "P1").strip() or "P1",
            "evidence_path": str(entry.get("evidence_path") or "").strip(),
            "required_files": list(entry.get("required_files") or ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"]),
        }
        scenarios.append(scenario)
        existing_source_tc_ids.add(source_tc_id)

        story_row = story_by_ac.get(ac_id)
        if story_row is None:
            sequence_row = story_sequence_by_ac.get(ac_id, {})
            story_row = {
                "ac_id": ac_id,
                "theme": str(sequence_row.get("theme") or "").strip(),
                "text": str(sequence_row.get("text") or entry.get("assertion") or "").strip(),
                "scenario_ids": [],
                "scenario_families": [],
                "required_families": list(sequence_row.get("required_families") or []),
                "scenarios": [],
            }
            stories.append(story_row)
            story_by_ac[ac_id] = story_row
        story_row.setdefault("scenario_ids", [])
        story_row.setdefault("scenario_families", [])
        story_row.setdefault("scenarios", [])
        if scenario_id not in story_row["scenario_ids"]:
            story_row["scenario_ids"].append(scenario_id)
        story_row["scenario_families"].append("primary")
        story_row["scenarios"].append(
            {
                "scenario_id": scenario_id,
                "source_tc_id": source_tc_id,
                "tc_id": f"{source_tc_id}-PRIMARY",
                "scenario_family": "primary",
                "qa_type": qa_type,
                "browser_required": bool(entry.get("browser_required")),
                "replay_required": bool(entry.get("replay_required")),
            }
        )
    return normalized


def _expand_targeted_entries_for_mode(
    *,
    execution_mode: str,
    feature: str,
    story_sequence: list[dict[str, Any]],
    targeted_entries: list[dict[str, Any]],
    scenario_map: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    normalized_mode = str(execution_mode or "feature-aware").strip().lower()
    if normalized_mode != "story-exhaustive":
        return targeted_entries, [], []
    scenarios = scenario_map.get("scenarios") if isinstance(scenario_map.get("scenarios"), list) else []
    source_tc_ids = {
        str(item.get("tc_id") or "").strip()
        for item in targeted_entries
        if isinstance(item, dict) and str(item.get("tc_id") or "").strip()
    }
    scenario_entries = [
        dict(item)
        for item in scenarios
        if isinstance(item, dict) and str(item.get("source_tc_id") or "").strip() in source_tc_ids
    ]
    scenario_ids = sorted(
        {
            str(item.get("scenario_id") or "").strip()
            for item in scenario_entries
            if str(item.get("scenario_id") or "").strip()
        }
    )
    families = sorted(
        {
            str(item.get("scenario_family") or "").strip()
            for item in scenario_entries
            if str(item.get("scenario_family") or "").strip()
        }
    )
    return scenario_entries or targeted_entries, scenario_ids, families


def _spec_hash(project_root: Path, *, version: str, revision: dict[str, Any]) -> str:
    fingerprint = load_latest_spec_fingerprint(project_root, version=version)
    current = str(fingerprint.get("fingerprint_hash") or "").strip()
    if current:
        return current
    return str(revision.get("baseline_hash") or "").strip()


def _implementation_marker(project_root: Path, *, feature: str) -> dict[str, Any]:
    return _load_json(project_root / ".beacon" / "state" / f"implementation-{feature_slug(feature)}.json")


def _technical_archive(project_root: Path, *, version: str, feature: str) -> tuple[Path, dict[str, Any]]:
    path = project_root / "docs" / "beacon" / version / ".machine" / "execution" / f"technical-implementation-{feature_slug(feature)}.json"
    return path, _load_json(path)


def _impacted_layers(derived_entries: list[dict[str, Any]], technical_archive: dict[str, Any]) -> list[str]:
    all_layers = sorted({str(item.get("qa_type") or "") for item in derived_entries if str(item.get("qa_type") or "").strip()})
    if not technical_archive:
        return all_layers

    impacted: set[str] = set()
    changed_files = [str(item).lower() for item in technical_archive.get("changed_files", []) if str(item).strip()]
    for path in changed_files:
        if path.endswith((".md", ".json")) and (path.startswith("docs/") or path in {"readme.md", "skill.md"} or "/skill.md" in path):
            impacted.add("contract")
        if any(token in path for token in ("/commands/", "/cli", "/utils/")):
            impacted.update({"contract", "integration", "regression"})
        if "/tests/" in path:
            impacted.add("regression")
        if any(token in path for token in ("/ui", "/frontend", "playwright", "cypress", "browser")):
            impacted.update({"functional", "compatibility", "regression"})
        if any(token in path for token in ("api", "contract", "openapi", "schema")):
            impacted.update({"interface", "contract", "integration"})
        if any(token in path for token in ("db", "migration", "sql", "data")):
            impacted.update({"integration", "exception", "regression"})
        if any(token in path for token in ("config", "env", ".yaml", ".yml", ".toml")):
            impacted.update({"smoke", "regression"})

    api_changes = technical_archive.get("api_changes") if isinstance(technical_archive.get("api_changes"), dict) else {}
    if not bool(api_changes.get("none", True)):
        impacted.update({"interface", "contract", "integration"})

    db_changes = technical_archive.get("db_changes") if isinstance(technical_archive.get("db_changes"), dict) else {}
    if not bool(db_changes.get("none", True)):
        impacted.update({"integration", "exception", "regression"})

    if technical_archive.get("config_changes") or technical_archive.get("env_changes") or technical_archive.get("feature_flags"):
        impacted.update({"smoke", "regression"})

    resolved = sorted(set(all_layers) & impacted)
    return resolved or all_layers


def _previous_evidence_done(
    previous: dict[str, Any],
    *,
    spec_hash: str,
    implementation_run_id: str,
    source_matrix_path: str,
    source_matrix_hash: str = "",
) -> bool:
    if not isinstance(previous, dict) or not previous:
        return False
    if not bool(previous.get("evidence_done", False)):
        return False
    if str(previous.get("current_spec_fingerprint_hash") or "") != spec_hash:
        return False
    if str(previous.get("implementation_run_id") or "") != implementation_run_id:
        return False
    if str(previous.get("source_matrix_path") or "") != source_matrix_path:
        return False
    if str(previous.get("source_matrix_hash") or "") != source_matrix_hash:
        return False
    feature_scorecard = previous.get("feature_scorecard")
    if not isinstance(feature_scorecard, dict) or not feature_scorecard:
        return False
    scenario_results = previous.get("scenario_results_v2") if isinstance(previous.get("scenario_results_v2"), list) else []
    coverage_current = feature_scorecard.get("coverage_current") if isinstance(feature_scorecard.get("coverage_current"), dict) else {}
    executed_scenarios = int(coverage_current.get("executed_scenarios") or 0)
    if executed_scenarios <= 0 and not scenario_results:
        return False
    return True


def _targeted_entries(
    *,
    derived_entries: list[dict[str, Any]],
    previous_status: dict[str, Any],
    spec_hash: str,
    implementation_run_id: str,
    source_matrix_path: str,
    source_matrix_hash: str,
    technical_archive: dict[str, Any],
    blocking_updates: list[dict[str, Any]],
) -> tuple[str, list[str], list[dict[str, Any]]]:
    if not derived_entries:
        return "blocked", ["no_matrix_entries"], []

    reason_codes: list[str] = []
    if not previous_status:
        reason_codes.append("no_prior_feature_qa")
    if previous_status and str(previous_status.get("status") or "").strip().lower() not in {"passed", "up_to_date"}:
        reason_codes.append("previous_feature_qa_not_passed")
    if previous_status and str(previous_status.get("current_spec_fingerprint_hash") or "") != spec_hash:
        reason_codes.append("spec_fingerprint_changed")
    if previous_status and str(previous_status.get("implementation_run_id") or "") != implementation_run_id:
        reason_codes.append("implementation_run_changed")
    if previous_status and str(previous_status.get("source_matrix_path") or "") != source_matrix_path:
        reason_codes.append("source_matrix_changed")
    if previous_status and str(previous_status.get("source_matrix_hash") or "") != source_matrix_hash:
        reason_codes.append("source_matrix_changed")
    if not previous_status:
        impacted = list(derived_entries)
        return "rerun_required", reason_codes or ["no_prior_feature_qa"], impacted

    if not reason_codes and _previous_evidence_done(
        previous_status,
        spec_hash=spec_hash,
        implementation_run_id=implementation_run_id,
        source_matrix_path=source_matrix_path,
        source_matrix_hash=source_matrix_hash,
    ):
        return "up_to_date", [], []

    if any(
        code in {"spec_fingerprint_changed", "implementation_run_changed", "source_matrix_changed"}
        for code in reason_codes
    ):
        return "rerun_required", reason_codes, list(derived_entries)

    impacted_layers = _impacted_layers(derived_entries, technical_archive)
    impacted = [item for item in derived_entries if str(item.get("qa_type") or "") in set(impacted_layers)]
    return "rerun_required", reason_codes, impacted or list(derived_entries)


def build_feature_qa_plan(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    execution_mode: str = "feature-aware",
    ui_runner: str = "playwright",
    persist: bool = True,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=persist) or {}
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=persist)
    source_matrix_path, source_matrix = _load_source_matrix(project_root, version=resolved_version, feature=feature, story=story)
    evidence_contract_path, evidence_contract = _load_feature_evidence_contract(project_root, version=resolved_version, feature=feature)
    source_entries = source_matrix.get("entries") if isinstance(source_matrix.get("entries"), list) else []
    derived_entries = _derive_entries(
        feature,
        [item for item in source_entries if isinstance(item, dict)],
        ui_runner=ui_runner,
    )
    derived_entries = _apply_feature_evidence_contract(
        derived_entries,
        contract=evidence_contract,
        ui_runner=ui_runner,
    )
    source_matrix_hash = _entries_fingerprint(derived_entries)
    marker = _implementation_marker(project_root, feature=feature)
    archive_path, archive_payload = _technical_archive(project_root, version=resolved_version, feature=feature)
    implementation_evidence_gate = _implementation_evidence_gate(
        marker,
        version=resolved_version,
        archive_payload=archive_payload,
    )
    matrix_projection_gate = _matrix_projection_gate(source_matrix, version=resolved_version)
    obligations = load_artifact_update_obligations(project_root, feature=feature)
    blocking_updates = blocking_obligations(obligations)
    implementation_run_id = str(marker.get("run_id") or revision.get("last_implementation_run_id") or archive_payload.get("run_id") or "").strip()
    implementation_done = bool(implementation_run_id) or str(revision.get("delivery_status") or "").strip().lower() in {"implemented", "verified", "accepted", "released"}
    if bool(implementation_evidence_gate.get("blocked")):
        implementation_done = False
    spec_hash = _spec_hash(project_root, version=resolved_version, revision=revision)
    previous_status = load_feature_qa_status(project_root, feature=feature)
    source_matrix_rel = str(source_matrix_path.relative_to(project_root))
    status, reason_codes, targeted_source_entries = _targeted_entries(
        derived_entries=derived_entries,
        previous_status=previous_status,
        spec_hash=spec_hash,
        implementation_run_id=implementation_run_id,
        source_matrix_path=source_matrix_rel,
        source_matrix_hash=source_matrix_hash,
        technical_archive=archive_payload,
        blocking_updates=blocking_updates,
    )
    story_sequence = _story_sequence(story, derived_entries)
    scenario_map = _build_story_scenario_map(
        project_root,
        version=resolved_version,
        feature=feature,
        story_sequence=story_sequence,
        entries=derived_entries,
        ui_runner=ui_runner,
    )
    exhaustive_source_entries = derived_entries if implementation_done and str(execution_mode or "").strip().lower() == "story-exhaustive" else (targeted_source_entries if implementation_done else [])
    targeted_entries, targeted_scenario_ids, targeted_scenario_families = _expand_targeted_entries_for_mode(
        execution_mode=execution_mode,
        feature=feature,
        story_sequence=story_sequence,
        targeted_entries=exhaustive_source_entries,
        scenario_map=scenario_map,
    )
    if implementation_done and str(execution_mode or "").strip().lower() == "story-exhaustive":
        previous_targeted_source_tc_ids = sorted(
            {
                str(item).strip()
                for item in (
                    previous_status.get("targeted_source_tc_ids")
                    or previous_status.get("targeted_rerun", {}).get("targeted_tc_ids")
                    or previous_status.get("targeted_tc_ids")
                    or []
                )
                if str(item).strip()
            }
        ) if isinstance(previous_status, dict) else []
        expected_targeted_source_tc_ids = sorted(
            {
                str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
                for item in targeted_entries
                if isinstance(item, dict) and str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
            }
        )
        previous_targeted_scenario_ids = sorted(
            {
                str(item).strip()
                for item in (
                    previous_status.get("targeted_scenario_ids")
                    or previous_status.get("targeted_rerun", {}).get("targeted_scenario_ids")
                    or []
                )
                if str(item).strip()
            }
        ) if isinstance(previous_status, dict) else []
        expected_targeted_scenario_ids = sorted({str(item).strip() for item in targeted_scenario_ids if str(item).strip()})
        previous_execution_mode = str(previous_status.get("execution_mode") or "").strip().lower() if isinstance(previous_status, dict) else ""
        if previous_execution_mode != "story-exhaustive":
            reason_codes.append("execution_mode_changed")
        if previous_targeted_source_tc_ids != expected_targeted_source_tc_ids:
            reason_codes.append("targeted_source_tc_ids_changed")
        if previous_targeted_scenario_ids != expected_targeted_scenario_ids:
            reason_codes.append("targeted_scenario_ids_changed")
        if any(
            code in {"execution_mode_changed", "targeted_source_tc_ids_changed", "targeted_scenario_ids_changed"}
            for code in reason_codes
        ):
            status = "rerun_required"
    evidence_done = implementation_done and bool(previous_status.get("evidence_done", False)) and status == "up_to_date"
    if status == "up_to_date" and not previous_status:
        evidence_done = False

    p0_gate_reason_codes = [
        str(item).strip()
        for item in [
            *(implementation_evidence_gate.get("reason_codes") or []),
            *(matrix_projection_gate.get("reason_codes") or []),
        ]
        if str(item).strip()
    ]
    if p0_gate_reason_codes:
        status = "blocked"
        targeted_entries = []
    reason_code_list = (
        (["implementation_not_recorded"] if not implementation_done and not p0_gate_reason_codes else [])
        + p0_gate_reason_codes
        + reason_codes
        + (["artifact_updates_pending"] if blocking_updates else [])
    )
    payload = {
        "schema_version": FEATURE_QA_SCHEMA,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "generated_at": now_iso(),
        "execution_mode": execution_mode,
        "status": "blocked" if not implementation_done else status,
        "implementation_done": implementation_done,
        "evidence_done": evidence_done,
        "current_spec_fingerprint_hash": spec_hash,
        "current_baseline_hash": str(revision.get("baseline_hash") or "").strip(),
        "implementation_run_id": implementation_run_id,
        "source_matrix_path": source_matrix_rel,
        "source_matrix_hash": source_matrix_hash,
        "derived_matrix_path": str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
        "story_scenario_map_path": str(feature_qa_scenario_map_path(project_root, feature=feature).relative_to(project_root)),
        "docs_story_scenario_map_path": str(docs_story_scenario_map_path(project_root, version=resolved_version, feature=feature).relative_to(project_root)),
        "technical_archive_path": str(archive_path.relative_to(project_root)) if archive_path.exists() else str(archive_path.relative_to(project_root)),
        "feature_status_path": str(feature_qa_status_path(project_root, feature=feature).relative_to(project_root)),
        "feature_evidence_contract_path": str(evidence_contract_path.relative_to(project_root)) if evidence_contract_path else "",
        "story_sequence": story_sequence,
        "story_scenarios": scenario_map,
        "required_scenario_families": list(scenario_map.get("families_required") or []),
        "reason_codes": reason_code_list,
        "implementation_evidence_gate": implementation_evidence_gate,
        "matrix_projection_gate": matrix_projection_gate,
        "qa_outcome_taxonomy": _qa_outcome_taxonomy(reason_code_list, plan_status=status),
        "blocking_artifact_updates": blocking_updates,
        "all_entries": derived_entries,
        "targeted_entries": targeted_entries if implementation_done else [],
        "targeted_layers": sorted({str(item.get("qa_type") or "") for item in targeted_entries}),
        "targeted_ac_ids": sorted({str(item.get("ac_id") or "") for item in targeted_entries if str(item.get("ac_id") or "").strip()}),
        "targeted_tc_ids": sorted({str(item.get("tc_id") or "") for item in targeted_entries if str(item.get("tc_id") or "").strip()}),
        "targeted_source_tc_ids": sorted({str(item.get("source_tc_id") or item.get("tc_id") or "") for item in targeted_entries if str(item.get("source_tc_id") or item.get("tc_id") or "").strip()}),
        "targeted_scenario_ids": targeted_scenario_ids,
        "targeted_scenario_families": targeted_scenario_families,
        "previous_run_id": str(previous_status.get("run_id") or "").strip() if isinstance(previous_status, dict) else "",
    }
    if persist:
        write_json(feature_qa_plan_path(project_root, feature=feature), payload)
        write_json(feature_qa_scenario_map_path(project_root, feature=feature), scenario_map)
        write_json(docs_story_scenario_map_path(project_root, version=resolved_version, feature=feature), scenario_map)
    return payload


def materialize_feature_qa_matrix(project_root: Path, *, plan: dict[str, Any]) -> Path:
    feature = str(plan.get("feature") or plan.get("feature_slug") or "").strip()
    if not feature:
        raise ValueError("feature_missing")
    path = feature_qa_matrix_path(project_root, feature=feature)
    targeted_entries = plan.get("targeted_entries") if isinstance(plan.get("targeted_entries"), list) else []
    materialized_entries: list[dict[str, Any]] = []
    for entry in targeted_entries:
        if not isinstance(entry, dict):
            continue
        item = dict(entry)
        tc_id = str(item.get("tc_id") or "").strip()
        if tc_id:
            item["evidence_path"] = _derived_evidence_path(feature=feature, tc_id=tc_id)
        materialized_entries.append(item)
    payload = {
        "schema_version": FEATURE_QA_SCHEMA,
        "feature": str(plan.get("feature_slug") or feature_slug(feature)),
        "feature_slug": str(plan.get("feature_slug") or feature_slug(feature)),
        "version": str(plan.get("version") or ""),
        "generated_at": now_iso(),
        "execution_mode": str(plan.get("execution_mode") or "feature-aware"),
        "source_matrix_path": str(plan.get("source_matrix_path") or ""),
        "story_scenario_map_path": str(plan.get("story_scenario_map_path") or ""),
        "reason_codes": list(plan.get("reason_codes") or []),
        "qa_types": list(plan.get("targeted_layers") or []),
        "entries": materialized_entries,
    }
    write_json(path, payload)
    return path


def tc_id_to_test_item_id(tc_id: str) -> str:
    match = re.search(r"(\d+)$", str(tc_id or "").strip())
    if not match:
        return ""
    return f"TEST-{int(match.group(1)):03d}"


def collect_verification_writeback(
    *,
    plan: dict[str, Any],
    qa_status: dict[str, Any],
) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    targeted_tc_ids = {str(item) for item in plan.get("targeted_tc_ids", [])}
    targeted_source_tc_ids = {str(item) for item in plan.get("targeted_source_tc_ids", [])}
    tc_results = []
    qa9 = qa_status.get("qa9") if isinstance(qa_status.get("qa9"), dict) else {}
    if isinstance(qa9.get("tc_results"), list):
        tc_results = [item for item in qa9.get("tc_results", []) if isinstance(item, dict)]
    verified: set[str] = set()
    failed: set[str] = set()
    per_item: list[dict[str, Any]] = []

    if tc_results:
        source_statuses: dict[str, list[str]] = {}
        source_by_ac: dict[str, str] = {}
        for item in tc_results:
            tc_id = str(item.get("tc_id") or "").strip()
            if targeted_tc_ids and tc_id not in targeted_tc_ids:
                continue
            ac_id = str(item.get("ac_id") or "").strip()
            source_tc_id = str(item.get("source_tc_id") or tc_id).strip()
            if targeted_source_tc_ids and source_tc_id not in targeted_source_tc_ids and targeted_tc_ids:
                continue
            test_item_id = tc_id_to_test_item_id(source_tc_id)
            status = str(item.get("status") or "pending").strip().lower()
            source_statuses.setdefault(source_tc_id, []).append(status)
            if ac_id and source_tc_id not in source_by_ac:
                source_by_ac[source_tc_id] = ac_id
            per_item.append(
                {
                    "ac_id": ac_id,
                    "tc_id": tc_id,
                    "source_tc_id": source_tc_id,
                    "scenario_id": str(item.get("scenario_id") or "").strip(),
                    "scenario_family": str(item.get("scenario_family") or "").strip(),
                    "test_item_id": test_item_id,
                    "status": status,
                    "reason_code": str(item.get("reason_code") or "").strip(),
                    "qa_type": str(item.get("qa_type") or item.get("layer") or "").strip(),
                    "browser_required": bool(item.get("browser_required")),
                    "replay_required": bool(item.get("replay_required")),
                    "browser_evidence_pack_ref": str(item.get("browser_evidence_pack_ref") or "").strip(),
                    "browser_evidence_authenticity_status": str(item.get("browser_evidence_authenticity_status") or "").strip(),
                    "replay_ref": str(item.get("replay_ref") or "").strip(),
                    "evidence_ref": item.get("evidence_ref") if isinstance(item.get("evidence_ref"), list) else [],
                }
            )
        for source_tc_id, statuses in source_statuses.items():
            ac_id = source_by_ac.get(source_tc_id, "")
            test_item_id = tc_id_to_test_item_id(source_tc_id)
            normalized = {status for status in statuses if status}
            if normalized and normalized <= {"passed"}:
                if ac_id:
                    verified.add(ac_id)
                if test_item_id:
                    verified.add(test_item_id)
            elif normalized & {"failed", "blocked"}:
                if ac_id:
                    failed.add(ac_id)
                if test_item_id:
                    failed.add(test_item_id)
        return sorted(verified), sorted(failed), per_item

    run_status = str(qa_status.get("status") or "").strip().lower()
    for entry in plan.get("targeted_entries", []):
        if not isinstance(entry, dict):
            continue
        ac_id = str(entry.get("ac_id") or "").strip()
        tc_id = str(entry.get("tc_id") or "").strip()
        source_tc_id = str(entry.get("source_tc_id") or tc_id).strip()
        test_item_id = tc_id_to_test_item_id(source_tc_id)
        if run_status == "passed":
            if ac_id:
                verified.add(ac_id)
            if test_item_id:
                verified.add(test_item_id)
        elif run_status in {"failed", "blocked"}:
            if ac_id:
                failed.add(ac_id)
            if test_item_id:
                failed.add(test_item_id)
        per_item.append(
            {
                "ac_id": ac_id,
                "tc_id": tc_id,
                "source_tc_id": source_tc_id,
                "scenario_id": str(entry.get("scenario_id") or "").strip(),
                "scenario_family": str(entry.get("scenario_family") or "").strip(),
                "test_item_id": test_item_id,
                "status": run_status or "pending",
                "reason_code": str(entry.get("reason_code") or "").strip(),
                "qa_type": str(entry.get("qa_type") or "").strip(),
                "browser_required": bool(entry.get("browser_required")),
                "replay_required": bool(entry.get("replay_required")),
                "browser_evidence_pack_ref": str(entry.get("browser_evidence_pack_ref") or "").strip(),
                "browser_evidence_authenticity_status": str(entry.get("browser_evidence_authenticity_status") or "").strip(),
                "replay_ref": str(entry.get("replay_ref") or "").strip(),
                "evidence_ref": [],
            }
        )
    return sorted(verified), sorted(failed), per_item


def _executed_acceptance_layers(*, scenario_results: list[dict[str, Any]], qa_status: dict[str, Any]) -> list[str]:
    layers: set[str] = set()
    for item in scenario_results:
        if not isinstance(item, dict):
            continue
        if not (
            str(item.get("status") or "").strip().lower() in {"passed", "failed", "review_required"}
            or bool(item.get("evidence_ref"))
            or bool(str(item.get("browser_evidence_pack_ref") or "").strip())
        ):
            continue
        layer = BROWSER_QA_LAYER if bool(item.get("browser_required")) else normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
        if layer:
            layers.add(layer)

    qa9 = qa_status.get("qa9") if isinstance(qa_status.get("qa9"), dict) else {}
    tc_results = qa9.get("tc_results") if isinstance(qa9.get("tc_results"), list) else []
    for item in tc_results:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").strip().lower() not in {"passed", "failed", "review_required"} and not bool(item.get("evidence_ref")):
            continue
        layer = BROWSER_QA_LAYER if bool(item.get("browser_required")) else normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
        if layer:
            layers.add(layer)
    return sorted(layers)


def _clamp_confidence(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def _confidence_band(calibrated: float, *, auto_accept_threshold: float, review_threshold: float) -> str:
    if calibrated >= auto_accept_threshold:
        return "high"
    if calibrated >= review_threshold:
        return "medium"
    return "low"


def _evidence_sufficiency(item: dict[str, Any]) -> str:
    browser_required = bool(item.get("browser_required"))
    replay_required = bool(item.get("replay_required"))
    has_browser_pack = bool(str(item.get("browser_evidence_pack_ref") or "").strip())
    has_replay = bool(str(item.get("replay_ref") or "").strip())
    authenticity = str(item.get("browser_evidence_authenticity_status") or "").strip().lower()
    has_refs = bool(item.get("evidence_ref")) or has_browser_pack or has_replay
    if browser_required:
        if authenticity == "placeholder_only":
            return "weak"
        if has_browser_pack and (not replay_required or has_replay):
            return "strong"
        if has_browser_pack or has_replay:
            return "partial"
        return "missing"
    return "strong" if has_refs else "weak"


def _is_runner_reason_code(reason_code: str) -> bool:
    normalized_reason = str(reason_code or "").strip().lower()
    if not normalized_reason:
        return False
    return any(token in normalized_reason for token in ("runner", "browser-use", "agent-browser", "junit", "assertion_count_zero"))


def _closure_outcome(item: dict[str, Any], *, evidence_sufficiency: str) -> str:
    status = str(item.get("status") or "pending").strip().lower()
    reason_code = str(item.get("reason_code") or "").strip()
    browser_required = bool(item.get("browser_required"))
    replay_required = bool(item.get("replay_required"))
    has_replay = bool(str(item.get("replay_ref") or "").strip())
    has_browser_pack = bool(str(item.get("browser_evidence_pack_ref") or "").strip())
    authenticity = str(item.get("browser_evidence_authenticity_status") or "").strip().lower()
    if browser_required and replay_required and not has_replay:
        return "needs_replay"
    if browser_required and authenticity == "placeholder_only":
        return "needs_more_evidence"
    if browser_required and not has_browser_pack:
        return "needs_more_evidence"
    if _is_runner_reason_code(reason_code):
        return "needs_more_evidence" if browser_required else "review_required"
    if status == "passed":
        return "accepted"
    if status == "failed":
        return "implementation_reopened"
    if status == "blocked":
        return "review_required" if evidence_sufficiency in {"strong", "partial"} else "needs_more_evidence"
    if status == "review_required":
        return "review_required"
    return "review_required"


def _root_cause_type(*, status: str, closure_outcome: str, reason_code: str = "") -> str:
    normalized_reason = str(reason_code or "").strip().lower()
    if any(token in normalized_reason for token in ("contract_drift", "requirement", "trace_mismatch")):
        return "spec_gap"
    if any(token in normalized_reason for token in ("session", "auth", "environment", "origin_target_unknown")):
        return "environment_gap"
    if any(token in normalized_reason for token in ("flake", "rerun")):
        return "flake"
    if _is_runner_reason_code(normalized_reason):
        return "runner_gap"
    if closure_outcome in {"needs_more_evidence", "needs_replay"}:
        return "evidence_gap"
    if closure_outcome == "requirement_rewrite_required":
        return "spec_gap"
    if closure_outcome in {"runner_issue", "flake_quarantined"}:
        return "runner_gap" if closure_outcome == "runner_issue" else "flake"
    if status == "failed" or closure_outcome in {"implementation_reopened", "bug_filed"}:
        return "implementation_gap"
    return "none"


def _judge_signals(item: dict[str, Any], *, evidence_sufficiency: str) -> dict[str, float]:
    status = str(item.get("status") or "pending").strip().lower()
    status_score = {
        "passed": 1.0,
        "failed": 0.15,
        "blocked": 0.35,
        "review_required": 0.45,
        "pending": 0.25,
    }.get(status, 0.25)
    evidence_score = {
        "strong": 1.0,
        "partial": 0.7,
        "weak": 0.45,
        "missing": 0.1,
    }.get(evidence_sufficiency, 0.25)
    replay_required = bool(item.get("replay_required"))
    replay_present = bool(str(item.get("replay_ref") or "").strip())
    replay_score = 1.0 if (not replay_required or replay_present) else 0.0
    trace_score = 1.0 if str(item.get("ac_id") or "").strip() and str(item.get("tc_id") or "").strip() else 0.5
    flake_penalty = 0.0
    return {
        "status_score": round(status_score, 4),
        "evidence_score": round(evidence_score, 4),
        "replay_score": round(replay_score, 4),
        "trace_score": round(trace_score, 4),
        "flake_penalty": round(flake_penalty, 4),
    }


def _calibrated_confidence(raw: float, calibration_model: dict[str, Any]) -> float:
    bins = calibration_model.get("bins") if isinstance(calibration_model.get("bins"), list) else []
    for item in bins:
        if not isinstance(item, dict):
            continue
        lower = float(item.get("lower") or 0.0)
        upper = float(item.get("upper") or 1.0)
        if lower <= raw <= upper:
            return _clamp_confidence(float(item.get("empirical_accuracy") or raw))
    return _clamp_confidence(raw)


def _browser_blocker_session_reason(stop_reasons: list[str]) -> str:
    for reason in stop_reasons:
        normalized = str(reason or "").strip()
        if normalized in {
            "protected_surface_session_bridge_missing",
            "protected_surface_runner_priority_unavailable",
            "browser_runner_learning_missing",
        }:
            return normalized
    return ""


def build_feature_qa_precision_artifacts(
    project_root: Path,
    *,
    feature: str,
    run_id: str,
    plan: dict[str, Any],
    per_item_results: list[dict[str, Any]],
    project_profile_gate: dict[str, Any] | None = None,
    qa_status: dict[str, Any] | None = None,
    exhaustiveness: dict[str, Any] | None = None,
    design_truth_verdict: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], Path, Path]:
    calibration_model = load_qa_calibration_model(project_root)
    risk_bands = calibration_model.get("risk_bands") if isinstance(calibration_model.get("risk_bands"), dict) else {}
    auto_accept_threshold = float(risk_bands.get("auto_accept") or DEFAULT_AUTO_ACCEPT_THRESHOLD)
    review_threshold = float(risk_bands.get("review_required") or DEFAULT_REVIEW_THRESHOLD)

    scenario_results: list[dict[str, Any]] = []
    for item in per_item_results:
        if not isinstance(item, dict):
            continue
        evidence_sufficiency = _evidence_sufficiency(item)
        closure_outcome = _closure_outcome(item, evidence_sufficiency=evidence_sufficiency)
        judge_signals = _judge_signals(item, evidence_sufficiency=evidence_sufficiency)
        raw = _clamp_confidence(
            (
                float(judge_signals["status_score"])
                + float(judge_signals["evidence_score"])
                + float(judge_signals["replay_score"])
                + float(judge_signals["trace_score"])
            )
            / 4.0
            - float(judge_signals["flake_penalty"])
        )
        calibrated = _calibrated_confidence(raw, calibration_model)
        confidence_band = _confidence_band(
            calibrated,
            auto_accept_threshold=auto_accept_threshold,
            review_threshold=review_threshold,
        )
        requires_human_review = closure_outcome in {
            "review_required",
            "needs_more_evidence",
            "needs_replay",
            "needs_requirement_clarification",
        } or (review_threshold <= calibrated < auto_accept_threshold)
        status = str(item.get("status") or "pending").strip().lower()
        reason_code = str(item.get("reason_code") or "").strip()
        scenario_results.append(
            {
                "scenario_id": str(item.get("scenario_id") or item.get("tc_id") or "").strip(),
                "tc_id": str(item.get("tc_id") or "").strip(),
                "source_tc_id": str(item.get("source_tc_id") or item.get("tc_id") or "").strip(),
                "ac_id": str(item.get("ac_id") or "").strip(),
                "feature_slug": feature_slug(feature),
                "scenario_family": str(item.get("scenario_family") or "").strip(),
                "status": "review_required" if requires_human_review and status == "blocked" else status,
                "closure_outcome": closure_outcome,
                "confidence_raw": raw,
                "confidence_calibrated": calibrated,
                "confidence_band": confidence_band,
                "requires_human_review": requires_human_review,
                "evidence_sufficiency": evidence_sufficiency,
                "root_cause_type": _root_cause_type(status=status, closure_outcome=closure_outcome, reason_code=reason_code),
                "reason_code": reason_code,
                "browser_required": bool(item.get("browser_required")),
                "replay_required": bool(item.get("replay_required")),
                "replay_present": bool(str(item.get("replay_ref") or "").strip()),
                "browser_evidence_pack_ref": str(item.get("browser_evidence_pack_ref") or "").strip(),
                "browser_evidence_authenticity_status": str(item.get("browser_evidence_authenticity_status") or "").strip(),
                "judge_signals": judge_signals,
                "evidence_ref": item.get("evidence_ref") if isinstance(item.get("evidence_ref"), list) else [],
            }
        )

    selected_source_tc_ids = {
        str(item).strip()
        for item in (
            plan.get("targeted_source_tc_ids")
            or plan.get("targeted_tc_ids")
            or [
                tc_id
                for row in (plan.get("story_sequence") or [])
                if isinstance(row, dict)
                for tc_id in (row.get("tc_ids") or [])
            ]
        )
        if str(item).strip()
    }

    required_by_ac: dict[str, list[str]] = {}
    families_by_ac_and_source_tc: dict[tuple[str, str], set[str]] = {}
    story_rows = plan.get("story_scenarios", {}).get("stories") if isinstance(plan.get("story_scenarios"), dict) else []
    for row in story_rows if isinstance(story_rows, list) else []:
        if not isinstance(row, dict):
            continue
        ac_id = str(row.get("ac_id") or "").strip()
        scenarios = row.get("scenarios") if isinstance(row.get("scenarios"), list) else []
        filtered_required_families: list[str] = []
        if selected_source_tc_ids and scenarios:
            filtered_required_families = [
                str(scenario.get("scenario_family") or "").strip()
                for scenario in scenarios
                if isinstance(scenario, dict)
                and str(scenario.get("source_tc_id") or "").strip() in selected_source_tc_ids
                and str(scenario.get("scenario_family") or "").strip() not in {"", "primary"}
            ]
        if ac_id:
            required_by_ac[ac_id] = (
                filtered_required_families
                if filtered_required_families or selected_source_tc_ids
                else [str(item) for item in (row.get("required_families") or []) if str(item).strip()]
            )
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                continue
            source_tc_id = str(scenario.get("source_tc_id") or "").strip()
            scenario_family = str(scenario.get("scenario_family") or "").strip()
            if ac_id and source_tc_id and scenario_family:
                families_by_ac_and_source_tc.setdefault((ac_id, source_tc_id), set()).add(scenario_family)
    accepted_source_tc_ids = {
        str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
        for item in scenario_results
        if str(item.get("closure_outcome") or "").strip() == "accepted"
        and str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
    }

    ac_reports: list[dict[str, Any]] = []
    ac_ids = sorted({str(item.get("ac_id") or "").strip() for item in scenario_results if str(item.get("ac_id") or "").strip()})
    for ac_id in ac_ids:
        ac_results = [item for item in scenario_results if str(item.get("ac_id") or "").strip() == ac_id]
        required_families = required_by_ac.get(ac_id, [])
        passed_family_set: set[str] = set()
        for item in ac_results:
            if str(item.get("closure_outcome") or "").strip() != "accepted":
                continue
            scenario_family = str(item.get("scenario_family") or "").strip()
            if scenario_family:
                passed_family_set.add(scenario_family)
                continue
            source_tc_id = str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
            passed_family_set.update(families_by_ac_and_source_tc.get((ac_id, source_tc_id), set()))
        for source_tc_id in accepted_source_tc_ids:
            passed_family_set.update(families_by_ac_and_source_tc.get((ac_id, source_tc_id), set()))
        passed_families = sorted(passed_family_set)
        missing_replay = [
            str(item.get("scenario_id") or "")
            for item in ac_results
            if bool(item.get("replay_required")) and not bool(item.get("replay_present"))
        ]
        open_outcomes = sorted(
            {
                str(item.get("closure_outcome") or "").strip()
                for item in ac_results
                if str(item.get("closure_outcome") or "").strip() not in {"accepted"}
            }
        )
        missing_required_families = [family for family in required_families if family not in passed_families]
        confidences = [float(item.get("confidence_calibrated") or 0.0) for item in ac_results]
        closure_status = "accepted"
        blocking_reasons: list[str] = []
        if any(str(item.get("closure_outcome") or "") in {"implementation_reopened", "bug_filed"} for item in ac_results):
            closure_status = "failed"
            blocking_reasons.append("implementation_reopened")
        elif missing_replay or any(outcome in {"needs_more_evidence", "needs_replay"} for outcome in open_outcomes):
            closure_status = "blocked"
            if missing_replay:
                blocking_reasons.append("missing_replay")
        elif missing_required_families:
            closure_status = "blocked"
            blocking_reasons.append("required_scenario_family_missing")
        elif any(bool(item.get("requires_human_review")) for item in ac_results):
            closure_status = "review_required"
            blocking_reasons.append("human_review_required")
        ac_reports.append(
            {
                "ac_id": ac_id,
                "feature_slug": feature_slug(feature),
                "required_scenario_families": required_families,
                "passed_scenario_families": passed_families,
                "required_replay_scenarios": [
                    str(item.get("scenario_id") or "")
                    for item in ac_results
                    if bool(item.get("replay_required"))
                ],
                "missing_replay_scenarios": missing_replay,
                "scenario_ids": [str(item.get("scenario_id") or "") for item in ac_results],
                "closure_status": closure_status,
                "confidence_min": round(min(confidences), 4) if confidences else 0.0,
                "confidence_avg": round(sum(confidences) / float(len(confidences) or 1), 4),
                "open_outcomes": open_outcomes,
                "blocking_reasons": blocking_reasons + missing_required_families,
            }
        )

    ac_closure_payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "run_id": run_id,
        "generated_at": now_iso(),
        "reports": ac_reports,
    }
    ac_closure_path = write_feature_qa_ac_closure(project_root, feature=feature, payload=ac_closure_payload)
    resolved_version = resolve_target_version(project_root, str(plan.get("version") or "auto"))
    deep_absorption = build_deep_absorption_status(
        project_root,
        version=resolved_version,
        feature=feature,
        ac_closure=ac_closure_payload,
    )

    project_profile_gate = project_profile_gate if isinstance(project_profile_gate, dict) else {}
    review_required_count = len([item for item in scenario_results if bool(item.get("requires_human_review"))])
    needs_replay_count = len([item for item in scenario_results if str(item.get("closure_outcome") or "") == "needs_replay"])
    unresolved_closure_outcomes = sorted(
        {
            str(item.get("closure_outcome") or "").strip()
            for item in scenario_results
            if str(item.get("closure_outcome") or "").strip() not in {"accepted"}
        }
    )
    calibrated_confidences = [float(item.get("confidence_calibrated") or 0.0) for item in scenario_results]
    release_confidence_min = round(min(calibrated_confidences), 4) if calibrated_confidences else 0.0
    release_confidence_avg = round(sum(calibrated_confidences) / float(len(calibrated_confidences) or 1), 4)
    scenario_total = len(scenario_results)
    scenario_passed = len([item for item in scenario_results if str(item.get("closure_outcome") or "") == "accepted"])
    false_complete_risk = round(
        max(
            1.0 - release_confidence_avg,
            float(len(unresolved_closure_outcomes)) / float(scenario_total or 1),
        ),
        4,
    )
    project_gate_status = str(project_profile_gate.get("status") or "not_configured")
    qa_status = qa_status if isinstance(qa_status, dict) else {}
    exhaustiveness = exhaustiveness if isinstance(exhaustiveness, dict) else {}
    design_truth_verdict = design_truth_verdict if isinstance(design_truth_verdict, dict) else {}
    revision_state = load_revision_state(
        project_root,
        version=resolved_version,
        feature=feature,
        create_if_missing=False,
    )
    reconciliation_gate = (
        detect_implementation_first_reconciliation_needed(
            project_root,
            version=resolved_version,
            feature=feature,
            revision_state=revision_state,
        )
        if revision_state
        else {}
    )
    design_truth_blocked = bool(design_truth_verdict.get("blocked")) or str(design_truth_verdict.get("status") or "").strip().lower() in {"blocked", "fail", "failed"}
    design_truth_reason_codes = [
        str(item).strip()
        for item in (design_truth_verdict.get("reason_codes") if isinstance(design_truth_verdict.get("reason_codes"), list) else [])
        if str(item).strip()
    ]
    quality_issues = qa_status.get("quality_issues") if isinstance(qa_status.get("quality_issues"), list) else []
    runtime_taxonomy = _qa_runtime_taxonomy(qa_status)
    quality_reason_codes = sorted(
        {
            str(item.get("reason_code") or "").strip()
            for item in quality_issues
            if isinstance(item, dict) and str(item.get("reason_code") or "").strip()
        }
    )
    qa_attribution = summarize_qa_attributions(
        qa_status.get("qa_attributions") if isinstance(qa_status.get("qa_attributions"), list) else []
    )
    quality_stop_reasons = sorted(
        {
            str(reason).strip()
            for item in quality_issues
            if isinstance(item, dict) and isinstance(item.get("details"), dict)
            for reason in (item.get("details", {}).get("stop_reasons") or [])
            if str(reason).strip()
        }
    )
    scenario_reason_codes = sorted(
        {
            str(item.get("reason_code") or "").strip()
            for item in scenario_results
            if isinstance(item, dict) and str(item.get("reason_code") or "").strip()
        }
    )
    stop_reasons: list[str] = []
    if project_gate_status == "blocked":
        gate_issues = project_profile_gate.get("issues") if isinstance(project_profile_gate.get("issues"), list) else []
        stop_reasons.extend(
            str(item.get("reason_code") or "project_profile_gate_blocked").strip()
            for item in gate_issues
            if isinstance(item, dict)
        )
        if not stop_reasons:
            stop_reasons.append("project_profile_gate_blocked")
    stop_reasons.extend(
        outcome
        for outcome in unresolved_closure_outcomes
        if outcome in {"implementation_reopened", "bug_filed", "needs_replay", "needs_more_evidence"}
    )
    for item in quality_issues:
        if not isinstance(item, dict):
            continue
        code = str(item.get("reason_code") or "").strip()
        if not code:
            continue
        if not any(
            token in code
            for token in (
                "auth",
                "session",
                "environment",
                "protected_surface",
                "browser_evidence_placeholder_only",
                "browser_runner_learning_missing",
                "contract_drift",
                "required_evidence_missing",
                "required_case_missing",
                "junit_missing",
                "assertion_count_zero",
                "compatibility_execution_missing",
            )
        ):
            continue
        if code in {"junit_missing_or_invalid", "assertion_count_zero_pass"}:
            layer = normalize_qa_type(str(item.get("layer") or "").strip())
            if layer not in {"unit", "integration", "contract"}:
                continue
        stop_reasons.append(code)
    stop_reasons.extend(
        code
        for code in (
            "required_replay_missing" if list(exhaustiveness.get("missing_replay_scenarios") or []) else "",
            "browser_evidence_incomplete" if list(exhaustiveness.get("missing_browser_evidence_scenarios") or []) else "",
        )
        if code
    )
    stop_reasons.extend(quality_stop_reasons)
    stop_reasons.extend(
        code
        for code in scenario_reason_codes
        if code in {
            "protected_surface_session_bridge_missing",
            "protected_surface_runner_priority_unavailable",
            "browser_evidence_placeholder_only",
            "browser_runner_learning_missing",
        }
    )
    if design_truth_blocked:
        stop_reasons.extend(design_truth_reason_codes or ["design_truth_verdict_failed"])
    if bool(reconciliation_gate.get("required")):
        stop_reasons.append(str(reconciliation_gate.get("reason_code") or "implementation_first_reconciliation_required"))
    primary_runtime_class = str(runtime_taxonomy.get("primary_class") or "").strip()
    if primary_runtime_class:
        stop_reasons.append(primary_runtime_class)
    stop_reasons = sorted({code for code in stop_reasons if str(code).strip()})
    required_scenarios = int(exhaustiveness.get("scenario_count") or scenario_total or len(plan.get("targeted_scenario_ids") or []))
    executed_scenarios = len(
        [
            item
            for item in scenario_results
            if bool(item.get("evidence_ref"))
            or str(item.get("status") or "").strip().lower() in {"passed", "failed", "review_required"}
        ]
    )
    required_source_tc_ids = sorted(
        {
            str(item)
            for item in (plan.get("targeted_source_tc_ids") or plan.get("targeted_tc_ids") or [])
            if str(item).strip()
        }
    )
    executed_source_tc_ids = {
        str(row.get("source_tc_id") or row.get("tc_id") or "").strip()
        for row in scenario_results
        if str(row.get("source_tc_id") or row.get("tc_id") or "").strip()
    }
    unexecuted_source_tc_ids = sorted(item for item in required_source_tc_ids if item not in executed_source_tc_ids)
    unresolved_source_tc_ids = sorted(
        {
            str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
            for item in scenario_results
            if str(item.get("closure_outcome") or "").strip() not in {"accepted"}
            and str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
        }
    )
    missing_test_case_ids = sorted(
        {
            *unexecuted_source_tc_ids,
            *unresolved_source_tc_ids,
        }
    )
    coverage_missing_families = list(exhaustiveness.get("missing_axes") or [])
    family_names = {str(item.get("scenario_family") or "").strip() for item in scenario_results if str(item.get("scenario_family") or "").strip()}
    missing_scenario_families = sorted([item for item in coverage_missing_families if item in family_names or item in (plan.get("required_scenario_families") or [])])
    covered_scenario_families: set[str] = set()
    for item in scenario_results:
        if not bool(item.get("evidence_ref")):
            continue
        scenario_family = str(item.get("scenario_family") or "").strip()
        if scenario_family:
            covered_scenario_families.add(scenario_family)
            continue
        ac_id = str(item.get("ac_id") or "").strip()
        source_tc_id = str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
        covered_scenario_families.update(families_by_ac_and_source_tc.get((ac_id, source_tc_id), set()))

    coverage_current = {
        "required_scenarios": required_scenarios,
        "executed_scenarios": executed_scenarios,
        "coverage_rate": round(float(executed_scenarios) / float(required_scenarios or 1), 4),
        "required_scenario_families": sorted({str(item) for item in (plan.get("required_scenario_families") or []) if str(item).strip()}),
        "covered_scenario_families": sorted(covered_scenario_families),
        "missing_scenario_families": missing_scenario_families,
        "missing_test_case_ids": missing_test_case_ids,
    }
    coverage_gap = {
        "missing_axes": list(exhaustiveness.get("missing_axes") or []),
        "missing_replay_scenarios": list(exhaustiveness.get("missing_replay_scenarios") or []),
        "missing_browser_evidence_scenarios": list(exhaustiveness.get("missing_browser_evidence_scenarios") or []),
        "missing_scenario_families": missing_scenario_families,
        "missing_test_case_ids": missing_test_case_ids,
        "open_closure_outcomes": unresolved_closure_outcomes,
    }
    coverage_gap_remaining = bool(
        missing_scenario_families
        or missing_test_case_ids
        or list(exhaustiveness.get("missing_replay_scenarios") or [])
    )
    test_case_backfill_required = bool(
        missing_scenario_families
    )
    release_ready = (
        bool(ac_reports)
        and all(str(item.get("closure_status") or "") == "accepted" for item in ac_reports)
        and review_required_count == 0
        and needs_replay_count == 0
        and release_confidence_min >= auto_accept_threshold
        and project_gate_status in {"pass", "not_configured"}
        and not design_truth_blocked
    )
    continue_decision = "ready_for_release"
    if stop_reasons:
        continue_decision = "stop_for_repair"
    elif release_ready:
        continue_decision = "ready_for_release"
    elif coverage_gap_remaining or unresolved_closure_outcomes or str(exhaustiveness.get("status") or "").strip().lower() != "passed":
        continue_decision = "continue"
    resume_command = (
        f'beacon help --project-root {project_root} --version {str(plan.get("version") or "")} --feature "{feature}"'
    )
    browser_session_reason = _browser_blocker_session_reason(stop_reasons)
    browser_placeholder_only = "browser_evidence_placeholder_only" in stop_reasons
    repair_handoff = {
        "action": (
            "beacon-change"
            if bool(reconciliation_gate.get("required"))
            else (
                "implement"
                if any(reason in {"implementation_reopened", "bug_filed"} for reason in stop_reasons)
                else (
                    "qa-session"
                    if browser_session_reason
                    else (
                        "qa-browser-rerun"
                        if browser_placeholder_only
                        else ("verify-run" if project_gate_status == "blocked" else ("test-case-create" if test_case_backfill_required else "qa-repair"))
                    )
                )
            )
        ),
        "reason": (
            str(
                ((reconciliation_gate.get("artifact") or {}).get("recovery_reason"))
                or "implementation-first reconciliation is required before QA proof can be trusted"
            )
            if bool(reconciliation_gate.get("required"))
            else (
                "protected browser surface requires an attached session or runner before QA can continue"
                if browser_session_reason
                else (
                    "browser evidence is placeholder-only and must be rerun with a real attached browser path"
                    if browser_placeholder_only
                    else (", ".join(stop_reasons[:3]) if stop_reasons else ("coverage_gap_remaining" if coverage_gap_remaining else "qa_round_incomplete"))
                )
            )
        ),
        "command": (
            str((((reconciliation_gate.get("artifact") or {}).get("change_route") or {}).get("command")) or resume_command)
            if bool(reconciliation_gate.get("required"))
            else (
                f'beacon implement run "{feature}" --project {project_root} --version {str(plan.get("version") or "")} --runner native-single'
                if any(reason in {"implementation_reopened", "bug_filed"} for reason in stop_reasons)
                else (
                    f"beacon qa session list --project {project_root}"
                    if browser_session_reason
                    else (
                        f'beacon qa run "{feature}" --project {project_root} --version {str(plan.get("version") or "")}'
                        if browser_placeholder_only
                        else (
                            f'beacon verify run "{feature}" --project-root {project_root} --version {str(plan.get("version") or "")}'
                            if project_gate_status == "blocked"
                            else (
                                f'beacon test-case create "{feature}" --project {project_root} --version {str(plan.get("version") or "")}'
                                if test_case_backfill_required
                                else (resume_command if coverage_gap_remaining else resume_command)
                            )
                        )
                    )
                )
            )
        ),
    }
    executed_acceptance_layers = _executed_acceptance_layers(scenario_results=scenario_results, qa_status=qa_status)
    blocked_acceptance_layers = sorted(
        {
            BROWSER_QA_LAYER if bool(item.get("browser_required")) else normalize_qa_type(str(item.get("qa_type") or item.get("layer") or "").strip())
            for item in scenario_results
            if str(item.get("status") or "").strip().lower() in {"blocked"}
        }
    )
    browser_evidence_item = next(
        (
            item
            for item in scenario_results
            if bool(item.get("browser_required")) and str(item.get("browser_evidence_pack_ref") or "").strip()
        ),
        {},
    )
    browser_evidence_refs = []
    if isinstance(browser_evidence_item, dict):
        browser_evidence_refs = [
            *[str(ref).strip() for ref in (browser_evidence_item.get("evidence_ref") or []) if str(ref).strip()],
            str(browser_evidence_item.get("browser_evidence_pack_ref") or "").strip(),
            str(browser_evidence_item.get("replay_ref") or "").strip(),
        ]
    browser_required_for_acceptance = any(bool(item.get("browser_required")) for item in scenario_results) or any(
        bool(item.get("browser_required")) for item in (plan.get("targeted_entries") or [])
    )
    qa_acceptance_capability = build_qa_acceptance_capability_summary(
        profile="browser" if browser_required_for_acceptance else "closure",
        browser_required=browser_required_for_acceptance,
        executed_layers=[layer for layer in executed_acceptance_layers if layer],
        blocked_layers=[layer for layer in blocked_acceptance_layers if layer],
        browser_evidence={
            "run_id": run_id,
            "source_command": str(browser_evidence_item.get("command") or "") if isinstance(browser_evidence_item, dict) else "",
            "runner": str(browser_evidence_item.get("exploratory_runner") or browser_evidence_item.get("deterministic_runner") or "playwright")
            if isinstance(browser_evidence_item, dict)
            else "playwright",
            "target_url": str(browser_evidence_item.get("target_url") or browser_evidence_item.get("route") or "") if isinstance(browser_evidence_item, dict) else "",
            "result_status": str(browser_evidence_item.get("status") or "") if isinstance(browser_evidence_item, dict) else "",
            "accepted_test_ids": [
                str(browser_evidence_item.get("tc_id") or "").strip(),
                str(browser_evidence_item.get("source_tc_id") or "").strip(),
            ]
            if isinstance(browser_evidence_item, dict)
            else [],
            "evidence_refs": [ref for ref in browser_evidence_refs if ref],
            "axes": [
                axis
                for axis in ("function", "ui", "ux", "compatibility", "session", "state_data")
                if any(axis.replace("_", "-") in str(ref).lower() or axis in str(ref).lower() for ref in browser_evidence_refs)
            ],
            "notes": str(browser_evidence_item.get("reason_code") or "") if isinstance(browser_evidence_item, dict) else "",
        }
        if browser_required_for_acceptance
        else {},
    )
    feature_scorecard_payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "run_id": run_id,
        "ac_total": len(ac_reports),
        "ac_accepted": len([item for item in ac_reports if str(item.get("closure_status") or "") == "accepted"]),
        "scenario_total": scenario_total,
        "scenario_passed": scenario_passed,
        "release_confidence_min": release_confidence_min,
        "release_confidence_avg": release_confidence_avg,
        "review_required_count": review_required_count,
        "needs_replay_count": needs_replay_count,
        "false_complete_risk": false_complete_risk,
        "unresolved_closure_outcomes": unresolved_closure_outcomes,
        "project_profile_gate_status": project_gate_status,
        "project_profile_id": str(project_profile_gate.get("profile_id") or ""),
        "coverage_current": coverage_current,
        "coverage_gap": coverage_gap,
        "boundary_evidence": {
            "boundary_principles": plan.get("boundary_principles", []),
            "assumption_capture_required": True,
            "goal_driven_verification_required": True,
            "verification_item_count": len(per_item_results),
            "targeted_scope_only": bool(plan.get("targeted_tc_ids") or plan.get("targeted_ac_ids")),
        },
        "design_truth_verdict": design_truth_verdict,
        "qa_outcome_taxonomy": {
            **runtime_taxonomy,
            "stable_taxonomy": [
                "product_failed",
                "test_failed",
                "runner_admission_blocked",
                "environment_blocked",
                "auth_session_blocked",
                "evidence_binding_missing",
                "coverage_gap",
                "truth_projection_gap",
            ],
        },
        "qa_attribution": qa_attribution,
        "qa_acceptance_capability": qa_acceptance_capability,
        "reconciliation": reconciliation_gate if isinstance(reconciliation_gate, dict) else {},
        "deep_absorption": deep_absorption,
        "release_supplement_input": {
            "deep_findings_absorbed": bool(deep_absorption.get("eligible_for_release_supplement", False)),
            "absorbed_finding_count": int(deep_absorption.get("absorbed_count") or 0),
            "advisory_or_blocked_finding_count": int(deep_absorption.get("deferred_count") or 0)
            + int(deep_absorption.get("blocked_count") or 0),
            "policy": "absorbed_deep_findings_only",
        },
        "continue_decision": continue_decision,
        "stop_reasons": stop_reasons,
        "test_case_backfill_required": test_case_backfill_required,
        "resume_command": resume_command,
        "repair_handoff": repair_handoff,
        "release_ready": release_ready and not bool(reconciliation_gate.get("required")),
    }
    feature_scorecard_path = write_feature_qa_scorecard(project_root, feature=feature, payload=feature_scorecard_payload)
    return scenario_results, ac_closure_payload, feature_scorecard_payload, ac_closure_path, feature_scorecard_path


def writeback_feature_matrix_evidence(
    project_root: Path,
    *,
    plan: dict[str, Any],
    per_item_results: list[dict[str, Any]],
    run_id: str,
) -> Path | None:
    source_rel = str(plan.get("source_matrix_path") or "").strip()
    if not source_rel:
        return None
    source_path = project_root / source_rel
    if not source_path.exists():
        return None
    payload = _load_json(source_path)
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    by_tc: dict[str, dict[str, Any]] = {}
    for item in per_item_results:
        if not isinstance(item, dict):
            continue
        source_tc_id = str(item.get("source_tc_id") or item.get("tc_id") or "").strip()
        if not source_tc_id:
            continue
        current = by_tc.get(source_tc_id, {"evidence_ref": []})
        refs = current.get("evidence_ref") if isinstance(current.get("evidence_ref"), list) else []
        new_refs = item.get("evidence_ref") if isinstance(item.get("evidence_ref"), list) else []
        merged_refs = list(dict.fromkeys([*refs, *new_refs]))
        current_status = str(current.get("status") or "").strip().lower()
        next_status = str(item.get("status") or "").strip().lower()
        resolved_status = next_status
        if current_status in {"failed", "blocked"} or next_status in {"failed", "blocked"}:
            resolved_status = "failed" if "failed" in {current_status, next_status} else "blocked"
        elif current_status == "passed" and next_status in {"passed", ""}:
            resolved_status = "passed"
        elif current_status == "passed" and not next_status:
            resolved_status = "passed"
        elif current_status and not next_status:
            resolved_status = current_status
        current.update(item)
        current["status"] = resolved_status or current_status or next_status
        current["evidence_ref"] = merged_refs
        by_tc[source_tc_id] = current
    changed = False
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        tc_id = str(entry.get("tc_id") or "").strip()
        if tc_id not in by_tc:
            continue
        result = by_tc[tc_id]
        refs = result.get("evidence_ref") if isinstance(result.get("evidence_ref"), list) else []
        existing_evidence_path = str(entry.get("evidence_path") or "").strip()
        has_run_placeholder = any(token in existing_evidence_path for token in ("{run_id}", "__RUN_ID__", "$RUN_ID"))
        if has_run_placeholder:
            entry["evidence_path"] = existing_evidence_path
        else:
            entry["evidence_path"] = str(refs[0]).strip() if refs else existing_evidence_path
        entry["status"] = str(result.get("status") or "planned").strip().lower() or "planned"
        entry["last_run_id"] = run_id
        if refs:
            entry["last_evidence_ref"] = str(refs[0]).strip()
        changed = True
    if changed:
        write_json(source_path, payload)
        return source_path
    return None
