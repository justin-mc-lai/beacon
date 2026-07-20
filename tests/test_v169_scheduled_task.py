"""Scheduled task ledger + wake + execution logs + timer confirm (v1.6.9 / v2.0.0)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.product_goal_runtime import host_visible_whitelist
from beacon.utils.scheduled_task import (
    create_task,
    install_timer,
    list_executions,
    list_tasks,
    load_task,
    resume_task,
    suspend_task,
    wake_task,
)


ROOT = Path(__file__).resolve().parents[1]


def test_ac_st_001_create_list_get(tmp_path: Path) -> None:
    created = create_task(
        tmp_path,
        title="daily review",
        utterance="run plan review",
        cron="0 9 * * 1-5",
        host="dry_run",
    )
    assert created.get("task_id", "").startswith("st-")
    tid = created["task_id"]
    assert (tmp_path / ".beacon" / "tasks" / tid / "task.json").is_file()
    listed = list_tasks(tmp_path)
    assert listed["count"] == 1
    got = load_task(tmp_path, tid)
    assert got["title"] == "daily review"
    assert got["schema"] == "scheduled-task.v1"


def test_ac_st_002_010_wake_writes_execution_log(tmp_path: Path) -> None:
    created = create_task(tmp_path, title="t", utterance="hello", host="dry_run")
    tid = created["task_id"]
    out = wake_task(tmp_path, tid, once=True, trigger="wake")
    assert out["status"] == "succeeded"
    assert out["execution"]["schema"] == "scheduled-task-execution.v1"
    assert out["execution"]["status"] == "succeeded"
    logs = list_executions(tmp_path, tid)
    assert logs["count"] >= 1
    exec_path = tmp_path / ".beacon" / "tasks" / tid / "executions" / f"{out['execution']['exec_id']}.json"
    assert exec_path.is_file()
    log_file = tmp_path / ".beacon" / "tasks" / tid / "executions" / f"{out['execution']['exec_id']}.log"
    assert log_file.is_file()
    events = (tmp_path / ".beacon" / "tasks" / tid / "events.jsonl").read_text(encoding="utf-8")
    assert "wake_started" in events and "wake_finished" in events


def test_ac_st_003_011_suspend_skip_until_resume(tmp_path: Path) -> None:
    created = create_task(tmp_path, title="t", utterance="x", host="dry_run")
    tid = created["task_id"]
    suspend_task(tmp_path, tid, reason_code="host_interrupted", resume_pack_ref="pack-1")
    skipped = wake_task(tmp_path, tid)
    assert skipped["status"] == "skipped"
    assert skipped["reason_code"] == "suspended_skip_until_resume"
    # force can run
    forced = wake_task(tmp_path, tid, force=True)
    assert forced["status"] == "succeeded"


def test_ac_st_004_resume_then_wake(tmp_path: Path) -> None:
    created = create_task(tmp_path, title="t", utterance="x", host="dry_run")
    tid = created["task_id"]
    suspend_task(tmp_path, tid, reason_code="budget")
    resume_task(tmp_path, tid)
    out = wake_task(tmp_path, tid)
    assert out["status"] == "succeeded"
    assert load_task(tmp_path, tid)["state"] == "scheduled"


def test_ac_st_005_install_timer_requires_confirm(tmp_path: Path) -> None:
    created = create_task(tmp_path, title="t", utterance="x", every_sec=120, host="dry_run")
    tid = created["task_id"]
    blocked = install_timer(tmp_path, tid, confirm=False)
    assert blocked.get("blocked") is True
    assert blocked.get("reason_code") == "timer_install_requires_confirm"


def test_ac_st_008_no_new_public_skill() -> None:
    wl = host_visible_whitelist("beacon")
    assert "beacon-task" not in wl
    assert len(wl) == 7


def test_ac_st_012_dual_feature_packages() -> None:
    p169 = ROOT / "docs/beacon/v1.6.9/features/beacon-scheduled-task-agent-suspend-v169/truth.md"
    p200 = ROOT / "docs/beacon/v2.0.0/features/loom-scheduled-task-agent-suspend-v200/truth.md"
    assert p169.is_file() and p200.is_file()
    assert "UD-ST-010" in p169.read_text(encoding="utf-8")
    assert "UD-ST-010" in p200.read_text(encoding="utf-8")
    assert "scheduled-task-execution.v1" in p169.read_text(encoding="utf-8")
