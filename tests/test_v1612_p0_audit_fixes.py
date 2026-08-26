"""P0 audit fixes (v1.6.12, task 08-26-p0-audit-fixes).

Covers prd.md acceptance criteria:
- R1: truth-promotion receipts discovered under either lakes/<row-slug>/ or lakes/<feature-slug>/
- R2: orchestrator closure evidence keyed by feature_slug (row slug kept for display)
- R3: additive program_binding diagnostics on unbound goal payloads
- R4: complete-time closure artifact backfill citing real evidence only
"""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.product_goal_runtime import (
    attach_verifier,
    complete_goal_run,
    run_goal_facade,
    sync_program_orchestrator_route,
)
from beacon.utils.program_admission import _implementation_closed, _qa_closed
from beacon.utils.program_freeze_gate import build_program_freeze_gate
from beacon.utils.program_orchestrator import build_program_orchestrator_state

VERSION = "v1.6.12"
PROGRAM = "sea-demo"

ROW_A = {
    "slug": "L1-alpha",
    "feature_slug": "alpha",
    "depends_on": [],
    "parity_subset": ["auth"],
    "status": "planned",
}
ROW_B = {
    "slug": "L2-beta",
    "feature_slug": "beta",
    "depends_on": ["L1-alpha"],
    "parity_subset": ["billing"],
    "status": "planned",
}


def _program_dir(root: Path, program: str = PROGRAM) -> Path:
    return root / "docs" / "beacon" / VERSION / "programs" / program


def _write_graph(root: Path, lakes: list[dict], *, program: str = PROGRAM, frozen: bool = True) -> None:
    directory = _program_dir(root, program)
    directory.mkdir(parents=True, exist_ok=True)
    graph: dict = {
        "program_slug": program,
        "version": VERSION,
        "scope_mode": "full_parity",
        "lakes": lakes,
    }
    if frozen:
        graph["program_plan_frozen"] = True
    (_program_dir(root, program) / "feature-graph.json").write_text(json.dumps(graph), encoding="utf-8")


def _freeze_truth_row(root: Path, slug: str, *, program: str = PROGRAM) -> None:
    path = _program_dir(root, program) / "feature-graph.json"
    graph = json.loads(path.read_text(encoding="utf-8"))
    for row in graph["lakes"]:
        if row.get("slug") == slug:
            row["status"] = "frozen"
    path.write_text(json.dumps(graph), encoding="utf-8")


def _write_receipt(root: Path, lake_dir_name: str, *, program: str = PROGRAM) -> Path:
    promo_dir = _program_dir(root, program) / "lakes" / lake_dir_name
    promo_dir.mkdir(parents=True, exist_ok=True)
    path = promo_dir / "truth-promotion.json"
    path.write_text(json.dumps({"status": "complete"}), encoding="utf-8")
    return path


def _close_impl_machine(root: Path, feature: str) -> None:
    path = root / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"implementation-summary-{feature}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": "passed"}), encoding="utf-8")


def _close_qa_machine(root: Path, feature: str) -> None:
    path = root / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"qa-acceptance-{feature}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"status": "passed", "verdict": "passed", "evidence_done": True}),
        encoding="utf-8",
    )


# --- R1: dual-path receipt discovery ----------------------------------------


def test_receipt_only_under_feature_dir_passes_gate(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)])
    _freeze_truth_row(root, "L1-alpha")
    _write_receipt(root, "alpha")  # writer keys receipts by feature name
    gate = build_program_freeze_gate(root, version=VERSION, program_slug=PROGRAM)
    assert gate["lakes"][0]["truth_promotion_complete"] is True
    codes = [str(f.get("code")) for f in gate["findings"]]
    assert not any(code.startswith("truth_promotion_missing") for code in codes)


def test_receipt_only_under_row_slug_dir_passes_gate(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)])
    _freeze_truth_row(root, "L1-alpha")
    _write_receipt(root, "L1-alpha")  # legacy layout keyed by row slug
    gate = build_program_freeze_gate(root, version=VERSION, program_slug=PROGRAM)
    assert gate["lakes"][0]["truth_promotion_complete"] is True
    codes = [str(f.get("code")) for f in gate["findings"]]
    assert not any(code.startswith("truth_promotion_missing") for code in codes)


def test_receipt_in_both_dirs_still_passes_once(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)])
    _freeze_truth_row(root, "L1-alpha")
    _write_receipt(root, "L1-alpha")  # legacy layout
    _write_receipt(root, "alpha")  # writer layout coexists (selfmedia dual-dir)
    gate = build_program_freeze_gate(root, version=VERSION, program_slug=PROGRAM)
    assert gate["lakes"][0]["truth_promotion_complete"] is True
    codes = [str(f.get("code")) for f in gate["findings"]]
    assert not any(code.startswith("truth_promotion_missing") for code in codes)


def test_missing_receipt_still_blocks(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)])
    _freeze_truth_row(root, "L1-alpha")
    gate = build_program_freeze_gate(root, version=VERSION, program_slug=PROGRAM)
    assert gate["lakes"][0]["truth_promotion_complete"] is False
    assert {"kind": "lake", "code": "truth_promotion_missing:L1-alpha"} in gate["findings"]


# --- R2: evidence keyed by feature_slug (merged R1+R2 scenario) --------------


def test_orchestrate_closes_lake_from_feature_keyed_evidence(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)])
    route = build_program_orchestrator_state(root, version=VERSION, program_slug=PROGRAM)
    lake = route["lakes"][0]
    assert lake["lake"] == "l1-alpha"  # display keeps original slug
    assert lake["stage"] == "truth"  # nothing frozen yet

    _freeze_truth_row(root, "L1-alpha")
    route_pre = build_program_orchestrator_state(root, version=VERSION, program_slug=PROGRAM)
    assert route_pre["lakes"][0]["stage"] == "implement"  # feature-keyed evidence not found yet
    assert route_pre["lakes"][0]["implementation_closed"] is False

    _close_impl_machine(root, "alpha")
    _close_qa_machine(root, "alpha")
    route2 = build_program_orchestrator_state(root, version=VERSION, program_slug=PROGRAM)
    closed = route2["lakes"][0]
    assert closed["implementation_closed"] is True
    assert closed["qa_closed"] is True
    assert closed["stage"] == "release"
    assert closed["complete"] is True
    assert route2["sea_completion_status"] == "all_lakes_complete"
    assert route2["status"] == "pass"


def test_dependency_alias_resolves_to_feature_keyed_evidence(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A), dict(ROW_B)])
    # close upstream A entirely (evidence keyed by feature name alpha)
    _freeze_truth_row(root, "L1-alpha")
    _close_impl_machine(root, "alpha")
    _close_qa_machine(root, "alpha")
    route = build_program_orchestrator_state(root, version=VERSION, program_slug=PROGRAM)
    beta = next(row for row in route["lakes"] if row["lake"] == "l2-beta")
    # upstream A counts as closed even though deps are declared with the row slug L1-alpha
    assert beta["unclosed_dependencies"] == []
    assert beta["reason_code"] == "await_next_lake_truth"


# --- R3: program_binding diagnostics -----------------------------------------


def test_binding_diagnostic_program_not_frozen(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)], frozen=False)
    payload = sync_program_orchestrator_route(
        root, {"run_id": "r1", "version": VERSION, "feature": "alpha"}, persist_run_state=False
    )
    binding = payload.get("program_binding")
    assert binding and binding["status"] == "unbound"
    assert binding["reason_code"] == "program_not_frozen"
    entry = binding["checked"][0]
    assert entry["graph_valid"] is True
    assert entry["feature_in_graph"] is True
    assert entry["frozen"] is False
    assert binding["hint"]


def test_binding_diagnostic_feature_not_in_graph(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)])  # frozen graph, but only contains alpha
    payload = sync_program_orchestrator_route(
        root, {"run_id": "r2", "version": VERSION, "feature": "ghost"}, persist_run_state=False
    )
    binding = payload.get("program_binding")
    assert binding and binding["status"] == "unbound"
    assert binding["reason_code"] == "feature_not_in_graph"
    assert binding["checked"][0]["feature_in_graph"] is False


def test_binding_diagnostic_graph_invalid(tmp_path: Path):
    root = tmp_path
    directory = _program_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    (_program_dir(root) / "feature-graph.json").write_text("{not-json", encoding="utf-8")
    payload = sync_program_orchestrator_route(
        root, {"run_id": "r3", "version": VERSION, "feature": "alpha"}, persist_run_state=False
    )
    binding = payload.get("program_binding")
    assert binding and binding["status"] == "unbound"
    assert binding["reason_code"] == "graph_invalid"
    assert binding["checked"][0]["graph_valid"] is False
    assert binding["checked"][0]["errors"]


def test_binding_bound_attaches_slug_and_route(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)], frozen=True)
    payload = sync_program_orchestrator_route(
        root, {"run_id": "r4", "version": VERSION, "feature": "alpha"}, persist_run_state=False
    )
    assert payload.get("program_binding") == {"status": "bound", "program_slug": PROGRAM}
    assert payload["program_orchestrator"]["program_slug"] == PROGRAM


def test_no_programs_dir_attaches_nothing(tmp_path: Path):
    payload = sync_program_orchestrator_route(
        tmp_path, {"run_id": "r5", "version": VERSION, "feature": "alpha"}, persist_run_state=False
    )
    assert "program_binding" not in payload
    assert "program_orchestrator" not in payload


def test_facade_unbound_payload_carries_diagnostic(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(ROW_A)], frozen=False)
    payload = run_goal_facade(root, utterance="做 alpha", version=VERSION, feature="alpha")
    binding = payload.get("program_binding")
    assert binding and binding["status"] == "unbound"
    assert binding["reason_code"] == "program_not_frozen"


# --- R4: complete-time closure backfill --------------------------------------


def test_complete_backfills_impl_marker_citing_verifier_refs(tmp_path: Path):
    root = tmp_path
    scorecard = root / "docs" / "beacon" / VERSION / "qa" / "alpha-scorecard.md"
    scorecard.parent.mkdir(parents=True, exist_ok=True)
    scorecard.write_text("# scorecard evidence\n", encoding="utf-8")
    facade = run_goal_facade(root, utterance="交付 alpha", version=VERSION, feature="alpha")
    rid = facade["run_id"]
    attach_verifier(root, rid, refs=[str(scorecard.relative_to(root))])
    done = complete_goal_run(root, rid)
    assert done["status"] == "completed"
    impl_path = root / "docs" / "beacon" / VERSION / ".machine" / "execution" / "implementation-summary-alpha.json"
    assert impl_path.exists()
    body = json.loads(impl_path.read_text(encoding="utf-8"))
    assert body["status"] == "passed"
    assert body["run_id"] == rid
    assert str(scorecard.relative_to(root)) in body["verifier_refs"]
    # markers are readable by admission checks (the whole point of the backfill)
    assert _implementation_closed(root, version=VERSION, feature="alpha")["closed"] is True
    # qa stage never ran -> no fabricated qa acceptance
    assert not (
        root / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"qa-acceptance-alpha.json"
    ).exists()


def test_complete_backfills_qa_mirror_when_qa_stage_done(tmp_path: Path):
    root = tmp_path
    scorecard = root / "docs" / "beacon" / VERSION / "qa" / "alpha-scorecard.md"
    scorecard.parent.mkdir(parents=True, exist_ok=True)
    scorecard.write_text("# scorecard evidence\n", encoding="utf-8")
    facade = run_goal_facade(root, utterance="交付 alpha qa", version=VERSION, feature="alpha")
    rid = facade["run_id"]
    state_path = root / ".beacon" / "state" / "product-goal" / f"{rid}.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    for item in state.get("stages") or []:
        if item.get("stage") == "qa":
            item["status"] = "done"
            item["artifact"] = str(scorecard.relative_to(root))
    state_path.write_text(json.dumps(state), encoding="utf-8")
    attach_verifier(root, rid, refs=[str(scorecard.relative_to(root))])
    done = complete_goal_run(root, rid)
    assert done["status"] == "completed"
    qa_path = root / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"qa-acceptance-alpha.json"
    assert qa_path.exists()
    body = json.loads(qa_path.read_text(encoding="utf-8"))
    assert body["verdict"] == "passed"
    assert body["scorecard_ref"] == str(scorecard.relative_to(root))
    assert _qa_closed(root, version=VERSION, feature="alpha")["closed"] is True
    events = [str(h.get("event")) for h in done.get("history") or []]
    assert "closure_backfilled" in events


def test_complete_without_verifier_skips_and_records_history_event(tmp_path: Path):
    root = tmp_path
    facade = run_goal_facade(root, utterance="force complete demo", version=VERSION, feature="alpha")
    rid = facade["run_id"]
    done = complete_goal_run(root, rid, force=True)
    assert done["status"] == "completed"
    exec_dir = root / "docs" / "beacon" / VERSION / ".machine" / "execution"
    assert not (exec_dir / "implementation-summary-alpha.json").exists()
    skip_events = [
        h
        for h in done.get("history") or []
        if h.get("event") == "closure_backfill_skipped" and h.get("kind") == "implementation_summary"
    ]
    assert skip_events and skip_events[0]["reason_code"] == "no_verifier_refs"


def test_qa_backfill_skips_without_any_real_evidence_refs(tmp_path: Path):
    root = tmp_path
    facade = run_goal_facade(root, utterance="qa skip demo", version=VERSION, feature="alpha")
    rid = facade["run_id"]
    state_path = root / ".beacon" / "state" / "product-goal" / f"{rid}.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    for item in state.get("stages") or []:
        if item.get("stage") == "qa":
            item["status"] = "done"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    done = complete_goal_run(root, rid, force=True)
    assert done["status"] == "completed"
    events = [
        h
        for h in done.get("history") or []
        if h.get("event") == "closure_backfill_skipped" and h.get("kind") == "qa_acceptance"
    ]
    assert events and events[0]["reason_code"] == "no_qa_evidence_refs"
    exec_dir = root / "docs" / "beacon" / VERSION / ".machine" / "execution"
    assert not (exec_dir / "qa-acceptance-alpha.json").exists()


def test_existing_markers_never_overwritten(tmp_path: Path):
    root = tmp_path
    exec_dir = root / "docs" / "beacon" / VERSION / ".machine" / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    original = {"status": "passed", "verdict": "passed", "note": "authored-by-qa"}
    (exec_dir / "implementation-summary-alpha.json").write_text(json.dumps(original), encoding="utf-8")
    (exec_dir / "qa-acceptance-alpha.json").write_text(json.dumps(original), encoding="utf-8")
    facade = run_goal_facade(root, utterance="no overwrite demo", version=VERSION, feature="alpha")
    rid = facade["run_id"]
    attach_verifier(root, rid, refs=["docs/beacon/v1.6.12/qa/real.md"])
    done = complete_goal_run(root, rid)
    assert json.loads((exec_dir / "implementation-summary-alpha.json").read_text(encoding="utf-8")) == original
    assert json.loads((exec_dir / "qa-acceptance-alpha.json").read_text(encoding="utf-8")) == original
    assert all(h.get("event") != "closure_backfilled" for h in done.get("history") or [])
