//! Beacon v2 global SQLite store — single authority at `~/.beacon/beacon.db`.

pub mod dao;
pub mod migration;
pub mod pool;
pub mod schema;
pub mod writer_lease;

pub use dao::{
    ArtifactDao, ArtifactRef, CheckpointDao, CheckpointRow, FeatureDao, FeatureRow, GateDao,
    GateResultSummary, LifecycleEventDao, ProjectDao, ProjectRow, ProjectShow, ProjectVersionDao,
    ProjectVersionRow, RunDao, SpineDao, SpineSnapshot,
};
pub use migration::{backup_before_migrate, migrate, MigrationError, SCHEMA_VERSION};
pub use pool::{BeaconStore, StoreError};
pub use schema::{assert_schema_contract, REQUIRED_TRUTH_TABLES};
pub use writer_lease::{
    acquire_lease, assert_can_write, ensure_writer_leases_table, lease_holder,
    normalize_track, release_lease, WriterLeaseError, TRACK_V1, TRACK_V2,
    V2_WRITE_NAMESPACES,
};
