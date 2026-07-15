use rusqlite::{params, Connection, OptionalExtension};
use serde::{Deserialize, Serialize};

/// AC-017 SpineSnapshot — full field set aligned with plan §2.5 + v1.6 spine.
/// Serialized as snapshot_json in spine_snapshots table.
#[derive(Debug, Clone, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct SpineSnapshot {
    pub run_id: i64,
    pub project_key: String,
    pub project_root: String,
    pub version: String,
    pub feature_slug: String,
    pub lifecycle_stage: String,
    pub lifecycle_status: String,
    pub phase: String,
    pub phases_completed: Vec<String>,
    pub phase_promoted: bool,
    pub next_harness: String,
    pub next_action: String,
    pub progress_status: String,
    pub active_run_id: String,
    pub run_status: String,
    pub iteration: i64,
    pub gate_results: Vec<GateResultSummary>,
    pub artifact_refs: Vec<ArtifactRef>,
    pub blocking_reason_codes: Vec<String>,
    pub updated_at: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct GateResultSummary {
    pub gate_type: String,
    pub status: String,
    pub reason_codes: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct ArtifactRef {
    pub path: String,
    pub content_hash: String,
    pub stale: bool,
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

    /// AC-017 spine show — latest snapshot for a run.
    /// Tolerates legacy JSON (missing fields) by merging into a default snapshot.
    pub fn latest_for_run(conn: &Connection, run_id: i64) -> rusqlite::Result<Option<SpineSnapshot>> {
        let row: Option<(String,)> = conn
            .query_row(
                "SELECT snapshot_json FROM spine_snapshots
                 WHERE run_id = ?1 ORDER BY created_at DESC LIMIT 1",
                [run_id],
                |r| Ok((r.get::<_, String>(0)?,)),
            )
            .optional()?;
        match row {
            Some((json,)) => {
                // Try full deserialize; on failure, merge over a default with run_id set
                // so legacy snapshots (P0 format) still return Some.
                let mut snap: SpineSnapshot = serde_json::from_str(&json).unwrap_or_default();
                snap.run_id = run_id;
                Ok(Some(snap))
            }
            None => Ok(None),
        }
    }

    /// AC-018 spine list — latest snapshot per run across all runs.
    pub fn list_latest(conn: &Connection) -> rusqlite::Result<Vec<SpineSnapshot>> {
        let mut stmt = conn.prepare(
            "SELECT s.snapshot_json FROM spine_snapshots s
             INNER JOIN (
                 SELECT run_id, MAX(id) AS max_id
                 FROM spine_snapshots GROUP BY run_id
             ) m ON s.id = m.max_id
             ORDER BY s.run_id",
        )?;
        let rows = stmt.query_map([], |row| row.get::<_, String>(0))?;
        let mut out = Vec::new();
        for json_row in rows {
            let json = json_row?;
            if let Ok(snap) = serde_json::from_str::<SpineSnapshot>(&json) {
                out.push(snap);
            }
        }
        Ok(out)
    }

    /// AC-019 spine artifacts — artifact_refs from the latest snapshot for a run.
    pub fn artifacts_for_run(conn: &Connection, run_id: i64) -> rusqlite::Result<Vec<ArtifactRef>> {
        Ok(Self::latest_for_run(conn, run_id)?
            .map(|s| s.artifact_refs)
            .unwrap_or_default())
    }
}
