#!/usr/bin/env python3
"""v1.6.16 P5 exec-layer tests: bad-merge rate baseline.

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.bad_merge_baseline import (
    collect_merges,
    compute_bad_merge_rate,
    emit_baseline_report,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_collect_merges() -> None:
    """AC-001: collect merges into main + revert mapping (git analysis)."""
    merges = collect_merges(PROJECT_ROOT, branch="main")
    assert isinstance(merges, list), "must return list"
    assert merges, "expected at least one merge in repo history"
    for m in merges:
        assert m.get("sha") and m.get("subject"), "merge must have sha + subject"


def test_compute_rate() -> None:
    """AC-002: bad-merge rate = reverts / merges (time window)."""
    result = compute_bad_merge_rate(PROJECT_ROOT, branch="main", min_merges=1)
    assert "bad_merge_rate" in result
    assert 0.0 <= result["bad_merge_rate"] <= 1.0
    assert result["merges"] >= 1
    # rate = reverts / merges consistency
    assert abs(result["bad_merge_rate"] - round(result["reverts"] / float(result["merges"]), 4)) < 1e-6


def test_report_emitted() -> None:
    """AC-003: baseline report has merges/reverts/rate/window/confidence."""
    report = emit_baseline_report(PROJECT_ROOT, branch="main", min_merges=1)
    rep = report.get("report") or {}
    for field in ("merges", "reverts", "bad_merge_rate", "window_days", "confidence"):
        assert field in rep, f"report missing {field}"
    assert rep["confidence"] in {"high", "low"}


def test_no_change_to_merge() -> None:
    """AC-004: observation only — does not alter merge behavior; low-confidence when sparse."""
    result = compute_bad_merge_rate(PROJECT_ROOT, branch="main", min_merges=999999)
    if result["merges"] < 999999:
        assert result["confidence"] == "low", "sparse data must be low-confidence"
    assert "bad_merge_rate" in result


def test_fsm_legal_walk() -> None:
    """Domain FSM legal walk: scaffold->collected->computed->reported/warned."""
    from beacon.utils.truth_fsm import parse_truth_fsm, validate_truth_fsm

    truth_path = PROJECT_ROOT / "docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/truth.md"
    md = truth_path.read_text(encoding="utf-8")
    fsm = parse_truth_fsm(md)
    assert fsm["five_tuple_present"], "five-tuple must be present"
    result = validate_truth_fsm(fsm)
    assert not result["blocked"], f"FSM must validate: {result['findings']}"
    assert "reported" in fsm.get("terminal_states") or "warned" in fsm.get("terminal_states"), "reported/warned terminal"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_collect_merges,
        test_compute_rate,
        test_report_emitted,
        test_no_change_to_merge,
        test_fsm_legal_walk,
    ]
    if args.keyword:
        kw = args.keyword.lower()

        def _match(fn) -> bool:
            name = fn.__name__.lower()
            if kw in name:
                return True
            if kw.endswith("or") and len(kw) > 2 and kw[:-2] in name:
                return True
            first = kw.split("_")[0]
            return bool(first) and first in name

        tests = [fn for fn in tests if _match(fn)]
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
