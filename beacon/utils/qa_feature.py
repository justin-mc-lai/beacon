"""Feature-aware QA planning and writeback helpers for Beacon v1.1.9."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.commands.auto_test import LAYER_NAMES
from beacon.utils.artifact_paths import qa_matrix_candidates
from beacon.utils.artifact_update_obligations import blocking_obligations, load_artifact_update_obligations
from beacon.utils.qa9 import QA9_TYPES, normalize_qa_type
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_scenarios import expand_story_scenarios, scenario_map_path as docs_story_scenario_map_path
from beacon.utils.story_state import feature_slug, load_story_state
from beacon.utils.v110_baseline import load_latest_spec_fingerprint
from beacon.utils.versioning import resolve_target_version

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


def _normalize_entry_command(value: str) -> str:
    command = str(value or "").strip()
    lowered = command.lower()
    if not command:
        return ""
    if any(token in lowered for token in PLACEHOLDER_COMMAND_TOKENS):
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


def _derive_entries(feature: str, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
                "command": _normalize_entry_command(str(item.get("command") or "")),
                "evidence_path": str(item.get("evidence_path") or _derived_evidence_path(feature=feature, tc_id=tc_id)),
            }
        )
    return derived


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
) -> dict[str, Any]:
    docs_path = docs_story_scenario_map_path(project_root, version=version, feature=feature)
    if docs_path.exists():
        payload = _load_json(docs_path)
        if isinstance(payload.get("scenarios"), list):
            return payload
    return expand_story_scenarios(
        feature=feature,
        version=version,
        story_sequence=story_sequence,
        entries=entries,
        expansion_profile="pua-web",
        scenario_depth="standard",
    )


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


def _previous_evidence_done(previous: dict[str, Any], *, spec_hash: str, implementation_run_id: str) -> bool:
    if not isinstance(previous, dict) or not previous:
        return False
    if not bool(previous.get("evidence_done", False)):
        return False
    if str(previous.get("current_spec_fingerprint_hash") or "") != spec_hash:
        return False
    if str(previous.get("implementation_run_id") or "") != implementation_run_id:
        return False
    return True


def _targeted_entries(
    *,
    derived_entries: list[dict[str, Any]],
    previous_status: dict[str, Any],
    spec_hash: str,
    implementation_run_id: str,
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
    if not previous_status:
        impacted = list(derived_entries)
        return "rerun_required", reason_codes or ["no_prior_feature_qa"], impacted

    if not reason_codes and _previous_evidence_done(previous_status, spec_hash=spec_hash, implementation_run_id=implementation_run_id):
        return "up_to_date", [], []

    impacted_layers = _impacted_layers(derived_entries, technical_archive)
    impacted = [item for item in derived_entries if str(item.get("qa_type") or "") in set(impacted_layers)]
    return "rerun_required", reason_codes, impacted or list(derived_entries)


def build_feature_qa_plan(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    execution_mode: str = "feature-aware",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True) or {}
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    source_matrix_path, source_matrix = _load_source_matrix(project_root, version=resolved_version, feature=feature, story=story)
    source_entries = source_matrix.get("entries") if isinstance(source_matrix.get("entries"), list) else []
    derived_entries = _derive_entries(feature, [item for item in source_entries if isinstance(item, dict)])
    marker = _implementation_marker(project_root, feature=feature)
    archive_path, archive_payload = _technical_archive(project_root, version=resolved_version, feature=feature)
    obligations = load_artifact_update_obligations(project_root, feature=feature)
    blocking_updates = blocking_obligations(obligations)
    implementation_run_id = str(marker.get("run_id") or revision.get("last_implementation_run_id") or archive_payload.get("run_id") or "").strip()
    implementation_done = bool(implementation_run_id) or str(revision.get("delivery_status") or "").strip().lower() in {"implemented", "verified", "accepted", "released"}
    spec_hash = _spec_hash(project_root, version=resolved_version, revision=revision)
    previous_status = load_feature_qa_status(project_root, feature=feature)
    status, reason_codes, targeted_source_entries = _targeted_entries(
        derived_entries=derived_entries,
        previous_status=previous_status,
        spec_hash=spec_hash,
        implementation_run_id=implementation_run_id,
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
    )
    targeted_entries, targeted_scenario_ids, targeted_scenario_families = _expand_targeted_entries_for_mode(
        execution_mode=execution_mode,
        feature=feature,
        story_sequence=story_sequence,
        targeted_entries=targeted_source_entries if implementation_done else [],
        scenario_map=scenario_map,
    )
    evidence_done = implementation_done and bool(previous_status.get("evidence_done", False)) and status == "up_to_date"
    if status == "up_to_date" and not previous_status:
        evidence_done = False

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
        "source_matrix_path": str(source_matrix_path.relative_to(project_root)),
        "derived_matrix_path": str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
        "story_scenario_map_path": str(feature_qa_scenario_map_path(project_root, feature=feature).relative_to(project_root)),
        "docs_story_scenario_map_path": str(docs_story_scenario_map_path(project_root, version=resolved_version, feature=feature).relative_to(project_root)),
        "technical_archive_path": str(archive_path.relative_to(project_root)) if archive_path.exists() else str(archive_path.relative_to(project_root)),
        "feature_status_path": str(feature_qa_status_path(project_root, feature=feature).relative_to(project_root)),
        "story_sequence": story_sequence,
        "story_scenarios": scenario_map,
        "required_scenario_families": list(scenario_map.get("families_required") or []),
        "reason_codes": (
            (["implementation_not_recorded"] if not implementation_done else [])
            + reason_codes
            + (["artifact_updates_pending"] if blocking_updates else [])
        ),
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
        "entries": targeted_entries,
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
                    "qa_type": str(item.get("qa_type") or item.get("layer") or "").strip(),
                    "browser_required": bool(item.get("browser_required")),
                    "browser_evidence_pack_ref": str(item.get("browser_evidence_pack_ref") or "").strip(),
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
                "qa_type": str(entry.get("qa_type") or "").strip(),
                "browser_required": bool(entry.get("browser_required")),
                "browser_evidence_pack_ref": str(entry.get("browser_evidence_pack_ref") or "").strip(),
                "replay_ref": str(entry.get("replay_ref") or "").strip(),
                "evidence_ref": [],
            }
        )
    return sorted(verified), sorted(failed), per_item


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
        chosen = str(refs[0]).strip() if refs else str(entry.get("evidence_path") or "").strip()
        if "{run_id}" in chosen:
            chosen = chosen.replace("{run_id}", run_id)
        if "__RUN_ID__" in chosen:
            chosen = chosen.replace("__RUN_ID__", run_id)
        if "$RUN_ID" in chosen:
            chosen = chosen.replace("$RUN_ID", run_id)
        entry["evidence_path"] = chosen
        entry["status"] = str(result.get("status") or "planned").strip().lower() or "planned"
        entry["last_run_id"] = run_id
        changed = True
    if changed:
        write_json(source_path, payload)
        return source_path
    return None
