from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.test_contract_governance import (
    CANONICAL_TEST_CONTRACT_LANES,
    QA_FIRST_PRINCIPLES_ORDER,
    build_test_contract_gate_payload,
    build_test_contract_index,
    load_test_contract_index,
    test_contract_index_path as contract_index_path,
)

runner = CliRunner()
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
    assert len(payload["test_refs"]) == 12
    assert payload["truth_refs"]["prd"] == f"docs/beacon/{VERSION}/prd/{SLUG}.md"
    assert payload["ac_to_test_refs"]["AC-001"] == ["TC-US001-001"]
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
