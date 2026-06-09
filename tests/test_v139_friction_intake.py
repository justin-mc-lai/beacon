from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import SUPPORT_COMMANDS, SUPPORTED_SUBCOMMANDS
from beacon.main import app


runner = CliRunner()


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / "v1.3.9" / "execution"
    base.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.3.9" / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")


def test_v139_friction_intake_should_be_support_surface_and_skill_visible() -> None:
    assert "friction-intake" in SUPPORT_COMMANDS
    assert "friction-intake" in SUPPORTED_SUBCOMMANDS

    host_skill = Path("skills/beacon/SKILL.md")
    text = host_skill.read_text(encoding="utf-8")
    assert "`beacon-pln-friction`" in text
    assert "friction-intake run" in text

    subskill = Path("skills/beacon/beacon-pln-friction/SKILL.md")
    subskill_text = subskill.read_text(encoding="utf-8")
    assert "name: beacon-pln-friction" in subskill_text
    assert "摩擦记录" in subskill_text


def test_v139_scan_should_dual_write_to_friction_queue(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_docs(tmp_path)
    issues_root = tmp_path / ".beacon" / "debug" / "issues"
    issues_root.mkdir(parents=True, exist_ok=True)
    (issues_root / "beacon-core--qa-blocked.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "issue_id": "beacon-core--qa-blocked",
                "reason_code": "qa_blocked",
                "count": 2,
                "sample": "QA blocked because acceptance dual-write did not materialize",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "scan",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["mode"] == "scan"
    assert payload["governance"]["status"] == "ok"
    assert payload["items"]
    first = payload["items"][0]
    assert first["source_type"] == "scan"
    assert first["item_class"] in {"blocking_bug", "improvement", "optimization_enhancement"}
    assert (tmp_path / payload["paths"]["json"]).exists()

    db_path = Path(payload["governance"]["db_path"])
    assert db_path.exists()
    with sqlite3.connect(str(db_path)) as conn:
        row = conn.execute(
            "SELECT queue_status, requirement_route_status, summary FROM friction_items WHERE item_id = ?",
            (first["item_id"],),
        ).fetchone()
        assert row is not None
        assert row[0] == "queued"
        assert row[1] == "queue_only"
        assert "QA blocked" in row[2]


def test_v139_capture_should_support_acceptance_gate_and_inbox(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_docs(tmp_path)

    result = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            "Host runtime blocked implement because codex skill admission drifted.",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    item_id = payload["items"][0]["item_id"]
    assert payload["items"][0]["source_type"] == "manual_capture"

    inbox = runner.invoke(
        app,
        [
            "friction-intake",
            "inbox",
            "--project-root",
            str(tmp_path),
            "--json",
        ],
    )
    assert inbox.exit_code == 0, inbox.stdout
    inbox_payload = json.loads(inbox.stdout)
    assert any(str(item.get("item_id") or "") == item_id for item in inbox_payload["items"])

    accepted = runner.invoke(
        app,
        [
            "friction-intake",
            "accept",
            item_id,
            "--project-root",
            str(tmp_path),
            "--json",
        ],
    )
    assert accepted.exit_code == 0, accepted.stdout
    accepted_payload = json.loads(accepted.stdout)
    assert accepted_payload["requirement_route_status"] == "accepted_for_requirement"


def test_v139_capture_should_dual_write_to_friction_queue(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_docs(tmp_path)

    result = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            "Manual capture should dual-write into sqlite while preserving local evidence.",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["governance"]["status"] == "ok"
    item = payload["items"][0]
    assert item["source_type"] == "manual_capture"

    evidence_ref = item["evidence_refs"][0]
    assert (tmp_path / evidence_ref).exists()

    db_path = Path(payload["governance"]["db_path"])
    assert db_path.exists()
    with sqlite3.connect(str(db_path)) as conn:
        row = conn.execute(
            """
            SELECT source_type, queue_status, requirement_route_status, summary
            FROM friction_items
            WHERE item_id = ?
            """,
            (item["item_id"],),
        ).fetchone()
        assert row is not None
        assert row[0] == "manual_capture"
        assert row[1] == "queued"
        assert row[2] == "queue_only"
        assert "dual-write" in row[3]


def test_v139_legacy_memory_friction_evolution_should_remain_compatible(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_docs(tmp_path)
    issues_root = tmp_path / ".beacon" / "debug" / "issues"
    issues_root.mkdir(parents=True, exist_ok=True)
    (issues_root / "beacon-core--runtime-feedback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "issue_id": "beacon-core--runtime-feedback",
                "reason_code": "runtime_feedback",
                "count": 1,
                "sample": "runtime feedback still needs review",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "memory-friction-evolution",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "friction",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["tool"] == "beacon-memory-friction-evolution"
    assert payload["candidates"]


def test_v139_queue_state_and_truth_boundaries_should_hold(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_docs(tmp_path)

    result = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            "Workflow bug blocks release because queue route is unclear.",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    item_id = payload["items"][0]["item_id"]
    item_summary = payload["items"][0]["summary"]
    evidence_ref = payload["items"][0]["evidence_refs"][0]

    claim = runner.invoke(app, ["friction-intake", "claim", item_id, "--project-root", str(tmp_path), "--json"])
    assert claim.exit_code == 0, claim.stdout
    resolve = runner.invoke(app, ["friction-intake", "resolve", item_id, "--project-root", str(tmp_path), "--json"])
    assert resolve.exit_code == 0, resolve.stdout
    reopen = runner.invoke(app, ["friction-intake", "reopen", item_id, "--project-root", str(tmp_path), "--json"])
    assert reopen.exit_code == 0, reopen.stdout

    db_path = tmp_path / ".runtime-ledger" / "runtime-ledger.sqlite3"
    with sqlite3.connect(str(db_path)) as conn:
        row = conn.execute(
            """
            SELECT source_type, item_class, severity, domain, queue_status,
                   requirement_route_status, project_root, summary, first_seen_at, last_seen_at, occurrence_count
            FROM friction_items
            WHERE item_id = ?
            """,
            (item_id,),
        ).fetchone()
        assert row is not None
        assert row[0] == "manual_capture"
        assert row[1] in {"blocking_bug", "improvement", "optimization_enhancement"}
        assert row[2] in {"P0", "P1", "P2", "P3"}
        assert row[3]
        assert row[4] == "reopened"
        assert row[5] == "queue_only"
        assert row[6] == str(tmp_path.resolve())
        assert row[7] == item_summary
        assert row[8]
        assert row[9]
        assert row[10] >= 1

        refs = conn.execute(
            "SELECT ref_path FROM friction_refs WHERE item_id = ?",
            (item_id,),
        ).fetchall()
        assert [ref[0] for ref in refs] == [evidence_ref]

        events = conn.execute(
            "SELECT event_type FROM friction_events WHERE item_id = ? ORDER BY event_at ASC",
            (item_id,),
        ).fetchall()
        event_types = [event[0] for event in events]
        assert "captured" in event_types
        assert "claimed" in event_types
        assert "resolved" in event_types
        assert "reopened" in event_types

        debug_issue_count = conn.execute("SELECT COUNT(*) FROM debug_issues").fetchone()[0]
        assert debug_issue_count == 0

        columns = {row[1] for row in conn.execute("PRAGMA table_info(friction_items)").fetchall()}
        assert "summary" in columns
        assert "requirement_route_status" in columns
        assert "raw_note" not in columns

    capture_path = tmp_path / evidence_ref
    assert capture_path.exists()
    capture_payload = json.loads(capture_path.read_text(encoding="utf-8"))
    assert capture_payload["raw_note"].startswith("Workflow bug blocks release")


def test_v139_capture_should_classify_non_blocking_work_into_allowed_classes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_docs(tmp_path)

    improvement = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            "Documentation guidance should be improved for onboarding clarity.",
            "--json",
        ],
    )
    assert improvement.exit_code == 0, improvement.stdout
    improvement_payload = json.loads(improvement.stdout)
    assert improvement_payload["items"][0]["item_class"] == "improvement"

    optimization = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            "Latency optimization is needed for runtime queue sync performance.",
            "--json",
        ],
    )
    assert optimization.exit_code == 0, optimization.stdout
    optimization_payload = json.loads(optimization.stdout)
    assert optimization_payload["items"][0]["item_class"] == "optimization_enhancement"


def test_v139_sqlite_failure_should_preserve_local_truth_and_allow_replay(tmp_path: Path, monkeypatch) -> None:
    runtime_root = tmp_path / ".runtime-ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(runtime_root))
    _seed_docs(tmp_path)
    note = "QA recovery path should keep local truth even when sqlite is disabled."

    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", "1")
    failed = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            note,
            "--json",
        ],
    )
    assert failed.exit_code == 0, failed.stdout
    failed_payload = json.loads(failed.stdout)
    assert failed_payload["governance"]["status"] == "manual_dual_write_local_only"
    assert failed_payload["governance"]["global_sqlite_written"] is False
    failed_item = failed_payload["items"][0]
    local_ref = failed_item["evidence_refs"][0]
    assert (tmp_path / local_ref).exists()
    assert (tmp_path / failed_payload["paths"]["json"]).exists()
    manual_record = failed_payload["governance"]["manual_dual_write_record"]
    assert (tmp_path / manual_record).exists()

    monkeypatch.delenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", raising=False)
    replayed = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            note,
            "--json",
        ],
    )
    assert replayed.exit_code == 0, replayed.stdout
    replayed_payload = json.loads(replayed.stdout)
    assert replayed_payload["governance"]["status"] == "ok"
    item_id = replayed_payload["items"][0]["item_id"]

    replayed_again = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            note,
            "--json",
        ],
    )
    assert replayed_again.exit_code == 0, replayed_again.stdout

    db_path = runtime_root / "runtime-ledger.sqlite3"
    with sqlite3.connect(str(db_path)) as conn:
        row = conn.execute(
            "SELECT occurrence_count, summary FROM friction_items WHERE item_id = ?",
            (item_id,),
        ).fetchone()
    assert row is not None
    assert row[0] >= 2
    assert "QA recovery path" in row[1]


def test_v139_friction_intake_human_report_should_mark_manual_dual_write_substitute(tmp_path: Path, monkeypatch) -> None:
    runtime_root = tmp_path / ".runtime-ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(runtime_root))
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", "1")
    _seed_docs(tmp_path)

    result = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            "Runner admission failed before sqlite write; keep local substitute evidence.",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "global_sqlite    : False" in result.stdout
    assert "manual_dual_write:" in result.stdout


def test_v139_scan_and_capture_should_share_queue_with_distinct_source_types(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(tmp_path / ".runtime-ledger"))
    _seed_docs(tmp_path)
    issues_root = tmp_path / ".beacon" / "debug" / "issues"
    issues_root.mkdir(parents=True, exist_ok=True)
    (issues_root / "beacon-core--workflow-blocked.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "issue_id": "beacon-core--workflow-blocked",
                "reason_code": "workflow_blocked",
                "count": 1,
                "sample": "workflow blocked because support route drifted",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    scan = runner.invoke(
        app,
        ["friction-intake", "run", "--project-root", str(tmp_path), "--version", "v1.3.9", "--mode", "scan", "--json"],
    )
    assert scan.exit_code == 0, scan.stdout
    scan_payload = json.loads(scan.stdout)
    scan_id = scan_payload["items"][0]["item_id"]

    capture = runner.invoke(
        app,
        [
            "friction-intake",
            "run",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.9",
            "--mode",
            "capture",
            "--note",
            "manual queue intake should remain distinct from scanned issues",
            "--json",
        ],
    )
    assert capture.exit_code == 0, capture.stdout
    capture_payload = json.loads(capture.stdout)
    capture_id = capture_payload["items"][0]["item_id"]

    inbox = runner.invoke(app, ["friction-intake", "inbox", "--project-root", str(tmp_path), "--json"])
    assert inbox.exit_code == 0, inbox.stdout
    items = json.loads(inbox.stdout)["items"]
    by_id = {str(item.get("item_id") or ""): item for item in items}
    assert by_id[scan_id]["source_type"] == "scan"
    assert by_id[capture_id]["source_type"] == "manual_capture"
