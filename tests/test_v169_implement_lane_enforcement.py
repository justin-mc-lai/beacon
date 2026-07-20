"""Implement-lane enforcement (UD-ENF) tests."""

from __future__ import annotations

import json
import os
from pathlib import Path

from beacon.utils.implement_lane_enforcement import (
    REASON_EXCEPTION_OK,
    REASON_MAIN_IMPLEMENT,
    check_main_implement_commit,
    is_business_path,
    release_implement_lane_advisory,
    setup_git_hooks,
    verify_git_hooks,
    write_exception_evidence,
)


ROOT = Path(__file__).resolve().parents[1]


def test_business_path_classification() -> None:
    assert is_business_path("beacon/utils/foo.py")
    assert is_business_path("packages/beacon-rs/x.rs")
    assert is_business_path("tests/test_v169_foo.py")
    assert not is_business_path("docs/beacon/v1.6.9/features/x/truth.md")
    assert not is_business_path("skills/beacon/beacon-goal/SKILL.md")
    assert not is_business_path("README.md")


def test_ac_enf_001_main_blocks_business(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("BEACON_ALLOW_MAIN_IMPLEMENT", raising=False)
    result = check_main_implement_commit(
        tmp_path,
        files=["beacon/utils/x.py", "docs/a.md"],
        branch="main",
    )
    assert result["blocked"] is True
    assert result["reason_code"] == REASON_MAIN_IMPLEMENT
    assert "beacon/utils/x.py" in result["business_files"]


def test_ac_enf_002_main_docs_pass(tmp_path: Path) -> None:
    result = check_main_implement_commit(
        tmp_path,
        files=["docs/beacon/v1.6.9/features/x/truth.md", "README.md"],
        branch="main",
    )
    assert result["blocked"] is False


def test_ac_enf_003_exception_env_and_evidence(tmp_path: Path, monkeypatch) -> None:
    write_exception_evidence(tmp_path, reason="hotfix", feature="demo")
    monkeypatch.setenv("BEACON_ALLOW_MAIN_IMPLEMENT", "1")
    result = check_main_implement_commit(
        tmp_path,
        files=["beacon/commands/task.py"],
        branch="main",
    )
    assert result["blocked"] is False
    assert result["reason_code"] == REASON_EXCEPTION_OK


def test_leaf_branch_allows_business(tmp_path: Path) -> None:
    result = check_main_implement_commit(
        tmp_path,
        files=["beacon/utils/x.py"],
        branch="beacon/v1.6.9/beacon-implement-lane-enforcement-v169",
    )
    assert result["blocked"] is False


def test_ac_enf_004_005_setup_and_verify_hooks(tmp_path: Path) -> None:
    # minimal git repo
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    # need beacon package importable - use real project by writing hooks into tmp with file check only
    # setup uses project_root for hooks path via git
    out = setup_git_hooks(tmp_path, force=True)
    assert out["status"] == "ok"
    assert (tmp_path / ".git" / "hooks" / "pre-commit").is_file()
    assert (tmp_path / ".git" / "hooks" / "pre-push").is_file()
    ver = verify_git_hooks(tmp_path)
    assert ver["ok"] is True


def test_ac_enf_007_dual_packages() -> None:
    p169 = ROOT / "docs/beacon/v1.6.9/features/beacon-implement-lane-enforcement-v169/truth.md"
    p200 = ROOT / "docs/beacon/v2.0.0/features/loom-implement-lane-enforcement-v200/truth.md"
    assert p169.is_file() and p200.is_file()
    assert "UD-ENF-001" in p169.read_text(encoding="utf-8")


def test_ac_enf_008_release_advisory_nonfatal(tmp_path: Path) -> None:
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    adv = release_implement_lane_advisory(tmp_path, version="v1.6.9")
    assert adv.get("blocking") is False
    assert adv.get("check") == "release_implement_lane_advisory"
