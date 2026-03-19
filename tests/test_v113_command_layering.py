from beacon.command_catalog import (
    ADVANCED_SURFACE,
    BRIDGE_COMMANDS,
    CORE_COMMANDS,
    DEFAULT_USER_SURFACE,
    DEPRECATED_COMMANDS,
    LABS_COMMANDS,
    SUPPORT_COMMANDS,
    SUPPORTED_SUBCOMMANDS,
)
from beacon.utils.intent_router import DEFAULT_ROUTABLE_INTENTS, EXPLICIT_ONLY_COMMAND_HINTS, SUPPORTED_INTENTS


def test_command_catalog_should_expose_layered_groups():
    assert set(CORE_COMMANDS) == {
        "think",
        "user-story",
        "prd",
        "prototype",
        "test-case",
        "workflow",
        "auto-test",
        "gate",
        "release",
    }
    assert "review" in SUPPORT_COMMANDS
    assert "review" in DEFAULT_USER_SURFACE
    assert set(DEFAULT_USER_SURFACE) == set(CORE_COMMANDS) | set(SUPPORT_COMMANDS)
    assert set(ADVANCED_SURFACE) == set(LABS_COMMANDS) | set(BRIDGE_COMMANDS) | set(DEPRECATED_COMMANDS)
    assert set(SUPPORTED_SUBCOMMANDS) == set(DEFAULT_USER_SURFACE) | set(ADVANCED_SURFACE)


def test_intent_router_should_default_to_core_and_support_only():
    assert "prototype" in DEFAULT_ROUTABLE_INTENTS
    assert "doctor" in DEFAULT_ROUTABLE_INTENTS
    assert "analyze" not in DEFAULT_ROUTABLE_INTENTS
    assert "team" not in DEFAULT_ROUTABLE_INTENTS
    assert "run" not in DEFAULT_ROUTABLE_INTENTS
    explicit_only = set(SUPPORTED_INTENTS) - set(DEFAULT_ROUTABLE_INTENTS) - {"outside-boundary"}
    assert explicit_only == set(EXPLICIT_ONLY_COMMAND_HINTS)
