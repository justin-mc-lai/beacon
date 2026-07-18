"""v2.0.0 Product Goal program — parity & delivery readiness contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from beacon.utils.product_goal_runtime import (
    attach_verifier,
    complete_goal_run,
    load_goal_run,
    run_goal_facade,
)
from beacon.utils.v2_product_goal_parity import (
    DGS_TO_V2_DLR,
    V2_DOMAIN_TRUTH_CHAIN,
    V2_PRODUCT_GOAL_LAKES,
    V2_VERSION,
    assert_feature_package_present,
    delivery_readiness_snapshot,
    durable_parity_map_complete,
    extract_ac_ids,
    no_early_beacon_v2_default,
    program_topology_ok,
    python_cli_surface_ok,
    skill_single_public_entry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_all_eight_lakes_frozen_packages() -> None:
    for slug in V2_PRODUCT_GOAL_LAKES:
        check = assert_feature_package_present(ROOT, V2_VERSION, slug)
        assert check["ok"], check
        truth = (ROOT / check["paths"]["truth"]).read_text(encoding="utf-8")
        assert "status: frozen" in truth


def test_domain_truth_chain_option_a_five_lakes() -> None:
    assert len(V2_DOMAIN_TRUTH_CHAIN) == 5
    topo = program_topology_ok(ROOT)
    assert topo["domain_truth_chain_count"] == 5
    assert topo["ok"] is True


def test_program_topology_ok() -> None:
    assert program_topology_ok(ROOT)["ok"] is True


def test_durable_dgs_to_dlr_parity_table() -> None:
    assert len(DGS_TO_V2_DLR) == 14
    result = durable_parity_map_complete(ROOT)
    assert result["ok"] is True, result


def test_longrun_truth_has_legal_illegal() -> None:
    tests = (
        ROOT
        / "docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/tests.md"
    ).read_text(encoding="utf-8")
    assert "legal" in tests.lower() or "LEGAL" in tests or "TC-" in tests
    assert "illegal" in tests.lower() or "ILLEGAL" in tests


def test_skill_single_public_entry() -> None:
    assert skill_single_public_entry(ROOT)["ok"] is True


def test_python_cli_compat_surface() -> None:
    assert python_cli_surface_ok()["ok"] is True


def test_no_early_beacon_v2_default() -> None:
    assert no_early_beacon_v2_default(env={})["ok"] is True
    assert no_early_beacon_v2_default(env={"BEACON_V2": "0"})["ok"] is True
    assert no_early_beacon_v2_default(env={"BEACON_V2": "1"})["ok"] is False


def test_goal_run_on_v2_docs_line(tmp_path: Path) -> None:
    # facade works with version v2.0.0 string even if docs not in tmp;
    # use real project root for version resolution when docs exist
    run = run_goal_facade(ROOT, utterance="v2 parity smoke", version="v2.0.0", longrun=False)
    assert run.get("version") == "v2.0.0"
    assert run.get("longrun") in (False, None) or run.get("driver", {}).get("state") == "idle"
    assert (run.get("supervisor") or {}).get("attached") is False


def test_goal_longrun_on_v2_docs_line_attach() -> None:
    run = run_goal_facade(
        ROOT,
        utterance="v2 longrun 长跑 smoke",
        version="v2.0.0",
        longrun=True,
        driver_start=True,
        driver_run_loop=False,
        bridge_cmd="true",
    )
    assert run.get("longrun") is True
    assert (run.get("supervisor") or {}).get("attached") is True
    assert complete_goal_run(ROOT, run["run_id"])["status"] != "completed"
    attach_verifier(ROOT, run["run_id"], refs=["docs/beacon/v2.0.0/SUMMARY.md"])
    done = complete_goal_run(ROOT, run["run_id"])
    assert done["status"] == "completed"


def test_orchestrator_acs_present() -> None:
    truth = (
        ROOT / "docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/truth.md"
    ).read_text(encoding="utf-8")
    acs = extract_ac_ids(truth)
    for i in range(1, 12):
        assert f"AC-V2-PGO-{i:03d}" in acs


def test_delivery_readiness_snapshot() -> None:
    snap = delivery_readiness_snapshot(ROOT)
    assert snap["runtime_still"] == "v1.6.7"
    assert snap["runtime_promotion"] == "blocked_until_w4"
    assert snap["ok"] is True, snap


def test_rust_workspace_scaffold_exists() -> None:
    assert (ROOT / "packages/beacon-rs/Cargo.toml").is_file()
    text = (ROOT / "packages/beacon-rs/Cargo.toml").read_text(encoding="utf-8")
    assert "beacon-core" in text
    assert "beacon-orchestrator" in text
