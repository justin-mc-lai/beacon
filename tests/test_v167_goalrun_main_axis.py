"""Contract tests for beacon-goalrun-main-axis-v167."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.goalrun_main_axis import (
    CHANGE_TRIGGERS,
    GOALRUN_STATES,
    PROGRAM_V167,
    assert_submachine_cannot_complete,
    change_requires_axis_regenerate,
    default_done_when,
    generate_main_axis,
    validate_main_axis,
)

ROOT = Path(__file__).resolve().parents[1]
PROG = PROGRAM_V167
VER = "v1.6.7"


def test_axis_artifact_exists() -> None:
    gen = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    assert gen.get("blocked") is False
    path = ROOT / gen["axis_md"]
    text = path.read_text(encoding="utf-8")
    for s in ("created", "awaiting_verifier", "completed", "stage_active"):
        assert s in text


def test_mount_table_covers_lakes() -> None:
    gen = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    text = (ROOT / gen["axis_md"]).read_text(encoding="utf-8")
    # core lakes must appear
    for slug in (
        "beacon-product-goal-runtime-v167",
        "beacon-domain-fsm-authority-v167",
        "beacon-goal-durable-supervisor-v167",
        "beacon-truth-human-readable-i18n-v167",
    ):
        assert slug in text


def test_change_triggers() -> None:
    assert change_requires_axis_regenerate(["typo"])["required"] is False
    hit = change_requires_axis_regenerate(["ac", "longrun"])
    assert hit["required"] is True
    assert "ac" in hit["matched_triggers"]
    assert CHANGE_TRIGGERS


def test_validate_fail_closed(tmp_path: Path) -> None:
    # empty project-like structure without axis
    v = validate_main_axis(tmp_path, version=VER, program_slug=PROG)
    assert v.get("ok") is False
    assert v.get("blocked") is True


def test_done_when_domain() -> None:
    d = default_done_when(domain_bearing=True)
    assert "domain_fsm_coverage" in d


def test_no_submachine_complete() -> None:
    bad = assert_submachine_cannot_complete("AgentDriver", "completed")
    assert bad["blocked"] is True
    ok = assert_submachine_cannot_complete("AgentDriver", "halt_budget")
    assert ok["allowed"] is True


def test_wave_order_section() -> None:
    gen = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    text = (ROOT / gen["axis_md"]).read_text(encoding="utf-8")
    assert "Wave" in text


def test_generate_machine_json() -> None:
    gen = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    mpath = ROOT / gen["axis_machine"]
    assert mpath.is_file()
    import json

    data = json.loads(mpath.read_text(encoding="utf-8"))
    assert data.get("goalrun_states") == list(GOALRUN_STATES)


def test_q1_q6() -> None:
    gen = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    text = (ROOT / gen["axis_md"]).read_text(encoding="utf-8")
    assert "Q1" in text and "Q6" in text


def test_legal_illegal() -> None:
    tests = (
        ROOT / "docs/beacon/v1.6.7/features/beacon-goalrun-main-axis-v167/tests.md"
    ).read_text(encoding="utf-8")
    assert "TC-AXIS-LEGAL" in tests
    assert "TC-AXIS-ILLEGAL" in tests


def test_state_names_shared() -> None:
    assert "awaiting_verifier" in GOALRUN_STATES
    assert "host_interrupted" in GOALRUN_STATES


def test_refreeze_note() -> None:
    gen = generate_main_axis(ROOT, version=VER, program_slug=PROG)
    text = (ROOT / gen["axis_md"]).read_text(encoding="utf-8")
    assert "refreeze" in text.lower()


def test_validate_pass_after_generate() -> None:
    generate_main_axis(ROOT, version=VER, program_slug=PROG)
    v = validate_main_axis(ROOT, version=VER, program_slug=PROG)
    assert v.get("ok") is True
