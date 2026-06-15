use thiserror::Error;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ReasonCode {
    IllegalStageTransition,
    MissingReasonCodes,
    MissingDeferralId,
    InvalidEnum,
    EvidenceChainBroken,
    StorageAuthorityViolation,
    DualWriteForbidden,
    PerProjectDbForbidden,
}

impl ReasonCode {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::IllegalStageTransition => "ILLEGAL_STAGE_TRANSITION",
            Self::MissingReasonCodes => "MISSING_REASON_CODES",
            Self::MissingDeferralId => "MISSING_DEFERRAL_ID",
            Self::InvalidEnum => "INVALID_ENUM",
            Self::EvidenceChainBroken => "EVIDENCE_CHAIN_BROKEN",
            Self::StorageAuthorityViolation => "STORAGE_AUTHORITY_VIOLATION",
            Self::DualWriteForbidden => "DUAL_WRITE_FORBIDDEN",
            Self::PerProjectDbForbidden => "PER_PROJECT_DB_FORBIDDEN",
        }
    }
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum BeaconError {
    #[error("illegal enum value for {kind}: {value}")]
    InvalidEnum { kind: &'static str, value: String },
    #[error("evidence chain broken")]
    EvidenceChainBroken,
    #[error("transition error: {0}")]
    Transition(#[from] TransitionError),
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum TransitionError {
    #[error("illegal workflow transition {from} -> {to}")]
    IllegalWorkflowTransition { from: String, to: String },
    #[error("blocked status requires reason_codes")]
    MissingReasonCodes,
    #[error("skipped status requires user_accepted_deferral_id")]
    MissingDeferralId,
}

impl TransitionError {
    pub fn reason_code(&self) -> ReasonCode {
        match self {
            Self::IllegalWorkflowTransition { .. } => ReasonCode::IllegalStageTransition,
            Self::MissingReasonCodes => ReasonCode::MissingReasonCodes,
            Self::MissingDeferralId => ReasonCode::MissingDeferralId,
        }
    }
}
