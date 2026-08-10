"""v1.6.9 delivery closure: runtime promote + public shells progressive."""

from __future__ import annotations

import json
from pathlib import Path

import beacon
from beacon.utils.versioning import load_version_truth

ROOT = Path(__file__).resolve().parents[1]


def test_ac_dc_001_version_truth_runtime_v169() -> None:
    vt = load_version_truth(ROOT)
    assert vt.get("package_version") == "1.6.12"
    assert str(vt.get("runtime_version") or "") in {"v1.6.12", "1.6.12"}
    assert str(vt.get("docs_default_line") or "") in {"v1.6.12", "1.6.12"}
    assert str(vt.get("current_runtime_release_line") or "") in {"v1.6.12", "1.6.12"}
    lines = vt.get("lines") if isinstance(vt.get("lines"), dict) else {}
    st = (lines.get("v1.6.12") or {}).get("status") if isinstance(lines.get("v1.6.12"), dict) else ""
    assert st == "current_runtime_release"


def test_ac_dc_002_package_version_constant() -> None:
    assert beacon.__version__ == "1.6.12"
    assert str(getattr(beacon, "__toolkit_version__", "")).lstrip("v") == "1.6.12"


def test_ac_dc_003_shells_have_progressive() -> None:
    for rel in [
        "skills/beacon/beacon-goal/SKILL.md",
        "skills/loom/loom-goal/SKILL.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "progressive" in text, rel


def test_ac_dc_005_summary_delivered() -> None:
    text = (ROOT / "docs/beacon/v1.6.9/SUMMARY.md").read_text(encoding="utf-8")
    assert "runtime promote" in text.lower() or "v1.6.9" in text
    assert "pending follow-up" not in text.lower()
    assert "beacon-public-surface-1plus6-v169" in text
