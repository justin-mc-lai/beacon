#!/usr/bin/env python3
"""v1.6.16 P4 exec-layer tests: failure-mode catalog expansion (5 -> 20+).

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATHS = [
    PROJECT_ROOT / "skills/beacon/beacon-qa/references/failure-mode-catalog.md",
    PROJECT_ROOT / ".agents/skills/beacon-qa/references/failure-mode-catalog.md",
    PROJECT_ROOT / ".cursor/skills/beacon-qa/references/failure-mode-catalog.md",
    PROJECT_ROOT / ".trae/skills/beacon-qa/references/failure-mode-catalog.md",
    PROJECT_ROOT / ".windsurf/skills/beacon-qa/references/failure-mode-catalog.md",
]


def _catalog() -> str:
    p = next((c for c in CATALOG_PATHS if c.exists()), CATALOG_PATHS[0])
    return p.read_text(encoding="utf-8")


def test_count_ge_20() -> None:
    """AC-001: catalog entries >= 20 (expanded from 5)."""
    count = len(re.findall(r"^##\s+FM-\d+", _catalog(), re.MULTILINE))
    assert count >= 20, f"expected >=20 entries, got {count}"


def test_source_refs_traceable() -> None:
    """AC-002: each entry carries a traceable source_ref."""
    md = _catalog()
    fm_blocks = re.split(r"^##\s+FM-\d+", md, flags=re.MULTILINE)[1:]
    assert len(fm_blocks) >= 20
    for block in fm_blocks:
        assert "source_ref" in block, f"entry missing source_ref: {block[:80]}"
        # every entry must reference a real version/failure origin
        assert re.search(r"v1\.6\.(1[3-6]|1[0-2])", block), f"source_ref must reference real version: {block[:80]}"


def test_rubric_complete() -> None:
    """AC-003: each entry has symptom/judge/through/block rubric."""
    md = _catalog()
    fm_blocks = re.split(r"^##\s+FM-\d+", md, flags=re.MULTILINE)[1:]
    for block in fm_blocks:
        assert "症状" in block, f"missing symptom: {block[:60]}"
        assert "判定规则" in block, f"missing judge rule: {block[:60]}"
        assert "rubric" in block and "通过" in block and "拦截" in block, f"missing rubric: {block[:60]}"


def test_surfaces_in_sync() -> None:
    """AC-004: catalog synced across canonical + agent surfaces."""
    contents = [p.read_text(encoding="utf-8") for p in CATALOG_PATHS if p.exists()]
    assert len(contents) >= 2, "expected canonical + at least one surface"
    for c in contents[1:]:
        assert c == contents[0], "surface catalogs must match canonical"


def test_adversarial_input_usable() -> None:
    """AC-004: catalog usable as adversarial review flip-point input (3-5 per review)."""
    md = _catalog()
    fm_ids = re.findall(r"^##\s+(FM-\d+)", md, re.MULTILINE)
    assert len(fm_ids) >= 3, "must support picking 3-5 flip points"
    # id sequence contiguous
    nums = sorted(int(f.split("-")[1]) for f in fm_ids)
    assert nums == list(range(1, len(nums) + 1)), f"FM ids must be contiguous: {nums}"


def test_fsm_legal_walk() -> None:
    """Domain FSM legal walk: scaffold->collected->authored->verified->cataloged."""
    from beacon.utils.truth_fsm import parse_truth_fsm, validate_truth_fsm

    truth_path = PROJECT_ROOT / "docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/truth.md"
    md = truth_path.read_text(encoding="utf-8")
    fsm = parse_truth_fsm(md)
    assert fsm["five_tuple_present"], "five-tuple must be present"
    result = validate_truth_fsm(fsm)
    assert not result["blocked"], f"FSM must validate: {result['findings']}"
    assert "cataloged" in fsm.get("terminal_states") or [], "cataloged must be terminal"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_count_ge_20,
        test_source_refs_traceable,
        test_rubric_complete,
        test_surfaces_in_sync,
        test_adversarial_input_usable,
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
