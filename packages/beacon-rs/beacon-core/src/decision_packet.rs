//! decision_packet.v1 + intent_snapshot.v1 (AC-111..114).

use serde::{Deserialize, Serialize};

pub const SCHEMA_DECISION_PACKET: &str = "decision_packet.v1";
pub const SCHEMA_INTENT_SNAPSHOT: &str = "intent_snapshot.v1";
pub const REASON_DECISION_PACKET_MISSING: &str = "decision_packet_missing";
pub const REASON_INTENT_LOW_CONFIDENCE: &str = "intent_low_confidence_freeze_block";
pub const REASON_INTENT_MISSING: &str = "intent_snapshot_missing";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntentSnapshot {
    pub schema: String,
    pub run_id: String,
    pub utterance: String,
    pub confidence: f32,
    pub accepted: bool,
    pub topics: Vec<String>,
}

impl IntentSnapshot {
    pub fn new(run_id: impl Into<String>, utterance: impl Into<String>, confidence: f32) -> Self {
        Self {
            schema: SCHEMA_INTENT_SNAPSHOT.into(),
            run_id: run_id.into(),
            utterance: utterance.into(),
            confidence,
            accepted: confidence >= 0.55,
            topics: vec![],
        }
    }

    /// AC-113: low-confidence freeze block
    pub fn freeze_gate(&self) -> Result<(), String> {
        if self.utterance.trim().is_empty() {
            return Err(REASON_INTENT_MISSING.into());
        }
        if !self.accepted || self.confidence < 0.55 {
            return Err(REASON_INTENT_LOW_CONFIDENCE.into());
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecisionPacket {
    pub schema: String,
    pub run_id: String,
    pub intent_snapshot_ref: String,
    pub next_harness: String,
    pub auto_decide: bool,
    pub human_release_required: bool,
    pub reasons: Vec<String>,
}

impl DecisionPacket {
    pub fn for_loop(
        run_id: impl Into<String>,
        intent_ref: impl Into<String>,
        next_harness: impl Into<String>,
    ) -> Self {
        Self {
            schema: SCHEMA_DECISION_PACKET.into(),
            run_id: run_id.into(),
            intent_snapshot_ref: intent_ref.into(),
            next_harness: next_harness.into(),
            auto_decide: false,
            human_release_required: true,
            reasons: vec!["loop_admission".into()],
        }
    }

    /// AC-114: loop admission requires non-empty packet bound to intent.
    pub fn loop_admission_gate(&self) -> Result<(), String> {
        if self.schema != SCHEMA_DECISION_PACKET {
            return Err(REASON_DECISION_PACKET_MISSING.into());
        }
        if self.intent_snapshot_ref.trim().is_empty() {
            return Err(REASON_DECISION_PACKET_MISSING.into());
        }
        if self.next_harness.trim().is_empty() {
            return Err(REASON_DECISION_PACKET_MISSING.into());
        }
        // release never auto
        if self.next_harness == "release" && !self.human_release_required {
            return Err("auto_release_confirmed_forbidden".into());
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn low_confidence_blocks() {
        let i = IntentSnapshot::new("r", "maybe something", 0.2);
        assert!(i.freeze_gate().is_err());
    }

    #[test]
    fn packet_admission() {
        let p = DecisionPacket::for_loop("r", "intent:r", "implement");
        assert!(p.loop_admission_gate().is_ok());
    }
}
