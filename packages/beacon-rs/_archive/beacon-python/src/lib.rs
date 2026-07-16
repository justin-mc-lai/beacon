//! Python bindings crate — P4+ PyO3 surface (library stub for P0).

pub use beacon_core::*;
pub use beacon_store::*;

#[no_mangle]
pub extern "C" fn beacon_python_version() -> u32 {
    1
}
