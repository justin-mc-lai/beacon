//! External stop_when verification (AC-105 / AC-106 / W2).
//! Agent stop_signal alone must not terminate the loop (maker ≠ checker).

use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::process::Command;

pub const REASON_STOP_WHEN_UNVERIFIED: &str = "stop_when_unverified";
pub const REASON_EXTERNAL_STOP_VERIFIED: &str = "external_stop_verified";

/// Result of an external stop check after an agent iteration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExternalStopCheckResult {
    pub allowed: bool,
    pub reason_code: String,
    pub detail: String,
}

/// Trait for external stop checkers (gate exit0 / --stop-check-cmd / evaluator).
pub trait ExternalStopChecker: Send {
    fn check(&mut self) -> ExternalStopCheckResult;
}

/// Always deny — used to prove agent self-stop is ignored.
pub struct DenyStopChecker;

impl ExternalStopChecker for DenyStopChecker {
    fn check(&mut self) -> ExternalStopCheckResult {
        ExternalStopCheckResult {
            allowed: false,
            reason_code: REASON_STOP_WHEN_UNVERIFIED.into(),
            detail: "deny_all".into(),
        }
    }
}

/// Always allow — fixture for external verified stop.
pub struct AllowStopChecker {
    pub label: String,
}

impl ExternalStopChecker for AllowStopChecker {
    fn check(&mut self) -> ExternalStopCheckResult {
        ExternalStopCheckResult {
            allowed: true,
            reason_code: REASON_EXTERNAL_STOP_VERIFIED.into(),
            detail: self.label.clone(),
        }
    }
}

/// Run an external command; exit 0 → allow stop.
pub struct CommandStopChecker {
    pub command: Vec<String>,
    pub cwd: Option<PathBuf>,
}

impl ExternalStopChecker for CommandStopChecker {
    fn check(&mut self) -> ExternalStopCheckResult {
        if self.command.is_empty() {
            return ExternalStopCheckResult {
                allowed: false,
                reason_code: REASON_STOP_WHEN_UNVERIFIED.into(),
                detail: "empty_stop_check_cmd".into(),
            };
        }
        let mut cmd = Command::new(&self.command[0]);
        if self.command.len() > 1 {
            cmd.args(&self.command[1..]);
        }
        if let Some(ref cwd) = self.cwd {
            cmd.current_dir(cwd);
        }
        match cmd.output() {
            Ok(out) if out.status.success() => ExternalStopCheckResult {
                allowed: true,
                reason_code: REASON_EXTERNAL_STOP_VERIFIED.into(),
                detail: format!("cmd_exit_0:{}", self.command.join(" ")),
            },
            Ok(out) => ExternalStopCheckResult {
                allowed: false,
                reason_code: REASON_STOP_WHEN_UNVERIFIED.into(),
                detail: format!(
                    "cmd_exit_{}:{}",
                    out.status.code().unwrap_or(-1),
                    String::from_utf8_lossy(&out.stderr)
                ),
            },
            Err(e) => ExternalStopCheckResult {
                allowed: false,
                reason_code: REASON_STOP_WHEN_UNVERIFIED.into(),
                detail: format!("cmd_spawn_failed:{e}"),
            },
        }
    }
}

/// File-presence checker: stop allowed when path exists (fixture-friendly).
pub struct FileExistsStopChecker {
    pub path: PathBuf,
}

impl ExternalStopChecker for FileExistsStopChecker {
    fn check(&mut self) -> ExternalStopCheckResult {
        if self.path.exists() {
            ExternalStopCheckResult {
                allowed: true,
                reason_code: REASON_EXTERNAL_STOP_VERIFIED.into(),
                detail: format!("file_exists:{}", self.path.display()),
            }
        } else {
            ExternalStopCheckResult {
                allowed: false,
                reason_code: REASON_STOP_WHEN_UNVERIFIED.into(),
                detail: format!("file_missing:{}", self.path.display()),
            }
        }
    }
}

/// Map CLI --agent value to a backend name (AC-105).
pub fn map_agent_name(agent: &str) -> Result<String, String> {
    let a = agent.trim().to_ascii_lowercase();
    if a.is_empty() {
        return Err("agent_required".into());
    }
    if a == "codex" || a == "claude" || a == "subprocess" || a == "implement-harness" {
        return Ok(a);
    }
    if let Some(rest) = a.strip_prefix("acp:") {
        if rest.is_empty() {
            return Err("acp_target_required".into());
        }
        return Ok(format!("acp:{rest}"));
    }
    Err(format!("unknown_agent:{agent}"))
}

/// Bind harness cwd for W1 worktree (optional).
pub fn assert_run_cwd(admitted: Option<&Path>, actual: &Path) -> Result<(), String> {
    let Some(adm) = admitted else {
        return Ok(());
    };
    let a = adm.canonicalize().unwrap_or_else(|_| adm.to_path_buf());
    let b = actual.canonicalize().unwrap_or_else(|_| actual.to_path_buf());
    if a != b {
        return Err(format!(
            "run_cwd_mismatch:admitted={} actual={}",
            a.display(),
            b.display()
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn map_agents() {
        assert_eq!(map_agent_name("codex").unwrap(), "codex");
        assert_eq!(map_agent_name("acp:demo").unwrap(), "acp:demo");
        assert!(map_agent_name("nope").is_err());
    }

    #[test]
    fn file_checker() {
        let d = tempdir().unwrap();
        let p = d.path().join("ok");
        let mut deny = FileExistsStopChecker { path: p.clone() };
        assert!(!deny.check().allowed);
        std::fs::write(&p, "x").unwrap();
        assert!(deny.check().allowed);
    }
}
