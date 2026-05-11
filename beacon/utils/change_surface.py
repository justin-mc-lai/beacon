"""Shared helpers for Beacon frozen-truth change loop routing."""

from __future__ import annotations

import json
from pathlib import Path


def build_change_command(
    *,
    feature: str,
    project_root: Path | str,
    version: str,
    reason: str | None = None,
) -> str:
    root = Path(project_root)
    resolved_reason = str(reason or "").strip()
    command = f'beacon change {json.dumps(feature, ensure_ascii=False)} --project-root {root} --version {version}'
    if resolved_reason:
        command += f" --reason {json.dumps(resolved_reason, ensure_ascii=False)}"
    return command
