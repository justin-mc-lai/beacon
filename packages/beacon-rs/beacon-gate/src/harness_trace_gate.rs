//! TraceSpine hard gates on implement / qa-evidence / release (AC-133).
//! lifecycle_events / evidence manifest alone cannot pass these gates.

use beacon_core::branch_context::BranchContext;
use beacon_core::trace_spine::{
    harness_requires_trace, TraceSpine, REASON_TRACE_MISSING,
};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HarnessGateResult {
    pub phase: String,
    pub blocked: bool,
    pub status: String,
    pub reason_code: String,
    pub release_ready_allowed: bool,
    pub findings: Vec<String>,
}

/// Evaluate TraceSpine hard gate for a harness phase.
/// `has_lifecycle_projection_only` simulates TC-N13: lifecycle without TraceSpine must fail.
pub fn evaluate_harness_trace_gate(
    phase: &str,
    spine: Option<&TraceSpine>,
    branch: Option<&BranchContext>,
    has_lifecycle_projection_only: bool,
) -> HarnessGateResult {
    let mut findings = Vec::new();
    if !harness_requires_trace(phase) {
        return HarnessGateResult {
            phase: phase.into(),
            blocked: false,
            status: "not_required".into(),
            reason_code: String::new(),
            release_ready_allowed: true,
            findings,
        };
    }

    if has_lifecycle_projection_only && spine.is_none() {
        findings.push("lifecycle_events_or_manifest_without_trace_spine".into());
        return HarnessGateResult {
            phase: phase.into(),
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_TRACE_MISSING.into(),
            release_ready_allowed: false,
            findings,
        };
    }

    let Some(spine) = spine else {
        return HarnessGateResult {
            phase: phase.into(),
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_TRACE_MISSING.into(),
            release_ready_allowed: false,
            findings: vec!["trace_spine_absent".into()],
        };
    };

    match spine.authority_gate(phase, branch) {
        Ok(()) => {
            // release still human; this gate only covers trace completeness
            let release_ready = phase != "release";
            HarnessGateResult {
                phase: phase.into(),
                blocked: false,
                status: "pass".into(),
                reason_code: String::new(),
                release_ready_allowed: release_ready,
                findings,
            }
        }
        Err(code) => HarnessGateResult {
            phase: phase.into(),
            blocked: true,
            status: "blocked".into(),
            reason_code: code,
            release_ready_allowed: false,
            findings,
        },
    }
}

/// Convenience: run gate for implement, qa-evidence, release in one shot.
pub fn evaluate_all_delivery_gates(
    spine: Option<&TraceSpine>,
    branch: Option<&BranchContext>,
) -> Vec<HarnessGateResult> {
    ["implement", "qa-evidence", "release"]
        .iter()
        .map(|p| evaluate_harness_trace_gate(p, spine, branch, false))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use beacon_core::trace_spine::TraceContext;

    #[test]
    fn missing_spine_blocks_implement() {
        let r = evaluate_harness_trace_gate("implement", None, None, false);
        assert!(r.blocked);
        assert_eq!(r.reason_code, REASON_TRACE_MISSING);
    }

    #[test]
    fn lifecycle_only_blocks_release() {
        let r = evaluate_harness_trace_gate("release", None, None, true);
        assert!(r.blocked);
    }

    #[test]
    fn complete_spine_passes_implement() {
        let ctx = TraceContext::new("r").with_bindings("bc:r", "dp", "is", "th", "des");
        let mut spine = TraceSpine::create("r", ctx);
        spine.append("decision", "start", "ev/1").unwrap();
        let bc = BranchContext::new("r", "/c", "/p", "/p", "main").mark_admitted();
        let r = evaluate_harness_trace_gate("implement", Some(&spine), Some(&bc), false);
        assert!(!r.blocked, "{:?}", r);
    }
}
