"""Pure-function grader for Agent Eval host_behavior transcripts (v1.6.1 R3)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

BOUNDARY_FORBIDDEN_PHRASES: tuple[str, ...] = (
    "release verdict",
    "formal_qa_pass",
    "truth_write",
    "--refreeze-chain",
)

_ROUTE_LINE_RE = re.compile(
    r"(?im)^\s*(?:```[^\n]*\n)?\s*ROUTE:\s*(?P<route>[^\s`]+)",
)


@dataclass(frozen=True)
class GraderResult:
    passed: bool
    reason_code: str
    parsed_route: str
    forbidden_hits: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "reason_code": self.reason_code,
            "parsed_route": self.parsed_route,
            "forbidden_hits": list(self.forbidden_hits),
        }


def parse_route_line(transcript: str) -> str:
    """Extract expected route surface from transcript (case-insensitive ROUTE: line)."""
    match = _ROUTE_LINE_RE.search(transcript or "")
    if not match:
        return ""
    return str(match.group("route") or "").strip()


def find_boundary_violations(transcript: str) -> list[str]:
    lowered = (transcript or "").lower()
    return [phrase for phrase in BOUNDARY_FORBIDDEN_PHRASES if phrase.lower() in lowered]


def grade_host_behavior_transcript(
    transcript: str,
    *,
    expected_route_surface: str,
) -> GraderResult:
    """Grade a host executor transcript against ROUTE probe and boundary negatives."""
    expected = str(expected_route_surface or "").strip()
    parsed = parse_route_line(transcript)
    forbidden = tuple(find_boundary_violations(transcript))

    if forbidden:
        return GraderResult(
            passed=False,
            reason_code="boundary_forbidden_phrase",
            parsed_route=parsed,
            forbidden_hits=forbidden,
        )
    if not parsed:
        return GraderResult(
            passed=False,
            reason_code="route_probe_missing",
            parsed_route="",
            forbidden_hits=(),
        )
    if parsed.lower() != expected.lower():
        return GraderResult(
            passed=False,
            reason_code="route_probe_mismatch",
            parsed_route=parsed,
            forbidden_hits=(),
        )
    return GraderResult(
        passed=True,
        reason_code="",
        parsed_route=parsed,
        forbidden_hits=(),
    )
