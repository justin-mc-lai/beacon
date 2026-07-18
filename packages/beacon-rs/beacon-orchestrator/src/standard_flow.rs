//! Beacon Standard Execution Flow state machine (AC-138..143).

use serde::{Deserialize, Serialize};

pub const REASON_FLOW_ORDER: &str = "standard_flow_order_violation";
pub const REASON_FLOW_INCOMPLETE: &str = "standard_flow_verification_incomplete";
pub const REASON_CANONICAL_NOT_COMMITTED: &str = "canonical_refreeze_not_committed";
pub const REASON_STALE_FEATURE_REFREEZE: &str = "stale_feature_local_refreeze";
pub const REASON_BASELINE_NOT_MERGED: &str = "truth_baseline_not_merged";

/// Ordered stages of the standard execution flow (AC-138).
pub const FLOW_STAGES: [&str; 8] = [
    "support_advisory",
    "canonical_truth_authoring",
    "canonical_refreeze",
    "canonical_commit",
    "feature_worktree_reconcile",
    "governance_verify",
    "workspace_admission",
    "implement_resume",
];

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowState {
    pub schema: String,
    pub completed: Vec<String>,
    pub current: String,
    pub truth_baseline_commit: String,
    pub revision: u64,
}

impl Default for FlowState {
    fn default() -> Self {
        Self {
            schema: "standard-execution-flow.v1".into(),
            completed: vec![],
            current: FLOW_STAGES[0].into(),
            truth_baseline_commit: String::new(),
            revision: 0,
        }
    }
}

impl FlowState {
    pub fn advance(&mut self, next: &str) -> Result<(), String> {
        let cur_idx = FLOW_STAGES
            .iter()
            .position(|s| *s == self.current.as_str())
            .ok_or_else(|| format!("{REASON_FLOW_ORDER}:unknown_current"))?;
        let next_idx = FLOW_STAGES
            .iter()
            .position(|s| *s == next)
            .ok_or_else(|| format!("{REASON_FLOW_ORDER}:unknown_next:{next}"))?;
        // allow stay (idempotent) or move exactly one step forward
        if next_idx == cur_idx {
            return Ok(()); // idempotent resume (AC-143)
        }
        if next_idx != cur_idx + 1 {
            return Err(format!(
                "{REASON_FLOW_ORDER}:expected {} got {next}",
                FLOW_STAGES.get(cur_idx + 1).unwrap_or(&"<end>")
            ));
        }
        if !self.completed.iter().any(|s| s == &self.current) {
            self.completed.push(self.current.clone());
        }
        self.current = next.into();
        // only bump revision on real forward (not idempotent re-entry)
        // AC-143: completed steps re-run must not bump — we don't bump on advance of already done
        Ok(())
    }

    pub fn mark_canonical_commit(&mut self, commit: impl Into<String>) {
        self.truth_baseline_commit = commit.into();
    }
}

/// Verify a claimed sequence of completed stages is a valid prefix of FLOW_STAGES.
pub fn verify_flow_order(completed: &[String], current: &str) -> Result<(), String> {
    for (i, stage) in completed.iter().enumerate() {
        if FLOW_STAGES.get(i).copied() != Some(stage.as_str()) {
            return Err(format!("{REASON_FLOW_ORDER}:at_index_{i}"));
        }
    }
    let expected_current_idx = completed.len();
    if FLOW_STAGES.get(expected_current_idx).copied() != Some(current) {
        // allow current == last completed for terminal implement_resume complete
        if !(current == "implement_resume"
            && completed.last().map(|s| s.as_str()) == Some("implement_resume"))
        {
            return Err(format!("{REASON_FLOW_ORDER}:current_mismatch:{current}"));
        }
    }
    Ok(())
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AdmissionBundle {
    pub schema: String,
    pub truth_map_verify: bool,
    pub verify_materials_strict: bool,
    pub diff_check: bool,
    pub branch_governance_verify: bool,
    pub workspace_admission: bool,
    pub truth_baseline_commit: String,
    pub baseline_merged_into_feature: bool,
    pub feature_machine_dirty: bool,
    pub feature_local_refreeze_quarantined: bool,
}

impl AdmissionBundle {
    pub fn empty() -> Self {
        Self {
            schema: "standard-flow-admission-bundle.v1".into(),
            truth_map_verify: false,
            verify_materials_strict: false,
            diff_check: false,
            branch_governance_verify: false,
            workspace_admission: false,
            truth_baseline_commit: String::new(),
            baseline_merged_into_feature: false,
            feature_machine_dirty: false,
            feature_local_refreeze_quarantined: false,
        }
    }

    /// AC-142: all verification artifacts required for implement admission.
    pub fn implement_admission_gate(&self) -> Result<(), String> {
        let checks = [
            ("truth_map_verify", self.truth_map_verify),
            ("verify_materials_strict", self.verify_materials_strict),
            ("diff_check", self.diff_check),
            ("branch_governance_verify", self.branch_governance_verify),
            ("workspace_admission", self.workspace_admission),
        ];
        for (name, ok) in checks {
            if !ok {
                return Err(format!("{REASON_FLOW_INCOMPLETE}:{name}"));
            }
        }
        if self.truth_baseline_commit.is_empty() {
            return Err(REASON_CANONICAL_NOT_COMMITTED.into());
        }
        if !self.baseline_merged_into_feature {
            return Err(REASON_BASELINE_NOT_MERGED.into());
        }
        if self.feature_machine_dirty && !self.feature_local_refreeze_quarantined {
            return Err(REASON_STALE_FEATURE_REFREEZE.into());
        }
        Ok(())
    }
}

/// Idempotent re-run of a completed step must not change revision (AC-143).
pub fn idempotent_resume(state: &mut FlowState, step: &str) -> Result<u64, String> {
    let before = state.revision;
    if state.completed.iter().any(|s| s == step) || state.current == step {
        // no revision bump
        return Ok(before);
    }
    state.advance(step)?;
    Ok(state.revision)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ordered_advance() {
        let mut s = FlowState::default();
        assert_eq!(s.current, "support_advisory");
        s.advance("canonical_truth_authoring").unwrap();
        s.advance("canonical_refreeze").unwrap();
        assert!(s.advance("workspace_admission").is_err()); // skip
    }

    #[test]
    fn skip_commit_blocked() {
        let completed = vec![
            "support_advisory".into(),
            "canonical_truth_authoring".into(),
            "canonical_refreeze".into(),
            // missing canonical_commit
        ];
        assert!(verify_flow_order(&completed, "feature_worktree_reconcile").is_err());
    }

    #[test]
    fn valid_prefix() {
        let completed = vec![
            "support_advisory".into(),
            "canonical_truth_authoring".into(),
        ];
        assert!(verify_flow_order(&completed, "canonical_refreeze").is_ok());
    }

    #[test]
    fn admission_bundle_incomplete() {
        let b = AdmissionBundle::empty();
        assert!(b.implement_admission_gate().is_err());
    }

    #[test]
    fn admission_bundle_complete() {
        let mut b = AdmissionBundle::empty();
        b.truth_map_verify = true;
        b.verify_materials_strict = true;
        b.diff_check = true;
        b.branch_governance_verify = true;
        b.workspace_admission = true;
        b.truth_baseline_commit = "abc123".into();
        b.baseline_merged_into_feature = true;
        assert!(b.implement_admission_gate().is_ok());
    }

    #[test]
    fn stale_feature_refreeze() {
        let mut b = AdmissionBundle::empty();
        b.truth_map_verify = true;
        b.verify_materials_strict = true;
        b.diff_check = true;
        b.branch_governance_verify = true;
        b.workspace_admission = true;
        b.truth_baseline_commit = "abc".into();
        b.baseline_merged_into_feature = true;
        b.feature_machine_dirty = true;
        b.feature_local_refreeze_quarantined = false;
        assert_eq!(
            b.implement_admission_gate().unwrap_err(),
            REASON_STALE_FEATURE_REFREEZE
        );
    }

    #[test]
    fn idempotent_no_revision_bump() {
        let mut s = FlowState::default();
        s.revision = 3;
        s.completed.push("support_advisory".into());
        let rev = idempotent_resume(&mut s, "support_advisory").unwrap();
        assert_eq!(rev, 3);
    }
}
