"""Dual-axis version defaults: greenfield / external / beacon_self."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.version_defaults import (
    GREENFIELD_DEFAULT,
    bump_patch,
    classify_project,
    default_hotfix_baseline,
    default_target_version,
    resolve_goal_version,
)

ROOT = Path(__file__).resolve().parents[1]


def test_ac_axis_classify_beacon_self() -> None:
    info = classify_project(ROOT)
    assert info["project_kind"] == "beacon_self"
    assert info["runtime_version"]


def test_ac_axis_empty_greenfield_v001(tmp_path: Path) -> None:
    # empty project: no docs/beacon, no version-truth, no skills/beacon
    info = classify_project(tmp_path)
    assert info["project_kind"] == "external_greenfield"
    target = default_target_version(tmp_path)
    assert target["version"] == GREENFIELD_DEFAULT == "v0.0.1"
    assert target["source"] == "external_greenfield_default"
    assert target["runtime_version"]  # toolkit still reported
    # must NOT equal monorepo next line by coincidence requirement:
    # greenfield is always v0.0.1 regardless of toolkit
    r = resolve_goal_version(tmp_path, "auto", goal_mode="normal")
    assert r["project_docs_version"] == "v0.0.1"
    assert r["axis"]["project_docs_version"] == "v0.0.1"
    assert r["axis"]["runtime_version"]


def test_ac_axis_external_existing_patch(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "beacon" / "v0.2.3"
    docs.mkdir(parents=True)
    (docs / "SUMMARY.md").write_text("# v0.2.3\n", encoding="utf-8")
    info = classify_project(tmp_path)
    assert info["project_kind"] == "external_existing"
    target = default_target_version(tmp_path)
    assert target["version"] == "v0.2.4"
    assert target["source"] == "external_project_patch_bump"
    assert target["project_baseline"] == "v0.2.3"
    # toolkit runtime must not become the product version
    assert not target["version"].startswith("v1.6.")


def test_ac_axis_external_hotfix_project_baseline(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "beacon" / "v0.3.1"
    docs.mkdir(parents=True)
    (docs / "SUMMARY.md").write_text("# x\n", encoding="utf-8")
    hf = default_hotfix_baseline(tmp_path)
    assert hf["baseline"] == "v0.3.1"
    assert hf["bump"] is False
    assert hf["source"] == "project_delivery_baseline"
    r = resolve_goal_version(tmp_path, "auto", goal_mode="hotfix")
    assert r["hotfix_baseline"] == "v0.3.1"


def test_ac_axis_beacon_self_not_forced_v001() -> None:
    target = default_target_version(ROOT)
    assert target["project_kind"] == "beacon_self"
    assert target["version"] != "v0.0.1" or "beacon_self" in target["source"]
    # self should not use external_greenfield_default
    assert target["source"] != "external_greenfield_default"


def test_ac_axis_bump_patch_only() -> None:
    assert bump_patch("v0.0.1") == "v0.0.2"
    assert bump_patch("v1.6.8") == "v1.6.9"


def test_ac_axis_global_boundaries() -> None:
    text = (ROOT / "docs/beacon/global-boundaries.md").read_text(encoding="utf-8")
    assert "Dual-axis version" in text or "双轴" in text or "screwdriver" in text.lower() or "工件" in text
    assert "v0.0.1" in text
    assert "Runtime" in text or "runtime" in text


def test_ac_axis_skill_text() -> None:
    ref = (ROOT / "skills/beacon/references/version-default.md").read_text(encoding="utf-8")
    assert "v0.0.1" in ref
    assert "螺丝刀" in ref or "screwdriver" in ref.lower() or "工件" in ref


def test_ac_axis_feature_packages() -> None:
    assert (ROOT / "docs/beacon/archive/v1.6.9/features/beacon-fix-version-defaults-dual-axis-v169/truth.md").is_file()
