from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.cli_factory import build_app
from beacon.utils.qa_evo_deep import FINDING_FAMILIES, run_qa_evo_deep, validate_qa_evo_deep_payload
from beacon.utils.qa_feature import _qa_runtime_taxonomy
from beacon.utils.skill_eval_kit import (
    REQUIRED_CASE_FIELDS,
    SCORING_DIMENSIONS,
    default_route_stability_cases,
    materialize_skill_eval_kit,
    run_skill_eval,
    validate_cases,
)


VERSION = "v1.4.10"
FEATURE = "qa-evo-deep-and-skill-eval-kit-v1410"
SLUG = "qa-evo-deep-and-skill-eval-kit-v1410"


def test_qa_evo_deep_output_contract(tmp_path: Path) -> None:
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["output_path"] == f"docs/beacon/{VERSION}/qa/evo-deep/{SLUG}.md"
    assert payload["machine_path"] == f"docs/beacon/{VERSION}/.machine/qa/evo-deep/{SLUG}.json"
    finding = payload["findings"][0]
    for key in (
        "source_refs",
        "finding_family",
        "risk",
        "affected_ac_ids",
        "route_recommendation",
        "blocked_admissions",
        "release_supplement_input",
    ):
        assert key in finding
    assert "routeable_findings_only" in (tmp_path / payload["output_path"]).read_text(encoding="utf-8")


def test_round_memory_is_advisory_influence(tmp_path: Path) -> None:
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)

    memory = payload["round_memory"][0]
    assert memory["current_run_required"] is True
    assert memory["counts_as_pass_evidence"] is False
    assert payload["round_memory_policy"] == "advisory_influence_only_current_evidence_required"


def test_deep_finding_taxonomy_supported(tmp_path: Path) -> None:
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)

    families = {item["finding_family"] for item in payload["findings"]}
    assert set(FINDING_FAMILIES).issubset(families)
    assert payload["validation"]["status"] == "pass"


def test_qa_evo_deep_write_topology(tmp_path: Path) -> None:
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)

    assert (tmp_path / f"docs/beacon/{VERSION}/qa/evo-deep/{SLUG}.md").exists()
    assert not (tmp_path / f"docs/beacon/{VERSION}/research/{SLUG}.md").exists()
    assert payload["output_policy"] == "routeable_findings_only"


def test_skill_eval_case_schema(tmp_path: Path) -> None:
    payload = materialize_skill_eval_kit(tmp_path)
    cases_payload = json.loads((tmp_path / payload["cases_path"]).read_text(encoding="utf-8"))

    assert payload["status"] == "ready"
    for case in cases_payload["cases"]:
        for field in REQUIRED_CASE_FIELDS:
            assert case.get(field) not in ("", None, [], {})
        assert set(SCORING_DIMENSIONS).issubset(set(case["scoring_dimensions"]))


def test_skill_eval_splits_and_regression_core(tmp_path: Path) -> None:
    payload = materialize_skill_eval_kit(tmp_path)

    assert (tmp_path / payload["optimization_split_path"]).exists()
    assert (tmp_path / payload["holdout_split_path"]).exists()
    regression_core = (tmp_path / payload["regression_core_path"]).read_text(encoding="utf-8").splitlines()
    assert payload["regression_core_count"] >= 1
    assert "route-implement-team" in regression_core


def test_skill_eval_outputs_are_evidence_only(tmp_path: Path) -> None:
    payload = run_skill_eval(tmp_path)

    assert payload["status"] == "pass"
    assert payload["runtime_evidence_only"] is True
    assert payload["requirement_truth"] is False
    assert (tmp_path / payload["metrics_path"]).exists()
    assert ".beacon/state/skill-eval/runs/" in payload["metrics_path"]


def test_route_stability_cases_cover_support_and_implement_modes() -> None:
    cases = default_route_stability_cases()
    validation = validate_cases(cases)

    routes = {case["expected_route"] for case in cases}
    assert validation["status"] == "pass"
    assert "beacon-brainstorm" in routes
    assert "beacon-deep" in routes
    assert "beacon-learn" in routes
    assert "beacon-implement --mode single" in routes
    assert "beacon-implement --mode team" in routes
    assert "beacon-implement --mode ralph" in routes
    assert "beacon-implement-team" not in routes
    assert "beacon-implement-ralph" not in routes


def test_authority_bypass_fails_closed(tmp_path: Path) -> None:
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)
    payload["findings"][0]["authority_boundary"] = "release_verdict"

    validation = validate_qa_evo_deep_payload(payload)

    assert validation["blocked"] is True
    assert validation["issues"][0]["reason_code"] == "qa_evo_deep_authority_bypass"


def test_runtime_taxonomy_ignores_auth_text_in_passing_authority_cases() -> None:
    payload = {
        "qa9": {
            "tc_results": [
                {
                    "status": "passed",
                    "command": "python3 -m pytest -k authority_gate",
                    "stdout": "authority boundary passed",
                    "stderr": "",
                }
            ]
        }
    }

    taxonomy = _qa_runtime_taxonomy(payload)

    assert taxonomy["status"] == "not_applicable"
    assert taxonomy["failure_classes"] == []
    assert taxonomy["primary_class"] == ""


def test_cli_surfaces_materialize_contracts(tmp_path: Path) -> None:
    app = build_app(package_version="0-test")
    runner = CliRunner()

    qa_result = runner.invoke(app, ["qa", "evo-deep", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert qa_result.exit_code == 0, qa_result.output
    qa_payload = json.loads(qa_result.output)
    assert qa_payload["output_path"] == f"docs/beacon/{VERSION}/qa/evo-deep/{SLUG}.md"

    init_result = runner.invoke(app, ["skill", "eval-kit", "init", "--project", str(tmp_path), "--json"])
    assert init_result.exit_code == 0, init_result.output
    init_payload = json.loads(init_result.output)
    assert init_payload["status"] == "ready"

    run_result = runner.invoke(app, ["skill", "eval-kit", "run", "--project", str(tmp_path), "--json"])
    assert run_result.exit_code == 0, run_result.output
    run_payload = json.loads(run_result.output)
    assert run_payload["runtime_evidence_only"] is True
