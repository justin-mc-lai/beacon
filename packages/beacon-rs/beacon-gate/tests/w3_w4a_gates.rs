//! W3 TIG + W4a release adversarial gates.

use beacon_gate::{
    doctor_exit_code, evaluate_release_gate, evaluate_truth_integrity, sample_valid_adversarial,
    AdversarialReview, EvidenceRef, FailurePoint, ReleaseGateInput, TigMode, TruthIntegrityInput,
    REASON_ADVERSARIAL_MISSING, REASON_CROSS_TRACK_EVIDENCE, REASON_TIG_EMPTY_AC,
};

#[test]
fn tc101_tig_blocks_empty_ac() {
    let r = evaluate_truth_integrity(
        &TruthIntegrityInput {
            status: "draft".into(),
            has_acceptance_criteria: false,
            soft_tc_only: false,
            unapproved_deferral: false,
            fake_delivery_claim: false,
            package_valid: true,
            ac_count: 0,
        },
        TigMode::Block,
    );
    assert!(r.blocked);
    assert!(r.reason_codes.iter().any(|c| c == REASON_TIG_EMPTY_AC));
    assert!(!r.repair_route.is_empty());
    assert_eq!(doctor_exit_code(&r), 2);
}

#[test]
fn tc103_doctor_exit_audit_frozen() {
    let r = evaluate_truth_integrity(
        &TruthIntegrityInput {
            status: "frozen".into(),
            has_acceptance_criteria: false,
            soft_tc_only: true,
            unapproved_deferral: false,
            fake_delivery_claim: false,
            package_valid: true,
            ac_count: 0,
        },
        TigMode::AuditOnly,
    );
    assert!(!r.blocked);
    assert_eq!(doctor_exit_code(&r), 0);
}

#[test]
fn tc166_contamination() {
    let r = evaluate_release_gate(&ReleaseGateInput {
        claim_track: "v2".into(),
        evidence: vec![EvidenceRef {
            path: "v1-scorecard.json".into(),
            track: "v1".into(),
            kind: "scorecard".into(),
        }],
        adversarial: Some(sample_valid_adversarial()),
        skill_score_as_adversarial: false,
    });
    assert!(r.blocked);
    assert!(r.reason_codes.iter().any(|c| c == REASON_CROSS_TRACK_EVIDENCE));
}

#[test]
fn tc167_missing_adversarial() {
    let r = evaluate_release_gate(&ReleaseGateInput {
        claim_track: "v2".into(),
        evidence: vec![EvidenceRef {
            path: "v2-score.json".into(),
            track: "v2".into(),
            kind: "scorecard".into(),
        }],
        adversarial: None,
        skill_score_as_adversarial: false,
    });
    assert!(r.blocked);
    assert!(r.reason_codes.iter().any(|c| c == REASON_ADVERSARIAL_MISSING));
}

#[test]
fn tc167_insufficient_points() {
    let r = evaluate_release_gate(&ReleaseGateInput {
        claim_track: "v2".into(),
        evidence: vec![],
        adversarial: Some(AdversarialReview {
            schema: "adversarial_review.v1".into(),
            failure_points: vec![FailurePoint {
                id: "1".into(),
                summary: "only one".into(),
                evidence_refs: vec!["e".into()],
            }],
            evidence_refs: vec!["e".into()],
            reviewer: "x".into(),
        }),
        skill_score_as_adversarial: false,
    });
    assert!(r.blocked);
}
