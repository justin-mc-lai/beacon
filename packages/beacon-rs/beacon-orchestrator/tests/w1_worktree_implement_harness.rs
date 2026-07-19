//! W1 integration: real git worktree + ImplementHarness one iteration (AC-099/100/042).

use beacon_core::agent::AgentBackend;
use beacon_orchestrator::{
    admit_workspace, resolve_worktree, run_one_implement_iteration, ImplementHarnessBackend,
    GitWorktreeMode, WorktreeResolveRequest, WorkspaceAdmissionRequest, REASON_ILLEGAL_MODE_COMBO,
};
use std::path::{Path, PathBuf};
use std::process::Command;

fn init_repo(dir: &Path) {
    assert!(Command::new("git")
        .args(["init"])
        .current_dir(dir)
        .status()
        .unwrap()
        .success());
    let _ = Command::new("git")
        .args(["config", "user.email", "w1@test.local"])
        .current_dir(dir)
        .status();
    let _ = Command::new("git")
        .args(["config", "user.name", "w1-test"])
        .current_dir(dir)
        .status();
    // default branch main for determinism
    let _ = Command::new("git")
        .args(["checkout", "-b", "main"])
        .current_dir(dir)
        .status();
    std::fs::write(dir.join("README.md"), "w1 fixture\n").unwrap();
    assert!(Command::new("git")
        .args(["add", "README.md"])
        .current_dir(dir)
        .status()
        .unwrap()
        .success());
    assert!(Command::new("git")
        .args(["commit", "-m", "init"])
        .current_dir(dir)
        .status()
        .unwrap()
        .success());
}

/// TC-W1-001 / AC-099: real git worktree exists after materialize.
#[test]
fn tc099_real_git_worktree() {
    let dir = tempfile::tempdir().unwrap();
    init_repo(dir.path());
    let r = resolve_worktree(&WorktreeResolveRequest {
        project_root: dir.path().to_path_buf(),
        mode: GitWorktreeMode::Worktree,
        run_id: "tc099".into(),
        feature_slug: "loom-w1".into(),
        isolated: false,
        materialize: true,
        base_ref: None,
    });
    assert!(!r.blocked, "blocked: {:?}", r);
    assert!(r.git_worktree_added);
    let wt = PathBuf::from(&r.admitted_worktree);
    assert!(wt.is_dir());
    assert!(
        wt.join(".git").is_file(),
        "must be git worktree (gitdir file), not mkdir-only"
    );
    // list worktrees should include path
    let out = Command::new("git")
        .args(["worktree", "list", "--porcelain"])
        .current_dir(dir.path())
        .output()
        .unwrap();
    let text = String::from_utf8_lossy(&out.stdout);
    assert!(
        text.contains(wt.file_name().unwrap().to_str().unwrap())
            || text.contains(&r.admitted_worktree),
        "git worktree list missing path: {text}"
    );
}

/// TC-W1-000 / AC-042: IterationResult schema from implement harness.
#[test]
fn iteration_result_schema_from_harness() {
    let dir = tempfile::tempdir().unwrap();
    init_repo(dir.path());
    let r = resolve_worktree(&WorktreeResolveRequest {
        project_root: dir.path().to_path_buf(),
        mode: GitWorktreeMode::CurrentBranch,
        run_id: "tc042".into(),
        feature_slug: "schema".into(),
        isolated: false,
        materialize: false,
        base_ref: None,
    });
    assert!(!r.blocked);
    let admit = admit_workspace(&WorkspaceAdmissionRequest {
        run_id: "tc042".into(),
        caller_cwd: r.admitted_worktree.clone(),
        target_project_root: r.project_root.clone(),
        worktree: Some(r.admitted_worktree.clone()),
        branch: r.branch.clone(),
        allow_cwd_as_root: true,
    });
    let bc = admit.branch_context.expect("bc");
    let mut backend = ImplementHarnessBackend::try_new(bc, None).unwrap();
    let result = backend.iterate("schema check").unwrap();
    let json = serde_json::to_value(&result).unwrap();
    for key in [
        "success",
        "summary",
        "key_changes_made",
        "key_learnings",
        "token_usage",
        "agent_name",
    ] {
        assert!(json.get(key).is_some(), "missing field {key}");
    }
}

/// TC-W1-002 / AC-100: ImplementHarness one real iteration in admitted worktree.
#[test]
fn tc100_implement_harness_one_iter() {
    let dir = tempfile::tempdir().unwrap();
    init_repo(dir.path());
    let wt = resolve_worktree(&WorktreeResolveRequest {
        project_root: dir.path().to_path_buf(),
        mode: GitWorktreeMode::Worktree,
        run_id: "tc100".into(),
        feature_slug: "impl".into(),
        isolated: false,
        materialize: true,
        base_ref: None,
    });
    assert!(!wt.blocked, "{:?}", wt);
    let admit = admit_workspace(&WorkspaceAdmissionRequest {
        run_id: "tc100".into(),
        caller_cwd: wt.admitted_worktree.clone(),
        target_project_root: dir.path().to_string_lossy().to_string(),
        worktree: Some(wt.admitted_worktree.clone()),
        branch: wt.branch.clone(),
        allow_cwd_as_root: true,
    });
    assert!(!admit.blocked);
    let bc = admit.branch_context.unwrap();
    assert_eq!(bc.admitted_worktree, wt.admitted_worktree);
    let (result, refs) = run_one_implement_iteration(bc, "one implement round").unwrap();
    assert!(result.success);
    assert_eq!(result.agent_name, "implement-harness");
    assert!(!result.key_changes_made.is_empty());
    assert!(!refs.is_empty());
    for path in &refs {
        assert!(
            Path::new(path).exists(),
            "artifact missing: {path}"
        );
    }
    // Not a subprocess echo fake: learnings prove harness backend
    assert!(result
        .key_learnings
        .iter()
        .any(|l| l.contains("implement_harness_is_not_subprocess_echo")));
}

/// TC-W1-003 / AC-099: illegal current-branch + isolated fail-closed.
#[test]
fn tc099_illegal_combo() {
    let dir = tempfile::tempdir().unwrap();
    init_repo(dir.path());
    let r = resolve_worktree(&WorktreeResolveRequest {
        project_root: dir.path().to_path_buf(),
        mode: GitWorktreeMode::CurrentBranch,
        run_id: "bad".into(),
        feature_slug: "x".into(),
        isolated: true,
        materialize: true,
        base_ref: None,
    });
    assert!(r.blocked);
    assert_eq!(r.reason_code, REASON_ILLEGAL_MODE_COMBO);
}

/// Legal walk: current-branch + run-branch without isolated.
#[test]
fn tc_w1_legal_modes_walk() {
    let dir = tempfile::tempdir().unwrap();
    init_repo(dir.path());
    for mode in [GitWorktreeMode::CurrentBranch, GitWorktreeMode::RunBranch] {
        let r = resolve_worktree(&WorktreeResolveRequest {
            project_root: dir.path().to_path_buf(),
            mode,
            run_id: "legal".into(),
            feature_slug: "walk".into(),
            isolated: false,
            materialize: true,
            base_ref: None,
        });
        assert!(!r.blocked, "mode {:?} blocked {:?}", mode, r);
        assert!(!r.admitted_worktree.is_empty());
    }
}
