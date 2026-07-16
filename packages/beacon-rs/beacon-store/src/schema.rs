//! Schema contract for global `~/.beacon/beacon.db`.
//!
//! AC-067..AC-075 define the nine requirement/runtime tables.
//! `spine_snapshots` and `schema_meta` are projection/meta tables (not counted
//! against the nine-table contract). AC-161 requires explicit closure of the
//! nine-table set — no silent drift.

/// Required tables from truth AC-067..AC-075 (nine-table contract).
pub const REQUIRED_TRUTH_TABLES: &[&str] = &[
    "projects",          // AC-067
    "project_versions",  // AC-068
    "feature_packages",  // AC-069
    "feature_lifecycle", // AC-070
    "runs",              // AC-071
    "lifecycle_events",  // AC-072
    "gate_results",      // AC-073
    "artifact_refs",     // AC-074
    "checkpoints",       // AC-075
];

/// Fresh-install schema (user_version >= 2). AC-067..075 + spine projection.
pub const SCHEMA_V2: &str = r#"
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT NOT NULL UNIQUE,
    root_path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    registered_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS project_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    docs_root TEXT,
    is_current INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(project_id, version)
);

CREATE TABLE IF NOT EXISTS feature_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    project_version_id INTEGER REFERENCES project_versions(id) ON DELETE SET NULL,
    slug TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    revision_id TEXT,
    baseline_hash TEXT,
    truth_path TEXT,
    tests_path TEXT,
    UNIQUE(project_id, slug, version)
);

CREATE TABLE IF NOT EXISTS feature_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_package_id INTEGER NOT NULL UNIQUE REFERENCES feature_packages(id) ON DELETE CASCADE,
    current_stage TEXT NOT NULL DEFAULT 'Think',
    stage_status TEXT NOT NULL DEFAULT 'NotStarted',
    stage_payload_json TEXT,
    reason_codes_json TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    runner TEXT NOT NULL,
    run_kind TEXT,
    status TEXT NOT NULL DEFAULT 'Created' CHECK(status IN (
        'Created','Resolving','Running','Paused','Stopping','Stopped',
        'Succeeded','Failed','Repairing','Importing','AwaitingQa','Closed'
    )),
    iteration INTEGER NOT NULL DEFAULT 0,
    started_at TEXT,
    finished_at TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS lifecycle_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES runs(id) ON DELETE SET NULL,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS gate_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    gate_name TEXT NOT NULL,
    verdict TEXT NOT NULL,
    reason_codes_json TEXT,
    evaluated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS artifact_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES runs(id) ON DELETE SET NULL,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    abs_path TEXT NOT NULL,
    content_hash TEXT,
    size_bytes INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    iteration INTEGER NOT NULL DEFAULT 0,
    state_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Projection / meta (not part of the nine-table contract)
CREATE TABLE IF NOT EXISTS spine_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    snapshot_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"#;

/// Incremental migration from SCHEMA_V1 (user_version=1) → V2.
pub const SCHEMA_V1_TO_V2: &str = r#"
CREATE TABLE IF NOT EXISTS project_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    docs_root TEXT,
    is_current INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(project_id, version)
);

CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    iteration INTEGER NOT NULL DEFAULT 0,
    state_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS artifact_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES runs(id) ON DELETE SET NULL,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    abs_path TEXT NOT NULL,
    content_hash TEXT,
    size_bytes INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Backfill project_versions from distinct feature_packages.version when present
-- (artifact backfill is done in migration.rs only if legacy `artifacts` table exists).
INSERT OR IGNORE INTO project_versions (project_id, version, is_current)
SELECT DISTINCT project_id, version, 0 FROM feature_packages
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='feature_packages');
"#;

/// Legacy V1 bootstrap kept only for mid-migration path documentation.
pub const SCHEMA_V1: &str = SCHEMA_V2;

pub const RUN_STATUS_CHECK_VALUES: &[&str] = &[
    "Created",
    "Resolving",
    "Running",
    "Paused",
    "Stopping",
    "Stopped",
    "Succeeded",
    "Failed",
    "Repairing",
    "Importing",
    "AwaitingQa",
    "Closed",
];

/// AC-161 / TC-161: assert nine-table contract is present.
pub fn assert_schema_contract(conn: &rusqlite::Connection) -> Result<(), String> {
    for table in REQUIRED_TRUTH_TABLES {
        let exists: bool = conn
            .query_row(
                "SELECT COUNT(*) > 0 FROM sqlite_master WHERE type='table' AND name=?1",
                [*table],
                |row| row.get(0),
            )
            .map_err(|e| e.to_string())?;
        if !exists {
            return Err(format!(
                "schema_contract_drift: missing required table `{table}`"
            ));
        }
    }
    Ok(())
}
