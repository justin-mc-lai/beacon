//! Beacon v2 global SQLite store — single authority at `~/.beacon/beacon.db`.

pub mod dao;
pub mod migration;
pub mod pool;
pub mod schema;

pub use dao::{
    ArtifactDao, FeatureDao, GateDao, ProjectDao, RunDao, SpineDao, SpineSnapshot,
};
pub use migration::{backup_before_migrate, migrate, MigrationError, SCHEMA_VERSION};
pub use pool::{BeaconStore, StoreError};
