//! TC-067..TC-076, TC-031, TC-084 — store layer acceptance tests.

use beacon_core::RunStatus;
use beacon_store::{
    migration::{backup_before_migrate, current_user_version, migrate, SCHEMA_VERSION},
    schema::RUN_STATUS_CHECK_VALUES,
    ArtifactDao, BeaconStore, FeatureDao, GateDao, ProjectDao, RunDao, SpineDao,
};
use rusqlite::Connection;
use tempfile::tempdir;

#[test]
fn tc031_run_status_check_constraint_has_twelve_values() {
    assert_eq!(RunStatus::all().len(), 12);
    assert_eq!(RUN_STATUS_CHECK_VALUES.len(), 12);
    for status in RunStatus::all() {
        assert!(RUN_STATUS_CHECK_VALUES.contains(&status.as_str()));
    }
}

#[test]
fn tc031_invalid_run_status_rejected_by_db() {
    let conn = Connection::open_in_memory().unwrap();
    migrate(&conn).unwrap();
    let project_id = ProjectDao::insert(&conn, "/tmp/p", "p").unwrap();
    let feature_id = FeatureDao::insert(&conn, project_id, "f", "v1", "draft", None).unwrap();
    let err = conn.execute(
        "INSERT INTO runs (feature_package_id, runner, status) VALUES (?1, ?2, ?3)",
        rusqlite::params![feature_id, "test", "NotARealStatus"],
    );
    assert!(err.is_err());
}

#[test]
fn tc067_through_tc076_dao_crud_roundtrip() {
    let mut store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection_mut();

    let project_id = ProjectDao::insert(conn, "/proj/beacon", "beacon").unwrap();
    assert!(ProjectDao::get_by_root(conn, "/proj/beacon").unwrap().is_some());

    let feature_id =
        FeatureDao::insert(conn, project_id, "beacon-v2", "v2.0.0", "frozen", Some("truth.md"))
            .unwrap();
    FeatureDao::update_stage(conn, feature_id, "Implement", "InProgress", None).unwrap();

    let run_id = RunDao::insert(conn, feature_id, "codex", RunStatus::Running).unwrap();
    RunDao::update_status(conn, run_id, RunStatus::Succeeded).unwrap();
    assert_eq!(
        RunDao::get(conn, run_id).unwrap().unwrap().status,
        "Succeeded"
    );

    GateDao::insert(conn, feature_id, "qa", "pass", Some("[]")).unwrap();
    assert!(GateDao::latest_for_gate(conn, feature_id, "qa")
        .unwrap()
        .is_some());

    ArtifactDao::insert(conn, feature_id, Some(run_id), "evidence", "/tmp/e.json", None).unwrap();
    assert_eq!(ArtifactDao::list_for_feature(conn, feature_id).unwrap().len(), 1);

    SpineDao::save(conn, run_id, r#"{"stages":[]}"#).unwrap();
    assert!(SpineDao::latest_for_run(conn, run_id).unwrap().is_some());
}

#[test]
fn tc075_migration_skeleton_user_version_and_backup() {
    let dir = tempdir().unwrap();
    let db_path = dir.path().join("beacon.db");
    {
        let conn = Connection::open(&db_path).unwrap();
        migrate(&conn).unwrap();
    }
    let backup = backup_before_migrate(&db_path).unwrap();
    assert!(backup.is_some());
    let conn = Connection::open(&db_path).unwrap();
    assert_eq!(current_user_version(&conn).unwrap(), SCHEMA_VERSION);
}

#[test]
fn tc084_p0_workspace_smoke() {
    assert_eq!(RunStatus::all().len(), 12);
    let _store = BeaconStore::open_in_memory().unwrap();
}

#[test]
fn tc161_schema_contract_nine_tables_present() {
    // AC-161 / TC-161: migrate must materialize all nine truth tables.
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    beacon_store::assert_schema_contract(conn).expect("schema_contract_drift");
    for table in beacon_store::REQUIRED_TRUTH_TABLES {
        let n: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?1",
                [*table],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(n, 1, "missing table {table}");
    }
    assert_eq!(current_user_version(conn).unwrap(), SCHEMA_VERSION);
    assert_eq!(SCHEMA_VERSION, 2);
}

#[test]
fn tc075_checkpoints_write_and_read() {
    // AC-075 checkpoints table behavioral write.
    use beacon_store::CheckpointDao;
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let project_id = ProjectDao::insert(conn, "/tmp/cp", "cp").unwrap();
    let feature_id = FeatureDao::insert(conn, project_id, "f", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, feature_id, "test", RunStatus::Running).unwrap();
    let cp_id = CheckpointDao::insert(conn, run_id, 3, r#"{"i":3}"#).unwrap();
    assert!(cp_id > 0);
    let latest = CheckpointDao::latest_for_run(conn, run_id).unwrap().expect("checkpoint");
    assert_eq!(latest.iteration, 3);
    assert!(latest.state_json.contains("\"i\":3"));
}

#[test]
fn tc068_project_versions_ensured_on_feature_insert() {
    use beacon_store::ProjectVersionDao;
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let project_id = ProjectDao::insert(conn, "/tmp/pv", "pv").unwrap();
    FeatureDao::insert(conn, project_id, "slug", "v2.0.0", "draft", None).unwrap();
    let versions = ProjectVersionDao::list_for_project(conn, project_id).unwrap();
    assert!(versions.iter().any(|v| v.version == "v2.0.0"));
    let show = ProjectDao::show(conn, "/tmp/pv", "/tmp/pv")
        .unwrap()
        .expect("show");
    assert!(show.versions.contains(&"v2.0.0".to_string()));
}
