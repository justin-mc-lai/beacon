"""
Exit detection with dual-condition gate.

Inspired by ralph-claude-code's exit detection pattern:
- Natural language completion indicators
- Explicit EXIT_SIGNAL flag
- Dual-condition gate: BOTH must be true
"""

import re
from typing import Any, Optional


class ExitDetector:
    """Multi-layer exit detection for iterative workflows."""

    def __init__(
        self,
        completion_threshold: int = 2,
        completion_patterns: Optional[list[str]] = None,
    ):
        """
        Initialize exit detector.

        Args:
            completion_threshold: Minimum completion indicators needed
            completion_patterns: Regex patterns indicating completion
        """
        self.completion_threshold = completion_threshold
        self.completion_indicators = 0
        self.exit_signal = False

        # Default completion patterns (can be overridden)
        self.completion_patterns = completion_patterns or [
            r"project\s+complete",
            r"task.*complete",
            r"all\s+tasks?\s+(?:are\s+)?(?:done|complete|finished)",
            r"all\s+work\s+(?:is\s+)?done",
            r"implementation\s+(?:is\s+)?complete",
            r"ready\s+for\s+(?:review|qa|release)",
            r"no\s+(?:more|further|additional)\s+work\s+(?:needed|required)",
            r"successfully\s+(?:completed|finished|implemented)",
            r"验证通过",  # Chinese: verification passed
            r"实现完成",  # Chinese: implementation complete
            r"任务完成",  # Chinese: task complete
            r"所有任务完成",  # Chinese: all tasks complete
            r"所有工作.*完成",  # Chinese: all work complete
        ]

    def check_exit(
        self,
        result: dict[str, Any],
        text_key: str = "output",
    ) -> tuple[bool, str]:
        """
        Check if exit conditions are met.

        Args:
            result: Result dictionary from iteration
            text_key: Key to extract text from result

        Returns:
            (should_exit, reason)
        """
        # Reset indicators for this check
        self.completion_indicators = 0

        # Extract text content
        text = result.get(text_key, "")
        if isinstance(text, dict):
            text = str(text)

        # Check natural language patterns
        for pattern in self.completion_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                self.completion_indicators += 1

        # Check explicit signal
        self.exit_signal = result.get("EXIT_SIGNAL", False)

        # Dual-condition gate
        if self.completion_indicators >= self.completion_threshold and self.exit_signal:
            return (
                True,
                f"Exit conditions met: {self.completion_indicators} indicators + EXIT_SIGNAL",
            )

        # Build reason for not exiting
        reasons = []
        if self.completion_indicators < self.completion_threshold:
            reasons.append(
                f"indicators={self.completion_indicators}/{self.completion_threshold}"
            )
        if not self.exit_signal:
            reasons.append("EXIT_SIGNAL=False")

        return (False, f"Continue: {', '.join(reasons)}")

    def add_pattern(self, pattern: str) -> None:
        """Add a custom completion pattern."""
        self.completion_patterns.append(pattern)

    def reset(self) -> None:
        """Reset detector state."""
        self.completion_indicators = 0
        self.exit_signal = False
