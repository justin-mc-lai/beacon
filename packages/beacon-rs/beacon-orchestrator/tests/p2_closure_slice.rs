//! Closure slice: git BranchContext, checkpoint, decision packet path, stagnation, refreeze.

use beacon_core::{
    check_harness_boundary, detect_stagnation, validate_refreeze, DecisionPacket, HarnessBoundaryEvent,
    IntentSnapshot, RefreezeRequest, TraceContext, TraceSpine,
};
use beacon_orchestrator::{
    load_checkpoint, probe_git, stop_with_checkpoint,
};
use std::path::PathBuf;

#[test]
fn git_probe_repo() {
    let here = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let root = here
        .ancestors()
        .find(|p| p.join(".git").exists() || p.join(".git").is_file())
        .expect("repo root")
        .to_path_buf();
    let p = probe_git(&root);
    assert!(p.ok, "{:?}", p);
    assert!(!p.branch.is_empty());
}

#[test]
fn checkpoint_graceful_and_force() {
    let dir = tempfile::tempdir().unwrap();
    let g = stop_with_checkpoint(dir.path(), "r1", "implement", 2, false).unwrap();
    assert!(g.graceful);
    assert!(!g.force_stop);
    let f = stop_with_checkpoint(dir.path(), "r2", "implement", 1, true).unwrap();
    assert!(f.force_stop);
    let loaded = load_checkpoint(dir.path(), "r1").unwrap();
    assert_eq!(loaded.iteration, 2);
}

#[test]
fn decision_packet_and_intent() {
    let intent = IntentSnapshot::new("r", "ship v2 kernel gates", 0.9);
    assert!(intent.freeze_gate().is_ok());
    let low = IntentSnapshot::new("r", "???", 0.1);
    assert!(low.freeze_gate().is_err());
    let pkt = DecisionPacket::for_loop("r", "intent:r", "implement");
    assert!(pkt.loop_admission_gate().is_ok());
}

#[test]
fn stagnation_on_trace() {
    let ctx = TraceContext::new("r").with_bindings("b", "d", "i", "t", "x");
    let mut s = TraceSpine::create("r", ctx);
    s.append("failure", "fail 1", "e1").unwrap();
    s.append("failure", "fail 2", "e2").unwrap();
    let rep = detect_stagnation(&s).unwrap();
    assert!(rep.detected);
    assert_eq!(rep.schema, "stagnation-report.v1");
    assert!(rep.trace_event_range.to_seq >= 2);
}

#[test]
fn refreeze_guards() {
    let bad = RefreezeRequest {
        change_reason: "x".into(),
        human_narrative: "".into(),
        machine_revision_bump: false,
        machine_revision: "".into(),
        human_revision: "".into(),
        truth_body_changed: false,
    };
    assert!(validate_refreeze(&bad).is_err());
}

#[test]
fn harness_boundary() {
    let e = HarnessBoundaryEvent {
        actor_harness: "implement".into(),
        action: "write".into(),
        target_authority: "truth".into(),
    };
    assert!(check_harness_boundary(&e).is_err());
}

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .ancestors()
        .find(|p| p.join("docs/beacon/v2.0.0").is_dir())
        .expect("repo root with docs/beacon/v2.0.0")
        .to_path_buf()
}

#[test]
fn route_examples_exist() {
    let root = repo_root().join("docs/beacon/v2.0.0/fixtures/route-examples");
    assert!(root.join("decision_packet.example.json").is_file(), "{:?}", root);
    assert!(root.join("branch-blocked.example.json").is_file());
}

#[test]
fn reason_codes_doc_exists() {
    let root = repo_root().join("docs/beacon/v2.0.0/execution/reason-codes.md");
    assert!(root.is_file(), "{:?}", root);
    let t = std::fs::read_to_string(root).unwrap();
    assert!(t.contains("trace_spine_missing"));
}
