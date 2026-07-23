"""Scheme A monorepo host-discovery anti-leak (Cursor slash menu root fix)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.agent_surface import (
    HOST_DISCOVERABLE_MANIFEST,
    INTERNAL_SUPPORT_MANIFEST,
    list_host_visible_skills,
    packaged_beacon_skill_root,
    scan_monorepo_skill_discovery_leaks,
)

ROOT = Path(__file__).resolve().parents[1]
WHITELIST = {
    "beacon-goal",
    "beacon-plan",
    "beacon-truth",
    "beacon-design",
    "beacon-implement",
    "beacon-qa",
    "beacon-release",
}


def test_monorepo_skill_discovery_leak_scan_clean() -> None:
    result = scan_monorepo_skill_discovery_leaks(ROOT)
    assert result["ok"] is True, result["leaks"]
    assert result["leak_count"] == 0


def test_only_whitelist_packages_carry_skill_md() -> None:
    package = packaged_beacon_skill_root()
    discoverable = sorted(
        child.name
        for child in package.iterdir()
        if child.is_dir() and (child / HOST_DISCOVERABLE_MANIFEST).is_file()
    )
    assert set(discoverable) == WHITELIST
    assert {p.name for p in list_host_visible_skills(package)} == WHITELIST


def test_gov_packages_use_support_manifest_not_skill_md() -> None:
    package = packaged_beacon_skill_root()
    gov_dirs = sorted(package.glob("beacon-gov-*"))
    assert gov_dirs, "expected internal gov packages to remain for progressive/support use"
    for gov in gov_dirs:
        assert not (gov / HOST_DISCOVERABLE_MANIFEST).exists(), gov
        assert (gov / INTERNAL_SUPPORT_MANIFEST).is_file(), gov


def test_archive_and_docs_generated_have_no_live_skill_md() -> None:
    archive = ROOT / "skills" / "_archive"
    if archive.is_dir():
        assert not list(archive.rglob(HOST_DISCOVERABLE_MANIFEST))
    docs = ROOT / "docs"
    if docs.is_dir():
        live = [
            p
            for p in docs.rglob(HOST_DISCOVERABLE_MANIFEST)
            if "/.generated/skills/" in p.as_posix() or "/generated/skills/" in p.as_posix()
        ]
        assert live == []


def test_top_level_legacy_beacon_skills_are_not_host_discoverable() -> None:
    for name in ("beacon-iteration-governance", "beacon-prototype-reconcile"):
        base = ROOT / "skills" / name
        assert (base / "SUPPORT.md").is_file()
        assert not (base / HOST_DISCOVERABLE_MANIFEST).exists()


def test_cursorignore_blocks_archive_and_gov_trees() -> None:
    text = (ROOT / ".cursorignore").read_text(encoding="utf-8")
    assert "skills/_archive/**" in text
    assert "skills/beacon-iteration-governance/**" in text
    assert "skills/beacon-prototype-reconcile/**" in text
    assert "skills/beacon/beacon-gov-*/**" in text
    assert "docs/**/.generated/skills/**" in text
