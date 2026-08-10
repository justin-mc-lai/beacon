from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from beacon.utils.project_governance import commit_governance_payload
from beacon.utils.workspace_admission import run_workspace_admit, write_admission_artifact

VERSION = "v1.6.2"
FEATURE = "beacon-global-workspace-git-admission-v162"
REPO_ROOT = Path(__file__).resolve().parents[1]
CURSOR_HOOK = REPO_ROOT / ".cursor/hooks/beacon-workspace-admission-gate.py"
CLAUDE_HOOK = REPO_ROOT / ".claude/hooks/beacon-workspace-admission-gate.py"


def _git(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(result.stdout or "").strip()


def _seed_repo(root: Path, *, branch: str = "pre-main") -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_governance(root: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "single_repo",
            "default_execution_service": "beacon",
            "service_bindings": [
                {
                    "service_key": "beacon",
                    "repo_root": str(root),
                    "repo_root_relative": ".",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                }
            ],
        },
        "version_scoped_metadata": {
            VERSION: {
                "version": VERSION,
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": "beacon/v1.6.2"},
                "branch_guard_mode": "strict",
                "validation_state": "active",
                "previous_version_baseline_branch": "pre-main",
                "next_version_feature_branch": "beacon/v1.6.2/<feature-slug>",
                "worktree_mode": "dedicated",
                "worktree_path": ".beacon/worktrees/v1.6.2",
                "require_workspace_admission": True,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    docs = root / "docs" / "beacon"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "VERSION").write_text(f"{VERSION}\n", encoding="utf-8")


def _invoke_hook(root: Path, *, target: Path, cwd: Path | None = None) -> dict:
    payload = {
        "tool_name": "Write",
        "tool_input": {"path": str(target)},
        "cwd": str(cwd or root),
    }
    proc = subprocess.run(
        [sys.executable, str(CURSOR_HOOK)],
        input=json.dumps(payload),
        cwd=root,
        capture_output=True,
        text=True,
        env={**os.environ, "TRELLIS_DISABLE_HOOKS": "1"},
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_cursor_hook_denies_missing_artifact(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    target = tmp_path / "src.py"
    result = _invoke_hook(tmp_path, target=target, cwd=tmp_path)
    assert result.get("permission") == "deny"


def test_cursor_hook_allows_valid_artifact(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    admit = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    worktree = Path(str(admit["worktree_path"]))
    target = worktree / "src.py"
    result = _invoke_hook(tmp_path, target=target, cwd=worktree)
    assert result.get("permission") == "allow"


def test_hook_no_ttl_deny(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    admit = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    worktree = Path(str(admit["worktree_path"]))
    artifact_path = tmp_path / ".beacon/state/workspace-admission/v1.6.2" / f"{FEATURE}.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["issued_at"] = "2020-01-01T00:00:00+00:00"
    write_admission_artifact(artifact_path, artifact)
    target = worktree / "still-valid.py"
    result = _invoke_hook(tmp_path, target=target, cwd=worktree)
    assert result.get("permission") == "allow"


def test_claude_hook_parity() -> None:
    assert CURSOR_HOOK.is_file()
    if not CLAUDE_HOOK.is_file():
        pytest.skip("claude hook not installed in this workspace (.claude/ is local-excluded)")
    assert CLAUDE_HOOK.is_file()
    assert CURSOR_HOOK.read_text(encoding="utf-8") == CLAUDE_HOOK.read_text(encoding="utf-8")


def test_beacon_hook_independent_of_trellis(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    payload = {
        "tool_name": "Write",
        "tool_input": {"path": str(tmp_path / "blocked.py")},
        "cwd": str(tmp_path),
    }
    proc = subprocess.run(
        [sys.executable, str(CURSOR_HOOK)],
        input=json.dumps(payload),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "TRELLIS_DISABLE_HOOKS": "1"},
    )
    assert proc.returncode == 0
    result = json.loads(proc.stdout)
    assert result.get("permission") == "deny"
    hooks_json = json.loads((REPO_ROOT / ".cursor/hooks.json").read_text(encoding="utf-8"))
    pre_hooks = hooks_json.get("hooks", {}).get("preToolUse", [])
    assert any("beacon-workspace-admission-gate.py" in str(item.get("command", "")) for item in pre_hooks)
