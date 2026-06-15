use std::path::{Path, PathBuf};

use rusqlite::Connection;
use thiserror::Error;

use crate::schema::SCHEMA_V1;

pub const SCHEMA_VERSION: i64 = 1;

#[derive(Debug, Error)]
pub enum MigrationError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    #[error("sqlite error: {0}")]
    Sqlite(#[from] rusqlite::Error),
    #[error("unsupported schema version: {0}")]
    UnsupportedVersion(i64),
}

/// P0 skeleton: copy DB before applying migrations. AC-075
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

pub fn migrate(conn: &Connection) -> Result<i64, MigrationError> {
    let current = current_user_version(conn)?;
    if current > SCHEMA_VERSION {
        return Err(MigrationError::UnsupportedVersion(current));
    }
    if current < 1 {
        conn.execute_batch(SCHEMA_V1)?;
        conn.execute(
            "INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('schema_version', ?1)",
            [SCHEMA_VERSION.to_string()],
        )?;
        conn.pragma_update(None, "user_version", SCHEMA_VERSION)?;
    }
    Ok(SCHEMA_VERSION)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;

    #[test]
    fn user_version_starts_at_one_after_migrate() {
        let conn = Connection::open_in_memory().unwrap();
        migrate(&conn).unwrap();
        assert_eq!(current_user_version(&conn).unwrap(), 1);
    }
}
