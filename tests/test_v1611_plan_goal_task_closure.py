"""v1.6.11 Plan/Goal task closure contracts (Program L0–L8 / D3 R2)."""

from __future__ import annotations

from pathlib import Path

import beacon.utils.plan_goal_task_closure as pg
from beacon.utils.feature_package import REASON_PACKAGE_SHAPE_UPGRADE, package_paths
from beacon.utils.program_freeze_gate import build_program_freeze_gate, validate_program_freeze_authenticated


def _filled_response() -> dict:
    return {
        "schema": pg.SCHEMA_FILL_RESPONSE,
        "plain_language_l0": "把大目标拆成可验证任务并闭环。",
        "user_intent_snapshot": "lake_or_ocean: 湖\nscope: full",
        "journeys": [{"id": "J1", "name": "goal to freeze"}],
        "intent_coverage_matrix": [
            {"intent_id": "INT-01", "source": "user", "strength": "must", "landing": "AC-001", "status": "covered", "text": "deliver closure"}
        ],
        "acceptance_criteria": [{"ac_id": "AC-001", "description": "closure works"}],
        "domain_model": "GoalRun / TaskNode / FillTransaction",
        "fsm_quintuples": [
            {"state": "scaffold_materialized", "event": "request_host_fill", "guard": "unfilled", "to": "host_fill_requested", "action": "emit request"}
        ],
        "illegal_transitions": ["scaffold -> frozen"],
        "non_goals": ["auto-release"],
        "projection_inputs": {
            "tests": "| TC ID | AC ID | Command | Assertion |\n|----|----|----|----|\n| TC-001 | AC-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k package_shape_upgrade_required --tb=no` | pass |\n",
            "tasks": "- [ ] TASK-001 Implement AC-001 · ac=AC-001 · evidence=e1\n",
            "evidence": "| surface | authority |\n|---|---|\n| tests | acceptance_truth |\n",
        },
        "source_hash": "sha256:abc",
    }


def _request() -> dict:
    req = {
        "schema": pg.SCHEMA_FILL_REQUEST,
        "utterance": "deliver closure",
        "version": "v1.6.11",
        "revision_id": "R2",
        "source_hashes": {s: f"hash-{s}" for s in ("truth", "tests", "tasks", "evidence")},
        "semantic_compiler_refs": ["legacy-prd-compiler"],
        "host_transport": {"capability": "host-response"},
        "humanizer_profile": {"language": "zh"},
        "program_refs": {"program": "p"},
        "pac_refs": ["PAC-001"],
    }
    req["request_hash"] = pg._stable_hash(req)
    return req


def _envelope_ok() -> dict:
    return pg.build_context_envelope(
        utterance="deliver v1.6.11 closure",
        version="v1.6.11",
        baseline_commit="30b9adff",
        truth_refs={"truth": "docs/beacon/v1.6.11/features/x/truth.md"},
        code_entries=["beacon/utils/plan_goal_task_closure.py"],
        test_entries=["tests/test_v1611_plan_goal_task_closure.py"],
        change_history=["D3"],
        inherited_contracts=["truth-core-authority-v1610"],
        execution_authorities={
            "subagent_runtime": "host_or_fallback",
            "truth_canonical": "main",
            "worktree_governance": "admit",
            "trace_authority": "agent_trace.v1",
        },
        source_hashes={s: f"h-{s}" for s in ("truth", "tests", "tasks", "evidence")},
        semantic_compiler_refs=["prd-semantic"],
        host_transport={"capability": "host-response", "precedence": ["host", "cli"]},
        program_refs={"manifest": "program-manifest.md"},
        pac_refs=["PAC-001", "PAC-021"],
    )


def _receipt(feature: str = "contract-baseline-convergence-v1611") -> dict:
    return {
        "promotion_contract": pg.SCHEMA_PROMOTION,
        "feature": feature,
        "status": "complete",
        "revision_id": "R2",
        "baseline_hash": "sha256:base",
        "source_hashes": {s: f"sha256:{s}" for s in ("truth", "tests", "tasks", "evidence")},
        "package_validation": {"status": "pass", "report_hash": "sha256:pv"},
        "truth_review": {"status": "pass", "report_hash": "sha256:tr"},
        "human_ack_ref": "truth-human-ack:user",
        "scope_ack_ref": "user-confirmation",
    }


# ---- L0 ----

def test_package_shape_upgrade_required():
    bad = {"shape": "legacy", "version": "v1.6.11", "feature": "x"}
    out = pg.detect_package_shape_upgrade_required(bad)
    assert out["blocked"] is True
    assert out["reason_code"] == REASON_PACKAGE_SHAPE_UPGRADE


def test_frozen_truth_lineage():
    ok = pg.assert_frozen_truth_lineage(
        parent_truth="docs/old/truth.md",
        inherited_contracts=["c1"],
        proposed_mutation={"apply_without_new_revision": False},
    )
    assert ok["pass"] is True
    bad = pg.assert_frozen_truth_lineage(
        parent_truth="docs/old/truth.md",
        inherited_contracts=["c1"],
        proposed_mutation={"mutate_parent": True},
    )
    assert bad["blocked"] is True


def test_deterministic_scaffold_not_filled(tmp_path: Path):
    # humanizer optional path may be missing; materialize still works
    (tmp_path / "docs/beacon/v1.6.11").mkdir(parents=True)
    out = pg.materialize_deterministic_scaffold(tmp_path, version="v1.6.11", feature="demo-lake")
    assert out["pass"] is True
    paths = package_paths(tmp_path, version="v1.6.11", feature="demo-lake")
    assert all(paths[s].exists() for s in ("truth", "tests", "tasks", "evidence"))
    assert out["package_maturity"] == "scaffold"
    assert out["recommend_freeze"] is False


def test_semantic_compiler_feature_package_authority():
    ok = pg.semantic_compiler_as_input_only(semantic_payload={"ac": ["AC-001"]})
    assert ok["pass"] is True
    assert ok["authority"] == "feature_package_authoritative"
    bad = pg.semantic_compiler_as_input_only(semantic_payload={"ac": ["AC-001"]}, write_legacy_canonical=True)
    assert bad["blocked"] is True


def test_authenticated_freeze_receipt():
    assert pg.validate_authenticated_freeze_receipt(_receipt())["pass"] is True
    bad = dict(_receipt())
    bad.pop("baseline_hash")
    assert pg.validate_authenticated_freeze_receipt(bad)["blocked"] is True


def test_baseline_illegal_transition():
    assert pg.reject_baseline_illegal_transition(from_state="old_shape", event="deliver", package_shape="legacy")["blocked"]
    assert pg.reject_baseline_illegal_transition(from_state="current", event="verify")["pass"]


# ---- L1 ----

def test_context_envelope():
    out = _envelope_ok()
    assert out["pass"] is True
    assert set(out["envelope"]["surfaces"]) >= {"baseline_commit", "truth_refs", "code_entries", "test_entries", "change_history"}


def test_context_reverse_lookup():
    out = _envelope_ok()
    env = out["envelope"]
    assert "beacon/utils/plan_goal_task_closure.py" in env["surfaces"]["code_entries"]
    assert "tests/test_v1611_plan_goal_task_closure.py" in env["surfaces"]["test_entries"]


def test_context_conflict():
    out = pg.build_context_envelope(
        utterance="x",
        version="v1.6.11",
        baseline_commit="c",
        truth_refs={"t": "t"},
        code_entries=["a"],
        test_entries=["b"],
        change_history=["d"],
        inherited_contracts=["c1"],
        execution_authorities={
            "subagent_runtime": "x",
            "truth_canonical": "main",
            "worktree_governance": "admit",
            "trace_authority": "trace",
        },
        source_hashes={s: "h" for s in ("truth", "tests", "tasks", "evidence")},
        conflicts=[{"kind": "hash_mismatch"}],
    )
    assert out["status"] == "awaiting_human"
    assert out["reason_code"] == "context_conflict"


def test_context_stale():
    a = _envelope_ok()
    b = _envelope_ok()
    # mutate one field then re-fingerprint
    env = dict(a["envelope"])
    env["utterance"] = "changed"
    env["fingerprint"] = ""
    env["fingerprint"] = pg._stable_hash(env)
    assert env["fingerprint"] != a["fingerprint"]


def test_inherited_truth_contracts():
    out = _envelope_ok()
    assert out["envelope"]["inherited_contracts"]


def test_execution_authorities():
    out = _envelope_ok()
    for key in ("subagent_runtime", "truth_canonical", "worktree_governance", "trace_authority"):
        assert key in out["envelope"]["execution_authorities"]


def test_truth_fill_request_context():
    req = pg.build_truth_fill_request(_envelope_ok())
    assert req["pass"] is True
    assert req["request"]["schema"] == pg.SCHEMA_FILL_REQUEST
    assert req["request"]["revision_id"] == "R2"


def test_host_fill_fail_closed():
    assert pg.host_fill_fail_closed(None)["blocked"]
    assert pg.host_fill_fail_closed({"conflict": "x"})["blocked"]
    assert pg.host_fill_fail_closed({"semantic_objects": {"a": 1}})["pass"]


def test_context_illegal_transition():
    assert pg.reject_context_illegal_transition(scanned=False, decision_ref=None, event="resolve")["blocked"]
    assert pg.reject_context_illegal_transition(scanned=True, decision_ref=None, event="continue")["blocked"]


# ---- L2 ----

def test_intent_dimensions():
    intents = [{"dimensions": list(pg.INTENT_DIMENSIONS)}]
    assert pg.evaluate_intent_dimensions(intents)["pass"]


def test_missing_must():
    assert pg.evaluate_missing_must([{"id": "I1", "strength": "must", "landing": None}])["blocked"]
    assert pg.evaluate_missing_must([{"id": "I1", "strength": "must", "landing": "AC-1"}])["pass"]


def test_semantic_stop():
    assert pg.reject_semantic_stop_by_count(node_count=120, semantic_complete=False)["blocked"]
    assert pg.reject_semantic_stop_by_count(node_count=120, semantic_complete=True)["pass"]


def test_intent_human_decision():
    assert pg.require_intent_human_decision(ambiguous=True, decision_ref=None)["blocked"]
    assert pg.require_intent_human_decision(ambiguous=True, decision_ref="d1")["pass"]


def test_inherited_must_intents():
    landings = {k: f"AC-{i}" for i, k in enumerate(pg.INHERITED_MUST_INTENTS, 1)}
    assert pg.evaluate_inherited_must_intents(landings)["pass"]


def test_host_llm_full_package_fill():
    assert pg.validate_host_llm_full_package_fill(_filled_response())["pass"]
    bad = dict(_filled_response())
    bad.pop("fsm_quintuples")
    assert pg.validate_host_llm_full_package_fill(bad)["blocked"]


def test_false_completeness_blocked():
    bad = dict(_filled_response())
    bad["domain_skipped"] = True
    assert pg.reject_false_completeness(bad)["blocked"]
    assert pg.reject_false_completeness(_filled_response())["pass"]


def test_intent_illegal_transition():
    assert pg.reject_intent_illegal_transition(missing_must=True, decision_ref=None, force_complete=True)["blocked"]
    assert pg.reject_intent_illegal_transition(missing_must=False, decision_ref="d", force_complete=True)["pass"]


# ---- L3 ----

def test_five_surface_diff():
    out = pg.build_five_surface_diff(
        {s: "b" for s in pg.FIVE_SURFACES},
        {s: "a" for s in pg.FIVE_SURFACES},
    )
    assert out["pass"] and set(out["surfaces"]) == set(pg.FIVE_SURFACES)


def test_fsm_diff():
    out = pg.build_fsm_diff(
        [{"from": "a", "event": "e", "to": "b"}],
        [{"from": "a", "event": "e", "to": "b"}, {"from": "b", "event": "x", "to": "c"}],
    )
    assert out["added"]


def test_diff_traceability():
    assert pg.require_diff_traceability({"bindings": {"intent_id": "I", "code_scope": "c", "tc_id": "T"}})["pass"]
    assert pg.require_diff_traceability({"bindings": {}})["blocked"]


def test_destructive_diff_review():
    assert pg.require_destructive_diff_review(high_risk=True, human_ack=None)["blocked"]
    assert pg.require_destructive_diff_review(high_risk=True, human_ack="ack")["pass"]


def test_inherited_surface_diff():
    surfaces = {k: True for k in ("lifecycle", "delegation", "admission", "trace", "goal_ownership", "no_compat")}
    assert pg.evaluate_inherited_surface_diff(surfaces)["pass"]


def test_structured_fill_patch_transaction(tmp_path: Path):
    (tmp_path / "docs/beacon/v1.6.11").mkdir(parents=True)
    ok = pg.apply_structured_fill_transaction(
        tmp_path,
        version="v1.6.11",
        feature="fill-demo",
        request=_request(),
        response=_filled_response(),
    )
    assert ok["pass"] is True
    assert ok["transaction"]["schema"] == pg.SCHEMA_FILL_TRANSACTION
    bad = pg.apply_structured_fill_transaction(
        tmp_path,
        version="v1.6.11",
        feature="fill-demo",
        request=_request(),
        response=_filled_response(),
        allow_direct_markdown_overwrite=True,
    )
    assert bad["blocked"] is True


def test_full_fill_changeplan_fsm():
    out = pg.evaluate_full_fill_changeplan_fsm()
    assert ("scaffold_materialized", "request_host_fill", "host_fill_requested") in out["edges"]
    assert out["steps"][-1] == "freeze"


def test_diff_illegal_transition():
    assert pg.reject_diff_illegal_transition(missing_surface=True, human_ack=None, approve=True)["blocked"]


# ---- L4 ----

def test_atomic_compile():
    assert pg.compile_atomic_tasks([{"id": "t1", "verification": "pytest"}])["pass"]
    assert pg.compile_atomic_tasks([{"id": "t1"}])["blocked"]


def test_task_trace_bindings():
    node = {k: "x" for k in pg.REQUIRED_TASK_BINDINGS}
    assert pg.require_task_trace_bindings(node)["pass"]


def test_dag_ready_set():
    nodes = [
        {"id": "a", "dependencies": [], "status": "done"},
        {"id": "b", "dependencies": ["a"], "status": "ready"},
    ]
    assert pg.compute_dag_ready_set(nodes)["ready_set"] == ["b"]
    cycle = [{"id": "a", "dependencies": ["b"]}, {"id": "b", "dependencies": ["a"]}]
    assert pg.compute_dag_ready_set(cycle)["blocked"]


def test_orphan_padding():
    nodes = [{"id": "root", "is_root": True, "dependencies": []}, {"id": "pad", "padding": True, "dependencies": []}]
    assert pg.reject_orphan_padding(nodes)["blocked"]


def test_graph_scale():
    nodes = [{"id": f"n{i}", "dependencies": [], "verification": "x"} for i in range(120)]
    out = pg.accept_graph_scale(nodes)
    assert out["count"] == 120 and out["count_is_not_kpi"] is True


def test_task_delegation_contract():
    node = {"delegated": True, "execution_mode": "host", "role": "reviewer", "reason": "x", "evidence": "e"}
    assert pg.validate_task_delegation_contract(node)["pass"]
    bad = dict(node)
    bad["child_completion_authority"] = True
    assert pg.validate_task_delegation_contract(bad)["blocked"]


def test_honest_subagent_fallback():
    out = pg.honest_subagent_fallback(host_agents=False, intent_on=True)
    assert out["honest_fallback"] is True


def test_implementation_worktree_admission():
    ok = {
        "service": "beacon",
        "admission_ref": "adm",
        "worktree_path": "/tmp/.beacon/worktrees/x",
        "cwd": "/tmp/.beacon/worktrees/x",
        "git_head": "abc",
    }
    assert pg.require_implementation_worktree_admission(ok)["pass"]
    assert pg.require_implementation_worktree_admission({"main_write": True})["blocked"]


def test_deterministic_package_projection():
    assert pg.require_deterministic_package_projection(
        ac_ids=["AC-001"],
        tests=[{"ac_id": "AC-001", "command": "pytest", "assertion": "pass"}],
        tasks=[{"ac_id": "AC-001", "evidence": "e"}],
        evidence={"transaction_hash": "h", "revision_id": "R2"},
    )["pass"]


def test_semantic_compile_forward_migration():
    assert pg.semantic_compile_forward_migration(legacy_semantics={"ac": 1}, execution_inputs={})["pass"]
    assert pg.semantic_compile_forward_migration(legacy_semantics={"ac": 1}, execution_inputs={"old_shape": True})["blocked"]


def test_task_graph_illegal_transition():
    assert pg.reject_task_graph_illegal_transition(cycle=True, orphan=False, stale_graph=False, admission_missing=False)["blocked"]


# ---- L5 ----

def test_task_attempt_fields():
    assert pg.record_task_attempt({"task_id": "t", "attempt": 1, "status": "running", "feedback": "x", "started_at": "t"})["pass"]


def test_feedback_append_only():
    assert pg.append_feedback([], {"text": "a"})["pass"]
    assert pg.append_feedback([], {"text": "a", "overwrite_index": 0})["blocked"]


def test_path_progress():
    nodes = [
        {"status": "done"},
        {"status": "blocked"},
        {"status": "cancelled"},
        {"status": "ready"},
        {"status": "superseded", "replacement_of": "x"},
    ]
    out = pg.aggregate_path_progress(nodes)
    assert out["path_progress"]["completed"] == 1
    assert out["path_progress"]["remaining"] == 1


def test_progress_revision():
    assert pg.stale_progress_on_revision("R1", "R2")["blocked"]
    assert pg.stale_progress_on_revision("R2", "R2")["pass"]


def test_goal_run_lifecycle_trace():
    assert pg.bind_goal_run_lifecycle_trace(
        {"run_id": "r", "internal_state": "running", "public_stage": "implement", "agent_trace_ref": "trace"}
    )["pass"]


def test_trace_append_fail_closed():
    assert pg.apply_state_with_trace(transition_ok=True, trace_append_ok=False)["blocked"]
    assert pg.apply_state_with_trace(transition_ok=True, trace_append_ok=True)["committed"] is True


def test_fill_transaction_progress_replay():
    steps = [
        {"sequence": i + 1, "name": name, "hash": f"h{i}", "status": "ok", "feedback": ""}
        for i, name in enumerate(pg.FILL_STEPS)
    ]
    assert pg.record_fill_transaction_progress(steps)["replayable"] is True


def test_ledger_illegal_transition():
    assert pg.reject_ledger_illegal_transition(sequence_gap=True, stale_snapshot=False, trace_failed=False)["blocked"]


# ---- L6 ----

def test_drift_kinds():
    findings = [{"kind": k} for k in pg.DRIFT_KINDS]
    assert pg.detect_drift_kinds(findings)["pass"]


def test_drift_pause():
    out = pg.pause_on_drift([{"kind": "padding_task", "severity": "mandatory"}])
    assert out["status"] == "awaiting_human"


def test_human_choices():
    assert pg.validate_human_choice("rewrite")["pass"]
    assert pg.validate_human_choice("ignore")["blocked"]


def test_decision_ref():
    assert pg.require_decision_ref(decision_ref=None, event="continue")["blocked"]
    assert pg.require_decision_ref(decision_ref="d1", event="continue")["pass"]


def test_advisory_finding_sources():
    assert pg.advisory_findings_cannot_mutate("subagent", mutates_canonical=True)["blocked"]
    assert pg.advisory_findings_cannot_mutate("subagent", mutates_canonical=False)["pass"]


def test_canonical_human_gate_owner():
    assert pg.apply_canonical_human_gate(actor="beacon_policy", decision_ref="d", parent_scheduler=True)["pass"]
    assert pg.apply_canonical_human_gate(actor="subagent", decision_ref="d", parent_scheduler=True)["blocked"]


def test_hollow_fill_review_gate():
    findings = [{"kind": k} for k in ("placeholder", "hollow_domain", "orphan", "hanging_fsm", "padding", "evidence_hash_drift")]
    out = pg.hollow_fill_review_gate(findings)
    assert out["reason_code"] == "hollow_fill_review_gate"
    assert set(out["choices"]) == set(pg.HUMAN_CHOICES)


def test_review_gate_illegal_transition():
    assert pg.reject_review_gate_illegal_transition(decision_ref=None, event="resume")["blocked"]


# ---- L7 ----

def test_replan_choices():
    out = pg.apply_replan_choice("cancel", {"id": "t1", "status": "running"})
    assert out["task"]["disposition"] == "cancelled"


def test_required_cancel():
    task = {"id": "t1", "required": True, "status": "cancelled"}
    assert pg.required_cancel_without_replacement(task, [{"id": "t2"}])["blocked"]


def test_ready_recompute():
    nodes = [
        {"id": "a", "status": "cancelled", "required": True},
        {"id": "b", "status": "ready", "dependencies": ["a"]},
    ]
    out = pg.recompute_ready_after_cancel(nodes)
    assert "b" in out["blocked"]


def test_evidence_reuse():
    assert pg.evidence_reuse_policy(cancelled=True, reusable=False)["evidence_status"] == "stale"


def test_illegal_terminal_transition():
    assert pg.reject_illegal_terminal_transition(status="cancelled", to_status="done")["blocked"]


def test_goal_scheduler_shared_admission():
    binding = {
        "service": "beacon",
        "admission_ref": "a",
        "worktree_path": "/x/worktree/y",
        "cwd": "/x/worktree/y",
        "git_head": "h",
    }
    assert pg.goal_scheduler_shared_admission(["direct", "goal", "team", "ralph"], binding)["pass"]


def test_refreeze_invalidates_dispatch():
    assert pg.refreeze_invalidates_dispatch(graph_stale=True, ready_stale=False, admission_stale=False)["blocked"]


def test_fill_task_failure_recovery():
    assert pg.fill_task_failure_recovery(failure_kind="timeout", retry_budget=1)["route"] == "retry_wait"
    assert pg.fill_task_failure_recovery(failure_kind="human_reject", retry_budget=0)["governed"] is True


def test_no_open_work_closure_ready():
    assert pg.no_open_work_closure_ready(ready_set=[], blocked_open=[], remaining_required=[])["closure_ready"] is True
    assert pg.no_open_work_closure_ready(ready_set=[], blocked_open=["t1"], remaining_required=[])["blocked"]


def test_replan_illegal_transition():
    assert pg.reject_replan_illegal_transition(after_cancel=True, after_refreeze=False, event="dispatch")["blocked"]


# ---- L8 ----

def test_closure_matrix():
    links = {layer: ["x"] for layer in pg.CLOSURE_LAYERS}
    assert pg.evaluate_closure_matrix(links)["pass"]


def test_goal_completion():
    assert pg.evaluate_goal_completion(["task"])["blocked"]
    assert pg.evaluate_goal_completion([])["complete"] is True


def test_stale_blocks():
    assert pg.stale_blocks_completion(stale=["graph"])["blocked"]


def test_goal_owner():
    assert pg.reject_goal_owner_subagent_complete(actor="subagent")["blocked"]
    assert pg.reject_goal_owner_subagent_complete(actor="parent_goal")["pass"]


def test_minimal_gap_route():
    out = pg.minimal_gap_route(["evidence"])
    assert out["blocked"] and out["gaps"][0]["route"] == "qa"


def test_goal_run_required_refs():
    refs = {
        "program_ref": "p",
        "graph_ref": "g",
        "truth_ref": "t",
        "ready_ref": "r",
        "decision_ref": "d",
        "admission_ref": "a",
        "trace_ref": "tr",
        "verifier_ref": "v",
    }
    assert pg.require_goal_run_refs(refs)["pass"]


def test_public_lifecycle_boundary():
    assert pg.enforce_public_lifecycle_boundary(["plan", "truth", "implement", "qa", "release", "goal"])["pass"]
    assert pg.enforce_public_lifecycle_boundary(["plan", "loop-goal"])["blocked"]


def test_pac_full_trace_matrix():
    rows = [
        {
            "pac_id": "PAC-001",
            "lake": "L0",
            "ac_id": "AC-1",
            "tc_id": "TC-1",
            "task_id": "T1",
            "evidence": "e",
            "revision_id": "R2",
            "final_hash": "h",
        }
    ]
    assert pg.evaluate_pac_full_trace_matrix(rows)["pass"]


def test_authenticated_program_freeze(tmp_path: Path):
    # status-only rejected
    bad = [{"status": "complete", "feature": "x"}]
    assert pg.validate_authenticated_program_freeze(tmp_path, version="v1.6.11", program_slug="p", lake_receipts=bad)["blocked"]
    ok = [_receipt("x")]
    # no package files => hash compare skipped, receipt structure ok
    assert pg.validate_authenticated_program_freeze(tmp_path, version="v1.6.11", program_slug="p", lake_receipts=ok)["pass"]


def test_fill_chain_convergence():
    assert pg.evaluate_fill_chain_convergence(
        transaction_steps=list(pg.FILL_STEPS),
        progress_ref="progress",
        recovery_ref="recovery",
    )["pass"]
    assert pg.evaluate_fill_chain_convergence(transaction_steps=["scaffold"], progress_ref=None, recovery_ref=None)["blocked"]


def test_convergence_illegal_transition():
    assert pg.reject_convergence_illegal_transition(actor="child", stale_verdict=False, new_public_harness=False)["blocked"]


def test_program_freeze_gate_authenticated_helper():
    # pure helper import surface
    assert callable(validate_program_freeze_authenticated)
    assert callable(build_program_freeze_gate)
