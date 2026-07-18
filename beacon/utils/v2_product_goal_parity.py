"""v2.0.0 Product Goal program parity helpers (docs-line delivery).

Runtime remains v1.6.7 until Wave W4 (DEF-SE-004 / AC-V2-PGO-011).
This module is the Python compat/parity surface for frozen v2 lakes.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

V2_VERSION = "v2.0.0"
V167_VERSION = "v1.6.7"
PROGRAM_SLUG = "beacon-v2-product-goal-parallel-v200"

# Topology order (program lakes) — excludes rust-kernel primary feature
V2_PRODUCT_GOAL_LAKES: tuple[str, ...] = (
    "beacon-v2-product-goal-orchestrator",
    "beacon-v2-main-star-satellite-pool",
    "beacon-v2-domain-fsm-authority",
    "beacon-v2-golden-commerce-fixture-parity",
    "beacon-v2-domain-fsm-qa-gate",
    "beacon-v2-ui-state-matrix-ship-gate",
    "beacon-v2-ralph-implement-boundary",
    "beacon-v2-goal-durable-longrun",
)

# Domain truth chain subset (Option A merge)
V2_DOMAIN_TRUTH_CHAIN: tuple[str, ...] = (
    "beacon-v2-domain-fsm-authority",
    "beacon-v2-golden-commerce-fixture-parity",
    "beacon-v2-domain-fsm-qa-gate",
    "beacon-v2-ui-state-matrix-ship-gate",
    "beacon-v2-ralph-implement-boundary",
)

# v1.6.7 durable AC → v2 longrun AC map (truth R2)
DGS_TO_V2_DLR: dict[str, str] = {
    "AC-DGS-001": "AC-V2-DLR-002",
    "AC-DGS-002": "AC-V2-DLR-004",
    "AC-DGS-003": "AC-V2-DLR-005",
    "AC-DGS-004": "AC-V2-DLR-006",
    "AC-DGS-005": "AC-V2-DLR-007",
    "AC-DGS-006": "AC-V2-DLR-007",
    "AC-DGS-007": "AC-V2-DLR-009",
    "AC-DGS-008": "AC-V2-DLR-010",
    "AC-DGS-009": "AC-V2-DLR-011",
    "AC-DGS-010": "AC-V2-DLR-002",
    "AC-DGS-011": "AC-V2-DLR-005",
    "AC-DGS-012": "AC-V2-DLR-015",
    "AC-DGS-013": "AC-V2-DLR-003",
    "AC-DGS-014": "AC-V2-DLR-016",
}

PUBLIC_ENTRY = "beacon-goal"
SUPPORT_ENTRY = "beacon-loop-goal"


def feature_package_dir(project_root: Path, version: str, slug: str) -> Path:
    return Path(project_root) / "docs" / "beacon" / version / "features" / slug


def package_paths(project_root: Path, version: str, slug: str) -> dict[str, Path]:
    base = feature_package_dir(project_root, version, slug)
    return {
        "truth": base / "truth.md",
        "tests": base / "tests.md",
        "tasks": base / "tasks.md",
        "evidence": base / "evidence.md",
    }


def assert_feature_package_present(project_root: Path, version: str, slug: str) -> dict[str, Any]:
    paths = package_paths(project_root, version, slug)
    missing = [k for k, p in paths.items() if not p.is_file()]
    return {
        "slug": slug,
        "version": version,
        "ok": not missing,
        "missing": missing,
        "paths": {k: str(v.relative_to(project_root)) for k, v in paths.items()},
    }


def read_frontmatter_status(truth_path: Path) -> str:
    text = truth_path.read_text(encoding="utf-8")
    m = re.search(r"^status:\s*(\S+)", text, re.M)
    return (m.group(1) if m else "").strip()


def extract_ac_ids(markdown: str) -> set[str]:
    return set(re.findall(r"\bAC-[A-Z0-9]+(?:-[A-Z0-9]+)+\b", markdown))


def no_early_beacon_v2_default(*, env: dict[str, str] | None = None) -> dict[str, Any]:
    """AC-V2-PGO-011 / DEF-SE-004: do not default BEACON_V2=1 before W4."""
    e = env if env is not None else dict(os.environ)
    raw = str(e.get("BEACON_V2", "")).strip()
    # Missing / empty / 0 / false / off → ok; only explicit 1/true/on is early-default risk when W4 not done
    early = raw.lower() in {"1", "true", "yes", "on"}
    return {
        "ok": not early,
        "BEACON_V2": raw or "(unset)",
        "policy": "reject_early_default_until_w4",
        "reason_code": "" if not early else "early_beacon_v2_default_forbidden",
    }


def program_topology_ok(project_root: Path) -> dict[str, Any]:
    root = Path(project_root)
    graph = root / "docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json"
    manifest = root / "docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/program-manifest.md"
    missing_lakes: list[str] = []
    statuses: dict[str, str] = {}
    for slug in V2_PRODUCT_GOAL_LAKES:
        check = assert_feature_package_present(root, V2_VERSION, slug)
        if not check["ok"]:
            missing_lakes.append(slug)
            continue
        statuses[slug] = read_frontmatter_status(Path(root) / check["paths"]["truth"])
    domain_present = all(
        assert_feature_package_present(root, V2_VERSION, s)["ok"] for s in V2_DOMAIN_TRUTH_CHAIN
    )
    return {
        "ok": graph.is_file()
        and manifest.is_file()
        and not missing_lakes
        and domain_present
        and all(st == "frozen" for st in statuses.values()),
        "graph_exists": graph.is_file(),
        "manifest_exists": manifest.is_file(),
        "missing_lakes": missing_lakes,
        "statuses": statuses,
        "domain_truth_chain_count": len(V2_DOMAIN_TRUTH_CHAIN),
        "lake_count": len(V2_PRODUCT_GOAL_LAKES),
    }


def durable_parity_map_complete(project_root: Path) -> dict[str, Any]:
    """AC-V2-DLR-001: parity table present in v2 longrun truth."""
    truth = feature_package_dir(project_root, V2_VERSION, "beacon-v2-goal-durable-longrun") / "truth.md"
    text = truth.read_text(encoding="utf-8") if truth.is_file() else ""
    missing_pairs = []
    for dgs, dlr in DGS_TO_V2_DLR.items():
        if dgs not in text or dlr not in text:
            missing_pairs.append({"dgs": dgs, "dlr": dlr})
    acs = extract_ac_ids(text)
    required = {f"AC-V2-DLR-{i:03d}" for i in range(1, 17)}
    # 014/015 may be Should; still should appear
    return {
        "ok": not missing_pairs and required.issubset(acs),
        "missing_pairs": missing_pairs,
        "ac_count": len(acs),
        "required_present": sorted(required & acs),
        "required_missing": sorted(required - acs),
    }


def skill_single_public_entry(project_root: Path) -> dict[str, Any]:
    """AC-V2-PGO-002/007: beacon-goal is public primary; loop is support."""
    root = Path(project_root)
    goal = (root / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    loop = (root / "skills/beacon/beacon-loop-goal/SKILL.md").read_text(encoding="utf-8")
    goal_ok = "public_primary" in goal or "唯一公共入口" in goal
    loop_ok = "support" in loop.lower() and ("发现" in loop or "discovery" in loop.lower())
    not_dual = "不要先调" in goal or "support only" in goal.lower()
    return {
        "ok": goal_ok and loop_ok and not_dual,
        "goal_public": goal_ok,
        "loop_support": loop_ok,
        "anti_dual_call": not_dual,
    }


def python_cli_surface_ok() -> dict[str, Any]:
    """AC-V2-PGO-006 + longrun CLI exist on Python runtime (compat shim)."""
    from beacon.utils.goal_agent_driver import detect_longrun_intent
    from beacon.utils.goal_durable_supervisor import DEFAULT_HEARTBEAT_INTERVAL_SEC
    from beacon.utils.product_goal_runtime import PUBLIC_ENTRY, public_entry_contract

    contract = public_entry_contract()
    return {
        "ok": contract.get("public_primary") == PUBLIC_ENTRY
        and contract.get("single_entry") is True
        and DEFAULT_HEARTBEAT_INTERVAL_SEC == 120
        and detect_longrun_intent("长跑直到验收") is True
        and detect_longrun_intent("plain feature") is False,
        "public_entry": contract.get("public_primary"),
        "heartbeat_sec": DEFAULT_HEARTBEAT_INTERVAL_SEC,
    }


def delivery_readiness_snapshot(project_root: Path) -> dict[str, Any]:
    """Aggregate readiness for v2.0.0 docs-line delivery (not runtime promotion)."""
    root = Path(project_root)
    topo = program_topology_ok(root)
    durable = durable_parity_map_complete(root)
    skill = skill_single_public_entry(root)
    cli = python_cli_surface_ok()
    early = no_early_beacon_v2_default()
    rust_crate = (root / "packages/beacon-rs/Cargo.toml").is_file()
    parts = {
        "topology": topo,
        "durable_parity_map": durable,
        "skill_entry": skill,
        "python_cli_compat": cli,
        "no_early_v2_default": early,
        "rust_workspace_scaffold": {"ok": rust_crate, "path": "packages/beacon-rs/Cargo.toml"},
    }
    ok = all(bool(v.get("ok")) for v in parts.values())
    return {
        "version": V2_VERSION,
        "runtime_still": V167_VERSION,
        "delivery_mode": "docs_line_parity_plus_python_compat",
        "runtime_promotion": "blocked_until_w4",
        "ok": ok,
        "parts": parts,
    }
