//! Worktree full modes (AC-099 / TC-099 / TC-N06).
//!
//! Modes: worktree | current-branch | run-branch
//! Illegal: current-branch + isolated-worktree simultaneously.

use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

pub const REASON_WORKTREE_ILLEGAL_COMBO: &str = "worktree_illegal_combo";
pub const REASON_WORKTREE_UNKNOWN_MODE: &str = "worktree_unknown_mode";
pub const REASON_WORKTREE_CWD_MISMATCH: &str = "worktree_cwd_mismatch";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum WorktreeMode {
    /// Isolated worktree under project/.loom/worktrees/<id>
    Worktree,
    /// Use caller's current branch in place
    CurrentBranch,
    /// Dedicated run branch (no isolated path)
    RunBranch,
}

impl WorktreeMode {
    pub fn parse(s: &str) -> Result<Self, String> {
        match s.trim().to_ascii_lowercase().as_str() {
            "worktree" | "isolated-worktree" | "isolated" => Ok(WorktreeMode::Worktree),
            "current-branch" | "current_branch" | "current" => Ok(WorktreeMode::CurrentBranch),
            "run-branch" | "run_branch" | "run" => Ok(WorktreeMode::RunBranch),
            other => Err(format!("{REASON_WORKTREE_UNKNOWN_MODE}:{other}")),
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            WorktreeMode::Worktree => "worktree",
            WorktreeMode::CurrentBranch => "current-branch",
            WorktreeMode::RunBranch => "run-branch",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorktreePlan {
    pub mode: WorktreeMode,
    pub project_root: String,
    pub harness_cwd: String,
    pub branch: String,
    pub run_id: String,
    pub isolated: bool,
    pub blocked: bool,
    pub reason_code: String,
}

/// Resolve mode + flags into a plan. Fail-closed on illegal combos.
///
/// `isolated_flag`: caller asked for isolated worktree path.
/// `current_branch_flag`: caller also asked for current-branch semantics.
pub fn resolve_worktree_mode(
    mode: WorktreeMode,
    project_root: &Path,
    run_id: &str,
    branch: &str,
    isolated_flag: bool,
    current_branch_flag: bool,
) -> WorktreePlan {
    let root = project_root.to_string_lossy().to_string();

    // TC-N06: current-branch + isolated-worktree illegal
    let illegal = match mode {
        WorktreeMode::CurrentBranch if isolated_flag => true,
        WorktreeMode::Worktree if current_branch_flag => true,
        _ if current_branch_flag && isolated_flag => true,
        _ => false,
    };
    if illegal {
        return WorktreePlan {
            mode,
            project_root: root.clone(),
            harness_cwd: root,
            branch: branch.into(),
            run_id: run_id.into(),
            isolated: true,
            blocked: true,
            reason_code: REASON_WORKTREE_ILLEGAL_COMBO.into(),
        };
    }

    match mode {
        WorktreeMode::Worktree => {
            let wt = project_root.join(".loom").join("worktrees").join(run_id);
            WorktreePlan {
                mode,
                project_root: root,
                harness_cwd: wt.to_string_lossy().to_string(),
                branch: branch.into(),
                run_id: run_id.into(),
                isolated: true,
                blocked: false,
                reason_code: String::new(),
            }
        }
        WorktreeMode::CurrentBranch => WorktreePlan {
            mode,
            project_root: root.clone(),
            harness_cwd: root,
            branch: branch.into(),
            run_id: run_id.into(),
            isolated: false,
            blocked: false,
            reason_code: String::new(),
        },
        WorktreeMode::RunBranch => {
            let run_branch = if branch.starts_with("loom/run/") || branch.starts_with("beacon/run/") {
                branch.to_string()
            } else {
                format!("loom/run/{run_id}")
            };
            WorktreePlan {
                mode,
                project_root: root.clone(),
                harness_cwd: root,
                branch: run_branch,
                run_id: run_id.into(),
                isolated: false,
                blocked: false,
                reason_code: String::new(),
            }
        }
    }
}

pub fn assert_harness_cwd(plan: &WorktreePlan, actual_cwd: &Path) -> Result<(), String> {
    if plan.blocked {
        return Err(plan.reason_code.clone());
    }
    let actual = actual_cwd.to_string_lossy().replace('\\', "/");
    let expect = plan.harness_cwd.replace('\\', "/");
    if matches!(plan.mode, WorktreeMode::Worktree) && actual != expect && !actual.starts_with(&expect)
    {
        return Err(format!("{REASON_WORKTREE_CWD_MISMATCH}:{actual}!={expect}"));
    }
    Ok(())
}

pub fn ensure_worktree_dir(plan: &WorktreePlan) -> Result<PathBuf, String> {
    if plan.blocked {
        return Err(plan.reason_code.clone());
    }
    let p = PathBuf::from(&plan.harness_cwd);
    if matches!(plan.mode, WorktreeMode::Worktree) {
        std::fs::create_dir_all(&p).map_err(|e| e.to_string())?;
        let marker = p.join(".loom-worktree.json");
        let body = serde_json::json!({
            "schema": "loom-worktree.v1",
            "run_id": plan.run_id,
            "mode": plan.mode.as_str(),
            "branch": plan.branch,
        });
        std::fs::write(&marker, body.to_string()).map_err(|e| e.to_string())?;
    }
    Ok(p)
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn three_modes_resolve() {
        let d = tempdir().unwrap();
        for mode in [
            WorktreeMode::Worktree,
            WorktreeMode::CurrentBranch,
            WorktreeMode::RunBranch,
        ] {
            let p = resolve_worktree_mode(mode, d.path(), "r1", "main", false, false);
            assert!(!p.blocked, "{:?}", p);
        }
    }

    #[test]
    fn illegal_current_plus_isolated() {
        let d = tempdir().unwrap();
        let p = resolve_worktree_mode(
            WorktreeMode::CurrentBranch,
            d.path(),
            "r1",
            "main",
            true,
            false,
        );
        assert!(p.blocked);
        assert_eq!(p.reason_code, REASON_WORKTREE_ILLEGAL_COMBO);
    }

    #[test]
    fn worktree_under_loom() {
        let d = tempdir().unwrap();
        let p = resolve_worktree_mode(WorktreeMode::Worktree, d.path(), "run-x", "feat", false, false);
        assert!(p.harness_cwd.contains(".loom/worktrees"));
        let path = ensure_worktree_dir(&p).unwrap();
        assert!(path.join(".loom-worktree.json").is_file());
    }
}
