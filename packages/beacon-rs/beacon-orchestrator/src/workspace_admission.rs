//! Workspace admission → BranchContext.v1 (AC-128 / TC-128).

use beacon_core::branch_context::{
    BranchContext, REASON_ADMISSION_MISSING, REASON_CWD_ROOT_MISMATCH,
};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkspaceAdmissionRequest {
    pub run_id: String,
    pub caller_cwd: String,
    pub target_project_root: String,
    pub worktree: Option<String>,
    pub branch: String,
    pub allow_cwd_as_root: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkspaceAdmissionResult {
    pub blocked: bool,
    pub status: String,
    pub reason_code: String,
    pub branch_context: Option<BranchContext>,
}

/// Admit a workspace and produce BranchContext.v1.
/// Policy: if worktree provided, admitted_worktree = worktree; else target_project_root.
/// If caller_cwd is used as sole target without explicit project root → mismatch blocked (TC-N12).
pub fn admit_workspace(req: &WorkspaceAdmissionRequest) -> WorkspaceAdmissionResult {
    let target = PathBuf::from(&req.target_project_root);
    let cwd = PathBuf::from(&req.caller_cwd);

    // Fail-closed: inferring target solely from cwd when roots differ and no explicit worktree
    if !req.allow_cwd_as_root
        && req.worktree.is_none()
        && normalize(&cwd) != normalize(&target)
        && req.target_project_root.trim().is_empty()
    {
        return WorkspaceAdmissionResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_CWD_ROOT_MISMATCH.into(),
            branch_context: None,
        };
    }

    if req.target_project_root.trim().is_empty() {
        return WorkspaceAdmissionResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_ADMISSION_MISSING.into(),
            branch_context: None,
        };
    }

    let admitted_wt = req
        .worktree
        .clone()
        .unwrap_or_else(|| req.target_project_root.clone());

    let ctx = BranchContext::new(
        &req.run_id,
        &req.caller_cwd,
        &req.target_project_root,
        &admitted_wt,
        &req.branch,
    )
    .mark_admitted();

    if let Err(code) = ctx.validate_schema() {
        return WorkspaceAdmissionResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: code,
            branch_context: None,
        };
    }

    WorkspaceAdmissionResult {
        blocked: false,
        status: "pass".into(),
        reason_code: String::new(),
        branch_context: Some(ctx),
    }
}

fn normalize(p: &Path) -> String {
    p.to_string_lossy().replace('\\', "/")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn admit_produces_branch_context() {
        let r = admit_workspace(&WorkspaceAdmissionRequest {
            run_id: "r1".into(),
            caller_cwd: "/home/u/proj".into(),
            target_project_root: "/home/u/proj".into(),
            worktree: None,
            branch: "main".into(),
            allow_cwd_as_root: true,
        });
        assert!(!r.blocked);
        let bc = r.branch_context.unwrap();
        assert!(bc.admitted);
        assert_eq!(bc.schema, "BranchContext.v1");
        assert!(bc.is_canonical_truth_branch);
    }

    #[test]
    fn empty_root_blocked() {
        let r = admit_workspace(&WorkspaceAdmissionRequest {
            run_id: "r1".into(),
            caller_cwd: "/tmp".into(),
            target_project_root: "".into(),
            worktree: None,
            branch: "main".into(),
            allow_cwd_as_root: false,
        });
        assert!(r.blocked);
    }
}
