"""
Tests for ExitDetector.

Verifies dual-condition exit detection logic.
"""

import pytest

from beacon.utils.exit_detector import ExitDetector


class TestExitDetector:
    """Test suite for ExitDetector."""

    def test_initialization_defaults(self):
        """Test default initialization."""
        detector = ExitDetector()
        assert detector.completion_threshold == 2
        assert detector.completion_indicators == 0
        assert detector.exit_signal is False
        assert len(detector.completion_patterns) > 0

    def test_initialization_custom(self):
        """Test custom initialization."""
        patterns = [r"custom\s+pattern"]
        detector = ExitDetector(completion_threshold=3, completion_patterns=patterns)
        assert detector.completion_threshold == 3
        assert detector.completion_patterns == patterns

    def test_exit_with_both_conditions_met(self):
        """Test exit when both conditions are met."""
        detector = ExitDetector(completion_threshold=2)
        result = {
            "output": "Project complete. All tasks are done.",
            "EXIT_SIGNAL": True,
        }

        should_exit, reason = detector.check_exit(result)
        assert should_exit is True
        assert "EXIT_SIGNAL" in reason
        assert detector.completion_indicators >= 2

    def test_no_exit_without_exit_signal(self):
        """Test no exit when EXIT_SIGNAL is missing."""
        detector = ExitDetector(completion_threshold=2)
        result = {
            "output": "Project complete. All tasks are done.",
            "EXIT_SIGNAL": False,
        }

        should_exit, reason = detector.check_exit(result)
        assert should_exit is False
        assert "EXIT_SIGNAL=False" in reason

    def test_no_exit_without_enough_indicators(self):
        """Test no exit when not enough completion indicators."""
        detector = ExitDetector(completion_threshold=2)
        result = {
            "output": "Still working on the project.",
            "EXIT_SIGNAL": True,
        }

        should_exit, reason = detector.check_exit(result)
        assert should_exit is False
        assert "indicators=" in reason

    def test_pattern_matching_case_insensitive(self):
        """Test pattern matching is case insensitive."""
        detector = ExitDetector(completion_threshold=1)
        result = {
            "output": "PROJECT COMPLETE",
            "EXIT_SIGNAL": True,
        }

        should_exit, reason = detector.check_exit(result)
        assert should_exit is True

    def test_chinese_patterns(self):
        """Test Chinese completion patterns."""
        detector = ExitDetector(completion_threshold=1)
        result = {
            "output": "实现完成，所有任务完成",
            "EXIT_SIGNAL": True,
        }

        should_exit, reason = detector.check_exit(result)
        assert should_exit is True

    def test_add_custom_pattern(self):
        """Test adding custom patterns."""
        detector = ExitDetector(completion_threshold=1)
        detector.add_pattern(r"custom\s+done")

        result = {
            "output": "custom done",
            "EXIT_SIGNAL": True,
        }

        should_exit, reason = detector.check_exit(result)
        assert should_exit is True

    def test_reset(self):
        """Test reset functionality."""
        detector = ExitDetector()
        result = {
            "output": "Project complete",
            "EXIT_SIGNAL": True,
        }

        detector.check_exit(result)
        assert detector.completion_indicators > 0
        assert detector.exit_signal is True

        detector.reset()
        assert detector.completion_indicators == 0
        assert detector.exit_signal is False

    def test_dict_text_handling(self):
        """Test handling of dict as text."""
        detector = ExitDetector(completion_threshold=1)
        result = {
            "output": {"message": "project complete"},
            "EXIT_SIGNAL": True,
        }

        should_exit, reason = detector.check_exit(result)
        assert should_exit is True
