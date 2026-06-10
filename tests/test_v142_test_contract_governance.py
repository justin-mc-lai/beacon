from __future__ import annotations

import importlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils import qa_feature
from beacon.commands.auto_test import _browser_evidence_authenticity, resolve_browser_runtime_admission
from beacon.commands.auto_test import _write_browser_runner_learning_note
from beacon.commands.qa import _default_feature_qa_ui_runner
from beacon.utils.browser_task_compiler import build_browser_task, default_browser_runner_command
from beacon.utils.story_scenarios import expand_story_scenarios
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.qa_feature import _build_story_scenario_map, _closure_outcome, _evidence_sufficiency, _resolve_entry_command
from beacon.utils.qa9 import default_command_for_qa_type
from beacon.utils.test_contract_governance import (
    CANONICAL_TEST_CONTRACT_LANES,
    QA_FIRST_PRINCIPLES_ORDER,
    TEST_CONTRACT_REASON_CODES,
    build_test_contract_gate_payload,
    build_test_contract_index,
    load_test_contract_index,
    test_contract_index_path as contract_index_path,
)

runner = CliRunner()
gate_module = importlib.import_module("beacon.commands.gate")
VERSION = "v1.4.2"
FEATURE = "beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance"
SLUG = FEATURE


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_project(tmp_path: Path, *, include_evidence: bool = True) -> None:
    _write_json(
        tmp_path / "beacon" / "version-truth.json",
        {
            "schema_version": "1.0",
            "runtime_version": "v1.4.0",
            "package_version": "1.4.0",
            "docs_default_line": "v1.4.0",
            "current_runtime_release_line": "v1.4.0",
            "planning_lines": [VERSION],
            "partial_runtime_supplement_lines": [],
            "lines": {
                "v1.4.0": {"status": "current_runtime_release"},
                VERSION: {"status": "planning_only"},
            },
        },
    )
    (tmp_path / "beacon" / "__init__.py").write_text(
        '__version__ = "1.4.0"\n__toolkit_version__ = "v1.4.0"\n',
        encoding="utf-8",
    )
    version_root = tmp_path / "docs" / "beacon" / VERSION
    for rel in [
        f"prd/{SLUG}.md",
        f"user-story/{SLUG}.md",
        f"qa/test-cases/{SLUG}.md",
    ]:
        path = version_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {rel}\n", encoding="utf-8")
    _write_json(
        version_root / ".machine" / "user-story" / f"{SLUG}.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "current_revision_id": "R1",
            "stories": [
                {
                    "story_id": "US-001",
                    "items": [
                        {"id": "AC-001", "kind": "ac", "theme": "index-contract", "text": "Index contract"},
                        {"id": "AC-002", "kind": "ac", "theme": "lane-taxonomy", "text": "Canonical lanes"},
                        {"id": "AC-003", "kind": "ac", "theme": "release-facing-mapping", "text": "Release mapping"},
                        {"id": "AC-004", "kind": "ac", "theme": "doctor-ownership", "text": "Doctor ownership"},
                        {"id": "AC-005", "kind": "ac", "theme": "qa-order", "text": "QA order"},
                        {"id": "AC-006", "kind": "ac", "theme": "release-gating", "text": "Release gating"},
                        {"id": "AC-007", "kind": "ac", "theme": "generated-surface-sync", "text": "Generated surface"},
                        {"id": "AC-008", "kind": "ac", "theme": "legacy-classification", "text": "Legacy snapshot"},
                        {"id": "AC-009", "kind": "ac", "theme": "skill-delivery", "text": "Skill delivery"},
                        {"id": "AC-010", "kind": "ac", "theme": "deep-delta-adoption", "text": "Deep delta"},
                        {"id": "AC-011", "kind": "ac", "theme": "planning-line-safety", "text": "Planning line"},
                        {"id": "AC-012", "kind": "ac", "theme": "recovery-routing", "text": "Recovery routing"},
                        {"id": "AC-013", "kind": "ac", "theme": "browser-admission", "text": "Protected browser admission"},
                        {"id": "AC-014", "kind": "ac", "theme": "browser-evidence-authenticity", "text": "Browser evidence authenticity"},
                        {"id": "AC-015", "kind": "ac", "theme": "browser-runner-priority", "text": "Browser runner priority"},
                        {"id": "AC-016", "kind": "ac", "theme": "blocked-not-false-fail", "text": "Blocked not false fail"},
                        {"id": "AC-017", "kind": "ac", "theme": "runner-learning", "text": "Runner learning"},
                        {"id": "AC-018", "kind": "ac", "theme": "browser-lane-traceability", "text": "Browser lane traceability"},
                    ],
                }
            ],
        },
    )
    entries = [
        ("TC-US001-001", "AC-001", "contract", "tests/test_v142_test_contract_index.py", "index shape"),
        ("TC-US002-001", "AC-002", "contract", "tests/test_v142_test_contract_lanes.py", "canonical lanes"),
        ("TC-US003-001", "AC-003", "regression", "tests/test_v142_test_contract_index.py", "release-facing mapping"),
        ("TC-US004-001", "AC-004", "integration", "tests/test_v142_doctor_test_contract_governance.py", "doctor build and verify"),
        ("TC-US005-001", "AC-005", "contract", "tests/test_v142_qa_lane_order.py", "qa first principles order"),
        ("TC-US006-001", "AC-006", "integration", "tests/test_v142_release_test_contract_governance.py", "release consumes lane status"),
        ("TC-US007-001", "AC-007", "regression", "tests/test_v142_generated_surface_lane.py", "generated surface sync drift"),
        ("TC-US008-001", "AC-008", "regression", "tests/test_v142_legacy_snapshot_classification.py", "legacy snapshot not release blocker"),
        ("TC-US009-001", "AC-009", "contract", "tests/test_v142_skill_delivery_guidance.py", "skill delivery guidance"),
        ("TC-US010-001", "AC-010", "regression", "tests/test_v142_deep_delta_adoption.py", "deep delta routes to test-case or QA"),
        ("TC-US011-001", "AC-011", "regression", "tests/test_v142_planning_line_safety.py", "planning line safety"),
        ("TC-US012-001", "AC-012", "integration", "tests/test_v142_test_contract_recovery.py", "blocked governance has repair route"),
        ("TC-US013-001", "AC-013", "integration", "tests/test_v142_browser_runtime_admission.py", "protected surface requires session admission"),
        ("TC-US014-001", "AC-014", "regression", "tests/test_v142_browser_evidence_authenticity.py", "placeholder transcript is not browser closure"),
        ("TC-US015-001", "AC-015", "contract", "tests/test_v142_browser_runner_priority.py", "protected surface runner priority"),
        ("TC-US016-001", "AC-016", "integration", "tests/test_v142_browser_runtime_admission.py", "missing session bridge yields blocked or skip"),
        ("TC-US017-001", "AC-017", "contract", "tests/test_v142_browser_runner_learning.py", "runner learning note contract"),
        ("TC-US018-001", "AC-018", "integration", "tests/test_v142_browser_lane_traceability.py", "browser admission and evidence participate in lane reasoning"),
    ]
    matrix_entries = []
    for tc_id, ac_id, layer, command, assertion in entries:
        evidence_path = f".beacon/evidence/test-results/{SLUG}/{tc_id}.json"
        matrix_entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac_id,
                "layer": layer,
                "command": f"python3 -m pytest -q {command}",
                "assertion": assertion,
                "evidence_path": evidence_path,
                "status": "pending",
                "source": f"qa:test-cases:docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
            }
        )
        if include_evidence:
            _write_json(tmp_path / evidence_path, {"status": "passed", "tc_id": tc_id})
    _write_json(
        version_root / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "entries": matrix_entries,
        },
    )
    _write_json(
        version_root / ".machine" / "execution" / f"{SLUG}.revision.json",
        {"schema_version": "1.0", "feature": FEATURE, "feature_slug": SLUG, "version": VERSION, "revision_id": "R1"},
    )


def test_index_shape_and_canonical_lanes_from_frozen_truth(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)

    assert payload["status"] == "pass"
    assert payload["feature"] == FEATURE
    assert payload["docs_line"] == VERSION
    assert payload["runtime_line"] == VERSION
    assert payload["canonical_lanes"] == list(CANONICAL_TEST_CONTRACT_LANES)
    assert set(payload["lanes"]) == set(CANONICAL_TEST_CONTRACT_LANES)
    assert len(payload["test_refs"]) == 18
    assert payload["truth_refs"]["prd"] == f"docs/beacon/{VERSION}/prd/{SLUG}.md"
    assert payload["ac_to_test_refs"]["AC-001"] == ["TC-US001-001"]
    assert payload["ac_to_test_refs"]["AC-018"] == ["TC-US018-001"]
    assert contract_index_path(tmp_path, VERSION).exists()


def test_release_facing_mapping_required_and_unclassified_fail_closed(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["entries"][0]["evidence_path"] = ""
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    gate = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["blocked"] is True
    assert "ac_test_mapping_missing" in payload["reason_codes"]
    assert gate["blocked"] is True
    assert "ac_test_mapping_missing" in gate["reason_codes"]


def test_doctor_build_and_verify_commands(tmp_path: Path) -> None:
    _seed_project(tmp_path)

    build = runner.invoke(app, ["doctor", "build-test-contract-index", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert build.exit_code == 0, build.stdout
    build_payload = json.loads(build.stdout)
    assert build_payload["action"] == "build-test-contract-index"
    assert build_payload["result"]["status"] == "pass"

    verify = runner.invoke(app, ["doctor", "verify-test-contract-index", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--strict", "--json"])
    assert verify.exit_code == 0, verify.stdout
    verify_payload = json.loads(verify.stdout)
    assert verify_payload["action"] == "verify-test-contract-index"
    assert verify_payload["result"]["gate"]["status"] == "pass"


def test_gate_rebuilds_in_memory_when_global_index_belongs_to_other_feature(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    index_path = contract_index_path(tmp_path, VERSION)
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    payload["feature"] = "other-feature"
    payload["feature_slug"] = "other-feature"
    payload["source_hashes"] = {"truth": "sha256:other"}
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    gate = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert gate["blocked"] is False
    assert gate["release_gate"]["blocked"] is False
    assert "test_contract_index_stale" not in gate["release_gate"]["reason_codes"]


def test_verify_missing_index_has_repair_route(tmp_path: Path) -> None:
    _seed_project(tmp_path)

    gate = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert gate["blocked"] is True
    assert gate["reason_codes"] == ["test_contract_index_missing"]
    assert "build-test-contract-index" in gate["repair_commands"][0]


def test_release_consumes_lane_status_and_reason_codes(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(scorecard)

    assert scorecard["test_contract_governance"]["release_gate"]["blocked"] is True
    assert "test_contract_index_missing" in scorecard["host_native_delivery"]["reason_codes"]
    assert summary["test_contract_release_blocked"] is True
    assert "test_contract_index_missing" in summary["test_contract_release_reason_codes"]


def test_release_passes_test_contract_gate_after_index_build(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(scorecard)

    assert scorecard["test_contract_governance"]["release_gate"]["status"] == "pass"
    assert summary["test_contract_release_blocked"] is False


def test_canonical_qa_matrix_evidence_should_satisfy_release_lane_when_feature_qa_matrix_is_missing(tmp_path: Path) -> None:
    _seed_project(tmp_path, include_evidence=False)
    canonical_matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json"
    result_dir = tmp_path / ".beacon" / "evidence" / "auto-test" / "run-20260514T144852438487" / "qa9-tc" / "TC-US003-001"
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / "command.txt").write_text("pytest ...\n", encoding="utf-8")
    _write_json(result_dir / "result.json", {"status": "passed", "tc_id": "TC-US003-001"})
    _write_json(
        canonical_matrix_path,
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "entries": [
                {
                    "tc_id": "TC-US003-001",
                    "last_run_id": "run-20260514T144852438487",
                    "last_evidence_ref": ".beacon/evidence/auto-test/run-20260514T144852438487/qa9-tc/TC-US003-001/command.txt",
                    "evidence_path": ".beacon/evidence/test-results/"
                    + f"{SLUG}"
                    + "/{run_id}/TC-US003-001.json",
                    "status": "passed",
                }
            ],
        },
    )
    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["entries"] = [
        entry for entry in matrix["entries"] if str(entry.get("tc_id")) == "TC-US003-001"
    ]
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    gate = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    feature_lane = payload["lanes"]["feature_release_facing"]
    assert len(feature_lane) == 1
    assert feature_lane[0]["tc_id"] == "TC-US003-001"
    assert feature_lane[0]["evidence_status"] == "passed"
    assert "feature_release_lane_missing" not in gate["release_gate"]["reason_codes"]


def test_current_qa9_status_should_satisfy_release_lane_evidence(tmp_path: Path) -> None:
    _seed_project(tmp_path, include_evidence=False)
    _write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "passed",
            "run_id": "run-qa9-current",
            "qa9": {
                "tc_results": [
                    {
                        "tc_id": "TC-US003-001-PRIMARY",
                        "source_tc_id": "TC-US003-001",
                        "ac_id": "AC-003",
                        "status": "passed",
                    }
                ]
            },
        },
    )
    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["entries"] = [
        entry for entry in matrix["entries"] if str(entry.get("tc_id")) == "TC-US003-001"
    ]
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    gate = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    feature_lane = payload["lanes"]["feature_release_facing"]
    assert len(feature_lane) == 1
    assert feature_lane[0]["tc_id"] == "TC-US003-001"
    assert feature_lane[0]["evidence_status"] == "passed"
    assert "feature_release_lane_failed" not in gate["release_gate"]["reason_codes"]


def test_requirement_deepening_coverage_entries_do_not_block_current_runtime_release(tmp_path: Path) -> None:
    version = "v1.4.6"
    feature = "beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces"
    slug = feature
    _write_json(
        tmp_path / "beacon" / "version-truth.json",
        {
            "schema_version": "1.0",
            "runtime_version": version,
            "package_version": "1.4.6",
            "docs_default_line": version,
            "current_runtime_release_line": version,
            "planning_lines": [],
            "partial_runtime_supplement_lines": [],
            "lines": {
                version: {"status": "current_runtime_release"},
            },
        },
    )
    (tmp_path / "beacon" / "__init__.py").write_text(
        '__version__ = "1.4.6"\n__toolkit_version__ = "v1.4.6"\n',
        encoding="utf-8",
    )
    version_root = tmp_path / "docs" / "beacon" / version
    for rel in [
        f"prd/{slug}.md",
        f"user-story/{slug}.md",
        f"qa/test-cases/{slug}.md",
    ]:
        path = version_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {rel}\n", encoding="utf-8")
    _write_json(
        version_root / ".machine" / "user-story" / f"{slug}.json",
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": version,
            "current_revision_id": "R1",
            "stories": [
                {
                    "story_id": "US-001",
                    "items": [
                        {"id": "AC-001", "kind": "ac", "theme": "index-contract", "text": "Index contract"},
                    ],
                }
            ],
        },
    )
    _write_json(
        version_root / ".machine" / "qa" / f"{slug}.ac-test-matrix.json",
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": version,
            "entries": [
                {
                    "tc_id": "TC-ADRIFT46-001",
                    "ac_id": "AC-001",
                    "layer": "contract",
                    "command": "python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k contract",
                    "assertion": "key host-visible skills freeze contract",
                    "evidence_path": f".beacon/evidence/test-results/{slug}/TC-ADRIFT46-001.json",
                    "status": "pending",
                    "source": f"qa:test-cases:docs/beacon/{version}/qa/test-cases/{slug}.md",
                },
                {
                    "tc_id": "TC-011",
                    "ac_id": "AC-001",
                    "layer": "unit",
                    "command": "python3 -m pytest -q -k unit",
                    "assertion": "coverage family happy remains executable",
                    "evidence_path": f".beacon/evidence/test-results/{slug}/TC-011.json",
                    "status": "pending",
                    "source": "requirement-deepening:coverage-family",
                    "coverage_family": "happy",
                },
            ],
        },
    )
    _write_json(
        tmp_path / ".beacon" / "evidence" / "test-results" / slug / "TC-ADRIFT46-001.json",
        {"status": "passed", "tc_id": "TC-ADRIFT46-001"},
    )

    payload = build_test_contract_index(tmp_path, version=version, feature=feature, write=True)
    gate = build_test_contract_gate_payload(tmp_path, version=version, feature=feature)

    coverage_entry = next(item for item in payload["test_refs"] if item["tc_id"] == "TC-011")
    assert coverage_entry["release_blocking"] is False
    assert gate["release_gate"]["blocked"] is False
    assert "feature_release_lane_missing" not in gate["release_gate"]["reason_codes"]


def test_research_projection_entries_do_not_block_release_until_adopted_into_test_case(tmp_path: Path) -> None:
    _seed_project(tmp_path, include_evidence=False)
    story_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json"
    story_payload = json.loads(story_path.read_text(encoding="utf-8"))
    for story in story_payload["stories"]:
        story["items"] = [
            item
            for item in story["items"]
            if str(item.get("id") or "") in {"AC-001", "AC-002", "AC-003"}
        ]
    story_path.write_text(json.dumps(story_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["entries"] = [
        {
            "tc_id": "TC-US003-001",
            "ac_id": "AC-003",
            "layer": "regression",
            "command": "python3 -m pytest -q tests/test_v142_test_contract_index.py",
            "assertion": "adopted release-facing mapping stays executable",
            "evidence_path": f".beacon/evidence/test-results/{SLUG}/TC-US003-001.json",
            "status": "pending",
            "source": f"qa:test-cases:docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        },
        {
            "tc_id": "TC-RESEARCH-001",
            "ac_id": "AC-003",
            "layer": "unit",
            "command": "python3 -m pytest -q -k unit",
            "assertion": "research projection remains visible but advisory",
            "evidence_path": f".beacon/evidence/test-results/{SLUG}/TC-RESEARCH-001.json",
            "status": "pending",
            "source": f"research:docs/beacon/{VERSION}/research/{SLUG}.md",
        },
    ]
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_json(
        tmp_path / ".beacon" / "evidence" / "test-results" / SLUG / "TC-US003-001.json",
        {"status": "passed", "tc_id": "TC-US003-001"},
    )

    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    gate = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    research_entry = next(item for item in payload["test_refs"] if item["tc_id"] == "TC-RESEARCH-001")
    assert research_entry["evidence_status"] == "missing"
    assert research_entry["release_blocking"] is False
    assert gate["release_gate"]["blocked"] is False
    assert "feature_release_lane_missing" not in gate["release_gate"]["reason_codes"]


def test_feature_qa_placeholder_evidence_paths_resolve_to_feature_qa_artifacts(tmp_path: Path) -> None:
    _seed_project(tmp_path, include_evidence=False)
    feature_matrix_path = tmp_path / ".beacon" / "qa" / "features" / SLUG / "matrix.qa9.json"
    feature_matrix_path.parent.mkdir(parents=True, exist_ok=True)
    feature_matrix_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "tc_id": "TC-US003-001",
                        "evidence_path": f".beacon/evidence/qa-feature/{SLUG}/tc-us003-001/__RUN_ID__.json",
                        "last_run_id": "run-qa-001",
                        "last_evidence_ref": ".beacon/evidence/auto-test/run-qa-001/qa9-tc/TC-US003-001/command.txt",
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    qa_evidence_path = tmp_path / ".beacon" / "evidence" / "qa-feature" / SLUG / "tc-us003-001" / "run-qa-001.json"
    _write_json(qa_evidence_path, {"status": "passed", "tc_id": "TC-US003-001"})

    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    release_lane = payload["lanes"]["feature_release_facing"]
    tc_entry = next(item for item in release_lane if item["tc_id"] == "TC-US003-001")

    assert tc_entry["evidence_status"] == "passed"


def test_release_surfaces_browser_blockers_in_host_native_delivery(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    _write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "blocked",
            "evidence_done": False,
            "qa9": {
                "tc_results": [
                    {
                        "tc_id": "TC-US013-001",
                        "reason_code": "protected_surface_session_bridge_missing",
                    }
                ]
            },
        },
    )
    _write_json(
        tmp_path / ".beacon" / "qa" / "features" / SLUG / "scorecard.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "stop_reasons": [
                "browser_evidence_placeholder_only",
                "protected_surface_runner_priority_unavailable",
            ],
            "continue_decision": "stop_for_repair",
            "release_ready": False,
            "unresolved_closure_outcomes": ["needs_more_evidence"],
        },
    )

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(scorecard)

    assert scorecard["browser_release_reason_codes"] == [
        "browser_evidence_placeholder_only",
        "protected_surface_runner_priority_unavailable",
        "protected_surface_session_bridge_missing",
    ]
    assert "browser_evidence_placeholder_only" in scorecard["host_native_delivery"]["reason_codes"]
    assert "protected_surface_session_bridge_missing" in summary["browser_release_reason_codes"]


def test_qa_order_and_deep_delta_policy_are_indexed(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)

    assert payload["qa_order_contract"]["sequence"] == list(QA_FIRST_PRINCIPLES_ORDER)
    assert payload["deep_delta_policy"] == {
        "owner": "deep",
        "adoption_route": "test-case_or_supplemental_qa",
        "executes_qa": False,
    }


def test_legacy_snapshot_not_release_blocker_by_default(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    legacy_entries = payload["lanes"]["legacy_snapshot"]

    assert legacy_entries
    assert all(item["release_blocking"] is False for item in legacy_entries)


def test_browser_runtime_admission_lane_is_classified_and_release_blocking(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    browser_lane = payload["lanes"]["browser_runtime_admission"]

    assert len(browser_lane) == 6
    assert all(item["release_blocking"] is True for item in browser_lane)
    assert {item["ac_id"] for item in browser_lane} == {"AC-013", "AC-014", "AC-015", "AC-016", "AC-017", "AC-018"}


def test_browser_runtime_admission_lane_accepts_legacy_tc_evidence_names(tmp_path: Path) -> None:
    _seed_project(tmp_path, include_evidence=False)
    evidence_root = tmp_path / ".beacon" / "evidence" / "test-results" / SLUG
    for index in range(13, 19):
        _write_json(evidence_root / f"TC-{index:03d}.json", {"status": "passed", "tc_id": f"TC-{index:03d}"})

    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    browser_lane = payload["lanes"]["browser_runtime_admission"]

    assert len(browser_lane) == 6
    assert all(item["evidence_status"] == "passed" for item in browser_lane)


def test_gate_precision_contract_surfaces_browser_release_blockers(tmp_path: Path, monkeypatch) -> None:
    version = "v1.4.2"
    monkeypatch.setattr(gate_module, "_resolved_gate_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "qa": {
                "feature": FEATURE,
                "project_profile_gate_status": "pass",
            },
            "acceptance": {
                "source": "feature_qa_scorecard",
                "feature": FEATURE,
                "release_ready": False,
                "continue_decision": "stop_for_repair",
                "project_profile_gate_status": "pass",
                "unresolved_closure_outcomes": ["needs_more_evidence"],
                "review_required_count": 0,
                "needs_replay_count": 0,
                "release_confidence_min": 0.4,
            },
            "browser_release_reason_codes": [
                "protected_surface_session_bridge_missing",
                "browser_evidence_placeholder_only",
            ],
            "host_native_delivery": {
                "reason_codes": [
                    "protected_surface_session_bridge_missing",
                    "browser_evidence_placeholder_only",
                ]
            },
        },
    )

    issues = gate_module.check_v110_precision_contract(
        tmp_path,
        gate_module.GateMode.STRICT,
        "release",
        version,
    )

    reason_codes = {item["reason_code"] for item in issues}
    assert "protected_surface_session_bridge_missing" in reason_codes


def test_generated_surface_sync_lane_blocks_failed_evidence(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    generated_evidence = tmp_path / ".beacon" / "evidence" / "test-results" / SLUG / "TC-US007-001.json"
    _write_json(generated_evidence, {"status": "failed"})
    build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)

    gate = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert gate["release_gate"]["blocked"] is True
    assert "generated_surface_sync_drift" in gate["release_gate"]["reason_codes"]


def test_planning_line_safety_keeps_v142_out_of_runtime(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    payload = build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)

    assert payload["planning_line_safety"]["status"] == "pass"
    assert payload["planning_line_safety"]["runtime_line"] == "v1.4.0"
    assert payload["planning_line_safety"]["docs_default_line"] == "v1.4.0"
    assert payload["planning_line_safety"]["current_runtime_release_line"] == "v1.4.0"
    assert payload["planning_line_safety"]["feature_line_status"] == "planning_only"


def test_skill_guidance_mentions_contract_lanes_and_unclassified_full_suite() -> None:
    usage = Path("skills/beacon/references/usage-rules.md").read_text(encoding="utf-8")
    skill = Path("skills/beacon/SKILL.md").read_text(encoding="utf-8")

    combined = usage + "\n" + skill
    assert "contract-lane" in combined
    assert "feature_release_facing" in combined
    assert "generated_surface_sync" in combined
    assert "legacy_snapshot" in combined
    assert "unclassified full-suite" in combined


def test_browser_runtime_admission_requires_session_for_protected_surface() -> None:
    item = {"target_url": "https://demo-preview.vercel.app/dashboard", "exploratory_runner": "browser-use"}
    payload = resolve_browser_runtime_admission(item=item, active_browser_session={})

    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "protected_surface_session_bridge_missing"
    assert payload["protected_surface"] is True


def test_browser_runtime_admission_prefers_attached_session_runner() -> None:
    item = {"target_url": "https://demo-preview.vercel.app/dashboard", "exploratory_runner": "browser-use"}
    session = {
        "session_id": "qa-live",
        "runner_type": "web-access",
        "origin": "https://demo-preview.vercel.app",
        "storage_state_ref": ".beacon/qa/sessions/qa-live/storage-state.json",
    }
    payload = resolve_browser_runtime_admission(item=item, active_browser_session=session)

    assert payload["status"] == "ready"
    assert payload["preferred_runner"] == "web-access"
    assert payload["attached_runner_available"] is True


def test_browser_evidence_authenticity_marks_placeholder_runner_statuses() -> None:
    payload = _browser_evidence_authenticity(
        explore_bundle={"status": "fallback-executed"},
        replay_bundle={},
        admission={"status": "ready"},
    )

    assert payload["authentic"] is False
    assert payload["reason_code"] == "browser_evidence_placeholder_only"


def test_browser_evidence_authenticity_accepts_real_fallback_execution() -> None:
    payload = _browser_evidence_authenticity(
        explore_bundle={
            "status": "fallback-browser-use-unavailable",
            "report_ref": ".beacon/evidence/auto-test/run-x/tc/explore/browser-runner-report.json",
            "result_ref": ".beacon/evidence/auto-test/run-x/tc/explore/browser-runner-result.json",
            "task_ref": ".beacon/evidence/auto-test/run-x/tc/explore/browser-runner-task.json",
        },
        replay_bundle={},
        admission={"status": "ready"},
    )

    assert payload["authentic"] is True
    assert payload["reason_code"] == ""
    assert payload["real_fallback_execution"] is True


def test_feature_qa_default_ui_runner_prefers_agent_browser_for_attached_session(tmp_path: Path) -> None:
    session_root = tmp_path / ".beacon" / "qa" / "sessions" / "attached-demo"
    session_root.mkdir(parents=True, exist_ok=True)
    _write_json(
        tmp_path / ".beacon" / "qa" / "current-session.json",
        {"schema_version": "1.0", "session_id": "attached-demo"},
    )
    _write_json(
        session_root / "manifest.json",
        {
            "schema_version": "1.0",
            "session_id": "attached-demo",
            "runner_type": "web-access",
            "origin": "https://demo-preview.vercel.app",
            "storage_state_ref": ".beacon/qa/sessions/attached-demo/storage-state.json",
        },
    )

    assert _default_feature_qa_ui_runner(tmp_path) == "agent-browser"


def test_feature_qa_default_ui_runner_prefers_playwright_without_session(tmp_path: Path) -> None:
    assert _default_feature_qa_ui_runner(tmp_path) == "playwright"


def test_story_scenarios_default_browser_path_prefers_playwright() -> None:
    payload = expand_story_scenarios(
        feature=FEATURE,
        version=VERSION,
        story_sequence=[{"ac_id": "AC-001", "theme": "browser", "text": "Open dashboard in browser"}],
        entries=[{"ac_id": "AC-001", "tc_id": "TC-US001-001", "qa_type": "functional", "assertion": "Dashboard renders", "browser_required": True}],
        ui_runner="playwright",
        expansion_profile="pua-web",
        scenario_depth="standard",
    )

    browser_scenario = next(item for item in payload["scenarios"] if item["source_tc_id"] == "TC-US001-001")
    assert browser_scenario["browser_required"] is True
    assert 'npx playwright test' in browser_scenario["command"]
    assert 'npx playwright test' in browser_scenario["explore_command"]
    assert 'tournament_miniapp/playwright.config.ts' in browser_scenario["explore_command"]
    assert 'browser_use_runner' not in browser_scenario["command"]
    assert browser_scenario["exploratory_runner"] == "playwright"
    assert browser_scenario["deterministic_runner"] == "playwright"


def test_story_scenarios_treats_legacy_ui_layer_as_browser_required() -> None:
    payload = expand_story_scenarios(
        feature=FEATURE,
        version=VERSION,
        story_sequence=[{"ac_id": "AC-001", "theme": "legacy-ui", "text": "Create match from miniapp"}],
        entries=[{"ac_id": "AC-001", "tc_id": "TC-US001-UI", "layer": "ui", "assertion": "Create flow succeeds"}],
        ui_runner="playwright",
        expansion_profile="pua-web",
        scenario_depth="standard",
    )

    browser_scenarios = [item for item in payload["scenarios"] if item["source_tc_id"] == "TC-US001-UI"]
    assert browser_scenarios
    assert all(item["browser_required"] is True for item in browser_scenarios)
    assert any(item["scenario_family"] == "happy" for item in browser_scenarios)
    assert all('tournament_miniapp/playwright.config.ts' in item["explore_command"] for item in browser_scenarios)


def test_build_story_scenario_map_regenerates_stale_legacy_ui_machine_map(tmp_path: Path) -> None:
    docs_map = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json"
    docs_map.parent.mkdir(parents=True, exist_ok=True)
    docs_map.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "stories": [{"ac_id": "AC-001", "theme": "legacy-ui", "text": "Create match from miniapp", "scenario_ids": ["SC-001"], "scenario_families": ["primary"], "scenarios": []}],
                "scenarios": [
                    {
                        "scenario_id": "SC-001",
                        "source_tc_id": "TC-US001-UI",
                        "tc_id": "TC-US001-UI-PRIMARY",
                        "ac_id": "AC-001",
                        "qa_type": "functional",
                        "layer": "ui",
                        "scenario_family": "primary",
                        "browser_required": False,
                        "explore_command": "",
                        "replay_command": "",
                        "command": 'npx playwright test',
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = _build_story_scenario_map(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        story_sequence=[{"ac_id": "AC-001", "theme": "legacy-ui", "text": "Create match from miniapp"}],
        entries=[{"ac_id": "AC-001", "tc_id": "TC-US001-UI", "layer": "ui", "assertion": "Create flow succeeds"}],
        ui_runner="playwright",
    )

    browser_scenarios = [item for item in payload["scenarios"] if item["source_tc_id"] == "TC-US001-UI"]
    assert browser_scenarios
    assert any(item["scenario_family"] == "happy" for item in browser_scenarios)
    assert all(item["browser_required"] is True for item in browser_scenarios)


def test_feature_plan_rewrites_legacy_browser_use_default_to_playwright() -> None:
    command = _resolve_entry_command(
        qa_type="functional",
        command='python3 -m beacon.adapters.browser_use_runner --mode functional --fallback-cmd "python3 -m pytest -q -k functional --junitxml \\"${BEACON_JUNIT_PATH:-.beacon/junit.xml}\\""',
        ui_runner="playwright",
    )

    assert 'npx playwright test' in command
    assert 'browser_use_runner' not in command


def test_story_scenario_augment_rewrites_legacy_browser_use_default() -> None:
    payload = {
        "scenarios": [
            {
                "scenario_id": "SC-001",
                "source_tc_id": "TC-US001-001",
                "tc_id": "TC-US001-001-PRIMARY",
                "qa_type": "functional",
                "layer": "functional",
                "scenario_family": "happy",
                "browser_required": True,
                "replay_required": True,
                "exploratory_runner": "browser-use",
                "deterministic_runner": "playwright",
                "command": 'python3 -m beacon.adapters.browser_use_runner --mode functional --fallback-cmd "python3 -m pytest -q -k functional --junitxml \\"${BEACON_JUNIT_PATH:-.beacon/junit.xml}\\""',
                "replay_command": "",
            }
        ],
        "stories": [{"ac_id": "AC-001", "scenario_ids": ["SC-001"], "scenario_families": ["happy"], "scenarios": []}],
    }
    augmented = qa_feature._augment_story_scenario_map(
        feature=FEATURE,
        payload=payload,
        story_sequence=[{"ac_id": "AC-001", "theme": "browser", "text": "Open dashboard in browser"}],
        entries=[{"ac_id": "AC-001", "tc_id": "TC-US001-001", "qa_type": "functional", "browser_required": True}],
        ui_runner="playwright",
    )

    scenario = augmented["scenarios"][0]
    assert 'npx playwright test' in scenario["command"]
    assert 'npx playwright test' in scenario["explore_command"]
    assert 'tournament_miniapp/playwright.config.ts' in scenario["explore_command"]
    assert 'browser_use_runner' not in scenario["command"]
    assert scenario["exploratory_runner"] == "playwright"
    assert 'npx playwright test' in scenario["replay_command"]


def test_story_scenario_augment_backfills_empty_browser_explore_command() -> None:
    payload = {
        "scenarios": [
            {
                "scenario_id": "SC-001",
                "source_tc_id": "TC-US001-001",
                "tc_id": "TC-US001-001-HAPPY",
                "qa_type": "functional",
                "layer": "functional",
                "scenario_family": "happy",
                "browser_required": True,
                "replay_required": True,
                "exploratory_runner": "playwright",
                "deterministic_runner": "playwright",
                "command": "",
                "explore_command": "",
                "replay_command": "",
            }
        ],
        "stories": [{"ac_id": "AC-001", "scenario_ids": ["SC-001"], "scenario_families": ["happy"], "scenarios": []}],
    }
    augmented = qa_feature._augment_story_scenario_map(
        feature=FEATURE,
        payload=payload,
        story_sequence=[{"ac_id": "AC-001", "theme": "browser", "text": "Open dashboard in browser"}],
        entries=[{"ac_id": "AC-001", "tc_id": "TC-US001-001", "qa_type": "functional", "browser_required": True}],
        ui_runner="playwright",
    )

    scenario = augmented["scenarios"][0]
    assert 'npx playwright test' in scenario["explore_command"]
    assert 'tournament_miniapp/playwright.config.ts' in scenario["explore_command"]


def test_browser_runner_learning_reason_code_is_frozen() -> None:
    assert "browser_runner_learning_missing" in TEST_CONTRACT_REASON_CODES


def test_browser_runner_learning_note_is_written(tmp_path: Path) -> None:
    ref = _write_browser_runner_learning_note(
        project_root=tmp_path,
        version=VERSION,
        feature=FEATURE,
        tc_id="TC-US017-001",
        admission={
            "status": "blocked",
            "reason_code": "protected_surface_session_bridge_missing",
            "preferred_runner": "",
            "requested_runner": "browser-use",
            "target_url": "https://demo-preview.vercel.app/dashboard",
            "protected_surface": True,
        },
        authenticity={"status": "placeholder_only", "reason_code": "browser_evidence_placeholder_only"},
    )
    path = tmp_path / ref
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["feature_slug"] == SLUG
    assert payload["reason_code"] == "protected_surface_session_bridge_missing"
    assert payload["fallback_runner"] == "web-access"


def test_placeholder_browser_evidence_forces_needs_more_evidence() -> None:
    item = {
        "status": "passed",
        "browser_required": True,
        "replay_required": False,
        "browser_evidence_pack_ref": ".beacon/evidence/browser-pack.json",
        "browser_evidence_authenticity_status": "placeholder_only",
        "replay_ref": "",
        "evidence_ref": [".beacon/evidence/browser-pack.json"],
    }
    evidence = _evidence_sufficiency(item)
    closure = _closure_outcome(item, evidence_sufficiency=evidence)

    assert evidence == "weak"
    assert closure == "needs_more_evidence"


def test_runner_gap_does_not_reopen_implementation() -> None:
    item = {
        "status": "failed",
        "browser_required": True,
        "replay_required": False,
        "browser_evidence_pack_ref": ".beacon/evidence/browser-pack.json",
        "browser_evidence_authenticity_status": "authentic",
        "replay_ref": "",
        "evidence_ref": [".beacon/evidence/browser-pack.json"],
        "reason_code": "browser-use-unavailable",
    }

    evidence = _evidence_sufficiency(item)
    closure = _closure_outcome(item, evidence_sufficiency=evidence)

    assert evidence == "strong"
    assert closure == "needs_more_evidence"


def test_browser_runtime_admission_defaults_to_playwright_without_session() -> None:
    admission = resolve_browser_runtime_admission(
        item={"exploratory_runner": "", "target_url": "/"},
        active_browser_session={},
    )

    assert admission["status"] == "ready"
    assert admission["preferred_runner"] == "playwright"


def test_browser_task_defaults_to_playwright_runner_contract(tmp_path: Path) -> None:
    payload = build_browser_task(
        item={"tc_id": "TC-US001-001", "source_tc_id": "TC-US001-001", "assertion": "Dashboard renders"},
        qa_type="functional",
        mode="functional",
        project_root=tmp_path,
        session={},
    )

    assert payload["runner_contract"]["exploratory_runner"] == "playwright"
    assert payload["runner_contract"]["deterministic_runner"] == "playwright"


def test_default_browser_runner_command_ignores_playwright() -> None:
    assert default_browser_runner_command("playwright", qa_type="functional") == ""


def test_playwright_default_command_prefers_frontend_workspace_probe() -> None:
    command = default_command_for_qa_type("functional", ui_runner="playwright")

    assert 'tournament_miniapp/playwright.config.ts' in command
    assert 'cd "tournament_miniapp" && npx playwright test' in command


def test_playwright_compatibility_command_prefers_frontend_workspace_probe() -> None:
    command = default_command_for_qa_type("compatibility", ui_runner="playwright")

    assert 'tournament_miniapp/playwright.config.ts' in command
    assert '--project=chromium --project=firefox --project=webkit' in command
