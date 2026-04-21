"""Tests for beacon/commands/implement/team.py"""

import pytest
from beacon.commands.implement.team import (
    validate_team_mode,
)


def test_validate_team_mode_explicit():
    """Test team mode validation with explicit mode."""
    assert validate_team_mode("team", "", "") is True


def test_validate_team_mode_codex_subagents():
    """Test team mode validation with codex-subagents."""
    assert validate_team_mode("single", "codex-subagents", "") is True


def test_validate_team_mode_claude_code():
    """Test team mode validation with claude-code runtime."""
    assert validate_team_mode("single", "", "claude-code") is True


def test_validate_team_mode_single():
    """Test team mode validation with single mode."""
    assert validate_team_mode("single", "regular", "file") is False
