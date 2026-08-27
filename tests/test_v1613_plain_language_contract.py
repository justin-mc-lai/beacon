#!/usr/bin/env python3
"""L1 (v1.6.13) F4 人话契约：7 个 beacon core skill 的 SKILL.md 输出契约均含
plain_language_delivery_summary 必填字段。"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ["design", "goal", "implement", "plan", "qa", "release", "truth"]
FIELD = "plain_language_delivery_summary"

def main() -> int:
    ok = True
    surfaces = [
        ROOT / "skills" / "beacon",
        ROOT / ".agents" / "skills",
        ROOT / ".cursor" / "skills",
    ]
    for surface in surfaces:
        for s in SKILLS:
            f = surface / f"beacon-{s}" / "SKILL.md"
            if not f.exists():
                continue
            text = f.read_text(encoding="utf-8")
            if FIELD not in text:
                print(f"FAIL: {f} missing {FIELD}", file=sys.stderr)
                ok = False
            else:
                print(f"ok: {f}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
