"""CLI-safe version resolution with the external dual-axis guard (issue #14)."""

from __future__ import annotations

from pathlib import Path

import typer

from beacon.utils.version_defaults import guard_external_docs_axis
from beacon.utils.versioning import resolve_target_version


def resolve_target_version_guarded(
    project_root: Path,
    version: str | None,
    *,
    command_name: str,
    fallback: str = "v1.0.0",
) -> str:
    """Resolve the target docs version and refuse runtime==docs on external repos.

    Raises typer.Exit(2) with a clear message when the external dual-axis guard
    blocks the resolution (external project + docs_version == Beacon runtime).
    """
    try:
        resolved = resolve_target_version(project_root, version, fallback=fallback)
        guard_external_docs_axis(project_root, resolved, command_name=command_name)
        return resolved
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc
