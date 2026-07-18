//! BranchContext.v1 — workspace/branch admission contract (AC-128 / TC-128).

use serde::{Deserialize, Serialize};

pub const SCHEMA_BRANCH_CONTEXT: &str = "BranchContext.v1";
pub const REASON_BRANCH_CONTEXT_MISSING: &str = "branch_context_missing";
pub const REASON_CWD_ROOT_MISMATCH: &str = "branch_context_cwd_root_mismatch";
pub const REASON_PROTECTED_PATH_WRITE: &str = "branch_context_protected_path_write";
pub const REASON_ADMISSION_MISSING: &str = "workspace_admission_missing";
pub const REASON_CANONICAL_BRANCH_MISMATCH: &str = "truth_canonical_branch_mismatch";

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BranchContext {
    pub schema: String,
    pub caller_cwd: String,
    pub target_project_root: String,
    pub admitted_worktree: String,
    pub branch: String,
    pub is_canonical_truth_branch: bool,
    pub dirty_policy: String,
    pub protected_paths: Vec<String>,
    pub admitted: bool,
    pub run_id: String,
    pub topology: String,
}

impl BranchContext {
    pub fn new(
        run_id: impl Into<String>,
        caller_cwd: impl Into<String>,
        target_project_root: impl Into<String>,
        admitted_worktree: impl Into<String>,
        branch: impl Into<String>,
    ) -> Self {
        let branch = branch.into();
        let is_canonical = matches!(branch.as_str(), "main" | "master");
        Self {
            schema: SCHEMA_BRANCH_CONTEXT.into(),
            caller_cwd: caller_cwd.into(),
            target_project_root: target_project_root.into(),
            admitted_worktree: admitted_worktree.into(),
            branch,
            is_canonical_truth_branch: is_canonical,
            dirty_policy: "fail_closed_on_protected".into(),
            protected_paths: vec![
                "docs/beacon".into(),
                ".machine".into(),
            ],
            admitted: false,
            run_id: run_id.into(),
            topology: "single_repo".into(),
        }
    }

    pub fn mark_admitted(mut self) -> Self {
        self.admitted = true;
        self
    }

    /// Required fields present (schema contract).
    pub fn validate_schema(&self) -> Result<(), String> {
        if self.schema != SCHEMA_BRANCH_CONTEXT {
            return Err(format!("expected {SCHEMA_BRANCH_CONTEXT}"));
        }
        for (name, val) in [
            ("caller_cwd", &self.caller_cwd),
            ("target_project_root", &self.target_project_root),
            ("admitted_worktree", &self.admitted_worktree),
            ("branch", &self.branch),
            ("run_id", &self.run_id),
        ] {
            if val.trim().is_empty() {
                return Err(format!("{REASON_BRANCH_CONTEXT_MISSING}:{name}"));
            }
        }
        Ok(())
    }

    /// Hard gate: write/agent/evidence harness consume admitted context (AC-129).
    pub fn governance_gate(&self, write_path: Option<&str>) -> Result<(), String> {
        self.validate_schema()?;
        if !self.admitted {
            return Err(REASON_ADMISSION_MISSING.into());
        }
        // cwd may differ from root when worktree is admitted; target must equal admitted worktree root policy
        if self.admitted_worktree != self.target_project_root
            && !self.admitted_worktree.starts_with(&self.target_project_root)
            && !self.target_project_root.starts_with(&self.admitted_worktree)
        {
            // allow relative mismatch only when admitted worktree is explicit
            if self.caller_cwd == self.target_project_root && self.admitted_worktree.is_empty() {
                return Err(REASON_CWD_ROOT_MISMATCH.into());
            }
        }
        if let Some(path) = write_path {
            for prot in &self.protected_paths {
                if path.contains(prot) && !self.is_canonical_truth_branch {
                    // feature branch writing protected truth paths blocked unless consumption-only
                    if path.contains("truth.md") || path.contains("/.machine/") {
                        return Err(format!("{REASON_PROTECTED_PATH_WRITE}:{path}"));
                    }
                }
            }
        }
        Ok(())
    }

    /// Truth write only on main/master (AC-136).
    pub fn canonical_truth_write_gate(&self) -> Result<(), String> {
        self.validate_schema()?;
        if !self.is_canonical_truth_branch {
            return Err(REASON_CANONICAL_BRANCH_MISMATCH.into());
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn schema_and_admission() {
        let mut ctx = BranchContext::new("r1", "/cwd", "/proj", "/proj", "main");
        assert!(ctx.validate_schema().is_ok());
        assert!(ctx.governance_gate(None).is_err());
        ctx = ctx.mark_admitted();
        assert!(ctx.governance_gate(None).is_ok());
        assert!(ctx.canonical_truth_write_gate().is_ok());
    }

    #[test]
    fn feature_branch_blocks_truth_write() {
        let ctx = BranchContext::new("r1", "/cwd", "/proj", "/proj", "feature/x").mark_admitted();
        assert!(ctx.canonical_truth_write_gate().is_err());
        assert!(ctx
            .governance_gate(Some("docs/beacon/v2.0.0/features/x/truth.md"))
            .is_err());
    }
}
