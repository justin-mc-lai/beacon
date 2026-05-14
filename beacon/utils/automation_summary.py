"""Shared automation summary schema and rendering helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json


def _load_json(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def _normalize_name_list(values: list[str] | None) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values or []:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def _entry_reconciliation(entry: dict[str, Any]) -> dict[str, Any]:
    summary = entry.get("summary") if isinstance(entry.get("summary"), dict) else {}
    feature_scorecard = entry.get("feature_scorecard") if isinstance(entry.get("feature_scorecard"), dict) else {}
    reconciliation = entry.get("reconciliation") if isinstance(entry.get("reconciliation"), dict) else (
        feature_scorecard.get("reconciliation") if isinstance(feature_scorecard.get("reconciliation"), dict) else {}
    )
    required = bool(
        reconciliation.get("required", False)
        or summary.get("reconciliation_required", False)
        or "implementation_first_reconciliation_required" in [
            str(item).strip()
            for item in (
                feature_scorecard.get("stop_reasons")
                or entry.get("reason_codes")
                or summary.get("stop_reasons")
                or []
            )
            if str(item).strip()
        ]
    )
    reason_code = str(
        reconciliation.get("reason_code")
        or summary.get("reconciliation_reason_code")
        or ("implementation_first_reconciliation_required" if required else "")
    ).strip()
    artifact_path = str(reconciliation.get("artifact_path") or summary.get("reconciliation_artifact_path") or "").strip()
    reprojection_targets = _normalize_name_list(
        list(((reconciliation.get("artifact") or {}).get("reprojection_targets")) or [])
        or list(summary.get("reconciliation_reprojection_targets") or [])
    )
    return {
        "required": required,
        "reason_code": reason_code,
        "artifact_path": artifact_path,
        "reprojection_targets": reprojection_targets,
    }


def _status_rank(status: str) -> int:
    lowered = str(status or "").strip().lower()
    if lowered in {"failed", "error"}:
        return 4
    if lowered in {"blocked", "repair_needed"}:
        return 3
    if lowered in {"warning", "warn", "partial"}:
        return 2
    if lowered in {"passed", "success"}:
        return 1
    return 0


def _derive_status(
    *,
    explicit_status: str,
    failure_count: int,
    blocked_count: int,
    statuses: list[str],
) -> str:
    text = str(explicit_status or "").strip().lower()
    if text:
        return text
    if failure_count > 0:
        return "failed"
    if blocked_count > 0:
        return "blocked"
    if statuses and all(item == "passed" for item in statuses):
        return "passed"
    if statuses:
        return "warning"
    return "unknown"


def _build_analysis_line(
    *,
    tests: int | None,
    failures: int | None,
    skipped: int | None,
    feature_count: int,
    release_ready_count: int,
    repair_count: int,
    queue_update_count: int | None,
) -> str:
    parts: list[str] = []
    if tests is not None:
        parts.append(f"{tests} tests")
    if failures is not None:
        parts.append(f"{failures} failures")
    if skipped is not None:
        parts.append(f"{skipped} skipped")
    if feature_count:
        parts.append(f"{feature_count} features checked")
    if release_ready_count:
        parts.append(f"{release_ready_count} release-ready")
    if repair_count:
        parts.append(f"{repair_count} repair-needed")
    if queue_update_count is not None:
        parts.append(f"{queue_update_count} queue updates")
    return ", ".join(parts) + "." if parts else "No automation evidence captured."


def build_automation_summary_payload(
    *,
    project_root: Path,
    summary_kind: str,
    job: str,
    layer: str,
    status: str = "",
    ledger_path: Path | None = None,
    queue_update_path: Path | None = None,
    tests: int | None = None,
    failures: int | None = None,
    skipped: int | None = None,
    artifacts: dict[str, str] | None = None,
    features: list[str] | None = None,
    release_ready_features: list[str] | None = None,
    repair_features: list[str] | None = None,
    title: str = "",
) -> dict[str, Any]:
    root = project_root.resolve()
    ledger = _load_json(ledger_path)
    queue_update = _load_json(queue_update_path)
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), list) else []

    entry_features = [
        str(entry.get("feature") or entry.get("feature_slug") or "").strip()
        for entry in entries
        if isinstance(entry, dict)
    ]
    entry_statuses = [
        str(entry.get("status") or "unknown").strip().lower()
        for entry in entries
        if isinstance(entry, dict)
    ]
    entry_release_ready = [
        str(entry.get("feature") or entry.get("feature_slug") or "").strip()
        for entry in entries
        if isinstance(entry, dict) and bool(entry.get("release_ready"))
    ]
    entry_repair = [
        str(entry.get("feature") or entry.get("feature_slug") or "").strip()
        for entry in entries
        if isinstance(entry, dict)
        and (
            str(entry.get("continue_decision") or "").strip() == "stop_for_repair"
            or str(entry.get("status") or "").strip().lower() in {"failed", "blocked"}
        )
    ]
    entry_reconciliation = [
        {
            "feature": str(entry.get("feature") or entry.get("feature_slug") or "").strip(),
            **_entry_reconciliation(entry),
        }
        for entry in entries
        if isinstance(entry, dict) and _entry_reconciliation(entry).get("required")
    ]
    failed_features = [
        str(entry.get("feature") or entry.get("feature_slug") or "").strip()
        for entry in entries
        if isinstance(entry, dict) and str(entry.get("status") or "").strip().lower() == "failed"
    ]
    blocked_features = [
        str(entry.get("feature") or entry.get("feature_slug") or "").strip()
        for entry in entries
        if isinstance(entry, dict) and str(entry.get("status") or "").strip().lower() == "blocked"
    ]

    normalized_features = _normalize_name_list(features or entry_features)
    normalized_release_ready = _normalize_name_list(release_ready_features or entry_release_ready)
    normalized_repair = _normalize_name_list(repair_features or entry_repair)
    normalized_reconciliation = _normalize_name_list([str(item.get("feature") or "").strip() for item in entry_reconciliation])
    reconciliation_targets = _normalize_name_list(
        [
            str(target).strip()
            for item in entry_reconciliation
            for target in (item.get("reprojection_targets") or [])
            if str(target).strip()
        ]
    )
    normalized_failed = _normalize_name_list(failed_features)
    normalized_blocked = _normalize_name_list(blocked_features)
    queue_update_count = int(queue_update.get("update_count") or 0) if queue_update else 0
    failure_count = failures if failures is not None else len(normalized_failed)
    blocked_count = len(normalized_blocked)
    resolved_status = _derive_status(
        explicit_status=status,
        failure_count=failure_count or 0,
        blocked_count=blocked_count,
        statuses=entry_statuses,
    )
    headline = title or f"[{root.name}] {layer or job} {resolved_status}"
    analysis_line = _build_analysis_line(
        tests=tests,
        failures=failures,
        skipped=skipped,
        feature_count=len(normalized_features),
        release_ready_count=len(normalized_release_ready),
        repair_count=len(normalized_repair),
        queue_update_count=queue_update_count,
    )
    if normalized_reconciliation:
        analysis_line = analysis_line.rstrip(".") + f", {len(normalized_reconciliation)} reconciliation-required."

    artifact_payload: dict[str, str] = {}
    for key, value in (artifacts or {}).items():
        name = str(key or "").strip()
        path_text = str(value or "").strip()
        if name and path_text:
            artifact_payload[name] = path_text
    if ledger_path:
        artifact_payload.setdefault("qa_feedback_ledger", str(ledger_path))
    if queue_update_path:
        artifact_payload.setdefault("queue_update", str(queue_update_path))

    notification_lines = [
        analysis_line,
        f"job={job}",
        f"layer={layer}",
        f"status={resolved_status}",
    ]
    if tests is not None:
        notification_lines.append(f"tests={tests}")
    if failures is not None:
        notification_lines.append(f"failures={failures}")
    if skipped is not None:
        notification_lines.append(f"skipped={skipped}")
    notification_lines.extend(
        [
            f"feature_count={len(normalized_features)}",
            f"release_ready={', '.join(normalized_release_ready) or '-'}",
            f"repair_features={', '.join(normalized_repair) or '-'}",
            f"reconciliation_required={', '.join(normalized_reconciliation) or '-'}",
            f"reprojection_targets={', '.join(reconciliation_targets) or '-'}",
            f"queue_update_count={queue_update_count}",
        ]
    )
    for name, value in artifact_payload.items():
        notification_lines.append(f"{name}={value}")

    return {
        "schema_version": "1.0",
        "summary_kind": str(summary_kind or "").strip() or "qa",
        "project_root": str(root),
        "project_name": root.name,
        "job": str(job or "").strip(),
        "layer": str(layer or "").strip(),
        "status": resolved_status,
        "generated_at": now_iso(),
        "analysis": {
            "headline": headline,
            "summary_line": analysis_line,
        },
        "metrics": {
            "tests": tests,
            "failures": failures,
            "skipped": skipped,
            "feature_count": len(normalized_features),
            "failed_feature_count": len(normalized_failed),
            "blocked_feature_count": len(normalized_blocked),
            "release_ready_feature_count": len(normalized_release_ready),
            "repair_feature_count": len(normalized_repair),
            "queue_update_count": queue_update_count,
            "status_rank": _status_rank(resolved_status),
        },
        "features": {
            "all": normalized_features,
            "release_ready": normalized_release_ready,
            "repair_needed": normalized_repair,
            "reconciliation_required": normalized_reconciliation,
            "failed": normalized_failed,
            "blocked": normalized_blocked,
        },
        "reconciliation": {
            "required_feature_count": len(normalized_reconciliation),
            "required_features": normalized_reconciliation,
            "reprojection_targets": reconciliation_targets,
            "entries": entry_reconciliation,
        },
        "artifacts": artifact_payload,
        "notification": {
            "title": headline,
            "lines": notification_lines,
        },
    }
