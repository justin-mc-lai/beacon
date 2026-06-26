"""Tests for beacon-version-resolve-fail-closed-v163 (P0-1).

The post-release hook is heavy (installs skills/launcher), so we test the
extracted pure resolver `_resolve_eval_version` directly, plus the drift
payload fields by mocking the heavy internals.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import beacon.utils.project_hooks as project_hooks_mod
from beacon.utils.project_hooks import _resolve_eval_version


def _make_docs(tmp_path: Path, version: str) -> None:
    docs = tmp_path / "docs" / "beacon" / version
    docs.mkdir(parents=True)
    (docs / "SUMMARY.md").write_text(f"# {version}\n", encoding="utf-8")


# ---- AC-001 no hardcoded fallback ----

def test_no_hardcoded_v161_fallback() -> None:
    """The eval_version line must not fall back to a hardcoded v1.6.1 literal."""
    src = Path(project_hooks_mod.__file__).read_text(encoding="utf-8")
    assert 'else "v1.6.1"' not in src, "hardcoded v1.6.1 fallback still present"
    assert "resolve_target_version" in src, "must use resolve_target_version"


# ---- AC-002 docs version resolved ----

def test_eval_version_resolves_docs_version(tmp_path: Path) -> None:
    """version=auto resolves to the docs version, not v1.6.1."""
    _make_docs(tmp_path, "v1.6.3")
    eval_version, err = _resolve_eval_version(tmp_path, "auto")
    assert err is None
    assert eval_version == "v1.6.3"
    assert eval_version != "v1.6.1"


def test_eval_version_explicit_v_passes_through(tmp_path: Path) -> None:
    _make_docs(tmp_path, "v1.6.3")
    eval_version, err = _resolve_eval_version(tmp_path, "v1.6.3")
    assert err is None
    assert eval_version == "v1.6.3"


# ---- AC-004 resolve failure fail-closed ----

def test_resolve_failure_fail_closed(tmp_path: Path) -> None:
    """When resolve_target_version raises, _resolve_eval_version returns an error."""
    with patch.object(
        project_hooks_mod, "resolve_target_version", side_effect=ValueError("boom")
    ):
        eval_version, err = _resolve_eval_version(tmp_path, "auto")
    assert err is not None
    assert "version_resolve_failed" == err or "version_resolve_failed" in str(err)


# ---- AC-003/005/006/007 drift payload via mocked hook ----

def _stub_heavy_internals(payload_status: str = "PASS") -> dict:
    """Patch the heavy internals at their source modules; return the patchers."""
    import beacon.utils.doctor_orchestrator as doc
    import beacon.utils.agent_surface as asurf

    patchers = [
        patch.object(doc, "run_legacy_beacon_skills_cleanup", return_value=type("R", (), {"payload": {"result": {}}})()),
        patch.object(asurf, "install_global_claude_beacon_skills", return_value={"status": "pass"}),
        patch.object(asurf, "verify_global_claude_beacon_skills", return_value={"status": "pass"}),
        patch.object(doc, "run_agent_surface_setup", return_value=type("R", (), {"exit_code": 0, "payload": {"status": payload_status}})()),
        patch.object(doc, "run_agent_surface_verify", return_value=type("R", (), {"exit_code": 0, "payload": {"status": payload_status}})()),
        patch.object(doc, "run_launcher_setup", return_value=type("R", (), {"exit_code": 0, "payload": {"status": "PASS"}})()),
        patch.object(project_hooks_mod, "is_live_runner_admitted", return_value=False),
        patch.object(project_hooks_mod, "_command_output", return_value={"status": "pass", "stdout": project_hooks_mod.__toolkit_version__}),
    ]
    for p in patchers:
        p.start()
    return {"patchers": patchers}


def test_hook_payload_has_drift_fields(tmp_path: Path) -> None:
    """AC-003: payload carries runtime_version/docs_version/drift."""
    _make_docs(tmp_path, "v1.6.3")
    state = _stub_heavy_internals()
    try:
        payload = project_hooks_mod._run_beacon_post_release_local_install(
            tmp_path, version="v1.6.3", feature="demo"
        )
    finally:
        for p in state["patchers"]:
            p.stop()
    assert "runtime_version" in payload
    assert "docs_version" in payload
    assert "drift" in payload


def test_agent_eval_uses_resolved_version(tmp_path: Path) -> None:
    """AC-005: is_live_runner_admitted receives the resolved version."""
    _make_docs(tmp_path, "v1.6.3")
    captured: dict[str, str] = {}

    def fake_admitted(project_root: Path, *, version: str = "v1.6.1") -> bool:
        captured["version"] = version
        return False

    state = _stub_heavy_internals()
    # override the is_live_runner_admitted stub with a capturing one
    state["patchers"][-2].stop()
    with patch.object(project_hooks_mod, "is_live_runner_admitted", side_effect=fake_admitted):
        try:
            project_hooks_mod._run_beacon_post_release_local_install(
                tmp_path, version="auto", feature="demo"
            )
        finally:
            for p in state["patchers"][:-2]:
                p.stop()
            state["patchers"][-1].stop()
    assert captured.get("version") == "v1.6.3", captured


def test_no_regression_normal_scenario(tmp_path: Path) -> None:
    """AC-006: runtime==docs normal scenario not blocked on version grounds."""
    rt = project_hooks_mod.__toolkit_version__
    _make_docs(tmp_path, rt)
    state = _stub_heavy_internals()
    try:
        payload = project_hooks_mod._run_beacon_post_release_local_install(
            tmp_path, version=rt, feature="demo"
        )
    finally:
        for p in state["patchers"]:
            p.stop()
    assert payload.get("drift") is False
    assert "version_resolve_failed" not in payload.get("reason_codes", [])


def test_drift_legitimate_not_blocked(tmp_path: Path) -> None:
    """AC-007: runtime!=docs records drift=true but does not block on drift."""
    _make_docs(tmp_path, "v1.6.3")
    state = _stub_heavy_internals()
    try:
        payload = project_hooks_mod._run_beacon_post_release_local_install(
            tmp_path, version="v1.6.3", feature="demo"
        )
    finally:
        for p in state["patchers"]:
            p.stop()
    runtime = payload.get("runtime_version")
    docs_v = payload.get("docs_version")
    if runtime != docs_v:
        assert payload.get("drift") is True
        assert "runtime_docs_version_drift" not in payload.get("reason_codes", [])


def test_resolve_failure_blocks_hook(tmp_path: Path) -> None:
    """AC-004 end-to-end: resolve failure makes the hook fail closed."""
    state = _stub_heavy_internals()
    with patch.object(
        project_hooks_mod, "resolve_target_version", side_effect=ValueError("boom")
    ):
        try:
            payload = project_hooks_mod._run_beacon_post_release_local_install(
                tmp_path, version="auto", feature="demo"
            )
        finally:
            for p in state["patchers"]:
                p.stop()
    assert payload.get("blocked") is True
    assert "version_resolve_failed" in payload.get("reason_codes", [])
