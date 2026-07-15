use rusqlite::{params, Connection};

/// AC-050/AC-032 lifecycle_events DAO — phase transitions write events here.
pub struct LifecycleEventDao;

impl LifecycleEventDao {
    /// Insert a lifecycle event. run_id is optional (some events are feature-scoped).
    pub fn insert(
        conn: &Connection,
        run_id: Option<i64>,
        feature_package_id: i64,
        event_type: &str,
        payload_json: Option<&str>,
    ) -> rusqlite::Result<i64> {
        conn.execute(
            "INSERT INTO lifecycle_events (run_id, feature_package_id, event_type, payload_json)
             VALUES (?1, ?2, ?3, ?4)",
            params![run_id, feature_package_id, event_type, payload_json],
        )?;
        Ok(conn.last_insert_rowid())
    }

    /// List events for a feature package, ordered by created_at.
    pub fn list_for_feature(conn: &Connection, feature_package_id: i64) -> rusqlite::Result<Vec<(i64, String, Option<String>)>> {
        let mut stmt = conn.prepare(
            "SELECT id, event_type, payload_json FROM lifecycle_events
             WHERE feature_package_id = ?1 ORDER BY created_at",
        )?;
        let rows = stmt.query_map([feature_package_id], |row| {
            Ok((row.get::<_, i64>(0)?, row.get::<_, String>(1)?, row.get::<_, Option<String>>(2)?))
        })?;
        rows.collect::<Result<Vec<_>, _>>()
    }
}
