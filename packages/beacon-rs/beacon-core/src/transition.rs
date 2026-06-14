use crate::error::{ReasonCode, TransitionError};
use crate::stage::{BlockedStatus, SkippedStatus, StageStatus};
use crate::workflow::WorkflowStage;

/// Explicit workflow stage transition table. AC-027
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WorkflowTransition {
    Forward,
    Retry,
    Back,
}

pub fn validate_workflow_transition(
    from: WorkflowStage,
    to: WorkflowStage,
) -> Result<WorkflowTransition, TransitionError> {
    use WorkflowStage::*;
    use WorkflowTransition::*;

    if from == to {
        return Ok(Retry);
    }

    let allowed = match (from, to) {
        (Think, UserStory) | (UserStory, Prd) | (Prd, TestCase) => Forward,
        (TestCase, Prototype) | (TestCase, Implement) => Forward,
        (Prototype, Implement) => Forward,
        (Implement, Qa) => Forward,
        (Qa, Release) => Forward,
        (Release, Archive) => Forward,
        (Freeze, Implement) => Forward,
        (TestCase, Prd) | (Prototype, TestCase) | (Implement, TestCase) | (Implement, Prototype) => {
            Back
        }
        (Qa, Implement) | (Release, Qa) | (Release, Implement) => Back,
        (Freeze, Think) | (Freeze, Prd) | (Archive, _) | (_, Think) => {
            return Err(TransitionError::IllegalWorkflowTransition {
                from: from.as_str().to_string(),
                to: to.as_str().to_string(),
            });
        }
        _ => {
            return Err(TransitionError::IllegalWorkflowTransition {
                from: from.as_str().to_string(),
                to: to.as_str().to_string(),
            });
        }
    };

    Ok(allowed)
}

/// Stage status transition guards. AC-028, AC-029
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum StageTransition {
    Blocked(BlockedStatus),
    Skipped(SkippedStatus),
    Other(StageStatus),
}

pub fn validate_stage_status(transition: &StageTransition) -> Result<(), TransitionError> {
    match transition {
        StageTransition::Blocked(blocked) => {
            if blocked.reason_codes.is_empty() {
                return Err(TransitionError::MissingReasonCodes);
            }
            Ok(())
        }
        StageTransition::Skipped(skipped) => {
            if skipped.user_accepted_deferral_id.trim().is_empty() {
                return Err(TransitionError::MissingDeferralId);
            }
            Ok(())
        }
        StageTransition::Other(status) => {
            if matches!(
                status,
                StageStatus::Crashed | StageStatus::TimedOut | StageStatus::Interrupted
            ) {
                // AC-030: caller must persist lifecycle_events — validated at store layer.
            }
            Ok(())
        }
    }
}

pub fn transition_reason_code(err: &TransitionError) -> ReasonCode {
    err.reason_code()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::workflow::WorkflowStage;

    #[test]
    fn freeze_to_think_is_illegal() {
        let err = validate_workflow_transition(WorkflowStage::Freeze, WorkflowStage::Think)
            .unwrap_err();
        assert_eq!(
            err.reason_code(),
            ReasonCode::IllegalStageTransition
        );
    }

    #[test]
    fn blocked_requires_reason_codes() {
        let err = validate_stage_status(&StageTransition::Blocked(BlockedStatus {
            reason_codes: vec![],
            blocking_gate: None,
        }))
        .unwrap_err();
        assert_eq!(err, TransitionError::MissingReasonCodes);
    }

    #[test]
    fn skipped_requires_deferral_id() {
        let err = validate_stage_status(&StageTransition::Skipped(SkippedStatus {
            user_accepted_deferral_id: String::new(),
        }))
        .unwrap_err();
        assert_eq!(err, TransitionError::MissingDeferralId);
    }
}
