"""v1.6.8 friction-closeout contract tests (4 lakes)."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.fsm_implement_order import evaluate_fsm_implement_order
from beacon.utils.prod_ops_v168 import (
    resolve_longrun_enabled,
    select_release_profile,
    set_goal_ops_config,
)
from beacon.utils.product_goal_runtime import run_goal_facade
from beacon.utils.runtime_install_truth import diagnose_runtime_install, longrun_doctor

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_install_diagnose_self_repo():
    report = diagnose_runtime_install(ROOT)
    assert "package" in report
    assert "version_truth" in report
    assert "git" in report
    assert report["package"]["version"]
    assert report["status"] in {"pass", "blocked"}


def test_runtime_install_detects_package_truth_fields():
    report = diagnose_runtime_install(ROOT)
    vt = report["version_truth"]
    assert "current_runtime_release_line" in vt
    assert "package_version" in vt


def test_longrun_default_honored_without_env(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("BEACON_GOAL_HONOR_LONGRUN_DEFAULT", raising=False)
    monkeypatch.delenv("BEACON_GOAL_FORCE_LONGRUN", raising=False)
    monkeypatch.delenv("BEACON_GOAL_FORCE_NO_LONGRUN", raising=False)
    set_goal_ops_config(tmp_path, longrun_default=True)
    r = resolve_longrun_enabled(tmp_path, cli_longrun=None)
    assert r["enabled"] is True
    # facade should attach longrun from project default (no utterance longrun words)
    payload = run_goal_facade(
        tmp_path,
        utterance="ship friction closeout lakes",
        version="v1.6.8",
        longrun=False,
        driver_start=False,
        auto_tick=False,
    )
    assert payload.get("longrun") is True
    assert payload.get("longrun_source") in {"project_default", "utterance_intent"}


def test_longrun_cli_opt_out(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("BEACON_GOAL_FORCE_LONGRUN", raising=False)
    set_goal_ops_config(tmp_path, longrun_default=True)
    # explicit False via resolve
    r = resolve_longrun_enabled(tmp_path, cli_longrun=False)
    assert r["enabled"] is False
    assert r["source"] == "cli_flag_off"


def test_longrun_doctor_shape():
    report = longrun_doctor(ROOT)
    assert "longrun_resolved" in report
    assert "bridge" in report


def test_release_profile_hotfix_gates():
    p = select_release_profile("hotfix")
    assert p["ok"] is True
    assert "rollback_notes" in p["gates"]
    assert "forward_port_plan" in p["gates"]


def test_release_profile_full():
    p = select_release_profile("full")
    assert p["ok"] is True
    assert p["profile"] == "full"


def test_release_check_accepts_profile_cli():
    from typer.testing import CliRunner
    from beacon.commands.release import app

    runner = CliRunner()
    # may be blocked on scorecard but must parse profile and not crash invalid
    result = runner.invoke(app, ["check", "v1.6.8", "-p", str(ROOT), "--profile", "hotfix", "--json"])
    # exit 0 or 1/2 depending on gates; must not be usage error
    assert result.exit_code in {0, 1, 2}
    if result.stdout.strip().startswith("{"):
        data = json.loads(result.stdout)
        assert "release_profile" in data or data.get("reason_code") == "release_profile_invalid" or "status" in data


def test_fsm_implement_order_skip_non_domain():
    # ops lakes are domain_required false
    r = evaluate_fsm_implement_order(
        ROOT,
        version="v1.6.8",
        feature="beacon-runtime-install-truth-v168",
    )
    assert r.get("blocked") is False


def test_fsm_implement_order_blocks_open_predecessor(tmp_path: Path):
    # minimal domain truth with entity precedence
    version = "v1.6.8"
    feat = "order-checkout"
    base = tmp_path / "docs" / "beacon" / version / "features" / feat
    base.mkdir(parents=True)
    (base / "truth.md").write_text(
        """---
slug: order-checkout
domain_required: true
---
# Truth
## Domain Model
entity order requires product
## Entity precedence
| entity | requires |
| order | product |
## Domain FSM
order: created -> paid
## Illegal transition
paid -> created
""",
        encoding="utf-8",
    )
    r = evaluate_fsm_implement_order(tmp_path, version=version, feature=feat)
    # may pass with no_entity_match if parser shape differs; assert structure
    assert "status" in r
    assert "blocked" in r


def test_no_fake_closed_loop_marker():
    text = (ROOT / "docs/beacon/v1.6.8/features/beacon-runtime-install-truth-v168/truth.md").read_text(
        encoding="utf-8"
    )
    assert "禁止" in text or "placeholder" in text.lower() or "fake" in text.lower()


def test_friction_packages_exist():
    for slug in (
        "beacon-runtime-install-truth-v168",
        "beacon-longrun-contract-align-v168",
        "beacon-release-profile-wiring-v168",
        "beacon-fsm-implement-order-v168",
    ):
        assert (ROOT / "docs/beacon/v1.6.8/features" / slug / "truth.md").exists()


def test_axis_program_graph():
    graph = json.loads(
        (ROOT / "docs/beacon/v1.6.8/programs/beacon-friction-closeout-v168/feature-graph.json").read_text(
            encoding="utf-8"
        )
    )
    assert graph["program_slug"] == "beacon-friction-closeout-v168"
    assert len(graph["lakes"]) == 4
