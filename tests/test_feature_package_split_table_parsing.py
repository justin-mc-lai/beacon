"""Regression for issue #28: contract tables split by a blank line lost rows.

``_extract_test_rows`` / ``_extract_ac_rows`` / ``_extract_evidence_rows`` used
to ``break`` on the first non-table line after a table started. A ``tests.md``
whose table is visually split into segments therefore yielded only the first
segment, and the QA gate scored a silently narrowed contract as a full verdict
(a false-green class of bug).

A blank line now pauses the segment; real prose still ends the scan, so
unrelated tables further down a document are never mistaken for the contract.
"""

from __future__ import annotations

from beacon.utils.feature_package import (
    _extract_ac_rows,
    _extract_evidence_rows,
    _extract_test_rows,
)

TC_HEADER = "| TC ID | AC ID | Command | Assertion |\n|---|---|---|---|\n"


def _tc(tc_id: str, ac_id: str, command: str) -> str:
    return f"| {tc_id} | {ac_id} | `{command}` | verify {tc_id} |\n"


def test_blank_line_between_segments_keeps_every_row() -> None:
    markdown = TC_HEADER + _tc("TC-001", "AC-001", "true") + "\n" + _tc("TC-002", "AC-002", "true") + _tc("TC-003", "AC-003", "true")

    rows = _extract_test_rows(markdown)

    assert [row["tc_id"] for row in rows] == ["TC-001", "TC-002", "TC-003"]
    assert all(row["command"] for row in rows)


def test_prose_ends_the_scan_so_later_tables_are_not_swallowed() -> None:
    markdown = (
        TC_HEADER
        + _tc("TC-001", "AC-001", "true")
        + "\n## Notes\n\nSome prose that is not part of the contract.\n\n"
        + TC_HEADER
        + _tc("TC-999", "AC-999", "true")
    )

    rows = _extract_test_rows(markdown)

    assert [row["tc_id"] for row in rows] == ["TC-001"]


def test_segment_with_its_own_header_reanchors_columns() -> None:
    markdown = (
        TC_HEADER
        + _tc("TC-001", "AC-001", "first")
        + "\n"
        + "| TC ID | AC ID | Command | Assertion |\n|---|---|---|---|\n"
        + _tc("TC-002", "AC-002", "second")
    )

    rows = _extract_test_rows(markdown)

    assert [(row["tc_id"], row["command"]) for row in rows] == [
        ("TC-001", "`first`"),
        ("TC-002", "`second`"),
    ]


def test_ac_rows_survive_a_split_table() -> None:
    markdown = (
        "| AC ID | Theme | Description |\n|---|---|---|\n"
        "| AC-001 | a | one |\n\n| AC-002 | b | two |\n"
    )

    assert [row["ac_id"] for row in _extract_ac_rows(markdown)] == ["AC-001", "AC-002"]


def test_evidence_rows_survive_a_split_table() -> None:
    markdown = (
        "| Surface | Authority | Canonical Artifact | Status | Route |\n"
        "|---|---|---|---|---|\n"
        "| implement | requirement_truth | a.json | verified | qa |\n\n"
        "| implement | requirement_truth | b.json | verified | qa |\n"
    )

    rows = _extract_evidence_rows(markdown)

    assert [row["canonical_artifact"] for row in rows] == ["a.json", "b.json"]


def test_single_segment_table_is_unchanged() -> None:
    markdown = TC_HEADER + _tc("TC-001", "AC-001", "true") + _tc("TC-002", "AC-002", "true")

    rows = _extract_test_rows(markdown)

    assert [row["tc_id"] for row in rows] == ["TC-001", "TC-002"]
