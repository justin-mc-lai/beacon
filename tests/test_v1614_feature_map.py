#!/usr/bin/env python3
"""v1.6.14 L3 exec-layer tests: feature map skeleton + reproduce + self-verify (AC-001..004).

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.feature_map import (
    _extract_acceptance_criteria,
    derive_feature_map,
    render_feature_map_markdown,
    route_reproduce,
    scaffold_feature_map,
    verify_map_one_way,
)

FEATURE = "beacon-v1614-feature-map"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _truth_md() -> str:
    p = PROJECT_ROOT / "docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md"
    return p.read_text(encoding="utf-8")


def test_derive_skeleton_ac_bound() -> None:
    map_data = derive_feature_map(PROJECT_ROOT, version="v1.6.14", feature=FEATURE)
    assert map_data["schema"] == "feature-map.v1"
    assert map_data["ac_bound"], "skeleton must be AC-bound (AC-001)"
    assert map_data["ac_ids"], "AC ids must be extracted from truth"
    assert "AC-001" in map_data["ac_ids"], "AC-001 must be present"


def test_entry_points_derived() -> None:
    map_data = derive_feature_map(PROJECT_ROOT, version="v1.6.14", feature=FEATURE)
    assert isinstance(map_data["entry_points"], list)
    assert map_data["entry_points"], "entry_points skeleton should not be empty in this repo"


def test_verification_bound_to_ac() -> None:
    map_data = derive_feature_map(PROJECT_ROOT, version="v1.6.14", feature=FEATURE)
    for v in map_data["verification"]:
        assert v["ac_id"], "verification command must bind an AC id (AC-001/AC-003)"
        assert v["command"].strip(), "verification command must be present"


def test_render_markdown() -> None:
    map_data = derive_feature_map(PROJECT_ROOT, version="v1.6.14", feature=FEATURE)
    md = render_feature_map_markdown(map_data)
    assert "# Feature Map" in md
    assert "## 入口（Entry Points）" in md
    assert "## 验证命令（Verification Commands）" in md
    assert "## 复现路由（Reproduce Routes）" in md
    assert "单向投影" in md, "map must declare one-way projection (AC-004)"


def test_reproduce_routing() -> None:
    map_data = derive_feature_map(PROJECT_ROOT, version="v1.6.14", feature=FEATURE)
    first_hint = map_data["reproduce"][0]["symptom_hint"]
    routes = route_reproduce(map_data, f"bug: {first_hint} not working")
    assert routes, f"fuzzy hint '{first_hint}' should route to a reproduce path (AC-002)"
    for r in routes:
        assert r["steps"], "reproduce route must have steps"


def test_self_verify_command_runnable() -> None:
    map_data = derive_feature_map(PROJECT_ROOT, version="v1.6.14", feature=FEATURE)
    # pick a verification command that does NOT invoke this test file (avoid recursion),
    # run it and assert the exit-code signal (AC-003).
    self_name = Path(__file__).name
    candidates = [v for v in map_data["verification"] if self_name not in v["command"]]
    assert candidates, "expected a non-recursive verification command"
    cmd = candidates[0]["command"]
    proc = subprocess.run(cmd, shell=True, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    assert proc.returncode == 0, f"verification command failed: {cmd} -> {proc.stderr}"


def test_one_way_projection() -> None:
    # AC-004: map references truth AC ids; no reverse write; no new command surface.
    result = verify_map_one_way(PROJECT_ROOT, version="v1.6.14", feature=FEATURE)
    assert result["ok"], f"map must not drift from truth: {result.get('drift_acs')}"
    truth_md = _truth_md()
    map_md = render_feature_map_markdown(derive_feature_map(PROJECT_ROOT, version="v1.6.14", feature=FEATURE))
    truth_acs = {a["ac_id"] for a in _extract_acceptance_criteria(truth_md)}
    map_acs = {a["ac_id"] for a in _extract_acceptance_criteria(map_md)}
    assert map_acs <= truth_acs, "map AC ids must be a subset of truth AC ids"


def test_scaffold_writes_skeleton() -> None:
    result = scaffold_feature_map(PROJECT_ROOT, version="v1.6.14", feature=FEATURE)
    assert result["status"] == "scaffolded"
    assert (PROJECT_ROOT / result["path"]).exists(), "scaffold must write feature-map.md (AC-001)"
    assert result["ac_bound"], "scaffold must be AC-bound"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_derive_skeleton_ac_bound,
        test_entry_points_derived,
        test_verification_bound_to_ac,
        test_render_markdown,
        test_reproduce_routing,
        test_self_verify_command_runnable,
        test_one_way_projection,
        test_scaffold_writes_skeleton,
    ]
    if args.keyword:
        tests = [fn for fn in tests if args.keyword in fn.__name__]
        if not tests:
            print(f"no test matches -k {args.keyword}")
            return 1
    failures = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
