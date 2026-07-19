//! AC-099 worktree modes + AC-045/046 backend integration.

use beacon_core::agent::AgentBackend;
use beacon_core::RunStatus;
use beacon_orchestrator::{
    ensure_worktree_dir, resolve_worktree_mode, AcpBackend, ClaudeBackend, Orchestrator, StopWhen,
    WorktreeMode, REASON_WORKTREE_ILLEGAL_COMBO,
};
use beacon_store::{ArtifactDao, BeaconStore, FeatureDao, ProjectDao, RunDao};
use std::io::Write;
use std::os::unix::fs::PermissionsExt;

fn json_harness(label: &str) -> (tempfile::TempDir, std::path::PathBuf) {
    let dir = tempfile::tempdir().unwrap();
    let script = dir.path().join(format!("{label}_harness.sh"));
    let body = r#"#!/usr/bin/env bash
set -euo pipefail
iter="${AGENT_BACKEND_ITER:-1}"
name="${AGENT_BACKEND_NAME:-harness}"
printf '%s\n' "{\"success\":true,\"summary\":\"${name} iter ${iter}\",\"key_changes_made\":[\"${name}-change-${iter}\"],\"key_learnings\":[],\"stop_signal\":null,\"token_usage\":{\"input_tokens\":3,\"output_tokens\":4},\"agent_name\":\"${name}\"}"
"#;
    let mut f = std::fs::File::create(&script).unwrap();
    f.write_all(body.as_bytes()).unwrap();
    let mut perms = std::fs::metadata(&script).unwrap().permissions();
    perms.set_mode(0o755);
    std::fs::set_permissions(&script, perms).unwrap();
    (dir, script)
}

#[test]
fn tc099_worktree_modes_all_paths() {
    let d = tempfile::tempdir().unwrap();
    for mode in [
        WorktreeMode::Worktree,
        WorktreeMode::CurrentBranch,
        WorktreeMode::RunBranch,
    ] {
        let plan = resolve_worktree_mode(mode, d.path(), "r99", "main", false, false);
        assert!(!plan.blocked, "{:?}", plan);
        if mode == WorktreeMode::Worktree {
            let p = ensure_worktree_dir(&plan).unwrap();
            assert!(p.exists());
            assert_eq!(plan.harness_cwd, p.to_string_lossy());
        }
    }
}

#[test]
fn tc099_n06_illegal_combo() {
    let d = tempfile::tempdir().unwrap();
    let plan = resolve_worktree_mode(
        WorktreeMode::CurrentBranch,
        d.path(),
        "r",
        "main",
        true,
        false,
    );
    assert!(plan.blocked);
    assert_eq!(plan.reason_code, REASON_WORKTREE_ILLEGAL_COMBO);
}

#[test]
fn tc045_claude_iterate_health_abort() {
    let (_d, script) = json_harness("claude");
    let mut b = ClaudeBackend::with_command("claude", vec![script.to_str().unwrap().into()], 2);
    b.health_check().unwrap();
    let r = b.iterate("x").unwrap();
    assert!(r.success);
    b.abort().unwrap();
    assert!(b.iterate("y").is_err());
}

#[test]
fn tc045_missing_claude_cred_explicit() {
    // Ensure env cleared for this test
    std::env::remove_var("ANTHROPIC_API_KEY");
    std::env::remove_var("CLAUDE_API_KEY");
    match ClaudeBackend::try_live(1) {
        Ok(_) => panic!("expected missing cred"),
        Err(err) => assert!(err.contains("BLOCKED:missing_claude_cred"), "{err}"),
    }
}

#[test]
fn tc045_claude_orchestrator_artifact() {
    let (_d, script) = json_harness("claude");
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/c", "c").unwrap();
    let fid = FeatureDao::insert(conn, pid, "f", "v2.0.0", "frozen", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "claude", RunStatus::Running).unwrap();
    let mut b = ClaudeBackend::with_command("claude", vec![script.to_str().unwrap().into()], 1);
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(1));
    let steps = orch.run(&mut b, "go").unwrap();
    assert_eq!(steps.len(), 1);
    let arts = ArtifactDao::list_for_feature(conn, fid).unwrap();
    assert!(arts.iter().any(|a| a.kind == "iteration_result"));
}

#[test]
fn tc046_acp_target_form() {
    let (_d, script) = json_harness("acp");
    let mut b = AcpBackend::with_command("acp:fixture", vec![script.to_str().unwrap().into()], 1);
    b.health_check().unwrap();
    let r = b.iterate("a").unwrap();
    assert_eq!(r.agent_name, "acp:fixture");
}
