"""Tests for beacon/commands/implement/ralph.py"""

import pytest
from beacon.commands.implement.ralph import (
    refresh_ralph_state_after_resume,
    render_ralph_round_markdown,
    build_ralph_summary,
    render_ralph_summary_markdown,
)


def test_render_ralph_round_markdown():
    """Test Ralph round markdown rendering."""
    payload = {
        "round_index": 1,
        "status": "completed",
        "timestamp": "2026-04-21T16:00:00Z",
        "result": {"success": True},
        "verification": {"passed": True}
    }

    markdown = render_ralph_round_markdown(payload)

    assert "# Ralph Round 1" in markdown
    assert "**Status**: completed" in markdown
    assert "2026-04-21T16:00:00Z" in markdown


def test_build_ralph_summary_with_qa():
    """Test Ralph summary building with QA payload."""
    qa_payload = {
        "status": "passed",
        "coverage": 92.5,
        "passed": True
    }

    summary = build_ralph_summary(qa_payload)

    assert summary["ralph_mode"] is True
    assert summary["auto_qa_executed"] is True
    assert summary["qa_status"] == "passed"
    assert summary["qa_coverage"] == 92.5
    assert summary["qa_passed"] is True


def test_build_ralph_summary_without_qa():
    """Test Ralph summary building without QA payload."""
    summary = build_ralph_summary(None)

    assert summary["ralph_mode"] is True
    assert summary["auto_qa_executed"] is False


def test_render_ralph_summary_markdown():
    """Test Ralph summary markdown rendering."""
    payload = {
        "feature": "test-feature",
        "version": "v1.3.6",
        "status": "completed",
        "rounds": [
            {
                "status": "completed",
                "timestamp": "2026-04-21T16:00:00Z"
            }
        ],
        "auto_qa": {
            "executed": True,
            "passed": True,
            "coverage": 92.5
        }
    }

    markdown = render_ralph_summary_markdown(payload)

    assert "# Ralph Implementation Summary" in markdown
    assert "**Feature**: test-feature" in markdown
    assert "**Version**: v1.3.6" in markdown
    assert "## Rounds" in markdown
    assert "## Auto-QA" in markdown
