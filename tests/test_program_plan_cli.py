from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.program_change_intent import append_change_intent_log, require_promotion_diff_before_refreeze
from beacon.utils.program_change_intent import record_promotion_diff_review, rerun_program_freeze_after_structural_refreeze
from beacon.utils.program_graph import (
    capture_feature_graph_structure_baseline,
    feature_graph_structure_changed,
    feature_graph_structure_fingerprint,
    program_dir,
    validate_feature_graph_payload,
)

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]


def test_validate_graph_payload_required_fields():
    errors = validate_feature_graph_payload({})
    assert "missing:program_slug" in errors
    assert "missing:lakes" in errors


def test_plan_start_help_exposes_mode():
    result = runner.invoke(app, ["plan", "start", "--help"])
    assert result.exit_code == 0
    assert "--mode" in result.stdout


def test_program_validate_graph_help():
    result = runner.invoke(app, ["program", "validate-graph", "--help"])
    assert result.exit_code == 0
    assert "validate-graph" in result.stdout


def test_program_guard_sea_help():
    result = runner.invoke(app, ["program", "guard-sea-single-lake", "--help"])
    assert result.exit_code == 0
    assert "guard-sea" in result.stdout


def test_program_freeze_help():
    result = runner.invoke(app, ["program", "freeze", "--help"])
    assert result.exit_code == 0
    assert "program" in result.stdout.lower()


def test_plan_start_json_creates_manifest(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "plan",
            "start",
            "完整复刻 github 项目",
            "--project",
            str(tmp_path),
            "--version",
            "v1.6.1",
            "--mode",
            "auto",
            "--program",
            "demo-program",
            "--json",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["program_slug"] == "demo-program"
    assert payload["plan_mode"] == "auto"
    manifest = tmp_path / "docs/beacon/v1.6.1/programs/demo-program/program-manifest.md"
    assert manifest.exists()


def test_program_validate_graph_blocks_missing_file(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "program",
            "validate-graph",
            "missing-program",
            "--project",
            str(tmp_path),
            "--version",
            "v1.6.1",
            "--json",
        ],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["blocked"] is True


def test_program_guard_sea_blocks_without_ack():
    result = runner.invoke(
        app,
        [
            "program",
            "guard-sea-single-lake",
            "demo",
            "--lake-or-ocean",
            "海",
            "--json",
        ],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["blocked"] is True


def test_change_intent_log_append(tmp_path: Path):
    log_path = append_change_intent_log(
        tmp_path,
        version="v1.6.1",
        program_slug="demo-program",
        utterance="adjust parity matrix",
        affected_slugs=["beacon-harness-program-plan-v161"],
    )
    assert log_path.exists()
    line = log_path.read_text(encoding="utf-8").strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload["utterance"] == "adjust parity matrix"
    assert "beacon-harness-program-plan-v161" in payload["affected_slugs"]


def test_promotion_diff_blocks_refreeze_when_log_exists(tmp_path: Path):
    append_change_intent_log(
        tmp_path,
        version="v1.6.1",
        program_slug="demo-program",
        utterance="change scope",
    )
    gate = require_promotion_diff_before_refreeze(
        tmp_path,
        version="v1.6.1",
        program_slug="demo-program",
    )
    assert gate["blocked"] is True
    assert gate["reason_code"] == "promotion_diff_review_required"


def _write_graph(tmp_path: Path, lakes: list[dict]) -> None:
    program_root = program_dir(tmp_path, "v1.6.1", "demo-program")
    program_root.mkdir(parents=True, exist_ok=True)
    graph = {
        "program_slug": "demo-program",
        "version": "v1.6.1",
        "scope_mode": "full_parity",
        "lakes": lakes,
    }
    (program_root / "feature-graph.json").write_text(json.dumps(graph), encoding="utf-8")


def test_feature_graph_structure_fingerprint_changes_when_lake_added(tmp_path: Path):
    base = [
        {
            "slug": "lake-a",
            "depends_on": [],
            "parity_subset": ["auth"],
            "status": "frozen",
        }
    ]
    extended = base + [
        {
            "slug": "lake-b",
            "depends_on": ["lake-a"],
            "parity_subset": ["billing"],
            "status": "planned",
        }
    ]
    _write_graph(tmp_path, base)
    fp1 = feature_graph_structure_fingerprint(json.loads((program_dir(tmp_path, "v1.6.1", "demo-program") / "feature-graph.json").read_text()))
    capture_feature_graph_structure_baseline(tmp_path, version="v1.6.1", program_slug="demo-program")
    _write_graph(tmp_path, extended)
    fp2 = feature_graph_structure_fingerprint(json.loads((program_dir(tmp_path, "v1.6.1", "demo-program") / "feature-graph.json").read_text()))
    assert fp1 != fp2
    changed = feature_graph_structure_changed(tmp_path, version="v1.6.1", program_slug="demo-program")
    assert changed["changed"] is True


def test_promotion_diff_review_unblocks_refreeze(tmp_path: Path):
    append_change_intent_log(
        tmp_path,
        version="v1.6.1",
        program_slug="demo-program",
        utterance="change scope",
    )
    record_promotion_diff_review(
        tmp_path,
        version="v1.6.1",
        program_slug="demo-program",
        promotion_diff={"summary": "scope narrowed to billing only"},
        reviewed_by="beacon-pln-review",
    )
    gate = require_promotion_diff_before_refreeze(
        tmp_path,
        version="v1.6.1",
        program_slug="demo-program",
    )
    assert gate["blocked"] is False


def test_structural_refreeze_reruns_program_freeze_gate(tmp_path: Path):
    lakes = [
        {
            "slug": "lake-a",
            "depends_on": [],
            "parity_subset": ["auth"],
            "status": "frozen",
        }
    ]
    _write_graph(tmp_path, lakes)
    capture_feature_graph_structure_baseline(tmp_path, version="v1.6.1", program_slug="demo-program")
    lakes.append(
        {
            "slug": "lake-b",
            "depends_on": ["lake-a"],
            "parity_subset": ["billing"],
            "status": "planned",
        }
    )
    _write_graph(tmp_path, lakes)
    result = rerun_program_freeze_after_structural_refreeze(
        tmp_path,
        version="v1.6.1",
        program_slug="demo-program",
    )
    assert result["status"] == "rerun"
    assert result["program_freeze_gate"]["blocked"] is True
    freeze_path = program_dir(tmp_path, "v1.6.1", "demo-program") / "program-truth-freeze.json"
    assert freeze_path.exists()
