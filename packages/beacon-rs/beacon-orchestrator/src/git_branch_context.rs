//! Real git collection for BranchContext.v1 (AC-128 / AC-171 partial).

use crate::workspace_admission::{admit_workspace, WorkspaceAdmissionRequest, WorkspaceAdmissionResult};
use beacon_core::branch_context::BranchContext;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GitProbe {
    pub ok: bool,
    pub branch: String,
    pub is_dirty: bool,
    pub root: String,
    pub head: String,
    pub error: String,
}

pub fn probe_git(project_root: &Path) -> GitProbe {
    let root = rev_parse(project_root, &["--show-toplevel"]).unwrap_or_default();
    let branch = rev_parse(project_root, &["--abbrev-ref", "HEAD"]).unwrap_or_else(|_| "HEAD".into());
    let head = rev_parse(project_root, &["HEAD"]).unwrap_or_default();
    let dirty = Command::new("git")
        .args(["status", "--porcelain"])
        .current_dir(project_root)
        .output()
        .map(|o| !String::from_utf8_lossy(&o.stdout).trim().is_empty())
        .unwrap_or(false);
    let ok = !root.is_empty();
    GitProbe {
        ok,
        branch,
        is_dirty: dirty,
        root,
        head,
        error: if ok {
            String::new()
        } else {
            "git_probe_failed".into()
        },
    }
}

fn rev_parse(cwd: &Path, args: &[&str]) -> Result<String, String> {
    let mut cmd = Command::new("git");
    cmd.arg("rev-parse").args(args).current_dir(cwd);
    let out = cmd.output().map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(String::from_utf8_lossy(&out.stderr).to_string());
    }
    Ok(String::from_utf8_lossy(&out.stdout).trim().to_string())
}

/// Collect BranchContext from real git + workspace admission.
pub fn collect_branch_context(
    run_id: &str,
    caller_cwd: &Path,
    project_root: &Path,
    worktree: Option<&Path>,
) -> WorkspaceAdmissionResult {
    let probe = probe_git(project_root);
    if !probe.ok {
        return WorkspaceAdmissionResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: "gitscope_branch_context_parity_failed".into(),
            branch_context: None,
        };
    }
    let req = WorkspaceAdmissionRequest {
        run_id: run_id.into(),
        caller_cwd: caller_cwd.to_string_lossy().to_string(),
        target_project_root: if probe.root.is_empty() {
            project_root.to_string_lossy().to_string()
        } else {
            probe.root.clone()
        },
        worktree: worktree.map(|p| p.to_string_lossy().to_string()),
        branch: probe.branch.clone(),
        allow_cwd_as_root: true,
    };
    let mut result = admit_workspace(&req);
    if let Some(ref mut bc) = result.branch_context {
        if probe.is_dirty {
            bc.dirty_policy = "dirty_detected_fail_closed_on_protected".into();
        }
        // topology heuristic
        let gitfiles = PathBuf::from(&bc.target_project_root).join(".git");
        if gitfiles.is_file() {
            bc.topology = "worktree_or_linked".into();
        }
    }
    result
}

/// Convenience: context only if admitted.
pub fn try_branch_context(
    run_id: &str,
    project_root: &Path,
) -> Result<BranchContext, String> {
    let cwd = std::env::current_dir().unwrap_or_else(|_| project_root.to_path_buf());
    let r = collect_branch_context(run_id, &cwd, project_root, None);
    if r.blocked {
        return Err(r.reason_code);
    }
    r.branch_context.ok_or_else(|| "branch_context_missing".into())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn probe_this_repo() {
        // run from packages/beacon-rs in tests — find repo root via CARGO_MANIFEST_DIR
        let here = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        let root = here
            .ancestors()
            .find(|p| p.join(".git").exists() || p.join(".git").is_file())
            .unwrap_or(&here)
            .to_path_buf();
        let probe = probe_git(&root);
        // In this monorepo we expect git
        assert!(probe.ok, "{:?}", probe);
        assert!(!probe.branch.is_empty());
    }
}
