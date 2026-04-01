from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
implement_cmd = importlib.import_module("beacon.commands.implement")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _init_git_repo(root: Path, *, version: str) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", f"beacon/{version}"], cwd=root, check=True, capture_output=True, text=True)


def _seed_feature_docs(root: Path, *, version: str = "v1.1.4", feature: str = "my feature") -> str:
    slug = feature.lower().replace(" ", "-")
    if not (root / ".git").exists():
        _init_git_repo(root, version=version)
    base = root / "docs" / "beacon" / version
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "user-story" / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
    (base / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    return slug


def _write_runner_script(path: Path, *, write_result: bool = True) -> None:
    path.write_text(
        (
            "import json, sys, pathlib\n"
            "request_file = pathlib.Path(sys.argv[1])\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "payload = json.loads(request_file.read_text())\n"
            "if " + ("True" if write_result else "False") + ":\n"
            "  result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "  result_file.write_text(json.dumps({\n"
            "    'schema_version':'1.0',\n"
            "    'run_id': payload['run_id'],\n"
            "    'status':'completed',\n"
            "    'summary':'runner finished',\n"
            "    'changed_files':['beacon/commands/implement.py'],\n"
            "    'verification':[{'command':'pytest -q','status':'passed'}],\n"
            "    'artifact_updates':{'prd':{'required':False}}\n"
            "  }, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )


def _write_sleep_runner_script(path: Path) -> None:
    path.write_text(
        (
            "import time\n"
            "time.sleep(0.2)\n"
        ),
        encoding="utf-8",
    )


def _write_invalid_result_runner_script(path: Path) -> None:
    path.write_text(
        (
            "import sys, pathlib\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "result_file.write_text('{not-json}\\n', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )


def test_implement_list_runners_should_show_preferred(tmp_path: Path):
    (tmp_path / "beacon.config.yaml").write_text(
        "skill:\n  preferred: omx\n",
        encoding="utf-8",
    )
    result = _invoke(["implement", "list-runners", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["preferred"] == "omx"
    ids = {item["id"] for item in payload["runners"]}
    assert {"omx", "omc", "gstack"} <= ids


def test_implement_run_dry_run_should_write_request_and_state(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "omx",
            "--dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "dry_run"
    assert payload["command"][:5] == ["omx", "exec", "--full-auto", "--cd", str(tmp_path)]
    assert "--skip-git-repo-check" in payload["command"]
    run_id = payload["run_id"]
    assert (tmp_path / ".beacon" / "implement" / run_id / "state.json").exists()
    assert (tmp_path / ".beacon" / "implement" / run_id / "request.json").exists()


def test_implement_run_handoff_should_write_markdown_request(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    (tmp_path / ".claude" / "skills" / "gstack").mkdir(parents=True, exist_ok=True)
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "gstack",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "handoff_required"
    assert (tmp_path / payload["request_markdown"]).exists()
    assert not (tmp_path / ".beacon" / "state" / "implementation-my-feature.json").exists()


def test_implement_run_command_runner_should_write_marker_summary_and_review(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_runner_script(script)
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert (tmp_path / ".beacon" / "state" / "implementation-my-feature.json").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.4" / "execution" / "implementation-summary-my-feature.json").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.4" / "execution" / "review-spec-my-feature.json").exists()


def test_implement_run_should_fail_when_result_missing(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_runner_script(script, write_result=False)
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_result_missing"


def test_implement_run_should_fail_when_result_json_is_unparseable(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    script.write_text(
        (
            "import sys, pathlib\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "result_file.write_text('{bad json', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_result_invalid"


def test_implement_run_should_fail_when_runner_times_out(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_sleep_runner_script(script)
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      timeout_sec: 0.01\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_execution_timeout"


def test_implement_run_should_fail_when_result_is_invalid_json(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_invalid_result_runner_script(script)
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_result_invalid"
    assert "result json parse failed" in payload["problems"][0]


def test_implement_check_branch_should_block_when_current_branch_is_not_version_branch(tmp_path: Path):
    _init_git_repo(tmp_path, version="v1.1.4")
    subprocess.run(["git", "switch", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    result = _invoke(
        [
            "implement",
            "check-branch",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["expected_branch"] == "beacon/v1.1.4"
    assert payload["current_branch"] == "main"


def test_implement_run_should_block_before_runner_when_branch_mismatched(tmp_path: Path):
    _init_git_repo(tmp_path, version="v1.1.4")
    subprocess.run(["git", "switch", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    _seed_feature_docs(tmp_path, feature="My Feature")
    subprocess.run(["git", "switch", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "omx",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "implement_branch_guard_blocked"
    assert payload["expected_branch"] == "beacon/v1.1.4"
    assert payload["current_branch"] == "main"


def test_implement_check_branch_should_auto_switch_when_explicitly_requested(tmp_path: Path):
    _init_git_repo(tmp_path, version="v1.1.4")
    subprocess.run(["git", "switch", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    result = _invoke(
        [
            "implement",
            "check-branch",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--auto-switch-branch",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["current_branch"] == "beacon/v1.1.4"
    assert payload["switch_attempt"]["status"] == "switched"


def test_implement_run_should_support_auto_review_quality_and_status_surface(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_runner_script(script)
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text('{"status":"passed"}\n', encoding="utf-8")
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--auto-review-quality",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["review_quality"]["exit_code"] == 0
    assert (tmp_path / "docs" / "beacon" / "v1.1.4" / "execution" / "review-quality-my-feature.json").exists()

    status = _invoke(
        [
            "implement",
            "status",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--json",
        ]
    )
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["summary_exists"] is True
    assert status_payload["review_spec_exists"] is True
    assert status_payload["review_quality_exists"] is True
    assert status_payload["implementation_marker_exists"] is True


def test_run_auto_qa_sequence_should_follow_supported_handoff_and_rerun(monkeypatch, tmp_path: Path):
    calls: list[tuple[str, str]] = []
    qa_payloads = [
        (
            2,
            {
                "feature_scorecard": {
                    "continue_decision": "continue",
                    "repair_handoff": {
                        "action": "test-case-create",
                        "command": 'beacon test-case create "My Feature" --project-root /tmp/demo --version v1.1.10',
                    },
                }
            },
        ),
        (
            0,
            {
                "feature_scorecard": {
                    "continue_decision": "ready_for_release",
                    "repair_handoff": {
                        "action": "release-check",
                        "command": "beacon gate check release --project-root /tmp/demo --version v1.1.10",
                    },
                }
            },
        ),
    ]

    def _fake_run_auto_qa(project_root: Path, *, feature: str, version: str, extra_args: list[str]):
        calls.append(("qa", feature))
        return qa_payloads.pop(0)

    def _fake_run_beacon_json_command(project_root: Path, command: str):
        calls.append(("handoff", command))
        return 0, {"status": "generated"}

    monkeypatch.setattr(implement_cmd, "_run_auto_qa", _fake_run_auto_qa)
    monkeypatch.setattr(implement_cmd, "_run_beacon_json_command", _fake_run_beacon_json_command)

    exit_code, payload = implement_cmd._run_auto_qa_sequence(  # type: ignore[attr-defined]
        tmp_path,
        feature="My Feature",
        version="v1.1.10",
        extra_args=["--mode", "story-exhaustive"],
        follow_handoff=True,
        max_rounds=3,
    )
    assert exit_code == 0
    assert payload["follow_handoff"] is True
    assert payload["max_rounds"] == 3
    assert len(payload["history"]) == 3
    assert calls[0] == ("qa", "My Feature")
    assert calls[1][0] == "handoff"
    assert calls[2] == ("qa", "My Feature")


def test_run_auto_qa_sequence_should_not_follow_handoff_when_disabled(monkeypatch, tmp_path: Path):
    calls: list[str] = []

    def _fake_run_auto_qa(project_root: Path, *, feature: str, version: str, extra_args: list[str]):
        calls.append("qa")
        return 2, {
            "feature_scorecard": {
                "continue_decision": "continue",
                "repair_handoff": {
                    "action": "test-case-create",
                    "command": 'beacon test-case create "My Feature" --project-root /tmp/demo --version v1.1.10',
                },
            }
        }

    def _fake_run_beacon_json_command(project_root: Path, command: str):
        calls.append("handoff")
        return 0, {"status": "generated"}

    monkeypatch.setattr(implement_cmd, "_run_auto_qa", _fake_run_auto_qa)
    monkeypatch.setattr(implement_cmd, "_run_beacon_json_command", _fake_run_beacon_json_command)

    exit_code, payload = implement_cmd._run_auto_qa_sequence(  # type: ignore[attr-defined]
        tmp_path,
        feature="My Feature",
        version="v1.1.10",
        extra_args=[],
        follow_handoff=False,
        max_rounds=3,
    )
    assert exit_code == 2
    assert payload["follow_handoff"] is False
    assert calls == ["qa"]


def test_implement_run_should_fail_when_runner_times_out(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    script.write_text(
        (
            "import time\n"
            "time.sleep(2)\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--timeout-sec",
            "1",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_execution_timeout"
