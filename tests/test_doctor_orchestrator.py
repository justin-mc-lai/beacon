from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.doctor_orchestrator import run_context_setup, run_context_verify
from beacon.utils.doctor_registry import get_doctor_registry


def test_doctor_registry_should_expose_all_migrated_doctor_handlers():
    registry = get_doctor_registry()
    assert {
        "diagnostics.run.payload",
        "diagnostics.advise.next-step",
        "launcher.setup.install",
        "launcher.uninstall.remove",
        "context.setup.managed-files",
        "context.setup.onboarding-state",
        "context.verify.managed-files",
        "context.sync.gitignore",
        "context.verify.gitignore",
        "materials.sync.requirement-materials",
        "materials.sync.requirement-clarity",
        "materials.sync.technical-review-contract",
        "materials.verify.material-audit",
        "runtime.verify.subagent-runtime",
        "runtime.verify.subagent-delegation",
        "projection.verify.runtime-ledger",
        "projection.export.runtime-ledger",
        "projection.rebuild.runtime-ledger",
        "delivery.verify.audit",
        "package.repair.v115-delivery",
        "package.upgrade.version-package",
        "package.verify.source-architecture-status",
        "host.quiet-worktree.manage",
        "host.setup.codex-hud-hook",
        "host.verify.codex-hud-hook",
    }.issubset(registry.keys())


def test_run_context_setup_should_compose_gitignore_and_onboarding_actions(tmp_path: Path):
    execution = run_context_setup(
        project_root=str(tmp_path),
        dry_run=False,
        force=False,
        sync_materials=False,
        feature="",
        all_features=True,
        overwrite_test_doc=False,
        with_claude=True,
        with_agents=True,
        with_gitignore=True,
    )

    assert execution.exit_code == 0
    payload = execution.payload
    assert payload["action"] == "setup-context"
    actions = payload["result"]["actions"]
    assert any(item["file"] == ".gitignore" for item in actions)
    assert any(item["file"] == ".beacon/state/project-onboarding.json" for item in actions)
    onboarding = json.loads((tmp_path / ".beacon" / "state" / "project-onboarding.json").read_text(encoding="utf-8"))
    assert onboarding["runtime_version"] == payload["runtime_version"]


def test_run_context_verify_should_merge_gitignore_check_into_context_result(tmp_path: Path):
    run_context_setup(
        project_root=str(tmp_path),
        dry_run=False,
        force=False,
        sync_materials=False,
        feature="",
        all_features=True,
        overwrite_test_doc=False,
        with_claude=True,
        with_agents=True,
        with_gitignore=True,
    )

    execution = run_context_verify(
        project_root=str(tmp_path),
        strict=False,
        with_gitignore=True,
    )

    assert execution.exit_code == 0
    checks = execution.payload["result"]["checks"]
    assert any(item["name"] == "beacon_gitignore_policy" for item in checks)
