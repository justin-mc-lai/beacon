//! Beacon v2 core — types, state machines, agent contracts (zero IO).

pub mod agent;
pub mod delivery;
pub mod error;
pub mod evidence;
pub mod lifecycle;
pub mod stage;
pub mod transition;
pub mod workflow;

pub use agent::{AgentBackend, IterationResult, TokenUsage};
pub use delivery::RunStatus;
pub use error::{BeaconError, ReasonCode, TransitionError};
pub use evidence::EvidenceChain;
pub use lifecycle::LifecycleEventType;
pub use stage::StageStatus;
pub use transition::{StageTransition, WorkflowTransition};
pub use workflow::WorkflowStage;
