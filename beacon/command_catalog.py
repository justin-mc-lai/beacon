"""Canonical Beacon subcommand catalog."""

from __future__ import annotations

CORE_COMMANDS = (
    "prd",
    "user-story",
    "test-case",
    "prototype",
    "implement",
    "qa",
    "release",
)

SUPPORT_COMMANDS = (
    "board",
    "help",
    "status",
    "doctor",
    "archive",
    "ask",
    "skill",
    "profile",
    "orchestrate",
    "report",
    "review",
    "real-project-validation",
    "friction-intake",
    "feedback",
    "freeze",
    "reopen",
    "remember",
    "recall",
    "resume",
    "version",
    "evolution-summary",
    "init",
    "test-progress",
    "debug",
)

COMPAT_COMMANDS = (
    "think",
    "workflow",
    "gate",
    "verify",
    "auto-test",
)

LABS_COMMANDS = (
    "analyze",
    "api-design",
    "brainstorm",
    "data-dictionary",
    "design",
    "jtbd",
    "kano",
    "lighthouse",
    "memory-friction-evolution",
    "moscow",
    "persona",
    "roadmap",
    "ui-spec",
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
ADVANCED_SURFACE = LABS_COMMANDS + BRIDGE_COMMANDS + DEPRECATED_COMMANDS + COMPAT_COMMANDS

# Keep the canonical ordering stable for auto-generated docs/tests.
SUPPORTED_SUBCOMMANDS = (
    "ask",
    "analyze",
    "archive",
    "api-design",
    "auto-test",
    "board",
    "qa",
    "brainstorm",
    "data-dictionary",
    "debug",
    "design",
    "doctor",
    "evolution-summary",
    "feedback",
    "friction-intake",
    "freeze",
    "help",
    "gate",
    "implement",
    "init",
    "jtbd",
    "kano",
    "lighthouse",
    "memory-friction-evolution",
    "moscow",
    "persona",
    "prototype",
    "prompt",
    "profile",
    "prd",
    "qa",
    "orchestrate",
    "ralph-bridge",
    "real-project-validation",
    "recall",
    "release",
    "reopen",
    "remember",
    "report",
    "review",
    "resume",
    "roadmap",
    "run",
    "save",
    "skill",
    "status",
    "team",
    "test-case",
    "test-progress",
    "think",
    "ui-spec",
    "user-story",
    "verify",
    "version",
    "work",
    "workflow",
)
