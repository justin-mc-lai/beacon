//! Beacon v2 core — types, state machines, agent contracts (zero IO).

pub mod agent;
pub mod branch_context;
pub mod decision_packet;
pub mod delivery;
pub mod dual_track;
pub mod error;
pub mod evidence;
pub mod harness;
pub mod harness_boundary;
pub mod lifecycle;
pub mod refreeze_guard;
pub mod stage;
pub mod stagnation;
pub mod trace_spine;
pub mod transition;
pub mod workflow;

pub use agent::{AgentBackend, IterationResult, TokenUsage};
pub use branch_context::{
    BranchContext, REASON_ADMISSION_MISSING, REASON_BRANCH_CONTEXT_MISSING,
    REASON_CANONICAL_BRANCH_MISMATCH, REASON_CWD_ROOT_MISMATCH, REASON_PROTECTED_PATH_WRITE,
    SCHEMA_BRANCH_CONTEXT,
};
pub use decision_packet::{
    DecisionPacket, IntentSnapshot, REASON_DECISION_PACKET_MISSING, REASON_INTENT_LOW_CONFIDENCE,
    REASON_INTENT_MISSING, SCHEMA_DECISION_PACKET, SCHEMA_INTENT_SNAPSHOT,
};
pub use delivery::RunStatus;
pub use dual_track::{
    admit_path_set, classify_path, early_default_v2_forbidden, forbid_cross_track_fallback,
    DualTrackAdmission, PathTrackHit, Track, REASON_CROSS_TRACK_FALLBACK, REASON_DUAL_TRACK_MIXED,
    REASON_EARLY_DEFAULT_V2,
};
pub use error::{BeaconError, ReasonCode, TransitionError};
pub use evidence::EvidenceChain;
pub use harness::{HarnessAbility, HarnessSurface, INTERNAL_DENYLIST, PUBLIC_ABILITIES};
pub use harness_boundary::{check_harness_boundary, HarnessBoundaryEvent, REASON_HARNESS_CROSS};
pub use lifecycle::LifecycleEventType;
pub use refreeze_guard::{
    validate_refreeze, RefreezeRequest, REASON_EMPTY_REFREEZE, REASON_MACHINE_ONLY,
    REASON_REVISION_DRIFT,
};
pub use stage::StageStatus;
pub use stagnation::{detect_stagnation, StagnationReport, TraceEventRange, SCHEMA_STAGNATION};
pub use trace_spine::{
    harness_requires_trace, TraceContext, TraceEvent, TraceSpine, REASON_TRACE_APPEND_FAILED,
    REASON_TRACE_CONTEXT_INCOMPLETE, REASON_TRACE_CONTEXT_MISMATCH, REASON_TRACE_EVIDENCE_BREAK,
    REASON_TRACE_HASH_INVALID, REASON_TRACE_MISSING, SCHEMA_TRACE_CONTEXT, SCHEMA_TRACE_SPINE,
};
pub use transition::{StageTransition, WorkflowTransition};
pub use workflow::WorkflowStage;
