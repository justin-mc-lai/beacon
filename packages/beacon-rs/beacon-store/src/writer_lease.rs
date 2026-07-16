//! Dual-track writer lease (AC-158 / AC-093 / AC-150).
//!
//! Global `~/.beacon/beacon.db` is shared machine state. Writes must declare a
//! track (`track_v1` | `track_v2`). Only one track may hold a namespace lease at
//! a time. Cross-track **read** is always allowed. Detected second writer →
//! `dual_track_writer_conflict`.

use rusqlite::{params, Connection, OptionalExtension};
use thiserror::Error;

pub const TRACK_V1: &str = "track_v1";
pub const TRACK_V2: &str = "track_v2";

/// Default write namespaces owned by the v2 runtime path.
pub const V2_WRITE_NAMESPACES: &[&str] = &[
    "runs",
    "feature_lifecycle",
    "gate_results",
    "lifecycle_events",
    "artifact_refs",
    "checkpoints",
    "spine_snapshots",
    "feature_packages",
    "project_versions",
    "projects",
];

#[derive(Debug, Error, PartialEq, Eq)]
pub enum WriterLeaseError {
    #[error("dual_track_writer_conflict: namespace `{namespace}` held by `{holder}`, requested by `{requester}`")]
    DualTrackConflict {
        namespace: String,
        holder: String,
        requester: String,
    },
    #[error("runtime_track_unspecified: write requires explicit track_v1|track_v2")]
    TrackUnspecified,
    #[error("sqlite: {0}")]
    Sqlite(String),
}

impl From<rusqlite::Error> for WriterLeaseError {
    fn from(e: rusqlite::Error) -> Self {
        WriterLeaseError::Sqlite(e.to_string())
    }
}

pub fn ensure_writer_leases_table(conn: &Connection) -> Result<(), WriterLeaseError> {
    conn.execute_batch(
        r#"
CREATE TABLE IF NOT EXISTS writer_leases (
    namespace TEXT PRIMARY KEY,
    track TEXT NOT NULL,
    holder_id TEXT,
    acquired_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT
);
"#,
    )?;
    Ok(())
}

pub fn normalize_track(track: &str) -> Result<&str, WriterLeaseError> {
    match track.trim() {
        TRACK_V1 | "v1" => Ok(TRACK_V1),
        TRACK_V2 | "v2" => Ok(TRACK_V2),
        "" => Err(WriterLeaseError::TrackUnspecified),
        other if other.starts_with("track_") => Ok(other),
        _ => Err(WriterLeaseError::TrackUnspecified),
    }
}

pub fn acquire_lease(
    conn: &Connection,
    track: &str,
    namespace: &str,
    holder_id: Option<&str>,
) -> Result<(), WriterLeaseError> {
    ensure_writer_leases_table(conn)?;
    let track = normalize_track(track)?;
    let existing: Option<String> = conn
        .query_row(
            "SELECT track FROM writer_leases WHERE namespace = ?1",
            [namespace],
            |row| row.get(0),
        )
        .optional()?;
    if let Some(holder) = existing {
        if holder != track {
            return Err(WriterLeaseError::DualTrackConflict {
                namespace: namespace.to_string(),
                holder,
                requester: track.to_string(),
            });
        }
        conn.execute(
            "UPDATE writer_leases SET holder_id = COALESCE(?1, holder_id), acquired_at = datetime('now')
             WHERE namespace = ?2",
            params![holder_id, namespace],
        )?;
        return Ok(());
    }
    conn.execute(
        "INSERT INTO writer_leases (namespace, track, holder_id) VALUES (?1, ?2, ?3)",
        params![namespace, track, holder_id],
    )?;
    Ok(())
}

pub fn assert_can_write(
    conn: &Connection,
    track: &str,
    namespace: &str,
) -> Result<(), WriterLeaseError> {
    ensure_writer_leases_table(conn)?;
    let track = normalize_track(track)?;
    let existing: Option<String> = conn
        .query_row(
            "SELECT track FROM writer_leases WHERE namespace = ?1",
            [namespace],
            |row| row.get(0),
        )
        .optional()?;
    match existing {
        None => acquire_lease(conn, track, namespace, None),
        Some(holder) if holder == track => Ok(()),
        Some(holder) => Err(WriterLeaseError::DualTrackConflict {
            namespace: namespace.to_string(),
            holder,
            requester: track.to_string(),
        }),
    }
}

pub fn release_lease(
    conn: &Connection,
    track: &str,
    namespace: &str,
) -> Result<bool, WriterLeaseError> {
    ensure_writer_leases_table(conn)?;
    let track = normalize_track(track)?;
    let n = conn.execute(
        "DELETE FROM writer_leases WHERE namespace = ?1 AND track = ?2",
        params![namespace, track],
    )?;
    Ok(n > 0)
}

pub fn lease_holder(
    conn: &Connection,
    namespace: &str,
) -> Result<Option<String>, WriterLeaseError> {
    ensure_writer_leases_table(conn)?;
    Ok(conn
        .query_row(
            "SELECT track FROM writer_leases WHERE namespace = ?1",
            [namespace],
            |row| row.get(0),
        )
        .optional()?)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::migrate;
    use rusqlite::Connection;

    #[test]
    fn same_track_reacquire_ok() {
        let conn = Connection::open_in_memory().unwrap();
        migrate(&conn).unwrap();
        acquire_lease(&conn, TRACK_V2, "runs", Some("pid-1")).unwrap();
        acquire_lease(&conn, TRACK_V2, "runs", Some("pid-1")).unwrap();
    }

    #[test]
    fn cross_track_second_writer_conflicts() {
        let conn = Connection::open_in_memory().unwrap();
        migrate(&conn).unwrap();
        acquire_lease(&conn, TRACK_V2, "runs", None).unwrap();
        let err = acquire_lease(&conn, TRACK_V1, "runs", None).unwrap_err();
        assert!(matches!(err, WriterLeaseError::DualTrackConflict { .. }));
        assert!(err.to_string().contains("dual_track_writer_conflict"));
    }

    #[test]
    fn read_holder_allows_cross_track_observe() {
        let conn = Connection::open_in_memory().unwrap();
        migrate(&conn).unwrap();
        acquire_lease(&conn, TRACK_V2, "gate_results", None).unwrap();
        let h = lease_holder(&conn, "gate_results").unwrap();
        assert_eq!(h.as_deref(), Some(TRACK_V2));
    }

    #[test]
    fn unspecified_track_fails() {
        let conn = Connection::open_in_memory().unwrap();
        migrate(&conn).unwrap();
        let err = acquire_lease(&conn, "", "runs", None).unwrap_err();
        assert_eq!(err, WriterLeaseError::TrackUnspecified);
    }
}
