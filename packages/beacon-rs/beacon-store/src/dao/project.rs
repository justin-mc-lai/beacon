use rusqlite::{params, Connection, OptionalExtension};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProjectRow {
    pub id: i64,
    pub root_path: String,
    pub name: String,
}

pub struct ProjectDao;

impl ProjectDao {
    pub fn insert(conn: &Connection, root_path: &str, name: &str) -> rusqlite::Result<i64> {
        conn.execute(
            "INSERT INTO projects (root_path, name) VALUES (?1, ?2)",
            params![root_path, name],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn get_by_root(conn: &Connection, root_path: &str) -> rusqlite::Result<Option<ProjectRow>> {
        conn.query_row(
            "SELECT id, root_path, name FROM projects WHERE root_path = ?1",
            [root_path],
            |row| {
                Ok(ProjectRow {
                    id: row.get(0)?,
                    root_path: row.get(1)?,
                    name: row.get(2)?,
                })
            },
        )
        .optional()
    }

    pub fn list(conn: &Connection) -> rusqlite::Result<Vec<ProjectRow>> {
        let mut stmt =
            conn.prepare("SELECT id, root_path, name FROM projects ORDER BY id")?;
        let rows = stmt
            .query_map([], |row| {
                Ok(ProjectRow {
                    id: row.get(0)?,
                    root_path: row.get(1)?,
                    name: row.get(2)?,
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;
        Ok(rows)
    }
}
