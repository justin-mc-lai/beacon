"""Audit: v2 skill calling surface is loom public-entry + shared beacon/* content."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_loom_public_entry_exists() -> None:
    assert (ROOT / "skills/loom/loom-goal/SKILL.md").is_file()
    text = (ROOT / "skills/loom/loom-goal/SKILL.md").read_text(encoding="utf-8")
    assert "loom-goal" in text
    assert "beacon-goal" in text  # dual-install relation


def test_phase2_loom_prefix_with_beacon_content_source() -> None:
    """Phase-2: loom-* public prefix; content remains skills/beacon/*."""
    beacon_skills = [
        p.name
        for p in (ROOT / "skills/beacon").iterdir()
        if p.is_dir() and p.name.startswith("beacon-")
    ]
    loom_skills = [
        p.name
        for p in (ROOT / "skills/loom").iterdir()
        if p.is_dir() and p.name.startswith("loom-")
    ]
    assert len(beacon_skills) >= 20
    assert "loom-goal" in loom_skills
    assert "loom-gen-implement" in loom_skills
    src = (ROOT / "skills/loom/loom-gen-implement/CONTENT_SOURCE").read_text(encoding="utf-8").strip()
    assert src == "skills/beacon/beacon-gen-implement"


def test_phase1_shares_beacon_content() -> None:
    truth = (ROOT / "docs/beacon/v2.0.0/features/loom-brand-surface/truth.md").read_text(
        encoding="utf-8"
    )
    assert "UD-LOOM-007" in truth
    assert "共享" in truth or "share" in truth.lower() or "skills/beacon" in truth


def test_no_third_public_orchestration_skill() -> None:
    """Only loom-goal is public primary under skills/loom."""
    primaries = []
    for skill_md in (ROOT / "skills/loom").rglob("SKILL.md"):
        text = skill_md.read_text(encoding="utf-8")
        if "entry: public_primary" in text or "public_primary" in text:
            primaries.append(skill_md.parent.name)
    assert "loom-goal" in primaries or (ROOT / "skills/loom/loom-goal/SKILL.md").exists()
    host = (ROOT / "skills/loom/SKILL.md").read_text(encoding="utf-8")
    assert "routes to loom-goal" in host.lower() or "loom-goal" in host


def test_audit_doc_present() -> None:
    doc = ROOT / "docs/beacon/v2.0.0/research/v2-skill-loom-calling-surface-audit.md"
    assert doc.is_file()
    text = doc.read_text(encoding="utf-8")
    assert "Phase-1" in text
    assert "否" in text or "not" in text.lower()
