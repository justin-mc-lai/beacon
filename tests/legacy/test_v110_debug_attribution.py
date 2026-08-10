"""v1.1.0 debug attribution contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_debug_event(root: Path, *, run_id: str) -> None:
    debug_dir = root / ".beacon" / "state" / "debug-feedback"
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / f"{run_id}.jsonl").write_text(
        json.dumps(
            {
                "ts": "2026-03-07T00:00:00Z",
                "run_id": run_id,
                "source": "prompt.optimize",
                "goal": "请先检查 gate 并直接写代码上线",
                "intent": "workflow",
                "confidence": 0.52,
                "boundary_state": "mixed_need_confirm",
                "block_reason": "mixed-boundary-needs-confirmation",
                "recommended_command": "beacon workflow start ...",
                "executed": False,
                "exit_code": None,
                "note": "debug",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def test_attribution_should_generate_reason_codes(tmp_path: Path):
    run_id = "run-debug-attribution-001"
    _seed_debug_event(tmp_path, run_id=run_id)

    result = _invoke([
        "feedback",
        "extract",
        run_id,
        "--source",
        "debug",
        "--project-root",
        str(tmp_path),
        "--json",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    feedback = payload.get("feedback", [])
    reason_codes = {str(item.get("reason_code", "")) for item in feedback if isinstance(item, dict)}

    assert "boundary_mixed_ambiguous" in reason_codes
    assert "low-confidence" in reason_codes


def test_candidate_override_should_be_tracked(tmp_path: Path):
    run_id = "run-debug-attribution-002"
    _seed_debug_event(tmp_path, run_id=run_id)

    result = _invoke([
        "feedback",
        "extract",
        run_id,
        "--source",
        "debug",
        "--override",
        "low-confidence:router_false_positive",
        "--project-root",
        str(tmp_path),
        "--json",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    feedback = payload.get("feedback", [])
    overridden = [
        item
        for item in feedback
        if isinstance(item, dict)
        and str(item.get("original_reason_code", "")) == "low-confidence"
        and str(item.get("reason_code", "")) == "router_false_positive"
    ]
    assert overridden
    assert isinstance(overridden[0].get("override_trace"), dict)
