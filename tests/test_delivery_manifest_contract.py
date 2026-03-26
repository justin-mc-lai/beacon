from __future__ import annotations

import json
from pathlib import Path


def test_delivery_manifest_should_record_git_refs_and_affected_projects():
    root = Path(__file__).resolve().parents[1]
    path = root / "docs" / "beacon" / "v1.1.1" / "execution" / "delivery-manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    affected = payload["affected_projects"]
    assert affected
    item = affected[0]
    for key in ("base_branch", "target_branch", "current_branch", "commit", "worktree_path"):
        assert key in item
