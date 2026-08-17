from __future__ import annotations

from pathlib import Path

import pytest

from beacon.utils.archive_governance import (
    build_archive_inventory,
    build_archive_lineage,
    discover_features,
)
from beacon.utils.truth_map import evaluate_implement_version_governance_preflight
from beacon.utils.version_truth_catalog import (
    PARSER_CONTRACT,
    apply_catalog_plan,
    build_catalog_plan,
    catalog_md_authoritative,
    commit_catalog_payload,
    evaluate_catalog_delivery_preflight,
    list_active_catalog_versions,
    load_catalog_payload,
    parse_catalog_markdown,
    render_catalog_markdown,
    resolve_version_truth_root,
    verify_catalog_projection,
    verify_version_truth_catalog,
)


def _write_feature_truth(root: Path, version: str, slug: str, *, archived: bool = False) -> None:
    prefix = f"docs/beacon/archive/{version}" if archived else f"docs/beacon/{version}"
    truth_path = root / prefix / "features" / slug / "truth.md"
    truth_path.parent.mkdir(parents=True, exist_ok=True)
    truth_path.write_text(
        "\n".join(
            [
                "---",
                f"slug: {slug}",
                f"version: {version}",
                "status: frozen",
                "language: en",
                "canonical_refs:",
                f"  prd: {prefix}/features/{slug}/truth.md",
                "  user_story: ''",
                "  test_case: ''",
                "parser_contract: beacon-feature-package-v1",
                "---",
                "",
                "# Feature",
                "",
                "| AC ID | Theme | Description |",
                "|-------|-------|-------------|",
                "| AC-001 | demo | Demo acceptance |",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _seed_version_tree(root: Path, version: str) -> None:
    (root / "docs" / "beacon" / version / "features").mkdir(parents=True, exist_ok=True)


def _commit_catalog(
    root: Path,
    *,
    active: list[str],
    archived: list[str] | None = None,
) -> None:
    versions: dict[str, dict[str, str]] = {}
    for version in active:
        _seed_version_tree(root, version)
        versions[version] = {
            "version": version,
            "validation_state": "active",
            "truth_root": f"docs/beacon/{version}",
            "section": "active",
        }
    for version in archived or []:
        archive_root = root / "docs" / "beacon" / "archive" / version
        archive_root.mkdir(parents=True, exist_ok=True)
        versions[version] = {
            "version": version,
            "validation_state": "archived-reference-only",
            "truth_root": f"docs/beacon/archive/{version}",
            "section": "archived",
        }
    payload = {
        "schema_version": "1.0",
        "active_delivery_window": len(active) or 3,
        "active_truth_root_pattern": "docs/beacon/{version}/",
        "archived_truth_root_pattern": "docs/beacon/archive/{version}/",
        "support_research_root": "docs/beacon/research/",
        "versions": versions,
        "transaction": {},
    }
    commit_catalog_payload(root, payload, event_type="test-seed")


def test_catalog_md_is_sole_commit_source(tmp_path: Path) -> None:
    _commit_catalog(tmp_path, active=["v9.9.7", "v9.9.8", "v9.9.9"])
    md_path = tmp_path / "docs/beacon/governance/version-truth-catalog.md"
    assert md_path.is_file()
    text = md_path.read_text(encoding="utf-8")
    assert PARSER_CONTRACT in text
    round_trip = parse_catalog_markdown(text, project_root=tmp_path)
    assert round_trip["transaction"]["parser_contract"] == PARSER_CONTRACT
    assert (tmp_path / "docs/beacon/.machine/version-truth-catalog.json").is_file()
    rerendered = render_catalog_markdown(round_trip)
    assert "version-truth-catalog" in rerendered.lower() or "Version Truth Catalog" in rerendered


def test_active_window_three_versions(tmp_path: Path) -> None:
    _commit_catalog(tmp_path, active=["v9.9.7", "v9.9.8", "v9.9.9"])
    active = list_active_catalog_versions(tmp_path)
    assert active == ["v9.9.7", "v9.9.8", "v9.9.9"]
    payload = load_catalog_payload(tmp_path)
    active_entries = [
        item
        for item in payload["versions"].values()
        if isinstance(item, dict) and item.get("validation_state") == "active"
    ]
    assert len(active_entries) == 3
    for item in active_entries:
        assert str(item.get("truth_root", "")).startswith("docs/beacon/v")
        assert "/archive/" not in str(item.get("truth_root", ""))


def test_catalog_apply_relocates_archived_tree(tmp_path: Path) -> None:
    for version in ("v8.0.0", "v8.0.1", "v8.0.2", "v8.0.3"):
        _seed_version_tree(tmp_path, version)
        link_path = tmp_path / "docs/beacon" / version / "notes.md"
        link_path.write_text(f"see docs/beacon/{version}/features/demo/truth.md", encoding="utf-8")
    plan = build_catalog_plan(
        tmp_path,
        active_versions=["v8.0.1", "v8.0.2", "v8.0.3"],
    )
    assert plan["relocation_count"] == 1
    dry = apply_catalog_plan(tmp_path, plan, confirm=False)
    assert dry["status"] == "dry_run"
    applied = apply_catalog_plan(tmp_path, plan, confirm=True)
    assert applied["status"] == "applied"
    assert not (tmp_path / "docs/beacon/v8.0.0").exists()
    archive_tree = tmp_path / "docs/beacon/archive/v8.0.0"
    assert archive_tree.is_dir()
    rewritten = (archive_tree / "notes.md").read_text(encoding="utf-8")
    assert "docs/beacon/archive/v8.0.0/" in rewritten


def test_verify_strict_fails_on_catalog_drift(tmp_path: Path) -> None:
    _commit_catalog(tmp_path, active=["v9.9.7", "v9.9.8", "v9.9.9"])
    assert verify_catalog_projection(tmp_path, strict=True)["status"] == "pass"
    json_path = tmp_path / "docs/beacon/.machine/version-truth-catalog.json"
    json_path.write_text('{"source_hash": "stale"}', encoding="utf-8")
    drift = verify_catalog_projection(tmp_path, strict=True)
    assert drift["status"] == "fail"
    assert drift["reason_code"] == "catalog_projection_drift"
    doctor = verify_version_truth_catalog(tmp_path, strict=True)
    assert doctor["status"] == "fail"


def test_resolver_uses_active_catalog_only(tmp_path: Path) -> None:
    _commit_catalog(tmp_path, active=["v9.9.8", "v9.9.9"], archived=["v9.9.7"])
    _write_feature_truth(tmp_path, "v9.9.7", "legacy-feature", archived=True)
    blocked = evaluate_catalog_delivery_preflight(tmp_path, version="v9.9.7")
    assert blocked["blocked"] is True
    assert blocked["reason_code"] == "version_not_on_active_delivery_plane"
    preflight = evaluate_implement_version_governance_preflight(
        tmp_path,
        version="v9.9.7",
        feature="legacy-feature",
    )
    assert preflight["blocked"] is True
    assert preflight["reason_code"] == "version_not_on_active_delivery_plane"
    active_root = resolve_version_truth_root(tmp_path, "v9.9.9")
    assert str(active_root).endswith("docs/beacon/v9.9.9")


def test_discover_features_uses_truth_md(tmp_path: Path) -> None:
    _write_feature_truth(tmp_path, "v9.9.9", "package-feature")
    slugs = discover_features(tmp_path, version="v9.9.9")
    assert slugs == ["package-feature"]


def test_archive_lineage_spans_active_and_archive(tmp_path: Path) -> None:
    slug = "lineage-feature"
    _commit_catalog(tmp_path, active=["v9.9.8", "v9.9.9"], archived=["v9.9.7"])
    _write_feature_truth(tmp_path, "v9.9.7", slug, archived=True)
    _write_feature_truth(tmp_path, "v9.9.9", slug)
    payload = build_archive_lineage(tmp_path, feature=slug)
    assert payload["hop_count"] == 2
    hops = payload["hops"]
    assert hops[0]["version"] == "v9.9.7"
    assert "archive" in hops[0]["truth_path"]
    assert hops[1]["version"] == "v9.9.9"


def test_archive_inventory_active_ac_matrix(tmp_path: Path) -> None:
    _commit_catalog(tmp_path, active=["v9.9.8", "v9.9.9"], archived=["v9.9.7"])
    _write_feature_truth(tmp_path, "v9.9.7", "old-feature", archived=True)
    _write_feature_truth(tmp_path, "v9.9.9", "active-feature")
    payload = build_archive_inventory(tmp_path, version="auto", include_archived=False)
    versions = payload["versions"]
    assert "v9.9.7" not in versions
    assert payload["row_count"] == 1
    assert payload["rows"][0]["feature_slug"] == "active-feature"
    assert payload["rows"][0]["ac_ids"] == ["AC-001"]


def test_archive_index_regenerated_on_apply(tmp_path: Path) -> None:
    _seed_version_tree(tmp_path, "v7.0.0")
    _seed_version_tree(tmp_path, "v7.0.1")
    plan = build_catalog_plan(tmp_path, active_versions=["v7.0.1"])
    apply_catalog_plan(tmp_path, plan, confirm=True)
    index_path = tmp_path / "docs/beacon/archive/INDEX.md"
    assert index_path.is_file()
    index_text = index_path.read_text(encoding="utf-8")
    assert "v7.0.1" in index_text
    assert "beacon archive catalog status" in index_text.lower()


def test_catalog_bootstrap_dry_run_and_confirm(tmp_path: Path) -> None:
    for version in ("v6.0.0", "v6.0.1", "v6.0.2", "v6.0.3"):
        _seed_version_tree(tmp_path, version)
    plan = build_catalog_plan(tmp_path, active_versions=["v6.0.1", "v6.0.2", "v6.0.3"])
    dry = apply_catalog_plan(tmp_path, plan, confirm=False)
    assert dry["confirm_required"] is True
    applied = apply_catalog_plan(tmp_path, plan, confirm=True)
    assert applied["status"] == "applied"
    assert catalog_md_authoritative(tmp_path)
    assert verify_version_truth_catalog(tmp_path, strict=True)["status"] == "pass"


def test_beacon_archive_skill_documents_examples() -> None:
    skill_paths = [
        Path("skills/beacon/beacon-archive/SKILL.md"),
        Path(".cursor/skills/beacon-archive/SKILL.md"),
    ]
    for skill_path in skill_paths:
        if not skill_path.is_file():
            continue
        text = skill_path.read_text(encoding="utf-8")
        for verb in ("status", "history", "map", "cutover"):
            assert verb in text.lower()
        for marker in ("Example A", "Example B", "Example C", "Example D", "Example E", "Example F"):
            assert marker in text
        assert "beacon archive catalog plan" in text
        assert "beacon archive lineage" in text
        assert "beacon-change" in text.lower()


def test_global_boundaries_section_4_1_present() -> None:
    text = Path("docs/beacon/global-boundaries.md").read_text(encoding="utf-8")
    assert "### 4.1 MD-only catalog and archive plane" in text
    assert "version-truth-catalog.md" in text
    assert "does not replace `change`" in text
