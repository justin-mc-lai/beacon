"""QA layer confidence chain for Beacon v1.6.4."""

from __future__ import annotations

from typing import Any

CONFIDENCE_CHAIN_LAYERS: tuple[str, ...] = (
    "unit",
    "interface",
    "contract",
    "integration",
    "smoke",
    "functional",
    "regression",
    "exception",
    "compatibility",
    "browser_e2e",
)


def _normalize_layer(value: str | None) -> str:
    raw = str(value or "").strip().lower().replace("-", "_")
    if raw in {"browser", "browser_e2e", "browser_e2e_test", "e2e", "browser-e2e"}:
        return "browser_e2e"
    return raw


def _layer_status(
    layer: str,
    *,
    executed: set[str],
    skipped: set[str],
    blocked: set[str],
    missing: set[str],
) -> str:
    if layer in blocked:
        return "blocked"
    if layer in missing:
        return "missing"
    if layer in skipped:
        return "skipped"
    if layer in executed:
        return "executed"
    return "missing"


def build_confidence_chain(
    *,
    executed_layers: list[str] | None = None,
    skipped_layers: list[str] | None = None,
    blocked_layers: list[str] | None = None,
    missing_layers: list[str] | None = None,
    state_machine_gaps: list[str] | None = None,
) -> dict[str, Any]:
    executed = {_normalize_layer(item) for item in (executed_layers or [])}
    skipped = {_normalize_layer(item) for item in (skipped_layers or [])}
    blocked = {_normalize_layer(item) for item in (blocked_layers or [])}
    missing = {_normalize_layer(item) for item in (missing_layers or [])}
    sm_gaps = {str(item).strip() for item in (state_machine_gaps or []) if str(item).strip()}

    chain: list[dict[str, Any]] = []
    downstream_ok = True
    downstream_gap_sources: list[str] = []
    for layer in CONFIDENCE_CHAIN_LAYERS:
        status = _layer_status(layer, executed=executed, skipped=skipped, blocked=blocked, missing=missing)
        gap_markers: list[str] = []
        if not downstream_ok:
            gap_markers.append("downstream_gap")
        if sm_gaps:
            gap_markers.append("state_machine_gap")
        confidence = 1.0 if status == "executed" and not gap_markers else 0.0
        if status in {"skipped", "missing", "blocked"}:
            downstream_ok = False
            downstream_gap_sources.append(layer)
            if "downstream_gap" not in gap_markers:
                gap_markers.append("downstream_gap")
        elif gap_markers:
            confidence = 0.0
        chain.append(
            {
                "layer": layer,
                "status": status,
                "confidence": confidence,
                "depends_on": list(CONFIDENCE_CHAIN_LAYERS[: CONFIDENCE_CHAIN_LAYERS.index(layer)]),
                "gap_markers": sorted(set(gap_markers)),
                "downstream_gap_sources": list(downstream_gap_sources),
            }
        )
    terminal = CONFIDENCE_CHAIN_LAYERS[-1]
    terminal_entry = next(item for item in chain if item["layer"] == terminal)
    chain_broken = bool(terminal_entry.get("gap_markers")) or terminal_entry["status"] != "executed"
    return {
        "schema_version": "1.0",
        "layers": chain,
        "chain_direction": "unit_to_browser_e2e",
        "terminal_layer": terminal,
        "chain_broken": chain_broken,
        "downstream_gap_layers": sorted(downstream_gap_sources),
    }
