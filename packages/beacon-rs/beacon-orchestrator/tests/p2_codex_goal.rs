//! AC-043 Codex multi-turn + P2-001 GoalController + AC-126 skill load.

use beacon_core::agent::AgentBackend;
use beacon_orchestrator::{
    build_skill_load_plan, CodexBackend, GoalController, Orchestrator, StopWhen,
};
use beacon_store::BeaconStore;

#[test]
fn tc043_codex_backend_multi_turn_artifacts() {
    let dir = tempfile::tempdir().unwrap();
    let mut backend = CodexBackend::new(dir.path(), 3);
    let store = BeaconStore::open_in_memory().unwrap();
    // need a run for orchestrator status, but we can iterate backend alone
    let r1 = backend.iterate("turn1").unwrap();
    let r2 = backend.iterate("turn2").unwrap();
    assert!(r1.success && r2.success);
    assert!(backend.artifact_refs().len() >= 2);
    assert_ne!(r1.key_changes_made, r2.key_changes_made);
}

#[test]
fn tc043_orchestrator_runs_codex_at_least_two() {
    let dir = tempfile::tempdir().unwrap();
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = beacon_store::ProjectDao::insert(conn, "/tmp/codex", "c").unwrap();
    let fid = beacon_store::FeatureDao::insert(conn, pid, "f", "v2.0.0", "draft", None).unwrap();
    let run_id = beacon_store::RunDao::insert(conn, fid, "codex", beacon_core::RunStatus::Running).unwrap();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(2));
    let mut backend = CodexBackend::new(dir.path(), 5);
    let steps = orch.run(&mut backend, "implement").unwrap();
    assert!(steps.len() >= 2);
    assert!(backend.artifact_refs().len() >= 2);
}

#[test]
fn p2_001_goal_create_status_stop() {
    let store = BeaconStore::open_in_memory().unwrap();
    let ctrl = GoalController::new(&store);
    let handle = ctrl
        .create("/tmp/goal-proj", "goal-proj", "demo-feat", "v2.0.0", "do the thing")
        .unwrap();
    assert!(handle.run_id > 0);
    assert!(handle.release_human_gate);
    assert!(handle.verifier_required);
    let st = ctrl.status(handle.run_id).unwrap();
    assert_eq!(st.phase, "plan");
    let stopped = ctrl.stop(handle.run_id, false).unwrap();
    assert_eq!(stopped.status, "Stopped");
}

#[test]
fn ac126_skill_load_progressive() {
    let plan = build_skill_load_plan("implement", "ralph");
    assert_eq!(plan.schema, "skill_load_plan.v1");
    assert!(plan.bulk_history_forbidden);
    assert!(plan.loaded_count < 10);
    assert_eq!(plan.items.len(), 1);
}
