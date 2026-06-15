"""Resolve a usable Python interpreter for QA/auto-test shell commands."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

_BEACON_JUNIT_ARG = '--junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"'
_PYTHON_INVOCATION_RE = re.compile(r"(?<![\w./-])(python)\s+(?=-m\b)")


def _is_usable_python(path: str) -> bool:
    candidate = str(path or "").strip()
    if not candidate:
        return False
    try:
        result = subprocess.run(
            [candidate, "-c", "import sys"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def resolve_python_executable(project_root: Path | None = None) -> str:
    """Pick an interpreter that can actually run `-c import sys`."""
    candidates: list[str] = []
    if _is_usable_python(sys.executable):
        candidates.append(sys.executable)

    if isinstance(project_root, Path):
        for relative in (".venv/bin/python", ".venv/bin/python3", "venv/bin/python", "venv/bin/python3"):
            path = project_root / relative
            if path.is_file():
                candidates.append(str(path))

    for name in ("python3", "python"):
        found = shutil.which(name)
        if found:
            candidates.append(found)

    for candidate in candidates:
        if _is_usable_python(candidate):
            return candidate
    return "python3"


def normalize_python_invocation(command: str, *, project_root: Path | None = None) -> str:
    """Rewrite bare `python -m ...` invocations to a verified interpreter."""
    raw = str(command or "").strip()
    if not raw:
        return raw
    python = resolve_python_executable(project_root)
    if python == "python":
        return raw
    return _PYTHON_INVOCATION_RE.sub(f"{python} ", raw, count=1)


def ensure_pytest_junit_command(command: str) -> str:
    raw = str(command or "").strip()
    if not raw:
        return raw
    lowered = raw.lower()
    if "pytest" not in lowered or "--junitxml" in lowered:
        return raw
    return f"{raw} {_BEACON_JUNIT_ARG}"


def normalize_qa_shell_command(command: str, *, project_root: Path | None = None) -> str:
    """Apply python resolution and pytest junit defaults for QA matrix commands."""
    resolved = normalize_python_invocation(command, project_root=project_root)
    return ensure_pytest_junit_command(resolved)
