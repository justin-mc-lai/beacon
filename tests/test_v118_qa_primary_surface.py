from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def test_qa_run_should_write_canonical_and_legacy_status(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "qa",
            "run",
            "unit",
            "--project",
            str(tmp_path),
            "--unit-command",
            "python3 -c \"print('ok')\"",
        ],
    )
    assert result.exit_code == 0, result.stdout
    canonical = tmp_path / ".beacon" / "qa" / "status.json"
    legacy = tmp_path / ".beacon" / "auto-test-status.json"
    assert canonical.exists()
    assert legacy.exists()
    canonical_payload = json.loads(canonical.read_text(encoding="utf-8"))
    legacy_payload = json.loads(legacy.read_text(encoding="utf-8"))
    assert canonical_payload["status"] == "passed"
    assert legacy_payload["status"] == "passed"


def test_qa_session_save_list_use_and_show(tmp_path: Path):
    save = runner.invoke(
        app,
        [
            "qa",
            "session",
            "save",
            "uat-admin",
            "--project",
            str(tmp_path),
            "--origin",
            "https://example.test",
            "--runner-type",
            "browser-use",
            "--profile-ref",
            "Default",
            "--cookies-ref",
            ".beacon/qa/sessions/uat-admin/cookies.json",
            "--storage-state-ref",
            ".beacon/qa/sessions/uat-admin/storage-state.json",
            "--scope",
            "admin",
            "--scope",
            "dashboard",
            "--json",
        ],
    )
    assert save.exit_code == 0, save.stdout
    save_payload = json.loads(save.stdout)
    assert save_payload["session_id"] == "uat-admin"
    manifest = tmp_path / save_payload["manifest"]
    assert manifest.exists()

    listing = runner.invoke(app, ["qa", "session", "list", "--project", str(tmp_path), "--json"])
    assert listing.exit_code == 0, listing.stdout
    list_payload = json.loads(listing.stdout)
    assert list_payload["current_session_id"] == "uat-admin"
    assert len(list_payload["sessions"]) == 1

    show = runner.invoke(app, ["qa", "session", "show", "--project", str(tmp_path), "--json"])
    assert show.exit_code == 0, show.stdout
    show_payload = json.loads(show.stdout)
    assert show_payload["origin"] == "https://example.test"
    assert show_payload["runner_type"] == "browser-use"
