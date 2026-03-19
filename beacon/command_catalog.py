"""Canonical Beacon subcommand catalog."""

from __future__ import annotations

CORE_COMMANDS = (
    "think",
    "user-story",
    "prd",
    "prototype",
    "test-case",
    "workflow",
    "auto-test",
    "gate",
    "release",
)

SUPPORT_COMMANDS = (
    "ask",
    "status",
    "report",
    "review",
    "doctor",
    "feedback",
    "remember",
    "recall",
    "resume",
    "version",
    "evolution-summary",
    "init",
    "test-progress",
    "debug",
)

LABS_COMMANDS = (
    "analyze",
    "api-design",
    "brainstorm",
    "data-dictionary",
    "design",
    "jtbd",
    "kano",
    "moscow",
    "persona",
    "roadmap",
    "ui-spec",
    "wireframe",
)

BRIDGE_COMMANDS = (
    "run",
    "team",
    "ralph-bridge",
)

DEPRECATED_COMMANDS = (
    "prompt",
    "save",
    "work",
)

DEFAULT_USER_SURFACE = CORE_COMMANDS + SUPPORT_COMMANDS
ADVANCED_SURFACE = LABS_COMMANDS + BRIDGE_COMMANDS + DEPRECATED_COMMANDS

# Keep the canonical ordering stable for auto-generated docs/tests.
SUPPORTED_SUBCOMMANDS = (
    "ask",
    "analyze",
    "api-design",
    "auto-test",
    "brainstorm",
    "data-dictionary",
    "debug",
    "design",
    "doctor",
    "evolution-summary",
    "feedback",
    "gate",
    "init",
    "jtbd",
    "kano",
    "moscow",
    "persona",
    "prototype",
    "prompt",
    "prd",
    "ralph-bridge",
    "recall",
    "release",
    "remember",
    "report",
    "review",
    "resume",
    "roadmap",
    "run",
    "save",
    "status",
    "team",
    "test-case",
    "test-progress",
    "think",
    "ui-spec",
    "user-story",
    "version",
    "wireframe",
    "work",
    "workflow",
)
