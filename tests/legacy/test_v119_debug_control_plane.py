from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _seed_run(root: Path, run_id: str = "run-ctrl-001") -> str:
    run_dir = root / ".beacon" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "state.json").write_text(
        json.dumps({"run_id": run_id, "status": "blocked", "version": "v1.1.9", "feature": "Control Feature"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return run_id



def test_v119_debug_capture_should_update_control_plane_and_checkpoint(tmp_path: Path):
    run_id = _seed_run(tmp_path, "run-debug-ctrl-001")

    result = runner.invoke(
        app,
        [
            "debug",
            "capture",
            "Verify evidence drift",
            "--project-root",
            str(tmp_path),
            "--run-id",
            run_id,
            "--intent",
            "verify",
            "--confidence",
            "0.4",
            "--boundary-state",
            "blocked",
            "--block-reason",
            "verify_not_passed",
            "--recommended-command",
            "beacon qa run Control Feature",
            "--note",
            "verification still failing",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout

    exhaustion = json.loads((tmp_path / ".beacon" / "state" / "exhaustion.json").read_text(encoding="utf-8"))
    run_state = exhaustion["runs"][run_id]
    assert run_state["failure_streak"] == 1
    assert run_state["escalation_level"] == "E1"
    assert run_state["required_next_action"] == "switch_strategy"
    assert run_state["latest_checkpoint_ref"]

    checkpoint = json.loads((tmp_path / run_state["latest_checkpoint_ref"]).read_text(encoding="utf-8"))
    latest = checkpoint["checkpoints"][-1]
    assert latest["reason_code"] == "verify_not_passed"
    assert latest["next_hypothesis"]
    assert latest["evidence_gap"]

    recover = runner.invoke(app, ["debug", "recover", run_id, "--project-root", str(tmp_path), "--json"])
    assert recover.exit_code == 0, recover.stdout
    recover_payload = json.loads(recover.stdout)
    assert recover_payload["failure_streak"] == 1
    assert recover_payload["checkpoint_ref"] == run_state["latest_checkpoint_ref"]



def test_v119_resume_should_surface_resume_contract(tmp_path: Path):
    run_id = _seed_run(tmp_path, "run-resume-ctrl-001")
    runner.invoke(
        app,
        [
            "debug",
            "checkpoint",
            "save",
            run_id,
            "--project-root",
            str(tmp_path),
            "--stage",
            "implementation",
            "--attempted-strategy",
            "implementation:native-single",
            "--next-hypothesis",
            "switch implementation strategy and rerun targeted QA",
            "--evidence-gap",
            "missing technical archive verification",
            "--current-blocker",
            "implementation blocked",
        ],
    )
    runner.invoke(
        app,
        [
            "debug",
            "capture",
            "Implementation blocked",
            "--project-root",
            str(tmp_path),
            "--run-id",
            run_id,
            "--intent",
            "implementation",
            "--boundary-state",
            "blocked",
            "--block-reason",
            "implement_execution_failed",
            "--recommended-command",
            "beacon implement run Control Feature --runner native-team",
        ],
    )

    result = runner.invoke(app, ["resume", run_id, "--project-root", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    contract = payload["resume_contract"]
    assert contract["failure_streak"] >= 1
    assert contract["tried_approaches"]
    assert contract["next_hypothesis"]
    assert contract["evidence_gap"]



def test_v119_debug_harvest_should_refresh_learning_outputs(tmp_path: Path):
    _seed_run(tmp_path, "run-harvest-001")
    for idx in range(2):
        runner.invoke(
            app,
            [
                "debug",
                "capture",
                "Need stronger recovery loop",
                "--project-root",
                str(tmp_path),
                "--run-id",
                f"run-harvest-00{idx}",
                "--intent",
                "debug",
                "--boundary-state",
                "blocked",
                "--block-reason",
                "recovery_contract_missing",
                "--recommended-command",
                "beacon debug recover run-harvest-001",
            ],
        )

    harvest = runner.invoke(app, ["debug", "harvest", "--project-root", str(tmp_path), "--json"])
    assert harvest.exit_code == 0, harvest.stdout
    payload = json.loads(harvest.stdout)
    assert payload["issue_count"] >= 1
    assert payload["learning"]["counts"]["debug_issue_inputs"] >= 1

    baseline = json.loads((tmp_path / ".beacon" / "state" / "learning" / "execution-baseline.json").read_text(encoding="utf-8"))
    corpus = json.loads((tmp_path / ".beacon" / "state" / "eval-lab" / "benchmark-corpus.json").read_text(encoding="utf-8"))
    assert baseline["recommendations"]
    assert corpus["counts"]["debug_issue_inputs"] >= 1
