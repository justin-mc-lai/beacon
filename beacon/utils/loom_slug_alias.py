"""Loom display names + slug aliases for v2 features (identity stays canonical).

Policy: stabilize external Loom brand; keep frozen package identity
(`beacon-v2-*` paths) during transition; provide display_name and resolve
aliases without big-bang rename.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMA = "loom-slug-alias.v1"

_FEATURE_MAP: dict[str, dict[str, Any]] = {
    "beacon-v2-product-goal-orchestrator": {
        "display_name": "Loom Product Goal Orchestrator",
        "aliases": ["loom-product-goal-orchestrator", "product-goal-orchestrator"],
    },
    "beacon-v2-main-star-satellite-pool": {
        "display_name": "Loom Main-Star Satellite Pool",
        "aliases": ["loom-main-star-satellite-pool", "main-star-satellite-pool"],
    },
    "beacon-v2-domain-fsm-authority": {
        "display_name": "Loom Domain FSM Authority",
        "aliases": ["loom-domain-fsm-authority", "domain-fsm-authority"],
    },
    "beacon-v2-domain-fsm-qa-gate": {
        "display_name": "Loom Domain FSM QA Gate",
        "aliases": ["loom-domain-fsm-qa-gate", "domain-fsm-qa-gate"],
    },
    "beacon-v2-golden-commerce-fixture-parity": {
        "display_name": "Loom Golden Commerce Fixture Parity",
        "aliases": ["loom-golden-commerce-fixture-parity", "golden-commerce-fixture-parity"],
    },
    "beacon-v2-ui-state-matrix-ship-gate": {
        "display_name": "Loom UI State Matrix Ship Gate",
        "aliases": ["loom-ui-state-matrix-ship-gate", "ui-state-matrix-ship-gate"],
    },
    "beacon-v2-ralph-implement-boundary": {
        "display_name": "Loom Ralph Implement Boundary",
        "aliases": ["loom-ralph-implement-boundary", "ralph-implement-boundary"],
    },
    "beacon-v2-goal-durable-longrun": {
        "display_name": "Loom Goal Durable Longrun",
        "aliases": ["loom-goal-durable-longrun", "goal-durable-longrun"],
    },
    "beacon-v2-rust-kernel-redesign": {
        "display_name": "Loom Rust Kernel Redesign",
        "aliases": ["loom-rust-kernel-redesign", "rust-kernel-redesign"],
    },
    "beacon-v2-truth-human-readable-i18n": {
        "display_name": "Loom Truth Human-Readable i18n",
        "aliases": ["loom-truth-human-readable-i18n", "truth-human-readable-i18n"],
    },
    "beacon-goalrun-main-axis-v167": {
        "display_name": "Loom GoalRun Main Axis",
        "aliases": ["loom-goalrun-main-axis", "goalrun-main-axis"],
    },
    "loom-brand-surface": {
        "display_name": "Loom Brand Surface",
        "aliases": ["brand-surface"],
    },
    "loom-goal-optional-subagent": {
        "display_name": "Loom Optional Subagent",
        "aliases": ["loom-optional-subagent", "optional-subagent"],
    },
    "loom-goal-trace-bundle": {
        "display_name": "Loom Goal Trace Bundle",
        "aliases": ["loom-trace-bundle", "goal-trace-bundle"],
    },
}


def _alias_index() -> dict[str, str]:
    idx: dict[str, str] = {}
    for canonical, meta in _FEATURE_MAP.items():
        idx[canonical.lower()] = canonical
        for a in meta.get("aliases") or []:
            idx[str(a).lower()] = canonical
        if canonical.startswith("beacon-v2-"):
            idx[("loom-" + canonical[len("beacon-v2-") :]).lower()] = canonical
    return idx


def resolve_feature_slug(name: str) -> dict[str, Any]:
    raw = str(name or "").strip()
    if not raw:
        return {
            "schema": SCHEMA,
            "ok": False,
            "blocked": True,
            "reason_code": "slug_empty",
            "input": raw,
        }
    key = raw.lower().removeprefix("features/")
    idx = _alias_index()
    canonical = idx.get(key)
    if not canonical:
        return {
            "schema": SCHEMA,
            "ok": True,
            "blocked": False,
            "input": raw,
            "canonical_slug": raw,
            "display_name": raw,
            "brand": "Loom" if raw.startswith("loom-") or raw.startswith("beacon-v2-") else "",
            "resolved_via": "passthrough",
            "aliases": [],
        }
    meta = _FEATURE_MAP[canonical]
    return {
        "schema": SCHEMA,
        "ok": True,
        "blocked": False,
        "input": raw,
        "canonical_slug": canonical,
        "display_name": meta["display_name"],
        "brand": "Loom",
        "resolved_via": "alias_map" if key != canonical.lower() else "canonical",
        "aliases": list(meta.get("aliases") or []),
        "docs_path": f"docs/beacon/v2.0.0/features/{canonical}",
    }


def list_feature_aliases() -> dict[str, Any]:
    rows = []
    for canonical, meta in sorted(_FEATURE_MAP.items()):
        rows.append(
            {
                "canonical_slug": canonical,
                "display_name": meta["display_name"],
                "aliases": list(meta.get("aliases") or []),
                "docs_path": f"docs/beacon/v2.0.0/features/{canonical}",
            }
        )
    return {
        "schema": SCHEMA,
        "brand": "Loom",
        "policy": "identity_stays_canonical_display_is_loom",
        "count": len(rows),
        "features": rows,
    }


def feature_package_dir(project_root: Path, name: str, *, version: str = "v2.0.0") -> Path:
    resolved = resolve_feature_slug(name)
    slug = str(resolved.get("canonical_slug") or name)
    return Path(project_root) / "docs" / "beacon" / version / "features" / slug
