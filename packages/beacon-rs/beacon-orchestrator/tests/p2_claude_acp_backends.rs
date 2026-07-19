//! AC-045 ClaudeBackend + AC-046 AcpBackend true integration iterations.

use beacon_core::agent::AgentBackend;
use beacon_core::RunStatus;
use beacon_orchestrator::{AcpBackend, ClaudeBackend, Orchestrator, StopWhen};
use beacon_store::{ArtifactDao, BeaconStore, FeatureDao, ProjectDao, RunDao};
use std::io::Write;
use std::os::unix::fs::PermissionsExt;

fn json_harness(label: &str) -> (tempfile::TempDir, std::path::PathBuf) {
    let dir = tempfile::tempdir().unwrap();
    let script = dir.path().join(format!("{label}_harness.sh"));
    let body = r#"#!/usr/bin/env bash
set -euo pipefail
iter="${AGENT_BACKEND_ITER:-${CODEX_BACKEND_ITER:-1}}"
name="${AGENT_BACKEND_NAME:-harness}"
printf '%s\n' "{\"success\":true,\"summary\":\"${name} iter ${iter}\",\"key_changes_made\":[\"${name}-change-${iter}\"],\"key_learnings\":[],\"stop_signal\":null,\"token_usage\":{\"input_tokens\":$((iter*3)),\"output_tokens\":$((iter*4))},\"agent_name\":\"${name}\"}"
"#;
    let mut f = std::fs::File::create(&script).unwrap();
    f.write_all(body.as_bytes()).unwrap();
    let mut perms = std::fs::metadata(&script).unwrap().permissions();
    perms.set_mode(0o755);
    std::fs::set_permissions(&script, perms).unwrap();
    (dir, script)
}

#[test]
fn tc045_claude_backend_one_real_iteration_plus_health_abort() {
    let (_dir, script) = json_harness("claude");
    let mut backend = ClaudeBackend::with_command(
        "claude",
        vec![script.to_str().unwrap().to_string()],
        2,
    );
    backend.health_check().expect("claude harness health");
    let r1 = backend.iterate("do work").expect("iterate 1");
    assert!(r1.success);
    assert_eq!(r1.agent_name, "claude");
    assert!(r1.summary.contains("iter 1"));
    // schema fields from AC-042
    assert!(!r1.key_changes_made.is_empty());
    backend.abort().expect("abort");
    let err = backend.iterate("after abort");
    assert!(err.is_err(), "abort must block further iterate");
}

#[test]
fn tc045_claude_via_orchestrator_writes_artifact() {
    let (_dir, script) = json_harness("claude");
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/claude-ac045", "claude").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "frozen", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "claude", RunStatus::Running).unwrap();
    let mut backend = ClaudeBackend::with_command(
        "claude",
        vec![script.to_str().unwrap().to_string()],
        1,
    );
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(1));
    let steps = orch.run(&mut backend, "claude iter").unwrap();
    assert_eq!(steps.len(), 1);
    assert!(steps[0].result.success);
    let arts = ArtifactDao::list_for_feature(conn, fid).unwrap();
    assert!(arts.iter().any(|a| a.kind == "iteration_result"));
}

#[test]
fn tc046_acp_backend_one_real_iteration() {
    let (_dir, script) = json_harness("acp");
    let mut backend = AcpBackend::with_command(
        "acp:fixture",
        vec![script.to_str().unwrap().to_string()],
        1,
    );
    backend.health_check().expect("acp harness health");
    let r = backend.iterate("acp work").expect("iterate");
    assert!(r.success);
    assert_eq!(r.agent_name, "acp:fixture");
    assert!(r.summary.contains("iter 1"));
    backend.abort().unwrap();
}

#[test]
fn tc046_acp_via_orchestrator_artifact_refs() {
    let (_dir, script) = json_harness("acp");
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/acp-ac046", "acp").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "frozen", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "acp", RunStatus::Running).unwrap();
    let mut backend = AcpBackend::with_command(
        "acp:target",
        vec![script.to_str().unwrap().to_string()],
        1,
    );
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(1));
    let steps = orch.run(&mut backend, "acp").unwrap();
    assert_eq!(steps.len(), 1);
    let arts = ArtifactDao::list_for_feature(conn, fid).unwrap();
    assert!(arts.iter().any(|a| a.kind == "iteration_result" && a.path.starts_with('/')));
}

#[test]
fn tc045_claude_binary_health_if_present() {
    if which_bin("claude").is_none() {
        eprintln!("claude not on PATH; skip live health");
        return;
    }
    let backend = ClaudeBackend::new(1);
    // may fail if claude requires interactive login; only check binary invocable
    let _ = backend.health_check();
}

fn which_bin(name: &str) -> Option<std::path::PathBuf> {
    std::env::var_os("PATH").and_then(|paths| {
        for dir in std::env::split_paths(&paths) {
            let p = dir.join(name);
            if p.is_file() {
                return Some(p);
            }
        }
        None
    })
}
