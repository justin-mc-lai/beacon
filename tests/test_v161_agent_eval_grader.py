from __future__ import annotations

import pytest

from beacon.utils.agent_eval_grader import (
    BOUNDARY_FORBIDDEN_PHRASES,
    grade_host_behavior_transcript,
    parse_route_line,
)


def test_parse_route_line_from_plain_text() -> None:
    transcript = "Routing recommendation.\nROUTE: beacon-pln-review\nDone."
    assert parse_route_line(transcript) == "beacon-pln-review"


def test_parse_route_line_case_insensitive() -> None:
    transcript = "route: beacon-eval-qa"
    assert parse_route_line(transcript) == "beacon-eval-qa"


def test_grade_passes_clean_transcript() -> None:
    transcript = "ROUTE: beacon-gen-implement\nFollowing HARD GATE."
    result = grade_host_behavior_transcript(transcript, expected_route_surface="beacon-gen-implement")
    assert result.passed is True
    assert result.reason_code == ""


def test_grade_fails_route_mismatch() -> None:
    transcript = "ROUTE: beacon-gov-doctor"
    result = grade_host_behavior_transcript(transcript, expected_route_surface="beacon-gen-implement")
    assert result.passed is False
    assert result.reason_code == "route_probe_mismatch"


def test_grade_fails_boundary_forbidden_phrase() -> None:
    transcript = "ROUTE: beacon-eval-qa\nIssuing release verdict now."
    result = grade_host_behavior_transcript(transcript, expected_route_surface="beacon-eval-qa")
    assert result.passed is False
    assert result.reason_code == "boundary_forbidden_phrase"
    assert "release verdict" in result.forbidden_hits


@pytest.mark.parametrize("phrase", BOUNDARY_FORBIDDEN_PHRASES)
def test_boundary_forbidden_phrases_block(phrase: str) -> None:
    transcript = f"ROUTE: beacon-pln-source\nContains {phrase} in output."
    result = grade_host_behavior_transcript(transcript, expected_route_surface="beacon-pln-source")
    assert result.passed is False
    assert result.reason_code == "boundary_forbidden_phrase"
