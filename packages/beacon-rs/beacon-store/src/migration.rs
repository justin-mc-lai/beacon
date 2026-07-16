use std::path::{Path, PathBuf};

use rusqlite::Connection;
use thiserror::Error;

use crate::schema::{assert_schema_contract, SCHEMA_V1_TO_V2, SCHEMA_V2};

/// AC-161 closed: schema version 2 implements the nine-table truth contract.
pub const SCHEMA_VERSION: i64 = 2;

#[derive(Debug, Error)]
pub enum MigrationError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    #[error("sqlite error: {0}")]
    Sqlite(#[from] rusqlite::Error),
    #[error("unsupported schema version: {0}")]
    UnsupportedVersion(i64),
    #[error("schema contract drift: {0}")]
    SchemaContract(String),
}

/// P0 skeleton: copy DB before applying migrations. AC-075 / AC-092
pub fn backup_before_migrate(db_path: &Path) -> Result<Option<PathBuf>, MigrationError> {
    if !db_path.exists() {
        return Ok(None);
    }
    let backup = db_path.with_extension("db.bak");
    std::fs::copy(db_path, &backup)?;
    Ok(Some(backup))
}

pub fn current_user_version(conn: &Connection) -> Result<i64, MigrationError> {
    let version: i64 = conn.query_row("PRAGMA user_version", [], |row| row.get(0))?;
    Ok(version)
}


fn table_exists(conn: &Connection, name: &str) -> Result<bool, MigrationError> {
    let n: i64 = conn.query_row(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?1",
        [name],
        |row| row.get(0),
    )?;
    Ok(n > 0)
}

fn backfill_from_legacy(conn: &Connection) -> Result<(), MigrationError> {
    if table_exists(conn, "artifacts")? {
        conn.execute_batch(
            r#"
INSERT INTO artifact_refs (run_id, feature_package_id, kind, abs_path, content_hash, created_at)
SELECT run_id, feature_package_id, kind, path, content_hash, created_at
FROM artifacts
WHERE NOT EXISTS (
    SELECT 1 FROM artifact_refs ar
    WHERE ar.feature_package_id = artifacts.feature_package_id
      AND ar.abs_path = artifacts.path
);
"#,
        )?;
    }
    if table_exists(conn, "feature_packages")? {
        conn.execute_batch(
            r#"
INSERT OR IGNORE INTO project_versions (project_id, version, is_current)
SELECT DISTINCT project_id, version, 0 FROM feature_packages;
"#,
        )?;
    }
    Ok(())
}

fn table_has_column(conn: &Connection, table: &str, column: &str) -> Result<bool, MigrationError> {
    let mut stmt = conn.prepare(&format!("PRAGMA table_info({table})"))?;
    let cols = stmt.query_map([], |row| row.get::<_, String>(1))?;
    for c in cols {
        if c? == column {
            return Ok(true);
        }
    }
    Ok(false)
}

fn ensure_feature_package_columns(conn: &Connection) -> Result<(), MigrationError> {
    if !table_has_column(conn, "feature_packages", "project_version_id")? {
        conn.execute(
            "ALTER TABLE feature_packages ADD COLUMN project_version_id INTEGER",
            [],
        )?;
    }
    if !table_has_column(conn, "feature_packages", "tests_path")? {
        conn.execute("ALTER TABLE feature_packages ADD COLUMN tests_path TEXT", [])?;
    }
    if !table_has_column(conn, "feature_lifecycle", "reason_codes_json")? {
        conn.execute(
            "ALTER TABLE feature_lifecycle ADD COLUMN reason_codes_json TEXT",
            [],
        )?;
    }
    if !table_has_column(conn, "runs", "run_kind")? {
        conn.execute("ALTER TABLE runs ADD COLUMN run_kind TEXT", [])?;
    }
    if !table_has_column(conn, "runs", "iteration")? {
        conn.execute(
            "ALTER TABLE runs ADD COLUMN iteration INTEGER NOT NULL DEFAULT 0",
            [],
        )?;
    }
    Ok(())
}

pub fn migrate(conn: &Connection) -> Result<i64, MigrationError> {
    let current = current_user_version(conn)?;
    if current > SCHEMA_VERSION {
        return Err(MigrationError::UnsupportedVersion(current));
    }
    if current < 1 {
        // Fresh install: full V2 schema
        conn.execute_batch(SCHEMA_V2)?;
    } else if current == 1 {
        // V1 → V2 incremental
        conn.execute_batch(SCHEMA_V1_TO_V2)?;
        ensure_feature_package_columns(conn)?;
    } else if current == 2 {
        // already at target; still ensure contract
    }

    // Always ensure columns for partially upgraded DBs and re-assert contract
    if current >= 1 {
        let _ = ensure_feature_package_columns(conn);
        // Ensure v2 tables exist even if batch was partial
        conn.execute_batch(SCHEMA_V1_TO_V2)?;
    }

    conn.execute(
        "INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('schema_version', ?1)",
        [SCHEMA_VERSION.to_string()],
    )?;
    conn.pragma_update(None, "user_version", SCHEMA_VERSION)?;

    backfill_from_legacy(conn)?;
    assert_schema_contract(conn).map_err(MigrationError::SchemaContract)?;
    Ok(SCHEMA_VERSION)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;

    #[test]
    fn user_version_is_two_after_migrate() {
        let conn = Connection::open_in_memory().unwrap();
        migrate(&conn).unwrap();
        assert_eq!(current_user_version(&conn).unwrap(), 2);
    }
}
