//! W2: AC-105/106 external stop_when (maker ≠ checker).

use beacon_core::agent::{AgentBackend, IterationResult, TokenUsage};
use beacon_core::RunStatus;
use beacon_orchestrator::{
    map_agent_name, AllowStopChecker, DenyStopChecker, Orchestrator, StopWhen,
    REASON_STOP_WHEN_UNVERIFIED,
};
use beacon_store::{BeaconStore, FeatureDao, ProjectDao, RunDao};

struct SelfStopBackend {
    n: u32,
}

impl AgentBackend for SelfStopBackend {
    fn name(&self) -> &str {
        "self-stop"
    }
    fn health_check(&self) -> Result<(), String> {
        Ok(())
    }
    fn iterate(&mut self, _p: &str) -> Result<IterationResult, String> {
        self.n += 1;
        Ok(IterationResult {
            success: true,
            summary: format!("iter {}", self.n),
            key_changes_made: vec![],
            key_learnings: vec![],
            stop_signal: Some("gate_pass".into()),
            token_usage: TokenUsage::default(),
            agent_name: "self-stop".into(),
        })
    }
    fn abort(&mut self) -> Result<(), String> {
        Ok(())
    }
}

fn mk_run() -> (BeaconStore, i64) {
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "draft", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "test", RunStatus::Running).unwrap();
    (store, run_id)
}

#[test]
fn tc106_self_stop_unverified() {
    let (store, run_id) = mk_run();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(3));
    let mut backend = SelfStopBackend { n: 0 };
    let mut deny = DenyStopChecker;
    let steps = orch
        .run_with_external_stop(&mut backend, "go", &mut deny)
        .unwrap();
    assert_eq!(steps.len(), 3, "must continue despite stop_signal");
    assert!(steps.iter().take(2).all(|s| s.stop_unverified));
    assert!(steps
        .iter()
        .take(2)
        .all(|s| s.stop_reason == REASON_STOP_WHEN_UNVERIFIED));
    assert!(steps.last().unwrap().stopped);
    assert_eq!(steps.last().unwrap().stop_reason, "max_iterations");
}

#[test]
fn tc106_external_stop() {
    let (store, run_id) = mk_run();
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(10));
    let mut backend = SelfStopBackend { n: 0 };
    let mut allow = AllowStopChecker {
        label: "fixture".into(),
    };
    let steps = orch
        .run_with_external_stop(&mut backend, "go", &mut allow)
        .unwrap();
    assert_eq!(steps.len(), 1);
    assert!(steps[0].stopped);
    assert!(!steps[0].stop_unverified);
}

#[test]
fn tc105_agent_map() {
    assert_eq!(map_agent_name("codex").unwrap(), "codex");
    assert_eq!(map_agent_name("subprocess").unwrap(), "subprocess");
    assert_eq!(map_agent_name("acp:target").unwrap(), "acp:target");
    assert!(map_agent_name("nope").is_err());
}
