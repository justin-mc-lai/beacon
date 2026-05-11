from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.implementation_plan import build_implementation_plan_gate_payload
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.technical_review_contract import build_technical_review_gate_payload
from beacon.utils.test_contract_governance import build_test_contract_gate_payload, build_test_contract_index


VERSION = "v1.4.3"
UMBRELLA = "beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation"
UMBRELLA_SLUG = "beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, ensure_ascii=False, indent=2))


def _seed_umbrella_repo(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    for rel in (
        "SUMMARY.md",
        "execution/index.md",
        "execution/architecture-blueprint.md",
        "release/v1.4.3.md",
        f"prd/{UMBRELLA_SLUG}.md",
        f"user-story/{UMBRELLA_SLUG}.md",
        f"qa/test-cases/{UMBRELLA_SLUG}.md",
        f"change/{UMBRELLA_SLUG}.md",
        "change/v1.4.3.md",
    ):
        _write(docs / rel, "# doc\n")
    _write(
        docs / "change" / f"{UMBRELLA_SLUG}.md",
        "# change\n- status: `reopened-for-subfeature-decomposition`\n- aggregation contract over accepted subfeatures\n",
    )
    _write(
        docs / "SUMMARY.md",
        "# summary\n- `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`\n  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / planning-umbrella`\n",
    )
    _write_json(
        docs / ".machine" / "user-story" / f"{UMBRELLA_SLUG}.json",
        {
            "schema_version": "1.0",
            "feature": UMBRELLA,
            "feature_slug": UMBRELLA_SLUG,
            "version": VERSION,
            "stories": [
                {
                    "story_id": "US-001",
                    "items": [
                        {"id": "AC-001", "kind": "ac", "theme": "ceo-surface", "text": "CEO surface"},
                        {"id": "AC-012", "kind": "ac", "theme": "boundary-safety", "text": "Boundary safety"},
                    ],
                }
            ],
        },
    )
    _write_json(
        docs / ".machine" / "qa" / f"{UMBRELLA_SLUG}.ac-test-matrix.json",
        {
            "schema_version": "1.0",
            "feature": UMBRELLA,
            "feature_slug": UMBRELLA_SLUG,
            "version": VERSION,
            "entries": [
                {
                    "tc_id": "TC-US001-001",
                    "ac_id": "AC-001",
                    "layer": "contract",
                    "command": "python3 -m pytest -q tests/test_v143_ceo_review_surface.py -k \"surface_exists_and_is_support_only\"",
                    "assertion": "CEO surface exists",
                    "evidence_path": f".beacon/evidence/test-results/{UMBRELLA_SLUG}/TC-US001-001.json",
                    "source": f"qa:test-cases:docs/beacon/{VERSION}/qa/test-cases/{UMBRELLA_SLUG}.md",
                },
                {
                    "tc_id": "TC-US012-001",
                    "ac_id": "AC-012",
                    "layer": "regression",
                    "command": "python3 -m pytest -q tests/test_v143_umbrella_acceptance_contract.py -k \"version_line_preserves_boundary_contract\"",
                    "assertion": "Boundary preserved",
                    "evidence_path": f".beacon/evidence/test-results/{UMBRELLA_SLUG}/TC-US012-001.json",
                    "source": f"qa:test-cases:docs/beacon/{VERSION}/qa/test-cases/{UMBRELLA_SLUG}.md",
                },
            ],
        },
    )
    _write_json(
        docs / ".machine" / "change" / "v1.4.3.json",
        {
            "version": VERSION,
            "features": [
                {
                    "feature": UMBRELLA,
                    "feature_slug": UMBRELLA_SLUG,
                    "status": "qa-accepted",
                }
            ],
            "implementation_order": {
                "waves": [
                    {
                        "features": [
                            {
                                "feature": UMBRELLA,
                                "feature_slug": UMBRELLA_SLUG,
                                "reason_code": "umbrella_acceptance_aggregation",
                            }
                        ]
                    }
                ]
            },
        },
    )
    _write_json(root / ".beacon" / "gate-report.json", {"status": "Pass", "version": VERSION, "issues": [], "run_id": "run-123"})


def test_v143_umbrella_feature_does_not_require_technical_review(tmp_path: Path) -> None:
    _seed_umbrella_repo(tmp_path)
    payload = build_technical_review_gate_payload(tmp_path, version=VERSION, feature=UMBRELLA, revision_id="R1")
    assert payload["required"] is False
    assert payload["status"] == "not_required"
    assert payload["blocked"] is False


def test_v143_release_scorecard_does_not_require_technical_review_state_for_umbrella(tmp_path: Path, monkeypatch) -> None:
    _seed_umbrella_repo(tmp_path)

    monkeypatch.setattr("beacon.utils.release_scorecard.resolve_target_version", lambda *_args, **_kwargs: VERSION)
    monkeypatch.setattr("beacon.utils.release_scorecard.resolve_runtime_version", lambda *_args, **_kwargs: "v1.4.2")
    monkeypatch.setattr("beacon.utils.release_scorecard.runtime_feature_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("beacon.utils.release_scorecard.project_runtime_feature_enabled", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("beacon.utils.release_scorecard.version_requires_prototype", lambda *_args, **_kwargs: False)
    monkeypatch.setattr("beacon.utils.release_scorecard.implementation_plan_supported", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("beacon.utils.release_scorecard.validate_evidence_manifest", lambda *_args, **_kwargs: {"status": "pass", "blocked": False, "issues": [], "blocked_count": 0})
    monkeypatch.setattr("beacon.utils.release_scorecard.load_qa_status", lambda *_args, **_kwargs: {"feature": UMBRELLA, "version": VERSION, "status": "passed", "evidence_done": True, "release_ready": True, "project_profile_gate": {"status": "pass"}})
    monkeypatch.setattr("beacon.utils.release_scorecard.load_exhaustiveness_report", lambda *_args, **_kwargs: {"status": "passed"})
    monkeypatch.setattr("beacon.utils.release_scorecard.load_feature_qa_scorecard", lambda *_args, **_kwargs: {"release_ready": True, "continue_decision": "ready_for_release", "unresolved_closure_outcomes": [], "project_profile_gate_status": "pass", "coverage_current": {"required_scenarios": 1, "executed_scenarios": 1, "coverage_rate": 1.0}})
    monkeypatch.setattr("beacon.utils.release_scorecard.load_implementation_plan_progress", lambda *_args, **_kwargs: {})
    monkeypatch.setattr("beacon.utils.release_scorecard.load_latest_evo_experiment", lambda *_args, **_kwargs: {})
    monkeypatch.setattr("beacon.utils.release_scorecard.list_implementation_git_workflow_contracts", lambda *_args, **_kwargs: [])
    monkeypatch.setattr("beacon.utils.release_scorecard.load_revision_state", lambda *_args, **_kwargs: {"revision_id": "R1", "source_revision_id": "", "doc_status": "frozen", "delivery_status": "verified"})
    monkeypatch.setattr("beacon.utils.release_scorecard.build_requirement_completeness_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr("beacon.utils.release_scorecard.build_requirement_clarity_gate_payload", lambda *_args, **_kwargs: {"blocked": False})
    monkeypatch.setattr("beacon.utils.release_scorecard.load_requirement_clarity_state", lambda *_args, **_kwargs: {"status": "pass", "finding_count": 0})
    monkeypatch.setattr("beacon.utils.release_scorecard.build_technical_review_gate_payload", lambda *_args, **_kwargs: {"required": False, "blocked": False, "status": "not_required"})
    monkeypatch.setattr("beacon.utils.release_scorecard.load_technical_review_state", lambda *_args, **_kwargs: {})
    monkeypatch.setattr("beacon.utils.release_scorecard.evaluate_semantic_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr("beacon.utils.release_scorecard.build_test_contract_gate_payload", lambda *_args, **_kwargs: {"release_gate": {"status": "pass", "blocked": False, "reason_codes": []}})
    monkeypatch.setattr("beacon.utils.release_scorecard.build_acceptance_kit_projection", lambda *_args, **_kwargs: {"summary": {"all_layers_passed": True}})
    monkeypatch.setattr("beacon.utils.release_scorecard.acceptance_projection_transaction_contract", lambda *_args, **_kwargs: {"status": "pass", "reason_code": ""})
    monkeypatch.setattr("beacon.utils.release_scorecard.evaluate_implement_prompt_boundary", lambda *_args, **_kwargs: {})
    monkeypatch.setattr("beacon.utils.release_scorecard.load_delivery_read_model", lambda *_args, **_kwargs: {"implement": {"prompt_boundary": {"required": False, "status": "not_required", "blocked": False}, "delivery_contract": {}}, "qa": {"delivery_contract": {}}, "release": {"release_ready": True}, "traceability": {}, "risk_flags": []})

    payload = build_release_scorecard(tmp_path, version=VERSION)
    assert payload["technical_review"]["status"] == "not_required"
    assert payload["release_ready"] is True


def test_v143_umbrella_feature_does_not_require_implementation_plan(tmp_path: Path) -> None:
    _seed_umbrella_repo(tmp_path)
    payload = build_implementation_plan_gate_payload(tmp_path, version=VERSION, feature=UMBRELLA)
    assert payload["required"] is False
    assert payload["status"] == "not_required"
    assert payload["blocked"] is False


def test_v143_aggregation_contract_test_governance_does_not_require_browser_lane(tmp_path: Path) -> None:
    _seed_umbrella_repo(tmp_path)
    build_test_contract_index(tmp_path, version=VERSION, feature=UMBRELLA, write=True)
    payload = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=UMBRELLA)
    assert payload["release_gate"]["blocked"] is False
    assert "browser_runtime_admission_missing" not in payload["release_gate"]["reason_codes"]
    assert "feature_release_lane_missing" not in payload["release_gate"]["reason_codes"]
