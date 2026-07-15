use rusqlite::{params, Connection, OptionalExtension};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FeatureRow {
    pub id: i64,
    pub project_id: i64,
    pub slug: String,
    pub version: String,
    pub status: String,
}

pub struct FeatureDao;

impl FeatureDao {
    pub fn insert(
        conn: &Connection,
        project_id: i64,
        slug: &str,
        version: &str,
        status: &str,
        truth_path: Option<&str>,
    ) -> rusqlite::Result<i64> {
        conn.execute(
            "INSERT INTO feature_packages (project_id, slug, version, status, truth_path)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            params![project_id, slug, version, status, truth_path],
        )?;
        let feature_id = conn.last_insert_rowid();
        conn.execute(
            "INSERT INTO feature_lifecycle (feature_package_id, current_stage, stage_status)
             VALUES (?1, 'Think', 'NotStarted')",
            [feature_id],
        )?;
        Ok(feature_id)
    }

    pub fn get(
        conn: &Connection,
        project_id: i64,
        slug: &str,
        version: &str,
    ) -> rusqlite::Result<Option<FeatureRow>> {
        conn.query_row(
            "SELECT id, project_id, slug, version, status
             FROM feature_packages
             WHERE project_id = ?1 AND slug = ?2 AND version = ?3",
            params![project_id, slug, version],
            |row| {
                Ok(FeatureRow {
                    id: row.get(0)?,
                    project_id: row.get(1)?,
                    slug: row.get(2)?,
                    version: row.get(3)?,
                    status: row.get(4)?,
                })
            },
        )
        .optional()
    }

    pub fn update_stage(
        conn: &Connection,
        feature_id: i64,
        stage: &str,
        stage_status: &str,
        payload_json: Option<&str>,
    ) -> rusqlite::Result<()> {
        conn.execute(
            "UPDATE feature_lifecycle
             SET current_stage = ?1, stage_status = ?2, stage_payload_json = ?3,
                 updated_at = datetime('now')
             WHERE feature_package_id = ?4",
            params![stage, stage_status, payload_json, feature_id],
        )?;
        Ok(())
    }

    /// Find a feature package by slug + version across all projects.
    pub fn find_by_slug_version(
        conn: &Connection,
        slug: &str,
        version: &str,
    ) -> rusqlite::Result<Option<FeatureRow>> {
        conn.query_row(
            "SELECT id, project_id, slug, version, status
             FROM feature_packages
             WHERE slug = ?1 AND version = ?2
             ORDER BY id DESC LIMIT 1",
            params![slug, version],
            |row| {
                Ok(FeatureRow {
                    id: row.get(0)?,
                    project_id: row.get(1)?,
                    slug: row.get(2)?,
                    version: row.get(3)?,
                    status: row.get(4)?,
                })
            },
        )
        .optional()
    }
}
