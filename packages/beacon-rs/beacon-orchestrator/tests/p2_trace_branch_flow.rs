//! AC-128/129/131-133/138-143: TraceSpine hard gates + BranchContext + standard flow.

use beacon_core::branch_context::BranchContext;
use beacon_core::trace_spine::{TraceContext, TraceSpine, REASON_TRACE_MISSING};
use beacon_gate::harness_trace_gate::evaluate_harness_trace_gate;
use beacon_orchestrator::{
    admit_workspace, verify_flow_order, AdmissionBundle, FlowState, HarnessPathController,
    WorkspaceAdmissionRequest, FLOW_STAGES, REASON_FLOW_INCOMPLETE,
};

#[test]
fn tc128_branch_context_from_workspace_admit() {
    let r = admit_workspace(&WorkspaceAdmissionRequest {
        run_id: "run-1".into(),
        caller_cwd: "/work/proj".into(),
        target_project_root: "/work/proj".into(),
        worktree: Some("/work/proj/.beacon/worktrees/feature".into()),
        branch: "feature/x".into(),
        allow_cwd_as_root: true,
    });
    assert!(!r.blocked, "{:?}", r);
    let bc = r.branch_context.unwrap();
    assert_eq!(bc.schema, "BranchContext.v1");
    assert!(bc.admitted);
    assert!(!bc.is_canonical_truth_branch);
    assert_eq!(bc.admitted_worktree, "/work/proj/.beacon/worktrees/feature");
}

#[test]
fn tc129_missing_admission_blocks_governance() {
    let bc = BranchContext::new("r", "/c", "/p", "/p", "main");
    assert!(bc.governance_gate(None).is_err());
}

#[test]
fn tc129_protected_path_on_feature() {
    let bc = BranchContext::new("r", "/c", "/p", "/p", "feature/y").mark_admitted();
    assert!(bc
        .governance_gate(Some("docs/beacon/v2.0.0/features/x/truth.md"))
        .is_err());
}

#[test]
fn tc131_132_loop_start_requires_bindings() {
    let mut ctrl = HarnessPathController::new();
    let bc = BranchContext::new("r9", "/c", "/p", "/p", "main").mark_admitted();
    // incomplete bindings via empty decision packet should fail inside start_loop
    let err = ctrl.start_loop("r9", bc.clone(), "", "is", "th", "des");
    assert!(err.is_err());
    let ok = ctrl.start_loop("r9", bc, "dp:1", "is:1", "th:abc", "des:1");
    assert!(ok.is_ok());
    assert!(ctrl.spine.as_ref().unwrap().events.len() >= 1);
}

#[test]
fn tc133_implement_missing_trace_blocked() {
    let g = evaluate_harness_trace_gate("implement", None, None, false);
    assert!(g.blocked);
    assert_eq!(g.reason_code, REASON_TRACE_MISSING);
}

#[test]
fn tc133_hash_invalid_blocked() {
    let ctx = TraceContext::new("r").with_bindings("b", "d", "i", "t", "x");
    let mut spine = TraceSpine::create("r", ctx);
    spine.append("decision", "a", "e1").unwrap();
    spine.events[0].summary = "tamper".into();
    let g = evaluate_harness_trace_gate("qa-evidence", Some(&spine), None, false);
    assert!(g.blocked);
    assert!(g.reason_code.contains("hash") || g.reason_code.contains("trace"));
}

#[test]
fn tc133_n13_lifecycle_only_cannot_release() {
    let g = evaluate_harness_trace_gate("release", None, None, true);
    assert!(g.blocked);
    assert_eq!(g.reason_code, REASON_TRACE_MISSING);
}

#[test]
fn tc133_complete_path_implement_qa_release_trace() {
    let mut ctrl = HarnessPathController::new();
    let bc = BranchContext::new("r", "/c", "/p", "/p", "main").mark_admitted();
    ctrl.admission = full_admission();
    ctrl.start_loop("r", bc, "dp", "is", "th", "des").unwrap();
    ctrl.append_iteration("work", "ev/iter1").unwrap();
    assert!(ctrl.enter_phase("implement").is_ok());
    assert!(ctrl.enter_phase("qa-evidence").is_ok());
    // release trace gate passes completeness; human release is separate
    assert!(ctrl.enter_phase("release").is_ok());
}

#[test]
fn implement_blocked_without_admission_bundle() {
    let mut ctrl = HarnessPathController::new();
    let bc = BranchContext::new("r", "/c", "/p", "/p", "main").mark_admitted();
    ctrl.start_loop("r", bc, "dp", "is", "th", "des").unwrap();
    ctrl.append_iteration("work", "ev/1").unwrap();
    let err = ctrl.enter_phase("implement").unwrap_err();
    assert!(err.reason_code.contains("standard_flow") || err.reason_code.contains("incomplete") || err.reason_code.contains("canonical"));
}

#[test]
fn tc138_flow_stages_order() {
    assert_eq!(FLOW_STAGES.len(), 8);
    assert_eq!(FLOW_STAGES[0], "support_advisory");
    assert_eq!(FLOW_STAGES[7], "implement_resume");
    let mut s = FlowState::default();
    for next in &FLOW_STAGES[1..] {
        s.advance(next).unwrap();
    }
    assert_eq!(s.current, "implement_resume");
}

#[test]
fn tc138_skip_canonical_commit_blocked() {
    let completed = vec![
        "support_advisory".into(),
        "canonical_truth_authoring".into(),
        "canonical_refreeze".into(),
    ];
    assert!(verify_flow_order(&completed, "feature_worktree_reconcile").is_err());
}

#[test]
fn tc142_admission_bundle() {
    let mut b = AdmissionBundle::empty();
    assert!(b.implement_admission_gate().unwrap_err().contains("standard_flow") || b.implement_admission_gate().is_err());
    b = full_admission();
    assert!(b.implement_admission_gate().is_ok());
}

fn full_admission() -> AdmissionBundle {
    let mut b = AdmissionBundle::empty();
    b.truth_map_verify = true;
    b.verify_materials_strict = true;
    b.diff_check = true;
    b.branch_governance_verify = true;
    b.workspace_admission = true;
    b.truth_baseline_commit = "abc123".into();
    b.baseline_merged_into_feature = true;
    b
}

#[test]
fn tc136_canonical_truth_branch() {
    let feat = BranchContext::new("r", "/c", "/p", "/p", "feature/x").mark_admitted();
    assert!(feat.canonical_truth_write_gate().is_err());
    let main = BranchContext::new("r", "/c", "/p", "/p", "main").mark_admitted();
    assert!(main.canonical_truth_write_gate().is_ok());
}
