#[test]
fn archive_only_marker() {
    assert!(beacon_python::ARCHIVE_ONLY);
    assert_eq!(
        beacon_python::ARCHIVE_REASON,
        "v2_core_no_pyo3_runtime_fallback"
    );
}
