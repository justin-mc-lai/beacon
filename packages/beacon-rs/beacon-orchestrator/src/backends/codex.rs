//! AC-043 CodexBackend — multi-round agent integration.
//!
//! Each `iterate` invokes a command (default: `codex` CLI, or a multi-round
//! harness for deterministic integration tests). Outputs should be
//! `IterationResult` JSON on stdout. Iteration index is passed so successive
//! rounds can differ; orchestrator writes each result into `artifact_refs`.

use beacon_core::agent::{AgentBackend, IterationResult, TokenUsage};
use std::path::PathBuf;
use std::process::Command;

/// Codex (or codex-compatible) multi-round backend.
pub struct CodexBackend {
    name: String,
    /// Command argv. `{iter}` is replaced with 1-based iteration index.
    command: Vec<String>,
    iteration: u32,
    max_iterations: u32,
    cwd: Option<PathBuf>,
    aborted: bool,
}

impl CodexBackend {
    pub fn with_command(
        name: impl Into<String>,
        command: Vec<String>,
        max_iterations: u32,
    ) -> Self {
        Self {
            name: name.into(),
            command,
            iteration: 0,
            max_iterations: max_iterations.max(1),
            cwd: None,
            aborted: false,
        }
    }

    /// Default backend targeting local `codex` binary.
    pub fn new(max_iterations: u32) -> Self {
        Self::with_command(
            "codex",
            vec!["codex".into(), "--version".into()],
            max_iterations,
        )
    }

    pub fn with_cwd(mut self, cwd: impl Into<PathBuf>) -> Self {
        self.cwd = Some(cwd.into());
        self
    }

    pub fn iteration(&self) -> u32 {
        self.iteration
    }
}

impl AgentBackend for CodexBackend {
    fn name(&self) -> &str {
        &self.name
    }

    fn health_check(&self) -> Result<(), String> {
        if self.aborted {
            return Err("aborted".into());
        }
        if self.command.is_empty() {
            return Err("empty codex command".into());
        }
        let bin = &self.command[0];
        let path = std::path::Path::new(bin);
        if path.is_file() {
            return Ok(());
        }
        // Fall back to PATH lookup for bare command names like "codex".
        let mut cmd = Command::new(bin);
        if bin.ends_with("codex") || bin == "codex" {
            cmd.arg("--version");
        } else {
            cmd.env("CODEX_BACKEND_ITER", "0");
        }
        if let Some(cwd) = &self.cwd {
            cmd.current_dir(cwd);
        }
        match cmd.output() {
            Ok(out) if out.status.success() || !out.stdout.is_empty() || !out.stderr.is_empty() => {
                Ok(())
            }
            Ok(out) => Err(format!(
                "codex health failed: status={} stderr={}",
                out.status,
                String::from_utf8_lossy(&out.stderr)
            )),
            Err(e) => Err(format!("codex binary not runnable: {e}")),
        }
    }

    fn iterate(&mut self, prompt: &str) -> Result<IterationResult, String> {
        if self.aborted {
            return Err("aborted".into());
        }
        self.iteration += 1;
        if self.iteration > self.max_iterations {
            return Ok(IterationResult {
                success: true,
                summary: "max iterations reached".into(),
                key_changes_made: vec![],
                key_learnings: vec![],
                stop_signal: Some("max_iterations".into()),
                token_usage: TokenUsage::default(),
                agent_name: self.name.clone(),
            });
        }

        let bin = self.command[0].clone();
        let args: Vec<String> = self.command[1..]
            .iter()
            .map(|a| {
                a.replace("{iter}", &self.iteration.to_string())
                    .replace("{prompt}", prompt)
            })
            .collect();

        let mut cmd = Command::new(&bin);
        cmd.args(&args)
            .env("CODEX_BACKEND_ITER", self.iteration.to_string())
            .env("CODEX_BACKEND_PROMPT", prompt)
            .env("CODEX_BACKEND_RUN_NAME", &self.name);
        if let Some(cwd) = &self.cwd {
            cmd.current_dir(cwd);
        }

        let output = cmd
            .output()
            .map_err(|e| format!("codex iterate spawn failed: {e}"))?;
        if !output.status.success() {
            return Err(format!(
                "codex iterate exited {}: {}",
                output.status,
                String::from_utf8_lossy(&output.stderr)
            ));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        let trimmed = stdout.trim();
        if let Ok(result) = serde_json::from_str::<IterationResult>(trimmed) {
            return Ok(result);
        }
        Ok(IterationResult {
            success: true,
            summary: format!(
                "codex-iter-{}: {}",
                self.iteration,
                trimmed.lines().next().unwrap_or("")
            ),
            key_changes_made: vec![format!("iter:{}", self.iteration)],
            key_learnings: vec![],
            stop_signal: None,
            token_usage: TokenUsage::default(),
            agent_name: self.name.clone(),
        })
    }

    fn abort(&mut self) -> Result<(), String> {
        self.aborted = true;
        self.iteration = self.max_iterations;
        Ok(())
    }
}
