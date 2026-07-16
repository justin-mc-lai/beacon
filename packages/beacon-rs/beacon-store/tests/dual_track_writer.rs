//! AC-158 / TC-158 dual-track writer lease.

use beacon_store::{
    acquire_lease, assert_can_write, lease_holder, release_lease, BeaconStore, WriterLeaseError,
    TRACK_V1, TRACK_V2,
};

#[test]
fn tc158_dual_track_writer_conflict() {
    let store_v2 = BeaconStore::open_in_memory().unwrap().with_write_track(TRACK_V2);
    store_v2.acquire_v2_write_domain(Some("v2-pid")).unwrap();

    // Simulate track_v1 trying to take the same namespace → conflict
    let conn = store_v2.connection();
    let err = acquire_lease(conn, TRACK_V1, "runs", Some("v1-pid")).unwrap_err();
    let msg = err.to_string();
    assert!(msg.contains("dual_track_writer_conflict"), "{msg}");
    match &err {
        WriterLeaseError::DualTrackConflict {
            namespace,
            holder,
            requester,
        } => {
            assert_eq!(namespace, "runs");
            assert_eq!(holder, TRACK_V2);
            assert_eq!(requester, TRACK_V1);
        }
        other => panic!("expected DualTrackConflict, got {other:?}"),
    }
}

#[test]
fn tc158_cross_track_readonly_observe_ok() {
    let store = BeaconStore::open_in_memory().unwrap().with_write_track(TRACK_V2);
    store.require_write("gate_results").unwrap();
    let holder = lease_holder(store.connection(), "gate_results")
        .unwrap()
        .expect("holder");
    assert_eq!(holder, TRACK_V2);
    // read-only observation by "v1" is just lease_holder — no write
}

#[test]
fn tc158_same_track_second_writer_reacquire_ok() {
    let store = BeaconStore::open_in_memory().unwrap().with_write_track(TRACK_V2);
    store.require_write("checkpoints").unwrap();
    store.require_write("checkpoints").unwrap();
    assert!(release_lease(store.connection(), TRACK_V2, "checkpoints").unwrap());
    // after release, other track may acquire
    acquire_lease(store.connection(), TRACK_V1, "checkpoints", None).unwrap();
}

#[test]
fn tc158_assert_can_write_auto_acquires() {
    let store = BeaconStore::open_in_memory().unwrap().with_write_track(TRACK_V2);
    assert_can_write(store.connection(), TRACK_V2, "projects").unwrap();
    assert_eq!(
        lease_holder(store.connection(), "projects").unwrap().as_deref(),
        Some(TRACK_V2)
    );
}
