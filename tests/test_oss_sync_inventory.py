from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.oss_sync_inventory import (
    build_source_capability_inventory,
    resolve_oss_sync_source_inventory,
)


def _seed_oss_sync(tmp_path: Path) -> Path:
    root = tmp_path / "oss-sync"
    (root / "index" / "analysis").mkdir(parents=True)
    repos = {
        "repositories": [{
            "name": "compound-engineering-plugin",
            "owner": "EveryInc",
            "repo": "compound-engineering-plugin",
            "relative_path": "agents/agent-skills/compound-engineering-plugin",
            "remote_fetch": "git@github.com:EveryInc/compound-engineering-plugin.git",
            "analysis_status": "complete",
        }]
    }
    (root / "index" / "repos.json").write_text(json.dumps(repos), encoding="utf-8")
    (root / "index" / "analysis" / "everyinc-compound-engineering-plugin.json").write_text(
        json.dumps({"skills_paths": ["a", "b", "c", "d", "e"], "entrypoints": ["src/index.ts"], "top_level_dirs": ["plugins"]}),
        encoding="utf-8",
    )
    return root


def test_compound_ref_resolves_oss_sync_slug(tmp_path: Path) -> None:
    root = _seed_oss_sync(tmp_path)
    entries = resolve_oss_sync_source_inventory(
        ["compound-engineering-plugin"], oss_sync_root=root,
    )
    assert len(entries) == 1
    assert entries[0]["oss_sync_slug"] == "everyinc-compound-engineering-plugin"
    assert "persona_reviewer_catalog" in entries[0]["capabilities"]
    assert entries[0]["inventory_source"] == "oss_sync_index"


def test_unknown_ref_falls_back_to_defaults(tmp_path: Path) -> None:
    entries = build_source_capability_inventory(
        "some prompt", ["unknown-source-xyz"], "full_parity", oss_sync_root=tmp_path / "missing",
    )
    assert len(entries) == 1
    assert entries[0]["inventory_source"] == "fallback_defaults"
    assert "reviewer_catalog" in entries[0]["capabilities"]


def test_full_parity_uses_fake_oss_sync_root(tmp_path: Path) -> None:
    root = _seed_oss_sync(tmp_path)
    entries = build_source_capability_inventory(
        "完整复刻 compound-engineering-plugin",
        ["oss-sync/agents/agent-skills/compound-engineering-plugin"],
        "full_parity",
        oss_sync_root=root,
    )
    assert entries[0]["display_name"] == "compound-engineering-plugin"
    assert "multi_skill_catalog" in entries[0]["capabilities"]
