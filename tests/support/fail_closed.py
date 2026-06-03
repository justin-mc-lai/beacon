"""Shared assertions for post-cutover fail-closed CLI behavior in tests."""

from __future__ import annotations

from typer.testing import Result


def assert_cli_exit_blocked(
    result: Result,
    *,
    must_contain: str | tuple[str, ...] = (),
) -> None:
    """Assert a Typer CLI invocation failed closed with exit code 2."""
    assert result.exit_code == 2, result.stdout
    if not must_contain:
        return
    fragments = (must_contain,) if isinstance(must_contain, str) else must_contain
    for fragment in fragments:
        assert fragment in result.stdout, result.stdout


def assert_missing_prd_truth(result: Result, *, feature: str | None = None) -> None:
    """Assert user-story/test-case style commands blocked on missing PRD truth."""
    fragments: list[str] = ["Missing PRD truth"]
    if feature:
        fragments.append(feature)
    assert_cli_exit_blocked(result, must_contain=tuple(fragments))


def assert_prototype_missing_requirement_truth(result: Result) -> None:
    """Assert prototype create blocked before requirement truth is materialized."""
    assert_cli_exit_blocked(
        result,
        must_contain=(
            "Missing source docs: prototype requires requirement truth",
            "missing:",
        ),
    )
