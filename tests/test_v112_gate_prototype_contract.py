"""v1.1.2 gate contracts for prototype lifecycle."""

from __future__ import annotations

from pathlib import Path

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.utils.prototype_support import source_fingerprints


def _write_ui_requirements(root: Path, version: str, feature: str) -> None:
    slug = feature.lower().replace(" ", "-")
    us = root / "docs" / "beacon" / version / "user-story"
    prd = root / "docs" / "beacon" / version / "prd"
    us.mkdir(parents=True, exist_ok=True)
    prd.mkdir(parents=True, exist_ok=True)
    (us / f"{slug}.md").write_text("ui_visualization_required: true\n", encoding="utf-8")
    (prd / f"{slug}.md").write_text("ui_visualization_required: true\n", encoding="utf-8")


def test_gate_should_flag_missing_prototype_when_ui_visualization_required(tmp_path: Path):
    _write_ui_requirements(tmp_path, "v1.1.2", "Feature Proto")
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version="v1.1.2")
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_missing" in reason_codes


def test_gate_should_accept_frozen_prototype_contract(tmp_path: Path):
    feature = "Feature Proto"
    slug = feature.lower().replace(" ", "-")
    _write_ui_requirements(tmp_path, "v1.1.2", feature)
    proto = tmp_path / "docs" / "beacon" / "v1.1.2" / "prototype" / slug
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "index.html").write_text("<html></html>", encoding="utf-8")
    (proto / "manifest.json").write_text('{"ui_kit":"bootstrap-5.3.x"}', encoding="utf-8")
    (proto / "source-map.json").write_text("{}", encoding="utf-8")
    fps = source_fingerprints(tmp_path, "v1.1.2", feature)
    (proto / "freeze.json").write_text(
        f'{{"status":"frozen","source_fingerprints":{fps!r}}}'.replace("'", '"'),
        encoding="utf-8",
    )
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "prototype", version="v1.1.2")
    assert issues == []
