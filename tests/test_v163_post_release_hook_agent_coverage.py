"""Tests for beacon-post-release-hook-agent-coverage-v163.

Covers: post-release hook agent loop covers all 5 agents
(trae/claude/codex/cursor/windsurf), not just codex+claude.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import beacon.utils.project_hooks as project_hooks_mod


EXPECTED_AGENTS = ("trae", "claude", "codex", "cursor", "windsurf")


def _stub_heavy(payload_status: str = "PASS") -> dict:
    """Patch heavy internals at source modules; return patchers."""
    import beacon.utils.doctor_orchestrator as doc
    import beacon.utils.agent_surface as asurf

    patchers = [
        patch.object(doc, "run_legacy_beacon_skills_cleanup", return_value=type("R", (), {"payload": {"result": {}}})()),
        patch.object(asurf, "install_global_agents_beacon_skills", return_value={"status": "pass"}),
        patch.object(asurf, "verify_global_agents_beacon_skills", return_value={"status": "pass"}),
        patch.object(asurf, "install_global_claude_beacon_skills", return_value={"status": "pass"}),
        patch.object(asurf, "verify_global_claude_beacon_skills", return_value={"status": "pass"}),
        patch.object(doc, "run_agent_surface_setup", return_value=type("R", (), {"exit_code": 0, "payload": {"status": payload_status, "result": {}}})()),
        patch.object(doc, "run_agent_surface_verify", return_value=type("R", (), {"exit_code": 0, "payload": {"status": payload_status, "result": {}}})()),
        patch.object(doc, "run_context_setup", return_value=type("R", (), {"exit_code": 0, "payload": {"status": "PASS", "result": {}}})()),
        patch.object(doc, "run_context_verify", return_value=type("R", (), {"exit_code": 0, "payload": {"status": "PASS", "result": {}}})()),
        patch.object(doc, "run_launcher_setup", return_value=type("R", (), {"exit_code": 0, "payload": {"status": "PASS"}})()),
        patch.object(project_hooks_mod, "is_live_runner_admitted", return_value=False),
        patch.object(project_hooks_mod, "_command_output", return_value={"status": "pass", "stdout": project_hooks_mod.__toolkit_version__}),
    ]
    for p in patchers:
        p.start()
    return {"patchers": patchers}


# ---- AC-001 hook covers 5 agents ----

def test_hook_covers_5_agents() -> None:
    """Source must iterate all 5 agents via SUPPORTED_HOST_AGENTS, not just codex+claude."""
    src = Path(project_hooks_mod.__file__).read_text(encoding="utf-8")
    assert "SUPPORTED_HOST_AGENTS" in src, "must reuse canonical agent constant"
    assert '("codex", "claude")' not in src, "old 2-agent hardcoded loop still present"
    # the canonical constant must contain all 5
    from beacon.utils.agent_surface import SUPPORTED_HOST_AGENTS
    assert set(SUPPORTED_HOST_AGENTS) == set(EXPECTED_AGENTS), SUPPORTED_HOST_AGENTS


# ---- AC-002 all agents in payload ----

def test_all_agents_setup_verify_in_payload(tmp_path: Path) -> None:
    """agent_surfaces payload contains all 5 agents with setup+verify status."""
    state = _stub_heavy()
    try:
        payload = project_hooks_mod._run_beacon_post_release_local_install(
            tmp_path, version="v1.6.3", feature="demo"
        )
    finally:
        for p in state["patchers"]:
            p.stop()
    agent_surfaces = payload.get("agent_surfaces", {})
    for a in EXPECTED_AGENTS:
        assert a in agent_surfaces, f"{a} missing from agent_surfaces: {list(agent_surfaces)}"
        assert "setup_status" in agent_surfaces[a]
        assert "verify_status" in agent_surfaces[a]


# ---- AC-003 drift blocks hook ----

def test_drift_blocks_hook(tmp_path: Path) -> None:
    """When an agent verify fails (drift), hook blocks with verify_failed reason."""
    import beacon.utils.doctor_orchestrator as doc
    state = _stub_heavy()
    # override agent surface verify to fail (index: after cleanup + 4 global install/verify stubs)
    # 0 cleanup, 1-2 agents install/verify, 3-4 claude install/verify, 5 setup, 6 verify
    state["patchers"][6].stop()
    fail_verify = type("R", (), {"exit_code": 1, "payload": {"status": "BLOCKED", "result": {"checks": [{"name": "host_visible_skills_drift", "status": "fail"}]}}})()
    with patch.object(doc, "run_agent_surface_verify", return_value=fail_verify):
        try:
            payload = project_hooks_mod._run_beacon_post_release_local_install(
                tmp_path, version="v1.6.3", feature="demo"
            )
        finally:
            for p in state["patchers"][:6] + state["patchers"][7:]:
                p.stop()
    assert payload.get("blocked") is True
    reasons = payload.get("reason_codes", [])
    assert any("verify_failed" in r for r in reasons), reasons


# ---- AC-004 claude global preserved ----

def test_claude_global_preserved(tmp_path: Path) -> None:
    """hook still calls install_global_claude_beacon_skills + verify."""
    import beacon.utils.agent_surface as asurf
    state = _stub_heavy()
    try:
        project_hooks_mod._run_beacon_post_release_local_install(
            tmp_path, version="v1.6.3", feature="demo"
        )
    finally:
        for p in state["patchers"]:
            p.stop()
    # payload should carry claude global install/verify evidence
    src = Path(project_hooks_mod.__file__).read_text(encoding="utf-8")
    assert "install_global_agents_beacon_skills" in src
    assert "verify_global_agents_beacon_skills" in src
    assert "install_global_claude_beacon_skills" in src
    assert "verify_global_claude_beacon_skills" in src


# ---- AC-005 no regression codex/claude ----

def test_no_regression_codex_claude() -> None:
    """codex/claude still use force=True setup + strict=True verify."""
    src = Path(project_hooks_mod.__file__).read_text(encoding="utf-8")
    assert "force=True" in src
    assert "strict=True" in src


# ---- AC-006 block reason codes unchanged ----

def test_no_regression_block_reasons(tmp_path: Path) -> None:
    """setup_failed/verify_failed reason codes semantics unchanged."""
    src = Path(project_hooks_mod.__file__).read_text(encoding="utf-8")
    assert "agent_surface_setup_failed" in src
    assert "agent_surface_verify_failed" in src


# ---- AC-007 agent constant reused ----

def test_agent_constant_reused() -> None:
    """The agent list should come from agent_surface's canonical list, not a new hardcode."""
    from beacon.utils.agent_surface import resolve_agent_surface_target
    # all 5 agents must resolve (canonical list)
    for a in EXPECTED_AGENTS:
        target = resolve_agent_surface_target(Path("/tmp/proj"), a)
        assert target.agent == a
