use std::path::Path;

use rusqlite::{Connection, OpenFlags};
use thiserror::Error;

use crate::migration::migrate;
use crate::writer_lease::{
    acquire_lease, assert_can_write, release_lease, WriterLeaseError, TRACK_V2, V2_WRITE_NAMESPACES,
};

#[derive(Debug, Error)]
pub enum StoreError {
    #[error("sqlite error: {0}")]
    Sqlite(#[from] rusqlite::Error),
    #[error("migration error: {0}")]
    Migration(#[from] crate::migration::MigrationError),
    #[error("writer lease: {0}")]
    WriterLease(#[from] WriterLeaseError),
}

/// Global store handle — opens `~/.beacon/beacon.db` or in-memory for tests.
pub struct BeaconStore {
    conn: Connection,
    /// Active write track for this handle (default track_v2 for Rust kernel).
    write_track: String,
}

impl BeaconStore {
    pub fn open_in_memory() -> Result<Self, StoreError> {
        let conn = Connection::open_in_memory()?;
        migrate(&conn)?;
        Ok(Self {
            conn,
            write_track: TRACK_V2.to_string(),
        })
    }

    pub fn open(path: &Path) -> Result<Self, StoreError> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| {
                StoreError::Migration(crate::migration::MigrationError::Io(e))
            })?;
        }
        let conn = Connection::open_with_flags(
            path,
            OpenFlags::SQLITE_OPEN_READ_WRITE | OpenFlags::SQLITE_OPEN_CREATE,
        )?;
        migrate(&conn)?;
        Ok(Self {
            conn,
            write_track: TRACK_V2.to_string(),
        })
    }

    /// Override write track (tests / explicit dual-track selection).
    pub fn with_write_track(mut self, track: impl Into<String>) -> Self {
        self.write_track = track.into();
        self
    }

    pub fn write_track(&self) -> &str {
        &self.write_track
    }

    pub fn connection(&self) -> &Connection {
        &self.conn
    }

    pub fn connection_mut(&mut self) -> &mut Connection {
        &mut self.conn
    }

    /// AC-158: acquire leases for all default v2 write namespaces.
    pub fn acquire_v2_write_domain(&self, holder_id: Option<&str>) -> Result<(), StoreError> {
        for ns in V2_WRITE_NAMESPACES {
            acquire_lease(&self.conn, &self.write_track, ns, holder_id)?;
        }
        Ok(())
    }

    /// AC-158: assert write allowed for namespace under this handle's track.
    pub fn require_write(&self, namespace: &str) -> Result<(), StoreError> {
        assert_can_write(&self.conn, &self.write_track, namespace)?;
        Ok(())
    }

    /// AC-158: release one namespace if held by this track.
    pub fn release_write(&self, namespace: &str) -> Result<bool, StoreError> {
        Ok(release_lease(&self.conn, &self.write_track, namespace)?)
    }
}
