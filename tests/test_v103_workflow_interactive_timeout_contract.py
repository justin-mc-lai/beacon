"""v1.0.3 interactive HUD timeout/menu contracts."""

from __future__ import annotations

from beacon.commands import workflow as workflow_cmd
from beacon.utils.workflow_memory import load_lifecycle_events


def test_interactive_menu_should_list_six_actions(capsys):
    workflow_cmd._print_interactive_menu()  # noqa: SLF001
    out = capsys.readouterr().out
    for snippet in (
        "1) 执行 next_stage",
        "2) 自动补齐到 release",
        "3) 查看阻塞详情",
        "4) 执行反馈修订",
        "5) 暂停并保存",
        "6) 退出",
    ):
        assert snippet in out


def test_timeout_should_default_to_pause_and_record_event(tmp_path, monkeypatch):
    run_id = "run-timeout-001"
    monkeypatch.setattr(workflow_cmd, "_input_with_timeout", lambda *_args, **_kwargs: None)

    resolved = workflow_cmd._resolve_action_with_timeout(  # noqa: SLF001
        run_id=run_id,
        project_root=tmp_path,
        confirm_timeout=1,
        on_timeout="pause",
    )
    assert resolved == "pause"

    events = load_lifecycle_events(tmp_path, run_id=run_id, stage="workflow", event="workflow_paused")
    assert events
    latest = events[-1]
    details = latest.get("details", {})
    assert details.get("reason") == "timeout_or_no_input"
    assert details.get("resolved_action") == "pause"


def test_timeout_continue_should_resolve_single_step(tmp_path, monkeypatch):
    run_id = "run-timeout-002"
    monkeypatch.setattr(workflow_cmd, "_input_with_timeout", lambda *_args, **_kwargs: None)

    resolved = workflow_cmd._resolve_action_with_timeout(  # noqa: SLF001
        run_id=run_id,
        project_root=tmp_path,
        confirm_timeout=1,
        on_timeout="continue",
    )
    assert resolved == "single-step"

    events = load_lifecycle_events(tmp_path, run_id=run_id, stage="workflow", event="workflow_paused")
    assert events
    assert events[-1].get("details", {}).get("resolved_action") == "single-step"
