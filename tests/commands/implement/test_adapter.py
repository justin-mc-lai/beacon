"""Tests for beacon/commands/implement/adapter.py"""

import pytest
from pathlib import Path
from beacon.commands.implement.adapter import (
    discover_adapters,
    resolve_adapter_for_feature,
    build_adapter_context,
    resolve_host_runtime_for_adapter,
    requires_host_native_prechecks,
)


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create .beacon config
    beacon_dir = project_root / ".beacon"
    beacon_dir.mkdir()

    config_file = beacon_dir / "config.json"
    config_file.write_text('{"implement": {"default_runner": "ralph"}}')

    return project_root


def test_discover_adapters(temp_project):
    """Test adapter discovery."""
    adapters = discover_adapters(temp_project)
    assert isinstance(adapters, list)


def test_resolve_adapter_for_feature(temp_project):
    """Test adapter resolution for a feature."""
    adapter = resolve_adapter_for_feature(
        temp_project,
        feature="test-feature",
        runner="ralph"
    )
    # May return None if no adapters configured
    assert adapter is None or isinstance(adapter, dict)


def test_build_adapter_context(temp_project):
    """Test adapter context building."""
    context = build_adapter_context(
        temp_project,
        feature="test-feature",
        version="v1.3.6",
        requirements={"prd": "test.md"}
    )

    assert context["feature"] == "test-feature"
    assert context["version"] == "v1.3.6"
    assert "requirements" in context


def test_resolve_host_runtime_for_adapter():
    """Test host runtime resolution."""
    # Test explicit runtime
    runtime = resolve_host_runtime_for_adapter(
        adapter_id="test",
        adapter={},
        explicit_host_runtime="codex"
    )
    assert runtime == "codex"

    # Test codex-subagents
    runtime = resolve_host_runtime_for_adapter(
        adapter_id="codex-subagents",
        adapter={},
        explicit_host_runtime=None
    )
    assert runtime == "codex"

    # Test claude-code
    runtime = resolve_host_runtime_for_adapter(
        adapter_id="test",
        adapter={"runtime_family": "claude-code"},
        explicit_host_runtime=None
    )
    assert runtime == "claude-code"

    # Test default
    runtime = resolve_host_runtime_for_adapter(
        adapter_id="test",
        adapter={},
        explicit_host_runtime=None
    )
    assert runtime == "file"


def test_requires_host_native_prechecks():
    """Test host-native prechecks requirement."""
    # Test team mode
    assert requires_host_native_prechecks(
        adapter_id="test",
        adapter={},
        mode="team"
    ) is True

    # Test ralph mode
    assert requires_host_native_prechecks(
        adapter_id="test",
        adapter={},
        mode="ralph"
    ) is True

    # Test codex-subagents
    assert requires_host_native_prechecks(
        adapter_id="codex-subagents",
        adapter={},
        mode="single"
    ) is True

    # Test handoff adapter (should not require prechecks)
    assert requires_host_native_prechecks(
        adapter_id="test",
        adapter={"adapter_type": "handoff"},
        mode="single"
    ) is False

    # Test single mode with regular adapter
    assert requires_host_native_prechecks(
        adapter_id="test",
        adapter={},
        mode="single"
    ) is False
