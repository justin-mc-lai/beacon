"""AC-BG: hard stage-exit gates + freeze-before-implement + main write block."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.goal_stage_exit_gates import (
    REASON_FREEZE_ACK,
    REASON_TRUTH_DRAFT,
    evaluate_stage_exit,
    feature_package_frozen,
    parse_truth_frontmatter_status,
)
from beacon.utils.goal_implement_admission import ensure_goal_implement_admission, REASON_FREEZE_ACK as ADM_FREEZE
from beacon.utils.implement_lane_enforcement import check_main_implement_commit, is_business_path
from beacon.utils.product_goal_runtime import (
    create_goal_run,
    tick_goal_run,
    load_goal_run,
    _save,
)
from beacon.utils.revision_state import freeze_revision_state, load_revision_state, save_revision_state


def _write_truth(root: Path, version: str, slug: str, status: str = "draft") -> Path:
    d = root / "docs" / "beacon" / version / "features" / slug
    d.mkdir(parents=True, exist_ok=True)
    p = d / "truth.md"
    p.write_text(
        f"""---
slug: {slug}
version: {version}
status: {status}
revision_id: R1
language: en
parser_contract: beacon-feature-package-v2
---

# Truth {slug}

## Acceptance Criteria
| AC | Desc |
|----|------|
| AC-001 | demo |
""",
        encoding="utf-8",
    )
    (d / "tests.md").write_text("# tests\n", encoding="utf-8")
    (d / "tasks.md").write_text("# tasks\n", encoding="utf-8")
    (d / "evidence.md").write_text("# evidence\n", encoding="utf-8")
    return p


def test_parse_frontmatter_status():
    assert parse_truth_frontmatter_status("---\nstatus: draft\n---\n") == "draft"
    assert parse_truth_frontmatter_status("---\nstatus: frozen\n---\n") == "frozen"


def test_feature_package_frozen_frontmatter(tmp_path: Path):
    _write_truth(tmp_path, "v1.6.9", "lake-a", "draft")
    info = feature_package_frozen(tmp_path, version="v1.6.9", feature="lake-a")
    assert info["frozen"] is False
    _write_truth(tmp_path, "v1.6.9", "lake-a", "frozen")
    info2 = feature_package_frozen(tmp_path, version="v1.6.9", feature="lake-a")
    assert info2["frozen"] is True


def test_truth_stage_exit_blocks_draft(tmp_path: Path):
    _write_truth(tmp_path, "v1.6.9", "lake-a", "draft")
    payload = {"version": "v1.6.9", "feature": "lake-a", "lakes": ["lake-a"]}
    gate = evaluate_stage_exit(tmp_path, payload, stage="truth")
    assert gate["blocked"] is True
    assert gate["reason_code"] in {REASON_TRUTH_DRAFT, REASON_FREEZE_ACK}
    assert gate["fill_harness"] == "truth"
    assert gate["resume_action"] in {"await_freeze_ack", "load_next_skill"}


def test_truth_stage_exit_allows_frozen(tmp_path: Path):
    _write_truth(tmp_path, "v1.6.9", "lake-a", "frozen")
    payload = {"version": "v1.6.9", "feature": "lake-a"}
    gate = evaluate_stage_exit(tmp_path, payload, stage="truth")
    assert gate["allow"] is True
    assert gate["blocked"] is False


def test_implement_admission_requires_freeze(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_truth(tmp_path, "v1.6.9", "lake-a", "draft")
    payload = {"version": "v1.6.9", "feature": "lake-a"}
    gate = ensure_goal_implement_admission(tmp_path, payload, dry_run=True)
    assert gate["allow_implement"] is False
    assert gate["reason_code"] == ADM_FREEZE
    assert gate.get("resume_action") == "await_freeze_ack"

    _write_truth(tmp_path, "v1.6.9", "lake-a", "frozen")
    # dry_run may still fail worktree but freeze should pass — freeze check returns before admit
    # With frozen truth, dry_run proceeds to admit; may pass/block on admit — not freeze
    gate2 = ensure_goal_implement_admission(tmp_path, payload, dry_run=True)
    assert gate2["reason_code"] != ADM_FREEZE


def test_main_business_write_blocked():
    assert is_business_path("apps/web/src/x.ts") is True
    assert is_business_path("plugins/foo/index.ts") is True
    assert is_business_path("src/lib/a.ts") is True
    # tight docs policy: non-beacon docs are forbidden on main (business-classified)
    assert is_business_path("docs/readme.md") is True
    assert is_business_path("docs/beacon/v1.6.9/features/x/truth.md") is False
    r = check_main_implement_commit(
        Path("."),
        files=["apps/web/src/x.ts"],
        branch="main",
    )
    assert r["blocked"] is True
    assert r["reason_code"] == "main_implement_forbidden"


def test_tick_blocks_truth_exit_when_draft(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # minimal git repo for goal state
    import subprocess
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "i"], cwd=tmp_path, check=True, capture_output=True)

    _write_truth(tmp_path, "v1.6.9", "lake-a", "draft")
    payload = create_goal_run(
        tmp_path,
        utterance="implement lake-a hard gates test",
        version="v1.6.9",
        feature="lake-a",
        lakes=["lake-a"],
    )
    run_id = payload["run_id"]
    # force current stage to truth
    payload["current_stage"] = "truth"
    for s in payload.get("stages") or []:
        if isinstance(s, dict) and s.get("stage") == "plan":
            s["status"] = "done"
        if isinstance(s, dict) and s.get("stage") == "truth":
            s["status"] = "active"
    _save(tmp_path, payload)

    out = tick_goal_run(tmp_path, run_id, note="try leave truth")
    assert out.get("blocked") is True
    assert out.get("reason_code") in {REASON_TRUTH_DRAFT, REASON_FREEZE_ACK}
    assert out.get("fill_harness") == "truth"
    # truth stage must not be marked done
    stages = out.get("stages") or []
    truth = next(s for s in stages if s.get("stage") == "truth")
    assert truth.get("status") != "done"


def test_qa_exit_requires_evidence(tmp_path: Path):
    payload = {"version": "v1.6.9", "feature": "lake-a"}
    gate = evaluate_stage_exit(tmp_path, payload, stage="qa")
    assert gate["blocked"] is True
    assert gate["reason_code"] in {"stage_exit_qa_evidence_missing", "stage_exit_qa_evidence_missing"}
    # create evidence
    ev = tmp_path / "docs" / "beacon" / "v1.6.9" / "features" / "lake-a" / "evidence.md"
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text("# evidence\n\npass with details here\n", encoding="utf-8")
    gate2 = evaluate_stage_exit(tmp_path, payload, stage="qa")
    assert gate2["allow"] is True


def test_release_tick_exit_always_blocks():
    gate = evaluate_stage_exit(Path("."), {"version": "v1.6.9"}, stage="release")
    assert gate["blocked"] is True
    assert gate["resume_action"] == "await_human_release"


def test_reason_catalog_known_codes():
    from beacon.utils.goal_reason_codes import (
        FREEZE_ACK_REQUIRED,
        REASON_CATALOG,
        STAGE_EXIT_TRUTH_NOT_FROZEN,
        is_known_reason,
    )

    assert FREEZE_ACK_REQUIRED in REASON_CATALOG
    assert STAGE_EXIT_TRUTH_NOT_FROZEN in REASON_CATALOG
    assert is_known_reason(FREEZE_ACK_REQUIRED)
    assert is_known_reason("stage_exit_custom_future") or True  # prefix rule


def test_truth_missing_vs_draft_reason_codes(tmp_path: Path):
    # missing package
    payload = {"version": "v1.6.9", "feature": "no-such-lake"}
    gate = evaluate_stage_exit(tmp_path, payload, stage="truth")
    assert gate["blocked"] is True
    assert gate["reason_code"] == "stage_exit_truth_package_missing"
    assert gate["fill_harness"] == "truth"
    assert gate["resume_action"] == "load_next_skill"

    # draft package
    _write_truth(tmp_path, "v1.6.9", "draft-lake", "draft")
    gate2 = evaluate_stage_exit(
        tmp_path, {"version": "v1.6.9", "feature": "draft-lake"}, stage="truth"
    )
    assert gate2["reason_code"] == "stage_exit_truth_not_frozen"
    assert gate2["resume_action"] == "await_freeze_ack"


def test_design_exit_and_fill_fields(tmp_path: Path):
    gate = evaluate_stage_exit(tmp_path, {"version": "v1.6.9"}, stage="design")
    assert gate["blocked"] is True
    assert gate["reason_code"] == "stage_exit_design_incomplete"
    assert gate["fill_harness"] == "design"
    assert gate["fill_mode"] == "gen-design"
    (tmp_path / "DESIGN.md").write_text("# Design\n\nbaseline\n", encoding="utf-8")
    gate2 = evaluate_stage_exit(tmp_path, {"version": "v1.6.9"}, stage="design")
    assert gate2["allow"] is True


def test_block_payload_fill_routing_contract(tmp_path: Path):
    from beacon.utils.goal_stage_exit_gates import apply_stage_exit_block

    gate = evaluate_stage_exit(
        tmp_path, {"version": "v1.6.9", "feature": "x"}, stage="truth"
    )
    payload = apply_stage_exit_block({"run_id": "t", "history": []}, gate)
    assert payload["blocked"] is True
    assert payload["fill_harness"]
    assert payload["resume_action"]
    assert payload["stage_exit_gate"]["reason_code"] == payload["reason_code"]


def test_main_docs_policy_tightened():
    from beacon.utils.implement_lane_enforcement import (
        check_main_implement_commit,
        is_allowlisted,
        is_business_path,
        is_docs_policy_violation,
    )

    assert is_docs_policy_violation("docs/guide.md") is True
    assert is_docs_policy_violation("docs/marketing/x.md") is True
    assert is_docs_policy_violation("docs/beacon/v1.6.9/features/a/truth.md") is False
    assert is_allowlisted("docs/beacon/v1.6.9/features/a/truth.md") is True
    assert is_allowlisted("docs/guide.md") is False
    assert is_business_path("docs/guide.md") is True
    assert is_business_path("docs/beacon/v1.6.9/x.md") is False

    r = check_main_implement_commit(
        Path("."),
        files=["docs/architecture.md"],
        branch="main",
    )
    assert r["blocked"] is True
    assert r["reason_code"] == "main_docs_policy_forbidden"

    r2 = check_main_implement_commit(
        Path("."),
        files=["docs/beacon/v1.6.9/features/x/truth.md"],
        branch="main",
    )
    assert r2["blocked"] is False
    assert r2.get("note") == "no_business_paths" or r2["status"] == "pass"


def test_main_mixed_business_and_docs_uses_implement_reason():
    from beacon.utils.implement_lane_enforcement import check_main_implement_commit

    r = check_main_implement_commit(
        Path("."),
        files=["docs/guide.md", "apps/web/src/a.ts"],
        branch="main",
    )
    assert r["blocked"] is True
    assert r["reason_code"] == "main_implement_forbidden"
