//! ARCHIVE-ONLY: PyO3 / Python runtime bindings are **not** part of v2 core closure (R8/P4).
//!
//! This crate remains in the workspace as a historical scaffold marker so CI can
//! assert it is not used as a silent v1 fallback. Do not expand public surface here.
//!
//! Active v2 crates: beacon-core, beacon-store, beacon-orchestrator, beacon-gate, beacon-cli.

#![allow(dead_code)]

/// Archive marker constant — tests may assert archive-only status.
pub const ARCHIVE_ONLY: bool = true;
pub const ARCHIVE_REASON: &str = "v2_core_no_pyo3_runtime_fallback";

#[no_mangle]
pub extern "C" fn beacon_python_archive_marker() -> u32 {
    1
}
