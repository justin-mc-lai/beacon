//! Beacon v2 global SQLite store — single authority at `~/.beacon/beacon.db`.

pub mod dao;
pub mod migration;
pub mod pool;
pub mod schema;

pub use dao::{
    ArtifactDao, ArtifactRef, FeatureDao, GateDao, GateResultSummary, ProjectDao, ProjectRow,
    ProjectShow, RunDao, SpineDao, SpineSnapshot,
};
pub use migration::{backup_before_migrate, migrate, MigrationError, SCHEMA_VERSION};
pub use pool::{BeaconStore, StoreError};
