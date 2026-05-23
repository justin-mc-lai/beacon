"""Shared transaction helpers for support-surface receipts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, utc_compact_ts, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.support_research_topology import (
    feature_research_path,
    resolve_support_write_topology,
    support_surface_class,
    upsert_support_finding_section,
)
from beacon.utils.versioning import resolve_target_version


_SURFACE_ALIASES = {
    "beacon-ceo-review": "beacon-ceo-review",
    "ceo-review": "beacon-ceo-review",
    "beacon-design-review": "beacon-design-review",
    "design-review": "beacon-design-review",
    "beacon-learn": "beacon-learn",
    "learn": "beacon-learn",
}


def normalize_support_surface(surface: str) -> str:
    text = str(surface or "").strip()
    return _SURFACE_ALIASES.get(text, text)


def _surface_stub(surface: str) -> str:
    return normalize_support_surface(surface)


def machine_transaction_path(project_root: Path, *, version: str, surface: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / ".machine" / "execution" / f"{_surface_stub(surface)}-transaction.json"


def human_transaction_path(project_root: Path, *, version: str, surface: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / "execution" / f"{_surface_stub(surface)}-transaction.md"


def latest_state_path(project_root: Path, *, surface: str) -> Path:
    return project_root / ".beacon" / "state" / f"{_surface_stub(surface)}-latest.json"


def history_path(project_root: Path, *, surface: str, transaction_id: str) -> Path:
    return project_root / ".beacon" / "transactions" / _surface_stub(surface) / f"{transaction_id}.json"


def support_surface_transaction_id(surface: str, *, version: str, feature: str) -> str:
    normalized_surface = _surface_stub(surface)
    slug = feature_slug(feature or normalized_surface)
    version_text = str(version or "").strip() or "auto"
    return f"tx-{normalized_surface}-{version_text}-{slug}-{utc_compact_ts().lower()}"


def render_support_surface_markdown(payload: dict[str, Any]) -> str:
    next_route = payload.get("next_route", {}) if isinstance(payload.get("next_route"), dict) else {}
    reason_codes = payload.get("reason_codes", []) if isinstance(payload.get("reason_codes"), list) else []
    truth_refs = payload.get("truth_refs", []) if isinstance(payload.get("truth_refs"), list) else []
    challenge_axes = payload.get("challenge_axes", []) if isinstance(payload.get("challenge_axes"), list) else []
    lines = [
        f"# {payload.get('surface', 'Support Surface')} Transaction",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- status: `{payload.get('status', '')}`",
        f"- decision: `{payload.get('decision', '')}`",
    ]
    if truth_refs:
        lines.append(f"- truth_refs: `{', '.join(str(item) for item in truth_refs)}`")
    lines.extend(
        [
            "",
            "## Summary",
            str(payload.get("operator_visible_summary", "") or "No summary."),
            "",
            "## Next Route",
            f"- command: `{next_route.get('command', '')}`",
            f"- why: {next_route.get('why', '')}",
        ]
    )
    if challenge_axes:
        lines.extend(["", "## Challenge Axes"])
        for axis in challenge_axes:
            if not isinstance(axis, dict):
                continue
            code = str(axis.get("code", "") or "").strip()
            prompt = str(axis.get("prompt", "") or "").strip()
            risk = str(axis.get("risk", "") or "").strip()
            if code:
                lines.append(f"- `{code}`: {prompt or risk or 'challenge applied'}")
            elif prompt or risk:
                lines.append(f"- {prompt or risk}")
    if reason_codes:
        lines.extend(["", "## Reason Codes"])
        for code in reason_codes:
            lines.append(f"- `{code}`")
    if payload.get("blocked"):
        lines.extend(["", "## Blocked", f"- blocked_reason: `{payload.get('blocked_reason', '')}`"])
    return "\n".join(lines) + "\n"


def build_support_surface_transaction(
    *,
    surface: str,
    mode: str,
    version: str,
    feature: str,
    status: str,
    decision: str,
    route_decision: dict[str, Any],
    next_route: dict[str, Any],
    writeback_targets: list[str],
    operator_visible_summary: str,
    truth_refs: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    reason_codes: list[str] | None = None,
    challenge_axes: list[dict[str, Any]] | None = None,
    state_impact: dict[str, Any] | None = None,
    gate_impact: dict[str, Any] | None = None,
    blocked: bool = False,
    blocked_reason: str = "",
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "transaction_id": support_surface_transaction_id(surface, version=version, feature=feature),
        "surface": normalize_support_surface(surface),
        "mode": str(mode or "").strip(),
        "version": str(version or "").strip(),
        "feature": str(feature or "").strip(),
        "feature_slug": feature_slug(feature),
        "status": str(status or "").strip(),
        "decision": str(decision or "").strip(),
        "reason_codes": [str(item).strip() for item in (reason_codes or []) if str(item).strip()],
        "truth_refs": [str(item).strip() for item in (truth_refs or []) if str(item).strip()],
        "evidence_refs": [str(item).strip() for item in (evidence_refs or []) if str(item).strip()],
        "challenge_axes": [item for item in (challenge_axes or []) if isinstance(item, dict)],
        "route_decision": route_decision if isinstance(route_decision, dict) else {},
        "next_route": next_route if isinstance(next_route, dict) else {},
        "writeback_targets": [str(item).strip() for item in (writeback_targets or []) if str(item).strip()],
        "state_impact": state_impact if isinstance(state_impact, dict) else {},
        "gate_impact": gate_impact if isinstance(gate_impact, dict) else {},
        "blocked": bool(blocked),
        "blocked_reason": str(blocked_reason or "").strip(),
        "operator_visible_summary": str(operator_visible_summary or "").strip(),
        "created_at": now_iso(),
    }


def write_support_surface_transaction(project_root: Path, *, version: str, payload: dict[str, Any]) -> dict[str, str]:
    surface = normalize_support_surface(str(payload.get("surface", "") or ""))
    transaction_id = str(payload.get("transaction_id", "") or "").strip()
    machine_path = machine_transaction_path(project_root, version=version, surface=surface)
    human_path = human_transaction_path(project_root, version=version, surface=surface)
    state_path = latest_state_path(project_root, surface=surface)
    history = history_path(project_root, surface=surface, transaction_id=transaction_id) if transaction_id else None
    feature = str(payload.get("feature", "") or "")
    policy_class = support_surface_class(surface)
    topology_actual_path = (
        feature_research_path(project_root, version=version, feature=feature)
        if policy_class == "ordinary_support_review"
        else machine_path
    )
    topology = resolve_support_write_topology(
        project_root,
        version=version,
        feature=feature,
        surface=surface,
        actual_path=topology_actual_path,
    )
    if topology.get("supported"):
        payload["support_write_topology"] = topology
        if topology.get("blocked") and surface != "beacon-learn":
            payload["blocked"] = True
            payload["blocked_reason"] = str(topology.get("reason_code") or "support_write_topology_unresolved")
            payload["status"] = "blocked"
            reason_codes = payload.get("reason_codes") if isinstance(payload.get("reason_codes"), list) else []
            payload["reason_codes"] = [*reason_codes, str(topology.get("reason_code") or "support_write_topology_unresolved")]
    write_json(machine_path, payload)
    human_path.parent.mkdir(parents=True, exist_ok=True)
    human_path.write_text(render_support_surface_markdown(payload), encoding="utf-8")
    research_writeback: dict[str, Any] = {}
    if topology.get("supported") and policy_class == "ordinary_support_review" and not topology.get("blocked"):
        research_writeback = upsert_support_finding_section(
            project_root,
            version=version,
            feature=feature,
            surface=surface,
            finding_summary=str(payload.get("operator_visible_summary") or ""),
            source_refs=[str(machine_path.relative_to(project_root)), str(human_path.relative_to(project_root))],
            route_decision=str((payload.get("route_decision") or {}).get("route") or payload.get("decision") or "read-only route-only")
            if isinstance(payload.get("route_decision"), dict)
            else str(payload.get("decision") or "read-only route-only"),
            material_effect="read_only_route_only",
            adoption_status="route_only",
        )
        payload["support_research_writeback"] = research_writeback
        write_json(machine_path, payload)
    state_payload = {
        "surface": surface,
        "feature": payload.get("feature", ""),
        "feature_slug": payload.get("feature_slug", ""),
        "version": payload.get("version", ""),
        "status": payload.get("status", ""),
        "decision": payload.get("decision", ""),
        "blocked": bool(payload.get("blocked", False)),
        "blocked_reason": payload.get("blocked_reason", ""),
        "reason_codes": payload.get("reason_codes", []),
        "challenge_axis_codes": [
            str(item.get("code", "") or "").strip()
            for item in payload.get("challenge_axes", [])
            if isinstance(item, dict) and str(item.get("code", "") or "").strip()
        ],
        "next_route": payload.get("next_route", {}),
        "operator_visible_summary": payload.get("operator_visible_summary", ""),
        "transaction_id": transaction_id,
        "state_path": str(state_path.relative_to(project_root)),
    }
    write_json(state_path, state_payload)
    if history is not None:
        write_json(history, payload)
    return {
        "machine_path": str(machine_path.relative_to(project_root)),
        "human_path": str(human_path.relative_to(project_root)),
        "state_path": str(state_path.relative_to(project_root)),
        "history_path": str(history.relative_to(project_root)) if history is not None else "",
    }


def load_latest_support_surface_state(project_root: Path, *, surface: str) -> dict[str, Any]:
    payload = read_json(latest_state_path(project_root, surface=surface), {})
    return payload if isinstance(payload, dict) else {}


def load_support_surface_summary(project_root: Path, *, surface: str) -> dict[str, Any]:
    payload = load_latest_support_surface_state(project_root, surface=surface)
    next_route = payload.get("next_route", {}) if isinstance(payload.get("next_route"), dict) else {}
    return {
        "surface": normalize_support_surface(surface),
        "version": str(payload.get("version", "") or ""),
        "feature": str(payload.get("feature", "") or ""),
        "status": str(payload.get("status", "") or ""),
        "decision": str(payload.get("decision", "") or ""),
        "blocked": bool(payload.get("blocked", False)),
        "reason_code": str(payload.get("blocked_reason", "") or ""),
        "state_path": str(payload.get("state_path", "") or ""),
        "latest_next_route": str(next_route.get("command", "") or ""),
        "challenge_axis_codes": [
            str(item).strip()
            for item in payload.get("challenge_axis_codes", [])
            if str(item).strip()
        ] if isinstance(payload.get("challenge_axis_codes"), list) else [],
        "summary": str(payload.get("operator_visible_summary", "") or ""),
    }
