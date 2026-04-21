"""Tests for beacon/utils/llm_loop.py"""

import json
import pytest
from beacon.utils.llm_loop import build_next_stage_trace


def test_build_next_stage_trace_host_mode():
    """Test build_next_stage_trace with host inference mode."""
    context = {
        "feature": "test-feature",
        "version": "v1.3.6",
        "stage": "prd"
    }

    result = build_next_stage_trace(
        stage="prd",
        context=context,
        inference_mode="host"
    )

    assert result is not None
    assert "stage" in result
    assert result["stage"] == "prd"
    assert "inference_mode" in result
    assert result["inference_mode"] == "host"


def test_build_next_stage_trace_real_mode():
    """Test build_next_stage_trace with real (provider) inference mode."""
    context = {
        "feature": "test-feature",
        "version": "v1.3.6",
        "stage": "user-story"
    }

    result = build_next_stage_trace(
        stage="user-story",
        context=context,
        inference_mode="real"
    )

    assert result is not None
    assert result["inference_mode"] == "real"


def test_build_next_stage_trace_rule_mode():
    """Test build_next_stage_trace with rule-based mode."""
    context = {
        "feature": "test-feature",
        "version": "v1.3.6",
        "stage": "test-case"
    }

    result = build_next_stage_trace(
        stage="test-case",
        context=context,
        inference_mode="rule"
    )

    assert result is not None
    assert result["inference_mode"] == "rule"


def test_build_next_stage_trace_stage_order():
    """Test stage order validation."""
    # Valid stage order: think → user-story → prd → test-case → implementation → verify → none
    valid_stages = ["think", "user-story", "prd", "test-case", "implementation", "verify", "none"]

    for stage in valid_stages:
        result = build_next_stage_trace(
            stage=stage,
            context={"feature": "test"},
            inference_mode="host"
        )
        assert result["stage"] == stage


def test_build_next_stage_trace_token_tracking():
    """Test token usage tracking."""
    context = {
        "feature": "test-feature",
        "version": "v1.3.6"
    }

    result = build_next_stage_trace(
        stage="prd",
        context=context,
        inference_mode="host"
    )

    assert "token_usage" in result
    assert "input_tokens" in result["token_usage"]
    assert "output_tokens" in result["token_usage"]


def test_build_next_stage_trace_fallback():
    """Test fallback from host to provider."""
    context = {
        "feature": "test-feature",
        "version": "v1.3.6"
    }

    # Simulate host failure, should fallback to real
    result = build_next_stage_trace(
        stage="prd",
        context=context,
        inference_mode="rule-fallback"
    )

    assert result is not None
    assert "fallback_reason" in result
