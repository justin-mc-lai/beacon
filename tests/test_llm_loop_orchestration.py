from __future__ import annotations

import json

from beacon.utils import llm_loop


def test_build_next_stage_trace_should_use_rule_mode_by_default(monkeypatch):
    monkeypatch.delenv("BEACON_LLM_MODE", raising=False)
    monkeypatch.delenv("BEACON_LLM_API_KEY", raising=False)

    trace = llm_loop.build_next_stage_trace(
        feature="Login",
        version="v1.0.0",
        run_id="run-1",
        next_stage="think",
        context="workflow.start",
    )

    assert trace["inference_mode"] == "rule"
    assert trace["model"] == "beacon-rule-llm-v1"
    assert trace["next_stage"] == "think"


def test_build_next_stage_trace_should_fallback_when_real_mode_missing_key(monkeypatch):
    monkeypatch.setenv("BEACON_LLM_MODE", "real")
    monkeypatch.delenv("BEACON_LLM_API_KEY", raising=False)

    trace = llm_loop.build_next_stage_trace(
        feature="Login",
        version="v1.0.0",
        run_id="run-1",
        next_stage="prd",
        context="workflow.continue",
    )

    assert trace["inference_mode"] == "rule-fallback"
    assert trace["next_stage"] == "prd"
    assert "BEACON_LLM_API_KEY" in trace.get("error", "")


def test_build_next_stage_trace_should_use_real_mode_when_provider_available(monkeypatch):
    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"next_stage":"verify","risk":"low","reason":"all checks ready"}'
                            }
                        }
                    ],
                    "usage": {"prompt_tokens": 12, "completion_tokens": 7},
                }
            ).encode("utf-8")

    monkeypatch.setenv("BEACON_LLM_MODE", "real")
    monkeypatch.setenv("BEACON_LLM_API_KEY", "test-key")
    monkeypatch.setenv("BEACON_LLM_API_BASE", "https://example.invalid/v1")
    monkeypatch.setenv("BEACON_LLM_MODEL", "test-model")
    monkeypatch.setattr(llm_loop.request, "urlopen", lambda *args, **kwargs: _FakeResponse())

    trace = llm_loop.build_next_stage_trace(
        feature="Login",
        version="v1.0.0",
        run_id="run-2",
        next_stage="test-case",
        context="workflow.continue",
    )

    assert trace["inference_mode"] == "real"
    assert trace["model"] == "test-model"
    assert trace["next_stage"] == "verify"
    assert trace["prompt_tokens"] == 12
    assert trace["completion_tokens"] == 7
