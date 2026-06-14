use serde::{Deserialize, Serialize};

/// Delivery runtime compressed enum — persisted as `runs.status`. AC-031
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub enum RunStatus {
    Created,
    Resolving,
    Running,
    Paused,
    Stopping,
    Stopped,
    Succeeded,
    Failed,
    Repairing,
    Importing,
    AwaitingQa,
    Closed,
}

impl RunStatus {
    pub fn all() -> &'static [RunStatus] {
        &[
            Self::Created,
            Self::Resolving,
            Self::Running,
            Self::Paused,
            Self::Stopping,
            Self::Stopped,
            Self::Succeeded,
            Self::Failed,
            Self::Repairing,
            Self::Importing,
            Self::AwaitingQa,
            Self::Closed,
        ]
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Created => "Created",
            Self::Resolving => "Resolving",
            Self::Running => "Running",
            Self::Paused => "Paused",
            Self::Stopping => "Stopping",
            Self::Stopped => "Stopped",
            Self::Succeeded => "Succeeded",
            Self::Failed => "Failed",
            Self::Repairing => "Repairing",
            Self::Importing => "Importing",
            Self::AwaitingQa => "AwaitingQa",
            Self::Closed => "Closed",
        }
    }

    pub fn parse(value: &str) -> Result<Self, crate::error::BeaconError> {
        for status in Self::all() {
            if status.as_str() == value {
                return Ok(*status);
            }
        }
        Err(crate::error::BeaconError::InvalidEnum {
            kind: "RunStatus",
            value: value.to_string(),
        })
    }
}
