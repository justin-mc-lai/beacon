use rusqlite::{params, Connection};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CheckpointRow {
    pub id: i64,
    pub run_id: i64,
    pub iteration: i64,
    pub state_json: String,
}

pub struct CheckpointDao;

impl CheckpointDao {
    /// AC-075 / AC-014 checkpoint write.
    pub fn insert(
        conn: &Connection,
        run_id: i64,
        iteration: i64,
        state_json: &str,
    ) -> rusqlite::Result<i64> {
        conn.execute(
            "INSERT INTO checkpoints (run_id, iteration, state_json) VALUES (?1, ?2, ?3)",
            params![run_id, iteration, state_json],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn latest_for_run(conn: &Connection, run_id: i64) -> rusqlite::Result<Option<CheckpointRow>> {
        use rusqlite::OptionalExtension;
        conn.query_row(
            "SELECT id, run_id, iteration, state_json FROM checkpoints
             WHERE run_id = ?1 ORDER BY id DESC LIMIT 1",
            [run_id],
            |row| {
                Ok(CheckpointRow {
                    id: row.get(0)?,
                    run_id: row.get(1)?,
                    iteration: row.get(2)?,
                    state_json: row.get(3)?,
                })
            },
        )
        .optional()
    }
}
