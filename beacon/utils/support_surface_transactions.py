"""Shared transaction helpers for support-surface receipts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, utc_compact_ts, write_json
from beacon.utils.story_state import feature_slug
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
    write_json(machine_path, payload)
    human_path.parent.mkdir(parents=True, exist_ok=True)
    human_path.write_text(render_support_surface_markdown(payload), encoding="utf-8")
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
        "status": str(payload.get("status", "") or ""),
        "decision": str(payload.get("decision", "") or ""),
        "blocked": bool(payload.get("blocked", False)),
        "reason_code": str(payload.get("blocked_reason", "") or ""),
        "state_path": str(payload.get("state_path", "") or ""),
        "latest_next_route": str(next_route.get("command", "") or ""),
        "summary": str(payload.get("operator_visible_summary", "") or ""),
    }
