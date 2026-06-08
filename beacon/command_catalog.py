"""Canonical Beacon subcommand catalog."""

from __future__ import annotations

from typing import Any

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
    "automation",
    "board",
    "code2truth",
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
    "deep",
    "design",
    "hooks",
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

INTERNAL_COMMANDS = (
    "change",
    "prd-bootstrap",
    "labs",
    "bridge",
)

COMMAND_LAYER_ORDER = (
    "current",
    "support",
    "advanced",
    "labs",
    "compat",
    "deprecated",
    "internal",
)

# Keep the canonical ordering stable for auto-generated docs/tests.
SUPPORTED_SUBCOMMANDS = (
    "automation",
    "ask",
    "analyze",
    "archive",
    "api-design",
    "auto-test",
    "board",
    "code2truth",
    "qa",
    "brainstorm",
    "data-dictionary",
    "debug",
    "deep",
    "design",
    "doctor",
    "evolution-summary",
    "feedback",
    "friction-intake",
    "freeze",
    "help",
    "hooks",
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


def command_layers() -> dict[str, str]:
    layers: dict[str, str] = {}
    for name in CORE_COMMANDS:
        layers[name] = "current"
    for name in SUPPORT_COMMANDS:
        layers[name] = "support"
    for name in BRIDGE_COMMANDS:
        layers[name] = "advanced"
    for name in LABS_COMMANDS:
        layers[name] = "labs"
    for name in COMPAT_COMMANDS:
        layers[name] = "compat"
    for name in DEPRECATED_COMMANDS:
        layers[name] = "deprecated"
    for name in INTERNAL_COMMANDS:
        layers[name] = "internal"
    return layers


def command_layer(command: str) -> str:
    return command_layers().get(str(command or "").strip(), "internal")


def commands_by_layer() -> dict[str, tuple[str, ...]]:
    layers = command_layers()
    grouped: dict[str, list[str]] = {layer: [] for layer in COMMAND_LAYER_ORDER}
    for command, layer in layers.items():
        grouped.setdefault(layer, []).append(command)
    return {layer: tuple(items) for layer, items in grouped.items()}


def validate_command_catalog_layers(*, registry_entries: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None) -> dict[str, Any]:
    from beacon.compatibility.registry import command_aliases_from_registry

    layers = command_layers()
    issues: list[str] = []
    unsupported_layers = sorted({layer for layer in layers.values() if layer not in set(COMMAND_LAYER_ORDER)})
    if unsupported_layers:
        issues.extend([f"unsupported_layer:{layer}" for layer in unsupported_layers])
    unclassified = sorted({cmd for cmd in SUPPORTED_SUBCOMMANDS if cmd not in layers})
    issues.extend([f"unclassified_supported_command:{cmd}" for cmd in unclassified])
    default_compat = sorted(set(DEFAULT_USER_SURFACE).intersection(COMPAT_COMMANDS + DEPRECATED_COMMANDS))
    issues.extend([f"default_surface_promotes_compat_or_deprecated:{cmd}" for cmd in default_compat])
    registered_aliases = command_aliases_from_registry(registry_entries)
    missing_aliases = sorted(set(COMPAT_COMMANDS + DEPRECATED_COMMANDS) - registered_aliases)
    issues.extend([f"missing_registry_command_alias:{cmd}" for cmd in missing_aliases])
    return {
        "schema_version": "1.0",
        "status": "pass" if not issues else "blocked",
        "blocked": bool(issues),
        "layers": layers,
        "layer_order": COMMAND_LAYER_ORDER,
        "supported_count": len(SUPPORTED_SUBCOMMANDS),
        "unique_supported_count": len(set(SUPPORTED_SUBCOMMANDS)),
        "issues": issues,
    }
