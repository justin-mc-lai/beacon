//! Cross-track evidence contamination + adversarial_review.v1 (AC-166 / AC-167 / W4a).

use beacon_core::dual_track::Track;
use serde::{Deserialize, Serialize};

pub const REASON_CROSS_TRACK_EVIDENCE: &str = "cross_track_evidence_contamination";
pub const REASON_ADVERSARIAL_MISSING: &str = "adversarial_review_missing";
pub const REASON_ADVERSARIAL_INSUFFICIENT: &str = "adversarial_review_insufficient";
pub const REASON_SKILL_SCORE_NOT_ADVERSARIAL: &str = "skill_score_cannot_replace_adversarial";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceRef {
    pub path: String,
    pub track: String,
    pub kind: String, // scorecard | gate_results | qa | adversarial
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FailurePoint {
    pub id: String,
    pub summary: String,
    pub evidence_refs: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AdversarialReview {
    pub schema: String,
    pub failure_points: Vec<FailurePoint>,
    pub evidence_refs: Vec<String>,
    pub reviewer: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReleaseGateInput {
    pub claim_track: String,
    pub evidence: Vec<EvidenceRef>,
    pub adversarial: Option<AdversarialReview>,
    /// If true, caller tried to use skill-score as adversarial substitute.
    pub skill_score_as_adversarial: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReleaseGateResult {
    pub blocked: bool,
    pub status: String,
    pub reason_codes: Vec<String>,
    pub schema: String,
}

pub fn evaluate_release_gate(input: &ReleaseGateInput) -> ReleaseGateResult {
    let mut codes = Vec::new();
    let claim = Track::parse(&input.claim_track);

    // AC-166: evidence from other track cannot alone close this track's release
    if let Some(claim_t) = claim {
        for e in &input.evidence {
            if let Some(et) = Track::parse(&e.track) {
                if et != claim_t {
                    // contamination if foreign evidence is used for release decision kinds
                    if matches!(e.kind.as_str(), "scorecard" | "gate_results" | "qa" | "release") {
                        codes.push(REASON_CROSS_TRACK_EVIDENCE.into());
                        break;
                    }
                }
            }
        }
    }

    if input.skill_score_as_adversarial {
        codes.push(REASON_SKILL_SCORE_NOT_ADVERSARIAL.into());
    }

    // AC-167: adversarial_review.v1 required
    match &input.adversarial {
        None => codes.push(REASON_ADVERSARIAL_MISSING.into()),
        Some(adv) => {
            if adv.schema != "adversarial_review.v1" {
                codes.push(REASON_ADVERSARIAL_MISSING.into());
            } else if adv.failure_points.len() < 3 {
                codes.push(REASON_ADVERSARIAL_INSUFFICIENT.into());
            } else {
                let all_have_ev = adv.failure_points.iter().all(|fp| !fp.evidence_refs.is_empty());
                if !all_have_ev || adv.evidence_refs.is_empty() {
                    codes.push(REASON_ADVERSARIAL_INSUFFICIENT.into());
                }
            }
        }
    }

    codes.sort();
    codes.dedup();
    let blocked = !codes.is_empty();
    ReleaseGateResult {
        blocked,
        status: if blocked { "blocked".into() } else { "pass".into() },
        reason_codes: codes,
        schema: "release-adversarial-gate.v1".into(),
    }
}

pub fn sample_valid_adversarial() -> AdversarialReview {
    AdversarialReview {
        schema: "adversarial_review.v1".into(),
        failure_points: vec![
            FailurePoint {
                id: "fp-1".into(),
                summary: "cross-track scorecard misuse".into(),
                evidence_refs: vec!["ev/fp1".into()],
            },
            FailurePoint {
                id: "fp-2".into(),
                summary: "missing human release confirm".into(),
                evidence_refs: vec!["ev/fp2".into()],
            },
            FailurePoint {
                id: "fp-3".into(),
                summary: "incomplete gate_results on claim track".into(),
                evidence_refs: vec!["ev/fp3".into()],
            },
        ],
        evidence_refs: vec!["ev/fp1".into(), "ev/fp2".into(), "ev/fp3".into()],
        reviewer: "human".into(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tc166_contamination() {
        let r = evaluate_release_gate(&ReleaseGateInput {
            claim_track: "v2".into(),
            evidence: vec![EvidenceRef {
                path: "docs/beacon/v1.6.7/.beacon/qa/scorecard.json".into(),
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
                path: "docs/beacon/v2.0.0/qa/scorecard.json".into(),
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
    fn legal_clean() {
        let r = evaluate_release_gate(&ReleaseGateInput {
            claim_track: "v2".into(),
            evidence: vec![EvidenceRef {
                path: "docs/beacon/v2.0.0/qa/scorecard.json".into(),
                track: "v2".into(),
                kind: "scorecard".into(),
            }],
            adversarial: Some(sample_valid_adversarial()),
            skill_score_as_adversarial: false,
        });
        assert!(!r.blocked, "{:?}", r);
    }
}
