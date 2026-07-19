//! Real git worktree modes for Loom W1 (AC-099 / TC-W1-001/003).
//!
//! Modes: worktree | current-branch | run-branch.
//! Illegal: current-branch + isolated → fail-closed.
//! Materialize uses `git worktree add` (never mkdir-only fake).

use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::process::Command;

pub const REASON_ILLEGAL_MODE_COMBO: &str = "worktree_illegal_mode_combo";
pub const REASON_UNKNOWN_MODE: &str = "worktree_unknown_mode";
pub const REASON_GIT_WORKTREE_FAILED: &str = "git_worktree_add_failed";
pub const REASON_NOT_A_GIT_REPO: &str = "not_a_git_repo";
pub const REASON_MKDIR_ONLY_FORBIDDEN: &str = "mkdir_only_worktree_forbidden";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum WorktreeMode {
    Worktree,
    CurrentBranch,
    RunBranch,
}

impl WorktreeMode {
    pub fn parse(s: &str) -> Option<Self> {
        match s.trim().to_ascii_lowercase().as_str() {
            "worktree" | "isolated" | "isolated-worktree" => Some(Self::Worktree),
            "current-branch" | "current_branch" | "current" => Some(Self::CurrentBranch),
            "run-branch" | "run_branch" | "run" => Some(Self::RunBranch),
            _ => None,
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Worktree => "worktree",
            Self::CurrentBranch => "current-branch",
            Self::RunBranch => "run-branch",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorktreeResolveRequest {
    pub project_root: PathBuf,
    pub mode: WorktreeMode,
    pub run_id: String,
    pub feature_slug: String,
    /// When true with CurrentBranch → illegal combo (I-W1-003).
    pub isolated: bool,
    /// When true, actually run `git worktree add` for Worktree mode.
    pub materialize: bool,
    /// Optional base ref (default HEAD).
    pub base_ref: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorktreeResolveResult {
    pub blocked: bool,
    pub status: String,
    pub reason_code: String,
    pub mode: String,
    pub admitted_worktree: String,
    pub branch: String,
    pub project_root: String,
    pub git_worktree_added: bool,
    pub git_dir_is_file: bool,
    pub materialize_requested: bool,
}

/// Resolve (and optionally materialize) a worktree admission path.
pub fn resolve_worktree(req: &WorktreeResolveRequest) -> WorktreeResolveResult {
    let root = &req.project_root;
    let root_s = root.to_string_lossy().to_string();

    // Illegal: current-branch + isolated
    if req.mode == WorktreeMode::CurrentBranch && req.isolated {
        return WorktreeResolveResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_ILLEGAL_MODE_COMBO.into(),
            mode: req.mode.as_str().into(),
            admitted_worktree: String::new(),
            branch: String::new(),
            project_root: root_s,
            git_worktree_added: false,
            git_dir_is_file: false,
            materialize_requested: req.materialize,
        };
    }

    if !is_git_repo(root) {
        return WorktreeResolveResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_NOT_A_GIT_REPO.into(),
            mode: req.mode.as_str().into(),
            admitted_worktree: String::new(),
            branch: String::new(),
            project_root: root_s,
            git_worktree_added: false,
            git_dir_is_file: false,
            materialize_requested: req.materialize,
        };
    }

    match req.mode {
        WorktreeMode::CurrentBranch => {
            let branch = current_branch(root).unwrap_or_else(|_| "HEAD".into());
            WorktreeResolveResult {
                blocked: false,
                status: "pass".into(),
                reason_code: String::new(),
                mode: req.mode.as_str().into(),
                admitted_worktree: root_s.clone(),
                branch,
                project_root: root_s,
                git_worktree_added: false,
                git_dir_is_file: false,
                materialize_requested: req.materialize,
            }
        }
        WorktreeMode::RunBranch => {
            let branch_name = format!(
                "loom/{}/{}",
                sanitize(&req.run_id),
                sanitize(&req.feature_slug)
            );
            if req.materialize {
                if let Err(e) = ensure_branch(root, &branch_name) {
                    return WorktreeResolveResult {
                        blocked: true,
                        status: "blocked".into(),
                        reason_code: format!("{REASON_GIT_WORKTREE_FAILED}:{e}"),
                        mode: req.mode.as_str().into(),
                        admitted_worktree: String::new(),
                        branch: branch_name,
                        project_root: root_s,
                        git_worktree_added: false,
                        git_dir_is_file: false,
                        materialize_requested: true,
                    };
                }
            }
            WorktreeResolveResult {
                blocked: false,
                status: "pass".into(),
                reason_code: String::new(),
                mode: req.mode.as_str().into(),
                admitted_worktree: root_s.clone(),
                branch: branch_name,
                project_root: root_s,
                git_worktree_added: false,
                git_dir_is_file: false,
                materialize_requested: req.materialize,
            }
        }
        WorktreeMode::Worktree => {
            let branch_name = format!(
                "loom/wt/{}/{}",
                sanitize(&req.run_id),
                sanitize(&req.feature_slug)
            );
            let wt_path = root
                .join(".loom")
                .join("worktrees")
                .join(format!(
                    "{}-{}",
                    sanitize(&req.feature_slug),
                    sanitize(&req.run_id)
                ));

            if !req.materialize {
                return WorktreeResolveResult {
                    blocked: false,
                    status: "planned".into(),
                    reason_code: String::new(),
                    mode: req.mode.as_str().into(),
                    admitted_worktree: wt_path.to_string_lossy().to_string(),
                    branch: branch_name,
                    project_root: root_s,
                    git_worktree_added: false,
                    git_dir_is_file: false,
                    materialize_requested: false,
                };
            }

            match materialize_git_worktree(root, &wt_path, &branch_name, req.base_ref.as_deref()) {
                Ok(info) => WorktreeResolveResult {
                    blocked: false,
                    status: "pass".into(),
                    reason_code: String::new(),
                    mode: req.mode.as_str().into(),
                    admitted_worktree: info.path,
                    branch: info.branch,
                    project_root: root_s,
                    git_worktree_added: true,
                    git_dir_is_file: info.git_dir_is_file,
                    materialize_requested: true,
                },
                Err(e) => WorktreeResolveResult {
                    blocked: true,
                    status: "blocked".into(),
                    reason_code: format!("{REASON_GIT_WORKTREE_FAILED}:{e}"),
                    mode: req.mode.as_str().into(),
                    admitted_worktree: wt_path.to_string_lossy().to_string(),
                    branch: branch_name,
                    project_root: root_s,
                    git_worktree_added: false,
                    git_dir_is_file: false,
                    materialize_requested: true,
                },
            }
        }
    }
}

struct MaterializeInfo {
    path: String,
    branch: String,
    git_dir_is_file: bool,
}

/// Real `git worktree add` — rejects mkdir-only pretence.
fn materialize_git_worktree(
    project_root: &Path,
    wt_path: &Path,
    branch_name: &str,
    base_ref: Option<&str>,
) -> Result<MaterializeInfo, String> {
    if wt_path.exists() {
        // Re-admit existing worktree if already linked
        let git_file = wt_path.join(".git");
        if git_file.is_file() || wt_path.join(".git").exists() {
            let branch = current_branch(wt_path).unwrap_or_else(|_| branch_name.to_string());
            return Ok(MaterializeInfo {
                path: wt_path.to_string_lossy().to_string(),
                branch,
                git_dir_is_file: git_file.is_file(),
            });
        }
        return Err(format!(
            "path exists but is not a git worktree: {}",
            wt_path.display()
        ));
    }

    if let Some(parent) = wt_path.parent() {
        std::fs::create_dir_all(parent).map_err(|e| format!("create parent: {e}"))?;
    }

    let base = base_ref.unwrap_or("HEAD");
    // Prefer creating a new branch at base; fall back to worktree on existing branch name.
    let out = Command::new("git")
        .args([
            "worktree",
            "add",
            "-b",
            branch_name,
            &wt_path.to_string_lossy(),
            base,
        ])
        .current_dir(project_root)
        .output()
        .map_err(|e| format!("spawn git worktree: {e}"))?;

    if !out.status.success() {
        let stderr = String::from_utf8_lossy(&out.stderr);
        // Branch may already exist — retry without -b
        let retry = Command::new("git")
            .args([
                "worktree",
                "add",
                &wt_path.to_string_lossy(),
                branch_name,
            ])
            .current_dir(project_root)
            .output()
            .map_err(|e| format!("spawn git worktree retry: {e}"))?;
        if !retry.status.success() {
            return Err(format!(
                "git worktree add failed: {} | retry: {}",
                stderr.trim(),
                String::from_utf8_lossy(&retry.stderr).trim()
            ));
        }
    }

    let git_file = wt_path.join(".git");
    // Enforce real worktree linkage (gitdir file), not bare mkdir
    if !git_file.exists() {
        let _ = std::fs::remove_dir_all(wt_path);
        return Err(format!(
            "{REASON_MKDIR_ONLY_FORBIDDEN}: .git missing after worktree add"
        ));
    }

    Ok(MaterializeInfo {
        path: wt_path
            .canonicalize()
            .unwrap_or_else(|_| wt_path.to_path_buf())
            .to_string_lossy()
            .to_string(),
        branch: current_branch(wt_path).unwrap_or_else(|_| branch_name.to_string()),
        git_dir_is_file: git_file.is_file(),
    })
}

fn is_git_repo(path: &Path) -> bool {
    let git = path.join(".git");
    git.is_dir() || git.is_file()
}

fn current_branch(cwd: &Path) -> Result<String, String> {
    let out = Command::new("git")
        .args(["rev-parse", "--abbrev-ref", "HEAD"])
        .current_dir(cwd)
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(String::from_utf8_lossy(&out.stderr).to_string());
    }
    Ok(String::from_utf8_lossy(&out.stdout).trim().to_string())
}

fn ensure_branch(root: &Path, branch_name: &str) -> Result<(), String> {
    // Create branch if missing; leave HEAD unchanged (run-branch admission path).
    let exists = Command::new("git")
        .args(["rev-parse", "--verify", &format!("refs/heads/{branch_name}")])
        .current_dir(root)
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false);
    if exists {
        return Ok(());
    }
    let out = Command::new("git")
        .args(["branch", branch_name, "HEAD"])
        .current_dir(root)
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(String::from_utf8_lossy(&out.stderr).trim().to_string());
    }
    Ok(())
}

fn sanitize(s: &str) -> String {
    s.chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '-' || c == '_' {
                c
            } else {
                '-'
            }
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::process::Command;
    use tempfile::tempdir;

    fn init_repo(dir: &Path) {
        assert!(Command::new("git")
            .args(["init"])
            .current_dir(dir)
            .status()
            .unwrap()
            .success());
        // identity for commit
        let _ = Command::new("git")
            .args(["config", "user.email", "w1@test.local"])
            .current_dir(dir)
            .status();
        let _ = Command::new("git")
            .args(["config", "user.name", "w1-test"])
            .current_dir(dir)
            .status();
        std::fs::write(dir.join("README.md"), "w1\n").unwrap();
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

    #[test]
    fn illegal_current_branch_plus_isolated() {
        let dir = tempdir().unwrap();
        init_repo(dir.path());
        let r = resolve_worktree(&WorktreeResolveRequest {
            project_root: dir.path().to_path_buf(),
            mode: WorktreeMode::CurrentBranch,
            run_id: "r1".into(),
            feature_slug: "demo".into(),
            isolated: true,
            materialize: false,
            base_ref: None,
        });
        assert!(r.blocked);
        assert_eq!(r.reason_code, REASON_ILLEGAL_MODE_COMBO);
    }

    #[test]
    fn real_git_worktree_add() {
        let dir = tempdir().unwrap();
        init_repo(dir.path());
        let r = resolve_worktree(&WorktreeResolveRequest {
            project_root: dir.path().to_path_buf(),
            mode: WorktreeMode::Worktree,
            run_id: "run1".into(),
            feature_slug: "feat-a".into(),
            isolated: false,
            materialize: true,
            base_ref: None,
        });
        assert!(!r.blocked, "{:?}", r);
        assert!(r.git_worktree_added);
        assert!(PathBuf::from(&r.admitted_worktree).exists());
        assert!(
            PathBuf::from(&r.admitted_worktree).join(".git").is_file(),
            "must be real linked worktree, not mkdir"
        );
    }
}
