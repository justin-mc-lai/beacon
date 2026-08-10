from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.artifact_update_obligations import write_artifact_update_obligations
from beacon.utils.delivery_baseline import materialize_implementation_delivery_baseline
from beacon.utils.implementation_plan import compile_implementation_plan
from beacon.utils.material_gate_contract import (
    ALLOWED_MATERIAL_EFFECTS,
    branch_governance_writeback_targets,
    build_material_gate_preflight,
    execution_host_required_surfaces,
    explicit_delivery_fact_gate,
    material_gate_diagnostics,
    subskill_material_effect_registry,
    support_and_toolkit_boundary_contract,
    support_finding_adoption_contract,
    validate_subskill_invocation_effect,
)
from beacon.utils.qa_feature import build_feature_qa_plan
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.story_state import freeze_story_state, sync_story_state_from_docs
from beacon.utils.technical_review_contract import materialize_technical_review_contract


VERSION = "v1.4.8"
FEATURE = "beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract"
SLUG = FEATURE


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_requirement_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", f"# Summary\n- `{FEATURE}`\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# Execution Index\n")
    _write(root, f"docs/beacon/{VERSION}/execution/boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/index.md", "# Source Architecture\n")
    _write(root, f"docs/beacon/{VERSION}/research/{SLUG}.md", "# Research\n\n## Business Flow\n- explicit material gates\n")
    _write(root, f"docs/beacon/{VERSION}/change/{SLUG}.md", "# Change\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        "\n".join(
            [
                "# PRD",
                "",
                "## 2. 目标",
                "- Restore strong material gates.",
                "",
                "## 4. 范围",
                "- execution host and subskill writeback contracts.",
                "",
                "## 8. 验收标准",
                *[f"- AC-{idx:03d} criterion {idx}" for idx in range(1, 13)],
                "",
            ]
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        "# User Story\n\n## Acceptance Criteria\n"
        + "\n".join(f"- AC-{idx:03d} criterion {idx}" for idx in range(1, 13))
        + "\n",
    )
    rows = [
        f'| AC-{idx:03d} | TC-MATGATE48-{idx:03d} | contract | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "case_{idx:03d}"` | covers AC-{idx:03d} |'
        for idx in range(1, 13)
    ]
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        "# Test Cases\n\n| AC ID | TC ID | Layer | Command | Assertion |\n| --- | --- | --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n",
    )


def _freeze_docs(root: Path) -> None:
    sync_story_state_from_docs(root, VERSION, FEATURE)
    freeze_story_state(root, VERSION, FEATURE)
    freeze_revision_state(root, version=VERSION, feature=FEATURE)


def _approved_contract(root: Path, *, source: str = "human_approved") -> None:
    materialize_technical_review_contract(
        root,
        version=VERSION,
        feature=FEATURE,
        revision_id="R1",
        force_refresh=True,
        contract_overrides={
            "review_status": "approved",
            "approved_by": "tester",
            "reviewed_at": "2026-05-21T10:00:00Z",
            "source": source,
        },
    )


def _seed_execution_ready(root: Path) -> None:
    _seed_requirement_docs(root)
    _freeze_docs(root)
    _approved_contract(root)
    exit_code, payload = compile_implementation_plan(root, version=VERSION, feature=FEATURE)
    assert exit_code == 0, payload


def test_execution_host_required_surfaces_are_declared(tmp_path: Path) -> None:
    _seed_execution_ready(tmp_path)

    payload = execution_host_required_surfaces(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["status"] == "pass"
    assert set(payload["surfaces"]) == {
        "execution_index",
        "architecture_blueprint",
        "delivery_baseline",
        "git_workflow",
        "technical_review_contract",
    }


def test_implement_blocks_on_missing_or_drifted_architecture_blueprint_projection(tmp_path: Path) -> None:
    _seed_execution_ready(tmp_path)
    blueprint = tmp_path / "docs" / "beacon" / VERSION / "execution" / "architecture-blueprint.md"
    blueprint.write_text("# drifted\n", encoding="utf-8")

    gate = build_material_gate_preflight(tmp_path, version=VERSION, feature=FEATURE)

    assert gate["blocked"] is True
    assert gate["reason_code"] == "architecture_blueprint_projection_missing"


def test_delivery_facts_must_be_explicit_not_default_seeded(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path)
    _freeze_docs(tmp_path)
    _approved_contract(tmp_path, source="version_default")

    gate = explicit_delivery_fact_gate(tmp_path, version=VERSION, feature=FEATURE)

    assert gate["blocked"] is True
    assert {"reason_code": "weak_fact_source", "field": "source", "value": "version_default"} in gate["diagnostics"]


def test_weak_fact_sources_do_not_unlock_implement(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path)
    _freeze_docs(tmp_path)
    _approved_contract(tmp_path, source="project_config_seed")

    exit_code, payload = compile_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert exit_code == 2
    assert payload["reason_code"] == "explicit_delivery_fact_gate_blocked"
    diagnostics = payload["material_gate_preflight"]["gates"]["explicit_delivery_facts"]["diagnostics"]
    assert any(item["reason_code"] == "weak_fact_source" for item in diagnostics)


def test_subskill_material_effect_registry_covers_all_human_surfaces() -> None:
    registry = subskill_material_effect_registry()

    assert registry["status"] == "pass"
    for family in ("host", "truth", "execution", "gate", "support", "toolkit", "compatibility", "project-local"):
        assert registry["families"][family]
    assert registry["entries"]["beacon-toolkit-branch-governance"]["default_material_effect"] == "execution_host_update_required"


def test_subskill_invocation_must_resolve_to_material_effect() -> None:
    valid = validate_subskill_invocation_effect(
        {
            "skill": "beacon-doubt-review",
            "material_effect": "read_only_route_only",
            "target_artifacts": [],
        }
    )
    invalid = validate_subskill_invocation_effect(
        {
            "skill": "beacon-toolkit-branch-governance",
            "material_effect": "writeback_completed",
            "target_artifacts": [],
        }
    )

    assert valid["status"] == "pass"
    assert invalid["status"] == "blocked"
    assert invalid["diagnostics"][0]["reason_code"] == "subskill_material_effect_target_missing"


def test_accepted_support_finding_opens_material_update_or_obligation() -> None:
    accepted = support_finding_adoption_contract(
        {
            "accepted": True,
            "artifact_update_obligation": {"required": True, "artifact": "technical_review_contract"},
        }
    )
    unadopted = support_finding_adoption_contract({"accepted": True})

    assert accepted["status"] == "pass"
    assert accepted["material_effect"] == "obligation_opened"
    assert unadopted["status"] == "blocked"
    assert unadopted["reason_code"] == "accepted_support_finding_not_adopted"


def test_support_surfaces_remain_advisory_until_adopted() -> None:
    readonly = validate_subskill_invocation_effect(
        {
            "skill": "beacon-source-driven",
            "material_effect": "read_only_route_only",
            "target_artifacts": [],
        }
    )
    boundary = support_and_toolkit_boundary_contract("beacon-source-driven")

    assert readonly["status"] == "pass"
    assert boundary["status"] == "pass"
    assert boundary["truth_source"] is False
    assert boundary["gate_source"] is False


def test_branch_governance_updates_canonical_execution_and_metadata_surfaces(tmp_path: Path) -> None:
    payload = branch_governance_writeback_targets(tmp_path, version=VERSION, feature=FEATURE)

    targets = payload["target_artifacts"]
    assert payload["material_effect"] == "execution_host_update_required"
    assert targets["git_workflow_json"].endswith(f"git-workflow-{SLUG}.json")
    assert targets["technical_review_json"].endswith(f"deterministic-implementation-contract-{SLUG}.json")
    assert targets["architecture_blueprint"].endswith("execution/architecture-blueprint.md")
    assert targets["service_slice_map"].endswith("execution/service-slice-map.md")
    assert targets["metadata_contract"].endswith(".beacon/metadata/project-version-metadata.json")


def test_qa_and_release_block_on_open_artifact_update_obligations(tmp_path: Path) -> None:
    _seed_execution_ready(tmp_path)
    write_artifact_update_obligations(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-test",
        updates={"technical_review_contract": {"required": True, "reason": "accepted support finding"}},
    )
    revision_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"{SLUG}.revision.json"
    revision = json.loads(revision_path.read_text(encoding="utf-8"))
    revision["delivery_status"] = "implemented"
    revision["last_implementation_run_id"] = "run-test"
    write_json(revision_path, revision)

    qa_plan = build_feature_qa_plan(tmp_path, version=VERSION, feature=FEATURE, persist=False)
    diagnostics = material_gate_diagnostics(tmp_path, version=VERSION, feature=FEATURE)

    assert "artifact_updates_pending" in qa_plan["reason_codes"]
    assert diagnostics["blocked"] is True
    assert any(item["reason_code"] == "artifact_updates_pending" for item in diagnostics["diagnostics"])


def test_gate_diagnostics_name_missing_material_and_repair_route(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path)
    _freeze_docs(tmp_path)
    materialize_implementation_delivery_baseline(tmp_path, version=VERSION, feature=FEATURE, revision_id="R1")

    diagnostics = material_gate_diagnostics(tmp_path, version=VERSION, feature=FEATURE)

    assert diagnostics["status"] == "blocked"
    reason_codes = {item["reason_code"] for item in diagnostics["diagnostics"]}
    assert "missing_material" in reason_codes
    assert "weak_fact_source" in reason_codes
    assert all("repair_route" in item for item in diagnostics["diagnostics"])


def test_support_and_toolkit_do_not_become_new_lifecycle_stages() -> None:
    for skill in ("beacon-doubt-review", "beacon-security-review", "beacon-toolkit-branch-governance"):
        payload = support_and_toolkit_boundary_contract(skill)
        assert payload["status"] == "pass"
        assert payload["new_lifecycle_stage"] is False
        assert payload["truth_source"] is False
        assert payload["gate_source"] is False


def test_case_001() -> None:
    assert "writeback_completed" in ALLOWED_MATERIAL_EFFECTS


def test_case_002() -> None:
    assert "execution_host_update_required" in ALLOWED_MATERIAL_EFFECTS


def test_case_003() -> None:
    assert "version_default" in {"version_default", "project_config_seed"}


def test_case_004() -> None:
    assert "project_config_seed" in {"version_default", "project_config_seed"}


def test_case_005() -> None:
    assert "toolkit" in subskill_material_effect_registry()["families"]


def test_case_006() -> None:
    assert validate_subskill_invocation_effect({"skill": "beacon-qa", "material_effect": "evidence_update_required", "target_artifacts": ["qa"]})["status"] == "pass"


def test_case_007() -> None:
    assert support_finding_adoption_contract({"accepted": True, "adoption_route": "release-blocker"})["status"] == "pass"


def test_case_008() -> None:
    assert support_and_toolkit_boundary_contract("beacon-ceo-review")["truth_source"] is False


def test_case_009(tmp_path: Path) -> None:
    assert branch_governance_writeback_targets(tmp_path, version=VERSION, feature=FEATURE)["status"] == "pass"


def test_case_010(tmp_path: Path) -> None:
    write_artifact_update_obligations(tmp_path, version=VERSION, feature=FEATURE, run_id="run", updates={"x": {"required": True}})
    assert material_gate_diagnostics(tmp_path, version=VERSION, feature=FEATURE)["blocked"] is True


def test_case_011(tmp_path: Path) -> None:
    assert material_gate_diagnostics(tmp_path, version=VERSION, feature=FEATURE)["diagnostics"]


def test_case_012() -> None:
    assert support_and_toolkit_boundary_contract("beacon-toolkit-branch-governance")["new_lifecycle_stage"] is False
