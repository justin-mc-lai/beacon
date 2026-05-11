"""Shared support-surface reason-code helpers."""

from __future__ import annotations

from typing import Any


def primary_reason_code(reason_codes: list[str] | None = None, blocked_reason: str = "") -> str:
    if str(blocked_reason or "").strip():
        return str(blocked_reason or "").strip()
    for item in reason_codes or []:
        text = str(item or "").strip()
        if text:
            return text
    return ""


def normalize_reason_codes(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in out:
            out.append(text)
    return out
