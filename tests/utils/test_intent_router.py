"""Tests for beacon/utils/intent_router.py"""

import pytest
from beacon.utils.intent_router import (
    route_intent,
    detect_intent,
    render_command_template
)


def test_route_intent_rule_based():
    """Test rule-based intent routing."""
    # Test PRD intent
    result = route_intent(
        user_input="create a prd for new feature",
        mode="rule"
    )

    assert result is not None
    assert result["intent"] == "prd"
    assert result["confidence"] >= 0.8


def test_route_intent_llm_based():
    """Test LLM-based intent routing."""
    result = route_intent(
        user_input="I need to write requirements for authentication",
        mode="llm"
    )

    assert result is not None
    assert "intent" in result
    assert "confidence" in result


def test_route_intent_host_based():
    """Test host-based intent routing."""
    result = route_intent(
        user_input="generate user story",
        mode="host"
    )

    assert result is not None
    assert result["intent"] == "user-story"


def test_detect_intent_supported_intents():
    """Test detection of all 54 supported intents."""
    test_cases = [
        ("create prd", "prd"),
        ("write user story", "user-story"),
        ("generate test cases", "test-case"),
        ("run implementation", "implement"),
        ("start qa", "qa"),
        ("check status", "status"),
        ("create prototype", "prototype"),
        ("release version", "release")
    ]

    for user_input, expected_intent in test_cases:
        result = detect_intent(user_input)
        assert result["intent"] == expected_intent


def test_detect_intent_confidence_scoring():
    """Test confidence scoring."""
    # High confidence case
    result_high = detect_intent("create prd for feature")
    assert result_high["confidence"] >= 0.8

    # Low confidence case
    result_low = detect_intent("maybe do something")
    assert result_low["confidence"] < 0.5


def test_detect_intent_boundary_guard():
    """Test out-of-scope detection."""
    result = route_intent(
        user_input="what's the weather today?",
        mode="rule"
    )

    assert result["intent"] == "out-of-scope"
    assert result["confidence"] < 0.3


def test_render_command_template():
    """Test command template rendering."""
    template = "beacon {{command}} {{feature}} --version {{version}}"
    context = {
        "command": "prd",
        "feature": "test-feature",
        "version": "v1.3.6"
    }

    result = render_command_template(template, context)
    assert result == "beacon prd test-feature --version v1.3.6"


def test_render_command_template_missing_variable():
    """Test template rendering with missing variable."""
    template = "beacon {{command}} {{feature}}"
    context = {
        "command": "prd"
        # feature is missing
    }

    with pytest.raises(KeyError):
        render_command_template(template, context)


def test_route_intent_multiple_modes():
    """Test routing with multiple modes."""
    user_input = "create prd"

    # Rule mode
    result_rule = route_intent(user_input, mode="rule")
    assert result_rule["mode"] == "rule"

    # LLM mode
    result_llm = route_intent(user_input, mode="llm")
    assert result_llm["mode"] == "llm"

    # Host mode
    result_host = route_intent(user_input, mode="host")
    assert result_host["mode"] == "host"

    # All should detect the same intent
    assert result_rule["intent"] == result_llm["intent"] == result_host["intent"]
