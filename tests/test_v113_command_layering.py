from beacon.command_catalog import (
    ADVANCED_SURFACE,
    BRIDGE_COMMANDS,
    COMPAT_COMMANDS,
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
        "prd",
        "user-story",
        "test-case",
        "prototype",
        "implement",
        "qa",
        "release",
    }
    assert "review" in SUPPORT_COMMANDS
    assert "review" in DEFAULT_USER_SURFACE
    assert set(DEFAULT_USER_SURFACE) == set(CORE_COMMANDS) | set(SUPPORT_COMMANDS)
    assert set(ADVANCED_SURFACE) == set(LABS_COMMANDS) | set(BRIDGE_COMMANDS) | set(DEPRECATED_COMMANDS) | set(COMPAT_COMMANDS)
    assert set(SUPPORTED_SUBCOMMANDS) == set(DEFAULT_USER_SURFACE) | set(ADVANCED_SURFACE)


def test_intent_router_should_default_to_core_and_support_only():
    assert "prototype" in DEFAULT_ROUTABLE_INTENTS
    assert "implement" in DEFAULT_ROUTABLE_INTENTS
    assert "help" in DEFAULT_ROUTABLE_INTENTS
    assert "doctor" in DEFAULT_ROUTABLE_INTENTS
    assert "analyze" not in DEFAULT_ROUTABLE_INTENTS
    assert "team" not in DEFAULT_ROUTABLE_INTENTS
    assert "run" not in DEFAULT_ROUTABLE_INTENTS
    for compat_intent in ("think", "workflow", "gate", "verify"):
        assert compat_intent in SUPPORTED_INTENTS
        assert compat_intent not in DEFAULT_ROUTABLE_INTENTS
        assert compat_intent in EXPLICIT_ONLY_COMMAND_HINTS
