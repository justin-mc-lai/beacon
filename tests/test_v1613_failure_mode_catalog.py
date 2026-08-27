#!/usr/bin/env python3
"""L3 (v1.6.13) D3 failure-mode catalog tests: catalog exists with >=5 modes,
each with rubric; adversarial review modes reference the catalog."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAIL = []


def cat(surface):
    return ROOT / surface / "beacon-qa" / "references" / "failure-mode-catalog.md"


def check(name, cond, detail=""):
    print(f"{'ok' if cond else 'FAIL'}: {name} {detail}" if not cond else f"ok: {name}")
    if not cond:
        FAIL.append(name)


def main():
    # canonical catalog
    canon = cat("skills/beacon")
    check("catalog_exists", canon.exists(), canon)
    if canon.exists():
        text = canon.read_text()
        modes = re.findall(r"^## FM-\d+", text, re.M)
        check("catalog_ge5_modes", len(modes) >= 5, f"found {len(modes)}")
        check("rubric_present", text.count("rubric：") >= len(modes), "rubric per mode")
        check("user_decides_boundary", "不自动判 pass" in text or "user decides" in text, "critical-opinion boundary")
    # wired into eval-qa modes
    for mode in ("eval-qa", "eval-qa-deep"):
        m = ROOT / "skills" / "beacon" / "beacon-qa" / "references" / "modes" / f"{mode}.md"
        check(f"wired_{mode}", m.exists() and "failure-mode-catalog" in m.read_text(), mode)
    # projections exist
    check("agents_projection", cat(".agents/skills").exists())
    check("cursor_projection", cat(".cursor/skills").exists())
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
