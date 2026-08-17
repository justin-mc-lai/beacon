from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import LABS_COMMANDS, SUPPORTED_SUBCOMMANDS
from beacon.main import app
from beacon.utils.memory import append_memory_entry, load_memory_entries


runner = CliRunner()


def _seed_v133_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / "v1.3.3" / "execution"
    base.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.3.3" / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_v133_memory_friction_should_be_labs_surface() -> None:
    assert "memory-friction-evolution" in LABS_COMMANDS
    assert "memory-friction-evolution" in SUPPORTED_SUBCOMMANDS


def test_v133_memory_mode_should_emit_candidates(tmp_path: Path) -> None:
    _seed_v133_docs(tmp_path)
    append_memory_entry(
        tmp_path,
        mem_type="feedback",
        text="QA blocked because missing evidence artifact.",
        source="test",
        source_session_id="session-memory",
        evidence_ref=[".beacon/evidence/mock-evidence.json"],
        reason_codes=["qa_policy"],
        confidence=0.91,
    )

    result = _invoke(
        [
            "memory-friction-evolution",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--mode",
            "memory",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["mode"] == "memory"
    assert payload["candidates"]
    first = payload["candidates"][0]
    assert first["friction_summary"]
    assert first["recommended_command"]
    assert first["recommendation"] in {"keep", "review", "discard"}
    assert (tmp_path / payload["paths"]["json"]).exists()
    assert (tmp_path / payload["paths"]["markdown"]).exists()


def test_v133_friction_mode_should_support_lighthouse_and_turn_guard(tmp_path: Path) -> None:
    _seed_v133_docs(tmp_path)
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    issues_root = tmp_path / ".beacon" / "debug" / "issues"
    issues_root.mkdir(parents=True, exist_ok=True)
    (issues_root / "beacon-core--runtime_feedback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "issue_id": "beacon-core--runtime_feedback",
                "feedback_target": "beacon-core",
                "reason_code": "runtime_feedback",
                "count": 3,
                "sample": "runtime repeatedly blocks at QA gate",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = _invoke(
        [
            "memory-friction-evolution",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--mode",
            "friction",
            "--with-lighthouse",
            "--max-turns",
            "2",
            "--top-n",
            "1",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["mode"] == "friction"
    assert len(payload["turns"]) <= 2
    assert payload["decision"]["should_exit"] is True
    lighthouse_ref = payload["inputs"]["lighthouse_ref"]
    assert lighthouse_ref
    assert (tmp_path / lighthouse_ref).exists()


def test_v133_writeback_should_use_memory_upsert_path(tmp_path: Path) -> None:
    _seed_v133_docs(tmp_path)
    append_memory_entry(
        tmp_path,
        mem_type="feedback",
        text="debug friction persists around release gate closure",
        source="test",
        source_session_id="session-writeback",
        reason_codes=["debug_policy"],
        confidence=0.87,
    )

    result = _invoke(
        [
            "memory-friction-evolution",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--mode",
            "both",
            "--writeback",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["writeback"]["enabled"] is True
    assert payload["writeback"]["memory_ids"]

    rows = load_memory_entries(tmp_path, mem_type="feedback")
    assert any(str(row.get("source") or "") == "memory-friction-evolution.writeback" for row in rows)
