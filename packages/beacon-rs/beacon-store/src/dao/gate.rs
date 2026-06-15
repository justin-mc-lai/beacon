use rusqlite::{params, Connection};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GateRow {
    pub id: i64,
    pub feature_package_id: i64,
    pub gate_name: String,
    pub verdict: String,
}

pub struct GateDao;

impl GateDao {
    pub fn insert(
        conn: &Connection,
        feature_package_id: i64,
        gate_name: &str,
        verdict: &str,
        reason_codes_json: Option<&str>,
    ) -> rusqlite::Result<i64> {
        conn.execute(
            "INSERT INTO gate_results (feature_package_id, gate_name, verdict, reason_codes_json)
             VALUES (?1, ?2, ?3, ?4)",
            params![feature_package_id, gate_name, verdict, reason_codes_json],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn latest_for_gate(
        conn: &Connection,
        feature_package_id: i64,
        gate_name: &str,
    ) -> rusqlite::Result<Option<GateRow>> {
        let mut stmt = conn.prepare(
            "SELECT id, feature_package_id, gate_name, verdict
             FROM gate_results
             WHERE feature_package_id = ?1 AND gate_name = ?2
             ORDER BY evaluated_at DESC LIMIT 1",
        )?;
        let mut rows = stmt.query(params![feature_package_id, gate_name])?;
        if let Some(row) = rows.next()? {
            Ok(Some(GateRow {
                id: row.get(0)?,
                feature_package_id: row.get(1)?,
                gate_name: row.get(2)?,
                verdict: row.get(3)?,
            }))
        } else {
            Ok(None)
        }
    }
}
