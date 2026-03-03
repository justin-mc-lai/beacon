"""LLM loop trace helpers.

This module provides a lightweight, deterministic "LLM trace" so workflow
states always include prompt/completion evidence for next-step inference.
"""

from __future__ import annotations

from typing import Any

from beacon.utils.runtime import now_iso


def _estimate_tokens(text: str) -> int:
    return max(1, len((text or "").split()))


def build_next_stage_trace(
    *,
    feature: str,
    version: str,
    run_id: str,
    next_stage: str | None,
    context: str,
) -> dict[str, Any]:
    stage = next_stage or "none"
    prompt = (
        f"Project workflow inference. feature={feature}; version={version}; "
        f"run_id={run_id}; context={context}. Determine next executable stage."
    )
    completion = (
        f"Predicted next_stage={stage}. "
        "Reasoning policy: lifecycle closure order "
        "(think->user-story->prd->test-case->implementation->verify)."
    )
    prompt_tokens = _estimate_tokens(prompt)
    completion_tokens = _estimate_tokens(completion)
    return {
        "ts": now_iso(),
        "source": "workflow.next-stage-inference",
        "model": "beacon-rule-llm-v1",
        "prompt": prompt,
        "completion": completion,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


def merge_token_usage(current: dict[str, Any] | None, trace: dict[str, Any]) -> dict[str, int]:
    current = current if isinstance(current, dict) else {}
    return {
        "prompt_tokens": int(current.get("prompt_tokens", 0)) + int(trace.get("prompt_tokens", 0)),
        "completion_tokens": int(current.get("completion_tokens", 0)) + int(trace.get("completion_tokens", 0)),
    }

