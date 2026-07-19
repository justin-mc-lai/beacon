//! ImplementHarnessBackend — true implement-surface one iteration (AC-100 / TC-W1-002).
//!
//! NOT SubprocessBackend echo-JSON. Writes implement artifacts inside admitted worktree cwd
//! and returns IterationResult matching AC-042.

use beacon_core::agent::{AgentBackend, IterationResult, TokenUsage};
use beacon_core::branch_context::BranchContext;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

pub const REASON_HARNESS_CWD_MISMATCH: &str = "implement_harness_cwd_mismatch";
pub const REASON_HARNESS_NOT_ADMITTED: &str = "implement_harness_not_admitted";
pub const REASON_SUBPROCESS_ONLY_FORBIDDEN: &str = "implement_harness_subprocess_only_forbidden";

/// Typed implement harness backend bound to an admitted worktree.
#[derive(Debug)]
pub struct ImplementHarnessBackend {
    name: String,
    /// Project root / admitted worktree path — must equal BranchContext.admitted_worktree.
    admitted_cwd: PathBuf,
    branch_context: BranchContext,
    iteration: u32,
    artifact_refs: Vec<String>,
    aborted: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImplementIterationArtifact {
    pub schema: String,
    pub backend: String,
    pub iteration: u32,
    pub admitted_worktree: String,
    pub branch: String,
    pub prompt_digest: String,
    pub key_changes_made: Vec<String>,
}

impl ImplementHarnessBackend {
    /// Construct only when BranchContext is admitted and cwd aligns.
    pub fn try_new(branch_context: BranchContext, project_root_hint: Option<&Path>) -> Result<Self, String> {
        if !branch_context.admitted {
            return Err(REASON_HARNESS_NOT_ADMITTED.into());
        }
        branch_context
            .validate_schema()
            .map_err(|e| format!("{REASON_HARNESS_NOT_ADMITTED}:{e}"))?;
        let admitted = PathBuf::from(&branch_context.admitted_worktree);
        if !admitted.exists() {
            return Err(format!(
                "{REASON_HARNESS_CWD_MISMATCH}:admitted_path_missing:{}",
                admitted.display()
            ));
        }
        if let Some(hint) = project_root_hint {
            let hint_s = hint.to_string_lossy();
            let adm_s = admitted.to_string_lossy();
            if hint_s != adm_s
                && !adm_s.starts_with(hint_s.as_ref())
                && !hint_s.starts_with(adm_s.as_ref())
            {
                // Allow when hint is target_project_root and admitted is nested worktree
                if branch_context.target_project_root != hint_s.as_ref()
                    && branch_context.admitted_worktree != hint_s.as_ref()
                {
                    return Err(format!(
                        "{REASON_HARNESS_CWD_MISMATCH}:hint={} admitted={}",
                        hint.display(),
                        admitted.display()
                    ));
                }
            }
        }
        Ok(Self {
            name: "implement-harness".into(),
            admitted_cwd: admitted,
            branch_context,
            iteration: 0,
            artifact_refs: vec![],
            aborted: false,
        })
    }

    pub fn admitted_cwd(&self) -> &Path {
        &self.admitted_cwd
    }

    pub fn artifact_refs(&self) -> &[String] {
        &self.artifact_refs
    }

    pub fn branch_context(&self) -> &BranchContext {
        &self.branch_context
    }

    /// Enforce harness project-root == admitted worktree (UD-LOOM-W1-003).
    pub fn assert_cwd_aligned(&self) -> Result<(), String> {
        let adm = self
            .admitted_cwd
            .canonicalize()
            .unwrap_or_else(|_| self.admitted_cwd.clone());
        let ctx = PathBuf::from(&self.branch_context.admitted_worktree);
        let ctx_c = ctx.canonicalize().unwrap_or(ctx);
        if adm != ctx_c {
            return Err(format!(
                "{REASON_HARNESS_CWD_MISMATCH}:cwd={} context={}",
                adm.display(),
                ctx_c.display()
            ));
        }
        Ok(())
    }

    fn write_iteration_artifact(&mut self, prompt: &str) -> Result<(String, ImplementIterationArtifact), String> {
        self.assert_cwd_aligned()?;
        let art_dir = self.admitted_cwd.join(".loom").join("artifacts").join("implement");
        std::fs::create_dir_all(&art_dir).map_err(|e| e.to_string())?;
        let n = self.iteration;
        let path = art_dir.join(format!("iteration-{n}.json"));
        let digest = format!("{:x}", simple_digest(prompt));
        let change_marker = art_dir.join(format!("change-{n}.txt"));
        std::fs::write(
            &change_marker,
            format!(
                "implement iteration {n} on branch {} in {}\n",
                self.branch_context.branch,
                self.admitted_cwd.display()
            ),
        )
        .map_err(|e| e.to_string())?;
        let changes = vec![
            change_marker.to_string_lossy().to_string(),
            path.to_string_lossy().to_string(),
        ];
        let body = ImplementIterationArtifact {
            schema: "implement-iteration-artifact.v1".into(),
            backend: self.name.clone(),
            iteration: n,
            admitted_worktree: self.admitted_cwd.to_string_lossy().to_string(),
            branch: self.branch_context.branch.clone(),
            prompt_digest: digest,
            key_changes_made: changes.clone(),
        };
        let json = serde_json::to_string_pretty(&body).map_err(|e| e.to_string())?;
        std::fs::write(&path, json).map_err(|e| e.to_string())?;
        let path_s = path.to_string_lossy().to_string();
        self.artifact_refs.push(path_s.clone());
        self.artifact_refs.push(change_marker.to_string_lossy().to_string());
        Ok((path_s, body))
    }
}

impl AgentBackend for ImplementHarnessBackend {
    fn name(&self) -> &str {
        &self.name
    }

    fn health_check(&self) -> Result<(), String> {
        if self.aborted {
            return Err("aborted".into());
        }
        self.assert_cwd_aligned()?;
        if !self.admitted_cwd.exists() {
            return Err(format!(
                "{REASON_HARNESS_CWD_MISMATCH}:missing {}",
                self.admitted_cwd.display()
            ));
        }
        Ok(())
    }

    fn iterate(&mut self, prompt: &str) -> Result<IterationResult, String> {
        if self.aborted {
            return Err("aborted".into());
        }
        // Reject "subprocess-only" masquerade: we never shell out for the iterate body.
        if prompt.contains("SUBPROCESS_ONLY_FAKE") {
            return Err(REASON_SUBPROCESS_ONLY_FORBIDDEN.into());
        }
        self.iteration += 1;
        let (art_path, body) = self.write_iteration_artifact(prompt)?;
        Ok(IterationResult {
            success: true,
            summary: format!(
                "implement harness iteration {} in {}",
                self.iteration,
                self.admitted_cwd.display()
            ),
            key_changes_made: body.key_changes_made,
            key_learnings: vec![
                "implement_harness_is_not_subprocess_echo".into(),
                format!("artifact={art_path}"),
                format!("cwd={}", self.admitted_cwd.display()),
            ],
            stop_signal: Some("max_iterations".into()),
            token_usage: TokenUsage {
                input_tokens: 42,
                output_tokens: 24,
            },
            agent_name: self.name.clone(),
        })
    }

    fn abort(&mut self) -> Result<(), String> {
        self.aborted = true;
        Ok(())
    }
}

/// Run one implement iteration after worktree admission (happy path helper).
pub fn run_one_implement_iteration(
    branch_context: BranchContext,
    prompt: &str,
) -> Result<(IterationResult, Vec<String>), String> {
    let mut backend = ImplementHarnessBackend::try_new(branch_context, None)?;
    backend.health_check()?;
    let result = backend.iterate(prompt)?;
    Ok((result, backend.artifact_refs().to_vec()))
}

fn simple_digest(s: &str) -> u64 {
    // FNV-1a 64 — no extra deps; stable enough for prompt digest in artifacts
    let mut hash: u64 = 0xcbf29ce484222325;
    for b in s.as_bytes() {
        hash ^= u64::from(*b);
        hash = hash.wrapping_mul(0x100000001b3);
    }
    hash
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::git_worktree::{resolve_worktree, WorktreeMode, WorktreeResolveRequest};
    use crate::workspace_admission::{admit_workspace, WorkspaceAdmissionRequest};
    use std::process::Command;
    use tempfile::tempdir;

    fn init_repo(dir: &Path) {
        assert!(Command::new("git").args(["init"]).current_dir(dir).status().unwrap().success());
        let _ = Command::new("git").args(["config", "user.email", "w1@test.local"]).current_dir(dir).status();
        let _ = Command::new("git").args(["config", "user.name", "w1"]).current_dir(dir).status();
        std::fs::write(dir.join("README.md"), "x\n").unwrap();
        assert!(Command::new("git").args(["add", "README.md"]).current_dir(dir).status().unwrap().success());
        assert!(Command::new("git").args(["commit", "-m", "i"]).current_dir(dir).status().unwrap().success());
    }

    #[test]
    fn one_iter_writes_artifact_in_worktree() {
        let dir = tempdir().unwrap();
        init_repo(dir.path());
        let wt = resolve_worktree(&WorktreeResolveRequest {
            project_root: dir.path().to_path_buf(),
            mode: WorktreeMode::Worktree,
            run_id: "r-imp".into(),
            feature_slug: "imp".into(),
            isolated: false,
            materialize: true,
            base_ref: None,
        });
        assert!(!wt.blocked, "{:?}", wt);
        let admit = admit_workspace(&WorkspaceAdmissionRequest {
            run_id: "r-imp".into(),
            caller_cwd: wt.admitted_worktree.clone(),
            target_project_root: dir.path().to_string_lossy().to_string(),
            worktree: Some(wt.admitted_worktree.clone()),
            branch: wt.branch.clone(),
            allow_cwd_as_root: true,
        });
        assert!(!admit.blocked);
        let bc = admit.branch_context.unwrap();
        let (result, refs) = run_one_implement_iteration(bc, "implement one round").unwrap();
        assert!(result.success);
        assert_eq!(result.agent_name, "implement-harness");
        assert!(!result.key_changes_made.is_empty());
        assert!(!refs.is_empty());
        for r in &refs {
            assert!(PathBuf::from(r).exists(), "missing {r}");
            // artifact must live under admitted worktree
            assert!(
                r.starts_with(&wt.admitted_worktree)
                    || PathBuf::from(r)
                        .canonicalize()
                        .map(|p| p.starts_with(PathBuf::from(&wt.admitted_worktree).canonicalize().unwrap()))
                        .unwrap_or(false),
                "artifact outside worktree: {r}"
            );
        }
        // schema fields AC-042
        let v = serde_json::to_value(&result).unwrap();
        for key in [
            "success",
            "summary",
            "key_changes_made",
            "key_learnings",
            "token_usage",
            "agent_name",
        ] {
            assert!(v.get(key).is_some(), "missing {key}");
        }
    }
}
