"""Multi-surface design packs + requirement-driven auto select."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.design_baseline import render_complete_design_md, synthesize_unattended_design_baseline
from beacon.utils.design_surfaces import auto_select_surface_from_text, google_yaml_frontmatter, scan_truth_for_ux


def test_auto_select_pc_console() -> None:
    d = auto_select_surface_from_text("ux_required: true\n运营中台订单管理后台")
    assert d["surface"] == "pc-console"


def test_auto_select_h5() -> None:
    d = auto_select_surface_from_text("H5 手机端下单页")
    assert d["surface"] == "h5"


def test_google_frontmatter_and_surface_render() -> None:
    body = render_complete_design_md(product_name="X", surface="client", version="v1.6.7")
    assert body.startswith("---")
    assert "version: alpha" in body
    assert "Delivery surface: `client`" in body
    assert "components:" in body
    fm = google_yaml_frontmatter("web")
    assert fm.startswith("---")
    assert "colors:" in fm


def test_ux_scan_and_surface_library_materialize(tmp_path: Path) -> None:
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "f").mkdir(parents=True)
    truth = "---\nux_required: true\n---\n# 客户端插件侧边栏\nextension sidebar UI\n"
    (tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "f" / "truth.md").write_text(truth, encoding="utf-8")
    assert scan_truth_for_ux(truth)["visual_delivery_claimed"] is True
    out = synthesize_unattended_design_baseline(tmp_path, "v1.6.7", surface="auto")
    assert out["surface"] == "client"
    assert out["visual_delivery_claimed"] is True
    assert (tmp_path / "docs/beacon/v1.6.7/design/surfaces/pc-console.DESIGN.md").exists()
    assert (tmp_path / "docs/beacon/v1.6.7/design/surfaces/web.DESIGN.md").exists()
    assert (tmp_path / "docs/beacon/v1.6.7/design/surfaces/h5.DESIGN.md").exists()
    assert (tmp_path / "docs/beacon/v1.6.7/design/surfaces/client.DESIGN.md").exists()
    assert (tmp_path / "DESIGN.md").read_text(encoding="utf-8").startswith("---")
