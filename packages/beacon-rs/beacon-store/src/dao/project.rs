use rusqlite::{params, Connection, OptionalExtension};
use serde::{Deserialize, Serialize};

/// AC-021 ProjectRow — machine-level multi-project registry row.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProjectRow {
    pub id: i64,
    pub project_key: String,
    pub root_path: String,
    pub name: String,
    pub registered_at: String,
}

/// AC-021 ProjectShow — the show payload with versions[] and is_current.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProjectShow {
    pub project_key: String,
    pub root_path: String,
    pub name: String,
    pub versions: Vec<String>,
    pub is_current: bool,
}

pub struct ProjectDao;

impl ProjectDao {
    /// Legacy insert (returns id) — kept for existing tests/internal use.
    pub fn insert(conn: &Connection, root_path: &str, name: &str) -> rusqlite::Result<i64> {
        let project_key = derive_project_key(root_path);
        conn.execute(
            "INSERT INTO projects (project_key, root_path, name) VALUES (?1, ?2, ?3)",
            params![project_key, root_path, name],
        )?;
        Ok(conn.last_insert_rowid())
    }

    /// AC-021 register — insert if absent, return the row. project_key is derived
    /// from root_path (stable hash) so re-registering is idempotent.
    pub fn register(conn: &Connection, root_path: &str, name: &str) -> rusqlite::Result<ProjectRow> {
        // idempotent: if root_path exists, return existing
        if let Some(existing) = Self::get_by_root(conn, root_path)? {
            return Ok(existing);
        }
        Self::insert(conn, root_path, name)?;
        Self::get_by_root(conn, root_path)?.ok_or(rusqlite::Error::QueryReturnedNoRows)
    }

    pub fn get_by_root(conn: &Connection, root_path: &str) -> rusqlite::Result<Option<ProjectRow>> {
        conn.query_row(
            "SELECT id, project_key, root_path, name, registered_at FROM projects WHERE root_path = ?1",
            [root_path],
            |row| {
                Ok(ProjectRow {
                    id: row.get(0)?,
                    project_key: row.get(1)?,
                    root_path: row.get(2)?,
                    name: row.get(3)?,
                    registered_at: row.get(4)?,
                })
            },
        )
        .optional()
    }

    pub fn get_by_key(conn: &Connection, project_key: &str) -> rusqlite::Result<Option<ProjectRow>> {
        conn.query_row(
            "SELECT id, project_key, root_path, name, registered_at FROM projects WHERE project_key = ?1",
            [project_key],
            |row| {
                Ok(ProjectRow {
                    id: row.get(0)?,
                    project_key: row.get(1)?,
                    root_path: row.get(2)?,
                    name: row.get(3)?,
                    registered_at: row.get(4)?,
                })
            },
        )
        .optional()
    }

    pub fn list(conn: &Connection) -> rusqlite::Result<Vec<ProjectRow>> {
        let mut stmt = conn.prepare(
            "SELECT id, project_key, root_path, name, registered_at FROM projects ORDER BY id",
        )?;
        let rows = stmt.query_map([], |row| {
            Ok(ProjectRow {
                id: row.get(0)?,
                project_key: row.get(1)?,
                root_path: row.get(2)?,
                name: row.get(3)?,
                registered_at: row.get(4)?,
            })
        })?;
        rows.collect::<Result<Vec<_>, _>>()
    }

    /// AC-021 show — project with versions[] (from feature_packages) and is_current
    /// (true if root_path matches the given current_root).
    pub fn show(conn: &Connection, root_path: &str, current_root: &str) -> rusqlite::Result<Option<ProjectShow>> {
        let row = Self::get_by_root(conn, root_path)?;
        match row {
            Some(p) => {
                let versions = Self::versions_for(conn, p.id)?;
                let is_current = p.root_path == current_root;
                Ok(Some(ProjectShow {
                    project_key: p.project_key,
                    root_path: p.root_path,
                    name: p.name,
                    versions,
                    is_current,
                }))
            }
            None => Ok(None),
        }
    }

    fn versions_for(conn: &Connection, project_id: i64) -> rusqlite::Result<Vec<String>> {
        // Prefer project_versions (AC-068); fall back to feature_packages for legacy rows.
        let mut stmt = conn.prepare(
            "SELECT version FROM project_versions WHERE project_id = ?1 ORDER BY version",
        )?;
        let rows = stmt.query_map([project_id], |row| row.get::<_, String>(0))?;
        let mut versions = rows.collect::<Result<Vec<_>, _>>()?;
        if versions.is_empty() {
            let mut stmt = conn.prepare(
                "SELECT DISTINCT version FROM feature_packages WHERE project_id = ?1 ORDER BY version",
            )?;
            let rows = stmt.query_map([project_id], |row| row.get::<_, String>(0))?;
            versions = rows.collect::<Result<Vec<_>, _>>()?;
        }
        Ok(versions)
    }
}

/// Derive a stable project_key from root_path (AC-021 machine-level key).
/// Uses a simple FNV-1a-ish hash formatted as hex; not cryptographic — only
/// needs to be stable and unique per distinct root_path.
fn derive_project_key(root_path: &str) -> String {
    let mut hash: u64 = 0xcbf29ce484222325;
    for byte in root_path.as_bytes() {
        hash ^= *byte as u64;
        hash = hash.wrapping_mul(0x100000001b3);
    }
    format!("proj-{:016x}", hash)
}
