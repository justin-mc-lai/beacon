//! P2 orchestrator integration tests — AC-044 (subprocess real iteration),
//! AC-048 (stop_when), AC-102 (planner_review fallback), AC-040 (run status).

use beacon_core::agent::{AgentBackend, IterationResult, TokenUsage};
use beacon_orchestrator::{Orchestrator, PlannerReviewResult, StopWhen, SubprocessBackend};
use beacon_store::{BeaconStore, FeatureDao, ProjectDao, RunDao};
use beacon_core::RunStatus;
use std::io::Write;

// ---- AC-040 orchestrator status reads from store ----

#[test]
fn tc040_orchestrator_status_reads_run() {
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    let orch = Orchestrator::new(&store, run_id, StopWhen::Never);
    let status = orch.status().unwrap();
    assert_eq!(status, "Running");
}

// ---- AC-044 SubprocessBackend real iteration (harness command) ----

#[test]
fn tc044_subprocess_backend_one_real_iteration() {
    // Create a test harness script that outputs valid IterationResult JSON
    let dir = tempfile::tempdir().unwrap();
    let script = dir.path().join("harness.sh");
    let json = r#"{"success":true,"summary":"did one iteration","key_changes_made":["fix"],"key_learnings":[],"stop_signal":null,"token_usage":{"input_tokens":10,"output_tokens":20},"agent_name":"subprocess-test"}"#;
    let mut f = std::fs::File::create(&script).unwrap();
    writeln!(f, "#!/bin/sh\necho '{}'", json).unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = std::fs::metadata(&script).unwrap().permissions();
        perms.set_mode(0o755);
        std::fs::set_permissions(&script, perms).unwrap();
    }
    let mut backend = SubprocessBackend::new("subprocess-test", vec![script.to_str().unwrap().to_string()], 1);
    backend.health_check().unwrap();
    let result = backend.iterate("do something").unwrap();
    assert!(result.success);
    assert_eq!(result.summary, "did one iteration");
    assert_eq!(result.agent_name, "subprocess-test");
    assert_eq!(result.token_usage.input_tokens, 10);
}

// ---- AC-048 stop_when: gate pass stops the loop ----

#[test]
fn tc048_stop_when_gate_pass_early_stop() {
    use std::sync::{Arc, Mutex};
    // A fake backend that returns qa_pass on iteration 2
    struct StopOnTwo { iter: Arc<Mutex<u32>> }
    impl AgentBackend for StopOnTwo {
        fn name(&self) -> &str { "stop-on-two" }
        fn health_check(&self) -> Result<(), String> { Ok(()) }
        fn iterate(&mut self, _p: &str) -> Result<IterationResult, String> {
            let mut g = self.iter.lock().unwrap();
            *g += 1;
            let stop = if *g >= 2 { Some("qa_pass".to_string()) } else { None };
            Ok(IterationResult {
                success: true,
                summary: format!("iter {}", *g),
                key_changes_made: vec![],
                key_learnings: vec![],
                stop_signal: stop,
                token_usage: TokenUsage::default(),
                agent_name: "stop-on-two".into(),
            })
        }
        fn abort(&mut self) -> Result<(), String> { Ok(()) }
    }
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::GatePass("qa".into()));
    let mut backend = StopOnTwo { iter: Arc::new(Mutex::new(0)) };
    let steps = orch.run(&mut backend, "prompt").unwrap();
    assert_eq!(steps.len(), 2, "should stop after 2 iterations");
    assert!(steps[1].stopped);
    assert!(steps[1].stop_reason.contains("qa_pass"));
}

// ---- AC-048 stop_when: max iterations ----

#[test]
fn tc048_stop_when_max_iterations() {
    struct AlwaysGo;
    impl AgentBackend for AlwaysGo {
        fn name(&self) -> &str { "always-go" }
        fn health_check(&self) -> Result<(), String> { Ok(()) }
        fn iterate(&mut self, _p: &str) -> Result<IterationResult, String> {
            Ok(IterationResult {
                success: true, summary: "go".into(), key_changes_made: vec![], key_learnings: vec![],
                stop_signal: None, token_usage: TokenUsage::default(), agent_name: "always-go".into(),
            })
        }
        fn abort(&mut self) -> Result<(), String> { Ok(()) }
    }
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(3));
    let mut backend = AlwaysGo;
    let steps = orch.run(&mut backend, "prompt").unwrap();
    assert_eq!(steps.len(), 3, "should hit max 3 iterations");
    assert!(!steps[2].stopped, "max iterations does not set stopped flag");
}

// ---- AC-049 orchestrator must not emit verdicts ----

#[test]
fn tc049_orchestrator_no_verdict_in_steps() {
    struct Dummy;
    impl AgentBackend for Dummy {
        fn name(&self) -> &str { "dummy" }
        fn health_check(&self) -> Result<(), String> { Ok(()) }
        fn iterate(&mut self, _p: &str) -> Result<IterationResult, String> {
            Ok(IterationResult {
                success: true, summary: "step".into(), key_changes_made: vec![], key_learnings: vec![],
                stop_signal: Some("qa_pass".into()), token_usage: TokenUsage::default(), agent_name: "dummy".into(),
            })
        }
        fn abort(&mut self) -> Result<(), String> { Ok(()) }
    }
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::GatePass("qa".into()));
    let mut backend = Dummy;
    let steps = orch.run(&mut backend, "prompt").unwrap();
    // AC-049: orchestrator must not output QA pass / release_ready / feature_complete
    for s in &steps {
        assert!(!s.result.summary.to_lowercase().contains("release_ready"));
        assert!(!s.result.summary.to_lowercase().contains("feature_complete"));
        // stop_signal qa_pass is a stop condition, not a verdict emitted by orchestrator
    }
}

// ---- AC-102 planner_review single-process fallback ----

#[test]
fn tc102_planner_review_fallback_isomorphic_fields() {
    let r = PlannerReviewResult::single_process_fallback(
        vec![beacon_orchestrator::Finding {
            severity: "P1".into(),
            title: "gap".into(),
            detail: "missing x".into(),
        }],
        "synthesis text".into(),
    );
    // AC-102: must produce v1.6 isomorphic fields
    assert!(serde_json::to_string(&r).unwrap().contains("reviewer_lanes"));
    assert!(serde_json::to_string(&r).unwrap().contains("findings"));
    assert!(serde_json::to_string(&r).unwrap().contains("synthesis"));
    assert!(serde_json::to_string(&r).unwrap().contains("execution_mode"));
    assert!(serde_json::to_string(&r).unwrap().contains("fallback_reason"));
    assert!(r.runtime_evidence_only);
    // must NOT claim parallel execution
    assert!(!r.execution_mode.contains("parallel"));
    assert!(!r.execution_mode.contains("subagent"));
}
