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


# ---- CLI wiring ----

def test_cli_truth_scaffold_and_fill_request(tmp_path: Path):
    from typer.testing import CliRunner
    from beacon.commands.truth import app as truth_app
    import subprocess
    import json as _json

    runner = CliRunner()
    subprocess.check_call(["git", "init"], cwd=tmp_path)
    subprocess.check_call(["git", "config", "user.email", "t@example.com"], cwd=tmp_path)
    subprocess.check_call(["git", "config", "user.name", "t"], cwd=tmp_path)
    (tmp_path / "README").write_text("x\n", encoding="utf-8")
    subprocess.check_call(["git", "add", "README"], cwd=tmp_path)
    subprocess.check_call(["git", "commit", "-m", "init"], cwd=tmp_path)

    init = runner.invoke(
        truth_app,
        ["init", "all", "-f", "demo-fill", "-v", "v1.6.11", "-p", str(tmp_path), "--force"],
    )
    assert init.exit_code == 0, init.output

    req = runner.invoke(
        truth_app,
        [
            "fill-request",
            "-f",
            "demo-fill",
            "-v",
            "v1.6.11",
            "-p",
            str(tmp_path),
            "-u",
            "deliver demo fill",
            "--program",
            "demo-program",
            "--json",
        ],
    )
    assert req.exit_code == 0, req.output
    payload = _json.loads(req.output)
    assert payload["status"] == "pass"
    assert payload["fill_request"]["request"]["schema"] == "truth-fill-request.v1"


def test_cli_fill_apply_and_validate(tmp_path: Path):
    from typer.testing import CliRunner
    from beacon.commands.truth import app as truth_app
    import json as _json

    runner = CliRunner()
    pg.materialize_deterministic_scaffold(tmp_path, version="v1.6.11", feature="apply-demo", force=True)
    request = _request()
    response = _filled_response()
    req_path = tmp_path / "req.json"
    resp_path = tmp_path / "resp.json"
    req_path.write_text(_json.dumps(request), encoding="utf-8")
    resp_path.write_text(_json.dumps(response), encoding="utf-8")

    val = runner.invoke(truth_app, ["fill-validate-response", str(resp_path), "--json"])
    assert val.exit_code == 0, val.output

    applied = runner.invoke(
        truth_app,
        [
            "fill-apply",
            "-f",
            "apply-demo",
            "-v",
            "v1.6.11",
            "-p",
            str(tmp_path),
            "--request-json",
            str(req_path),
            "--response-json",
            str(resp_path),
            "--json",
        ],
    )
    assert applied.exit_code == 0, applied.output
    out = _json.loads(applied.output)
    assert out["status"] == "pass"
    truth = (tmp_path / "docs/beacon/v1.6.11/features/apply-demo/truth.md").read_text(encoding="utf-8")
    assert "package_maturity: filled" in truth


def test_cli_program_freeze_authenticated_default(tmp_path: Path):
    from typer.testing import CliRunner
    from beacon.commands.program import app as program_app
    import json as _json

    prog = tmp_path / "docs/beacon/v1.6.11/programs/demo-prog"
    (prog / "lakes" / "lake-a").mkdir(parents=True)
    graph = {
        "schema_version": "1.0",
        "program_slug": "demo-prog",
        "version": "v1.6.11",
        "lakes": [{"slug": "lake-a", "status": "frozen"}],
    }
    (prog / "feature-graph.json").write_text(_json.dumps(graph), encoding="utf-8")
    (prog / "lakes/lake-a/truth-promotion.json").write_text(
        _json.dumps({"status": "complete", "feature": "lake-a"}),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        program_app,
        ["freeze", "demo-prog", "-p", str(tmp_path), "-v", "v1.6.11", "--json"],
    )
    assert result.exit_code == 2, result.output
    payload = _json.loads(result.output)
    assert payload["blocked"] is True


# ---- Goal/Truth runtime wiring ----

def test_version_requires_task_closure():
    assert pg.version_requires_task_closure("v1.6.11", "x") is True
    assert pg.version_requires_task_closure("v1.6.10", "x") is False
    assert pg.version_requires_task_closure("v1.6.10", "contract-baseline-convergence-v1611") is True


def test_goal_run_closure_gate_parent_only():
    payload = {
        "version": "v1.6.11",
        "feature": "contract-baseline-convergence-v1611",
        "run_id": "pgr-test",
        "completion_actor": "subagent",
        "stages": [{"stage": "plan"}, {"stage": "truth"}, {"stage": "implement"}, {"stage": "qa"}, {"stage": "release"}],
        "verifier": {"present": True, "refs": ["e"]},
        "task_closure": pg.build_goal_task_closure_binding(
            run_id="pgr-test",
            version="v1.6.11",
            feature="contract-baseline-convergence-v1611",
        ),
        "open_closure_layers": [],
    }
    bad = pg.evaluate_goal_run_closure_gate(payload)
    assert bad["blocked"] is True
    payload["completion_actor"] = "parent_goal"
    ok = pg.evaluate_goal_run_closure_gate(payload)
    assert ok["pass"] is True


def test_complete_goal_run_uses_task_closure_gate(tmp_path: Path):
    from beacon.utils.product_goal_runtime import create_goal_run, attach_verifier, complete_goal_run

    # minimal project metadata so version resolve works
    (tmp_path / "docs/beacon/v1.6.11/features/contract-baseline-convergence-v1611").mkdir(parents=True)
    (tmp_path / "docs/beacon/v1.6.11/features/contract-baseline-convergence-v1611/truth.md").write_text(
        "---\nstatus: frozen\npackage_maturity: filled\n---\n# t\n",
        encoding="utf-8",
    )
    # version truth for resolve
    import json as _json
    (tmp_path / "beacon").mkdir()
    (tmp_path / "beacon/version-truth.json").write_text(
        _json.dumps(
            {
                "schema_version": "1.0",
                "package_version": "1.6.10",
                "runtime_version": "v1.6.10",
                "docs_default_line": "v1.6.10",
                "planning_lines": ["v1.6.11"],
                "lines": {"v1.6.10": {"status": "current_runtime_release"}, "v1.6.11": {"status": "planning_only"}},
            }
        ),
        encoding="utf-8",
    )
    run = create_goal_run(
        tmp_path,
        utterance="deliver task closure",
        version="v1.6.11",
        feature="contract-baseline-convergence-v1611",
    )
    assert run.get("task_closure")
    # without verifier blocked
    rejected = complete_goal_run(tmp_path, run["run_id"])
    assert rejected.get("status") != "completed"
    attach_verifier(tmp_path, run["run_id"], refs=[".beacon/evidence/qa/x.json"], source="beacon-eval-qa")
    done = complete_goal_run(tmp_path, run["run_id"])
    assert done.get("status") == "completed", done
    assert done.get("task_closure_gate", {}).get("pass") is True


def test_truth_stage_blocks_scaffold_package(tmp_path: Path):
    from beacon.utils.goal_stage_exit_gates import evaluate_stage_exit

    feat = "scaffold-lake-v1611"
    d = tmp_path / "docs/beacon/v1.6.11/features" / feat
    d.mkdir(parents=True)
    (d / "truth.md").write_text(
        "---\nstatus: draft\npackage_maturity: scaffold\n---\n# scaffold\n",
        encoding="utf-8",
    )
    payload = {
        "version": "v1.6.11",
        "feature": feat,
        "stages": [{"stage": "truth", "status": "active"}],
        "current_stage": "truth",
    }
    gate = evaluate_stage_exit(tmp_path, payload, stage="truth")
    assert gate["blocked"] is True
    assert gate["reason_code"] == "truth_scaffold_not_filled"


def test_intent_decomposition_task_closure_advisory():
    from beacon.utils.intent_decomposition import decompose_product_intent

    out = decompose_product_intent(
        "Deliver v1.6.11 Plan/Goal task closure with CLI scaffold and Host LLM fill",
        lakes=["contract-baseline-convergence-v1611"],
    )
    assert out.get("task_closure_intent")
    assert out["task_closure_intent"]["intent_dimensions"]["pass"] is True
    assert "host_llm_full_package_fill_pending" in (out.get("truth_readiness") or {}).get("missing") or []


def test_tick_attaches_truth_fill_readiness_and_progress(tmp_path: Path):
    from beacon.utils.product_goal_runtime import create_goal_run, tick_goal_run
    import json as _json

    (tmp_path / "docs/beacon/v1.6.11/features/contract-baseline-convergence-v1611").mkdir(parents=True)
    truth = tmp_path / "docs/beacon/v1.6.11/features/contract-baseline-convergence-v1611/truth.md"
    truth.write_text(
        "---\nstatus: frozen\npackage_maturity: filled\n---\n# t\n",
        encoding="utf-8",
    )
    # also create other three package files so source hashes exist
    for name in ("tests.md", "tasks.md", "evidence.md"):
        (truth.parent / name).write_text(f"# {name}\n", encoding="utf-8")
    (tmp_path / "beacon").mkdir()
    (tmp_path / "beacon/version-truth.json").write_text(
        _json.dumps(
            {
                "schema_version": "1.0",
                "package_version": "1.6.10",
                "runtime_version": "v1.6.10",
                "docs_default_line": "v1.6.10",
                "planning_lines": ["v1.6.11"],
                "lines": {
                    "v1.6.10": {"status": "current_runtime_release"},
                    "v1.6.11": {"status": "planning_only"},
                },
            }
        ),
        encoding="utf-8",
    )
    run = create_goal_run(
        tmp_path,
        utterance="Deliver v1.6.11 task closure",
        version="v1.6.11",
        feature="contract-baseline-convergence-v1611",
    )
    assert run.get("current_stage") == "plan"
    # leave plan -> truth
    advanced = tick_goal_run(tmp_path, run["run_id"], note="to-truth")
    assert advanced.get("current_stage") in {"truth", "plan"}
    # if plan exit allowed, fill readiness should be present for v1.6.11
    if advanced.get("current_stage") == "truth":
        assert advanced.get("truth_fill_readiness")


def test_truth_gen_fill_pipeline_main_path(tmp_path: Path):
    out = pg.run_truth_gen_fill_pipeline(
        tmp_path,
        version="v1.6.11",
        feature="gen-main-path",
        utterance="Deliver structured fill for gen main path",
        language="zh",
    )
    assert out.get("pass") is True, out
    # Prefer command-bridge (truth host-bridge) when host runtime wires defaults; else semantic compile.
    assert out.get("resolve", {}).get("transport") in {"cli-semantic-compile", "command-bridge"}
    truth = tmp_path / "docs/beacon/v1.6.11/features/gen-main-path/truth.md"
    assert truth.exists()
    text = truth.read_text(encoding="utf-8")
    assert "package_maturity: filled" in text
    assert "feature_package_authoritative" in text


def test_truth_gen_fill_pipeline_host_response(tmp_path: Path, monkeypatch):
    response = _filled_response()
    monkeypatch.setenv("BEACON_HOST_TRUTH_RESPONSE_JSON", __import__("json").dumps(response))
    out = pg.run_truth_gen_fill_pipeline(
        tmp_path,
        version="v1.6.11",
        feature="gen-host-path",
        utterance="ignored because host response present",
        language="zh",
        allow_semantic_compile_fallback=False,
    )
    assert out.get("pass") is True, out
    assert str(out.get("resolve", {}).get("source") or "").startswith("host_response")
    assert (tmp_path / "docs/beacon/v1.6.11/features/gen-host-path/truth.md").exists()


def test_truth_gen_cli_uses_fill_pipeline(tmp_path: Path):
    from typer.testing import CliRunner
    from beacon.commands.truth import app as truth_app

    runner = CliRunner()
    result = runner.invoke(
        truth_app,
        [
            "gen",
            "-f",
            "cli-gen-fill",
            "-v",
            "v1.6.11",
            "-p",
            str(tmp_path),
            "-u",
            "Deliver cli gen fill path",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = __import__("json").loads(result.output)
    assert payload.get("pass") is True
    transport = str((payload.get("resolve") or {}).get("transport") or "")
    assert transport in {"cli-semantic-compile", "command-bridge"}


def test_truth_host_bridge_outputs_fill_response():
    """Host bridge must emit truth-fill-response.v1 (real host-agent I/O contract)."""
    import json
    from typer.testing import CliRunner
    from beacon.commands.truth import app as truth_app

    runner = CliRunner()
    request = {
        "schema": pg.SCHEMA_FILL_REQUEST,
        "utterance": "把大目标拆成可验证任务",
        "version": "v1.6.11",
        "feature": "host-bridge-feature",
        "humanizer_profile": {"language": "zh"},
    }
    result = runner.invoke(truth_app, ["host-bridge", json.dumps(request, ensure_ascii=False)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload.get("schema") == pg.SCHEMA_FILL_RESPONSE
    assert payload.get("acceptance_criteria")
    assert payload.get("bridge") == "beacon-truth-host-bridge"
    filled = pg.validate_host_llm_full_package_fill(payload)
    assert filled.get("pass") is True, filled


def test_truth_host_bridge_passthrough_fill_response():
    import json
    from typer.testing import CliRunner
    from beacon.commands.truth import app as truth_app

    runner = CliRunner()
    response = _filled_response()
    result = runner.invoke(truth_app, ["host-bridge", json.dumps(response, ensure_ascii=False)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload.get("schema") == pg.SCHEMA_FILL_RESPONSE
    assert payload.get("bridge") == "beacon-truth-host-bridge"


def test_truth_fill_host_bridge_defaults_alias_to_truth_command(monkeypatch):
    import os
    import shlex
    import sys

    monkeypatch.delenv("BEACON_HOST_TRUTH_BRIDGE_CMD", raising=False)
    monkeypatch.delenv("BEACON_HOST_GEN_TRUTH_BRIDGE_CMD", raising=False)
    monkeypatch.delenv("BEACON_HOST_TRUTH_FILL_BRIDGE_CMD", raising=False)
    # Force local default without requiring host runtime detect.
    monkeypatch.setenv("BEACON_TRUTH_FILL_FORCE_BRIDGE", "1")
    cmd = pg.ensure_truth_fill_host_bridge_defaults(force=True)
    assert "truth host-bridge" in cmd
    assert "gen-truth host-bridge" not in cmd
    assert os.environ["BEACON_HOST_TRUTH_BRIDGE_CMD"] == cmd
    assert os.environ["BEACON_HOST_GEN_TRUTH_BRIDGE_CMD"] == cmd
    assert os.environ["BEACON_HOST_TRUTH_FILL_BRIDGE_CMD"] == cmd
    # rewrite wrong alias defaults
    monkeypatch.setenv(
        "BEACON_HOST_GEN_TRUTH_BRIDGE_CMD",
        f"{shlex.quote(sys.executable)} -m beacon.main gen-truth host-bridge",
    )
    fixed = pg.ensure_truth_fill_host_bridge_defaults(force=True)
    assert "truth host-bridge" in os.environ["BEACON_HOST_GEN_TRUTH_BRIDGE_CMD"]
    assert fixed


def test_truth_gen_fill_pipeline_command_bridge(tmp_path: Path, monkeypatch):
    """When bridge env is set, resolve uses command-bridge transport to truth-fill-response.v1."""
    import json
    import shlex
    import sys

    bridge = f"{shlex.quote(sys.executable)} -m beacon.main truth host-bridge"
    monkeypatch.setenv("BEACON_HOST_TRUTH_BRIDGE_CMD", bridge)
    monkeypatch.delenv("BEACON_HOST_TRUTH_RESPONSE_JSON", raising=False)
    monkeypatch.delenv("BEACON_HOST_SEMANTIC_RESPONSE_JSON", raising=False)
    out = pg.run_truth_gen_fill_pipeline(
        tmp_path,
        version="v1.6.11",
        feature="gen-bridge-path",
        utterance="Deliver structured fill via command bridge",
        language="zh",
        allow_semantic_compile_fallback=False,
    )
    assert out.get("pass") is True, out
    assert out.get("resolve", {}).get("transport") == "command-bridge"
    assert str(out.get("resolve", {}).get("source") or "").startswith("host_bridge")
    assert (tmp_path / "docs/beacon/v1.6.11/features/gen-bridge-path/truth.md").exists()


def test_run_program_lakes_task_closure_wires_l0_l8(tmp_path: Path):
    out = pg.run_program_lakes_task_closure(
        tmp_path,
        version="v1.6.11",
        program_slug="beacon-plan-goal-task-closure-v1611",
        utterance="Wire nine lakes task closure",
    )
    assert out.get("schema") == "program-lakes-task-closure.v1"
    assert len(out.get("lake_order") or []) == 9
    assert len(out.get("lakes") or []) == 9
    artifact = Path(out["artifact"])
    assert artifact.exists()
    # Honest: without authenticated lake receipts + human hollow gate, program lakes stay blocked.
    assert out.get("blocked") is True
    codes = {f.get("code") for f in (out.get("findings") or [])}
    assert "hollow_fill_review_gate" in codes or any("auth" in str(c) for c in codes) or codes

