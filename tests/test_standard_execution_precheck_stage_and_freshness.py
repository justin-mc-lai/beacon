"""Regression for issue #31 P1/P2: pre-implement material gate + stale precheck bundle.

P1 — `verify_materials_strict` (an implement-prefix check) required
`docs/beacon/<v>/release/`, which only exists after implement+qa. That is a
chicken-and-egg: the gate deadlocks before any code is written. Release docs are
now required only at the release stage.

P2 — a stored precheck verdict was trusted regardless of the workspace it was
computed on, so after fixing the cause the gate still reported the old `blocked`.
The bundle is now content-addressed (`inputs_digest`) and a drifted bundle is
recomputed instead of trusted.
"""

from __future__ import annotations

from pathlib import Path

from beacon.utils.material_audit import build_material_audit
from beacon.utils.standard_execution_precheck import bundle_is_fresh, precheck_inputs_digest

VERSION = "v1.6.18"
SLUG = "demo"


def _materialize_package(root: Path) -> None:
    d = root / "docs" / "beacon" / VERSION / "features" / SLUG
    d.mkdir(parents=True, exist_ok=True)
    for name in ("truth.md", "tests.md", "tasks.md", "evidence.md"):
        (d / name).write_text(f"# {name}\n", encoding="utf-8")


def _add_release_doc(root: Path) -> None:
    d = root / "docs" / "beacon" / VERSION / "release"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{VERSION}.md").write_text("# release\n", encoding="utf-8")


def _release_check(root: Path, *, stage: str = "") -> dict:
    audit = build_material_audit(root, version=VERSION, strict=True, feature=SLUG, stage=stage)
    return {check["name"]: check for check in audit["checks"]}["formal_release_present"]


def test_implement_stage_does_not_require_release_docs(tmp_path: Path) -> None:
    _materialize_package(tmp_path)
    check = _release_check(tmp_path, stage="implement")
    assert check["status"] == "pass", f"pre-implement gate must not require release docs: {check}"
    assert check["details"]["required"] is False


def test_release_stage_still_requires_release_docs(tmp_path: Path) -> None:
    _materialize_package(tmp_path)
    check = _release_check(tmp_path)
    assert check["status"] == "fail", "release stage must require release docs"
    assert check["details"]["required"] is True

    _add_release_doc(tmp_path)
    assert _release_check(tmp_path)["status"] == "pass"


def test_precheck_digest_tracks_inputs(tmp_path: Path) -> None:
    _materialize_package(tmp_path)
    before = precheck_inputs_digest(tmp_path, version=VERSION, feature=SLUG)
    _add_release_doc(tmp_path)
    after = precheck_inputs_digest(tmp_path, version=VERSION, feature=SLUG)
    assert before != after, "adding a release brief must change the precheck inputs digest"

    (tmp_path / "docs" / "beacon" / VERSION / "features" / SLUG / "truth.md").write_text("# changed\n", encoding="utf-8")
    assert precheck_inputs_digest(tmp_path, version=VERSION, feature=SLUG) != after


def test_bundle_freshness_rejects_stale_and_unaddressed(tmp_path: Path) -> None:
    _materialize_package(tmp_path)
    fresh = precheck_inputs_digest(tmp_path, version=VERSION, feature=SLUG)
    assert bundle_is_fresh(tmp_path, {"inputs_digest": fresh}, version=VERSION, feature=SLUG) is True
    assert bundle_is_fresh(tmp_path, {"inputs_digest": "deadbeef"}, version=VERSION, feature=SLUG) is False
    assert bundle_is_fresh(tmp_path, {}, version=VERSION, feature=SLUG) is False

    _add_release_doc(tmp_path)
    assert bundle_is_fresh(tmp_path, {"inputs_digest": fresh}, version=VERSION, feature=SLUG) is False
