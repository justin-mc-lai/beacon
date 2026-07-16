//! AC-043 CodexBackend multi-round true integration.

use beacon_core::agent::AgentBackend;
use beacon_core::RunStatus;
use beacon_orchestrator::{CodexBackend, Orchestrator, StopWhen};
use beacon_store::{ArtifactDao, BeaconStore, FeatureDao, ProjectDao, RunDao};
use std::io::Write;
use std::os::unix::fs::PermissionsExt;

fn multi_round_harness() -> (tempfile::TempDir, std::path::PathBuf) {
    let dir = tempfile::tempdir().unwrap();
    let script = dir.path().join("codex_multi_round.sh");
    let body = r#"#!/usr/bin/env bash
set -euo pipefail
iter="${CODEX_BACKEND_ITER:-1}"
printf '%s\n' "{\"success\":true,\"summary\":\"codex multi-round iter ${iter}\",\"key_changes_made\":[\"change-iter-${iter}\"],\"key_learnings\":[\"learn-${iter}\"],\"stop_signal\":null,\"token_usage\":{\"input_tokens\":$((iter*10)),\"output_tokens\":$((iter*11))},\"agent_name\":\"codex-harness\"}"
"#;
    let mut f = std::fs::File::create(&script).unwrap();
    f.write_all(body.as_bytes()).unwrap();
    let mut perms = std::fs::metadata(&script).unwrap().permissions();
    perms.set_mode(0o755);
    std::fs::set_permissions(&script, perms).unwrap();
    (dir, script)
}

#[test]
fn tc043_codex_backend_multi_iterate_same_run() {
    let (_dir, script) = multi_round_harness();
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/codex-ac043", "codex").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "frozen", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "codex", RunStatus::Running).unwrap();

    let mut backend = CodexBackend::with_command(
        "codex",
        vec![script.to_str().unwrap().to_string()],
        3,
    );
    backend.health_check().expect("harness health");

    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(3));
    let steps = orch.run(&mut backend, "implement AC-043").expect("run");
    assert!(steps.len() >= 2, "AC-043 requires ≥2 iterates, got {}", steps.len());
    assert_eq!(steps.len(), 3);
    assert_ne!(steps[0].result.summary, steps[1].result.summary);
    assert!(steps[0].result.summary.contains("iter 1"));
    assert!(steps[1].result.summary.contains("iter 2"));
    assert_eq!(steps[0].result.agent_name, "codex-harness");

    let arts = ArtifactDao::list_for_feature(conn, fid).unwrap();
    let iter_arts: Vec<_> = arts.iter().filter(|a| a.kind == "iteration_result").collect();
    assert!(iter_arts.len() >= 2, "expected ≥2 artifact_refs, got {}", iter_arts.len());
    for a in &iter_arts {
        assert!(a.path.starts_with('/'), "abs_path required, got {}", a.path);
        assert!(std::path::Path::new(&a.path).exists(), "missing {}", a.path);
    }
}

#[test]
fn tc043_codex_backend_not_single_shot_fixture() {
    let (_dir, script) = multi_round_harness();
    let store = BeaconStore::open_in_memory().unwrap();
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/codex-ac043b", "codex").unwrap();
    let fid = FeatureDao::insert(conn, pid, "demo", "v2.0.0", "frozen", None).unwrap();
    let run_id = RunDao::insert(conn, fid, "codex", RunStatus::Running).unwrap();
    let mut backend =
        CodexBackend::with_command("codex", vec![script.to_str().unwrap().to_string()], 2);
    let mut orch = Orchestrator::new(&store, run_id, StopWhen::MaxIterations(2));
    let steps = orch.run(&mut backend, "round").unwrap();
    assert_eq!(steps[0].result.key_changes_made[0], "change-iter-1");
    assert_eq!(steps[1].result.key_changes_made[0], "change-iter-2");
}

#[test]
fn tc043_codex_binary_health_if_present() {
    if which_codex().is_none() {
        eprintln!("codex binary not on PATH; skipping live health probe");
        return;
    }
    let backend = CodexBackend::new(1);
    backend.health_check().expect("codex --version should succeed");
}

fn which_codex() -> Option<std::path::PathBuf> {
    std::env::var_os("PATH").and_then(|paths| {
        for dir in std::env::split_paths(&paths) {
            let p = dir.join("codex");
            if p.is_file() {
                return Some(p);
            }
        }
        None
    })
}
