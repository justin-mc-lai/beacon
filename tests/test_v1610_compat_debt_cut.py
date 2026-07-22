from __future__ import annotations

from pathlib import Path

from beacon.utils.truth_map import (
    TRUTH_SOURCE_MODEL_AUTHORITATIVE,
    feature_package_authoritative,
    feature_package_authoritative_feature,
    truth_map_supported,
    truth_source_model_for_version,
)
from beacon.utils.truth_integrity import build_truth_integrity_gate
from beacon.utils.feature_package import package_paths


def test_authoritative_ignores_docs_version_including_v00x() -> None:
    for ver in ("v0.0.13", "v1.0.0", "v1.4.10", "v1.5.1", "v1.6.10"):
        assert feature_package_authoritative(ver) is True
        assert truth_source_model_for_version(ver) == TRUTH_SOURCE_MODEL_AUTHORITATIVE
        assert truth_map_supported(ver) is True


def test_authoritative_feature_true_for_product_line(tmp_path: Path) -> None:
    assert feature_package_authoritative_feature(tmp_path, version="v0.0.13", feature="any") is True


def test_freeze_module_has_no_legacy_split_skip() -> None:
    src = Path("beacon/commands/freeze.py").read_text(encoding="utf-8")
    assert 'skip_reason": "legacy_split_truth"' not in src
    assert 'reason": "legacy_split_truth"' not in src
    assert "package_gate_enabled = True" in src
    assert "validate_feature_package" in src


def test_v00x_package_layout_is_validated_not_skipped(tmp_path: Path) -> None:
    """Product docs line v0.0.x must run package integrity (dual-axis, §2.1)."""
    version = "v0.0.13"
    slug = "demo-product-lake"
    paths = package_paths(tmp_path, version=version, feature=slug)
    # intentionally incomplete four-piece
    paths["truth"].parent.mkdir(parents=True, exist_ok=True)
    paths["truth"].write_text(
        "---\nslug: demo-product-lake\nversion: v0.0.13\nstatus: draft\ndomain_required: false\n"
        "parser_contract: beacon-feature-package-v2\ntruth_source_model: feature_package_authoritative\n---\n\n"
        "# Truth\n\n## 人话\n\ndemo\n\n## Acceptance Criteria\n\n| AC ID | Description |\n|-------|-------------|\n| AC-001 | demo |\n",
        encoding="utf-8",
    )
    gate = build_truth_integrity_gate(tmp_path, version=version, feature=slug, mode="block")
    assert gate["feature_package_validation"].get("status") != "skipped"
    assert gate["blocked"] is True
    findings = gate.get("findings") or []
    texts = " ".join(str(f.get("text") or f.get("reason_code") or "") for f in findings)
    assert "missing_" in texts or gate.get("reason_code") or findings
