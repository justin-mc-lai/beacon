from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.artifact_paths import execution_file_output


runner = CliRunner()


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


def _seed_feature_docs(root: Path, *, version: str = "v1.1.4", feature: str = "Workflow Feature") -> str:
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


def _write_runner_script(path: Path) -> None:
    path.write_text(
        (
            "import json, sys, pathlib\n"
            "request_file = pathlib.Path(sys.argv[1])\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "payload = json.loads(request_file.read_text())\n"
            "result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "result_file.write_text(json.dumps({\n"
            "  'schema_version':'1.0',\n"
            "  'run_id': payload['run_id'],\n"
            "  'status':'completed',\n"
            "  'summary':'workflow runner finished',\n"
            "  'changed_files':['beacon/commands/workflow.py'],\n"
            "  'verification':[{'command':'pytest -q','status':'passed'}],\n"
            "  'artifact_updates':{'prd':{'required':False}}\n"
            "}, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )


def test_workflow_auto_should_delegate_implementation_to_runner(tmp_path: Path):
    feature = "Workflow Feature"
    slug = _seed_feature_docs(tmp_path, feature=feature)
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
            "implementation:\n"
            "  default_runner: fake\n"
        ),
        encoding="utf-8",
    )
    result = _invoke(
        [
            "workflow",
            "start",
            feature,
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--auto",
            "--confirm-execute",
            "--confirm-execute-second",
            "--skip",
            "think,user-story,prd,test-case,verify,gate",
        ]
    )
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / ".beacon" / "state" / f"implementation-{slug}.json").exists()
    assert execution_file_output(tmp_path, "v1.1.4", f"implementation-summary-{slug}.json").exists()


def test_workflow_should_still_block_without_command_or_runner(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Workflow Feature",
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--auto",
            "--confirm-execute",
            "--confirm-execute-second",
            "--skip",
            "think,user-story,prd,test-case,verify,gate",
        ]
    )
    assert result.exit_code != 0
    assert "implementation stage requires explicit external command execution" in result.stdout
