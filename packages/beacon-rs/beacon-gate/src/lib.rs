//! Beacon v2 gate engine — truth_freeze / qa / release / implement gates.

pub mod harness_trace_gate;

use beacon_core::dual_track::{admit_path_set, DualTrackAdmission};
use beacon_core::trace_spine::TraceSpine;
use beacon_store::{BeaconStore, FeatureDao, GateDao};
use serde::{Deserialize, Serialize};

/// Gate types aligned with the Gate axis (truth_freeze / qa / release / implement).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum GateType {
    TruthFreeze,
    Qa,
    Release,
    Implement,
}

impl GateType {
    pub fn as_str(&self) -> &str {
        match self {
            GateType::TruthFreeze => "truth_freeze",
            GateType::Qa => "qa",
            GateType::Release => "release",
            GateType::Implement => "implement",
        }
    }

    pub fn parse(s: &str) -> Result<Self, String> {
        match s {
            "truth_freeze" => Ok(GateType::TruthFreeze),
            "qa" => Ok(GateType::Qa),
            "release" => Ok(GateType::Release),
            "implement" => Ok(GateType::Implement),
            other => Err(format!("unknown gate type: {other}")),
        }
    }
}

/// Gate verdict — pass / fail / blocked.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum Verdict {
    Pass,
    Fail,
    Blocked,
}

impl Verdict {
    pub fn as_str(&self) -> &str {
        match self {
            Verdict::Pass => "pass",
            Verdict::Fail => "fail",
            Verdict::Blocked => "blocked",
        }
    }
}

/// AC-013 gate result — written to gate_results on each evaluation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GateResult {
    pub gate_type: String,
    pub verdict: String,
    pub reason_codes: Vec<String>,
}

/// Gate engine — evaluates and persists gate results.
pub struct GateEngine<'a> {
    store: &'a BeaconStore,
}

impl<'a> GateEngine<'a> {
    pub fn new(store: &'a BeaconStore) -> Self {
        Self { store }
    }

    /// AC-013 evaluate a gate for a feature package and persist to gate_results.
    pub fn evaluate(
        &self,
        feature_slug: &str,
        version: &str,
        gate: GateType,
        verdict: Verdict,
        reason_codes: Vec<String>,
    ) -> Result<i64, String> {
        let conn = self.store.connection();
        let feature = FeatureDao::find_by_slug_version(conn, feature_slug, version)
            .map_err(|e| format!("store error: {e}"))?
            .ok_or_else(|| format!("feature package not found: {feature_slug} @ {version}"))?;
        let reason_json = if reason_codes.is_empty() {
            None
        } else {
            Some(serde_json::to_string(&reason_codes).unwrap_or_default())
        };
        GateDao::insert(
            conn,
            feature.id,
            gate.as_str(),
            verdict.as_str(),
            reason_json.as_deref(),
        )
        .map_err(|e| format!("store error: {e}"))
    }

    /// AC-020 spine gate — read the latest gate result for a feature.
    pub fn latest(
        &self,
        feature_slug: &str,
        version: &str,
        gate: GateType,
    ) -> Result<Option<GateResult>, String> {
        let conn = self.store.connection();
        let feature = FeatureDao::find_by_slug_version(conn, feature_slug, version)
            .map_err(|e| format!("store error: {e}"))?
            .ok_or_else(|| format!("feature package not found: {feature_slug} @ {version}"))?;
        let row = GateDao::latest_for_gate(conn, feature.id, gate.as_str())
            .map_err(|e| format!("store error: {e}"))?;
        Ok(row.map(|r| GateResult {
            gate_type: r.gate_name,
            verdict: r.verdict,
            reason_codes: parse_reason_codes_json(r.reason_codes_json.as_deref()),
        }))
    }
}

fn parse_reason_codes_json(raw: Option<&str>) -> Vec<String> {
    let Some(s) = raw else {
        return vec![];
    };
    serde_json::from_str::<Vec<String>>(s).unwrap_or_default()
}

/// AC-123/124: release must remain human gate; auto release_confirmed is illegal.
pub fn release_human_gate_invariant(auto_confirm: bool) -> Result<(), String> {
    if auto_confirm {
        Err("auto_release_confirmed_forbidden".into())
    } else {
        Ok(())
    }
}

/// Dual-track mixed source fail-closed (TC-148).
pub fn dual_track_gate(paths: &[&str], admitted_mixed: bool) -> DualTrackAdmission {
    admit_path_set(paths, admitted_mixed)
}

/// AC-133: implement/qa/release require valid TraceSpine.
pub fn require_trace_completeness(spine: &TraceSpine, phase: &str) -> Result<(), String> {
    spine.completeness_gate(phase)
}

#[cfg(test)]
mod tests {
    use super::*;
    use beacon_core::trace_spine::TraceContext;

    #[test]
    fn release_not_auto() {
        assert!(release_human_gate_invariant(false).is_ok());
        assert!(release_human_gate_invariant(true).is_err());
    }

    #[test]
    fn dual_track_blocks_mixed() {
        let r = dual_track_gate(
            &["beacon/main.py", "packages/beacon-rs/beacon-core/src/lib.rs"],
            false,
        );
        assert!(r.blocked);
    }

    #[test]
    fn trace_gate_requires_events() {
        let spine = TraceSpine::create("r", TraceContext::new("r"));
        assert!(require_trace_completeness(&spine, "implement").is_err());
    }
}
