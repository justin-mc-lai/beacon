"""v1.1.0 debug feedback pipeline coverage contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.memory import load_memory_entries

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _all_debug_events(root: Path) -> list[dict]:
    out: list[dict] = []
    debug_dir = root / ".beacon" / "state" / "debug-feedback"
    if not debug_dir.exists():
        return out
    for file in sorted(debug_dir.glob("*.jsonl")):
        for line in file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                out.append(payload)
    return out


def test_collectors_should_cover_all_sources(tmp_path: Path):
    enable = _invoke([
        "debug",
        "enable",
        "--project-root",
        str(tmp_path),
        "--run-id",
        "run-debug-collector",
        "--no-sync-history",
    ])
    assert enable.exit_code == 0

    ask = _invoke(["ask", "请做一次环境诊断", "--project-root", str(tmp_path), "--json"])
    assert ask.exit_code == 0

    run_result = _invoke(["run", "workflow", "--project-root", str(tmp_path), "--json"])
    assert run_result.exit_code == 0

    gate = _invoke(["gate", "check", "think", "--project-root", str(tmp_path), "--json"])
    assert gate.exit_code in {0, 2}

    team = _invoke(["team", "start", "调试反馈闭环", "--project", str(tmp_path), "--runtime", "file"])
    assert team.exit_code == 0

    workflow = _invoke(["workflow", "start", "调试反馈闭环", "--project", str(tmp_path), "--version", "v1.1.0"])
    assert workflow.exit_code == 0

    events = _all_debug_events(tmp_path)
    sources = {str(item.get("source", "")) for item in events}

    assert "prompt.optimize" in sources
    assert "run.workflow" in sources
    assert "gate.check" in sources
    assert "team.start" in sources
    assert "workflow.start" in sources


def test_feedback_sync_should_assimilate_debug_candidates(tmp_path: Path):
    debug_dir = tmp_path / ".beacon" / "state" / "debug-feedback"
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "run-debug-sync-001.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": "2026-03-07T00:00:00Z",
                        "run_id": "run-debug-sync-001",
                        "source": "prompt.optimize",
                        "goal": "请直接部署到生产",
                        "intent": "outside-boundary",
                        "confidence": 0.4,
                        "boundary_state": "out_of_scope",
                        "block_reason": "outside-beacon-boundary",
                        "recommended_command": "",
                        "executed": False,
                        "exit_code": None,
                        "note": "debug",
                    },
                    ensure_ascii=False,
                )
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    extract = _invoke([
        "feedback",
        "extract",
        "run-debug-sync-001",
        "--source",
        "debug",
        "--project-root",
        str(tmp_path),
        "--json",
    ])
    assert extract.exit_code == 0
    extract_payload = json.loads(extract.stdout)
    assert extract_payload.get("feedback")

    apply = _invoke([
        "feedback",
        "apply",
        "run-debug-sync-001",
        "--project-root",
        str(tmp_path),
        "--json",
    ])
    assert apply.exit_code == 0
    apply_payload = json.loads(apply.stdout)
    assert int(apply_payload.get("applied_count", 0)) >= 1

    entries = load_memory_entries(tmp_path)
    assert any(str(item.get("source", "")).startswith("feedback.apply") for item in entries)
