"""
Tests for CircuitBreaker.

Verifies stuck loop detection logic.
"""

import pytest

from beacon.utils.circuit_breaker import CircuitBreaker


class TestCircuitBreaker:
    """Test suite for CircuitBreaker."""

    def test_initialization_defaults(self):
        """Test default initialization."""
        breaker = CircuitBreaker()
        assert breaker.no_progress_threshold == 3
        assert breaker.same_error_threshold == 3
        assert breaker.output_decline_threshold == 3
        assert breaker.min_output_length == 50

    def test_initialization_custom(self):
        """Test custom initialization."""
        breaker = CircuitBreaker(
            no_progress_threshold=5,
            same_error_threshold=4,
            output_decline_threshold=2,
            min_output_length=100,
        )
        assert breaker.no_progress_threshold == 5
        assert breaker.same_error_threshold == 4
        assert breaker.output_decline_threshold == 2
        assert breaker.min_output_length == 100

    def test_no_progress_detection(self):
        """Test detection of no progress."""
        # Use very high decline threshold to disable that check
        breaker = CircuitBreaker(
            no_progress_threshold=3,
            output_decline_threshold=10,
        )

        # First iteration - no stuck
        is_stuck, reason = breaker.detect_stuck(1, {"output": "Working on task A"})
        assert is_stuck is False

        # Second iteration - same output
        is_stuck, reason = breaker.detect_stuck(2, {"output": "Working on task A"})
        assert is_stuck is False

        # Third iteration - still same output, should detect stuck
        is_stuck, reason = breaker.detect_stuck(3, {"output": "Working on task A"})
        assert is_stuck is True
        assert reason == "no_progress"

    def test_repeated_error_detection(self):
        """Test detection of repeated errors."""
        breaker = CircuitBreaker(same_error_threshold=3)

        # First error
        is_stuck, reason = breaker.detect_stuck(
            1, {"output": "output", "error": "Connection failed"}
        )
        assert is_stuck is False

        # Second error - same
        is_stuck, reason = breaker.detect_stuck(
            2, {"output": "output", "error": "Connection failed"}
        )
        assert is_stuck is False

        # Third error - same, should detect stuck
        is_stuck, reason = breaker.detect_stuck(
            3, {"output": "output", "error": "Connection failed"}
        )
        assert is_stuck is True
        assert reason == "repeated_error"

    def test_output_decline_detection(self):
        """Test detection of declining output."""
        breaker = CircuitBreaker(output_decline_threshold=3, min_output_length=50)

        # Declining outputs
        is_stuck, reason = breaker.detect_stuck(1, {"output": "A" * 100})
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(2, {"output": "A" * 80})
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(3, {"output": "A" * 60})
        assert is_stuck is True
        assert reason == "output_decline"

    def test_output_too_short_detection(self):
        """Test detection of consistently short outputs."""
        breaker = CircuitBreaker(output_decline_threshold=3, min_output_length=50)

        # All outputs too short
        is_stuck, reason = breaker.detect_stuck(1, {"output": "short"})
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(2, {"output": "short"})
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(3, {"output": "short"})
        assert is_stuck is True
        assert reason == "output_decline"

    def test_no_stuck_with_varying_output(self):
        """Test no stuck detection with varying output."""
        breaker = CircuitBreaker(
            no_progress_threshold=3,
            output_decline_threshold=10,
        )

        is_stuck, reason = breaker.detect_stuck(1, {"output": "Working on task A"})
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(2, {"output": "Working on task B"})
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(3, {"output": "Working on task C"})
        assert is_stuck is False

    def test_no_stuck_with_different_errors(self):
        """Test no stuck detection with different errors."""
        breaker = CircuitBreaker(
            same_error_threshold=3,
            output_decline_threshold=10,
        )

        is_stuck, reason = breaker.detect_stuck(
            1, {"output": "output A", "error": "Error A"}
        )
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(
            2, {"output": "output B", "error": "Error B"}
        )
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(
            3, {"output": "output C", "error": "Error C"}
        )
        assert is_stuck is False

    def test_reset(self):
        """Test reset functionality."""
        breaker = CircuitBreaker(no_progress_threshold=3)

        # Build up history
        breaker.detect_stuck(1, {"output": "same"})
        breaker.detect_stuck(2, {"output": "same"})

        assert len(breaker.progress_history) == 2

        # Reset
        breaker.reset()
        assert len(breaker.progress_history) == 0
        assert len(breaker.error_history) == 0
        assert len(breaker.output_lengths) == 0

    def test_dict_text_handling(self):
        """Test handling of dict as text."""
        breaker = CircuitBreaker(no_progress_threshold=3)

        output_dict = {"message": "working"}

        is_stuck, reason = breaker.detect_stuck(1, {"output": output_dict})
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(2, {"output": output_dict})
        assert is_stuck is False

        is_stuck, reason = breaker.detect_stuck(3, {"output": output_dict})
        assert is_stuck is True

    def test_error_normalization(self):
        """Test error message normalization."""
        breaker = CircuitBreaker(same_error_threshold=3)

        # Same error with different casing/whitespace
        breaker.detect_stuck(1, {"output": "out", "error": "  Connection Failed  "})
        breaker.detect_stuck(2, {"output": "out", "error": "connection failed"})
        is_stuck, reason = breaker.detect_stuck(
            3, {"output": "out", "error": "CONNECTION FAILED"}
        )

        assert is_stuck is True
        assert reason == "repeated_error"
