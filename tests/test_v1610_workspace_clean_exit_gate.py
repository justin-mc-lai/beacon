from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.qa import _formal_qa_evidence_refs
from beacon.main import app
from beacon.utils.agent_trace import append_event, build_event, record_lifecycle_stage_trace
from beacon.utils.project_hooks import _run_beacon_post_release_local_install
from beacon.utils.workspace_clean import (
    DIRTY_MANIFEST,
    artifact_role_for_path,
    build_trace_digest,
    validate_formal_evidence_manifest,
    validate_task_evidence,
    verify_clean_workspace,
)


VERSION = "v1.6.10"
FEATURE = "workspace-clean-exit-gate-v1610"


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)


def _init_repo(root: Path) -> None:
    _git(root, "init")
    _git(root, "config", "user.email", "beacon@example.test")
    _git(root, "config", "user.name", "Beacon Test")
    (root / "README.md").write_text("beacon\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "init")


def _commit_all(root: Path, message: str = "commit") -> None:
    _git(root, "add", ".")
    result = _git(root, "commit", "-m", message)
    assert result.returncode == 0, result.stderr


def test_verify_clean_workspace_classifies_full_git_status(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    truth = tmp_path / "docs/beacon/v1.6.10/features/f/truth.md"
    truth.parent.mkdir(parents=True)
    truth.write_text("truth\n", encoding="utf-8")
    _commit_all(tmp_path, "truth")
    truth.write_text("truth changed\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/app.py").write_text("print('dirty')\n", encoding="utf-8")

    payload = verify_clean_workspace(tmp_path, version=VERSION, feature=FEATURE)

    roles = {entry["path"]: entry["artifact_role"] for entry in payload["dirty_entries"]}
    assert roles["docs/beacon/v1.6.10/features/f/truth.md"] == "canonical_truth"
    assert roles["src/app.py"] == "unclassified"
    assert payload["blocked"] is True
    assert payload["reason_code"] == "workspace_dirty_unclassified"


def test_dirty_manifest_roles_cover_required_classes() -> None:
    assert {"canonical_truth", "formal_evidence", "machine_projection", "host_projection", "runtime_private", "forbidden"} <= set(DIRTY_MANIFEST)
    for role in ("canonical_truth", "formal_evidence", "machine_projection", "host_projection", "runtime_private", "forbidden"):
        assert DIRTY_MANIFEST[role]["patterns"]
        assert DIRTY_MANIFEST[role]["allowed_actions"]
    assert artifact_role_for_path(".beacon/auto-test-status.json") == "formal_evidence"
    assert artifact_role_for_path(".beacon/coverage-summary.json") == "formal_evidence"
    assert artifact_role_for_path(".beacon/evidence-manifest.json") == "formal_evidence"
    assert artifact_role_for_path(".beacon/evidence-signature-chain.json") == "formal_evidence"
    assert artifact_role_for_path(".beacon/gate-report.json") == "formal_evidence"
    assert artifact_role_for_path(".beacon/qa/status.json") == "formal_evidence"
    assert artifact_role_for_path(".beacon/release-gate-report.json") == "formal_evidence"
    assert artifact_role_for_path(".beacon/traces/run.jsonl") == "runtime_private"


def test_formal_manifest_rejects_untracked_runtime_refs(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    trace = tmp_path / ".beacon/traces/run.jsonl"
    trace.parent.mkdir(parents=True)
    trace.write_text("{}\n", encoding="utf-8")
    manifest = tmp_path / ".beacon/evidence-manifest.json"
    manifest.write_text(
        json.dumps({"manifest_role": "formal_evidence", "entries": [{"path": ".beacon/traces/run.jsonl", "sha256": "bad"}]}),
        encoding="utf-8",
    )

    payload = validate_formal_evidence_manifest(tmp_path)

    assert payload["blocked"] is True
    assert any(issue["reason_code"] == "runtime_evidence_not_formal" for issue in payload["issues"])


def test_task_evidence_promotion_gate(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    package = tmp_path / f"docs/beacon/{VERSION}/features/{FEATURE}"
    package.mkdir(parents=True)
    evidence_a = tmp_path / f".beacon/evidence/implement/{FEATURE}/AC-WC-001.json"
    evidence_b = tmp_path / f".beacon/evidence/implement/{FEATURE}/AC-WC-002.json"
    evidence_a.parent.mkdir(parents=True)
    evidence_a.write_text('{"ok": true}\n', encoding="utf-8")
    evidence_b.write_text('{"ok": true}\n', encoding="utf-8")
    (package / "tasks.md").write_text(
        "\n".join(
            [
                "# Tasks",
                f"- [x] TASK-001 · ac=AC-WC-001 · evidence=`.beacon/evidence/implement/{FEATURE}/AC-WC-001.json`",
                f"- [ ] TASK-002 · ac=AC-WC-002 · evidence=`.beacon/evidence/implement/{FEATURE}/AC-WC-002.json`",
            ]
        ),
        encoding="utf-8",
    )
    (package / "evidence.md").write_text("", encoding="utf-8")

    payload = validate_task_evidence(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["blocked"] is True
    reason_codes = {issue["reason_code"] for issue in payload["issues"]}
    assert "task_evidence_unpromoted" in reason_codes
    assert "orphan_evidence_unpromoted" in reason_codes


def test_agent_trace_redline_blocks_raw_chat_and_secrets(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    event = build_event(
        run_id="r1",
        event_type="gate_verdict",
        summary="bad raw chat",
        payload={"full_chat": "secret transcript", "chat_body": "raw"},
    )

    payload = append_event(tmp_path, event)

    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "agent_trace_redline_field"
    assert not (tmp_path / ".beacon/traces/r1.jsonl").exists()


def test_trace_digest_is_release_safe_and_raw_trace_private(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    trace = record_lifecycle_stage_trace(
        tmp_path,
        harness="qa",
        feature_slug=FEATURE,
        run_id="run-safe",
        summary="qa pass",
        payload={"chat_body": None, "result": "pass"},
    )

    digest = build_trace_digest(tmp_path, run_id="run-safe")

    assert trace["status"] == "pass"
    assert artifact_role_for_path(".beacon/traces/run-safe.jsonl") == "runtime_private"
    assert digest["status"] == "pass"
    assert digest["redaction_status"] == "pass"
    assert digest["event_count"] == 1
    assert digest["sha256"]


def test_post_release_local_install_does_not_dirty_original_root(tmp_path: Path, monkeypatch) -> None:
    _init_repo(tmp_path)

    def fake_in_place(project_root: Path, *, version: str, feature: str) -> dict:
        (project_root / "LOCAL_INSTALL_MARK").write_text(feature, encoding="utf-8")
        return {"schema_version": "1.0", "status": "pass", "blocked": False, "reason_codes": []}

    monkeypatch.setattr("beacon.utils.project_hooks._run_beacon_post_release_local_install_in_place", fake_in_place)

    payload = _run_beacon_post_release_local_install(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["status"] == "pass"
    assert payload["install_isolation"]["mode"] == "temp_worktree"
    assert payload["install_isolation"]["original_root_snapshot_delta"]["tracked_dirty_added_count"] == 0
    assert not (tmp_path / "LOCAL_INSTALL_MARK").exists()
    assert _git(tmp_path, "status", "--porcelain=v1").stdout.strip() == ""


def test_quiet_worktree_hidden_dirty_is_not_release_proof(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    tracked = tmp_path / ".beacon/evidence-manifest.json"
    tracked.parent.mkdir(parents=True)
    tracked.write_text('{"entries": []}\n', encoding="utf-8")
    _commit_all(tmp_path, "tracked runtime")
    assert _git(tmp_path, "update-index", "--skip-worktree", ".beacon/evidence-manifest.json").returncode == 0
    tracked.write_text('{"entries": [{"path": "hidden"}]}\n', encoding="utf-8")

    payload = verify_clean_workspace(tmp_path, strict=True)

    assert payload["blocked"] is True
    assert payload["reason_code"] == "skip_worktree_hidden_dirty"
    assert payload["skip_worktree_hidden_dirty"][0]["path"] == ".beacon/evidence-manifest.json"
    _git(tmp_path, "update-index", "--no-skip-worktree", ".beacon/evidence-manifest.json")


def test_illegal_skip_worktree_transition_blocks_clean_proof(tmp_path: Path) -> None:
    test_quiet_worktree_hidden_dirty_is_not_release_proof(tmp_path)


def test_host_projection_requires_policy_or_surface_sync_commit(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    projected = tmp_path / ".cursor/skills/beacon-goal/SKILL.md"
    projected.parent.mkdir(parents=True)
    projected.write_text("projected\n", encoding="utf-8")

    payload = verify_clean_workspace(tmp_path, strict=True, profile="release")

    assert payload["blocked"] is True
    assert any(issue["reason_code"] == "host_projection_requires_policy" for issue in payload["issues"])


def test_lifecycle_exits_attach_clean_gate_bundle(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    result = CliRunner().invoke(
        app,
        ["doctor", "verify-clean-workspace", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--strict", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "verify-clean-workspace"
    assert payload["result"]["schema_version"] == "workspace-clean-exit-gate.v1"
    assert payload["result"]["status"] == "pass"


def test_main_push_profile_blocks_generator_dirty(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    generated = tmp_path / f"docs/beacon/{VERSION}/.machine/execution/source.json"
    generated.parent.mkdir(parents=True)
    generated.write_text("{}", encoding="utf-8")

    payload = verify_clean_workspace(tmp_path, strict=True, profile="main-push")

    assert payload["blocked"] is True
    assert payload["dirty_entries"][0]["artifact_role"] == "machine_projection"
    assert payload["reason_code"] == "workspace_dirty_requires_resolution"


def test_clean_workspace_does_not_authorize_release(tmp_path: Path) -> None:
    _init_repo(tmp_path)

    payload = verify_clean_workspace(tmp_path, strict=True, profile="release")

    assert payload["status"] == "pass"
    assert payload.get("release_ready") is not True


def test_qa_acceptance_refs_exclude_runtime_private_paths() -> None:
    refs = _formal_qa_evidence_refs(
        [
            ".beacon/qa/status.json",
            ".beacon/release-gate-report.json",
            ".beacon/raw-command-log.jsonl",
            ".beacon/memory/workflow-lifecycle.json",
            "docs/beacon/v1.6.10/.machine/execution/qa-acceptance-feature.json",
        ]
    )

    assert ".beacon/qa/status.json" in refs
    assert ".beacon/release-gate-report.json" in refs
    assert "docs/beacon/v1.6.10/.machine/execution/qa-acceptance-feature.json" in refs
    assert ".beacon/raw-command-log.jsonl" not in refs
    assert ".beacon/memory/workflow-lifecycle.json" not in refs
