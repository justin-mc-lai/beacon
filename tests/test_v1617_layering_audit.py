#!/usr/bin/env python3
"""v1.6.17 A2 exec-layer tests: layering audit.

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.layering_audit import (
    GOD_MODULE_LINES,
    build_audit_report,
    detect_layer_violations,
    list_god_modules,
    scan_import_graph,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_graph_generated() -> None:
    """AC-001: import dependency graph generated (module x depends_on)."""
    graph = scan_import_graph(PROJECT_ROOT)
    assert graph["module_count"] > 100, f"expected >100 modules, got {graph['module_count']}"
    # runtime/versioning are heavily referenced
    assert any("versioning" in m for m in graph["modules"]), "versioning module must be in graph"
    sample = next(iter(graph["modules"].values()))
    assert "depends_on" in sample and "lines" in sample


def test_god_modules_listed() -> None:
    """AC-002: modules >2000 lines listed."""
    gods = list_god_modules(scan_import_graph(PROJECT_ROOT))
    assert gods, "beacon has known >2000-line modules (prototype_utils etc.)"
    for g in gods:
        assert g["lines"] > GOD_MODULE_LINES, f"{g['module']} not actually god-sized"
    # prototype_utils is the biggest known
    assert any("prototype_utils" in g["module"] for g in gods), "prototype_utils should be a god module"


def test_violations_detected() -> None:
    """AC-003: utils -> commands imports flagged as layer violations."""
    violations = detect_layer_violations(scan_import_graph(PROJECT_ROOT))
    assert isinstance(violations, list)
    for v in violations:
        assert v["from_module"].startswith("utils."), f"violation from non-utils: {v}"
        assert v["to_module"].startswith("commands."), f"violation to non-commands: {v}"


def test_report_emitted() -> None:
    """AC-004: maintainability risk report with god modules + violations."""
    report = build_audit_report(PROJECT_ROOT)
    for field in ("module_count", "god_module_count", "layer_violation_count", "risk_level", "risk_reasons"):
        assert field in report, f"report missing {field}"
    assert report["risk_level"] in {"low", "medium", "high"}
    assert report["god_module_count"] >= 1
    assert report["module_count"] > 100


def test_fsm_legal_walk() -> None:
    """Domain FSM legal walk: scaffold->scanned->sized->classified->reported."""
    from beacon.utils.truth_fsm import parse_truth_fsm, validate_truth_fsm

    truth_path = PROJECT_ROOT / "docs/beacon/v1.6.17/features/beacon-v1617-layering-audit/truth.md"
    md = truth_path.read_text(encoding="utf-8")
    fsm = parse_truth_fsm(md)
    assert fsm["five_tuple_present"], "five-tuple must be present"
    result = validate_truth_fsm(fsm)
    assert not result["blocked"], f"FSM must validate: {result['findings']}"
    assert "reported" in fsm.get("terminal_states") or [], "reported must be terminal"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_graph_generated,
        test_god_modules_listed,
        test_violations_detected,
        test_report_emitted,
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
