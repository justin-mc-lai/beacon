use rusqlite::{params, Connection};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ArtifactRow {
    pub id: i64,
    pub feature_package_id: i64,
    pub kind: String,
    pub path: String,
}

pub struct ArtifactDao;

impl ArtifactDao {
    pub fn insert(
        conn: &Connection,
        feature_package_id: i64,
        run_id: Option<i64>,
        kind: &str,
        path: &str,
        content_hash: Option<&str>,
    ) -> rusqlite::Result<i64> {
        conn.execute(
            "INSERT INTO artifacts (feature_package_id, run_id, kind, path, content_hash)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            params![feature_package_id, run_id, kind, path, content_hash],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn list_for_feature(
        conn: &Connection,
        feature_package_id: i64,
    ) -> rusqlite::Result<Vec<ArtifactRow>> {
        let mut stmt = conn.prepare(
            "SELECT id, feature_package_id, kind, path FROM artifacts WHERE feature_package_id = ?1",
        )?;
        let rows = stmt
            .query_map([feature_package_id], |row| {
                Ok(ArtifactRow {
                    id: row.get(0)?,
                    feature_package_id: row.get(1)?,
                    kind: row.get(2)?,
                    path: row.get(3)?,
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;
        Ok(rows)
    }
}
