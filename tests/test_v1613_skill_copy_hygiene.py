#!/usr/bin/env python3
"""L4 (v1.6.13) F2/F3/F5 skill-copy hygiene tests: shared reference, no copy
bugs, no stale version anchors, mode_id prefix unified with legacy alias."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAIL = []


def check(name, cond, detail=""):
    print(f"ok: {name}" if cond else f"FAIL: {name} {detail}")
    if not cond:
        FAIL.append(name)


def main():
    shared = ROOT / "skills" / "beacon" / "references" / "shared-preamble.md"
    check("shared_preamble_exists", shared.exists(), shared)
    if not shared.exists():
        sys.exit(1)

    modes = list((ROOT / "skills" / "beacon").glob("beacon-*/references/modes/*.md"))
    check("modes_found", len(modes) >= 15, f"{len(modes)} mode files")
    ref_count = sum(1 for m in modes if "shared-preamble.md" in m.read_text(encoding="utf-8"))
    check("modes_reference_shared", ref_count >= 10, f"{ref_count}/{len(modes)} reference shared")

    # AC-002: copy bugs fixed
    buggy = []
    for m in modes:
        t = m.read_text(encoding="utf-8")
        if "beacon-gen-truth`, `beacon-gen-truth`, and `beacon-gen-truth" in t:
            buggy.append(m.name)
        if "does not delete canonical v1.6.0 routees such as `beacon-gen-truth`" in t:
            buggy.append(m.name)
    check("no_copy_bugs", not buggy, buggy)

    # AC-003: no stale CURRENT-version self-anchors (historical compat refs like
    # "For v1.4.9+" / "Compatibility reference: v1.4.7" / correct "canonical v1.6.0 routes"
    # are preserved facts, not anchors)
    stale = []
    for m in modes:
        t = m.read_text(encoding="utf-8")
        if re.search(r"aligned to the current `v1\.\d|current `v1\.[0-5]\.\d`", t):
            stale.append(m.name)
    check("no_stale_version_anchors", not stale, stale)

    # AC-004: eval-truth-review + legacy alias
    ev = ROOT / "skills" / "beacon" / "beacon-truth" / "references" / "modes" / "eval-truth-review.md"
    check("eval_truth_review_exists", ev.exists(), ev)
    skf = ROOT / "skills" / "beacon" / "beacon-truth" / "SKILL.md"
    t = skf.read_text(encoding="utf-8")
    check("mode_table_renamed", "eval-truth-review" in t and "legacy alias" in t, "mode table")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
