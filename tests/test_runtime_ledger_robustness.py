"""Regression for issues #22 / #26: runtime ledger must degrade, not crash.

A fresh or unwritable runtime ledger used to raise an unhandled
``sqlite3.OperationalError`` (missing ``project_metadata_current`` table, or a
read-only ledger root) from the read path.
"""

from __future__ import annotations

from pathlib import Path

from beacon.utils.project_governance import read_sqlite_projection_hash
from beacon.utils.runtime_projection_store import (
    _connect,
    runtime_ledger_probe,
)


def _fresh_ledger(monkeypatch, tmp_path: Path) -> Path:
    root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(root))
    monkeypatch.delenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", raising=False)
    return root


def test_fresh_ledger_read_returns_empty_without_raising(monkeypatch, tmp_path: Path) -> None:
    _fresh_ledger(monkeypatch, tmp_path)
    assert read_sqlite_projection_hash(tmp_path) == ""


def test_read_path_ensures_project_metadata_table(monkeypatch, tmp_path: Path) -> None:
    _fresh_ledger(monkeypatch, tmp_path)
    read_sqlite_projection_hash(tmp_path)
    with _connect() as conn:
        names = {
            str(row[0])
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
    assert "project_metadata_current" in names
    assert "project_metadata_events" in names


def test_probe_fresh_ledger_is_ok(monkeypatch, tmp_path: Path) -> None:
    _fresh_ledger(monkeypatch, tmp_path)
    assert runtime_ledger_probe()["ledger_reason_code"] == ""


def test_probe_unwritable_ledger_names_reason_and_hint(monkeypatch, tmp_path: Path) -> None:
    blocker = tmp_path / "afile"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(blocker / "ledger"))
    monkeypatch.delenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", raising=False)

    result = runtime_ledger_probe()

    assert result["ledger_reason_code"] == "runtime_ledger_unwritable"
    assert "BEACON_RUNTIME_LEDGER_ROOT" in result["ledger_hint"]


def test_probe_disabled_reports_disabled(monkeypatch, tmp_path: Path) -> None:
    _fresh_ledger(monkeypatch, tmp_path)
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", "1")
    assert runtime_ledger_probe()["ledger_reason_code"] == "runtime_ledger_disabled"
