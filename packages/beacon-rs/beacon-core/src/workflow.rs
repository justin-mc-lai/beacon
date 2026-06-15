use serde::{Deserialize, Serialize};

/// Product lifecycle stages (type layer). AC-026
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub enum WorkflowStage {
    Think,
    UserStory,
    Prd,
    TestCase,
    Prototype,
    Freeze,
    Implement,
    Qa,
    Release,
    Archive,
}

impl WorkflowStage {
    pub fn all() -> &'static [WorkflowStage] {
        &[
            Self::Think,
            Self::UserStory,
            Self::Prd,
            Self::TestCase,
            Self::Prototype,
            Self::Freeze,
            Self::Implement,
            Self::Qa,
            Self::Release,
            Self::Archive,
        ]
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Think => "Think",
            Self::UserStory => "UserStory",
            Self::Prd => "Prd",
            Self::TestCase => "TestCase",
            Self::Prototype => "Prototype",
            Self::Freeze => "Freeze",
            Self::Implement => "Implement",
            Self::Qa => "Qa",
            Self::Release => "Release",
            Self::Archive => "Archive",
        }
    }

    pub fn parse(value: &str) -> Result<Self, crate::error::BeaconError> {
        match value {
            "Think" => Ok(Self::Think),
            "UserStory" => Ok(Self::UserStory),
            "Prd" => Ok(Self::Prd),
            "TestCase" => Ok(Self::TestCase),
            "Prototype" => Ok(Self::Prototype),
            "Freeze" => Ok(Self::Freeze),
            "Implement" => Ok(Self::Implement),
            "Qa" => Ok(Self::Qa),
            "Release" => Ok(Self::Release),
            "Archive" => Ok(Self::Archive),
            _ => Err(crate::error::BeaconError::InvalidEnum {
                kind: "WorkflowStage",
                value: value.to_string(),
            }),
        }
    }
}
