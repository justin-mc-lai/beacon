"""
Circuit breaker for detecting stuck loops.

Inspired by ralph-claude-code's circuit breaker pattern:
- No progress detection
- Repeated error detection
- Output decline detection
"""

from collections import deque
from typing import Any


class CircuitBreaker:
    """Detect stuck loops and prevent infinite iterations."""

    def __init__(
        self,
        no_progress_threshold: int = 3,
        same_error_threshold: int = 3,
        output_decline_threshold: int = 3,
        min_output_length: int = 50,
    ):
        """
        Initialize circuit breaker.

        Args:
            no_progress_threshold: Iterations with no progress before breaking
            same_error_threshold: Same error repetitions before breaking
            output_decline_threshold: Declining outputs before breaking
            min_output_length: Minimum output length to consider valid
        """
        self.no_progress_threshold = no_progress_threshold
        self.same_error_threshold = same_error_threshold
        self.output_decline_threshold = output_decline_threshold
        self.min_output_length = min_output_length

        # State tracking
        self.progress_history: deque[str] = deque(maxlen=no_progress_threshold)
        self.error_history: deque[str] = deque(maxlen=same_error_threshold)
        self.output_lengths: deque[int] = deque(maxlen=output_decline_threshold)

    def detect_stuck(
        self,
        iteration: int,
        result: dict[str, Any],
        text_key: str = "output",
        error_key: str = "error",
    ) -> tuple[bool, str]:
        """
        Check if loop is stuck.

        Args:
            iteration: Current iteration number
            result: Result dictionary from iteration
            text_key: Key to extract text from result
            error_key: Key to extract error from result

        Returns:
            (is_stuck, reason)
        """
        # Extract content
        text = result.get(text_key, "")
        error = result.get(error_key, "")

        if isinstance(text, dict):
            text = str(text)
        if isinstance(error, dict):
            error = str(error)

        # Track all states first
        no_progress = self._track_progress(text)
        repeated_error = error and self._track_error(error)
        output_declining = self._track_output_length(text)

        # Check in priority order: error > decline > no progress
        # This prevents false positives when output is intentionally same
        if repeated_error:
            return (True, "repeated_error")

        if output_declining:
            return (True, "output_decline")

        if no_progress:
            return (True, "no_progress")

        return (False, "")

    def _track_progress(self, text: str) -> bool:
        """Track progress and check if stuck."""
        content = text.strip()
        self.progress_history.append(content)

        if len(self.progress_history) < self.no_progress_threshold:
            return False

        return len(set(self.progress_history)) == 1

    def _track_error(self, error: str) -> bool:
        """Track errors and check if repeating."""
        error_normalized = error.strip().lower()
        self.error_history.append(error_normalized)

        if len(self.error_history) < self.same_error_threshold:
            return False

        return len(set(self.error_history)) == 1

    def _track_output_length(self, text: str) -> bool:
        """Track output length and check if declining."""
        length = len(text.strip())
        self.output_lengths.append(length)

        if len(self.output_lengths) < self.output_decline_threshold:
            return False

        lengths_list = list(self.output_lengths)

        # Check if all outputs are too short
        if all(l < self.min_output_length for l in lengths_list):
            return True

        # Check if lengths are strictly declining (each smaller than previous)
        # Must have actual decline, not just same length
        is_declining = all(
            lengths_list[i] > lengths_list[i + 1]
            for i in range(len(lengths_list) - 1)
        )

        return is_declining

    def reset(self) -> None:
        """Reset circuit breaker state."""
        self.progress_history.clear()
        self.error_history.clear()
        self.output_lengths.clear()
