"""Doctor-managed Codex HUD hook wiring contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str], *, input_text: str = "", env: dict[str, str] | None = None):
    return runner.invoke(app, args, input=input_text, env=env)


def test_setup_codex_hud_hook_defaults_to_dry_run(monkeypatch, tmp_path: Path):
    fake_home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(fake_home))

    result = _invoke(
        [
            "doctor",
            "setup-codex-hud-hook",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    setup = payload["result"]

    assert payload["action"] == "setup-codex-hud-hook"
    assert setup["mode"] == "dry-run"
    assert setup["restart_required"] is False
    assert all(item["action"] in {"planned", "would_update"} for item in setup["actions"])
    assert not (tmp_path / "plugins" / "beacon-fixed-hud").exists()
    assert not (tmp_path / ".agents" / "plugins" / "marketplace.json").exists()


def test_setup_and_verify_codex_hud_hook_should_write_managed_files(monkeypatch, tmp_path: Path):
    fake_home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(fake_home))

    setup = _invoke(
        [
            "doctor",
            "setup-codex-hud-hook",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--apply",
            "--json",
        ]
    )
    assert setup.exit_code == 0, setup.stdout
    setup_payload = json.loads(setup.stdout)["result"]

    plugin_root = tmp_path / "plugins" / "beacon-fixed-hud"
    marketplace_json = tmp_path / ".agents" / "plugins" / "marketplace.json"
    plugin_json = plugin_root / ".codex-plugin" / "plugin.json"
    hooks_json = plugin_root / "hooks.json"
    dispatch_script = plugin_root / "scripts" / "dispatch.sh"
    install_doc = plugin_root / "INSTALL.md"

    assert marketplace_json.exists()
    assert plugin_json.exists()
    assert hooks_json.exists()
    assert dispatch_script.exists()
    assert install_doc.exists()
    assert setup_payload["restart_required"] is True

    marketplace_payload = json.loads(marketplace_json.read_text(encoding="utf-8"))
    assert any(
        isinstance(item, dict) and item.get("name") == "beacon-fixed-hud"
        for item in marketplace_payload.get("plugins", [])
    )

    plugin_payload = json.loads(plugin_json.read_text(encoding="utf-8"))
    assert plugin_payload["hooks"] == "./hooks.json"

    hooks_payload = json.loads(hooks_json.read_text(encoding="utf-8"))
    assert sorted(hooks_payload["hooks"].keys()) == [
        "SessionRefresh",
        "SessionResume",
        "SessionStart",
        "UserPromptSubmit",
    ]
    dispatch_text = dispatch_script.read_text(encoding="utf-8")
    assert "# beacon-doctor-managed: true" in dispatch_text
    assert f"# beacon-doctor-project-root: {tmp_path}" in dispatch_text
    assert "# beacon-doctor-version: v1.3.3" in dispatch_text
    assert 'export BEACON_CODEX_HUD_ACTIVATION_SOURCE="doctor-managed-dispatch"' in dispatch_text
    assert "debug codex-fixed-hud" in dispatch_text

    verify = _invoke(
        [
            "doctor",
            "verify-codex-hud-hook",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert verify.exit_code == 0, verify.stdout
    verify_payload = json.loads(verify.stdout)
    assert verify_payload["status"] == "WARN"
    assert verify_payload["result"]["runtime"]["state"] == "activation_unproven"
    checks = verify_payload["result"]["checks"]
    assert checks
    required_checks = [item for item in checks if item.get("required", True)]
    optional_checks = [item for item in checks if not item.get("required", True)]
    assert required_checks and all(item["ok"] for item in required_checks)
    assert optional_checks and any(not item["ok"] for item in optional_checks)

    hook_payload = {
        "hook_event_name": "SessionRefresh",
        "session_id": "session-live-001",
    }
    debug = _invoke(
        [
            "debug",
            "codex-fixed-hud",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--feature",
            "beacon-v1.3.3-minimal-hud-scenarios-and-implementation",
        ],
        input_text=json.dumps(hook_payload, ensure_ascii=False),
        env={"BEACON_CODEX_HUD_ACTIVATION_SOURCE": "doctor-managed-dispatch"},
    )
    assert debug.exit_code == 0, debug.stdout

    reverify = _invoke(
        [
            "doctor",
            "verify-codex-hud-hook",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert reverify.exit_code == 0, reverify.stdout
    reverify_payload = json.loads(reverify.stdout)
    assert reverify_payload["status"] == "PASS"
    assert reverify_payload["result"]["runtime"]["state"] == "active"
    assert all(item["ok"] for item in reverify_payload["result"]["checks"])


def test_verify_codex_hud_hook_should_block_when_wiring_missing(monkeypatch, tmp_path: Path):
    fake_home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(fake_home))

    result = _invoke(
        [
            "doctor",
            "verify-codex-hud-hook",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED"
    assert any(not item["ok"] for item in payload["result"]["checks"])


def test_verify_codex_hud_hook_should_warn_on_stale_user_scope_shadow(monkeypatch, tmp_path: Path):
    fake_home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(fake_home))

    user_plugin_root = fake_home / ".codex" / "beacon-fixed-hud"
    (user_plugin_root / "hooks").mkdir(parents=True, exist_ok=True)
    (user_plugin_root / ".codex").mkdir(parents=True, exist_ok=True)
    (user_plugin_root / "hooks" / "hooks.json").write_text(
        json.dumps(
            {
                "description": "stale user plugin",
                "hooks": {
                    "UserPromptSubmit": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash stale.sh"}]}],
                    "SessionStart": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash stale.sh"}]}],
                    "SessionResume": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash stale.sh"}]}],
                    "SessionRefresh": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash stale.sh"}]}],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (user_plugin_root / "hooks" / "dispatch.sh").write_text(
        "#!/usr/bin/env bash\n"
        "# beacon-doctor-managed: true\n"
        "# beacon-doctor-project-root: .\n"
        "# beacon-doctor-version: v1.3.3\n"
        "set -euo pipefail\n"
        "exec bash /Users/apple/Developer/Personal/products/beacon/skills/beacon/scripts/run_beacon.sh "
        "debug codex-fixed-hud --project-root . --version v1.3.3 --json\n",
        encoding="utf-8",
    )
    (user_plugin_root / ".codex" / "INSTALL.md").write_text(
        "# Beacon Codex Fixed HUD Hook\n\n"
        "- project_root: `.`\n"
        "- version: `v1.3.3`\n",
        encoding="utf-8",
    )

    setup = _invoke(
        [
            "doctor",
            "setup-codex-hud-hook",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--apply",
            "--json",
        ]
    )
    assert setup.exit_code == 0, setup.stdout

    debug = _invoke(
        [
            "debug",
            "codex-fixed-hud",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--feature",
            "beacon-v1.3.3-minimal-hud-scenarios-and-implementation",
        ],
        input_text=json.dumps({"hook_event_name": "SessionRefresh", "session_id": "shadow-check"}, ensure_ascii=False),
        env={"BEACON_CODEX_HUD_ACTIVATION_SOURCE": "doctor-managed-dispatch"},
    )
    assert debug.exit_code == 0, debug.stdout

    verify = _invoke(
        [
            "doctor",
            "verify-codex-hud-hook",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert verify.exit_code == 0, verify.stdout
    payload = json.loads(verify.stdout)
    assert payload["status"] == "WARN"
    assert payload["result"]["runtime"]["state"] == "shadow_risk"

    checks = {item["name"]: item for item in payload["result"]["checks"]}
    assert checks["user_scope_plugin_dispatch_targets_project"]["ok"] is False
    assert checks["user_scope_plugin_dispatch_activation_source_export"]["ok"] is False
    assert checks["user_scope_plugin_install_doc_targets_project"]["ok"] is False
