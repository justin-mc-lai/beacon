from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.learning_loop import refresh_learning_loop


VERSION = "v1.1.9"
runner = CliRunner()



def _write_rewrite_input(root: Path, *, feature_slug: str, candidates: list[str], with_verification: bool = True) -> None:
    path = root / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"requirement-rewrite-input-{feature_slug}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "feature": feature_slug,
        "feature_slug": feature_slug,
        "version": VERSION,
        "generated_at": "2026-03-28T00:00:00+00:00",
        "technical_archive_path": f"docs/beacon/{VERSION}/.machine/execution/technical-implementation-{feature_slug}.json",
        "run_id": f"run-{feature_slug}",
        "modules_touched": ["beacon/commands"],
        "changed_files": [f"beacon/commands/{feature_slug}.py"],
        "known_risks": [],
        "rollback_notes": [],
        "artifact_update_obligations": [],
        "verification_commands": ["pytest -q tests/test_demo.py"] if with_verification else [],
        "rewrite_targets": {
            "prd": [],
            "test_case": [],
            "version_research": [],
        },
        "baseline_uplift_candidates": candidates,
        "benchmark_refs": [f"docs/beacon/{VERSION}/.machine/execution/technical-implementation-{feature_slug}.json"],
        "path": f"docs/beacon/{VERSION}/.machine/execution/requirement-rewrite-input-{feature_slug}.json",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def _write_debug_issue(root: Path, *, reason_code: str, count: int) -> None:
    issues_dir = root / ".beacon" / "debug" / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "issue_id": f"beacon-core--{reason_code}",
        "feedback_target": "beacon-core",
        "reason_code": reason_code,
        "count": count,
        "latest_event_at": "2026-03-28T00:00:00+00:00",
        "sample": "sample friction",
        "run_ids": ["run-a", "run-b"],
    }
    (issues_dir / f"beacon-core--{reason_code}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def test_v119_keep_discard_engine_should_score_real_candidates_and_filter_baseline(tmp_path: Path):
    repeated = "When api_changes.none=false, require endpoint diff + verification evidence."
    weak = "One-off optional docs tidy-up suggestion."
    _write_rewrite_input(tmp_path, feature_slug="feature-a", candidates=[repeated, weak])
    _write_rewrite_input(tmp_path, feature_slug="feature-b", candidates=[repeated])
    _write_rewrite_input(tmp_path, feature_slug="feature-c", candidates=[repeated])
    _write_debug_issue(tmp_path, reason_code="verify_not_passed", count=5)

    payload = refresh_learning_loop(tmp_path)

    assert payload["counts"]["keep_decisions"] >= 1
    assert payload["counts"]["discard_decisions"] >= 1

    scorecard = json.loads((tmp_path / ".beacon" / "state" / "evo" / "scorecards" / "latest.json").read_text(encoding="utf-8"))
    ledger = json.loads((tmp_path / ".beacon" / "state" / "evo" / "ledgers" / "latest.json").read_text(encoding="utf-8"))
    engine = json.loads((tmp_path / ".beacon" / "state" / "evo" / "decision-engine.json").read_text(encoding="utf-8"))
    baseline = json.loads((tmp_path / ".beacon" / "state" / "learning" / "execution-baseline.json").read_text(encoding="utf-8"))

    repeated_row = next(item for item in scorecard["candidates"] if item["text"] == repeated)
    weak_row = next(item for item in scorecard["candidates"] if item["text"] == weak)

    assert repeated_row["decision"] == "keep"
    assert weak_row["decision"] == "discard"
    assert any(repeated in item for item in baseline["recommendations"])
    assert not any(weak in item for item in baseline["recommendations"])
    assert engine["decision_summary"]["keep"] >= 1
    assert len(ledger["decisions"]) == len(scorecard["candidates"])



def test_v119_keep_discard_engine_should_append_machine_decision_logs(tmp_path: Path):
    repeated = "artifact_updates.required items must become explicit follow-up obligations before closure."
    _write_rewrite_input(tmp_path, feature_slug="feature-a", candidates=[repeated], with_verification=False)
    _write_rewrite_input(tmp_path, feature_slug="feature-b", candidates=[repeated], with_verification=False)
    _write_rewrite_input(tmp_path, feature_slug="feature-c", candidates=[repeated], with_verification=False)

    refresh_learning_loop(tmp_path)

    eval_log = tmp_path / ".beacon" / "state" / "eval-lab" / "keep-discard-log.jsonl"
    evo_log = tmp_path / ".beacon" / "state" / "evo" / "ledger.jsonl"
    assert eval_log.exists()
    assert evo_log.exists()

    eval_lines = [json.loads(line) for line in eval_log.read_text(encoding="utf-8").splitlines() if line.strip()]
    evo_lines = [json.loads(line) for line in evo_log.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any(line.get("source") == "auto-keep-discard-engine" for line in eval_lines)
    assert any(line.get("recommendation") in {"keep", "review", "discard"} for line in evo_lines)


def test_v119_evo_experiment_runner_should_apply_budget_score_delta_and_generate_docs(tmp_path: Path):
    weak_debug = "verify_not_passed"
    _write_debug_issue(tmp_path, reason_code=weak_debug, count=1)
    first = runner.invoke(
        app,
        [
            "version",
            "experiment",
            "Beacon v1.1.9 evo harness",
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--max-iterations",
            "2",
            "--max-command-count",
            "4",
            "--max-evidence-budget",
            "3",
            "--json",
        ],
    )
    assert first.exit_code == 0, first.stdout
    first_payload = json.loads(first.stdout)
    assert len(first_payload["selected_candidates"]) <= 2
    assert first_payload["command_count"] <= 4
    assert len(first_payload["selected_benchmark_refs"]) <= 3
    assert first_payload["main_kpi"] == "false_complete_rate"

    _write_debug_issue(tmp_path, reason_code=weak_debug, count=5)
    _write_rewrite_input(
        tmp_path,
        feature_slug="feature-a",
        candidates=["When api_changes.none=false, require endpoint diff + verification evidence."],
    )
    _write_rewrite_input(
        tmp_path,
        feature_slug="feature-b",
        candidates=["When api_changes.none=false, require endpoint diff + verification evidence."],
    )

    second = runner.invoke(
        app,
        [
            "version",
            "experiment",
            "Beacon v1.1.9 evo harness",
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--max-iterations",
            "3",
            "--json",
        ],
    )
    assert second.exit_code == 0, second.stdout
    second_payload = json.loads(second.stdout)
    assert second_payload["score_delta"]["main_kpi_score"] is not None
    assert second_payload["score_delta"]["false_complete_rate"] is not None

    harness_doc = tmp_path / "docs" / "beacon" / VERSION / "execution" / "evo-harness-contract.md"
    scorecard_doc = tmp_path / "docs" / "beacon" / VERSION / "execution" / "evo-scorecard-contract.md"
    index_doc = tmp_path / "docs" / "beacon" / VERSION / "execution" / "index.md"
    assert harness_doc.exists()
    assert scorecard_doc.exists()
    assert "false_complete_rate" in scorecard_doc.read_text(encoding="utf-8")
    assert "max_iterations" in harness_doc.read_text(encoding="utf-8")
    assert "./evo-harness-contract.md" in index_doc.read_text(encoding="utf-8")
