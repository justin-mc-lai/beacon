from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.design_contract import build_design_route_payload


VERSION = "v1.4.11"
FEATURE = "design-project-truth-initialization-contract"
runner = CliRunner()

pytestmark = [pytest.mark.current_contract]


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _truth_write(root: Path, *extra: str) -> dict:
    result = _invoke(["design", "truth", "--project", str(root), "--version", VERSION, "--write", *extra, "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_default_write_does_not_create_project_truth(tmp_path: Path) -> None:
    payload = _truth_write(tmp_path)

    assert not (tmp_path / "PRODUCT.md").exists()
    assert not (tmp_path / "DESIGN.md").exists()
    assert "product_truth" not in payload["writes"]
    assert "design_truth" not in payload["writes"]


def test_include_project_truth_creates_product_md(tmp_path: Path) -> None:
    payload = _truth_write(tmp_path, "--include-project-truth")

    assert (tmp_path / "PRODUCT.md").exists()
    assert payload["writes"]["product_truth"] == "written"


def test_include_project_truth_creates_design_md(tmp_path: Path) -> None:
    payload = _truth_write(tmp_path, "--include-project-truth")

    assert (tmp_path / "DESIGN.md").exists()
    assert payload["writes"]["design_truth"] == "written"


def test_existing_project_truth_is_not_overwritten_without_force(tmp_path: Path) -> None:
    product = tmp_path / "PRODUCT.md"
    design = tmp_path / "DESIGN.md"
    product.write_text("custom product truth\n", encoding="utf-8")
    design.write_text("custom design truth\n", encoding="utf-8")

    payload = _truth_write(tmp_path, "--include-project-truth")

    assert product.read_text(encoding="utf-8") == "custom product truth\n"
    assert design.read_text(encoding="utf-8") == "custom design truth\n"
    assert payload["writes"]["product_truth"] == "exists"
    assert payload["writes"]["design_truth"] == "exists"


def test_force_overwrites_project_truth(tmp_path: Path) -> None:
    product = tmp_path / "PRODUCT.md"
    design = tmp_path / "DESIGN.md"
    product.write_text("old product truth\n", encoding="utf-8")
    design.write_text("old design truth\n", encoding="utf-8")

    payload = _truth_write(tmp_path, "--include-project-truth", "--force")

    assert product.read_text(encoding="utf-8") != "old product truth\n"
    assert design.read_text(encoding="utf-8") != "old design truth\n"
    assert payload["writes"]["product_truth"] == "overwritten"
    assert payload["writes"]["design_truth"] == "overwritten"


def test_write_status_is_auditable(tmp_path: Path) -> None:
    payload = _truth_write(tmp_path, "--include-project-truth")

    expected = {
        "version_style",
        "component_system",
        "interaction_contract",
        "state_matrix",
        "product_truth",
        "design_truth",
        "machine_design_projection",
    }
    assert expected <= set(payload["writes"])
    assert payload["writes"]["machine_design_projection"].endswith("design-contract.projection.json")
    for key in expected - {"machine_design_projection"}:
        assert payload["writes"][key] in {"written", "exists", "overwritten"}


def test_product_template_has_required_sections(tmp_path: Path) -> None:
    _truth_write(tmp_path, "--include-project-truth")
    text = (tmp_path / "PRODUCT.md").read_text(encoding="utf-8")

    for required in [
        "project-level product truth",
        "Product Purpose",
        "Target Users",
        "Core Product Promises",
        "Non-Goals",
        "Truth Update Policy",
    ]:
        assert required in text


def test_design_template_has_required_sections(tmp_path: Path) -> None:
    _truth_write(tmp_path, "--include-project-truth")
    text = (tmp_path / "DESIGN.md").read_text(encoding="utf-8")

    for required in [
        "project-level design truth",
        "Design Principles",
        "Component System Baseline",
        "Interaction Principles",
        "UI State Coverage",
        "Accessibility And Responsive Baseline",
        "Truth Update Policy",
    ]:
        assert required in text


def test_machine_projection_remains_projection_only(tmp_path: Path) -> None:
    payload = _truth_write(tmp_path, "--include-project-truth")
    projection_path = tmp_path / payload["writes"]["machine_design_projection"]
    projection = json.loads(projection_path.read_text(encoding="utf-8"))

    assert projection["projection_only"] is True
    assert projection["truth_contract"]["truth_authority"]["projection_only"] == [
        f"docs/beacon/{VERSION}/.machine/design"
    ]


def test_design_routes_remain_support_only() -> None:
    payload = build_design_route_payload(Path("."), VERSION, FEATURE, intent="explore")

    assert payload["boundary"]["support_only"] is True
    assert payload["boundary"]["truth_source"] is False
    assert payload["boundary"]["gate_source"] is False
    assert payload["boundary"]["lifecycle_stage"] is False
