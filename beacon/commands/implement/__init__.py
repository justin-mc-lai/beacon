"""Beacon implement command package.

The package owns the current public ``beacon implement`` Typer surface.  The
CLI implementation lives in ``commands.py`` so imports do not depend on the
historical sibling ``beacon/commands/implement.py`` module.
"""

from __future__ import annotations

from . import adapter, commands, git, ralph, team

from .adapter import (
    build_adapter_context,
    discover_adapters,
    execute_adapter,
    requires_host_native_prechecks,
    resolve_adapter_for_feature,
    resolve_host_runtime_for_adapter,
)
from .commands import app, run_implement_stage
from .git import (
    get_git_commit,
    run_branch_preflight,
    validate_git_workflow,
)
from .ralph import (
    build_ralph_summary,
    refresh_ralph_state_after_resume,
    render_ralph_round_markdown,
    render_ralph_summary_markdown,
)
from .team import (
    validate_team_mode,
    write_team_handoff,
)

__all__ = [
    "app",
    "run_implement_stage",
    "adapter",
    "commands",
    "git",
    "ralph",
    "team",
    "build_adapter_context",
    "discover_adapters",
    "execute_adapter",
    "requires_host_native_prechecks",
    "resolve_adapter_for_feature",
    "resolve_host_runtime_for_adapter",
    "get_git_commit",
    "run_branch_preflight",
    "validate_git_workflow",
    "build_ralph_summary",
    "refresh_ralph_state_after_resume",
    "render_ralph_round_markdown",
    "render_ralph_summary_markdown",
    "validate_team_mode",
    "write_team_handoff",
]
