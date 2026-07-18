//! Empty/drift refreeze guards (AC-137).

use serde::{Deserialize, Serialize};

pub const REASON_EMPTY_REFREEZE: &str = "empty_refreeze_reason_only";
pub const REASON_REVISION_DRIFT: &str = "revision_authority_drift";
pub const REASON_MACHINE_ONLY: &str = "empty_refreeze_machine_only";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RefreezeRequest {
    pub change_reason: String,
    pub human_narrative: String,
    pub machine_revision_bump: bool,
    pub machine_revision: String,
    pub human_revision: String,
    pub truth_body_changed: bool,
}

pub fn validate_refreeze(req: &RefreezeRequest) -> Result<(), String> {
    // reason-only without truth body change
    if !req.truth_body_changed
        && !req.change_reason.trim().is_empty()
        && req.human_narrative.trim().is_empty()
        && !req.machine_revision_bump
    {
        return Err(REASON_EMPTY_REFREEZE.into());
    }
    // machine-only bump
    if req.machine_revision_bump && !req.truth_body_changed && req.human_narrative.trim().is_empty()
    {
        return Err(REASON_MACHINE_ONLY.into());
    }
    // revision narrative drift
    if !req.machine_revision.is_empty()
        && !req.human_revision.is_empty()
        && req.machine_revision != req.human_revision
    {
        return Err(REASON_REVISION_DRIFT.into());
    }
    if req.truth_body_changed && req.change_reason.trim().is_empty() {
        return Err(REASON_EMPTY_REFREEZE.into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reason_only_blocked() {
        let r = RefreezeRequest {
            change_reason: "because".into(),
            human_narrative: "".into(),
            machine_revision_bump: false,
            machine_revision: "".into(),
            human_revision: "".into(),
            truth_body_changed: false,
        };
        assert_eq!(validate_refreeze(&r).unwrap_err(), REASON_EMPTY_REFREEZE);
    }

    #[test]
    fn drift_blocked() {
        let r = RefreezeRequest {
            change_reason: "ok".into(),
            human_narrative: "did work".into(),
            machine_revision_bump: true,
            machine_revision: "R10".into(),
            human_revision: "R9".into(),
            truth_body_changed: true,
        };
        assert_eq!(validate_refreeze(&r).unwrap_err(), REASON_REVISION_DRIFT);
    }

    #[test]
    fn good_refreeze() {
        let r = RefreezeRequest {
            change_reason: "add gate".into(),
            human_narrative: "added gate".into(),
            machine_revision_bump: true,
            machine_revision: "R11".into(),
            human_revision: "R11".into(),
            truth_body_changed: true,
        };
        assert!(validate_refreeze(&r).is_ok());
    }
}
