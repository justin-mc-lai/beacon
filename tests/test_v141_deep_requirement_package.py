from __future__ import annotations

from pathlib import Path

from beacon import __toolkit_version__, __version__
from beacon.utils.revision_state import load_revision_state

from v141_deep_helpers import FEATURE, VERSION, seed_deep_project


def test_three_piece_requirement_package_exists(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    root = tmp_path / "docs" / "beacon" / VERSION

    assert (root / "prd" / f"{FEATURE}.md").exists()
    assert (root / "user-story" / f"{FEATURE}.md").exists()
    assert (root / "qa" / "test-cases" / f"{FEATURE}.md").exists()


def test_freeze_means_implement_pending_not_done(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    state = load_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    assert state["doc_status"] == "frozen"
    assert state["delivery_status"] != "implemented"
    assert not (tmp_path / ".beacon" / "qa" / "features" / FEATURE / "scorecard.json").exists()


def test_planning_line_does_not_promote_runtime(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)

    assert VERSION == "v1.4.1"
    assert __version__ == "1.4.0"
    assert __toolkit_version__ == "v1.4.0"
