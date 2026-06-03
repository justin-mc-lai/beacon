"""Implementation/verification/acceptance writeback helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from beacon.utils.artifact_paths import human_execution_file, machine_execution_dir, machine_trace_dir
from beacon.utils.revision_state import load_revision_state, save_revision_state
from beacon.utils.prototype_utils import prototype_files
from beacon.utils.reconciliation import append_implementation_writeback_event
from beacon.utils.acceptance_kit import write_acceptance_kit_projection
from beacon.utils.requirement_refs import requirement_truth_paths
from beacon.utils.implementation_plan import (
    mark_implementation_plan_accepted,
    update_plan_progress_for_implementation,
    update_plan_progress_for_verification,
)
from beacon.utils.runtime import load_run_state, now_iso, save_run_state, write_json
from beacon.utils.story_state import feature_slug, load_story_state, save_story_state
from beacon.utils.versioning import resolve_target_version
from beacon.utils.workflow_memory import (
    append_lifecycle_event,
    compute_workflow_progress,
    lifecycle_path,
    record_stage_writeback,
    resolve_workflow_run_id,
    workflow_stages_for_run,
    write_stage_context,
)


def _normalize_ids(values: Iterable[str] | None) -> set[str]:
    out: set[str] = set()
    for value in values or []:
        text = str(value or "").strip().upper()
        if text:
            out.add(text)
    return out


def _is_story_verification_complete(items: list[dict[str, Any]]) -> bool:
    required_acs = [item for item in items if isinstance(item, dict) and item.get("kind") == "ac" and bool(item.get("required", True))]
    required_tests = [item for item in items if isinstance(item, dict) and item.get("kind") == "test" and bool(item.get("required", True))]
    ac_complete = all(str(item.get("status", "")).lower() in {"verified", "accepted"} for item in required_acs)
    test_complete = all(str(item.get("status", "")).lower() in {"passed", "verified", "accepted"} for item in required_tests)
    return bool(required_acs or required_tests) and ac_complete and test_complete


def _existing_relative_paths(project_root: Path, candidates: Iterable[Path]) -> list[str]:
    refs: list[str] = []
    for candidate in candidates:
        path = Path(candidate)
        if not path.exists():
            continue
        refs.append(str(path.relative_to(project_root)))
    return refs


def _stable_hash(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _stable_file_hash(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _acceptance_machine_path(project_root: Path, version: str, feature: str) -> Path:
    return machine_execution_dir(project_root, version) / f"qa-acceptance-{feature_slug(feature)}.json"


def _acceptance_human_path(project_root: Path, version: str, feature: str) -> Path:
    return human_execution_file(project_root, version, f"qa-acceptance-brief-{feature_slug(feature)}.md")


def _acceptance_runtime_path(project_root: Path, feature: str) -> Path:
    return project_root / ".beacon" / "transactions" / f"qa-acceptance-{feature_slug(feature)}.json"


def _acceptance_requirement_refs(project_root: Path, *, version: str, feature: str) -> list[str]:
    slug = feature_slug(feature)
    refs = requirement_truth_paths(
        project_root,
        version=version,
        feature=feature,
        consumer="acceptance-writeback",
    )
    return _existing_relative_paths(
        project_root,
        [
            refs["prd"],
            refs["user_story"],
            refs["test_case"],
            load_revision_state(project_root, version=version, feature=feature, create_if_missing=True)
            and machine_execution_dir(project_root, version) / f"{slug}.revision.json",
        ],
    )


def _acceptance_projection_seq(path: Path) -> int:
    if not path.exists():
        return 1
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return 1
    current = payload.get("projection_seq") if isinstance(payload, dict) else None
    try:
        return int(current) + 1
    except Exception:  # noqa: BLE001
        return 1


def _render_acceptance_markdown(envelope: dict[str, Any]) -> str:
    requirement_refs = envelope.get("requirement_refs") if isinstance(envelope.get("requirement_refs"), list) else []
    evidence_refs = envelope.get("evidence_refs") if isinstance(envelope.get("evidence_refs"), list) else []
    test_case_refs = envelope.get("test_case_refs") if isinstance(envelope.get("test_case_refs"), list) else []
    verdict = str(envelope.get("verdict", "") or "")
    summary_line = "可以进入 release 检查与收口。" if verdict == "passed" else "仍需根据证据处理阻塞项。"
    lines = [
        f"# QA Acceptance Brief: {envelope.get('feature', '')}",
        "",
        f"- version: `{envelope.get('version', '')}`",
        f"- feature: `{envelope.get('feature', '')}`",
        f"- revision_id: `{envelope.get('revision_id', '')}`",
        f"- verdict: `{envelope.get('verdict', '')}`",
        f"- accepted_at: `{envelope.get('accepted_at', '')}`",
        f"- accepted_by: `{envelope.get('accepted_by', '')}`",
        "",
        "## Summary",
        f"- {summary_line}",
        f"- source_command: `{envelope.get('source_command', '')}`",
        "",
        "## Requirement Refs",
    ]
    lines.extend(f"- `{item}`" for item in requirement_refs) if requirement_refs else lines.append("- none")
    lines.extend(["", "## Test Case Refs"])
    lines.extend(f"- `{item}`" for item in test_case_refs) if test_case_refs else lines.append("- none")
    lines.extend(["", "## Evidence Refs"])
    lines.extend(f"- `{item}`" for item in evidence_refs) if evidence_refs else lines.append("- none")
    lines.extend(
        [
            "",
            "## Verdict Summary",
            f"- required_ac_count: `{envelope.get('required_ac_count', 0)}`",
            f"- required_test_count: `{envelope.get('required_test_count', 0)}`",
            f"- story_status: `{envelope.get('story_status', '')}`",
            f"- revision_delivery_status: `{envelope.get('revision_delivery_status', '')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_acceptance_runtime_projection(
    project_root: Path,
    *,
    envelope: dict[str, Any],
    machine_path: Path,
    human_path: Path,
) -> tuple[Path, dict[str, Any]]:
    runtime_path = _acceptance_runtime_path(project_root, str(envelope.get("feature") or ""))
    runtime_payload = {
        "schema_version": "1.0",
        "artifact": "qa_acceptance_runtime_projection",
        "version": str(envelope.get("version") or ""),
        "feature": str(envelope.get("feature") or ""),
        "feature_slug": str(envelope.get("feature_slug") or ""),
        "revision_id": str(envelope.get("revision_id") or ""),
        "verdict": str(envelope.get("verdict") or ""),
        "transaction_id": str(envelope.get("transaction_id") or ""),
        "source_hash": str(envelope.get("source_hash") or ""),
        "projection_seq": envelope.get("projection_seq"),
        "committed_at": now_iso(),
        "write_status": "applied",
        "failed_sinks": [],
        "machine_ref": str(machine_path.relative_to(project_root)),
        "markdown_ref": str(human_path.relative_to(project_root)),
        "runtime_projection_ref": str(runtime_path.relative_to(project_root)),
        "sink_checksums": {
            "machine": str(((envelope.get("sink_checksums") or {}).get("machine")) or "missing"),
            "human": str(((envelope.get("sink_checksums") or {}).get("human")) or "missing"),
            "runtime": "pending",
        },
    }
    write_json(runtime_path, runtime_payload)
    runtime_payload["sink_checksums"]["runtime"] = _stable_file_hash(runtime_path) or "missing"
    write_json(runtime_path, runtime_payload)
    return runtime_path, runtime_payload


def acceptance_projection_transaction_contract(
    project_root: Path,
    *,
    version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    resolved_feature = str(feature or "").strip()
    resolved_version = str(version or "").strip()
    if not resolved_feature:
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "acceptance_feature_missing",
            "message": "acceptance transaction contract requires a resolved feature",
            "details": {},
        }

    machine_path = _acceptance_machine_path(project_root, resolved_version, resolved_feature) if resolved_version else None
    if not machine_path or not machine_path.exists():
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "acceptance_transaction_missing",
            "message": "qa acceptance envelope is missing",
            "details": {
                "machine_ref": str(machine_path.relative_to(project_root)) if machine_path else "",
            },
        }

    try:
        envelope = json.loads(machine_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        envelope = {}
    if not isinstance(envelope, dict) or not envelope:
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "acceptance_transaction_corrupt",
            "message": "qa acceptance envelope is unreadable",
            "details": {"machine_ref": str(machine_path.relative_to(project_root))},
        }

    markdown_ref = str(envelope.get("markdown_ref") or "")
    runtime_ref = str(envelope.get("runtime_projection_ref") or "")
    markdown_path = project_root / markdown_ref if markdown_ref else None
    runtime_path = project_root / runtime_ref if runtime_ref else _acceptance_runtime_path(project_root, resolved_feature)
    if not runtime_ref:
        runtime_ref = str(runtime_path.relative_to(project_root))
    if not markdown_path or not markdown_path.exists() or not runtime_path.exists():
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "acceptance_projection_missing",
            "message": "qa acceptance transaction is missing one or more sinks",
            "details": {
                "machine_ref": str(machine_path.relative_to(project_root)),
                "markdown_ref": markdown_ref,
                "runtime_projection_ref": runtime_ref,
            },
        }

    try:
        runtime_payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        runtime_payload = {}
    if not isinstance(runtime_payload, dict) or not runtime_payload:
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "acceptance_projection_corrupt",
            "message": "qa acceptance runtime projection is unreadable",
            "details": {"runtime_projection_ref": runtime_ref},
        }

    if str(runtime_payload.get("write_status") or "").strip().lower() == "failed_transaction":
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "acceptance_projection_failed_transaction",
            "message": "qa acceptance runtime projection failed",
            "details": runtime_payload,
        }

    envelope_checksums = envelope.get("sink_checksums") if isinstance(envelope.get("sink_checksums"), dict) else {}
    runtime_checksums = runtime_payload.get("sink_checksums") if isinstance(runtime_payload.get("sink_checksums"), dict) else {}
    metadata_keys = ("transaction_id", "source_hash", "projection_seq")
    metadata_match = all(
        str(envelope.get(key) or "") == str(runtime_payload.get(key) or "")
        for key in metadata_keys
    )
    checksum_match = (
        str(envelope_checksums.get("machine") or "") == str(runtime_checksums.get("machine") or "")
        and str(envelope_checksums.get("human") or "") == str(runtime_checksums.get("human") or "")
        and str(envelope_checksums.get("runtime") or "") == str(runtime_checksums.get("runtime") or "")
    )
    checksum_present = all(
        str(runtime_checksums.get(name) or "") not in {"", "missing", "failed", "pending"}
        for name in ("machine", "human", "runtime")
    )
    if not metadata_match or not checksum_match or not checksum_present:
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "acceptance_projection_drift",
            "message": "qa acceptance transaction drift detected across sinks",
            "details": {
                "machine_ref": str(machine_path.relative_to(project_root)),
                "markdown_ref": markdown_ref,
                "runtime_projection_ref": runtime_ref,
                "envelope": envelope,
                "runtime_projection": runtime_payload,
            },
        }

    return {
        "status": "pass",
        "blocked": False,
        "reason_code": "acceptance_projection_transaction_ok",
        "message": "qa acceptance transaction metadata is consistent",
        "details": {
            "machine_ref": str(machine_path.relative_to(project_root)),
            "markdown_ref": markdown_ref,
            "runtime_projection_ref": runtime_ref,
            "transaction_id": str(envelope.get("transaction_id") or ""),
            "source_hash": str(envelope.get("source_hash") or ""),
            "projection_seq": envelope.get("projection_seq"),
        },
    }


def _workflow_stage_evidence(project_root: Path, *, version: str, feature: str) -> dict[str, list[str]]:
    slug = feature_slug(feature)
    docs_root = project_root / "docs" / "beacon" / version
    execution_root = docs_root / "execution"
    machine_root = docs_root / ".machine"
    machine_execution_root = machine_execution_dir(project_root, version)
    prototype = prototype_files(project_root, version, feature)
    state_root = project_root / ".beacon" / "state"
    qa_root = project_root / ".beacon" / "qa" / "features" / slug

    think_refs = _existing_relative_paths(
        project_root,
        [
            docs_root / "SUMMARY.md",
            execution_root / "index.md",
            execution_root / "architecture-blueprint.md",
        ],
    )
    requirement_refs = requirement_truth_paths(
        project_root,
        version=version,
        feature=feature,
        consumer="acceptance-workflow-closure",
    )
    user_story_refs = _existing_relative_paths(
        project_root,
        [
            requirement_refs["user_story"],
            machine_root / "user-story" / f"{slug}.json",
        ],
    )
    prd_refs = _existing_relative_paths(
        project_root,
        [
            requirement_refs["prd"],
            machine_root / "execution" / f"{slug}.revision.json",
        ],
    )
    prototype_refs = _existing_relative_paths(
        project_root,
        [
            prototype["prototype_plan"],
            prototype["manifest"],
            prototype["review_json"],
            prototype["freeze"],
        ],
    )
    test_case_refs = _existing_relative_paths(
        project_root,
        [
            requirement_refs["test_case"],
            machine_root / "qa" / f"{slug}.ac-test-matrix.json",
            machine_root / "qa" / f"{slug}.qa9-matrix.json",
            machine_root / "qa" / f"{slug}.story-scenario-map.json",
        ],
    )
    implement_refs = _existing_relative_paths(
        project_root,
        [
            machine_trace_dir(project_root, version, "implementation", slug) / f"technical-implementation-{slug}.md",
            machine_execution_root / f"technical-implementation-{slug}.json",
            execution_root / f"implementation-brief-{slug}.md",
            machine_execution_root / f"implementation-summary-{slug}.json",
            state_root / f"implementation-{slug}.json",
        ],
    )
    qa_refs = _existing_relative_paths(
        project_root,
        [
            project_root / ".beacon" / "auto-test-status.json",
            execution_root / f"review-quality-{slug}.md",
            machine_execution_root / f"review-quality-{slug}.json",
            execution_root / f"review-spec-{slug}.md",
            machine_execution_root / f"review-spec-{slug}.json",
            qa_root / "scorecard.json",
        ],
    )
    release_refs = _existing_relative_paths(
        project_root,
        [
            project_root / ".beacon" / "gate-report.json",
            project_root / ".beacon" / "evidence-manifest.json",
            machine_execution_root / "terminal.json",
        ],
    )

    return {
        "think": think_refs,
        "user-story": user_story_refs,
        "prd": prd_refs,
        "prototype": prototype_refs,
        "test-case": test_case_refs,
        "implement": implement_refs,
        "implementation": implement_refs,
        "qa": qa_refs,
        "verify": qa_refs,
        "review": qa_refs,
        "release": release_refs,
        "gate": release_refs,
        "delivery": release_refs,
    }


def _update_items(
    items: list[dict[str, Any]],
    *,
    target_ids: set[str],
    field: str,
    value: str,
    status: str,
    revision_id: str,
) -> int:
    updated = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", "") or "").upper()
        if target_ids and item_id not in target_ids:
            continue
        item["status"] = status
        item[field] = value
        item["changed_in_revision"] = revision_id
        updated += 1
    return updated


def record_implementation_writeback(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str,
    implemented_item_ids: Iterable[str] | None = None,
    task_ids: Iterable[str] | None = None,
    changed_files: Iterable[str] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True, revision_id=str(revision.get("revision_id", "R1")))
    target_ids = _normalize_ids(implemented_item_ids)
    updated = _update_items(
        story.get("items", []),
        target_ids=target_ids,
        field="implemented_by_run_id",
        value=run_id,
        status="implemented",
        revision_id=str(revision.get("revision_id", "R1")),
    )
    story["status"] = "implemented" if updated else story.get("status", "draft")
    story["last_changed_files"] = [str(x) for x in (changed_files or []) if str(x).strip()]
    save_story_state(project_root, version=resolved_version, feature=feature, state=story)

    revision["delivery_status"] = "implemented"
    revision["last_implementation_run_id"] = run_id
    if changed_files is not None:
        revision["changed_files"] = [str(x) for x in changed_files if str(x).strip()]
    save_revision_state(project_root, version=resolved_version, feature=feature, state=revision)
    append_implementation_writeback_event(
        project_root,
        version=resolved_version,
        feature=feature,
        revision_id=str(revision.get("revision_id", "R1") or "R1"),
        run_id=run_id,
        implemented_item_ids=target_ids,
        changed_files=changed_files,
    )
    plan = update_plan_progress_for_implementation(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        implemented_item_ids=target_ids,
        task_ids=task_ids,
        changed_files=changed_files,
    )
    return {"updated_items": updated, "story": story, "revision": revision, "implementation_plan": plan}


def record_verification_writeback(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str,
    verified_item_ids: Iterable[str] | None = None,
    failed_item_ids: Iterable[str] | None = None,
    evidence_ref: Iterable[str] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True, revision_id=str(revision.get("revision_id", "R1")))
    verified_ids = _normalize_ids(verified_item_ids)
    failed_ids = _normalize_ids(failed_item_ids)
    verified = 0
    failed = 0
    for item in story.get("items", []):
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", "") or "").upper()
        if item_id in failed_ids:
            item["status"] = "failed"
            item["verified_by_run_id"] = run_id
            item["changed_in_revision"] = str(revision.get("revision_id", "R1"))
            failed += 1
            continue
        if item_id in verified_ids:
            kind = str(item.get("kind", ""))
            item["status"] = "passed" if kind == "test" else "verified"
            item["verified_by_run_id"] = run_id
            item["changed_in_revision"] = str(revision.get("revision_id", "R1"))
            verified += 1
    story["verification_evidence"] = [str(x) for x in (evidence_ref or []) if str(x).strip()]
    verification_complete = _is_story_verification_complete([item for item in story.get("items", []) if isinstance(item, dict)])
    current_story_status = str(story.get("status", "draft") or "draft")
    if failed > 0:
        story["status"] = "blocked"
    elif verification_complete:
        story["status"] = "verified"
    elif current_story_status in {"implemented", "verified", "accepted", "released"}:
        story["status"] = current_story_status if current_story_status != "verified" else "implemented"
    else:
        story["status"] = "implemented" if verified > 0 else current_story_status
    save_story_state(project_root, version=resolved_version, feature=feature, state=story)

    current_delivery_status = str(revision.get("delivery_status", "") or "")
    if failed > 0:
        revision["delivery_status"] = "blocked"
    elif verification_complete:
        revision["delivery_status"] = "verified"
    elif current_delivery_status in {"implemented", "verified", "accepted", "released"}:
        revision["delivery_status"] = current_delivery_status if current_delivery_status != "verified" else "implemented"
    elif verified > 0:
        revision["delivery_status"] = "implemented"
    revision["last_verification_run_id"] = run_id
    revision["verification_evidence"] = [str(x) for x in (evidence_ref or []) if str(x).strip()]
    save_revision_state(project_root, version=resolved_version, feature=feature, state=revision)
    plan = update_plan_progress_for_verification(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        verified_item_ids=verified_ids,
        failed_item_ids=failed_ids,
        evidence_refs=evidence_ref,
    )
    return {"verified_items": verified, "failed_items": failed, "story": story, "revision": revision, "implementation_plan": plan}


def record_acceptance_writeback(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    accepted_by: str = "system",
    verdict: str = "passed",
    run_id: str = "",
    evidence_ref: Iterable[str] | None = None,
    source_command: str = "",
    accepted_ac_ids: Iterable[str] | None = None,
    accepted_test_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    if str(revision.get("doc_status", "draft")) != "frozen":
        raise ValueError("acceptance_revision_not_frozen")
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True, revision_id=str(revision.get("revision_id", "R1") or "R1"))
    items = [item for item in story.get("items", []) if isinstance(item, dict)]
    required_acs = [i for i in items if i.get("kind") == "ac" and bool(i.get("required", True))]
    required_tests = [i for i in items if i.get("kind") == "test" and bool(i.get("required", True))]
    accepted_ac_set = _normalize_ids(accepted_ac_ids)
    accepted_test_set = _normalize_ids(accepted_test_ids)
    target_acs = [i for i in required_acs if not accepted_ac_set or str(i.get("id", "") or "").upper() in accepted_ac_set]
    target_tests = [i for i in required_tests if not accepted_test_set or str(i.get("id", "") or "").upper() in accepted_test_set]
    if any(str(i.get("status", "")) != "verified" for i in target_acs):
        raise ValueError("acceptance_ac_not_verified")
    if any(str(i.get("status", "")) not in {"passed", "verified"} for i in target_tests):
        raise ValueError("acceptance_tests_not_passed")
    accepted_at = now_iso()
    updated_items: list[dict[str, Any]] = []
    for item in items:
        updated_item = dict(item)
        item_id = str(item.get("id", "") or "").upper()
        item_kind = str(item.get("kind", "") or "")
        if item_kind == "ac" and accepted_ac_set and item_id not in accepted_ac_set:
            updated_items.append(updated_item)
            continue
        if item_kind == "test" and accepted_test_set and item_id not in accepted_test_set:
            updated_items.append(updated_item)
            continue
        if str(item.get("status", "")).lower() in {"verified", "implemented", "passed"}:
            updated_item["status"] = "accepted"
            updated_item["accepted_at"] = accepted_at
            updated_item["changed_in_revision"] = str(revision.get("revision_id", "R1"))
        updated_items.append(updated_item)
    evidence_refs = _existing_relative_paths(project_root, [project_root / str(item) for item in (evidence_ref or [])])
    if not evidence_refs:
        evidence_refs = [str(item) for item in (evidence_ref or []) if str(item).strip()]
    requirement_refs = _acceptance_requirement_refs(project_root, version=resolved_version, feature=feature)
    test_case_refs = [ref for ref in requirement_refs if "/qa/test-cases/" in ref]
    machine_path = _acceptance_machine_path(project_root, resolved_version, feature)
    human_path = _acceptance_human_path(project_root, resolved_version, feature)
    projection_seq: Any = _acceptance_projection_seq(machine_path)
    transaction = None
    if run_id:
        transaction = record_stage_writeback(
            project_root,
            run_id=run_id,
            stage="qa",
            feature=feature,
            evidence_ref=evidence_refs,
            status="accepted",
        )
    transaction_metadata = transaction.get("metadata") if isinstance(transaction, dict) and isinstance(transaction.get("metadata"), dict) else {}
    source_payload = {
        "version": resolved_version,
        "feature": feature,
        "revision_id": str(revision.get("revision_id", "") or ""),
        "verdict": verdict,
        "accepted_at": accepted_at,
        "accepted_by": accepted_by,
        "run_id": run_id,
        "evidence_refs": evidence_refs,
        "requirement_refs": requirement_refs,
    }
    source_hash = str(transaction_metadata.get("source_hash", "") or "") if transaction_metadata else _stable_hash(source_payload)
    transaction_id = str(transaction_metadata.get("transaction_id", "") or "") if transaction_metadata else f"tx-qa-acceptance-{feature_slug(feature)}-{source_hash.split(':')[-1][:12]}"
    if transaction_metadata and transaction_metadata.get("projection_seq") not in (None, ""):
        projection_seq = transaction_metadata.get("projection_seq")
    envelope = {
        "schema_version": "1.0",
        "artifact": "qa_acceptance_envelope",
        "version": resolved_version,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "revision_id": str(revision.get("revision_id", "") or ""),
        "verdict": verdict,
        "accepted_at": accepted_at,
        "accepted_by": accepted_by,
        "run_id": run_id,
        "transaction_id": transaction_id,
        "source_hash": source_hash,
        "projection_seq": projection_seq,
        "source_command": source_command or f'beacon qa run "{feature}" --project-root . --version {resolved_version}',
        "requirement_refs": requirement_refs,
        "test_case_refs": test_case_refs,
        "evidence_refs": evidence_refs,
        "story_status": str(story.get("status", "") or ""),
        "revision_delivery_status": str(revision.get("delivery_status", "") or ""),
        "required_ac_count": len(target_acs),
        "required_test_count": len(target_tests),
        "canonical_envelope_ref": str(machine_path.relative_to(project_root)),
        "markdown_ref": str(human_path.relative_to(project_root)),
        "transaction_lineage": {
            "current_transaction_id": transaction_id,
            "projection_seq": projection_seq,
            "source_hash": source_hash,
            "workflow_memory_ref": str(lifecycle_path(project_root).relative_to(project_root)) if run_id else "",
            "memory_event_id": "",
            "memory_entry_id": str(transaction.get("memory_id", "") or "") if isinstance(transaction, dict) else "",
        },
    }
    write_json(machine_path, envelope)
    human_path.parent.mkdir(parents=True, exist_ok=True)
    human_path.write_text(_render_acceptance_markdown(envelope), encoding="utf-8")
    envelope["sink_checksums"] = {
        "machine": _stable_hash(json.loads(machine_path.read_text(encoding="utf-8"))),
        "human": _stable_hash({"markdown": human_path.read_text(encoding="utf-8")}),
        "runtime": "pending",
    }
    try:
        runtime_path, runtime_payload = _write_acceptance_runtime_projection(
            project_root,
            envelope=envelope,
            machine_path=machine_path,
            human_path=human_path,
        )
    except Exception as exc:  # noqa: BLE001
        runtime_path = _acceptance_runtime_path(project_root, feature)
        failure_payload = {
            "schema_version": "1.0",
            "artifact": "qa_acceptance_runtime_projection",
            "version": resolved_version,
            "feature": feature,
            "feature_slug": feature_slug(feature),
            "revision_id": str(revision.get("revision_id", "") or ""),
            "verdict": verdict,
            "transaction_id": transaction_id,
            "source_hash": source_hash,
            "projection_seq": projection_seq,
            "committed_at": "",
            "write_status": "failed_transaction",
            "failed_sinks": ["runtime"],
            "error": str(exc),
            "machine_ref": str(machine_path.relative_to(project_root)),
            "markdown_ref": str(human_path.relative_to(project_root)),
            "runtime_projection_ref": str(runtime_path.relative_to(project_root)),
            "sink_checksums": {
                "machine": str(envelope["sink_checksums"].get("machine") or "missing"),
                "human": str(envelope["sink_checksums"].get("human") or "missing"),
                "runtime": "failed",
            },
        }
        try:
            write_json(runtime_path, failure_payload)
        except Exception:  # noqa: BLE001
            pass
        envelope["runtime_projection_ref"] = str(runtime_path.relative_to(project_root))
        envelope["transaction_status"] = "failed_transaction"
        envelope["failed_sinks"] = ["runtime"]
        envelope["sink_checksums"]["runtime"] = "failed"
        write_json(machine_path, envelope)
        human_path.write_text(_render_acceptance_markdown(envelope), encoding="utf-8")
        raise ValueError(f"acceptance_runtime_projection_failed: {exc}") from exc

    envelope["runtime_projection_ref"] = str(runtime_path.relative_to(project_root))
    envelope["transaction_status"] = str(runtime_payload.get("write_status") or "applied")
    envelope["failed_sinks"] = list(runtime_payload.get("failed_sinks") or [])
    envelope["sink_checksums"]["runtime"] = str(((runtime_payload.get("sink_checksums") or {}).get("runtime")) or "missing")
    write_json(machine_path, envelope)
    human_path.write_text(_render_acceptance_markdown(envelope), encoding="utf-8")
    write_acceptance_kit_projection(
        project_root,
        version=resolved_version,
        feature=feature,
        acceptance_envelope=envelope,
    )

    story["items"] = updated_items
    story["status"] = "accepted"
    story["accepted_at"] = accepted_at
    story["accepted_by"] = accepted_by
    save_story_state(project_root, version=resolved_version, feature=feature, state=story)

    revision["delivery_status"] = "accepted"
    revision["lifecycle_status"] = "accepted"
    revision["accepted_at"] = accepted_at
    revision["accepted_by"] = accepted_by
    save_revision_state(project_root, version=resolved_version, feature=feature, state=revision)
    plan = mark_implementation_plan_accepted(
        project_root,
        version=resolved_version,
        feature=feature,
        accepted_by=accepted_by,
    )
    return {
        "story": story,
        "revision": revision,
        "implementation_plan": plan,
        "acceptance_envelope": envelope,
        "machine_path": str(machine_path.relative_to(project_root)),
        "markdown_path": str(human_path.relative_to(project_root)),
        "runtime_path": str(runtime_path.relative_to(project_root)),
    }


def sync_acceptance_workflow_closure(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str | None = None,
    source: str = "review.accept.sync",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    resolved_run_id = resolve_workflow_run_id(
        project_root,
        run_id=run_id,
        version=resolved_version,
        feature=feature,
    )
    if not resolved_run_id:
        return {
            "run_id": "",
            "version": resolved_version,
            "feature": feature,
            "synced_stages": [],
            "closure_complete": False,
            "gate_pass": False,
            "reason": "run_not_found",
        }

    run_state = load_run_state(project_root, resolved_run_id) or {}
    stage_order = workflow_stages_for_run(project_root, run_id=resolved_run_id, run_state=run_state)
    stage_evidence = _workflow_stage_evidence(project_root, version=resolved_version, feature=feature)
    progress = compute_workflow_progress(
        project_root,
        run_id=resolved_run_id,
        version=resolved_version,
        feature=feature,
    )
    synced_stages: list[str] = []

    for stage in stage_order:
        refs = stage_evidence.get(stage, [])
        if not refs:
            continue
        stage_state = progress.get("stages", {}).get(stage, {}) if isinstance(progress.get("stages"), dict) else {}
        changed = False
        if not bool(stage_state.get("has_started")):
            append_lifecycle_event(
                project_root,
                run_id=resolved_run_id,
                stage=stage,
                event="stage_started",
                source=source,
                evidence_ref=refs,
                details={"backfilled": True, "feature": feature, "version": resolved_version},
            )
            changed = True
        if not bool(stage_state.get("has_context")):
            write_stage_context(
                project_root,
                run_id=resolved_run_id,
                stage=stage,
                feature=feature,
            )
            changed = True
        if not bool(stage_state.get("has_finished")):
            append_lifecycle_event(
                project_root,
                run_id=resolved_run_id,
                stage=stage,
                event="stage_finished",
                source=source,
                evidence_ref=refs,
                details={"backfilled": True, "feature": feature, "version": resolved_version},
            )
            changed = True
        if not bool(stage_state.get("has_writeback")):
            record_stage_writeback(
                project_root,
                run_id=resolved_run_id,
                stage=stage,
                feature=feature,
                evidence_ref=refs,
                status="completed",
            )
            changed = True
        if changed:
            synced_stages.append(stage)
            progress = compute_workflow_progress(
                project_root,
                run_id=resolved_run_id,
                version=resolved_version,
                feature=feature,
            )

    final_progress = compute_workflow_progress(
        project_root,
        run_id=resolved_run_id,
        version=resolved_version,
        feature=feature,
    )
    if bool(final_progress.get("closure_complete")) and bool(final_progress.get("gate_pass")):
        updated_state = dict(run_state)
        updated_state["status"] = "completed"
        updated_state["reason"] = "synced_from_acceptance"
        updated_state["ended_at"] = now_iso()
        events = updated_state.get("events")
        if not isinstance(events, list):
            events = []
        if not any(isinstance(item, dict) and str(item.get("event", "")) == "workflow_completed" for item in events):
            events.append({"event": "workflow_completed", "ts": now_iso()})
        updated_state["events"] = events
        save_run_state(project_root, resolved_run_id, updated_state)

    return {
        "run_id": resolved_run_id,
        "version": resolved_version,
        "feature": feature,
        "synced_stages": synced_stages,
        "closure_complete": bool(final_progress.get("closure_complete")),
        "gate_pass": bool(final_progress.get("gate_pass")),
        "missing_closure_stages": final_progress.get("missing_closure_stages", []),
    }
