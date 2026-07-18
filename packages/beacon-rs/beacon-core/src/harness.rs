//! Six first-class harness abilities (v2 public surface) — AC-059/063/109/125.

use serde::{Deserialize, Serialize};

/// Public harness abilities exposed by v2 (exactly six; no seventh public skill).
pub const PUBLIC_ABILITIES: [&str; 6] = [
    "loop",
    "truth",
    "design",
    "implement",
    "qa-evidence",
    "release",
];

/// Host-visible denylist — internal modules, not first-class public skills (AC-125).
pub const INTERNAL_DENYLIST: [&str; 10] = [
    "doctor",
    "router",
    "hooks",
    "metadata",
    "debug",
    "archive",
    "status",
    "gov",
    "library",
    "lighthouse",
];

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct HarnessAbility {
    pub name: String,
    pub public: bool,
    pub description: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct HarnessSurface {
    pub schema: String,
    pub version: String,
    pub abilities: Vec<HarnessAbility>,
    pub internal_denylist: Vec<String>,
}

impl HarnessSurface {
    pub fn v2_default() -> Self {
        let abilities = PUBLIC_ABILITIES
            .iter()
            .map(|name| HarnessAbility {
                name: (*name).to_string(),
                public: true,
                description: format!("v2 first-class harness ability: {name}"),
            })
            .collect();
        Self {
            schema: "harness-surface.v1".into(),
            version: "v2.0.0".into(),
            abilities,
            internal_denylist: INTERNAL_DENYLIST.iter().map(|s| (*s).to_string()).collect(),
        }
    }

    pub fn is_public(name: &str) -> bool {
        PUBLIC_ABILITIES.contains(&name)
    }

    pub fn is_internal_denylist(name: &str) -> bool {
        INTERNAL_DENYLIST.iter().any(|d| name.contains(d))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exactly_six_public() {
        let s = HarnessSurface::v2_default();
        assert_eq!(s.abilities.len(), 6);
        assert!(s.abilities.iter().all(|a| a.public));
        assert!(!HarnessSurface::is_public("doctor"));
        assert!(HarnessSurface::is_internal_denylist("beacon-gov-doctor"));
    }
}
