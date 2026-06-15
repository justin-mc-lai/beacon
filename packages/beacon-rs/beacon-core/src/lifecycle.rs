use serde::{Deserialize, Serialize};

/// Plan delivery chain event types (audit log). AC-032
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub enum LifecycleEventType {
    IntentCapture,
    IntentReview,
    UserDecisionPending,
    TruthGapScan,
    TruthFill,
    TruthFreezeGate,
    ImplementLoop,
    EvidenceImport,
    QaPending,
    RepairFromQa,
    ReleasePending,
    RepairFromRelease,
    TerminalClosed,
    TerminalAborted,
    Crashed,
    TimedOut,
    Interrupted,
    NotesInjected,
    PhaseTransition,
}

impl LifecycleEventType {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::IntentCapture => "IntentCapture",
            Self::IntentReview => "IntentReview",
            Self::UserDecisionPending => "UserDecisionPending",
            Self::TruthGapScan => "TruthGapScan",
            Self::TruthFill => "TruthFill",
            Self::TruthFreezeGate => "TruthFreezeGate",
            Self::ImplementLoop => "ImplementLoop",
            Self::EvidenceImport => "EvidenceImport",
            Self::QaPending => "QaPending",
            Self::RepairFromQa => "RepairFromQa",
            Self::ReleasePending => "ReleasePending",
            Self::RepairFromRelease => "RepairFromRelease",
            Self::TerminalClosed => "TerminalClosed",
            Self::TerminalAborted => "TerminalAborted",
            Self::Crashed => "Crashed",
            Self::TimedOut => "TimedOut",
            Self::Interrupted => "Interrupted",
            Self::NotesInjected => "NotesInjected",
            Self::PhaseTransition => "PhaseTransition",
        }
    }
}
