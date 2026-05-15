from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.automation_feedback import refresh_qa_feedback_ledger
from beacon.utils.automation_runtime import (
    bounded_runtime_round_summary,
    load_feature_automation_runtime,
    record_support_review_outcome,
    set_truth_recompile_barrier,
)
from beacon.utils.runtime import write_json


runner = CliRunner()
implement_module = importlib.import_module("beacon.commands.implement")
legacy_implement_cli = implement_module._legacy_cli


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)


def _seed_docs(root: Path, *, version: str = "v1.4.7", feature_slug: str = "feature-support") -> None:
    _init_git_repo(root)
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    version_root = root / "docs" / "beacon" / version
    (version_root / "prd").mkdir(parents=True, exist_ok=True)
    (version_root / "user-story").mkdir(parents=True, exist_ok=True)
    (version_root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (version_root / "execution").mkdir(parents=True, exist_ok=True)
    (version_root / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    (version_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (version_root / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (version_root / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (version_root / "prd" / f"{feature_slug}.md").write_text("# PRD\n", encoding="utf-8")
    (version_root / "user-story" / f"{feature_slug}.md").write_text("# User Story\n", encoding="utf-8")
    (version_root / "qa" / "test-cases" / f"{feature_slug}.md").write_text("# Test Cases\n", encoding="utf-8")


def _seed_feature_status(
    root: Path,
    *,
    feature: str,
    status: str = "blocked",
    continue_decision: str = "route_support_review",
    support_review: dict | None = None,
    scenario_discovery: dict | None = None,
) -> None:
    slug = feature.replace(" ", "-").replace("_", "-").lower()
    support_payload = support_review or {"executor": "deep", "reason": "structural_failure", "repeat_count": 1}
    scenario_payload = scenario_discovery or {"classification": "promotion_candidate", "requirement_meaning_delta": False, "finding_count": 1, "evidence_refs": ["evidence://promo-1"], "requires_truth_reopen": False}
    _write_json(
        root / ".beacon" / "qa" / "features" / slug / "status.json",
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": "v1.4.7",
            "run_id": f"run-{slug}",
            "status": status,
            "evidence_done": status == "passed",
            "release_ready": status == "passed",
            "truth_hash": f"truth-{slug}",
            "implementation_evidence_hash": f"impl-{slug}",
            "feature_scorecard": {
                "continue_decision": continue_decision,
                "stop_reasons": ["needs-structural-review"] if continue_decision == "route_support_review" else ["needs-fix"],
                "resume_command": f'beacon qa run "{feature}" --project-root . --version v1.4.7',
                "support_review": support_payload,
                "scenario_discovery": scenario_payload,
                "coverage_current": {"coverage_rate": 0.5, "executed_scenarios": 1, "required_scenarios": 2},
            },
        },
    )
    _write_json(
        root / ".beacon" / "qa" / "features" / slug / "scorecard.json",
        {
            "continue_decision": continue_decision,
            "stop_reasons": ["needs-structural-review"] if continue_decision == "route_support_review" else ["needs-fix"],
            "support_review": support_payload,
            "scenario_discovery": scenario_payload,
            "coverage_current": {"coverage_rate": 0.5, "executed_scenarios": 1, "required_scenarios": 2},
        },
    )


def _write_acceptance_kit(root: Path, *, feature: str, all_layers_passed: bool = True, real_project_proof: bool = True) -> None:
    slug = feature.replace(" ", "-").replace("_", "-").lower()
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": "v1.4.7",
        "verdict": "passed" if all_layers_passed else "blocked",
        "layers": {
            "skill-contract": {"status": "pass", "source_truth_ref": "prd", "evidence_ref": "prd"},
            "scenario-suite": {"status": "pass", "source_truth_ref": "user-story", "evidence_ref": "user-story"},
            "trace-scorecard": {"status": "pass", "source_truth_ref": "test-case", "evidence_ref": "test-case"},
            "real-project-proof": {"status": "pass" if real_project_proof else "blocked", "source_truth_ref": "runtime", "evidence_ref": "runtime"},
        },
        "real_project_proof": {
            "status": "pass" if real_project_proof else "blocked",
            "evidence_refs": ["runtime://proof-1"] if real_project_proof else [],
            "source": "qa_acceptance_envelope",
        },
        "regression_pass": all_layers_passed,
    }
    write_json(root / "docs" / "beacon" / "v1.4.7" / ".machine" / "execution" / f"acceptance-kit-{slug}.json", payload)


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_qa_can_route_to_support_review_with_executor_metadata(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature support")
    payload = refresh_qa_feedback_ledger(tmp_path, features=["feature support"])
    runtime = payload["entries"][0]["bounded_runtime"]
    assert runtime["next_route"] == "support_review"
    assert runtime["terminal_signal"] == "qa_route_support_review"
    assert runtime["support_review"]["executor"] == "deep"
    assert runtime["support_review"]["required"] is True


def test_support_review_outcome_can_route_back_to_implement_without_truth_delta(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature support")
    refresh_qa_feedback_ledger(tmp_path, features=["feature support"])
    payload = record_support_review_outcome(
        tmp_path,
        feature="feature support",
        outcome="deep_exit_no_truth_delta",
        executor="deep",
        reason="implementation-only-defect",
    )
    assert payload["next_route"] == "implement"
    assert payload["terminal_signal"] == "deep_exit_no_truth_delta"
    assert payload["truth_recompiled_pending"] is False


def test_support_review_outcome_can_route_to_change_refreeze_on_requirement_meaning_delta(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature support")
    refresh_qa_feedback_ledger(tmp_path, features=["feature support"])
    payload = record_support_review_outcome(
        tmp_path,
        feature="feature support",
        outcome="support_review_deep_route_truth_refreeze",
        executor="deep",
        requirement_meaning_delta=True,
        reason="meaning-pressure",
    )
    assert payload["next_route"] == "change_refreeze"
    assert payload["terminal_signal"] == "support_review_deep_route_truth_refreeze"
    assert payload["truth_recompiled_pending"] is True
    assert payload["truth_recompile_gate"]["required"] is True
    assert "freeze" in payload["truth_recompile_gate"]["targets"]


def test_truth_recompile_barrier_is_written_and_can_be_cleared(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature support")
    refresh_qa_feedback_ledger(tmp_path, features=["feature support"])
    pending = set_truth_recompile_barrier(tmp_path, feature="feature support", pending=True)
    assert pending["truth_recompiled_pending"] is True
    assert pending["truth_recompile_gate"]["required"] is True
    cleared = set_truth_recompile_barrier(tmp_path, feature="feature support", pending=False)
    assert cleared["truth_recompiled_pending"] is False
    assert cleared["truth_recompile_gate"]["targets"] == []


def test_implement_preflight_blocks_on_support_review_truth_refreeze_and_truth_recompile_barriers(tmp_path: Path, monkeypatch) -> None:
    _seed_docs(tmp_path)
    monkeypatch.setattr(legacy_implement_cli, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass", "reason_code": "", "recommended_command": ""})
    monkeypatch.setattr(legacy_implement_cli, "_requirement_closure_preflight", lambda *_args, **_kwargs: {"enabled": True, "status": "pass", "blocked": False, "reason_code": ""})
    _seed_feature_status(tmp_path, feature="feature support")
    refresh_qa_feedback_ledger(tmp_path, features=["feature support"])
    blocked_support = _invoke(["implement", "plan", "feature support", "--project-root", str(tmp_path), "--version", "v1.4.7", "--json"])
    assert blocked_support.exit_code == 2
    payload = json.loads(blocked_support.stdout)
    assert payload["reason_code"] == "automation_support_review_required"

    record_support_review_outcome(
        tmp_path,
        feature="feature support",
        outcome="support_review_deep_route_truth_refreeze",
        executor="deep",
        requirement_meaning_delta=True,
    )
    runtime = load_feature_automation_runtime(tmp_path, feature="feature support")
    runtime["truth_recompiled_pending"] = False
    runtime["truth_recompile_gate"] = {"required": False, "targets": []}
    write_json(tmp_path / ".beacon" / "automation" / "features" / "feature-support" / "runtime.json", runtime)
    blocked_refreeze = _invoke(["implement", "plan", "feature support", "--project-root", str(tmp_path), "--version", "v1.4.7", "--json"])
    assert blocked_refreeze.exit_code == 2
    refreeze_payload = json.loads(blocked_refreeze.stdout)
    assert refreeze_payload["reason_code"] == "automation_truth_refreeze_required"

    runtime = load_feature_automation_runtime(tmp_path, feature="feature support")
    runtime["next_route"] = "implement"
    runtime["support_review"] = {}
    write_json(tmp_path / ".beacon" / "automation" / "features" / "feature-support" / "runtime.json", runtime)
    set_truth_recompile_barrier(tmp_path, feature="feature support", pending=True)
    blocked_recompile = _invoke(["implement", "plan", "feature support", "--project-root", str(tmp_path), "--version", "v1.4.7", "--json"])
    assert blocked_recompile.exit_code == 2
    recompile_payload = json.loads(blocked_recompile.stdout)
    assert recompile_payload["reason_code"] == "automation_truth_recompile_pending"


def test_scenario_discovery_is_split_between_closure_supplement_and_promotion_candidate(tmp_path: Path) -> None:
    _seed_feature_status(
        tmp_path,
        feature="feature supplement",
        continue_decision="stop_for_repair",
        scenario_discovery={"classification": "closure_supplement", "requirement_meaning_delta": True, "finding_count": 2, "evidence_refs": ["evidence://closure-1"], "requires_truth_reopen": True},
    )
    supplement = refresh_qa_feedback_ledger(tmp_path, features=["feature supplement"])["entries"][0]["bounded_runtime"]
    assert supplement["scenario_discovery"]["classification"] == "closure_supplement"
    assert supplement["scenario_discovery"]["requires_truth_reopen"] is True
    assert supplement["next_route"] == "change_refreeze"

    _seed_feature_status(
        tmp_path,
        feature="feature promotion",
        continue_decision="ready_for_release",
        status="passed",
        scenario_discovery={"classification": "promotion_candidate", "requirement_meaning_delta": False, "finding_count": 1, "evidence_refs": ["evidence://promo-1"], "requires_truth_reopen": False},
    )
    promotion = refresh_qa_feedback_ledger(tmp_path, features=["feature promotion"])["entries"][0]["bounded_runtime"]
    assert promotion["scenario_discovery"]["classification"] == "promotion_candidate"
    assert promotion["scenario_discovery"]["requires_truth_reopen"] is False


def test_promotion_candidate_does_not_block_release_route_but_is_retained_in_runtime_sink(tmp_path: Path) -> None:
    _seed_feature_status(
        tmp_path,
        feature="feature promotion",
        status="passed",
        continue_decision="ready_for_release",
        scenario_discovery={"classification": "promotion_candidate", "requirement_meaning_delta": False, "finding_count": 1, "evidence_refs": ["evidence://promo-1"], "requires_truth_reopen": False},
    )
    runtime = refresh_qa_feedback_ledger(tmp_path, features=["feature promotion"])["entries"][0]["bounded_runtime"]
    assert runtime["next_route"] == "release"
    assert runtime["scenario_discovery"]["classification"] == "promotion_candidate"
    summary = bounded_runtime_round_summary(runtime)
    assert summary["scenario_discovery_classification"] == "promotion_candidate"


def test_promotion_grade_proof_hooks_reflect_acceptance_and_real_project_evidence(tmp_path: Path) -> None:
    _seed_docs(tmp_path, feature_slug="feature-proof")
    _write_acceptance_kit(tmp_path, feature="feature proof", all_layers_passed=True, real_project_proof=True)
    _seed_feature_status(
        tmp_path,
        feature="feature proof",
        status="passed",
        continue_decision="ready_for_release",
    )
    runtime = refresh_qa_feedback_ledger(tmp_path, features=["feature proof"])["entries"][0]["bounded_runtime"]
    hooks = runtime["promotion_proof_hooks"]
    assert hooks["acceptance_kit_present"] is True
    assert hooks["acceptance_layers_passed"] is True
    assert hooks["real_project_proof_present"] is True
    assert hooks["missing_hooks"] == []


def test_second_slice_preserves_support_plane_boundary(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature support")
    refresh_qa_feedback_ledger(tmp_path, features=["feature support"])
    payload = record_support_review_outcome(
        tmp_path,
        feature="feature support",
        outcome="support_review_deep_route_truth_refreeze",
        executor="deep",
        requirement_meaning_delta=True,
    )
    assert payload["next_route"] == "change_refreeze"
    assert payload["truth_recompiled_pending"] is True
    assert "canonical_truth_write" not in payload
    assert payload["source"]["stage"] == "support_review"
