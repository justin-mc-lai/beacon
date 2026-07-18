//! TraceSpine.v1 + TraceContext.v1 — kernel authority for loop/implement/qa/release (AC-131..133).

use crate::branch_context::BranchContext;
use serde::{Deserialize, Serialize};
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

pub const SCHEMA_TRACE_SPINE: &str = "TraceSpine.v1";
pub const SCHEMA_TRACE_CONTEXT: &str = "TraceContext.v1";
pub const REASON_TRACE_MISSING: &str = "trace_spine_missing";
pub const REASON_TRACE_HASH_INVALID: &str = "trace_hash_chain_invalid";
pub const REASON_TRACE_APPEND_FAILED: &str = "trace_append_failed";
pub const REASON_TRACE_EVIDENCE_BREAK: &str = "trace_event_to_evidence_break";
pub const REASON_TRACE_CONTEXT_INCOMPLETE: &str = "trace_context_binding_incomplete";
pub const REASON_TRACE_CONTEXT_MISMATCH: &str = "trace_context_branch_mismatch";

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TraceContext {
    pub schema: String,
    pub run_id: String,
    pub branch_context_ref: String,
    pub decision_packet_ref: String,
    pub intent_snapshot_ref: String,
    pub truth_hash: String,
    pub design_primitives_ref: String,
}

impl TraceContext {
    pub fn new(run_id: impl Into<String>) -> Self {
        Self {
            schema: SCHEMA_TRACE_CONTEXT.into(),
            run_id: run_id.into(),
            branch_context_ref: String::new(),
            decision_packet_ref: String::new(),
            intent_snapshot_ref: String::new(),
            truth_hash: String::new(),
            design_primitives_ref: String::new(),
        }
    }

    pub fn with_bindings(
        mut self,
        branch_context_ref: impl Into<String>,
        decision_packet_ref: impl Into<String>,
        intent_snapshot_ref: impl Into<String>,
        truth_hash: impl Into<String>,
        design_primitives_ref: impl Into<String>,
    ) -> Self {
        self.branch_context_ref = branch_context_ref.into();
        self.decision_packet_ref = decision_packet_ref.into();
        self.intent_snapshot_ref = intent_snapshot_ref.into();
        self.truth_hash = truth_hash.into();
        self.design_primitives_ref = design_primitives_ref.into();
        self
    }

    /// AC-132: all required refs must be non-empty before loop start proceeds to implement.
    pub fn validate_bindings(&self) -> Result<(), String> {
        for (name, val) in [
            ("branch_context_ref", &self.branch_context_ref),
            ("decision_packet_ref", &self.decision_packet_ref),
            ("intent_snapshot_ref", &self.intent_snapshot_ref),
            ("truth_hash", &self.truth_hash),
        ] {
            if val.trim().is_empty() {
                return Err(format!("{REASON_TRACE_CONTEXT_INCOMPLETE}:{name}"));
            }
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TraceEvent {
    pub seq: u64,
    pub event_type: String,
    pub summary: String,
    pub prev_hash: String,
    pub event_hash: String,
    pub evidence_ref: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TraceSpine {
    pub schema: String,
    pub run_id: String,
    pub context: TraceContext,
    pub events: Vec<TraceEvent>,
    pub head_hash: String,
}

impl TraceSpine {
    pub fn create(run_id: impl Into<String>, context: TraceContext) -> Self {
        let run_id = run_id.into();
        Self {
            schema: SCHEMA_TRACE_SPINE.into(),
            run_id: run_id.clone(),
            context: TraceContext {
                run_id: run_id.clone(),
                ..context
            },
            events: vec![],
            head_hash: "genesis".into(),
        }
    }

    fn hash_payload(prev: &str, event_type: &str, summary: &str, evidence_ref: &str) -> String {
        let mut h = DefaultHasher::new();
        prev.hash(&mut h);
        event_type.hash(&mut h);
        summary.hash(&mut h);
        evidence_ref.hash(&mut h);
        format!("{:016x}", h.finish())
    }

    pub fn append(
        &mut self,
        event_type: impl Into<String>,
        summary: impl Into<String>,
        evidence_ref: impl Into<String>,
    ) -> Result<&TraceEvent, String> {
        let event_type = event_type.into();
        let summary = summary.into();
        let evidence_ref = evidence_ref.into();
        if evidence_ref.trim().is_empty() {
            return Err(REASON_TRACE_APPEND_FAILED.into());
        }
        let prev = self.head_hash.clone();
        let event_hash = Self::hash_payload(&prev, &event_type, &summary, &evidence_ref);
        let seq = self.events.len() as u64 + 1;
        self.events.push(TraceEvent {
            seq,
            event_type,
            summary,
            prev_hash: prev,
            event_hash: event_hash.clone(),
            evidence_ref,
        });
        self.head_hash = event_hash;
        Ok(self.events.last().expect("just pushed"))
    }

    pub fn validate_chain(&self) -> Result<(), String> {
        let mut prev = "genesis".to_string();
        for ev in &self.events {
            if ev.prev_hash != prev {
                return Err(REASON_TRACE_HASH_INVALID.into());
            }
            let expect =
                Self::hash_payload(&ev.prev_hash, &ev.event_type, &ev.summary, &ev.evidence_ref);
            if expect != ev.event_hash {
                return Err(REASON_TRACE_HASH_INVALID.into());
            }
            prev = ev.event_hash.clone();
        }
        if self.events.is_empty() {
            return Err(REASON_TRACE_MISSING.into());
        }
        if self.head_hash != prev {
            return Err(REASON_TRACE_HASH_INVALID.into());
        }
        Ok(())
    }

    /// Completeness gate for implement / qa-evidence / release (AC-133).
    pub fn completeness_gate(&self, phase: &str) -> Result<(), String> {
        self.validate_chain()?;
        for ev in &self.events {
            if ev.evidence_ref.is_empty() {
                return Err(format!("{REASON_TRACE_EVIDENCE_BREAK}:{phase}"));
            }
        }
        Ok(())
    }

    /// Bindings + chain + optional BranchContext consistency.
    pub fn authority_gate(
        &self,
        phase: &str,
        branch: Option<&BranchContext>,
    ) -> Result<(), String> {
        self.context.validate_bindings()?;
        self.completeness_gate(phase)?;
        if let Some(bc) = branch {
            bc.governance_gate(None)?;
            let expected = format!("branch_context:{}", bc.run_id);
            if !self.context.branch_context_ref.is_empty()
                && self.context.branch_context_ref != expected
                && !self.context.branch_context_ref.contains(&bc.run_id)
            {
                return Err(REASON_TRACE_CONTEXT_MISMATCH.into());
            }
        }
        Ok(())
    }
}

/// Harness phase names that require TraceSpine hard gate.
pub fn harness_requires_trace(phase: &str) -> bool {
    matches!(
        phase,
        "implement" | "qa-evidence" | "qa" | "release" | "loop"
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hash_chain_roundtrip() {
        let ctx = TraceContext::new("r1").with_bindings("bc", "dp", "is", "th", "des");
        let mut spine = TraceSpine::create("r1", ctx);
        spine.append("decision", "start", "ev/1").unwrap();
        spine.append("tool_call", "iterate", "ev/2").unwrap();
        assert!(spine.validate_chain().is_ok());
        assert!(spine.completeness_gate("implement").is_ok());
    }

    #[test]
    fn empty_trace_missing() {
        let spine = TraceSpine::create("r", TraceContext::new("r"));
        assert_eq!(spine.validate_chain().unwrap_err(), REASON_TRACE_MISSING);
    }

    #[test]
    fn tamper_detected() {
        let mut spine = TraceSpine::create(
            "r",
            TraceContext::new("r").with_bindings("b", "d", "i", "t", "x"),
        );
        spine.append("decision", "a", "e1").unwrap();
        spine.events[0].summary = "tampered".into();
        assert_eq!(
            spine.validate_chain().unwrap_err(),
            REASON_TRACE_HASH_INVALID
        );
    }

    #[test]
    fn binding_incomplete_blocks() {
        let ctx = TraceContext::new("r");
        assert!(ctx.validate_bindings().is_err());
    }

    #[test]
    fn empty_evidence_append_fails() {
        let mut spine = TraceSpine::create(
            "r",
            TraceContext::new("r").with_bindings("b", "d", "i", "t", "x"),
        );
        assert!(spine.append("decision", "x", "").is_err());
    }
}
