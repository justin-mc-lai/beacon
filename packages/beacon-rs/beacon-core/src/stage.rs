use serde::{Deserialize, Serialize};

/// Per-stage status (type layer). AC-026
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub enum StageStatus {
    NotStarted,
    InProgress,
    Blocked,
    Completed,
    Failed,
    Skipped,
    Crashed,
    TimedOut,
    Interrupted,
    Repairing,
}

impl StageStatus {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::NotStarted => "NotStarted",
            Self::InProgress => "InProgress",
            Self::Blocked => "Blocked",
            Self::Completed => "Completed",
            Self::Failed => "Failed",
            Self::Skipped => "Skipped",
            Self::Crashed => "Crashed",
            Self::TimedOut => "TimedOut",
            Self::Interrupted => "Interrupted",
            Self::Repairing => "Repairing",
        }
    }

    pub fn requires_deferral_id(self) -> bool {
        matches!(self, Self::Skipped)
    }
}

/// Blocked status payload. AC-028
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BlockedStatus {
    pub reason_codes: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub blocking_gate: Option<String>,
}

/// Skipped status payload. AC-029
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SkippedStatus {
    pub user_accepted_deferral_id: String,
}
