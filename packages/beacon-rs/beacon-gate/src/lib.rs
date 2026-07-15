//! Beacon v2 gate engine — truth_freeze / qa / release / implement gates (P2 skeleton, AC-013/020).
//!
//! P2 skeleton: gate evaluation writes gate_results (AC-013); spine gate reads
//! latest verdict (AC-020). Full reason_codes engine + FSM binding is P3.

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
    /// P2 skeleton: the verdict is provided by the caller (full reason_codes
    /// engine arrives in P3). Returns the inserted gate_result id.
    pub fn evaluate(
        &self,
        feature_slug: &str,
        version: &str,
        gate: GateType,
        verdict: Verdict,
        reason_codes: Vec<String>,
    ) -> Result<i64, String> {
        let conn = self.store.connection();
        // resolve feature_package_id by slug + version
        let feature = FeatureDao::find_by_slug_version(conn, feature_slug, version)
            .map_err(|e| format!("store error: {e}"))?
            .ok_or_else(|| format!("feature package not found: {feature_slug} @ {version}"))?;
        let reason_json = if reason_codes.is_empty() {
            None
        } else {
            Some(serde_json::to_string(&reason_codes).unwrap_or_default())
        };
        GateDao::insert(conn, feature.id, gate.as_str(), verdict.as_str(), reason_json.as_deref())
            .map_err(|e| format!("store error: {e}"))
    }

    /// AC-020 spine gate — read the latest gate result for a feature.
    pub fn latest(&self, feature_slug: &str, version: &str, gate: GateType) -> Result<Option<GateResult>, String> {
        let conn = self.store.connection();
        let feature = FeatureDao::find_by_slug_version(conn, feature_slug, version)
            .map_err(|e| format!("store error: {e}"))?
            .ok_or_else(|| format!("feature package not found: {feature_slug} @ {version}"))?;
        let row = GateDao::latest_for_gate(conn, feature.id, gate.as_str())
            .map_err(|e| format!("store error: {e}"))?;
        Ok(row.map(|r| GateResult {
            gate_type: r.gate_name,
            verdict: r.verdict,
            reason_codes: vec![], // P3: parse reason_codes_json
        }))
    }
}
