from __future__ import annotations

from pathlib import Path

from beacon.utils.versioning import load_version_semantics, render_version_semantics_markdown


ROOT = Path(__file__).resolve().parents[1]


def test_version_semantics_markdown_mirror_should_match_json_contract():
    semantics = load_version_semantics(ROOT)
    rendered = render_version_semantics_markdown(semantics, version="v1.3.0")
    # v1.3.0 is archived lineage; its mirror lives under docs/beacon/archive/.
    mirror_path = ROOT / "docs" / "beacon" / "archive" / "v1.3.0" / "execution" / "version-semantics-contract.md"
    assert mirror_path.read_text(encoding="utf-8") == rendered


def test_version_semantics_contract_should_expose_sync_rule():
    semantics = load_version_semantics(ROOT)
    assert "Commands should expose version_context and version_semantics rather than reinterpreting raw fields." in semantics["rules"]
    assert semantics["source_path"] == "beacon/version-semantics.json"
