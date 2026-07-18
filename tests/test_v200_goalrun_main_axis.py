"""v2.0.0 GoalRun main-axis sync (Loom mounts)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.goalrun_main_axis import (
    CHANGE_TRIGGERS,
    generate_main_axis,
    validate_main_axis,
)

ROOT = Path(__file__).resolve().parents[1]
PROG = "beacon-v2-product-goal-parallel-v200"
VER = "v2.0.0"


def test_generate_v2() -> None:
    r = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    assert r.get("blocked") is False
    assert (ROOT / r["axis_md"]).is_file()


def test_mounts_loom() -> None:
    r = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    text = (ROOT / r["axis_md"]).read_text(encoding="utf-8")
    for slug in (
        "loom-brand-surface",
        "loom-goal-optional-subagent",
        "loom-goal-trace-bundle",
        "beacon-v2-goal-durable-longrun",
        "beacon-v2-product-goal-orchestrator",
    ):
        assert slug in text


def test_subagent_trace_sections() -> None:
    r = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    text = (ROOT / r["axis_md"]).read_text(encoding="utf-8")
    assert "Subagent" in text or "subagent" in text.lower()
    assert "agent_trace" in text or "Trace" in text


def test_validate_v2() -> None:
    generate_main_axis(ROOT, version=VER, program_slug=PROG)
    v = validate_main_axis(ROOT, version=VER, program_slug=PROG)
    assert v.get("ok") is True


def test_wave0_to_3() -> None:
    r = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    text = (ROOT / r["axis_md"]).read_text(encoding="utf-8")
    assert "Wave 0" in text
    assert "subagent" in text.lower()
    assert "trace" in text.lower()


def test_triggers_shared() -> None:
    assert "longrun" in CHANGE_TRIGGERS
    assert "domain_fsm" in CHANGE_TRIGGERS
    assert "subagent" in CHANGE_TRIGGERS
