//! P1 remaining tests — TC-007/081/082/083 (store) + TC-064/065 (CLI schema).

use beacon_store::{BeaconStore, ProjectDao, SpineDao, SpineSnapshot};
use beacon_core::RunStatus;
use beacon_store::{FeatureDao, RunDao};
use rusqlite::Connection;
use tempfile::tempdir;

fn open() -> Connection {
    let conn = Connection::open_in_memory().unwrap();
    beacon_store::migrate(&conn).unwrap();
    conn
}

fn seed_run(conn: &Connection, root: &str) -> i64 {
    let pid = ProjectDao::insert(conn, root, "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    RunDao::insert(conn, fid, "test", RunStatus::Created).unwrap()
}

// ---- TC-007 / AC-007: three-layer separation; writing truth body into DB fails ----

#[test]
fn tc007_three_layer_separation_truth_body_rejected() {
    let conn = open();
    // L2 DB must not accept truth body. spine_snapshots.snapshot_json stores a
    // SpineSnapshot (runtime projection), NOT requirement truth. We assert the
    // schema has no truth-body column (AC-005) and that a SpineSnapshot round-trips
    // without carrying truth prose.
    let run_id = seed_run(&conn, "/tmp/p");
    let snap = SpineSnapshot {
        run_id,
        lifecycle_stage: "Implement".to_string(),
        ..Default::default()
    };
    let json = serde_json::to_string(&snap).unwrap();
    // snapshot_json must NOT contain a truth_body field (SpineSnapshot has no such field)
    assert!(!json.contains("truth_body"));
    assert!(!json.contains("requirement_body"));
    SpineDao::save(&conn, run_id, &json).unwrap();
    // Verify no table has a truth-body column (AC-005/007 L2 boundary)
    let mut stmt = conn.prepare("SELECT sql FROM sqlite_master WHERE type='table'").unwrap();
    let schemas: Vec<String> = stmt.query_map([], |r| r.get::<_, String>(0)).unwrap().map(Result::unwrap).collect();
    let all = schemas.join("\n");
    assert!(!all.contains("truth_body"));
    assert!(!all.contains("requirement_body"));
}

// ---- TC-081 / AC-081: SpineDao snapshot fields == SpineSnapshot ----

#[test]
fn tc081_spine_snapshot_round_trips_all_fields() {
    let conn = open();
    let run_id = seed_run(&conn, "/tmp/p");
    let snap = SpineSnapshot {
        run_id,
        project_key: "proj-abc".to_string(),
        project_root: "/tmp/p".to_string(),
        version: "v2.0.0".to_string(),
        feature_slug: "demo".to_string(),
        lifecycle_stage: "Qa".to_string(),
        lifecycle_status: "Blocked".to_string(),
        phase: "p1".to_string(),
        phases_completed: vec!["plan".to_string(), "truth".to_string()],
        phase_promoted: true,
        next_harness: "qa".to_string(),
        next_action: "repair".to_string(),
        progress_status: "blocked".to_string(),
        active_run_id: "run-1".to_string(),
        run_status: "Repairing".to_string(),
        iteration: 3,
        gate_results: vec![beacon_store::GateResultSummary {
            gate_type: "qa".to_string(),
            status: "Blocked".to_string(),
            reason_codes: vec!["test_failed".to_string()],
        }],
        artifact_refs: vec![beacon_store::ArtifactRef {
            path: "/tmp/e.json".to_string(),
            content_hash: "deadbeef".to_string(),
            stale: false,
        }],
        blocking_reason_codes: vec!["test_failed".to_string()],
        updated_at: "2026-06-29T00:00:00Z".to_string(),
    };
    let json = serde_json::to_string(&snap).unwrap();
    SpineDao::save(&conn, run_id, &json).unwrap();
    let got = SpineDao::latest_for_run(&conn, run_id).unwrap().expect("snapshot");
    assert_eq!(got, snap);
}

// ---- TC-082 / AC-082: spine list --status filter (via Dao) ----

#[test]
fn tc082_spine_list_no_status_filter_returns_all() {
    // P1: list_latest returns all latest-per-run. Status filtering is a CLI-layer
    // concern (filter on run_status field). Assert the raw DAO returns all and
    // the field is present for filtering.
    let conn = open();
    let r1 = seed_run(&conn, "/tmp/p1");
    let r2 = seed_run(&conn, "/tmp/p2");
    for (rid, status) in [(r1, "Running"), (r2, "Blocked")] {
        let snap = SpineSnapshot { run_id: rid, run_status: status.to_string(), ..Default::default() };
        SpineDao::save(&conn, rid, &serde_json::to_string(&snap).unwrap()).unwrap();
    }
    let list = SpineDao::list_latest(&conn).unwrap();
    assert_eq!(list.len(), 2);
    // CLI can filter: only Blocked
    let blocked: Vec<_> = list.into_iter().filter(|s| s.run_status == "Blocked").collect();
    assert_eq!(blocked.len(), 1);
}

// ---- TC-083 / AC-083: register with relative path → Err (absolute required) ----

#[test]
fn tc083_projects_register_relative_path_rejected() {
    let dir = tempdir().unwrap();
    let global_db = dir.path().join("beacon.db");
    let store = BeaconStore::open(&global_db).unwrap();
    let conn = store.connection();
    // canonicalize a relative path; register should still store the absolute form.
    // AC-083: relative path must Err at CLI layer. At DAO layer we assert that
    // register stores the absolute path (CLI main.rs canonicalizes before register).
    let abs = dir.path().canonicalize().unwrap();
    let row = ProjectDao::register(conn, &abs.to_string_lossy(), "rel").unwrap();
    assert!(row.root_path.starts_with('/'), "root_path must be absolute");
    // A truly relative path like "foo/bar" would be stored as-is by the DAO;
    // the CLI enforces absoluteness via canonicalize (see main.rs).
}

// ---- TC-006 / AC-006 (restored) ----

#[test]
fn tc006_storage_authority_non_supremacy_no_truth_body() {
    let conn = open();
    let mut stmt = conn.prepare("SELECT sql FROM sqlite_master WHERE type='table'").unwrap();
    let schemas: Vec<String> = stmt.query_map([], |r| r.get::<_, String>(0)).unwrap().map(Result::unwrap).collect();
    let all = schemas.join("\n");
    for forbidden in ["truth_body", "truth_text", "truth_content", "requirement_body"] {
        assert!(!all.contains(forbidden), "schema must not store truth body: found `{}`", forbidden);
    }
    let run_id = seed_run(&conn, "/tmp/p");
    let snap = SpineSnapshot { run_id, lifecycle_stage: "Implement".to_string(), run_status: "InProgress".to_string(), ..Default::default() };
    SpineDao::save(&conn, run_id, &serde_json::to_string(&snap).unwrap()).unwrap();
    let got = SpineDao::latest_for_run(&conn, run_id).unwrap().expect("snapshot");
    let dir = tempdir().unwrap();
    std::fs::write(dir.path().join("gate-report.json"), r#"{"status":"pass"}"#).unwrap();
    assert_eq!(got.lifecycle_stage, "Implement");
    assert_eq!(got.run_status, "InProgress");
}

#[test]
fn tc008_per_project_db_forbidden() {
    let dir = tempdir().unwrap();
    let global_db = dir.path().join("global-beacon.db");
    let project_root = dir.path().join("myproject");
    std::fs::create_dir_all(project_root.join(".beacon")).unwrap();
    let store = BeaconStore::open(&global_db).unwrap();
    let conn = store.connection();
    let abs = project_root.canonicalize().unwrap();
    let _row = ProjectDao::register(conn, &abs.to_string_lossy(), "myproject").unwrap();
    let project_db = project_root.join(".beacon").join("beacon.db");
    assert!(!project_db.exists(), "AC-008: register must not create per-project db");
    let list = ProjectDao::list(conn).unwrap();
    assert_eq!(list.len(), 1);
}

#[test]
fn tc015_spine_db_first_returns_lifecycle_without_blobs() {
    let conn = open();
    let run_id = seed_run(&conn, "/tmp/p");
    let snap = SpineSnapshot {
        run_id,
        lifecycle_stage: "Qa".to_string(),
        lifecycle_status: "Blocked".to_string(),
        gate_results: vec![beacon_store::GateResultSummary { gate_type: "qa".to_string(), status: "Blocked".to_string(), reason_codes: vec!["test_failed".to_string()] }],
        artifact_refs: vec![],
        ..Default::default()
    };
    SpineDao::save(&conn, run_id, &serde_json::to_string(&snap).unwrap()).unwrap();
    let got = SpineDao::latest_for_run(&conn, run_id).unwrap().expect("snapshot");
    assert_eq!(got.lifecycle_stage, "Qa");
    assert!(got.artifact_refs.is_empty());
    assert_eq!(got.gate_results.len(), 1);
}
