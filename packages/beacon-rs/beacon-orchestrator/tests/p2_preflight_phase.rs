//! P2 wrap-up tests — AC-041 (truth-map preflight) + AC-050 (phase controller).

use beacon_orchestrator::{truth_map_preflight, PhaseState};
use beacon_store::{BeaconStore, FeatureDao, ProjectDao, RunDao};
use beacon_core::RunStatus;
use tempfile::tempdir;

// ---- AC-041 truth-map preflight ----

#[test]
fn tc041_truth_map_preflight_pass_when_frozen() {
    let dir = tempdir().unwrap();
    let truth_md = dir.path().join("truth.md");
    std::fs::write(
        &truth_md,
        "---\nslug: demo\nstatus: frozen\nversion: v2.0.0\n---\n# truth\n",
    )
    .unwrap();
    let pf = truth_map_preflight(&truth_md);
    assert!(!pf.blocked);
    assert_eq!(pf.feature_status, "frozen");
    assert_eq!(pf.status, "pass");
}

#[test]
fn tc041_truth_map_preflight_blocked_when_draft() {
    let dir = tempdir().unwrap();
    let truth_md = dir.path().join("truth.md");
    std::fs::write(
        &truth_md,
        "---\nslug: demo\nstatus: draft\nversion: v2.0.0\n---\n# truth\n",
    )
    .unwrap();
    let pf = truth_map_preflight(&truth_md);
    assert!(pf.blocked);
    assert_eq!(pf.status, "blocked");
    assert!(pf.reason.contains("beacon change") || pf.reason.contains("freeze"));
}

#[test]
fn tc041_truth_map_preflight_blocked_when_file_missing() {
    let pf = truth_map_preflight(std::path::Path::new("/nonexistent/truth.md"));
    assert!(pf.blocked);
    assert!(pf.reason.contains("read failed"));
}

// ---- AC-050 phase controller ----

#[test]
fn tc050_phase_controller_writes_metadata_and_events() {
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();

    let mut phase = PhaseState::new();
    // plan -> truth -> generate -> evaluate
    phase.transition(&store, run_id, fid, "truth").unwrap();
    phase.transition(&store, run_id, fid, "generate").unwrap();
    phase.transition(&store, run_id, fid, "evaluate").unwrap();

    // AC-050: runs.metadata_json must contain the phase + completed
    let metadata = RunDao::get_metadata(conn, run_id).unwrap().expect("metadata");
    assert!(metadata.contains("evaluate"));
    assert!(metadata.contains("phases_completed"));
    let state: PhaseState = serde_json::from_str(&metadata).unwrap();
    assert_eq!(state.phase, "evaluate");
    assert!(state.phases_completed.contains(&"plan".to_string()));
    assert!(state.phases_completed.contains(&"truth".to_string()));
    assert!(state.phases_completed.contains(&"generate".to_string()));

    // AC-050: lifecycle_events must have PhaseTransition events
    let events = beacon_store::LifecycleEventDao::list_for_feature(conn, fid).unwrap();
    let transitions: Vec<_> = events.into_iter().filter(|(_, et, _)| et == "PhaseTransition").collect();
    assert_eq!(transitions.len(), 3, "3 phase transitions should be recorded");
}
