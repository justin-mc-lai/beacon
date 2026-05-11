from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_root, qa_matrix_candidates
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug, machine_story_path
from beacon.utils.technical_review_contract import feature_is_aggregation_contract
from beacon.utils.version_surface import get_version_surface_governance_payload
from beacon.utils.versioning import load_version_truth, release_truth_status, resolve_runtime_version, resolve_target_version

CANONICAL_TEST_CONTRACT_LANES = (
    "feature_release_facing",
    "current_runtime_contract",
    "generated_surface_sync",
    "compatibility_contract",
    "legacy_snapshot",
    "browser_runtime_admission",
)

QA_FIRST_PRINCIPLES_ORDER = (
    "user_story_ac_order",
    "scenario_divergence",
    "current_round_execution",
    "evidence_pack",
    "coverage_current_gap",
    "continue_decision",
    "severe_blocker_stop_for_repair",
    "repair_handoff",
    "beacon_help_resume",
    "next_qa_round_test_case_backfill",
    "release_guidance",
)

TEST_CONTRACT_REASON_CODES = (
    "test_contract_index_missing",
    "test_contract_index_stale",
    "ac_test_mapping_missing",
    "feature_release_lane_missing",
    "feature_release_lane_failed",
    "generated_surface_sync_drift",
    "planning_line_runtime_conflict",
    "unclassified_test_failure",
    "legacy_snapshot_misclassified_as_release_blocker",
    "protected_surface_session_bridge_missing",
    "protected_surface_runner_priority_unavailable",
    "browser_evidence_placeholder_only",
    "browser_runtime_admission_missing",
    "browser_runner_learning_missing",
)


def test_contract_index_path(project_root: Path, version: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_root(project_root, resolved_version) / "testing" / "test-contract-index.json"


def load_test_contract_index(project_root: Path, *, version: str) -> dict[str, Any]:
    payload = read_json(test_contract_index_path(project_root, version), {})
    return payload if isinstance(payload, dict) else {}


def _sha256(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _safe_relative(path: Path | None, project_root: Path) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(project_root))
    except Exception:
        return str(path)


def _read_dict(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def _ac_items(story_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for story in story_payload.get("stories", []) if isinstance(story_payload.get("stories"), list) else []:
        if not isinstance(story, dict):
            continue
        for item in story.get("items", []) if isinstance(story.get("items"), list) else []:
            if not isinstance(item, dict) or str(item.get("kind") or "") != "ac":
                continue
            ac_id = str(item.get("id") or "").strip()
            if ac_id:
                out[ac_id] = item
    return out


def _classify_lane(entry: dict[str, Any], ac_item: dict[str, Any]) -> str:
    ac_id = str(entry.get("ac_id") or "").strip().lower()
    theme = str(ac_item.get("theme") or "").strip().lower()
    if theme in {
        "browser-admission",
        "browser-evidence-authenticity",
        "browser-runner-priority",
        "blocked-not-false-fail",
        "runner-learning",
        "browser-lane-traceability",
    }:
        return "browser_runtime_admission"
    if theme in {"legacy-classification"}:
        return "legacy_snapshot"
    if theme in {"generated-surface-sync", "skill-delivery"}:
        return "generated_surface_sync"
    if theme in {"planning-line-safety"}:
        return "current_runtime_contract"
    text = " ".join(
        [
            ac_id,
            theme,
            str(entry.get("layer") or ""),
            str(entry.get("command") or ""),
            str(entry.get("assertion") or ""),
        ]
    ).lower()
    if "legacy" in text or "historical snapshot" in text:
        return "legacy_snapshot"
    if "generated_surface" in text or "generated surface" in text or "skill-delivery" in text or "skill delivery" in text:
        return "generated_surface_sync"
    if "planning-line" in text or "planning line" in text or "current runtime" in text or "docs default" in text or "package version" in text:
        return "current_runtime_contract"
    if "compatibility_contract" in text or "compatibility contract" in text or "compatibility" in text:
        return "compatibility_contract"
    if any(token in text for token in ("browser admission", "protected surface", "session bridge", "playwright attach/cdp", "web-access", "placeholder transcript", "runner-learning", "browser evidence")):
        return "browser_runtime_admission"
    return "feature_release_facing"


def _entry_release_blocking(lane: str) -> bool:
    return lane in {"feature_release_facing", "current_runtime_contract", "generated_surface_sync", "compatibility_contract", "browser_runtime_admission"}


_LEGACY_TC_EVIDENCE_RE = re.compile(r"^(TC)-US0*(\d+)-001(\.json)?$", re.IGNORECASE)


def _resolve_evidence_path(project_root: Path, relative_path: str) -> Path | None:
    path_text = str(relative_path or "").strip()
    if not path_text:
        return None
    path = project_root / path_text
    if path.exists():
        return path
    match = _LEGACY_TC_EVIDENCE_RE.match(path.name)
    if not match:
        return None
    legacy_name = f"{match.group(1).upper()}-{int(match.group(2)):03d}{match.group(3) or ''}"
    legacy_path = path.with_name(legacy_name)
    if legacy_path.exists():
        return legacy_path
    return None


def _evidence_status(project_root: Path, relative_path: str) -> str:
    path = _resolve_evidence_path(project_root, relative_path)
    if path is None:
        return "missing"
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        return "present"
    status = str(payload.get("status") or payload.get("result") or payload.get("verdict") or "").strip().lower()
    if status in {"pass", "passed", "ok", "success"}:
        return "passed"
    if status in {"fail", "failed", "blocked", "error"}:
        return "failed"
    return "present"


def _source_paths(project_root: Path, version: str, slug: str) -> dict[str, Path | None]:
    base = project_root / "docs" / "beacon" / version
    return {
        "prd": base / "prd" / f"{slug}.md",
        "user_story": base / "user-story" / f"{slug}.md",
        "test_case": base / "qa" / "test-cases" / f"{slug}.md",
        "ac_matrix": _first_existing(qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")),
        "story_state": machine_story_path(project_root, version, slug),
    }


def _truth_refs(project_root: Path, paths: dict[str, Path | None]) -> dict[str, str]:
    return {key: _safe_relative(path, project_root) for key, path in paths.items()}


def _source_hashes(paths: dict[str, Path | None]) -> dict[str, str]:
    return {key: _sha256(path) if path is not None else "" for key, path in paths.items()}


def _planning_line_safety(project_root: Path, version: str) -> dict[str, Any]:
    truth = load_version_truth(project_root)
    runtime_line = str(truth.get("runtime_version") or "")
    docs_default_line = str(truth.get("docs_default_line") or "")
    current_runtime_release_line = str(truth.get("current_runtime_release_line") or "")
    feature_line_status = release_truth_status(truth, version)
    conflict = feature_line_status == "planning_only" and version in {
        runtime_line,
        docs_default_line,
        current_runtime_release_line,
    }
    return {
        "status": "blocked" if conflict else "pass",
        "blocked": conflict,
        "reason_code": "planning_line_runtime_conflict" if conflict else "",
        "runtime_line": runtime_line,
        "docs_default_line": docs_default_line,
        "current_runtime_release_line": current_runtime_release_line,
        "feature_line_status": feature_line_status,
    }


def build_test_contract_index(project_root: Path, *, version: str, feature: str, write: bool = False) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    resolved_runtime = resolve_runtime_version(project_root, "auto")
    slug = feature_slug(feature)
    paths = _source_paths(project_root, resolved_version, slug)
    ac_matrix = _read_dict(paths.get("ac_matrix"))
    story_payload = _read_dict(paths.get("story_state"))
    ac_by_id = _ac_items(story_payload)
    entries = ac_matrix.get("entries") if isinstance(ac_matrix.get("entries"), list) else []
    lanes: dict[str, list[dict[str, Any]]] = {lane: [] for lane in CANONICAL_TEST_CONTRACT_LANES}
    test_refs: list[dict[str, Any]] = []
    ac_to_test_refs: dict[str, list[str]] = {}
    structural_reason_codes: list[str] = []
    unclassified: list[str] = []
    mapping_gaps: list[str] = []
    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            continue
        entry = dict(raw_entry)
        ac_id = str(entry.get("ac_id") or "").strip()
        tc_id = str(entry.get("tc_id") or "").strip()
        ac_item = ac_by_id.get(ac_id, {})
        lane = _classify_lane(entry, ac_item)
        if lane not in lanes:
            lane = ""
        if not lane:
            unclassified.append(tc_id or ac_id or "unknown")
            continue
        evidence_path = str(entry.get("evidence_path") or "").strip()
        mapping_status = "pass" if ac_id and tc_id and (evidence_path or lane == "generated_surface_sync") else "missing"
        if _entry_release_blocking(lane) and mapping_status != "pass":
            mapping_gaps.append(tc_id or ac_id or "unknown")
        normalized = {
            "tc_id": tc_id,
            "ac_id": ac_id,
            "ac_theme": str(ac_item.get("theme") or ""),
            "lane": lane,
            "layer": str(entry.get("layer") or ""),
            "command": str(entry.get("command") or ""),
            "assertion": str(entry.get("assertion") or ""),
            "evidence_path": evidence_path,
            "evidence_status": _evidence_status(project_root, evidence_path),
            "source": str(entry.get("source") or ""),
            "release_blocking": _entry_release_blocking(lane),
            "mapping_status": mapping_status,
        }
        test_refs.append(normalized)
        lanes[lane].append(normalized)
        if ac_id and tc_id:
            ac_to_test_refs.setdefault(ac_id, [])
            if tc_id not in ac_to_test_refs[ac_id]:
                ac_to_test_refs[ac_id].append(tc_id)
    if not entries:
        structural_reason_codes.append("ac_test_mapping_missing")
    if unclassified:
        structural_reason_codes.append("unclassified_test_failure")
    if mapping_gaps:
        structural_reason_codes.append("ac_test_mapping_missing")
    planning_safety = _planning_line_safety(project_root, resolved_version)
    if planning_safety.get("blocked"):
        structural_reason_codes.append("planning_line_runtime_conflict")
    payload = {
        "schema_version": "1.0",
        "contract_kind": "beacon_test_contract_index",
        "version": resolved_version,
        "runtime_line": resolved_runtime,
        "docs_line": resolved_version,
        "feature": feature,
        "feature_slug": slug,
        "feature_line_status": str(planning_safety.get("feature_line_status") or ""),
        "truth_refs": _truth_refs(project_root, paths),
        "source_hashes": _source_hashes(paths),
        "lanes": lanes,
        "lane_counts": {lane: len(items) for lane, items in lanes.items()},
        "canonical_lanes": list(CANONICAL_TEST_CONTRACT_LANES),
        "test_refs": test_refs,
        "ac_to_test_refs": {key: sorted(value) for key, value in sorted(ac_to_test_refs.items())},
        "qa_order_contract": {"sequence": list(QA_FIRST_PRINCIPLES_ORDER), "source": "skills/beacon/references/usage-rules.md"},
        "deep_delta_policy": {"owner": "deep", "adoption_route": "test-case_or_supplemental_qa", "executes_qa": False},
        "planning_line_safety": planning_safety,
        "status": "blocked" if structural_reason_codes else "pass",
        "blocked": bool(structural_reason_codes),
        "reason_codes": sorted(set(structural_reason_codes)),
        "generated_at": now_iso(),
        "index_path": str(test_contract_index_path(project_root, resolved_version).relative_to(project_root)),
    }
    if write:
        write_json(test_contract_index_path(project_root, resolved_version), payload)
    return payload


def _release_reason_codes(project_root: Path, payload: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    feature = str(payload.get("feature") or "").strip()
    version = str(payload.get("version") or "").strip()
    aggregation_contract = bool(feature) and bool(version) and feature_is_aggregation_contract(
        project_root,
        version=version,
        feature=feature,
    )
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), dict) else {}
    feature_lane = lanes.get("feature_release_facing") if isinstance(lanes.get("feature_release_facing"), list) else []
    if not feature_lane and not aggregation_contract:
        codes.append("feature_release_lane_missing")
    for entry in feature_lane:
        if not isinstance(entry, dict):
            continue
        status = str(entry.get("evidence_status") or "").strip().lower()
        if status == "missing" and not aggregation_contract:
            codes.append("feature_release_lane_missing")
        elif status in {"failed", "present"}:
            codes.append("feature_release_lane_failed")
    generated_lane = lanes.get("generated_surface_sync") if isinstance(lanes.get("generated_surface_sync"), list) else []
    if any(str(item.get("evidence_status") or "") == "failed" for item in generated_lane if isinstance(item, dict)):
        codes.append("generated_surface_sync_drift")
    browser_lane = lanes.get("browser_runtime_admission") if isinstance(lanes.get("browser_runtime_admission"), list) else []
    if not browser_lane and not aggregation_contract:
        codes.append("browser_runtime_admission_missing")
    for entry in browser_lane:
        if not isinstance(entry, dict):
            continue
        status = str(entry.get("evidence_status") or "").strip().lower()
        if status == "missing" and not aggregation_contract:
            codes.append("browser_runtime_admission_missing")
    if bool((payload.get("planning_line_safety") or {}).get("blocked", False)):
        codes.append("planning_line_runtime_conflict")
    version_surface = get_version_surface_governance_payload(project_root, strict=True)
    if generated_lane and bool(version_surface.get("blocked", False)):
        codes.append("generated_surface_sync_drift")
    return sorted(set(code for code in codes if code))


def build_test_contract_gate_payload(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    path = test_contract_index_path(project_root, resolved_version)
    if not path.exists():
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_codes": ["test_contract_index_missing"],
            "release_gate": {"status": "blocked", "blocked": True, "reason_codes": ["test_contract_index_missing"]},
            "index_path": str(path.relative_to(project_root)),
            "repair_commands": [
                f'beacon doctor build-test-contract-index "{feature}" --project-root . --version {resolved_version} --json'
            ],
        }
    payload = load_test_contract_index(project_root, version=resolved_version)
    structural_codes: list[str] = []
    if str(payload.get("feature_slug") or "") != feature_slug(feature) or str(payload.get("version") or "") != resolved_version:
        structural_codes.append("test_contract_index_stale")
    paths = _source_paths(project_root, resolved_version, feature_slug(feature))
    expected_hashes = _source_hashes(paths)
    actual_hashes = payload.get("source_hashes") if isinstance(payload.get("source_hashes"), dict) else {}
    if expected_hashes != {str(key): str(value) for key, value in actual_hashes.items()}:
        structural_codes.append("test_contract_index_stale")
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), dict) else {}
    missing_lanes = [lane for lane in CANONICAL_TEST_CONTRACT_LANES if lane not in lanes]
    if missing_lanes:
        structural_codes.append("unclassified_test_failure")
    test_refs = payload.get("test_refs") if isinstance(payload.get("test_refs"), list) else []
    if any(not str(item.get("lane") or "").strip() for item in test_refs if isinstance(item, dict)):
        structural_codes.append("unclassified_test_failure")
    if any(str(item.get("release_blocking") or "").lower() == "true" and str(item.get("mapping_status") or "") != "pass" for item in test_refs if isinstance(item, dict)):
        structural_codes.append("ac_test_mapping_missing")
    if bool((payload.get("planning_line_safety") or {}).get("blocked", False)):
        structural_codes.append("planning_line_runtime_conflict")
    release_codes = _release_reason_codes(project_root, payload)
    structural_codes = sorted(set(code for code in [*structural_codes, *list(payload.get("reason_codes") or [])] if str(code).strip()))
    blocked = bool(structural_codes)
    release_blocked = bool(release_codes or blocked)
    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_codes": structural_codes,
        "release_gate": {
            "status": "blocked" if release_blocked else "pass",
            "blocked": release_blocked,
            "reason_codes": sorted(set([*structural_codes, *release_codes])),
        },
        "index_path": str(path.relative_to(project_root)),
        "lane_counts": payload.get("lane_counts") if isinstance(payload.get("lane_counts"), dict) else {},
        "canonical_lanes": list(CANONICAL_TEST_CONTRACT_LANES),
        "qa_order_contract": payload.get("qa_order_contract") if isinstance(payload.get("qa_order_contract"), dict) else {},
        "deep_delta_policy": payload.get("deep_delta_policy") if isinstance(payload.get("deep_delta_policy"), dict) else {},
        "planning_line_safety": payload.get("planning_line_safety") if isinstance(payload.get("planning_line_safety"), dict) else {},
        "repair_commands": [
            f'beacon doctor build-test-contract-index "{feature}" --project-root . --version {resolved_version} --json',
            f'beacon doctor verify-test-contract-index "{feature}" --project-root . --version {resolved_version} --strict --json',
        ],
    }
