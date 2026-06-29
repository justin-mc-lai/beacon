/// Schema v1 — nine tables. AC-067..AC-075
pub const SCHEMA_V1: &str = r#"
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT NOT NULL UNIQUE,
    root_path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    registered_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS feature_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    revision_id TEXT,
    baseline_hash TEXT,
    truth_path TEXT,
    UNIQUE(project_id, slug, version)
);

CREATE TABLE IF NOT EXISTS feature_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_package_id INTEGER NOT NULL UNIQUE REFERENCES feature_packages(id) ON DELETE CASCADE,
    current_stage TEXT NOT NULL DEFAULT 'Think',
    stage_status TEXT NOT NULL DEFAULT 'NotStarted',
    stage_payload_json TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    runner TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Created' CHECK(status IN (
        'Created','Resolving','Running','Paused','Stopping','Stopped',
        'Succeeded','Failed','Repairing','Importing','AwaitingQa','Closed'
    )),
    started_at TEXT,
    finished_at TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS gate_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    gate_name TEXT NOT NULL,
    verdict TEXT NOT NULL,
    reason_codes_json TEXT,
    evaluated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES runs(id) ON DELETE SET NULL,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    path TEXT NOT NULL,
    content_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lifecycle_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES runs(id) ON DELETE SET NULL,
    feature_package_id INTEGER NOT NULL REFERENCES feature_packages(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

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
