from __future__ import annotations

from pathlib import Path

from beacon.utils.v115_delivery import ensure_human_primary_indexes


def test_v145_indexes_only_materialize_qa_index_when_qa_surface_exists(tmp_path: Path) -> None:
    version = "v1.1.5"
    base = tmp_path / "docs" / "beacon" / version
    (base / "execution").mkdir(parents=True, exist_ok=True)

    actions = ensure_human_primary_indexes(tmp_path, version=version, apply=True)

    assert (base / "execution" / "index.md").exists()
    assert not (base / "qa" / "test-cases" / "index.md").exists()
    assert [item["path"] for item in actions] == [f"docs/beacon/{version}/execution/index.md"]


def test_v145_indexes_materialize_qa_index_once_qa_surface_exists(tmp_path: Path) -> None:
    version = "v1.1.5"
    qa_root = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    qa_root.mkdir(parents=True, exist_ok=True)
    (qa_root / "feature-a.md").write_text("# test\n", encoding="utf-8")

    actions = ensure_human_primary_indexes(tmp_path, version=version, apply=True)

    assert (qa_root / "index.md").exists()
    assert any(item["path"] == f"docs/beacon/{version}/qa/test-cases/index.md" for item in actions)
