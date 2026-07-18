"""v2.0.0 Loom optional subagent tests."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.loom_subagent import (
    arm_and_run,
    assert_satellite_cannot_write_truth,
    create_session,
    detect_subagent_intent,
    omx_checklist_b1_b6,
)
from beacon.utils.product_goal_runtime import run_goal_facade
from beacon.utils.goal_durable_supervisor import execution_log_path


def test_opt_in_default_off(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="plain goal", version="v2.0.0")
    sess = create_session(tmp_path, run["run_id"], lakes=["a"], opt_in=False)
    assert sess["spawned"] is False
    assert sess.get("reason_code") == "subagent_default_off"


def test_plan_creates_worktree(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="并行 subagent 多湖", version="v2.0.0")
    sess = create_session(tmp_path, run["run_id"], lakes=["lake-a"], opt_in=True)
    assert sess["opt_in"] is True
    assert sess["satellites"]
    wt = tmp_path / sess["satellites"][0]["worktree"]
    assert wt.exists()


def test_one_lake_one_satellite(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="subagent", version="v2.0.0")
    sess = create_session(tmp_path, run["run_id"], lakes=["x", "y"], opt_in=True)
    assert sess["one_lake_one_satellite"] is True
    assert len(sess["satellites"]) == 2


def test_respects_depends_on(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="subagent", version="v2.0.0")
    # lake b depends on a, but only b listed → blocked
    sess = create_session(
        tmp_path,
        run["run_id"],
        lakes=["b"],
        depends_on={"b": ["a"]},
        opt_in=True,
    )
    assert sess.get("blocked") is True or sess.get("reason_code") == "subagent_depends_on_unmet"


def test_satellite_no_main_truth(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="subagent", version="v2.0.0")
    sess = create_session(tmp_path, run["run_id"], lakes=["z"], opt_in=True)
    wt = tmp_path / sess["satellites"][0]["worktree"]
    main_truth = tmp_path / "docs/beacon/v2.0.0/features/z/truth.md"
    r = assert_satellite_cannot_write_truth(wt, main_truth_path=main_truth)
    assert r["status"] == "pass"
    assert r["may_write_truth_on_main"] is False


def test_merge_to_star(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="subagent", version="v2.0.0")
    sess = create_session(tmp_path, run["run_id"], lakes=["m"], opt_in=True)
    out = arm_and_run(tmp_path, run["run_id"], session=sess)
    assert out["state"] == "done"
    assert out["merge_policy"] == "satellites_merge_to_star_only"
    assert out.get("product_complete") is False


def test_spawn_backend(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="subagent", version="v2.0.0")
    sess = create_session(tmp_path, run["run_id"], lakes=["s"], opt_in=True, backend="file")
    assert sess["spawn_backend"] in {"file", "tmux", "bridge"}


def test_fallback_reason(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="subagent", version="v2.0.0")
    sess = create_session(tmp_path, run["run_id"], lakes=["s"], opt_in=True, backend="tmux")
    # if tmux missing, fallback may be set
    assert sess.get("spawn_backend") in {"tmux", "file", "bridge"}


def test_omx_checklist_b1_b6() -> None:
    c = omx_checklist_b1_b6()
    for k in ("B1", "B2", "B3", "B4", "B5", "B6"):
        assert k in c


def test_no_complete_from_fanout(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="subagent", version="v2.0.0")
    sess = create_session(tmp_path, run["run_id"], lakes=["a"], opt_in=True)
    out = arm_and_run(tmp_path, run["run_id"], session=sess)
    assert out.get("cannot_complete_goal") is True or out.get("product_complete") is False


def test_execution_log_events(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="subagent", version="v2.0.0")
    rid = run["run_id"]
    create_session(tmp_path, rid, lakes=["a"], opt_in=True)
    arm_and_run(tmp_path, rid)
    path = execution_log_path(tmp_path, rid)
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "subagent" in text


def test_legal_illegal() -> None:
    assert detect_subagent_intent("用并行 subagent") is True
    assert detect_subagent_intent("普通目标") is False
