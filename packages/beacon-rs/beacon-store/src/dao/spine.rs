use rusqlite::{params, Connection, OptionalExtension};

/// AC-081 spine snapshot skeleton.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct SpineSnapshot {
    pub run_id: i64,
    pub stages: Vec<String>,
    pub payload_json: String,
}

pub struct SpineDao;

impl SpineDao {
    pub fn save(conn: &Connection, run_id: i64, snapshot_json: &str) -> rusqlite::Result<i64> {
        conn.execute(
            "INSERT INTO spine_snapshots (run_id, snapshot_json) VALUES (?1, ?2)",
            params![run_id, snapshot_json],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn latest_for_run(conn: &Connection, run_id: i64) -> rusqlite::Result<Option<SpineSnapshot>> {
        conn.query_row(
            "SELECT run_id, snapshot_json FROM spine_snapshots
             WHERE run_id = ?1 ORDER BY created_at DESC LIMIT 1",
            [run_id],
            |row| {
                Ok(SpineSnapshot {
                    run_id: row.get(0)?,
                    stages: vec![],
                    payload_json: row.get(1)?,
                })
            },
        )
        .optional()
    }
}
