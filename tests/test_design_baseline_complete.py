"""Complete DESIGN.md baseline + unattended fine-tune path."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.design_baseline import (
    OPEN_SOURCE_UI_AGENT_PRINCIPLES,
    render_complete_design_md,
    synthesize_unattended_design_baseline,
)
from beacon.utils.design_contract import write_version_design_contracts


def test_complete_design_md_has_required_axes_and_upstream_map() -> None:
    body = render_complete_design_md(product_name="Demo", preset="restrained-product", version="v1.6.7")
    assert "Open-source UI agent principles" in body
    assert "CSS variables" in body or "Visual tokens" in body
    assert "--primary:" in body
    assert "UI state coverage" in body
    assert "Anti-AI UI" in body
    assert "awesome-design-md" in body
    assert OPEN_SOURCE_UI_AGENT_PRINCIPLES["awesome-design-md"]["execution_kind"] == "reference-only"
    for axis in ("empty", "loading", "error", "success", "blocked"):
        assert axis in body


def test_unattended_writes_design_when_missing(tmp_path: Path) -> None:
    (tmp_path / "docs" / "beacon" / "v1.6.7").mkdir(parents=True)
    payload = synthesize_unattended_design_baseline(tmp_path, "v1.6.7", preset="operator-console")
    assert payload["status"] == "ready"
    assert payload["mode"] == "baseline"
    design = tmp_path / "DESIGN.md"
    assert design.exists()
    text = design.read_text(encoding="utf-8")
    assert "operator-console" in text or "Operator Console" in text
    assert (tmp_path / "docs/beacon/v1.6.7/design/style.md").exists()
    assert "Status: ready" in (tmp_path / "docs/beacon/v1.6.7/design/style.md").read_text(encoding="utf-8")


def test_unattended_fine_tune_preserves_existing_design(tmp_path: Path) -> None:
    (tmp_path / "docs" / "beacon" / "v1.6.7").mkdir(parents=True)
    existing = "# DESIGN.md — Brand X\n\n## Brand\nUse coral accent only.\n".encode("utf-8").decode("unicode_escape")
    (tmp_path / "DESIGN.md").write_text(existing, encoding="utf-8")
    payload = synthesize_unattended_design_baseline(tmp_path, "v1.6.7", force=False)
    assert payload["status"] == "fine_tune_proposed"
    assert payload["mode"] == "fine_tune"
    assert (tmp_path / "DESIGN.md").read_text(encoding="utf-8") == existing
    proposal = tmp_path / "docs/beacon/v1.6.7/design/fine-tune-proposal.md"
    assert proposal.exists()
    ptext = proposal.read_text(encoding="utf-8")
    assert "Fine-tune Against Existing DESIGN.md" in ptext
    assert "--primary:" in ptext


def test_write_version_design_contracts_include_complete_project_design(tmp_path: Path) -> None:
    (tmp_path / "docs" / "beacon" / "v1.6.7").mkdir(parents=True)
    payload = write_version_design_contracts(tmp_path, "v1.6.7", include_project_truth=True)
    assert payload["status"] == "ready"
    design = (tmp_path / "DESIGN.md").read_text(encoding="utf-8")
    assert design.startswith("---") and ("CSS variables" in design or "colors:" in design)
    assert "Open-source UI agent principles" in design
    assert "Delivery surface:" in design
