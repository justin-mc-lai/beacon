"""Issue #14: external repos must keep docs_version on the product line, never the runtime axis."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from beacon import __toolkit_version__
from beacon.main import app
from beacon.utils.context_files import setup_context_files
from beacon.utils.doctor_diagnostics import build_doctor_payload
from beacon.utils.runtime import write_json
from beacon.utils.version_defaults import (
    ALLOW_RUNTIME_AS_DOCS_ENV,
    classify_project,
    external_dual_axis_violation,
    guard_external_docs_axis,
    project_docs_baseline,
)
from beacon.utils.versioning import (
    describe_project_version_context,
    resolve_docs_version,
    resolve_operational_docs_version,
)

ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = str(__toolkit_version__)
runner = CliRunner()


def _external_existing(tmp_path: Path, version: str = "v0.0.5") -> Path:
    docs = tmp_path / "docs" / "beacon" / version
    docs.mkdir(parents=True)
    (docs / "SUMMARY.md").write_text(f"# {version}\n", encoding="utf-8")
    return tmp_path


def _poison_onboarding(root: Path, *, docs: str = TOOLKIT) -> None:
    state = root / ".beacon" / "state"
    state.mkdir(parents=True)
    write_json(
        state / "project-onboarding.json",
        {"docs_version": docs, "runtime_version": TOOLKIT},
    )


def test_classify_external_existing_reports_toolkit_runtime(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    info = classify_project(root)
    assert info["project_kind"] == "external_existing"
    # Regression: runtime must never be inferred from the product docs line.
    assert info["runtime_version"] == TOOLKIT
    assert info["runtime_version"] != "v0.0.5"


def test_resolve_docs_auto_greenfield_defaults_v001(tmp_path: Path) -> None:
    assert classify_project(tmp_path)["project_kind"] == "external_greenfield"
    assert resolve_docs_version(tmp_path, None) == "v0.0.1"
    assert resolve_docs_version(tmp_path, "auto") == "v0.0.1"


def test_resolve_docs_auto_external_existing_keeps_product_baseline(tmp_path: Path) -> None:
    root = _external_existing(tmp_path, "v0.0.5")
    assert resolve_docs_version(root, "auto") == "v0.0.5"


def test_project_docs_baseline_never_toolkit_for_external(tmp_path: Path) -> None:
    assert project_docs_baseline(tmp_path) == "v0.0.1"
    root = _external_existing(tmp_path, "v0.0.5")
    assert project_docs_baseline(root) == "v0.0.5"
    assert project_docs_baseline(ROOT) != "v0.0.1"


def test_guard_blocks_external_collapse_and_allows_product_line(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    guard_external_docs_axis(root, "v0.0.5")  # product line is fine
    with pytest.raises(ValueError, match="dual-axis"):
        guard_external_docs_axis(root, TOOLKIT, command_name="beacon change")
    violation = external_dual_axis_violation(root, TOOLKIT)
    assert violation["violated"] is True
    assert violation["blocked"] is True
    assert violation["override_env"] == ALLOW_RUNTIME_AS_DOCS_ENV


def test_guard_allows_beacon_self_docs_equal_runtime() -> None:
    assert classify_project(ROOT)["project_kind"] == "beacon_self"
    guard_external_docs_axis(ROOT, TOOLKIT)  # self docs lane tracks runtime


def test_guard_override_env_forces_collapse(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _external_existing(tmp_path)
    monkeypatch.setenv(ALLOW_RUNTIME_AS_DOCS_ENV, "1")
    guard_external_docs_axis(root, TOOLKIT)
    assert external_dual_axis_violation(root, TOOLKIT)["blocked"] is False


def test_resolve_operational_docs_version_blocks_external_collapse(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    assert resolve_operational_docs_version(root, "auto") == "v0.0.5"
    assert resolve_operational_docs_version(root, "v0.0.6") == "v0.0.6"
    with pytest.raises(ValueError, match="dual-axis"):
        resolve_operational_docs_version(root, TOOLKIT, command_name="beacon prd create")


def test_version_context_flags_project_kind_and_collapse(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    ctx = describe_project_version_context(root)
    assert ctx["project_kind"] == "external_existing"
    assert ctx["dual_axis_collapse_external"] is False
    _poison_onboarding(root)
    ctx = describe_project_version_context(root)
    assert ctx["project_kind"] == "external_existing"
    assert ctx["dual_axis_collapse_external"] is True


def test_setup_context_files_external_defaults_never_collapse(tmp_path: Path) -> None:
    payload = setup_context_files(
        tmp_path,
        runtime_version=TOOLKIT,
        dry_run=False,
        force=False,
        with_claude=True,
        with_agents=True,
    )
    assert payload["docs_version"] == "v0.0.1"
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert f"BEACON:VERSION:{TOOLKIT}" in agents
    assert "BEACON:DOCS_VERSION:v0.0.1" in agents


def test_setup_context_files_external_existing_keeps_baseline(tmp_path: Path) -> None:
    root = _external_existing(tmp_path, "v0.0.5")
    payload = setup_context_files(
        root,
        runtime_version=TOOLKIT,
        dry_run=False,
        force=False,
        with_claude=True,
        with_agents=True,
    )
    assert payload["docs_version"] == "v0.0.5"


def test_init_external_greenfield_defaults_dual_axis(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", "--project", str(tmp_path), "--apply"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["docs_version"] == "v0.0.1"
    assert payload["runtime_version"] == TOOLKIT
    onboarding = json.loads(
        (tmp_path / ".beacon" / "state" / "project-onboarding.json").read_text(encoding="utf-8")
    )
    assert onboarding["docs_version"] == "v0.0.1"
    assert onboarding["runtime_version"] == TOOLKIT
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "Docs target version: `v0.0.1`" in agents


def test_init_external_refuses_runtime_docs_version(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["init", "--project", str(tmp_path), "--apply", "--version", TOOLKIT],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["reason_code"] == "dual_axis_collapse_external"
    assert not (tmp_path / "docs" / "beacon" / TOOLKIT).exists()


def test_setup_context_external_defaults_dual_axis(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["doctor", "setup-context", "--project-root", str(tmp_path), "--json"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["docs_version"] == "v0.0.1"
    assert payload["runtime_version"] == TOOLKIT
    onboarding = json.loads(
        (tmp_path / ".beacon" / "state" / "project-onboarding.json").read_text(encoding="utf-8")
    )
    assert onboarding["docs_version"] == "v0.0.1"
    assert onboarding["runtime_version"] == TOOLKIT


def test_setup_context_external_blocks_runtime_docs_version(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["doctor", "setup-context", "--project-root", str(tmp_path), "--version", TOOLKIT, "--json"],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED"
    assert payload["reason_code"] == "dual_axis_collapse_external"
    assert not (tmp_path / "CLAUDE.md").exists()


def test_setup_context_external_existing_anchors_product_line(tmp_path: Path) -> None:
    root = _external_existing(tmp_path, "v0.0.5")
    result = runner.invoke(
        app,
        ["doctor", "setup-context", "--project-root", str(root), "--version", "v0.0.5", "--json"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["docs_version"] == "v0.0.5"
    assert payload["runtime_version"] == TOOLKIT
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert "Docs target version: `v0.0.5`" in agents


def test_change_external_refuses_runtime_docs_version(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["change", "some-feature", "--project", str(tmp_path), "--version", TOOLKIT],
    )
    assert result.exit_code == 2
    assert "dual-axis" in result.output


def test_truth_external_refuses_runtime_docs_version(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["truth", "init", "all", "--feature", "demo", "--project", str(tmp_path), "--version", TOOLKIT],
    )
    assert result.exit_code == 2
    assert "dual-axis" in result.output


def test_verify_context_blocks_external_collapse(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    _poison_onboarding(root)
    result = runner.invoke(
        app,
        ["doctor", "verify-context", "--project-root", str(root), "--json"],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED"
    names = {item.get("name") for item in payload.get("result", {}).get("checks", [])}
    assert "dual_axis_external_collapse" in names


def test_doctor_diagnostics_fail_on_axis_collapse(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    _poison_onboarding(root)
    payload = build_doctor_payload(root, strict=False)
    incompatibilities = {
        item.get("name"): item.get("status") for item in payload.get("incompatibilities", [])
    }
    assert incompatibilities.get("docs_runtime_separation_integrity") == "FAIL"
    assert incompatibilities.get("suspicious_runtime_named_docs_root") == "FAIL"


def test_doctor_diagnostics_fail_on_runtime_named_pollution(tmp_path: Path) -> None:
    root = _external_existing(tmp_path, "v0.0.5")
    polluted = root / "docs" / "beacon" / TOOLKIT / "prd"
    polluted.mkdir(parents=True)
    (polluted / "shadow.md").write_text("# shadow scaffold\n", encoding="utf-8")
    _poison_onboarding(root, docs="v0.0.5")
    payload = build_doctor_payload(root, strict=False)
    incompatibilities = {
        item.get("name"): item.get("status") for item in payload.get("incompatibilities", [])
    }
    assert incompatibilities.get("suspicious_runtime_named_docs_root") == "FAIL"
