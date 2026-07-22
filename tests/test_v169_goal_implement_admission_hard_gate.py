"""AC-GIA: goal implement admission hard gate (v1.6.9 / v2.0.0)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from beacon.utils.goal_implement_admission import (
    ensure_goal_implement_admission,
    resolve_goal_implement_target,
)
from beacon.utils.product_goal_runtime import create_goal_run, tick_goal_run
from beacon.utils.project_governance import commit_governance_payload


VERSION = "v1.6.9"
FEATURE = "demo-goal-admit-feat"


def _git(cmd: list[str], cwd: Path) -> str:
    r = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(r.stdout or "").strip()


def _seed_repo(root: Path, *, branch: str = "main") -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)



def _seed_frozen_truth(root: Path, *, feature: str = FEATURE, version: str = VERSION) -> None:
    """Decision A: implement admission requires frozen feature package."""
    d = root / "docs" / "beacon" / version / "features" / feature
    d.mkdir(parents=True, exist_ok=True)
    (d / "truth.md").write_text(
        f"""---
slug: {feature}
version: {version}
status: frozen
revision_id: R1
language: en
parser_contract: beacon-feature-package-v2
---

# {feature}

## Acceptance Criteria
| AC | Desc |
|----|------|
| AC-001 | seeded frozen for GIA tests |
""",
        encoding="utf-8",
    )
    (d / "tests.md").write_text("# tests\n", encoding="utf-8")
    (d / "tasks.md").write_text("# tasks\n", encoding="utf-8")
    (d / "evidence.md").write_text("# evidence\n", encoding="utf-8")


def _seed_governance(root: Path, *, require: bool = True, mode: str = "dedicated") -> None:
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
                "per_service_canonical_branch": {"beacon": f"beacon/{VERSION}"},
                "branch_guard_mode": "strict",
                "validation_state": "active",
                "previous_version_baseline_branch": "main",
                "next_version_feature_branch": f"beacon/{VERSION}/<feature-slug>",
                "worktree_mode": mode,
                "worktree_path": f".beacon/worktrees/{VERSION}",
                "require_workspace_admission": require,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    docs = root / "docs" / "beacon" / VERSION
    docs.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "VERSION").write_text(f"{VERSION}\n", encoding="utf-8")


def test_ac_gia_resolve_target() -> None:
    t = resolve_goal_implement_target(
        {"version": "v1.6.9", "feature": "", "lakes": ["v2.0.0::my-lake"]}
    )
    assert t["version"] == "v2.0.0"
    assert t["feature_slug"] == "my-lake"


def test_ac_gia_001_missing_feature_blocked(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True)
    gate = ensure_goal_implement_admission(
        tmp_path, {"version": VERSION, "feature": "", "lakes": []}
    )
    assert gate["allow_implement"] is False
    assert gate["reason_code"] == "goal_implement_feature_required"


def test_ac_gia_002_require_true_admit_pass(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True, mode="dedicated")
    _seed_frozen_truth(tmp_path)
    gate = ensure_goal_implement_admission(
        tmp_path, {"version": VERSION, "feature": FEATURE}
    )
    assert gate["allow_implement"] is True, gate
    assert gate["worktree_path"]
    wt = Path(gate["worktree_path"])
    assert wt.exists()
    assert (wt / ".git").exists() or (wt / ".git").is_file()
    assert gate.get("merge_main") is not None or gate["admission"].get("merge_main") is not None


def test_ac_gia_003_require_false_force_worktree(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=False, mode="branch-only")
    _seed_frozen_truth(tmp_path)
    gate = ensure_goal_implement_admission(
        tmp_path, {"version": VERSION, "feature": FEATURE}
    )
    assert gate["allow_implement"] is True, gate
    assert gate.get("goal_forced_worktree") is True
    assert Path(gate["worktree_path"]).exists()


def test_ac_gia_004_second_call_switches(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True, mode="dedicated")
    _seed_frozen_truth(tmp_path)
    g1 = ensure_goal_implement_admission(tmp_path, {"version": VERSION, "feature": FEATURE})
    assert g1["allow_implement"] is True
    g2 = ensure_goal_implement_admission(tmp_path, {"version": VERSION, "feature": FEATURE})
    assert g2["allow_implement"] is True
    attempt = (g2.get("worktree_attempt") or g2.get("admission", {}).get("worktree_attempt") or {})
    # second pass should switch or still pass with existing lane
    assert attempt.get("status") in {"switched", "created", None} or g2["status"] == "pass"


def test_ac_gia_005_tick_execute_blocks_without_feature(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True)
    (tmp_path / "docs" / "beacon" / VERSION).mkdir(parents=True, exist_ok=True)
    run = create_goal_run(tmp_path, utterance="implement something", version=VERSION, feature="")
    # force stage to implement
    state = tmp_path / ".beacon" / "state" / "product-goal" / f"{run['run_id']}.json"
    data = json.loads(state.read_text(encoding="utf-8"))
    data["current_stage"] = "implement"
    data["feature"] = ""
    data["lakes"] = []
    state.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    out = tick_goal_run(tmp_path, run["run_id"], execute=True)
    assert out.get("blocked") is True or out.get("implement_admission", {}).get("allow_implement") is False
    assert out.get("implement_delegate") != "ralph" or out.get("blocked")


def test_ac_gia_005b_tick_execute_allows_with_feature(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True, mode="dedicated")
    _seed_frozen_truth(tmp_path)
    (tmp_path / "docs" / "beacon" / VERSION).mkdir(parents=True, exist_ok=True)
    run = create_goal_run(
        tmp_path,
        utterance="implement lake",
        version=VERSION,
        feature=FEATURE,
    )
    state = tmp_path / ".beacon" / "state" / "product-goal" / f"{run['run_id']}.json"
    data = json.loads(state.read_text(encoding="utf-8"))
    data["current_stage"] = "implement"
    state.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    out = tick_goal_run(tmp_path, run["run_id"], execute=True)
    adm = out.get("implement_admission") or {}
    assert adm.get("allow_implement") is True, out
    assert out.get("implement_delegate") == "ralph"
    assert not out.get("blocked")


def test_ac_gia_006_execution_log(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True)
    _seed_frozen_truth(tmp_path)
    (tmp_path / "docs" / "beacon" / VERSION).mkdir(parents=True, exist_ok=True)
    run = create_goal_run(tmp_path, utterance="impl", version=VERSION, feature=FEATURE)
    state = tmp_path / ".beacon" / "state" / "product-goal" / f"{run['run_id']}.json"
    data = json.loads(state.read_text(encoding="utf-8"))
    data["current_stage"] = "implement"
    state.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tick_goal_run(tmp_path, run["run_id"], execute=True)
    log = tmp_path / ".beacon" / "state" / "product-goal" / run["run_id"] / "execution.jsonl"
    assert log.is_file()
    text = log.read_text(encoding="utf-8")
    assert "implement_admission" in text


def test_ac_gia_007_feature_packages_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (
        root / "docs/beacon/v1.6.9/features/beacon-goal-implement-admission-hard-gate-v169/truth.md"
    ).is_file()
    assert (
        root / "docs/beacon/v2.0.0/features/loom-goal-implement-admission-hard-gate-v200/truth.md"
    ).is_file()


def test_ac_gia_008_docs_registered() -> None:
    root = Path(__file__).resolve().parents[1]
    flow = (root / "skills/beacon/references/git-worktree-execution-flow.md").read_text(encoding="utf-8")
    assert "Goal implement admission hard gate" in flow
    gov = (root / "skills/beacon/beacon-gov-branch/SKILL.md").read_text(encoding="utf-8")
    assert "ensure_goal_implement_admission" in gov or "implement hard gate" in gov.lower()
    goal = (root / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    assert "ensure_goal_implement_admission" in goal


def test_merge_conflict_blocks(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True)
    _seed_frozen_truth(tmp_path)
    with patch(
        "beacon.utils.workspace_admission._merge_main_into_feature_branch",
        return_value={"status": "conflict", "base_branch": "main", "stderr": "CONFLICT"},
    ):
        gate = ensure_goal_implement_admission(
            tmp_path, {"version": VERSION, "feature": FEATURE}
        )
    assert gate["allow_implement"] is False
    assert "merge" in str(gate.get("reason_code") or "").lower() or gate.get("reason_code") == "merge_main_conflict"
