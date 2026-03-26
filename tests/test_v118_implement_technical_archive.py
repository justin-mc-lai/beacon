from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _seed_feature_docs(root: Path, *, version: str = "v1.1.8", feature: str = "My Feature") -> str:
    slug = feature.lower().replace(" ", "-")
    base = root / "docs" / "beacon" / version
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    (base / "user-story" / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
    (base / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    return slug


def test_implement_run_should_write_technical_archive_outputs(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    script.write_text(
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
            "  'summary':'runner finished',\n"
            "  'changed_files':['app/services/uploader.py','app/models/material.py'],\n"
            "  'verification':[{'command':'pytest -q','status':'passed'}],\n"
            "  'artifact_updates':{'prd':{'required':False}},\n"
            "  'services':[{'name':'marketing_sys','role':'backend','changed_files':['app/services/uploader.py']}],\n"
            "  'db_changes':{'new_tables':['material_assets'],'altered_tables':[],'indexes':['idx_material_assets_task_id'],'migrations':['20260326_add_material_assets.py']},\n"
            "  'api_changes':{'new_endpoints':['POST /api/material/upload'],'changed_endpoints':[],'removed_endpoints':[]},\n"
            "  'config_changes':['upload.max_size'],\n"
            "  'env_changes':['MATERIAL_UPLOAD_BUCKET'],\n"
            "  'known_risks':['migration rollback needs manual cleanup'],\n"
            "  'rollback_notes':['revert migration before worker restart']\n"
            "}, ensure_ascii=False, indent=2)+'\\n', encoding='utf-8')\n"
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

    result = runner.invoke(
        app,
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.8",
            "--runner",
            "fake",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"

    machine_json = tmp_path / "docs" / "beacon" / "v1.1.8" / ".machine" / "execution" / "technical-implementation-my-feature.json"
    human_md = tmp_path / "docs" / "beacon" / "v1.1.8" / "execution" / "technical-implementation-my-feature.md"
    assert machine_json.exists()
    assert human_md.exists()

    archive = json.loads(machine_json.read_text(encoding="utf-8"))
    assert archive["feature_slug"] == "my-feature"
    assert archive["run_id"] == payload["run_id"]
    assert archive["runner"] == "fake"
    assert "git_commit" in archive
    assert archive["db_changes"]["new_tables"] == ["material_assets"]
    assert archive["api_changes"]["new_endpoints"] == ["POST /api/material/upload"]
    assert archive["env_changes"] == ["MATERIAL_UPLOAD_BUCKET"]
    assert archive["services"][0]["name"] == "marketing_sys"
