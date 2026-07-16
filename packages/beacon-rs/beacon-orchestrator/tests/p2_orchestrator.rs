//! P2 orchestrator integration tests — AC-044 (subprocess real iteration),
//! AC-048/AC-106 (stop_when + maker≠checker), AC-102 (planner_review fallback), AC-040.

use beacon_core::agent::{AgentBackend, IterationResult, TokenUsage};
use beacon_core::RunStatus;
use beacon_orchestrator::{Orchestrator, PlannerReviewResult, StopWhen, SubprocessBackend};
use beacon_store::{BeaconStore, FeatureDao, ProjectDao, RunDao};
use std::io::Write;
use std::sync::{Arc, Mutex};

#[test]
fn tc040_orchestrator_status_reads_run() {
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    let orch = Orchestrator::new(&store, run_id, StopWhen::Never);
    assert_eq!(orch.status().unwrap(), "Running");
}

#[test]
fn tc044_subprocess_backend_one_real_iteration() {
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
    let mut backend =
        SubprocessBackend::new("subprocess-test", vec![script.to_str().unwrap().to_string()], 1);
    backend.health_check().unwrap();
    let result = backend.iterate("do something").unwrap();
    assert!(result.success);
    assert_eq!(result.summary, "did one iteration");
    assert_eq!(result.agent_name, "subprocess-test");
}

/// AC-106: agent qa_pass alone must NOT stop the loop (maker≠checker).
#[test]
fn tc106_agent_stop_signal_alone_does_not_stop() {
    struct StopOnTwo {
        iter: Arc<Mutex<u32>>,
    }
    impl AgentBackend for StopOnTwo {
        fn name(&self) -> &str {
            "stop-on-two"
        }
        fn health_check(&self) -> Result<(), String> {
            Ok(())
        }
        fn iterate(&mut self, _p: &str) -> Result<IterationResult, String> {
            let mut g = self.iter.lock().unwrap();
            *g += 1;
            let stop = if *g >= 2 {
                Some("qa_pass".to_string())
            } else {
                None
            };
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
        fn abort(&mut self) -> Result<(), String> {
            Ok(())
        }
    }
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    // GatePass without external notify → runs until safety max, but we use MaxIterations(4)
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(4));
    let mut backend = StopOnTwo {
        iter: Arc::new(Mutex::new(0)),
    };
    let steps = orch.run(&mut backend, "prompt").unwrap();
    assert_eq!(steps.len(), 4, "must not early-stop on agent qa_pass");
    assert!(steps[1].stop_reason.contains("stop_when_unverified"));
    assert!(steps[3].stopped);
    assert_eq!(steps[3].stop_reason, "max_iterations");
}

/// AC-048 + AC-106: external verified gate stop.
#[test]
fn tc048_external_gate_pass_stops() {
    struct AlwaysGo;
    impl AgentBackend for AlwaysGo {
        fn name(&self) -> &str {
            "always-go"
        }
        fn health_check(&self) -> Result<(), String> {
            Ok(())
        }
        fn iterate(&mut self, _p: &str) -> Result<IterationResult, String> {
            Ok(IterationResult {
                success: true,
                summary: "go".into(),
                key_changes_made: vec![],
                key_learnings: vec![],
                stop_signal: None,
                token_usage: TokenUsage::default(),
                agent_name: "always-go".into(),
            })
        }
        fn abort(&mut self) -> Result<(), String> {
            Ok(())
        }
    }
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::GatePass("qa".into()));
    // Simulate external checker after construction
    orch.notify_external_gate_pass();
    let mut backend = AlwaysGo;
    let steps = orch.run(&mut backend, "prompt").unwrap();
    assert_eq!(steps.len(), 1);
    assert!(steps[0].stopped);
    assert!(steps[0].stop_reason.contains("external_verified"));
}

#[test]
fn tc048_stop_when_max_iterations() {
    struct AlwaysGo;
    impl AgentBackend for AlwaysGo {
        fn name(&self) -> &str {
            "always-go"
        }
        fn health_check(&self) -> Result<(), String> {
            Ok(())
        }
        fn iterate(&mut self, _p: &str) -> Result<IterationResult, String> {
            Ok(IterationResult {
                success: true,
                summary: "go".into(),
                key_changes_made: vec![],
                key_learnings: vec![],
                stop_signal: None,
                token_usage: TokenUsage::default(),
                agent_name: "always-go".into(),
            })
        }
        fn abort(&mut self) -> Result<(), String> {
            Ok(())
        }
    }
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(3));
    let mut backend = AlwaysGo;
    let steps = orch.run(&mut backend, "prompt").unwrap();
    assert_eq!(steps.len(), 3);
    assert!(steps[2].stopped);
    assert_eq!(steps[2].stop_reason, "max_iterations");
}

#[test]
fn tc049_orchestrator_no_verdict_in_steps() {
    struct Dummy;
    impl AgentBackend for Dummy {
        fn name(&self) -> &str {
            "dummy"
        }
        fn health_check(&self) -> Result<(), String> {
            Ok(())
        }
        fn iterate(&mut self, _p: &str) -> Result<IterationResult, String> {
            Ok(IterationResult {
                success: true,
                summary: "step".into(),
                key_changes_made: vec![],
                key_learnings: vec![],
                stop_signal: Some("qa_pass".into()),
                token_usage: TokenUsage::default(),
                agent_name: "dummy".into(),
            })
        }
        fn abort(&mut self) -> Result<(), String> {
            Ok(())
        }
    }
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(2));
    let mut backend = Dummy;
    let steps = orch.run(&mut backend, "prompt").unwrap();
    for s in &steps {
        assert!(!s.result.summary.to_lowercase().contains("release_ready"));
        assert!(!s.result.summary.to_lowercase().contains("feature_complete"));
    }
}

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
    let s = serde_json::to_string(&r).unwrap();
    assert!(s.contains("reviewer_lanes"));
    assert!(s.contains("findings"));
    assert!(s.contains("synthesis"));
    assert!(s.contains("execution_mode"));
    assert!(s.contains("fallback_reason"));
    assert!(r.runtime_evidence_only);
    assert!(!r.execution_mode.contains("parallel"));
}
