from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.agent_trace import (
    SCHEMA_VERSION,
    agent_trace_coverage_signal,
    read_trace_events,
    record_lifecycle_stage_trace,
    resolve_lifecycle_trace_run_id,
    trace_path,
)
from beacon.utils.loom_trace import assert_no_full_chat_authority, record_driver_turn_trace


def test_resolve_run_id_prefers_explicit() -> None:
    assert resolve_lifecycle_trace_run_id(run_id="goal-abc", feature_slug="x") == "goal-abc"
    assert resolve_lifecycle_trace_run_id(feature_slug="trace-lifecycle-binding-v1610").startswith("lifecycle-")


def test_record_lifecycle_stage_trace_writes_jsonl(tmp_path: Path) -> None:
    out = record_lifecycle_stage_trace(
        tmp_path,
        harness="truth",
        stage="truth-review",
        feature_slug="trace-lifecycle-binding-v1610",
        event_type="gate_verdict",
        summary="review pass",
        payload={"review_gate_pass": True, "full_chat": "MUST_STRIP"},
        fail_closed=True,
    )
    assert out["status"] == "pass"
    run_id = out["run_id"]
    path = trace_path(tmp_path, run_id)
    assert path.is_file()
    events = read_trace_events(tmp_path, run_id)
    assert len(events) >= 1
    ev = events[-1]
    assert ev["schema_version"] == SCHEMA_VERSION
    assert ev["harness"] == "truth"
    assert ev["feature_slug"] == "trace-lifecycle-binding-v1610"
    assert "full_chat" not in (ev.get("payload") or {})
    sig = agent_trace_coverage_signal(tmp_path)
    assert sig["status"] == "pass"
    assert sig.get("valid_run_count", 0) >= 1


def test_multi_stage_same_feature_stream(tmp_path: Path) -> None:
    feat = "demo-lake"
    for harness, stage, et in (
        ("truth", "truth-review", "gate_verdict"),
        ("freeze", "freeze", "output"),
        ("qa", "qa-run", "gate_verdict"),
    ):
        r = record_lifecycle_stage_trace(
            tmp_path,
            harness=harness,
            stage=stage,
            feature_slug=feat,
            event_type=et,
            summary=f"{harness} ok",
        )
        assert r["status"] == "pass"
    run_id = resolve_lifecycle_trace_run_id(feature_slug=feat)
    events = read_trace_events(tmp_path, run_id)
    harnesses = {e.get("harness") for e in events}
    assert {"truth", "freeze", "qa"} <= harnesses
    assert agent_trace_coverage_signal(tmp_path)["status"] == "pass"


def test_driver_turn_trace_surfaces_status(tmp_path: Path) -> None:
    out = record_driver_turn_trace(
        tmp_path,
        "goal-run-1",
        turn_n=1,
        prompt_path=".beacon/goal/goal-run-1/turn-1.prompt.md",
        exit_code=0,
        summary="turn ok",
    )
    assert out["status"] == "ok"
    events = read_trace_events(tmp_path, "goal-run-1")
    assert len(events) >= 2
    bundle_ok = assert_no_full_chat_authority(
        {
            "full_chat_authority": False,
            "agent_events": events,
        }
    )
    assert bundle_ok.get("ok") is not False or "status" in bundle_ok


def test_fail_closed_when_traces_not_dir(tmp_path: Path) -> None:
    blocked = tmp_path / ".beacon" / "traces"
    blocked.parent.mkdir(parents=True, exist_ok=True)
    blocked.write_text("not-a-dir", encoding="utf-8")
    out = record_lifecycle_stage_trace(
        tmp_path,
        harness="freeze",
        feature_slug="x",
        summary="should block",
        fail_closed=True,
    )
    assert out["status"] == "blocked"


def test_package_gold_shape_present() -> None:
    root = Path(__file__).resolve().parents[1]
    truth = root / "docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md"
    text = truth.read_text(encoding="utf-8")
    for marker in ("## 人话", "Intent Coverage Matrix", "FSM 五元组", "Non-goals", "AC-TRC-001"):
        assert marker in text, marker
    assert "record_lifecycle_stage_trace" in (root / "beacon/utils/agent_trace.py").read_text(encoding="utf-8")
