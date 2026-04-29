"""Friction intake support surface and sqlite queue governance helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from beacon.utils.memory_friction_evolution import (
    _friction_candidates_from_issues,
    _merge_candidate_rows,
)
from beacon.utils.runtime import now_iso, read_json, utc_compact_ts, write_json
from beacon.utils.runtime_projection_store import (
    list_friction_items,
    transition_friction_item,
    write_friction_queue_batch,
)
from beacon.utils.versioning import resolve_target_version

SUPPORTED_FRICTION_INTAKE_MODES: tuple[str, ...] = ("scan", "capture")
FRICTION_INTAKE_TOOL = "beacon-friction-intake"


def _analysis_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "analysis"


def _state_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "friction-intake"


def _latest_state_path(project_root: Path) -> Path:
    return _state_dir(project_root) / "latest.json"


def _trim(value: str, *, limit: int = 180) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _candidate_id(source_type: str, summary: str) -> str:
    digest = hashlib.sha256(f"{source_type}::{summary}".encode("utf-8")).hexdigest()[:12]
    return f"friction:{digest}"


def _classify_item(summary: str) -> tuple[str, str, str]:
    text = str(summary or "").strip().lower()
    item_class = "improvement"
    if any(token in text for token in ("阻塞", "blocked", "blocker", "bug", "error", "失败", "fail", "crash")):
        item_class = "blocking_bug"
    elif any(token in text for token in ("优化", "optimiz", "performance", "perf", "latency")):
        item_class = "optimization_enhancement"

    severity = "P3"
    if any(token in text for token in ("data loss", "security", "crash", "p0")):
        severity = "P0"
    elif item_class == "blocking_bug":
        severity = "P1"
    elif any(token in text for token in ("qa", "release", "host runtime", "runtime", "implement")):
        severity = "P2"

    domain = "workflow"
    domain_rules = (
        ("host_runtime", ("host runtime", "runtime", "codex", "claude")),
        ("memory", ("memory", "记忆")),
        ("skill", ("skill", "技能")),
        ("implement", ("implement", "implementation", "编码", "开发")),
        ("qa", ("qa", "验收", "测试")),
        ("release", ("release", "发布")),
        ("docs", ("docs", "documentation", "文档")),
        ("prompt", ("prompt", "提示词")),
        ("workflow", ("workflow", "流程", "route", "routing")),
    )
    for candidate_domain, markers in domain_rules:
        if any(marker in text for marker in markers):
            domain = candidate_domain
            break
    return item_class, severity, domain


def _scan_candidates(project_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    candidates, refs = _friction_candidates_from_issues(project_root)
    normalized: list[dict[str, Any]] = []
    for row in candidates:
        if not isinstance(row, dict):
            continue
        summary = str(row.get("friction_summary") or "").strip()
        item_class, severity, domain = _classify_item(summary)
        normalized.append(
            {
                "item_id": str(row.get("candidate_id") or _candidate_id("scan", summary)),
                "candidate_id": str(row.get("candidate_id") or _candidate_id("scan", summary)),
                "summary": summary,
                "friction_summary": summary,
                "evidence_refs": list(row.get("evidence_refs") or []),
                "item_class": item_class,
                "severity": severity,
                "domain": domain,
                "queue_status": "queued",
                "source_type": "scan",
                "recommended_command": str(row.get("recommended_command") or ""),
            }
        )
    return _merge_candidate_rows(normalized), refs


def _capture_candidates(project_root: Path, note: str) -> tuple[list[dict[str, Any]], list[str]]:
    summary = _trim(note, limit=180)
    item_class, severity, domain = _classify_item(summary)
    note_hash = hashlib.sha256(summary.encode("utf-8")).hexdigest()[:12]
    notes_dir = project_root / ".beacon" / "debug" / "friction-captures"
    notes_dir.mkdir(parents=True, exist_ok=True)
    note_path = notes_dir / f"{note_hash}.json"
    payload = {
        "schema_version": "1.0",
        "captured_at": now_iso(),
        "summary": summary,
        "raw_note": str(note),
        "item_class": item_class,
        "severity": severity,
        "domain": domain,
    }
    write_json(note_path, payload)
    rel = str(note_path.relative_to(project_root))
    candidate = {
        "item_id": _candidate_id("manual_capture", summary),
        "candidate_id": _candidate_id("manual_capture", summary),
        "summary": summary,
        "friction_summary": summary,
        "evidence_refs": [rel],
        "item_class": item_class,
        "severity": severity,
        "domain": domain,
        "queue_status": "queued",
        "source_type": "manual_capture",
        "recommended_command": "beacon friction-intake inbox --project-root . --json",
    }
    return [candidate], [rel]


def _render_markdown(payload: dict[str, Any]) -> str:
    items = payload.get("items") if isinstance(payload.get("items"), list) else []
    governance = payload.get("governance") if isinstance(payload.get("governance"), dict) else {}
    lines = [
        "# Friction Intake Report",
        "",
        f"- run_id: `{payload.get('run_id', '')}`",
        f"- docs_version: `{payload.get('docs_version', '')}`",
        f"- mode: `{payload.get('mode', '')}`",
        f"- generated_at: `{payload.get('generated_at', '')}`",
        "",
        "## Inputs",
        f"- evidence_refs: `{len(payload.get('evidence_refs', []))}`",
        f"- sqlite_status: `{governance.get('status', '')}`",
        f"- sqlite_db: `{governance.get('db_path', '')}`",
        "",
        "## Items",
    ]
    if not items:
        lines.append("- none")
    else:
        for item in items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"`{item.get('item_id', '')}` "
                f"class={item.get('item_class', '')} "
                f"severity={item.get('severity', '')} "
                f"domain={item.get('domain', '')} "
                f"summary={item.get('summary', '')}"
            )
            refs = item.get("evidence_refs") if isinstance(item.get("evidence_refs"), list) else []
            lines.append(f"  - evidence_refs: {', '.join(f'`{ref}`' for ref in refs) if refs else 'none'}")
    return "\n".join(lines) + "\n"


def run_friction_intake(
    project_root: Path,
    *,
    version: str,
    mode: str,
    note: str = "",
    limit: int = 10,
) -> dict[str, Any]:
    normalized_mode = str(mode or "").strip().lower()
    if normalized_mode not in SUPPORTED_FRICTION_INTAKE_MODES:
        raise ValueError(f"unsupported mode: {mode}")
    if normalized_mode == "capture" and not str(note or "").strip():
        raise ValueError("--note is required when mode=capture")

    root = project_root.expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    run_id = f"fit-{utc_compact_ts()}"
    generated_at = now_iso()

    if normalized_mode == "scan":
        items, evidence_refs = _scan_candidates(root)
    else:
        items, evidence_refs = _capture_candidates(root, note)
    final_items = items[: max(1, int(limit))]
    governance = write_friction_queue_batch(
        project_root=root,
        docs_version=resolved_version,
        tool_name=FRICTION_INTAKE_TOOL,
        run_id=run_id,
        source_type="scan" if normalized_mode == "scan" else "manual_capture",
        items=final_items,
    )

    payload = {
        "schema_version": "1.0",
        "tool": FRICTION_INTAKE_TOOL,
        "run_id": run_id,
        "docs_version": resolved_version,
        "mode": normalized_mode,
        "generated_at": generated_at,
        "evidence_refs": evidence_refs,
        "items": final_items,
        "governance": governance,
    }
    analysis_dir = _analysis_dir(root)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    json_path = analysis_dir / f"friction-intake-{run_id}.json"
    md_path = analysis_dir / f"friction-intake-{run_id}.md"
    write_json(json_path, payload)
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    write_json(
        _latest_state_path(root),
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "generated_at": generated_at,
            "payload_path": str(json_path.relative_to(root)),
            "markdown_path": str(md_path.relative_to(root)),
        },
    )
    payload["paths"] = {
        "json": str(json_path.relative_to(root)),
        "markdown": str(md_path.relative_to(root)),
    }
    return payload


def load_latest_friction_intake_report(project_root: Path) -> dict[str, Any]:
    latest = read_json(_latest_state_path(project_root), {})
    if isinstance(latest, dict):
        payload_path = str(latest.get("payload_path") or "").strip()
        if payload_path:
            candidate = project_root / payload_path
            payload = read_json(candidate, {})
            if isinstance(payload, dict) and payload:
                return payload
    analysis_dir = _analysis_dir(project_root)
    candidates = sorted(analysis_dir.glob("friction-intake-*.json"))
    if not candidates:
        return {}
    payload = read_json(candidates[-1], {})
    return payload if isinstance(payload, dict) else {}


def render_friction_intake_human(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict) or not payload:
        return "No friction intake report found."
    items = payload.get("items") if isinstance(payload.get("items"), list) else []
    governance = payload.get("governance") if isinstance(payload.get("governance"), dict) else {}
    lines = [
        "Beacon Friction Intake",
        "=" * 22,
        f"run_id           : {payload.get('run_id', '')}",
        f"docs_version     : {payload.get('docs_version', '')}",
        f"mode             : {payload.get('mode', '')}",
        f"generated_at     : {payload.get('generated_at', '')}",
        f"items            : {len(items)}",
        f"sqlite_status    : {governance.get('status', '')}",
    ]
    if items:
        lines.extend(["", "Items"])
        for item in items[:5]:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"{item.get('item_id', '')} "
                f"class={item.get('item_class', '')} "
                f"severity={item.get('severity', '')} "
                f"summary={item.get('summary', '')}"
            )
    paths = payload.get("paths") if isinstance(payload.get("paths"), dict) else {}
    if paths:
        lines.extend(["", f"json report      : {paths.get('json', '')}", f"markdown report  : {paths.get('markdown', '')}"])
    return "\n".join(lines)


def friction_intake_payload_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def load_friction_inbox(project_root: Path, *, limit: int = 20) -> list[dict[str, Any]]:
    return list_friction_items(project_root=project_root, limit=limit)


def apply_friction_action(project_root: Path, *, item_id: str, action: str) -> dict[str, Any]:
    return transition_friction_item(project_root=project_root, item_id=item_id, action=action)
