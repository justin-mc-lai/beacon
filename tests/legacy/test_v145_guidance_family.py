from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.test_case import _infer_layer_from_ac
from beacon.main import app
from beacon.utils.qa_feature import _targeted_entries
from beacon.utils.requirement_parsing import extract_qa_case_rows
from beacon.utils.brainstorm import run_beacon_brainstorm
from beacon.utils.ceo_review_surface import run_ceo_review
from beacon.utils.deep_loop import run_deep_loop
from beacon.utils.guidance_family import (
    build_guidance_family_contract,
    build_guidance_surface_projection,
    route_non_software_guidance,
)
from beacon.utils.help_support import build_help_payload
from beacon.utils.test_contract_governance import build_test_contract_gate_payload, build_test_contract_index


runner = CliRunner()
VERSION = "v1.4.5"
FEATURE = "beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_feature(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{FEATURE}.md",
        "# prd\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        "| AC-001 | general | Beacon freezes a guidance surface family that includes `ceo-review`, `brainstorm`, `design-review`, and `deep`. |\n"
        "| AC-002 | general | guidance surfaces are explicitly non-truth, non-gate, and non-stage surfaces. |\n"
        "| AC-003 | general | Beacon expresses a shared loop: `define -> challenge -> freeze -> execute -> verify -> learn`. |\n"
        "| AC-004 | general | the existing software lifecycle is documented as one materialization of the shared loop. |\n"
        "| AC-005 | general | non-software scenarios can be routed through guidance surfaces without requiring coding-first intermediate declarations. |\n"
        "| AC-006 | general | route explainability is consistent across guidance surfaces. |\n"
        "| AC-007 | general | guidance-family skills prioritize strategy philosophy, minimum complete tools, and necessary factual grounding over over-specified step scripts. |\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{FEATURE}.md",
        "# story\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        "| AC-001 | general | Beacon freezes a guidance surface family that includes `ceo-review`, `brainstorm`, `design-review`, and `deep`. |\n"
        "| AC-002 | general | guidance surfaces are explicitly non-truth, non-gate, and non-stage surfaces. |\n"
        "| AC-003 | general | Beacon expresses a shared loop: `define -> challenge -> freeze -> execute -> verify -> learn`. |\n"
        "| AC-004 | general | the existing software lifecycle is documented as one materialization of the shared loop. |\n"
        "| AC-005 | general | non-software scenarios can be routed through guidance surfaces without requiring coding-first intermediate declarations. |\n"
        "| AC-006 | general | route explainability is consistent across guidance surfaces. |\n"
        "| AC-007 | general | guidance-family skills prioritize strategy philosophy, minimum complete tools, and necessary factual grounding over over-specified step scripts. |\n",
    )
    _write(root, f"docs/beacon/{VERSION}/qa/test-cases/{FEATURE}.md", "# test\n")


def test_guidance_family_members_are_frozen() -> None:
    contract = build_guidance_family_contract()
    assert contract["members"] == ["ceo-review", "brainstorm", "design-review", "deep"]


def test_guidance_surfaces_are_non_truth_non_gate() -> None:
    contract = build_guidance_family_contract()
    assert contract["boundaries"]["not_truth_source"] is True
    assert contract["boundaries"]["not_gate_source"] is True
    assert contract["boundaries"]["not_new_lifecycle_stage"] is True


def test_shared_decision_loop_is_documented() -> None:
    contract = build_guidance_family_contract()
    assert contract["shared_decision_loop"] == ["define", "challenge", "freeze", "execute", "verify", "learn"]


def test_software_lifecycle_is_materialization() -> None:
    contract = build_guidance_family_contract()
    projection = contract["software_lifecycle_materialization"]["loop_projection"]
    assert projection["challenge"] == ["ceo-review", "brainstorm", "design-review", "deep"]
    assert projection["execute"] == ["implement"]
    assert projection["verify"] == ["qa", "release"]


def test_non_software_scenarios_route_through_guidance() -> None:
    route = route_non_software_guidance("整理航空出行提醒文章", output_shape="wechat-post")
    assert route["surface"] == "brainstorm"
    assert route["current_loop_layer"] == "challenge"
    assert route["recommended_route"] == "beacon-brainstorm"


def test_route_explainability_is_consistent(tmp_path: Path) -> None:
    _seed_feature(tmp_path)
    help_payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    ceo = run_ceo_review(tmp_path, version=VERSION, feature=FEATURE)
    brainstorm = run_beacon_brainstorm(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        prompt="判断这个跨行业 guidance surface 应如何回路由",
    )
    deep = run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    for payload in (
        help_payload["guidance_projection"],
        ceo["guidance_family"],
        brainstorm["guidance_family"],
        deep["guidance_family"],
        build_guidance_surface_projection("design-review", target_surface="prototype", recommended_route="beacon prototype"),
    ):
        assert payload["family_member"] is True
        assert payload["current_loop_layer"] == "challenge"
        assert payload["shared_decision_loop"] == ["define", "challenge", "freeze", "execute", "verify", "learn"]
        assert payload["boundaries"]["not_truth_source"] is True
        assert payload["boundaries"]["not_gate_source"] is True


def test_skill_philosophy_is_strategy_tool_fact_first() -> None:
    contract = build_guidance_family_contract()
    assert contract["skill_philosophy_priority"] == [
        "strategy_philosophy",
        "minimum_complete_tools",
        "necessary_factual_grounding",
    ]


def test_route_explainability_ac_should_not_be_classified_as_ui() -> None:
    text = "route explainability is consistent across guidance surfaces."
    assert _infer_layer_from_ac(text) == "unit"


def test_support_surface_mapping_rule_ac_should_not_be_classified_as_ui() -> None:
    text = "support-surface requirement semantics default to deterministic non-browser QA mapping unless UI/browser interaction is explicitly declared."
    assert _infer_layer_from_ac(text) == "unit"


def test_executable_ac_matrix_parser_should_accept_five_column_rows() -> None:
    content = """# Test Cases

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-008 | TC-GUIDE45-008 | contract | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "support_surface_mapping_rule_ac_should_not_be_classified_as_ui"` | support-surface requirement semantics stay in deterministic non-browser QA mapping unless UI/browser interaction is explicit |
"""
    rows = extract_qa_case_rows(content, "qa:test-cases:test")
    assert len(rows) == 1
    assert rows[0]["ac_id"] == "AC-008"
    assert rows[0]["explicit_layer"] == "contract"


def test_v145_guidance_feature_qa9_generation_should_not_widen_to_functional(tmp_path: Path) -> None:
    _seed_feature(tmp_path)

    result = runner.invoke(
        app,
        [
            "test-case",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    qa9_path = tmp_path / payload["qa9_matrix_path"]
    qa9_payload = json.loads(qa9_path.read_text(encoding="utf-8"))
    entries = qa9_payload["entries"]

    assert entries
    assert all(str(entry.get("qa_type") or "") != "functional" for entry in entries)


def test_feature_qa_should_rerun_when_source_matrix_content_changes_at_same_path() -> None:
    derived_entries = [
        {
            "tc_id": "TC-GUIDE45-008",
            "ac_id": "AC-008",
            "qa_type": "contract",
            "layer": "contract",
            "command": "python3 -m pytest -q tests/test_v145_guidance_family.py",
            "assertion": "support-surface requirement semantics stay in deterministic non-browser QA mapping unless UI/browser interaction is explicit",
        }
    ]
    previous_status = {
        "status": "passed",
        "evidence_done": True,
        "current_spec_fingerprint_hash": "spec-1",
        "implementation_run_id": "impl-1",
        "source_matrix_path": "docs/beacon/v1.4.5/.machine/qa/feature.qa9-matrix.json",
        "source_matrix_hash": "",
        "feature_scorecard": {"coverage_current": {"executed_scenarios": 1}},
        "scenario_results_v2": [{"scenario_id": "S1", "status": "passed"}],
    }

    status, reason_codes, impacted = _targeted_entries(
        derived_entries=derived_entries,
        previous_status=previous_status,
        spec_hash="spec-1",
        implementation_run_id="impl-1",
        source_matrix_path="docs/beacon/v1.4.5/.machine/qa/feature.qa9-matrix.json",
        source_matrix_hash="matrix-2",
        technical_archive={},
        blocking_updates=[],
    )

    assert status == "rerun_required"
    assert "source_matrix_changed" in reason_codes
    assert impacted == derived_entries


def test_support_surface_release_gate_does_not_require_browser_lane(tmp_path: Path) -> None:
    _seed_feature(tmp_path)
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/qa/test-cases/{FEATURE}.md",
        "# Test Cases\n\n"
        "| AC ID | TC ID | Layer | Command | Assertion |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| AC-001 | TC-GUIDE45-001 | contract | `python3 -m pytest -q tests/test_v145_guidance_family.py -k \"guidance_family_members_are_frozen\"` | guidance surface family contains `ceo-review`, `brainstorm`, `design-review`, and `deep` |\n"
        "| AC-008 | TC-GUIDE45-008 | contract | `python3 -m pytest -q tests/test_v145_guidance_family.py -k \"support_surface_mapping_rule_ac_should_not_be_classified_as_ui\"` | support-surface requirement semantics stay in deterministic non-browser QA mapping unless UI/browser interaction is explicit |\n",
    )
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/.machine/qa/{FEATURE}.ac-test-matrix.json",
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": FEATURE,
                "version": VERSION,
                "entries": [
                    {
                        "tc_id": "TC-GUIDE45-001",
                        "ac_id": "AC-001",
                        "layer": "contract",
                        "command": "python3 -m pytest -q tests/test_v145_guidance_family.py -k \"guidance_family_members_are_frozen\"",
                        "assertion": "guidance surface family contains `ceo-review`, `brainstorm`, `design-review`, and `deep`",
                        "evidence_path": f".beacon/evidence/qa-feature/{FEATURE}/tc-guide45-001/run-qa-001.json",
                        "source": f"qa:test-cases:docs/beacon/{VERSION}/qa/test-cases/{FEATURE}.md",
                    },
                    {
                        "tc_id": "TC-GUIDE45-008",
                        "ac_id": "AC-008",
                        "layer": "contract",
                        "command": "python3 -m pytest -q tests/test_v145_guidance_family.py -k \"support_surface_mapping_rule_ac_should_not_be_classified_as_ui\"",
                        "assertion": "support-surface requirement semantics stay in deterministic non-browser QA mapping unless UI/browser interaction is explicit",
                        "evidence_path": f".beacon/evidence/qa-feature/{FEATURE}/tc-guide45-008/run-qa-001.json",
                        "source": f"qa:test-cases:docs/beacon/{VERSION}/qa/test-cases/{FEATURE}.md",
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        "beacon/version-truth.json",
        json.dumps(
            {
                "schema_version": "1.0",
                "runtime_version": "v1.4.3",
                "package_version": "1.4.3",
                "docs_default_line": "v1.4.3",
                "current_runtime_release_line": "v1.4.3",
                "planning_lines": [VERSION],
                "partial_runtime_supplement_lines": [],
                "lines": {
                    "v1.4.3": {"status": "current_runtime_release"},
                    VERSION: {"status": "planning_only"},
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        f".beacon/evidence/qa-feature/{FEATURE}/tc-guide45-001/run-qa-001.json",
        json.dumps({"status": "passed", "tc_id": "TC-GUIDE45-001"}, ensure_ascii=False, indent=2) + "\n",
    )
    _write(
        tmp_path,
        f".beacon/evidence/qa-feature/{FEATURE}/tc-guide45-008/run-qa-001.json",
        json.dumps({"status": "passed", "tc_id": "TC-GUIDE45-008"}, ensure_ascii=False, indent=2) + "\n",
    )

    build_test_contract_index(tmp_path, version=VERSION, feature=FEATURE, write=True)
    gate = build_test_contract_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert gate["release_gate"]["blocked"] is False
    assert "browser_runtime_admission_missing" not in gate["release_gate"]["reason_codes"]
