from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.feature_package import render_truth_package
from beacon.utils.manifest import compute_feature_paths, sync_manifest


runner = CliRunner()


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_package(root: Path, *, version: str = "v1.6.10", slug: str = "sidepilot-package") -> None:
    _write(root, f"docs/beacon/{version}/SUMMARY.md", f"# {version}\n")
    _write(root, f"docs/beacon/{version}/prd/{slug}.md", "# PRD\n\n- AC-001: package works\n")
    _write(root, f"docs/beacon/{version}/user-story/{slug}.md", "# User Story\n\n| AC ID | Theme | Description |\n|-------|-------|-------------|\n| AC-001 | package | package works |\n")
    _write(root, f"docs/beacon/{version}/qa/test-cases/{slug}.md", "# Test Cases\n\n| AC ID | TC ID | Layer | Assertion |\n|-------|-------|-------|-----------|\n| AC-001 | TC-001 | unit | pass |\n")
    package_root = root / "docs" / "beacon" / version / "features" / slug
    package_root.mkdir(parents=True, exist_ok=True)
    (package_root / "truth.md").write_text(
        "---\n"
        f"slug: {slug}\n"
        f"version: {version}\n"
        "status: draft\n"
        "language: zh\n"
        "canonical_refs:\n"
        f"  prd: docs/beacon/{version}/features/{slug}/truth.md\n"
        f"  user_story: docs/beacon/{version}/features/{slug}/truth.md\n"
        f"  test_case: docs/beacon/{version}/features/{slug}/tests.md\n"
        "parser_contract: beacon-feature-package-v1\n"
        "---\n\n"
        "# Feature\n\n"
        "## Acceptance Criteria\n\n"
        "| AC ID | Theme | Description |\n"
        "|-------|-------|-------------|\n"
        "| AC-001 | package | package works |\n",
        encoding="utf-8",
    )
    (package_root / "tests.md").write_text(
        "# Tests\n\n"
        "## Coverage Matrix\n\n"
        "| AC ID | TC ID | Layer | Command | Assertion |\n"
        "|-------|-------|-------|---------|-----------|\n"
        "| AC-001 | TC-001 | unit | `pytest` | pass |\n",
        encoding="utf-8",
    )
    (package_root / "tasks.md").write_text("# Tasks\n\n- [ ] TASK-001 do\n", encoding="utf-8")
    (package_root / "evidence.md").write_text(
        "# Evidence\n\n"
        "## Authority Surface\n\n"
        "| surface | authority | artifact |\n"
        "|---------|-----------|----------|\n"
        f"| truth.md | requirement_truth | docs/beacon/{version}/features/{slug}/truth.md |\n",
        encoding="utf-8",
    )


def test_package_ready_target_version_uses_package_paths(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    paths = compute_feature_paths(tmp_path, "v1.6.10", "sidepilot-package", prefer_package=True)
    manifest = sync_manifest(tmp_path, "v1.6.10")
    entry = next(item for item in manifest["features"] if item["slug"] == "sidepilot-package")

    assert paths["prd"] == "docs/beacon/v1.6.10/features/sidepilot-package/truth.md"
    assert paths["user_story"] == "docs/beacon/v1.6.10/features/sidepilot-package/truth.md"
    assert paths["test_case"] == "docs/beacon/v1.6.10/features/sidepilot-package/tests.md"
    assert entry["truth_paths"] == {
        "prd": "docs/beacon/v1.6.10/features/sidepilot-package/truth.md",
        "user_story": "docs/beacon/v1.6.10/features/sidepilot-package/truth.md",
        "test_case": "docs/beacon/v1.6.10/features/sidepilot-package/tests.md",
    }


def test_package_truth_presence_is_enough_for_default_paths(tmp_path: Path) -> None:
    version = "v1.6.10"
    slug = "truth-only-feature"
    _write(tmp_path, f"docs/beacon/{version}/SUMMARY.md", f"# {version}\n")
    _write(
        tmp_path,
        f"docs/beacon/{version}/features/{slug}/truth.md",
        "---\n"
        f"slug: {slug}\n"
        f"version: {version}\n"
        "status: draft\n"
        "language: zh\n"
        "canonical_refs:\n"
        f"  prd: docs/beacon/{version}/features/{slug}/truth.md\n"
        f"  user_story: docs/beacon/{version}/features/{slug}/truth.md\n"
        f"  test_case: docs/beacon/{version}/features/{slug}/tests.md\n"
        "parser_contract: beacon-feature-package-v1\n"
        "---\n\n"
        "# Feature\n\n"
        "## Acceptance Criteria\n\n"
        "| AC ID | Theme | Description |\n"
        "|-------|-------|-------------|\n"
        "| AC-001 | package | package truth is the visible requirement truth. |\n",
    )

    result = runner.invoke(
        app,
        [
            "prd-bootstrap",
            "run",
            slug,
            "--desc",
            "已有 package truth 时不默认生成旧三件套",
            "--project-root",
            str(tmp_path),
            "--version",
            version,
            "--skip-context-verify",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["targets"]["prd"] == f"docs/beacon/{version}/features/{slug}/truth.md"
    assert payload["targets"]["user_story"] == f"docs/beacon/{version}/features/{slug}/truth.md"
    assert payload["targets"]["test_case"] == f"docs/beacon/{version}/features/{slug}/tests.md"
    assert not (tmp_path / f"docs/beacon/{version}/prd/{slug}.md").exists()
    assert not (tmp_path / f"docs/beacon/{version}/user-story/{slug}.md").exists()
    assert not (tmp_path / f"docs/beacon/{version}/qa/test-cases/{slug}.md").exists()


def test_prd_bootstrap_truth_only_package_apply_writes_missing_tests_not_legacy_split(tmp_path: Path) -> None:
    version = "v1.6.10"
    slug = "truth-only-apply-feature"
    truth = (
        "---\n"
        f"slug: {slug}\n"
        f"version: {version}\n"
        "status: draft\n"
        "language: zh\n"
        "canonical_refs:\n"
        f"  prd: docs/beacon/{version}/features/{slug}/truth.md\n"
        f"  user_story: docs/beacon/{version}/features/{slug}/truth.md\n"
        f"  test_case: docs/beacon/{version}/features/{slug}/tests.md\n"
        "parser_contract: beacon-feature-package-v1\n"
        "---\n\n"
        "# Feature\n\n"
        "## Acceptance Criteria\n\n"
        "| AC ID | Theme | Description |\n"
        "|-------|-------|-------------|\n"
        "| AC-001 | package | package truth remains unchanged. |\n"
    )
    _write(tmp_path, f"docs/beacon/{version}/SUMMARY.md", f"# {version}\n")
    _write(tmp_path, f"docs/beacon/{version}/features/{slug}/truth.md", truth)

    result = runner.invoke(
        app,
        [
            "prd-bootstrap",
            "run",
            slug,
            "--desc",
            "补齐 package tests，不默认生成旧三件套",
            "--project-root",
            str(tmp_path),
            "--version",
            version,
            "--skip-context-verify",
            "--apply",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["generated_layers"] == ["tests"]
    assert payload["write_actions"] == [
        {
            "target": "test_case",
            "path": f"docs/beacon/{version}/features/{slug}/tests.md",
            "action": "created",
            "backup_path": "",
        }
    ]
    assert (tmp_path / f"docs/beacon/{version}/features/{slug}/truth.md").read_text(encoding="utf-8") == truth
    assert (tmp_path / f"docs/beacon/{version}/features/{slug}/tests.md").exists()
    assert not (tmp_path / f"docs/beacon/{version}/prd/{slug}.md").exists()
    assert not (tmp_path / f"docs/beacon/{version}/user-story/{slug}.md").exists()
    assert not (tmp_path / f"docs/beacon/{version}/qa/test-cases/{slug}.md").exists()


def test_prd_bootstrap_package_ready_does_not_generate_legacy_split_docs(tmp_path: Path) -> None:
    _seed_package(tmp_path, slug="new-package-feature")
    for rel in (
        "docs/beacon/v1.6.10/prd/new-package-feature.md",
        "docs/beacon/v1.6.10/user-story/new-package-feature.md",
        "docs/beacon/v1.6.10/qa/test-cases/new-package-feature.md",
    ):
        (tmp_path / rel).unlink()

    result = runner.invoke(
        app,
        [
            "prd-bootstrap",
            "run",
            "new-package-feature",
            "--desc",
            "生成 package truth，不默认写旧分面",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.10",
            "--skip-context-verify",
            "--apply",
            "--allow-overwrite",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["legacy_split"] is False
    assert payload["targets"]["prd"] == "docs/beacon/v1.6.10/features/new-package-feature/truth.md"
    assert payload["targets"]["user_story"] == "docs/beacon/v1.6.10/features/new-package-feature/truth.md"
    assert payload["targets"]["test_case"] == "docs/beacon/v1.6.10/features/new-package-feature/tests.md"
    assert not (tmp_path / "docs/beacon/v1.6.10/prd/new-package-feature.md").exists()
    assert not (tmp_path / "docs/beacon/v1.6.10/user-story/new-package-feature.md").exists()
    assert not (tmp_path / "docs/beacon/v1.6.10/qa/test-cases/new-package-feature.md").exists()


def test_truth_package_includes_plain_language_layer(tmp_path: Path) -> None:
    _seed_package(tmp_path, version="v1.6.10")

    text = render_truth_package(tmp_path, version="v1.6.10", feature="sidepilot-package")

    assert "## 人话" in text
    assert "## 用户旅程" in text
    assert "## First principles" in text
    assert "## Domain Model" in text
    assert "## Intent Coverage Matrix" in text
    assert "## FSM 五元组" in text
    assert "package_maturity: scaffold" in text
