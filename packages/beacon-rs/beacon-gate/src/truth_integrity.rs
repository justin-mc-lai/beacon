//! Truth Integrity Gate (TIG) for freeze/refreeze (AC-101 / AC-103 / W3).
//! Aligns with v1.6 build_truth_integrity_gate semantics without PyO3.

use serde::{Deserialize, Serialize};

pub const REASON_TIG_EMPTY_AC: &str = "truth_integrity_empty_ac";
pub const REASON_TIG_SOFT_TC: &str = "truth_integrity_soft_tc_only";
pub const REASON_TIG_UNAPPROVED_DEFERRAL: &str = "truth_integrity_unapproved_deferral";
pub const REASON_TIG_FAKE_DELIVERY: &str = "truth_integrity_fake_delivery";
pub const REASON_TIG_PACKAGE_INVALID: &str = "truth_integrity_package_invalid";
pub const REASON_TIG_PASS: &str = "truth_integrity_pass";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TigMode {
    /// Hard block freeze/refreeze when integrity fails.
    Block,
    /// Frozen historical packages: report findings without blocking.
    AuditOnly,
}

impl TigMode {
    pub fn parse(s: &str) -> Self {
        match s.trim().to_ascii_lowercase().as_str() {
            "audit" | "audit_only" | "audit-only" => TigMode::AuditOnly,
            _ => TigMode::Block,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TruthIntegrityInput {
    /// Package status: draft|frozen|in_progress|...
    pub status: String,
    pub has_acceptance_criteria: bool,
    /// Only soft/contract tests, no behavior/integration TC.
    pub soft_tc_only: bool,
    pub unapproved_deferral: bool,
    pub fake_delivery_claim: bool,
    pub package_valid: bool,
    /// Number of AC rows (optional count).
    pub ac_count: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TruthIntegrityGateResult {
    pub blocked: bool,
    pub status: String,
    pub mode: String,
    pub reason_codes: Vec<String>,
    pub repair_route: String,
    pub findings: Vec<String>,
    pub schema: String,
}

/// Evaluate TIG. Frozen + AuditOnly → never hard-block historical freezes (AC-LOOM-W3-001).
pub fn evaluate_truth_integrity(input: &TruthIntegrityInput, mode: TigMode) -> TruthIntegrityGateResult {
    let mut findings = Vec::new();
    let mut codes = Vec::new();

    if !input.has_acceptance_criteria || input.ac_count == 0 {
        findings.push("missing_acceptance_criteria".into());
        codes.push(REASON_TIG_EMPTY_AC.into());
    }
    if input.soft_tc_only {
        findings.push("soft_tc_only_no_behavior".into());
        codes.push(REASON_TIG_SOFT_TC.into());
    }
    if input.unapproved_deferral {
        findings.push("unapproved_deferral".into());
        codes.push(REASON_TIG_UNAPPROVED_DEFERRAL.into());
    }
    if input.fake_delivery_claim {
        findings.push("fake_delivery_closure".into());
        codes.push(REASON_TIG_FAKE_DELIVERY.into());
    }
    if !input.package_valid {
        findings.push("feature_package_invalid".into());
        codes.push(REASON_TIG_PACKAGE_INVALID.into());
    }

    let is_frozen = matches!(
        input.status.trim().to_ascii_lowercase().as_str(),
        "frozen" | "freeze" | "released"
    );

    // Already-frozen historical: audit_only does not block (even in Block mode when status frozen? UD: 已 frozen 历史默认 audit_only)
    let effective_mode = if is_frozen && mode == TigMode::AuditOnly {
        TigMode::AuditOnly
    } else if is_frozen && codes.is_empty() {
        mode
    } else if is_frozen {
        // Default frozen packages to audit-only unless explicitly re-freezing draft
        TigMode::AuditOnly
    } else {
        mode
    };

    let hard = !codes.is_empty() && matches!(effective_mode, TigMode::Block);
    let repair = if codes.is_empty() {
        String::new()
    } else {
        format!(
            "repair_route: fill AC (≥1), add behavior TC, approve deferrals, fix package validity; codes={}",
            codes.join(",")
        )
    };

    TruthIntegrityGateResult {
        blocked: hard,
        status: if hard {
            "blocked".into()
        } else if codes.is_empty() {
            "pass".into()
        } else {
            "audit".into()
        },
        mode: match effective_mode {
            TigMode::Block => "block".into(),
            TigMode::AuditOnly => "audit_only".into(),
        },
        reason_codes: if codes.is_empty() {
            vec![REASON_TIG_PASS.into()]
        } else {
            codes
        },
        repair_route: repair,
        findings,
        schema: "truth-integrity-gate.v1".into(),
    }
}

/// Doctor CLI exit: 0 pass/audit, 2 blocked (align v1.6).
pub fn doctor_exit_code(result: &TruthIntegrityGateResult) -> i32 {
    if result.blocked {
        2
    } else {
        0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn base() -> TruthIntegrityInput {
        TruthIntegrityInput {
            status: "draft".into(),
            has_acceptance_criteria: true,
            soft_tc_only: false,
            unapproved_deferral: false,
            fake_delivery_claim: false,
            package_valid: true,
            ac_count: 2,
        }
    }

    #[test]
    fn tc101_tig_blocks_empty_ac() {
        let mut i = base();
        i.has_acceptance_criteria = false;
        i.ac_count = 0;
        let r = evaluate_truth_integrity(&i, TigMode::Block);
        assert!(r.blocked);
        assert!(r.reason_codes.iter().any(|c| c == REASON_TIG_EMPTY_AC));
        assert!(!r.repair_route.is_empty());
        assert_eq!(doctor_exit_code(&r), 2);
    }

    #[test]
    fn frozen_audit_only_no_hard_block() {
        let mut i = base();
        i.status = "frozen".into();
        i.has_acceptance_criteria = false;
        i.ac_count = 0;
        let r = evaluate_truth_integrity(&i, TigMode::AuditOnly);
        assert!(!r.blocked);
        assert_eq!(doctor_exit_code(&r), 0);
    }

    #[test]
    fn pass_clean_draft() {
        let r = evaluate_truth_integrity(&base(), TigMode::Block);
        assert!(!r.blocked);
        assert_eq!(r.status, "pass");
    }
}
