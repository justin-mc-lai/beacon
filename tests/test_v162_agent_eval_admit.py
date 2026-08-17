from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from beacon.utils.agent_surface import setup_agent_surface, v160_skill_package_projection

VERSION = "v1.6.2"
FEATURE = "beacon-global-workspace-git-admission-v162"
REPO_ROOT = Path(__file__).resolve().parents[1]


def _invoke(args: list[str], *, cwd: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "beacon", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env={"BEACON_ALLOW_CONTEXT_VERSION_DRIFT": "1", **dict(__import__("os").environ)},
    )
    payload: dict = {"_exit_code": proc.returncode, "_stderr": proc.stderr}
    if proc.stdout.strip():
        payload.update(json.loads(proc.stdout))
    return payload


def test_slash_skill_step0_admit(tmp_path: Path) -> None:
    """AC-011: /beacon-gen-implement must route through workspace admit Step 0."""
    projections = v160_skill_package_projection()
    skill_ids = {item.id for item in projections}
    assert "beacon-gen-implement" in skill_ids
    implement_skill = next(item for item in projections if item.id == "beacon-gen-implement")
    text = implement_skill.content or ""
    if not text and implement_skill.source_dir is not None:
        text = (implement_skill.source_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "GIT_ADMISSION" in text
    assert "beacon workspace admit" in text
    assert "worktree_path" in text

    setup_agent_surface(
        tmp_path,
        agent="cursor",
        runtime_version=VERSION,
        docs_version=VERSION,
        dry_run=False,
        force=True,
    )
    materialized = tmp_path / ".cursor/skills/beacon-gen-implement/SKILL.md"
    assert materialized.is_file()
    materialized_text = materialized.read_text(encoding="utf-8")
    assert "GIT_ADMISSION" in materialized_text
    assert "workspace admit" in materialized_text

    admit = _invoke(
        [
            "workspace",
            "admit",
            "--project-root",
            str(REPO_ROOT),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--json",
        ],
        cwd=REPO_ROOT,
    )
    assert admit.get("status") == "pass", admit
    assert admit.get("worktree_path")
