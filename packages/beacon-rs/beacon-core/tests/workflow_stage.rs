//! TC-026 — invalid workflow stage parsing fails closed.

use beacon_core::WorkflowStage;

#[test]
fn tc026_invalid_workflow_stage_fails() {
    let err = WorkflowStage::parse("NotAStage").unwrap_err();
    assert!(matches!(
        err,
        beacon_core::BeaconError::InvalidEnum { kind: "WorkflowStage", .. }
    ));
}

#[test]
fn tc026_valid_workflow_stages_roundtrip() {
    for stage in WorkflowStage::all() {
        let parsed = WorkflowStage::parse(stage.as_str()).unwrap();
        assert_eq!(parsed, *stage);
    }
}
