"""Loop audit utilities (v1.6.6+ agent trace coverage signal)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.agent_trace import agent_trace_coverage_signal

SCHEMA_VERSION = "loop-audit-v1"


def run_loop_audit(
    project_root: Path,
    *,
    version: str = "",
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    trace_signal = agent_trace_coverage_signal(root)
    overall = str(trace_signal.get("status") or "missing")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": overall,
        "version": str(version or ""),
        "project_root": str(root),
        "signals": [trace_signal],
        "findings": list(trace_signal.get("findings") or []),
        "agent_trace_coverage": trace_signal,
    }
