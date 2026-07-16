use rusqlite::{params, Connection, OptionalExtension};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProjectVersionRow {
    pub id: i64,
    pub project_id: i64,
    pub version: String,
    pub docs_root: Option<String>,
    pub is_current: bool,
}

pub struct ProjectVersionDao;

impl ProjectVersionDao {
    /// AC-068 ensure a project_versions row; returns id.
    pub fn ensure(
        conn: &Connection,
        project_id: i64,
        version: &str,
        docs_root: Option<&str>,
        is_current: bool,
    ) -> rusqlite::Result<i64> {
        if let Some(existing) = Self::get(conn, project_id, version)? {
            return Ok(existing.id);
        }
        conn.execute(
            "INSERT INTO project_versions (project_id, version, docs_root, is_current)
             VALUES (?1, ?2, ?3, ?4)",
            params![project_id, version, docs_root, if is_current { 1 } else { 0 }],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn get(
        conn: &Connection,
        project_id: i64,
        version: &str,
    ) -> rusqlite::Result<Option<ProjectVersionRow>> {
        conn.query_row(
            "SELECT id, project_id, version, docs_root, is_current
             FROM project_versions WHERE project_id = ?1 AND version = ?2",
            params![project_id, version],
            |row| {
                Ok(ProjectVersionRow {
                    id: row.get(0)?,
                    project_id: row.get(1)?,
                    version: row.get(2)?,
                    docs_root: row.get(3)?,
                    is_current: row.get::<_, i64>(4)? != 0,
                })
            },
        )
        .optional()
    }

    pub fn list_for_project(conn: &Connection, project_id: i64) -> rusqlite::Result<Vec<ProjectVersionRow>> {
        let mut stmt = conn.prepare(
            "SELECT id, project_id, version, docs_root, is_current
             FROM project_versions WHERE project_id = ?1 ORDER BY version",
        )?;
        let rows = stmt.query_map([project_id], |row| {
            Ok(ProjectVersionRow {
                id: row.get(0)?,
                project_id: row.get(1)?,
                version: row.get(2)?,
                docs_root: row.get(3)?,
                is_current: row.get::<_, i64>(4)? != 0,
            })
        })?;
        rows.collect()
    }

    pub fn set_current(conn: &Connection, project_id: i64, version: &str) -> rusqlite::Result<()> {
        conn.execute(
            "UPDATE project_versions SET is_current = 0 WHERE project_id = ?1",
            [project_id],
        )?;
        conn.execute(
            "UPDATE project_versions SET is_current = 1 WHERE project_id = ?1 AND version = ?2",
            params![project_id, version],
        )?;
        Ok(())
    }
}
