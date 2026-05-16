from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.automation_scaffold import init_automation_scaffold


runner = CliRunner()


def test_automation_init_scaffold_should_generate_project_local_assets(tmp_path: Path) -> None:
    payload = init_automation_scaffold(tmp_path)

    assert payload["status"] == "completed"
    assert payload["queue_validation"]["status"] == "valid"
    assert payload["executor"] == "codex"
    assert payload["beacon_bin"]
    assert (tmp_path / "automation" / ".env").exists() is False

    queue_path = tmp_path / "automation" / "beacon-automation-queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    assert queue["project_root"] == str(tmp_path.resolve())
    assert [job["job_id"] for job in queue["jobs"]] == [
        "beacon-morning-status",
        "beacon-nightly-qa",
        "beacon-gated-implement",
    ]

    qa_wrapper = tmp_path / "automation" / "jobs" / "beacon-qa-job.sh"
    qa_text = qa_wrapper.read_text(encoding="utf-8")
    assert 'BEACON_BIN="beacon"' in qa_text
    assert "automation summarize-qa" in qa_text
    assert "automation update-queue" in qa_text
    assert "nightly QA window closed, skipping" in qa_text
    assert "send_summary_notification" in qa_text
    assert 'CANONICAL_LEDGER_PATH="${PROJECT_ROOT}/.beacon/automation/qa-feedback-ledger.json"' in qa_text
    assert 'cp "${LEDGER_ARTIFACT_PATH}" "${CANONICAL_LEDGER_PATH}"' in qa_text
    assert 'ENV_FILE="${ROOT_DIR}/automation/.env"' in qa_text
    assert 'FEISHU_WEBHOOK="${AUTOMATION_FEISHU_WEBHOOK:-}"' in qa_text
    assert 'NOTIFY_HELPER="${ROOT_DIR}/automation/jobs/beacon-notify-feishu-post.py"' in qa_text
    assert "automation build-summary" in qa_text
    assert 'SUMMARY_PATH="${OUTPUT_DIR}/qa-summary-${TIMESTAMP}.json"' in qa_text
    assert "SUMMARY_FEATURE_ARGS" not in qa_text
    assert os.access(qa_wrapper, os.X_OK)

    status_wrapper = tmp_path / "automation" / "jobs" / "beacon-status-job.sh"
    status_text = status_wrapper.read_text(encoding="utf-8")
    assert "automation build-summary" in status_text
    assert 'SUMMARY_PATH="${OUTPUT_DIR}/status-summary-${TIMESTAMP}.json"' in status_text
    assert "send_summary_notification" in status_text

    hourly_wrapper = tmp_path / "automation" / "jobs" / "beacon-hourly-qa-job.sh"
    hourly_text = hourly_wrapper.read_text(encoding="utf-8")
    assert "qa-global.lock" in hourly_text
    assert "automation summarize-qa" in hourly_text
    assert "automation update-queue" in hourly_text
    assert "hourly QA window closed, skipping" in hourly_text
    assert "send_summary_notification" in hourly_text
    assert "--summary-kind hourly" in hourly_text
    assert os.access(hourly_wrapper, os.X_OK)

    implement_wrapper = tmp_path / "automation" / "jobs" / "beacon-gated-implement-job.sh"
    implement_text = implement_wrapper.read_text(encoding="utf-8")
    assert "implement run" in implement_text
    assert "implement dev-run" not in implement_text
    assert '--mode "${MODE}"' in implement_text
    assert '--runner "${RUNNER}"' in implement_text
    assert '--auto-qa' in implement_text
    assert 'automation summarize-qa' in implement_text
    assert 'automation build-summary' in implement_text
    assert 'SUMMARY_PATH="${OUTPUT_DIR}/implement-summary-${TIMESTAMP}.json"' in implement_text
    assert '"${SUMMARY_FEATURE_ARGS[@]}"' in implement_text
    assert os.access(implement_wrapper, os.X_OK)

    repair_wrapper = tmp_path / "automation" / "jobs" / "beacon-repair-window-job.sh"
    repair_text = repair_wrapper.read_text(encoding="utf-8")
    assert "Repair window requires exactly one enabled implement feature" in repair_text
    assert "Refusing repair window on dirty worktree" in repair_text
    assert "--allow-dirty" in repair_text
    assert "implement run" in repair_text
    assert "qa run" in repair_text
    assert "automation update-queue" in repair_text
    assert "send_summary_notification" in repair_text
    assert os.access(repair_wrapper, os.X_OK)

    env_example = tmp_path / "automation" / ".env.example"
    assert "AUTOMATION_FEISHU_WEBHOOK=" in env_example.read_text(encoding="utf-8")

    notify_helper = tmp_path / "automation" / "jobs" / "beacon-notify-feishu-post.py"
    notify_text = notify_helper.read_text(encoding="utf-8")
    assert '"msg_type": "post"' in notify_text
    assert os.access(notify_helper, os.X_OK)
    assert 'notification.get("lines")' in notify_text
    assert 'reconciliation_summary' in notify_text

    prompt = (tmp_path / "automation" / "codex" / "nightly-qa.md").read_text(encoding="utf-8")
    assert str(tmp_path.resolve()) in prompt
    assert str(queue_path) in prompt

    project_slug = tmp_path.resolve().name.lower().replace("_", "-")
    launchd_files = sorted(path.name for path in (tmp_path / "automation" / "launchd").glob("*.plist"))
    assert launchd_files == [
        f"com.beacon.{project_slug}.gated-implement.plist",
        f"com.beacon.{project_slug}.hourly-qa.plist",
        f"com.beacon.{project_slug}.morning-status.plist",
        f"com.beacon.{project_slug}.nightly-qa.plist",
        f"com.beacon.{project_slug}.repair-window.plist",
    ]
    launchd_text = "\n".join((tmp_path / "automation" / "launchd" / name).read_text(encoding="utf-8") for name in launchd_files)
    assert str(tmp_path.resolve()) in launchd_text
    assert str(tmp_path / ".beacon" / "automation-runs") in launchd_text
    assert "<string>--beacon-bin</string>" in launchd_text
    assert "<string>--env-file</string>" in launchd_text
    assert "<key>StartInterval</key>" in launchd_text
    assert "<integer>3600</integer>" in launchd_text


def test_automation_init_should_not_overwrite_existing_files_without_force(tmp_path: Path) -> None:
    init_automation_scaffold(tmp_path)
    queue_path = tmp_path / "automation" / "beacon-automation-queue.json"
    custom_text = "{\n  \"sentinel\": true\n}\n"
    queue_path.write_text(custom_text, encoding="utf-8")

    payload = init_automation_scaffold(tmp_path, force=False)

    assert payload["unchanged_count"] >= 1
    assert queue_path.read_text(encoding="utf-8") == custom_text


def test_automation_init_should_refresh_existing_files_with_force(tmp_path: Path) -> None:
    init_automation_scaffold(tmp_path)
    queue_path = tmp_path / "automation" / "beacon-automation-queue.json"
    queue_path.write_text("{\n  \"sentinel\": true\n}\n", encoding="utf-8")

    payload = init_automation_scaffold(tmp_path, force=True)
    queue = json.loads(queue_path.read_text(encoding="utf-8"))

    assert payload["refreshed_count"] >= 1
    assert queue["project_root"] == str(tmp_path.resolve())
    assert queue["version"] == "v0"


def test_automation_init_cli_should_support_json_output(tmp_path: Path) -> None:
    result = runner.invoke(app, ["automation", "init", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["queue_validation"]["status"] == "valid"
    assert any(label.endswith(".nightly-qa") for label in payload["launchd_labels"])
    assert any(label.endswith(".hourly-qa") for label in payload["launchd_labels"])
    assert any(label.endswith(".repair-window") for label in payload["launchd_labels"])
    assert payload["toolkit"]["skill"] == "beacon-toolkit-automation"
    assert payload["readme_path"].endswith("automation/README.md")
    assert any("beacon automation validate-queue" in step for step in payload["next_steps"])


def test_automation_init_should_support_non_codex_executor_profiles(tmp_path: Path) -> None:
    payload = init_automation_scaffold(tmp_path, executor="cursor")
    queue = json.loads((tmp_path / "automation" / "beacon-automation-queue.json").read_text(encoding="utf-8"))

    assert payload["executor"] == "cursor"
    assert payload["executor_capability"]["status"] == "supported-via-adapter"
    assert queue["jobs"][0]["target_agent"] == "cursor"
    prompt = (tmp_path / "automation" / "generic" / "nightly-qa.md").read_text(encoding="utf-8")
    assert "Do not claim native Beacon host-runtime support" in prompt
    readme = (tmp_path / "automation" / "README.md").read_text(encoding="utf-8")
    assert "$beacon:beacon-toolkit-automation" in readme


def test_automation_init_human_output_should_show_toolkit_and_next_steps(tmp_path: Path) -> None:
    result = runner.invoke(app, ["automation", "init", "--project-root", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    assert "## Toolkit" in result.stdout
    assert "## Next Steps" in result.stdout
    assert "beacon-toolkit-automation" in result.stdout
    assert "beacon automation validate-queue" in result.stdout
