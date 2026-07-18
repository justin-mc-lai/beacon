//! Harness boundary reason_codes (AC-130).

use serde::{Deserialize, Serialize};

pub const REASON_HARNESS_CROSS: &str = "harness_boundary_violation";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HarnessBoundaryEvent {
    pub actor_harness: String,
    pub action: String,
    pub target_authority: String,
}

/// Fail-closed when a harness writes outside its authority.
pub fn check_harness_boundary(ev: &HarnessBoundaryEvent) -> Result<(), String> {
    let allowed = match ev.actor_harness.as_str() {
        "planner" | "loop" => vec!["decision_packet", "intent_snapshot", "trace"],
        "truth" => vec!["truth", "refreeze", "trace"],
        "design" => vec!["design_primitives", "design_md", "trace"],
        "implement" => vec!["code", "artifact", "trace"],
        "qa-evidence" | "qa" => vec!["scorecard", "evidence", "trace"],
        "release" => vec!["release_decision", "trace"],
        _ => vec![],
    };
    if allowed.is_empty() {
        return Err(format!("{REASON_HARNESS_CROSS}:unknown_harness"));
    }
    if !allowed.iter().any(|a| ev.target_authority.starts_with(a) || *a == ev.target_authority) {
        // implement writing truth is classic violation
        return Err(format!(
            "{REASON_HARNESS_CROSS}:{}->{}",
            ev.actor_harness, ev.target_authority
        ));
    }
    // special: implement must not write frozen truth
    if ev.actor_harness == "implement" && ev.target_authority.starts_with("truth") {
        return Err(format!("{REASON_HARNESS_CROSS}:implement_cannot_write_truth"));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn implement_cannot_write_truth() {
        let e = HarnessBoundaryEvent {
            actor_harness: "implement".into(),
            action: "write".into(),
            target_authority: "truth".into(),
        };
        assert!(check_harness_boundary(&e).is_err());
    }

    #[test]
    fn qa_can_write_scorecard() {
        let e = HarnessBoundaryEvent {
            actor_harness: "qa-evidence".into(),
            action: "write".into(),
            target_authority: "scorecard".into(),
        };
        assert!(check_harness_boundary(&e).is_ok());
    }
}
