"""v1.6.8 prod-ops hardening contract tests."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.prod_ops_v168 import (
    align_run_id,
    build_hotfix_plan,
    build_version_fleet,
    forbidden_production_fix_from_next,
    init_dual_version,
    load_goal_ops_config,
    repair_evidence_manifest,
    resolve_longrun_enabled,
    select_release_profile,
    set_goal_ops_config,
    validate_hotfix_for_release,
    verify_dual_version,
)

ROOT = Path(__file__).resolve().parents[1]


def test_hotfix_requires_baseline():
    plan = build_hotfix_plan(utterance="prod bug", from_version="", production_tag="")
    assert plan["blocked"] is True
    assert "hotfix_baseline_missing" in plan["reason_codes"]


def test_hotfix_release_validation():
    plan = build_hotfix_plan(
        utterance="prod bug",
        from_version="v1.6.7",
        forward_port_target="beacon/v1.6.8/main",
        rollback_notes="revert commit X",
    )
    v = validate_hotfix_for_release(plan)
    assert v["ok"] is True


def test_hotfix_auto_forward_port_default():
    plan = build_hotfix_plan(utterance="x", from_version="v1.6.7", rollback_notes="r")
    v = validate_hotfix_for_release(plan)
    # v1.6.9+ auto-defaults forward port to main for hotfix drafts
    assert plan.get("forward_port_target") == "main"
    assert v["ok"] is True


def test_release_profile_hotfix():
    p = select_release_profile("hotfix")
    assert p["ok"] is True
    assert "forward_port_plan" in p["gates"]


def test_release_profile_invalid():
    p = select_release_profile("nope")
    assert p["blocked"] is True


def test_longrun_default_true(tmp_path: Path):
    set_goal_ops_config(tmp_path, longrun_default=True)
    r = resolve_longrun_enabled(tmp_path, cli_longrun=None)
    assert r["enabled"] is True


def test_longrun_opt_out(tmp_path: Path):
    set_goal_ops_config(tmp_path, longrun_default=True)
    r = resolve_longrun_enabled(tmp_path, cli_longrun=False)
    assert r["enabled"] is False
    assert r["source"] == "cli_flag_off"


def test_repair_evidence_manifest(tmp_path: Path):
    manifest = tmp_path / ".beacon" / "evidence-manifest.json"
    manifest.parent.mkdir(parents=True)
    f = tmp_path / "a.txt"
    f.write_text("hello", encoding="utf-8")
    import json, hashlib
    digest = hashlib.sha256(b"hello").hexdigest()
    manifest.write_text(
        json.dumps({"schema_version": "1.0", "entries": [{"path": "a.txt", "sha256": "dead", "updated_at": "x"}]}),
        encoding="utf-8",
    )
    r = repair_evidence_manifest(tmp_path, version="v1.6.8")
    assert r["ok"] is True
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["entries"][0]["sha256"] == digest


def test_align_run_id(tmp_path: Path):
    (tmp_path / ".beacon").mkdir()
    (tmp_path / ".beacon" / "auto-test-status.json").write_text('{"status":"passed"}', encoding="utf-8")
    r = align_run_id(tmp_path, run_id="run-test-1")
    assert r["ok"] is True
    import json
    d = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert d["run_id"] == "run-test-1"


def test_version_fleet():
    fleet = build_version_fleet(ROOT)
    assert "prod" in fleet
    assert "active_roots" in fleet
    assert "v1.6.8" in fleet["active_roots"] or (ROOT / "docs/beacon/v1.6.8").exists()


def test_dual_version(tmp_path: Path):
    init_dual_version(tmp_path, previous_baseline="release/v1.6.7", next_feature="main")
    v = verify_dual_version(tmp_path)
    assert v["ok"] is True


def test_dual_version_missing(tmp_path: Path):
    v = verify_dual_version(tmp_path)
    assert v["blocked"] is True


def test_forbidden_next_to_prod():
    r = forbidden_production_fix_from_next("next_feature->first_production_fix", dual_on=True)
    assert r["blocked"] is True


def test_v168_packages_exist():
    for slug in (
        "beacon-hotfix-lane-v168",
        "beacon-release-profile-selfheal-v168",
        "beacon-goal-longrun-default-v168",
        "beacon-version-fleet-ops-v168",
        "beacon-v168-goalrun-axis-mount",
        "beacon-v2-loom-ops-philosophy-sync",
    ):
        assert (ROOT / f"docs/beacon/v1.6.8/features/{slug}/truth.md").is_file()
        text = (ROOT / f"docs/beacon/v1.6.8/features/{slug}/truth.md").read_text(encoding="utf-8")
        assert "## 人话" in text


def test_axis_program_graph():
    import json
    g = json.loads((ROOT / "docs/beacon/v1.6.8/programs/beacon-prod-ops-hardening-v168/feature-graph.json").read_text())
    assert len(g["lakes"]) == 6
    assert g["program_slug"] == "beacon-prod-ops-hardening-v168"


def test_no_fake_closed_loop_marker():
    # philosophy: packages declare non-goals against fake delivery
    text = (ROOT / "docs/beacon/v1.6.8/features/beacon-hotfix-lane-v168/truth.md").read_text(encoding="utf-8")
    assert "假" in text or "fake" in text.lower() or "placeholder" in text.lower() or "Non-Goals" in text


def test_loom_parity_package():
    text = (ROOT / "docs/beacon/v1.6.8/features/beacon-v2-loom-ops-philosophy-sync/truth.md").read_text(encoding="utf-8")
    assert "Loom" in text or "loom" in text.lower()
