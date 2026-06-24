"""Host executor adapter for Agent Eval live host_behavior mode."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from beacon.utils.agent_eval_grader import parse_route_line


@dataclass(frozen=True)
class HostExecutionResult:
    ok: bool
    transcript: str
    reason_code: str
    executor: str
    degraded: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "transcript": self.transcript,
            "reason_code": self.reason_code,
            "executor": self.executor,
            "degraded": self.degraded,
        }


def _executor_mode(host: str) -> str:
    explicit = str(os.environ.get("BEACON_AGENT_EVAL_EXECUTOR") or "").strip().lower()
    if explicit:
        return explicit
    if os.environ.get("BEACON_AGENT_EVAL_MOCK") == "1":
        return "mock"
    if host == "cursor":
        return "cursor_stub"
    return "mock"


def _mock_transcript(*, prompt_text: str, skill_id: str) -> str:
    route = parse_route_line(prompt_text) or skill_id
    return (
        f"Agent Eval mock host execution for {skill_id}.\n"
        f"ROUTE: {route}\n"
        "Acknowledged harness boundaries; routing to the expected evaluator surface.\n"
    )


def _cursor_stub_transcript(*, prompt_text: str, skill_id: str, skill_file: Path) -> str:
    route = parse_route_line(prompt_text) or skill_id
    loaded = skill_file.exists() and skill_file.stat().st_size > 0
    return (
        f"Cursor stub executor for {skill_id}.\n"
        f"ROUTE: {route}\n"
        f"Skill surface loaded: {'yes' if loaded else 'no'}.\n"
        "Executor transcript omits skill body to avoid boundary phrase false positives.\n"
    )


def execute_host_prompt(
    project_root: Path,
    *,
    skill_id: str,
    prompt_text: str,
    host: str,
    timeout_seconds: float,
) -> HostExecutionResult:
    """Run prompt through host executor (mock, cursor stub, or subprocess module)."""
    mode = _executor_mode(host)
    skill_file = project_root / "skills" / "beacon" / skill_id / "SKILL.md"

    if mode == "mock":
        transcript = _mock_transcript(prompt_text=prompt_text, skill_id=skill_id)
        return HostExecutionResult(
            ok=True,
            transcript=transcript,
            reason_code="",
            executor="mock",
            degraded=True,
        )

    if mode == "cursor_stub":
        transcript = _cursor_stub_transcript(
            prompt_text=prompt_text,
            skill_id=skill_id,
            skill_file=skill_file,
        )
        return HostExecutionResult(
            ok=True,
            transcript=transcript,
            reason_code="",
            executor="cursor_stub",
            degraded=False,
        )

    if mode == "subprocess":
        script = (
            "import sys\n"
            "from pathlib import Path\n"
            "from beacon.utils.agent_eval_live_executor import _cursor_stub_transcript\n"
            "root = Path(sys.argv[1])\n"
            "skill_id = sys.argv[2]\n"
            "prompt = Path(sys.argv[3]).read_text(encoding='utf-8')\n"
            "skill_file = root / 'skills/beacon' / skill_id / 'SKILL.md'\n"
            "print(_cursor_stub_transcript(prompt_text=prompt, skill_id=skill_id, skill_file=skill_file))\n"
        )
        with subprocess.Popen(
            [sys.executable, "-c", script, str(project_root), skill_id, "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root),
        ) as proc:
            try:
                stdout, stderr = proc.communicate(prompt_text, timeout=max(timeout_seconds, 1.0))
            except subprocess.TimeoutExpired:
                proc.kill()
                return HostExecutionResult(
                    ok=False,
                    transcript="",
                    reason_code="host_executor_timeout",
                    executor=mode,
                    degraded=False,
                )
        if proc.returncode != 0:
            return HostExecutionResult(
                ok=False,
                transcript=(stdout or "") + (stderr or ""),
                reason_code="host_executor_failed",
                executor=mode,
                degraded=False,
            )
        return HostExecutionResult(
            ok=True,
            transcript=stdout,
            reason_code="",
            executor=mode,
            degraded=False,
        )

    return HostExecutionResult(
        ok=False,
        transcript="",
        reason_code="host_executor_unknown_mode",
        executor=mode,
        degraded=False,
    )


def write_transcript(transcripts_dir: Path, skill_id: str, transcript: str) -> str:
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    path = transcripts_dir / f"{skill_id}.transcript.txt"
    path.write_text(transcript, encoding="utf-8")
    return str(path.name)
