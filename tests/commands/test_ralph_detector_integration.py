"""Integration tests for Ralph loop detectors in implement command."""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from beacon.utils.circuit_breaker import CircuitBreaker
from beacon.utils.exit_detector import ExitDetector


class TestRalphDetectorIntegration(unittest.TestCase):
    """Test ExitDetector and CircuitBreaker integration in Ralph loop."""

    def test_circuit_breaker_triggers_on_repeated_errors(self):
        """Circuit breaker should trigger after repeated errors."""
        breaker = CircuitBreaker(same_error_threshold=3)

        # Simulate 3 rounds with same error
        for i in range(1, 4):
            result = {"output": f"Attempt {i}", "error": "Connection timeout"}
            is_stuck, reason = breaker.detect_stuck(i, result)

            if i < 3:
                self.assertFalse(is_stuck, f"Should not trigger on iteration {i}")
            else:
                self.assertTrue(is_stuck, "Should trigger on 3rd error")
                self.assertEqual(reason, "repeated_error")

    def test_exit_detector_requires_both_conditions(self):
        """Exit detector should require both indicators and EXIT_SIGNAL."""
        detector = ExitDetector(completion_threshold=2)

        # Only indicators, no signal
        result1 = {
            "output": "Task complete. All work is done.",
            "EXIT_SIGNAL": False,
        }
        should_exit, _ = detector.check_exit(result1)
        self.assertFalse(should_exit, "Should not exit without EXIT_SIGNAL")

        # Only signal, no indicators
        result2 = {
            "output": "Still working on it",
            "EXIT_SIGNAL": True,
        }
        should_exit, _ = detector.check_exit(result2)
        self.assertFalse(should_exit, "Should not exit without indicators")

        # Both conditions met
        result3 = {
            "output": "Task complete. All work is done.",
            "EXIT_SIGNAL": True,
        }
        should_exit, _ = detector.check_exit(result3)
        self.assertTrue(should_exit, "Should exit with both conditions")

    def test_circuit_breaker_priority_over_exit_detector(self):
        """Circuit breaker should be checked before exit detector."""
        breaker = CircuitBreaker(same_error_threshold=2)
        detector = ExitDetector(completion_threshold=1)

        # Round 1: error
        result1 = {"output": "Task complete", "error": "Failed", "EXIT_SIGNAL": True}
        is_stuck, _ = breaker.detect_stuck(1, result1)
        self.assertFalse(is_stuck)

        # Round 2: same error (should trigger breaker)
        result2 = {"output": "Task complete", "error": "Failed", "EXIT_SIGNAL": True}
        is_stuck, reason = breaker.detect_stuck(2, result2)
        self.assertTrue(is_stuck, "Circuit breaker should trigger")
        self.assertEqual(reason, "repeated_error")

        # Exit detector would also trigger, but breaker takes priority
        should_exit, _ = detector.check_exit(result2)
        self.assertTrue(should_exit, "Exit detector would trigger")

        # In real integration, circuit breaker check comes first and breaks the loop

    def test_no_progress_detection_with_varying_errors(self):
        """No progress should be detected even with different errors."""
        breaker = CircuitBreaker(no_progress_threshold=3, output_decline_threshold=10)

        # Same output, different errors
        for i in range(1, 4):
            result = {"output": "Working on task", "error": f"Error {i}"}
            is_stuck, reason = breaker.detect_stuck(i, result)

            if i < 3:
                self.assertFalse(is_stuck)
            else:
                self.assertTrue(is_stuck)
                self.assertEqual(reason, "no_progress")

    def test_exit_detector_with_chinese_patterns(self):
        """Exit detector should work with Chinese completion patterns."""
        detector = ExitDetector(completion_threshold=2)

        result = {
            "output": "任务完成。所有工作已完成。",
            "EXIT_SIGNAL": True,
        }
        should_exit, reason = detector.check_exit(result)
        self.assertTrue(should_exit)
        self.assertIn("EXIT_SIGNAL", reason)

    def test_detector_reset_between_features(self):
        """Detectors should be reset for each new feature."""
        breaker = CircuitBreaker(same_error_threshold=3)
        detector = ExitDetector(completion_threshold=2)

        # Feature 1: trigger circuit breaker
        for i in range(1, 4):
            breaker.detect_stuck(i, {"output": "out", "error": "Error"})

        is_stuck, _ = breaker.detect_stuck(3, {"output": "out", "error": "Error"})
        self.assertTrue(is_stuck)

        # Reset for Feature 2
        breaker.reset()
        detector.reset()

        # Should not trigger immediately
        is_stuck, _ = breaker.detect_stuck(1, {"output": "out", "error": "Error"})
        self.assertFalse(is_stuck)


if __name__ == "__main__":
    unittest.main()
