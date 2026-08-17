from __future__ import annotations

from pathlib import Path

from beacon.utils.feature_package import sync_truth_frontmatter_status
VERSION = "v1.6.0"
FEATURE = "Truth Frontmatter Sync"
SLUG = "truth-frontmatter-sync"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_docs(root: Path) -> None:
    base = f"docs/beacon/{VERSION}"
    _write(
        root,
        f"{base}/features/{SLUG}/truth.md",
        "\n".join(
            [
                "---",
                f"slug: {SLUG}",
                f"version: {VERSION}",
                "status: draft",
                "language: en",
                "canonical_refs:",
                f"  prd: {base}/prd/{SLUG}.md",
                f"  user_story: {base}/user-story/{SLUG}.md",
                f"  test_case: {base}/qa/test-cases/{SLUG}.md",
                "parser_contract: beacon-feature-package-v1",
                "---",
                "",
                "# Feature Truth",
                "",
                "scope_mode = smoke",
                "",
                "| AC ID | Theme | Description |",
                "| --- | --- | --- |",
                "| AC-001 | sync | Freeze syncs truth frontmatter. |",
            ]
        ),
    )
    _write(
        root,
        f"{base}/features/{SLUG}/tests.md",
        "\n".join(
            [
                "# Tests",
                "",
                "| AC ID | TC ID | Layer | Command | Assertion |",
                "| --- | --- | --- | --- | --- |",
                "| AC-001 | TC-001 | contract | `pytest` | frontmatter sync |",
            ]
        ),
    )
    _write(
        root,
        f"{base}/user-story/{SLUG}.md",
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | sync | Freeze syncs truth frontmatter. |\n",
    )
    _write(root, f"{base}/prd/{SLUG}.md", "# PRD\n")
    _write(root, f"{base}/qa/test-cases/{SLUG}.md", "# Test Cases\n")


def test_sync_truth_frontmatter_status_updates_draft(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = sync_truth_frontmatter_status(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        status="frozen",
    )
    assert result["updated"] is True
    assert result["previous_status"] == "draft"
    assert result["status"] == "frozen"

    truth = (tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/truth.md").read_text(encoding="utf-8")
    assert "status: frozen" in truth
    assert "status: draft" not in truth

    idempotent = sync_truth_frontmatter_status(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        status="frozen",
    )
    assert idempotent["updated"] is False


def test_sync_truth_frontmatter_status_is_idempotent_after_update(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    sync_truth_frontmatter_status(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        status="frozen",
    )
    idempotent = sync_truth_frontmatter_status(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        status="frozen",
    )
    assert idempotent["updated"] is False
    assert idempotent["status"] == "frozen"
