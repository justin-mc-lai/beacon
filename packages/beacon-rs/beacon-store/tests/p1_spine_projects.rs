//! P1 acceptance tests — AC-017/018/021/085 (Spine API + projects registry).
//! TC-017/018/021/085.

use beacon_core::RunStatus;
use beacon_store::{BeaconStore, FeatureDao, ProjectDao, RunDao, SpineDao, SpineSnapshot};
use rusqlite::Connection;

fn open() -> Connection {
    let conn = Connection::open_in_memory().unwrap();
    beacon_store::migrate(&conn).unwrap();
    conn
}

/// Insert project + feature + run, return the run_id (spine_snapshots FK → runs.id).
fn seed_run(conn: &Connection, root: &str, slug: &str, version: &str) -> i64 {
    let project_id = ProjectDao::insert(conn, root, "p").unwrap();
    let feature_id = FeatureDao::insert(conn, project_id, slug, version, "draft", None).unwrap();
    RunDao::insert(conn, feature_id, "test", RunStatus::Created).unwrap()
}

fn sample_snapshot(run_id: i64) -> SpineSnapshot {
    SpineSnapshot {
        run_id,
        project_key: "proj-deadbeef".to_string(),
        project_root: "/tmp/p".to_string(),
        version: "v2.0.0".to_string(),
        feature_slug: "demo".to_string(),
        lifecycle_stage: "Implement".to_string(),
        lifecycle_status: "InProgress".to_string(),
        phase: "p1".to_string(),
        next_action: "implement".to_string(),
        run_status: "InProgress".to_string(),
        iteration: 1,
        updated_at: "2026-06-29T00:00:00Z".to_string(),
        ..Default::default()
    }
}

// ---- AC-017 spine show ----

#[test]
fn tc017_spine_show_returns_latest_snapshot() {
    let conn = open();
    let run_id = seed_run(&conn, "/tmp/p", "demo", "v2.0.0");
    let snap = sample_snapshot(run_id);
    let json = serde_json::to_string(&snap).unwrap();
    SpineDao::save(&conn, run_id, &json).unwrap();
    let got = SpineDao::latest_for_run(&conn, run_id).unwrap().expect("snapshot missing");
    assert_eq!(got.run_id, run_id);
    assert_eq!(got.lifecycle_stage, "Implement");
    assert_eq!(got.feature_slug, "demo");
}

#[test]
fn tc017_spine_show_none_for_unknown_run() {
    let conn = open();
    assert!(SpineDao::latest_for_run(&conn, 999).unwrap().is_none());
}

// ---- AC-018 spine list ----

#[test]
fn tc018_spine_list_latest_per_run() {
    let conn = open();
    // two runs, two snapshots each
    let r1 = seed_run(&conn, "/tmp/p1", "demo", "v2.0.0");
    let r2 = seed_run(&conn, "/tmp/p2", "demo", "v2.0.0");
    for run_id in [r1, r2] {
        for _ in 0..2 {
            let snap = sample_snapshot(run_id);
            SpineDao::save(&conn, run_id, &serde_json::to_string(&snap).unwrap()).unwrap();
        }
    }
    let list = SpineDao::list_latest(&conn).unwrap();
    // 2 runs -> 2 latest snapshots (one per run)
    assert_eq!(list.len(), 2);
    assert!(list.iter().any(|s| s.run_id == r1));
    assert!(list.iter().any(|s| s.run_id == r2));
}

// ---- AC-019 spine artifacts ----

#[test]
fn tc019_spine_artifacts_returns_refs() {
    let conn = open();
    let run_id = seed_run(&conn, "/tmp/p", "demo", "v2.0.0");
    let mut snap = sample_snapshot(run_id);
    snap.artifact_refs = vec![beacon_store::ArtifactRef {
        path: "/tmp/a.json".to_string(),
        content_hash: "abc".to_string(),
        stale: false,
    }];
    SpineDao::save(&conn, run_id, &serde_json::to_string(&snap).unwrap()).unwrap();
    let arts = SpineDao::artifacts_for_run(&conn, run_id).unwrap();
    assert_eq!(arts.len(), 1);
    assert_eq!(arts[0].path, "/tmp/a.json");
}

// ---- AC-021 projects register/list/show ----

#[test]
fn tc021_projects_register_idempotent() {
    let conn = open();
    let r1 = ProjectDao::register(&conn, "/tmp/proj-a", "proj-a").unwrap();
    let r2 = ProjectDao::register(&conn, "/tmp/proj-a", "proj-a").unwrap();
    assert_eq!(r1.id, r2.id, "re-register must be idempotent");
    assert!(!r1.project_key.is_empty());
    assert_eq!(r1.project_key, r2.project_key);
}

#[test]
fn tc021_projects_list() {
    let conn = open();
    ProjectDao::register(&conn, "/tmp/a", "a").unwrap();
    ProjectDao::register(&conn, "/tmp/b", "b").unwrap();
    let list = ProjectDao::list(&conn).unwrap();
    assert_eq!(list.len(), 2);
}

#[test]
fn tc021_projects_show_with_versions_and_is_current() {
    let conn = open();
    let row = ProjectDao::register(&conn, "/tmp/proj-x", "x").unwrap();
    // insert project_versions + feature_package (AC-068 primary path)
    conn.execute(
        "INSERT INTO project_versions (project_id, version, is_current) VALUES (?1, ?2, 1)",
        rusqlite::params![row.id, "v2.0.0"],
    )
    .unwrap();
    conn.execute(
        "INSERT INTO feature_packages (project_id, slug, version, status) VALUES (?1, ?2, ?3, ?4)",
        rusqlite::params![row.id, "demo", "v2.0.0", "draft"],
    )
    .unwrap();
    let show = ProjectDao::show(&conn, "/tmp/proj-x", "/tmp/proj-x")
        .unwrap()
        .expect("show missing");
    assert_eq!(show.project_key, row.project_key);
    assert!(show.versions.contains(&"v2.0.0".to_string()));
    assert!(show.is_current);
}

// ---- AC-085 P1 exit: spine + projects end-to-end via BeaconStore ----

#[test]
fn tc085_p1_exit_spine_and_projects_via_store() {
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    // register
    let row = ProjectDao::register(conn, "/tmp/exit", "exit").unwrap();
    assert!(!row.project_key.is_empty());
    // spine show empty for a run that has no snapshot
    let run_id = seed_run(conn, "/tmp/exit-r", "demo", "v2.0.0");
    assert!(SpineDao::latest_for_run(conn, run_id).unwrap().is_none());
    // save + show
    let snap = sample_snapshot(run_id);
    SpineDao::save(conn, run_id, &serde_json::to_string(&snap).unwrap()).unwrap();
    let got = SpineDao::latest_for_run(conn, run_id).unwrap().expect("snapshot");
    assert_eq!(got.run_id, run_id);
}
