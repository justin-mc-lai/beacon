from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from beacon.compatibility.registry import registry_by_id
from beacon.main import app
from beacon.utils.design_contract import (
    bootstrap_design_capabilities,
    build_design_route_payload,
    design_route_contract,
    design_truth_contract,
    write_version_design_contracts,
)
from beacon.utils.prototype_support import design_result_adapter_status, write_design_result_adapter_binding


runner = CliRunner()
VERSION = "v1.4.11"
FEATURE = "beacon-design-product-prototype-rebuild-contract"
SLUG = "beacon-design-product-prototype-rebuild-contract"
pytestmark = [pytest.mark.projection_integrity]


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_docs(root: Path, *, binding_required: bool = True) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# Summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# Execution\n")
    marker = "design_result_binding_required: true\n" if binding_required else ""
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        f"# PRD\n{marker}\nPRODUCT.md\nDESIGN.md\ndocs/beacon/<version>/design/style.md\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        (
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | product truth | Beacon defines PRODUCT.md and DESIGN.md participation. |\n"
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        (
            "# Test Cases\n\n"
            "| AC ID | TC ID | Layer | Command | Assertion | Evidence |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| AC-001 | TC-001 | contract | pytest | truth paths exist | evidence.json |\n"
        ),
    )


def _invoke(args: list[str]):
    return runner.invoke(app, args)


@pytest.mark.current_contract
def test_product_and_design_truth_paths_are_defined(tmp_path: Path) -> None:
    contract = design_truth_contract(tmp_path, VERSION)

    paths = contract["truth_paths"]
    assert paths["product_truth"] == "PRODUCT.md"
    assert paths["design_truth"] == "DESIGN.md"
    assert paths["version_style"] == f"docs/beacon/{VERSION}/design/style.md"


@pytest.mark.current_contract
def test_version_design_style_is_version_wide(tmp_path: Path) -> None:
    contract = design_truth_contract(tmp_path, VERSION)

    assert f"docs/beacon/{VERSION}/design/style.md" in contract["truth_authority"]["version_wide"]
    assert contract["truth_authority"]["feature_local_design_product_rejected"] is True


def test_machine_design_is_projection_only(tmp_path: Path) -> None:
    contract = design_truth_contract(tmp_path, VERSION)

    assert f"docs/beacon/{VERSION}/.machine/design" in contract["truth_authority"]["projection_only"]


@pytest.mark.current_contract
def test_design_command_supports_component_system_contract(tmp_path: Path) -> None:
    result = _invoke(["design", "contract", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["routes"]["system"]["upstream"] == "ui-ux-pro-max"
    assert "component_system" in payload["routes"]["system"]["capabilities"]


@pytest.mark.current_contract
def test_design_contract_covers_required_axes(tmp_path: Path) -> None:
    contract = design_truth_contract(tmp_path, VERSION)

    assert set(contract["required_axes"]) == {"page", "component", "state", "interaction", "accessibility", "responsive"}


@pytest.mark.current_contract
def test_component_library_choices_are_source_bound(tmp_path: Path) -> None:
    contract = design_route_contract(tmp_path, VERSION, feature=FEATURE)

    assert contract["upstreams"]["ui-ux-pro-max"]["canonical_mirror"].endswith("ui-ux-pro-max-skill")
    assert contract["upstreams"]["awesome-design-md"]["execution_kind"] == "reference-only"


@pytest.mark.current_contract
def test_accepted_ui_ux_ledger_records_truth_refs(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    payload = write_design_result_adapter_binding(
        tmp_path,
        VERSION,
        FEATURE,
        design_result_ref="docs/ui-ux-dev/accepted.md",
        accepted_by="tester",
        summary="accepted design facts",
    )

    assert payload["status"] == "ready"
    truth = payload["truth_bindings"]
    assert truth["prd_refs"] == f"docs/beacon/{VERSION}/prd/{SLUG}.md"
    assert truth["user_story_refs"] == f"docs/beacon/{VERSION}/user-story/{SLUG}.md"
    assert truth["test_case_refs"] == f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md"


@pytest.mark.projection_integrity
def test_implement_blocks_on_unbound_accepted_ui_ux_facts(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    status = design_result_adapter_status(tmp_path, VERSION, FEATURE)

    assert status["status"] == "missing"
    assert status["reason_code"] == "design_result_adapter_binding_missing"
    assert "prototype adapt" in status["recommended_command"]


@pytest.mark.projection_integrity
def test_qa_blocks_on_stale_ui_truth(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    status = design_result_adapter_status(tmp_path, VERSION, FEATURE)

    assert status["binding_ready"] is False
    assert status["adapter_role"] == "design-result-adapter"


@pytest.mark.projection_integrity
def test_release_blocks_unbound_accepted_ui_ux_facts(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    status = design_result_adapter_status(tmp_path, VERSION, FEATURE)

    assert status["reason_code"] == "design_result_adapter_binding_missing"


@pytest.mark.current_contract
def test_prototype_defaults_to_design_truth_adapter(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "prototype_generation_externalized"
    assert payload["prototype_role"] == "design-result-adapter"


@pytest.mark.compat_contract
@pytest.mark.historical_fixture
def test_legacy_wireframe_requires_explicit_admission(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    registry = registry_by_id()
    current = _invoke(["prototype", "status", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert "prototype-legacy-wireframe-source" in registry
    assert current.exit_code == 0, current.stdout
    current_payload = json.loads(current.stdout)
    assert "legacy_prototype" not in current_payload

    result = _invoke([
        "prototype",
        "status",
        FEATURE,
        "--project",
        str(tmp_path),
        "--version",
        VERSION,
        "--include-legacy",
        "--json",
    ])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["adapter_role"] == "design-result-adapter"
    assert "legacy_prototype" in payload
    assert payload["legacy_prototype"]["current_closure"] is False


@pytest.mark.historical_fixture
def test_legacy_source_only_is_retired(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = _invoke(["prototype", "status", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] != "legacy_source_only"


@pytest.mark.compat_contract
@pytest.mark.historical_fixture
def test_legacy_wireframe_cannot_satisfy_current_gate(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    registry = registry_by_id()
    status = design_result_adapter_status(tmp_path, VERSION, FEATURE)

    assert "prototype-legacy-wireframe-source" in registry
    assert status["status"] == "missing"
    assert status["adapter_role"] == "design-result-adapter"


@pytest.mark.current_contract
def test_beacon_design_child_skill_exposes_stable_routes(tmp_path: Path) -> None:
    skill = Path("skills/beacon/beacon-design/SKILL.md")
    text = skill.read_text(encoding="utf-8")
    contract = design_route_contract(tmp_path, VERSION, feature=FEATURE)

    assert skill.exists()
    assert set(contract["routes"]) == {"explore", "system", "review", "polish", "extract", "library", "bootstrap"}
    assert "not a truth source" in text


@pytest.mark.current_contract
def test_beacon_design_vibe_to_ui_routes_preserve_explore_and_extract(tmp_path: Path) -> None:
    explore = build_design_route_payload(tmp_path, VERSION, FEATURE, intent="explore")
    extract = build_design_route_payload(tmp_path, VERSION, FEATURE, intent="extract")

    assert explore["upstream"] == "vibe-to-ui"
    assert extract["upstream"] == "vibe-to-ui"


@pytest.mark.current_contract
def test_beacon_design_system_route_preserves_ui_ux_pro_max(tmp_path: Path) -> None:
    payload = build_design_route_payload(tmp_path, VERSION, FEATURE, intent="system")

    assert payload["upstream"] == "ui-ux-pro-max"
    assert "stack_aware_guidance" in payload["capabilities"]


@pytest.mark.current_contract
def test_beacon_design_review_and_polish_routes_preserve_impeccable(tmp_path: Path) -> None:
    review = build_design_route_payload(tmp_path, VERSION, FEATURE, intent="review")
    polish = build_design_route_payload(tmp_path, VERSION, FEATURE, intent="polish")

    assert review["upstream"] == "impeccable"
    assert polish["upstream"] == "impeccable"


@pytest.mark.current_contract
def test_beacon_design_library_is_reference_only(tmp_path: Path) -> None:
    payload = build_design_route_payload(tmp_path, VERSION, FEATURE, intent="library")

    assert payload["upstream"] == "awesome-design-md"
    assert payload["boundary"]["reference_only"] is True
    assert payload["boundary"]["truth_source"] is False


@pytest.mark.current_contract
def test_beacon_design_bootstrap_is_capability_admission_only(tmp_path: Path) -> None:
    payload = build_design_route_payload(tmp_path, VERSION, FEATURE, intent="bootstrap")
    bootstrap = bootstrap_design_capabilities(tmp_path, VERSION)

    assert payload["boundary"]["capability_admission_only"] is True
    assert bootstrap["boundary"]["truth_source"] is False
    assert bootstrap["boundary"]["gate_source"] is False
    assert bootstrap["boundary"]["release_verdict"] is False


@pytest.mark.current_contract
def test_design_truth_write_creates_version_wide_surfaces(tmp_path: Path) -> None:
    payload = write_version_design_contracts(tmp_path, VERSION)

    assert payload["status"] == "ready"
    assert (tmp_path / f"docs/beacon/{VERSION}/design/style.md").exists()
    assert (tmp_path / f"docs/beacon/{VERSION}/design/component-system.md").exists()
    assert (tmp_path / f"docs/beacon/{VERSION}/.machine/design/design-contract.projection.json").exists()
