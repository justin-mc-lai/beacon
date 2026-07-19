"""v2 full Loom brand surface: loom-* skill prefixes for progressive public skills."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOM = ROOT / "skills" / "loom"


def test_mirror_manifest() -> None:
    man = json.loads((LOOM / "mirror-manifest.json").read_text(encoding="utf-8"))
    assert man["phase"] == "phase2_full_public_prefix"
    names = {m["loom"] for m in man["mirrors"]}
    for required in (
        "loom-goal",
        "loom-gen-implement",
        "loom-eval-qa",
        "loom-pln-program",
        "loom-loop-goal",
    ):
        assert required in names, required


def test_loom_skills_exist_with_content_source() -> None:
    for name in ("loom-gen-truth", "loom-gen-implement", "loom-eval-qa", "loom-eval-release"):
        d = LOOM / name
        assert d.is_dir(), name
        assert (d / "SKILL.md").is_file()
        src = (d / "CONTENT_SOURCE").read_text(encoding="utf-8").strip()
        assert src.startswith("skills/beacon/beacon-")
        assert (ROOT / src).is_dir(), src


def test_gov_not_mirrored_as_public() -> None:
    gov = list(LOOM.glob("loom-gov-*"))
    assert gov == [], "gov must stay denylist / not first-class loom public"


def test_no_replace_beacon_stated() -> None:
    text = (LOOM / "SKILL.md").read_text(encoding="utf-8")
    assert "不得" in text or "不得" in text or "not" in text.lower() or "禁止" in text
