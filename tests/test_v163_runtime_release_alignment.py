"""Tests for beacon-runtime-release-alignment-v163.

Covers: release gate blocks runtime!=docs drift; post-release hook adds
runtime_alignment step routing to sync-version-surfaces; dev stages unaffected.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import beacon.utils.project_hooks as project_hooks_mod
from beacon.commands.gate import GateMode


def _stub_heavy() -> dict:
    import beacon.utils.doctor_orchestrator as doc
    import beacon.utils.agent_surface as asurf
    patchers = [
        patch.object(doc, "run_legacy_beacon_skills_cleanup", return_value=type("R", (), {"payload": {"result": {}}})()),
        patch.object(asurf, "install_global_agents_beacon_skills", return_value={"status": "pass"}),
        patch.object(asurf, "verify_global_agents_beacon_skills", return_value={"status": "pass"}),
        patch.object(asurf, "install_global_claude_beacon_skills", return_value={"status": "pass"}),
        patch.object(asurf, "verify_global_claude_beacon_skills", return_value={"status": "pass"}),
        patch.object(doc, "run_agent_surface_setup", return_value=type("R", (), {"exit_code": 0, "payload": {"status": "PASS", "result": {}}})()),
        patch.object(doc, "run_agent_surface_verify", return_value=type("R", (), {"exit_code": 0, "payload": {"status": "PASS", "result": {}}})()),
        patch.object(doc, "run_launcher_setup", return_value=type("R", (), {"exit_code": 0, "payload": {"status": "PASS"}})()),
        patch.object(project_hooks_mod, "is_live_runner_admitted", return_value=False),
        patch.object(project_hooks_mod, "_command_output", return_value={"status": "pass", "stdout": project_hooks_mod.__toolkit_version__}),
    ]
    for p in patchers:
        p.start()
    return {"patchers": patchers}


# ---- AC-001 release gate blocks drift ----

def test_release_gate_blocks_drift(tmp_path: Path) -> None:
    """release stage runtime != docs -> critical block runtime_docs_release_drift."""
    from beacon.commands.gate import check_runtime_release_alignment
    # runtime v1.6.1, docs target v1.6.3 -> drift
    issues = check_runtime_release_alignment(
        tmp_path, GateMode.STRICT, "release", version="v1.6.3",
        runtime_version="v1.6.1", docs_version="v1.6.3",
    )
    codes = [i.get("reason_code") for i in issues]
    assert "runtime_docs_release_drift" in codes, codes
    assert any(i.get("blocked") for i in issues if i.get("reason_code") == "runtime_docs_release_drift")


# ---- AC-002 release gate pass when aligned ----

def test_release_gate_pass_when_aligned(tmp_path: Path) -> None:
    """runtime == docs -> no drift block."""
    from beacon.commands.gate import check_runtime_release_alignment
    issues = check_runtime_release_alignment(
        tmp_path, GateMode.STRICT, "release", version="v1.6.3",
        runtime_version="v1.6.3", docs_version="v1.6.3",
    )
    codes = [i.get("reason_code") for i in issues]
    assert "runtime_docs_release_drift" not in codes, codes


# ---- AC-003 hook runtime_alignment field ----

def test_hook_runtime_alignment_field(tmp_path: Path) -> None:
    """hook payload contains runtime_alignment field."""
    state = _stub_heavy()
    try:
        payload = project_hooks_mod._run_beacon_post_release_local_install(
            tmp_path, version="v1.6.3", feature="demo"
        )
    finally:
        for p in state["patchers"]:
            p.stop()
    ra = payload.get("runtime_alignment")
    assert ra is not None, "runtime_alignment missing from payload"
    assert "runtime_version" in ra
    assert "docs_version" in ra
    assert "aligned" in ra
    assert "recommended_command" in ra


# ---- AC-004 hook routes sync-version-surfaces ----

def test_hook_routes_sync_version_surfaces(tmp_path: Path) -> None:
    """runtime != docs -> recommended_command contains sync-version-surfaces."""
    state = _stub_heavy()
    # force runtime != docs by patching __toolkit_version__
    with patch.object(project_hooks_mod, "__toolkit_version__", "v1.6.1"):
        try:
            payload = project_hooks_mod._run_beacon_post_release_local_install(
                tmp_path, version="v1.6.3", feature="demo"
            )
        finally:
            for p in state["patchers"]:
                p.stop()
    ra = payload.get("runtime_alignment", {})
    assert ra.get("aligned") is False, ra
    assert "sync-version-surfaces" in str(ra.get("recommended_command", "")), ra


# ---- AC-005 dev stages no block ----

def test_dev_stages_no_block(tmp_path: Path) -> None:
    """plan/qa stage runtime != docs -> no drift block."""
    from beacon.commands.gate import check_runtime_release_alignment
    for stage in ("plan", "qa", "implement", "truth"):
        issues = check_runtime_release_alignment(
            tmp_path, GateMode.STRICT, stage, version="v1.6.3",
            runtime_version="v1.6.1", docs_version="v1.6.3",
        )
        codes = [i.get("reason_code") for i in issues]
        assert "runtime_docs_release_drift" not in codes, f"{stage}: {codes}"


# ---- AC-006 no auto pip install ----

def test_no_auto_pip_install() -> None:
    """hook must not execute pip install (only advise in recommended_command)."""
    src = Path(project_hooks_mod.__file__).read_text(encoding="utf-8")
    # hook must not run pip install as a subprocess command argument
    import re
    # look for pip install inside actual command lists/args, not import lines
    lines = [ln for ln in src.splitlines() if "pip install" in ln and not ln.strip().startswith("#") and "recommended" not in ln.lower()]
    assert not lines, f"hook executes pip install: {lines}"


# ---- AC-007 no regression P0-1 ----

def test_no_regression_p01(tmp_path: Path) -> None:
    """P0-1 _resolve_eval_version + resolve failure fail-closed still works."""
    # resolve failure -> version_resolve_failed
    with patch.object(project_hooks_mod, "resolve_target_version", side_effect=ValueError("boom")):
        ev, err = project_hooks_mod._resolve_eval_version(tmp_path, "auto")
    assert err == "version_resolve_failed"
    assert ev == ""
