//! Delivery harness path: implement / qa-evidence / release with TraceSpine hard gates.

use crate::standard_flow::AdmissionBundle;
use beacon_core::branch_context::BranchContext;
use beacon_core::trace_spine::{TraceContext, TraceSpine};
use beacon_gate::harness_trace_gate::{evaluate_harness_trace_gate, HarnessGateResult};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HarnessPathBlocked {
    pub phase: String,
    pub reason_code: String,
    pub gate: HarnessGateResult,
}

/// Controller that refuses to enter implement/qa/release without TraceSpine + admission.
pub struct HarnessPathController {
    pub spine: Option<TraceSpine>,
    pub branch: Option<BranchContext>,
    pub admission: AdmissionBundle,
}

impl HarnessPathController {
    pub fn new() -> Self {
        Self {
            spine: None,
            branch: None,
            admission: AdmissionBundle::empty(),
        }
    }

    pub fn start_loop(
        &mut self,
        run_id: &str,
        branch: BranchContext,
        decision_packet_ref: &str,
        intent_snapshot_ref: &str,
        truth_hash: &str,
        design_primitives_ref: &str,
    ) -> Result<&TraceSpine, String> {
        branch.governance_gate(None)?;
        let ctx = TraceContext::new(run_id).with_bindings(
            format!("branch_context:{run_id}"),
            decision_packet_ref,
            intent_snapshot_ref,
            truth_hash,
            design_primitives_ref,
        );
        ctx.validate_bindings()?;
        let mut spine = TraceSpine::create(run_id, ctx);
        spine.append("decision", "loop_start", format!("run:{run_id}/loop_start"))?;
        self.branch = Some(branch);
        self.spine = Some(spine);
        Ok(self.spine.as_ref().unwrap())
    }

    pub fn append_iteration(&mut self, summary: &str, evidence_ref: &str) -> Result<(), String> {
        let spine = self
            .spine
            .as_mut()
            .ok_or_else(|| "trace_spine_missing".to_string())?;
        spine.append("output", summary, evidence_ref)?;
        Ok(())
    }

    pub fn enter_phase(&self, phase: &str) -> Result<(), HarnessPathBlocked> {
        if phase == "implement" {
            if let Err(code) = self.admission.implement_admission_gate() {
                let gate = evaluate_harness_trace_gate(
                    phase,
                    self.spine.as_ref(),
                    self.branch.as_ref(),
                    false,
                );
                return Err(HarnessPathBlocked {
                    phase: phase.into(),
                    reason_code: code,
                    gate,
                });
            }
        }
        let gate =
            evaluate_harness_trace_gate(phase, self.spine.as_ref(), self.branch.as_ref(), false);
        if gate.blocked {
            return Err(HarnessPathBlocked {
                phase: phase.into(),
                reason_code: gate.reason_code.clone(),
                gate,
            });
        }
        Ok(())
    }
}

impl Default for HarnessPathController {
    fn default() -> Self {
        Self::new()
    }
}
