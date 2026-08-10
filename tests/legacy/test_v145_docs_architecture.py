from __future__ import annotations

from pathlib import Path

from beacon.commands.workflow import ensure_output_dirs
from beacon.utils.docs_structure_contract import active_materialization_roots, build_docs_structure_contract, semantic_layer_for_surface


def test_new_docs_structure_contract_exists() -> None:
    contract = build_docs_structure_contract(version="v1.4.5")
    assert contract["semantic_layers"] == ["context", "truth", "guidance", "delivery", "evidence", ".machine"]
    assert contract["policies"]["progressive_materialization_default"] is True


def test_software_truth_maps_into_truth_layer() -> None:
    assert semantic_layer_for_surface("prd") == "truth"
    assert semantic_layer_for_surface("user-story") == "truth"
    assert semantic_layer_for_surface("test-case") == "truth"
    assert semantic_layer_for_surface("change") == "truth"


def test_guidance_outputs_do_not_mix_with_truth() -> None:
    assert semantic_layer_for_surface("ceo-review") == "guidance"
    assert semantic_layer_for_surface("brainstorm") == "guidance"
    assert semantic_layer_for_surface("design-review") == "guidance"
    assert semantic_layer_for_surface("deep") == "guidance"


def test_delivery_and_evidence_are_separated() -> None:
    assert semantic_layer_for_surface("implement") == "delivery"
    assert semantic_layer_for_surface("prototype") == "delivery"
    assert semantic_layer_for_surface("qa") == "evidence"
    assert semantic_layer_for_surface("release") == "evidence"


def test_paired_human_machine_projection_not_default() -> None:
    contract = build_docs_structure_contract(version="v1.4.5")
    assert contract["policies"]["paired_human_machine_projection_default"] is False
    assert contract["policies"]["machine_layer_role"] == "projection_only"


def test_machine_layer_is_projection_only() -> None:
    contract = build_docs_structure_contract(version="v1.4.5")
    assert contract["preferred_roots"][".machine"].endswith("/.machine/")
    assert contract["policies"]["machine_layer_role"] == "projection_only"


def test_historical_versions_remain_compatible() -> None:
    contract = build_docs_structure_contract(version="v1.4.5")
    truth_roots = contract["compatibility_projection_roots"]["truth"]
    assert "docs/beacon/v1.4.5/prd/" in truth_roots
    assert "docs/beacon/v1.4.5/user-story/" in truth_roots
    assert "docs/beacon/v1.4.5/qa/test-cases/" in truth_roots


def test_directories_are_created_progressively(tmp_path: Path) -> None:
    ensure_output_dirs(tmp_path, "v1.4.5")
    roots = active_materialization_roots(tmp_path, version="v1.4.5")
    assert roots["context"] == ["docs/beacon/v1.4.5/"]
    assert roots["guidance"] == ["docs/beacon/v1.4.5/execution/", "docs/brainstorms/"]
    assert roots["truth"] == []
    assert roots["evidence"] == []
    assert roots[".machine"] == []
    assert not (tmp_path / "docs" / "beacon" / "v1.4.5" / "prd").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.4.5" / "qa" / "test-cases").exists()
