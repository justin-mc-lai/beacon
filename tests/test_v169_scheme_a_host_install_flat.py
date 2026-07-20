"""Scheme A host install: flat 1+6 only, no package-root leak."""

from __future__ import annotations

from pathlib import Path

from beacon.utils import agent_surface as asurf


def test_install_global_agents_scheme_a_flat_only(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    for brand, prefix in (("beacon", "beacon"), ("loom", "loom")):
        root = repo / "skills" / brand
        root.mkdir(parents=True)
        (root / "SKILL.md").write_text(f"---\nname: {brand}\n---\n", encoding="utf-8")
        for leaf in ("goal", "plan", "truth", "design", "implement", "qa", "release"):
            d = root / f"{prefix}-{leaf}"
            d.mkdir()
            (d / "SKILL.md").write_text(f"---\nname: {prefix}-{leaf}\n---\n", encoding="utf-8")
        # internal progressive skill must NOT be installed
        internal = root / f"{prefix}-gov-router"
        internal.mkdir()
        (internal / "SKILL.md").write_text("---\nname: internal\n---\n", encoding="utf-8")

    home = tmp_path / "home"
    agents = home / ".agents" / "skills"
    agents.mkdir(parents=True)
    # pre-existing package root leak
    (agents / "beacon").symlink_to(repo / "skills" / "beacon")
    (agents / "loom").symlink_to(repo / "skills" / "loom")

    monkeypatch.setattr(asurf, "packaged_beacon_skill_root", lambda: repo / "skills" / "beacon")

    result = asurf.install_global_agents_beacon_skills(beacon_root=repo, dry_run=False, home=home)
    assert result["scheme_a"] is True
    assert not (agents / "beacon").exists()
    assert not (agents / "loom").exists()
    for brand, prefix in (("beacon", "beacon"), ("loom", "loom")):
        for leaf in ("goal", "plan", "truth", "design", "implement", "qa", "release"):
            link = agents / f"{prefix}-{leaf}"
            assert link.is_symlink(), link
            assert link.resolve() == (repo / "skills" / brand / f"{prefix}-{leaf}").resolve()
        assert not (agents / f"{prefix}-gov-router").exists()

    verify = asurf.verify_global_agents_beacon_skills(home=home)
    assert verify["status"] == "pass"
    assert verify["leak_package_roots"] == []
    assert verify["expected_count"] == 14


def test_install_global_claude_scheme_a_removes_package_root(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    root = repo / "skills" / "beacon"
    root.mkdir(parents=True)
    for leaf in ("goal", "plan", "truth", "design", "implement", "qa", "release"):
        d = root / f"beacon-{leaf}"
        d.mkdir()
        (d / "SKILL.md").write_text(f"---\nname: beacon-{leaf}\n---\n", encoding="utf-8")

    home = tmp_path / "home"
    claude = home / ".claude" / "skills"
    claude.mkdir(parents=True)
    (claude / "beacon").symlink_to(repo)

    monkeypatch.setattr(asurf, "packaged_beacon_skill_root", lambda: root)
    result = asurf.install_global_claude_beacon_skills(beacon_root=repo, dry_run=False, home=home)
    assert result["scheme_a"] is True
    assert not (claude / "beacon").exists()
    assert (claude / "beacon-goal").is_symlink()
    verify = asurf.verify_global_claude_beacon_skills(home=home)
    assert verify["status"] == "pass"
    assert verify["leak_package_roots"] == []
