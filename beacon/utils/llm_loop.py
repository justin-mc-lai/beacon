"""LLM loop trace helpers with host-first and optional provider fallback orchestration."""

from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib import request

from beacon.utils.runtime import now_iso
from beacon.utils.semantic_runtime import load_host_response_json

STAGE_ORDER = ("think", "user-story", "prd", "test-case", "implementation", "verify", "none")


def _estimate_tokens(text: str) -> int:
    return max(1, len((text or "").split()))


def _sanitize_stage(value: str | None, fallback: str) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    if raw in STAGE_ORDER:
        return raw
    for stage in STAGE_ORDER:
        if stage in raw:
            return stage
    return fallback


def _should_use_real_llm() -> bool:
    mode = str(os.environ.get("BEACON_LLM_MODE", "")).strip().lower()
    return mode in {"real", "live", "api"}


def _extract_stage_from_text(text: str, fallback: str) -> str:
    raw_text = (text or "").strip().lower()
    try:
        payload = json.loads(raw_text)
        if isinstance(payload, dict):
            return _sanitize_stage(
                str(payload.get("next_stage", "") or payload.get("next-stage", "")),
                fallback,
            )
    except Exception:  # noqa: BLE001
        pass

    normalized = raw_text.replace("_", "-")
    match = re.search(r"next[_\s-]*stage\s*[:=]\s*([a-z-]+)", normalized)
    if match:
        return _sanitize_stage(match.group(1), fallback)
    return _sanitize_stage(normalized, fallback)


def _real_llm_inference(
    *,
    feature: str,
    version: str,
    run_id: str,
    next_stage: str,
    context: str,
) -> dict[str, Any]:
    api_key = str(os.environ.get("BEACON_LLM_API_KEY", "")).strip()
    if not api_key:
        raise RuntimeError("BEACON_LLM_API_KEY missing")

    api_base = str(os.environ.get("BEACON_LLM_API_BASE", "https://api.openai.com/v1")).strip().rstrip("/")
    model = str(os.environ.get("BEACON_LLM_MODEL", "gpt-4o-mini")).strip()
    timeout_s = float(str(os.environ.get("BEACON_LLM_TIMEOUT", "8")).strip() or "8")
    temperature = float(str(os.environ.get("BEACON_LLM_TEMPERATURE", "0.1")).strip() or "0.1")

    system_prompt = (
        "You are Beacon workflow orchestrator. "
        "Return compact JSON: "
        '{"next_stage":"think|user-story|prd|test-case|implementation|verify|none","risk":"low|medium|high","reason":"..."}'
    )
    user_prompt = (
        f"feature={feature}\nversion={version}\nrun_id={run_id}\n"
        f"context={context}\nnext_stage_hint={next_stage}\n"
        "Infer the best next executable stage and short risk reasoning."
    )

    body = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    req = request.Request(
        url=f"{api_base}/chat/completions",
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with request.urlopen(req, timeout=timeout_s) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    choices = payload.get("choices")
    content = ""
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                content = str(message.get("content", ""))
    usage = payload.get("usage") if isinstance(payload, dict) else {}
    prompt_tokens = int((usage or {}).get("prompt_tokens", _estimate_tokens(system_prompt + user_prompt)))
    completion_tokens = int((usage or {}).get("completion_tokens", _estimate_tokens(content)))
    predicted_stage = _extract_stage_from_text(content, next_stage)
    return {
        "model": model,
        "completion": content or f"next_stage={predicted_stage}",
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "next_stage": predicted_stage,
    }


def _host_llm_inference(
    *,
    next_stage: str,
) -> dict[str, Any]:
    payload, _source = load_host_response_json("next-stage")
    if not payload:
        raise RuntimeError("host semantic response missing")
    completion = str(payload.get("completion") or payload.get("reason") or "").strip()
    predicted_stage = _extract_stage_from_text(
        str(payload.get("next_stage") or completion or next_stage),
        next_stage,
    )
    return {
        "model": str(payload.get("model") or "host-native"),
        "completion": completion or f"next_stage={predicted_stage}",
        "prompt_tokens": int(payload.get("prompt_tokens", 0) or 0),
        "completion_tokens": int(payload.get("completion_tokens", 0) or 0),
        "next_stage": predicted_stage,
    }


def build_next_stage_trace(
    *,
    feature: str,
    version: str,
    run_id: str,
    next_stage: str | None,
    context: str,
) -> dict[str, Any]:
    fallback_stage = _sanitize_stage(next_stage or "none", "none")
    prompt = (
        f"Project workflow inference. feature={feature}; version={version}; "
        f"run_id={run_id}; context={context}. Determine next executable stage."
    )

    try:
        host = _host_llm_inference(next_stage=fallback_stage)
        return {
            "ts": now_iso(),
            "source": "workflow.next-stage-inference",
            "inference_mode": "host",
            "model": host["model"],
            "prompt": prompt,
            "completion": host["completion"],
            "next_stage": host["next_stage"],
            "prompt_tokens": int(host["prompt_tokens"]),
            "completion_tokens": int(host["completion_tokens"]),
        }
    except Exception:  # noqa: BLE001
        pass

    if _should_use_real_llm():
        try:
            real = _real_llm_inference(
                feature=feature,
                version=version,
                run_id=run_id,
                next_stage=fallback_stage,
                context=context,
            )
            return {
                "ts": now_iso(),
                "source": "workflow.next-stage-inference",
                "inference_mode": "real",
                "model": real["model"],
                "prompt": prompt,
                "completion": real["completion"],
                "next_stage": real["next_stage"],
                "prompt_tokens": int(real["prompt_tokens"]),
                "completion_tokens": int(real["completion_tokens"]),
            }
        except Exception as exc:  # noqa: BLE001
            completion = (
                f"Predicted next_stage={fallback_stage}. "
                "Fallback to rule mode due to real LLM error."
            )
            return {
                "ts": now_iso(),
                "source": "workflow.next-stage-inference",
                "inference_mode": "rule-fallback",
                "model": "beacon-rule-llm-v1",
                "prompt": prompt,
                "completion": completion,
                "next_stage": fallback_stage,
                "error": str(exc),
                "prompt_tokens": _estimate_tokens(prompt),
                "completion_tokens": _estimate_tokens(completion),
            }

    completion = (
        f"Predicted next_stage={fallback_stage}. "
        "Reasoning policy: lifecycle closure order "
        "(think->user-story->prd->test-case->implementation->verify)."
    )
    return {
        "ts": now_iso(),
        "source": "workflow.next-stage-inference",
        "inference_mode": "rule",
        "model": "beacon-rule-llm-v1",
        "prompt": prompt,
        "completion": completion,
        "next_stage": fallback_stage,
        "prompt_tokens": _estimate_tokens(prompt),
        "completion_tokens": _estimate_tokens(completion),
    }


def merge_token_usage(current: dict[str, Any] | None, trace: dict[str, Any]) -> dict[str, int]:
    current = current if isinstance(current, dict) else {}
    return {
        "prompt_tokens": int(current.get("prompt_tokens", 0)) + int(trace.get("prompt_tokens", 0)),
        "completion_tokens": int(current.get("completion_tokens", 0)) + int(trace.get("completion_tokens", 0)),
    }
