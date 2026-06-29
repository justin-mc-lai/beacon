use rusqlite::{params, Connection, OptionalExtension};

use beacon_core::RunStatus;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RunRow {
    pub id: i64,
    pub feature_package_id: i64,
    pub runner: String,
    pub status: String,
}

pub struct RunDao;

impl RunDao {
    pub fn insert(
        conn: &Connection,
        feature_package_id: i64,
        runner: &str,
        status: RunStatus,
    ) -> rusqlite::Result<i64> {
        conn.execute(
            "INSERT INTO runs (feature_package_id, runner, status) VALUES (?1, ?2, ?3)",
            params![feature_package_id, runner, status.as_str()],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn update_status(
        conn: &Connection,
        run_id: i64,
        status: RunStatus,
    ) -> rusqlite::Result<()> {
        conn.execute(
            "UPDATE runs SET status = ?1 WHERE id = ?2",
            params![status.as_str(), run_id],
        )?;
        Ok(())
    }

    pub fn get(conn: &Connection, run_id: i64) -> rusqlite::Result<Option<RunRow>> {
        conn.query_row(
            "SELECT id, feature_package_id, runner, status FROM runs WHERE id = ?1",
            [run_id],
            |row| {
                Ok(RunRow {
                    id: row.get(0)?,
                    feature_package_id: row.get(1)?,
                    runner: row.get(2)?,
                    status: row.get(3)?,
                })
            },
        )
        .optional()
    }

    /// AC-050 update runs.metadata_json (phase controller writes phase here).
    pub fn update_metadata(conn: &Connection, run_id: i64, metadata_json: &str) -> rusqlite::Result<()> {
        conn.execute(
            "UPDATE runs SET metadata_json = ?1 WHERE id = ?2",
            params![metadata_json, run_id],
        )?;
        Ok(())
    }

    /// AC-050 read runs.metadata_json.
    pub fn get_metadata(conn: &Connection, run_id: i64) -> rusqlite::Result<Option<String>> {
        conn.query_row(
            "SELECT metadata_json FROM runs WHERE id = ?1",
            [run_id],
            |row| Ok(row.get::<_, Option<String>>(0)?),
        )
        .optional()
        .map(|o| o.flatten())
    }
}
