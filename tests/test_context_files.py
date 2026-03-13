"""Tests for Beacon context file management helpers."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.context_files import (
    MANAGED_BLOCK_END,
    MANAGED_BLOCK_START,
    build_default_agents_managed_block,
    build_default_claude_managed_block,
    inspect_context_file,
    merge_managed_block,
    setup_context_files,
    verify_context_files,
    write_context_file,
)


def test_merge_managed_block_should_create_when_empty():
    managed = build_default_claude_managed_block("v1.2.3")

    result = merge_managed_block("", managed)

    assert result["mode"] == "created"
    assert result["content"] == managed


def test_merge_managed_block_should_replace_only_managed_section_when_valid():
    old_managed = build_default_claude_managed_block("v1.0.0")
    new_managed = build_default_claude_managed_block("v1.2.3")
    existing = f"prefix\n{old_managed}suffix\n"

    result = merge_managed_block(existing, new_managed)

    assert result["mode"] == "replaced"
    assert result["content"].startswith("prefix\n")
    assert result["content"].endswith("suffix\n")
    assert "BEACON:VERSION:v1.2.3" in result["content"]
    assert "BEACON:VERSION:v1.0.0" not in result["content"]


def test_merge_managed_block_should_prepend_and_preserve_existing_when_no_markers():
    managed = build_default_agents_managed_block("v1.2.3")
    existing = "# AGENTS\n\nUser rules here\n"

    result = merge_managed_block(existing, managed)

    assert result["mode"] == "prepended"
    assert result["content"].startswith(managed)
    assert "## User Customization (preserved by Beacon)" in result["content"]
    assert "User rules here" in result["content"]


def test_merge_managed_block_should_recover_when_markers_corrupted():
    managed = build_default_claude_managed_block("v1.2.3")
    existing = f"{MANAGED_BLOCK_START}\npartial\n"

    result = merge_managed_block(existing, managed)

    assert result["mode"] == "recovered"
    assert result["content"].startswith(managed)
    assert "## User Customization (preserved by Beacon)" in result["content"]
    assert "partial" in result["content"]


def test_write_context_file_should_create_backup_when_existing_file_changes(tmp_path: Path):
    target = tmp_path / "CLAUDE.md"
    target.write_text("old content\n", encoding="utf-8")

    result = write_context_file(target, "new content\n", dry_run=False)

    assert result["action"] == "updated"
    assert result["changed"] is True
    assert result["backup_path"] is not None
    backup = Path(result["backup_path"])
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "old content\n"
    assert target.read_text(encoding="utf-8") == "new content\n"


def test_write_context_file_should_not_write_in_dry_run(tmp_path: Path):
    target = tmp_path / "AGENTS.md"
    target.write_text("original\n", encoding="utf-8")

    result = write_context_file(target, "changed\n", dry_run=True)

    assert result == {"action": "planned", "changed": True, "backup_path": None}
    assert target.read_text(encoding="utf-8") == "original\n"
    assert not list(tmp_path.glob("AGENTS.md.bak-*"))


def test_inspect_context_file_should_detect_corruption_and_version_drift(tmp_path: Path):
    corrupted = tmp_path / "CLAUDE.md"
    corrupted.write_text(f"{MANAGED_BLOCK_START}\nno end\n", encoding="utf-8")

    drifted = tmp_path / "AGENTS.md"
    drifted.write_text(build_default_agents_managed_block("v1.0.0"), encoding="utf-8")

    corrupted_info = inspect_context_file(corrupted, "v1.2.3")
    drifted_info = inspect_context_file(drifted, "v1.2.3")

    assert corrupted_info["marker_integrity"] == "corrupted"
    assert drifted_info["marker_integrity"] == "ok"
    assert drifted_info["managed_version"] == "v1.0.0"
    assert drifted_info["version_drift"] is True


def test_setup_context_files_should_create_both_files_with_markers(tmp_path: Path):
    payload = setup_context_files(
        tmp_path,
        runtime_version="v1.2.3",
        dry_run=False,
        force=False,
        with_claude=True,
        with_agents=True,
    )

    assert len(payload["actions"]) == 2

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    for content in (claude, agents):
        assert MANAGED_BLOCK_START in content
        assert MANAGED_BLOCK_END in content
        assert "BEACON:VERSION:v1.2.3" in content
    assert "docs/beacon/<version>/` is the canonical source of truth" in claude
    assert "docs/product/<version>/` is a compatibility mirror" in claude
    assert "Use `docs/beacon/<version>/` as the canonical delivery tree." in agents
    assert "Treat `docs/product/<version>/` as a compatibility mirror." in agents


def test_verify_context_files_should_return_expected_checks_and_statuses(tmp_path: Path):
    setup_context_files(
        tmp_path,
        runtime_version="v1.2.3",
        dry_run=False,
        force=False,
        with_claude=True,
        with_agents=True,
    )

    ok_payload = verify_context_files(tmp_path, runtime_version="v1.2.3", strict=True)
    check_names = [check["name"] for check in ok_payload["checks"]]
    check_statuses = {check["name"]: check["status"] for check in ok_payload["checks"]}

    assert check_names == [
        "context_files_presence",
        "managed_block_integrity",
        "managed_block_version_drift",
    ]
    assert check_statuses == {
        "context_files_presence": "pass",
        "managed_block_integrity": "pass",
        "managed_block_version_drift": "pass",
    }

    drift_payload = verify_context_files(tmp_path, runtime_version="v9.9.9", strict=False)
    drift_statuses = {check["name"]: check["status"] for check in drift_payload["checks"]}
    assert drift_statuses["managed_block_version_drift"] == "warn"
