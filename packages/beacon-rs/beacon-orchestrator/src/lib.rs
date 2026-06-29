//! Beacon v2 orchestrator — long-task goal/run/iterate loop (P2, AC-040..050).
//!
//! Orchestrator drives an AgentBackend through iterations, persists run state to
//! beacon-store, and honors stop_when. It does NOT issue QA/release verdicts (AC-049).

use beacon_core::agent::{AgentBackend, IterationResult};
use beacon_store::{BeaconStore, LifecycleEventDao, RunDao};
use std::sync::atomic::{AtomicBool, Ordering};

/// Stop condition for the iterate loop (AC-048 stop_when).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum StopWhen {
    /// Stop after a gate passes (e.g. "qa").
    GatePass(String),
    /// Stop after N iterations.
    MaxIterations(u32),
    /// Never stop (until externally aborted).
    Never,
}

/// Orchestrator drives a run's iteration loop against an AgentBackend.
pub struct Orchestrator<'a> {
    store: &'a BeaconStore,
    run_id: i64,
    stop_when: StopWhen,
    aborted: AtomicBool,
}

/// Result of a single iterate step.
#[derive(Debug, Clone)]
pub struct StepResult {
    pub iteration: u32,
    pub result: IterationResult,
    pub stopped: bool,
    pub stop_reason: String,
}

impl<'a> Orchestrator<'a> {
    pub fn new(store: &'a BeaconStore, run_id: i64, stop_when: StopWhen) -> Self {
        Self {
            store,
            run_id,
            stop_when,
            aborted: AtomicBool::new(false),
        }
    }

    /// Signal abort (SIGINT-like). The next iterate step returns stopped.
    pub fn abort(&self) {
        self.aborted.store(true, Ordering::SeqCst);
    }

    /// AC-040 run status — read from store.
    pub fn status(&self) -> Result<String, String> {
        let conn = self.store.connection();
        let row = beacon_store::RunDao::get(conn, self.run_id)
            .map_err(|e| format!("store error: {e}"))?
            .ok_or_else(|| format!("run {} not found", self.run_id))?;
        Ok(row.status)
    }

    /// AC-042/044 run the iterate loop. Returns the steps.
    /// AC-049: never emits QA/release/complete verdicts — only iteration results.
    pub fn run(&mut self, backend: &mut dyn AgentBackend, prompt: &str) -> Result<Vec<StepResult>, String> {
        backend.health_check().map_err(|e| format!("health check failed: {e}"))?;
        let mut steps: Vec<StepResult> = Vec::new();
        let max = match &self.stop_when {
            StopWhen::MaxIterations(n) => *n,
            _ => 100,
        };
        for i in 1..=max {
            if self.aborted.load(Ordering::SeqCst) {
                if let Some(last) = steps.last_mut() {
                    last.stopped = true;
                    last.stop_reason = "aborted".to_string();
                }
                break;
            }
            let result = backend.iterate(prompt).map_err(|e| format!("iterate error: {e}"))?;
            let stop_signal = result.stop_signal.clone();
            let mut stopped = false;
            let mut stop_reason = String::new();
            if let Some(ref sig) = stop_signal {
                if sig == "qa_pass" || sig == "gate_pass" {
                    stopped = true;
                    stop_reason = format!("stop_when gate pass: {sig}");
                }
            }
            steps.push(StepResult {
                iteration: i,
                result: result.clone(),
                stopped,
                stop_reason: stop_reason.clone(),
            });
            if stopped {
                break;
            }
        }
        Ok(steps)
    }
}

/// AC-044 SubprocessBackend — runs a harness command per iteration, parses JSON output.
pub struct SubprocessBackend {
    name: String,
    command: Vec<String>,
    iteration: u32,
    max_iterations: u32,
}

impl SubprocessBackend {
    /// Create a subprocess backend that runs `command` (with {iter} placeholder)
    /// up to `max_iterations` times. Each iteration's stdout must be JSON matching
    /// IterationResult schema.
    pub fn new(name: impl Into<String>, command: Vec<String>, max_iterations: u32) -> Self {
        Self {
            name: name.into(),
            command,
            iteration: 0,
            max_iterations,
        }
    }
}

impl AgentBackend for SubprocessBackend {
    fn name(&self) -> &str {
        &self.name
    }

    fn health_check(&self) -> Result<(), String> {
        if self.command.is_empty() {
            return Err("empty command".to_string());
        }
        Ok(())
    }

    fn iterate(&mut self, _prompt: &str) -> Result<IterationResult, String> {
        self.iteration += 1;
        if self.iteration > self.max_iterations {
            return Ok(IterationResult {
                success: true,
                summary: "max iterations reached".to_string(),
                key_changes_made: vec![],
                key_learnings: vec![],
                stop_signal: Some("max_iterations".to_string()),
                token_usage: beacon_core::agent::TokenUsage::default(),
                agent_name: self.name.clone(),
            });
        }
        let cmd = self.command[0].clone();
        let args: Vec<String> = self.command[1..]
            .iter()
            .map(|a| a.replace("{iter}", &self.iteration.to_string()))
            .collect();
        let output = std::process::Command::new(&cmd)
            .args(&args)
            .output()
            .map_err(|e| format!("subprocess spawn failed: {e}"))?;
        if !output.status.success() {
            return Err(format!(
                "subprocess exited {}: {}",
                output.status,
                String::from_utf8_lossy(&output.stderr)
            ));
        }
        let stdout = String::from_utf8_lossy(&output.stdout);
        let result: IterationResult = serde_json::from_str(stdout.trim())
            .map_err(|e| format!("parse iteration json: {e} (stdout: {})", stdout.trim()))?;
        Ok(result)
    }

    fn abort(&mut self) -> Result<(), String> {
        self.iteration = self.max_iterations;
        Ok(())
    }
}

/// AC-102 planner_review — v1.6 multi-agent runtime isomorphic fields.
/// Single-process fallback when no subagent runtime is available (must NOT claim
/// parallel execution).
#[derive(Debug, Clone, serde::Serialize)]
pub struct PlannerReviewResult {
    pub reviewer_lanes: Vec<ReviewerLane>,
    pub findings: Vec<Finding>,
    pub synthesis: String,
    pub execution_mode: String,
    pub fallback_reason: String,
    pub runtime_evidence_only: bool,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct ReviewerLane {
    pub authority: String,
    pub findings: Vec<Finding>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Finding {
    pub severity: String,
    pub title: String,
    pub detail: String,
}

impl PlannerReviewResult {
    /// Single-process multi-reviewer fallback (AC-102). No parallel subagent claim.
    pub fn single_process_fallback(findings: Vec<Finding>, synthesis: String) -> Self {
        Self {
            reviewer_lanes: vec![ReviewerLane {
                authority: "single_process_multi_reviewer".to_string(),
                findings: findings.clone(),
            }],
            findings,
            synthesis,
            execution_mode: "single_process_multi_reviewer".to_string(),
            fallback_reason: "subagent_runtime_unavailable".to_string(),
            runtime_evidence_only: true,
        }
    }
}

// ---- AC-041 truth-map preflight ----

/// AC-041 truth-map preflight result.
#[derive(Debug, Clone)]
pub struct TruthMapPreflight {
    pub status: String,
    pub feature_status: String,
    pub blocked: bool,
    pub reason: String,
}

/// AC-041 read a truth.md frontmatter `status:` field. Returns blocked=true if
/// the truth package is not frozen (status != "frozen"). The orchestrator must
/// not start a run on a non-frozen truth.
pub fn truth_map_preflight(truth_md_path: &std::path::Path) -> TruthMapPreflight {
    let text = match std::fs::read_to_string(truth_md_path) {
        Ok(t) => t,
        Err(e) => {
            return TruthMapPreflight {
                status: "blocked".to_string(),
                feature_status: String::new(),
                blocked: true,
                reason: format!("truth.md read failed: {e}"),
            };
        }
    };
    let feature_status = parse_frontmatter_status(&text).unwrap_or_default();
    let blocked = feature_status != "frozen";
    let reason = if blocked {
        format!("truth status is `{feature_status}`, not frozen; run `beacon change` to reopen or `beacon freeze` to freeze")
    } else {
        String::new()
    };
    TruthMapPreflight {
        status: if blocked { "blocked" } else { "pass" }.to_string(),
        feature_status,
        blocked,
        reason,
    }
}

fn parse_frontmatter_status(text: &str) -> Option<String> {
    let trimmed = text.trim_start();
    if !trimmed.starts_with("---") {
        return None;
    }
    let rest = &trimmed[3..];
    let end = rest.find("---")?;
    let fm = &rest[..end];
    for line in fm.lines() {
        let line = line.trim();
        if let Some(val) = line.strip_prefix("status:") {
            return Some(val.trim().trim_matches('"').to_string());
        }
    }
    None
}

// ---- AC-050 phase controller ----

/// AC-050 phase controller — four phases written to runs.metadata_json and
/// phase transitions written to lifecycle_events.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct PhaseState {
    pub phase: String,
    pub phases_completed: Vec<String>,
}

impl PhaseState {
    pub fn new() -> Self {
        Self { phase: "plan".to_string(), phases_completed: vec![] }
    }

    /// Transition to a new phase. Writes metadata_json + lifecycle_event.
    pub fn transition(
        &mut self,
        store: &BeaconStore,
        run_id: i64,
        feature_package_id: i64,
        new_phase: &str,
    ) -> Result<(), String> {
        if self.phase != new_phase {
            self.phases_completed.push(self.phase.clone());
        }
        self.phase = new_phase.to_string();
        let metadata_json = serde_json::to_string(self).map_err(|e| format!("serialize: {e}"))?;
        let conn = store.connection();
        RunDao::update_metadata(conn, run_id, &metadata_json).map_err(|e| format!("store: {e}"))?;
        let payload = serde_json::json!({ "from": self.phases_completed.last(), "to": new_phase });
        LifecycleEventDao::insert(
            conn,
            Some(run_id),
            feature_package_id,
            "PhaseTransition",
            Some(&payload.to_string()),
        )
        .map_err(|e| format!("store: {e}"))?;
        Ok(())
    }
}

impl Default for PhaseState {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stop_when_gate_pass_variants() {
        assert_eq!(StopWhen::GatePass("qa".into()), StopWhen::GatePass("qa".into()));
        assert_ne!(StopWhen::GatePass("qa".into()), StopWhen::MaxIterations(3));
    }

    #[test]
    fn planner_review_fallback_no_parallel_claim() {
        let r = PlannerReviewResult::single_process_fallback(
            vec![Finding { severity: "P2".into(), title: "x".into(), detail: "d".into() }],
            "synthesis".into(),
        );
        assert_eq!(r.execution_mode, "single_process_multi_reviewer");
        assert_eq!(r.fallback_reason, "subagent_runtime_unavailable");
        assert!(r.runtime_evidence_only);
        assert!(!r.execution_mode.contains("parallel"));
    }
}
