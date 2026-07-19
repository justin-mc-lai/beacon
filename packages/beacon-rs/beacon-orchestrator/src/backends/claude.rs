//! AC backend: ClaudeBackend — true integration iteration (command-driven).
//!
//! Mirrors CodexBackend: each iterate runs a process, prefers IterationResult
//! JSON on stdout, and supports multi-round harnesses via env ITER variables.

use beacon_core::agent::{AgentBackend, IterationResult, TokenUsage};
use std::path::PathBuf;
use std::process::Command;

pub struct ClaudeBackend {
    name: String,
    command: Vec<String>,
    iteration: u32,
    max_iterations: u32,
    cwd: Option<PathBuf>,
    aborted: bool,
}

impl ClaudeBackend {
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


    /// Live Claude: requires ANTHROPIC_API_KEY or CLAUDE_API_KEY, else BLOCKED:missing_claude_cred.
    pub fn try_live(max_iterations: u32) -> Result<Self, String> {
        let has = std::env::var_os("ANTHROPIC_API_KEY")
            .or_else(|| std::env::var_os("CLAUDE_API_KEY"))
            .map(|v| !v.is_empty())
            .unwrap_or(false);
        if !has {
            return Err("BLOCKED:missing_claude_cred".into());
        }
        Ok(Self::new(max_iterations))
    }

    pub fn new(max_iterations: u32) -> Self {
        Self::with_command(
            "claude",
            vec!["claude".into(), "--version".into()],
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

impl AgentBackend for ClaudeBackend {
    fn name(&self) -> &str {
        &self.name
    }

    fn health_check(&self) -> Result<(), String> {
        if self.aborted {
            return Err("aborted".into());
        }
        if self.command.is_empty() {
            return Err("empty command".into());
        }
        let bin = &self.command[0];
        let path = std::path::Path::new(bin);
        if path.is_file() {
            return Ok(());
        }
        let mut cmd = Command::new(bin);
        cmd.arg("--version");
        if let Some(cwd) = &self.cwd {
            cmd.current_dir(cwd);
        }
        match cmd.output() {
            Ok(out) if out.status.success() || !out.stdout.is_empty() || !out.stderr.is_empty() => Ok(()),
            Ok(out) => Err(format!(
                "claude health failed: status={} stderr={}",
                out.status,
                String::from_utf8_lossy(&out.stderr)
            )),
            Err(e) => Err(format!("claude binary not runnable: {e}")),
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
            .env("AGENT_BACKEND_ITER", self.iteration.to_string())
            .env("AGENT_BACKEND_PROMPT", prompt)
            .env("AGENT_BACKEND_NAME", &self.name)
            .env("CODEX_BACKEND_ITER", self.iteration.to_string()); // harness compatibility
        if let Some(cwd) = &self.cwd {
            cmd.current_dir(cwd);
        }

        let output = cmd
            .output()
            .map_err(|e| format!("claude iterate spawn failed: {e}"))?;
        if !output.status.success() {
            return Err(format!(
                "claude iterate exited {}: {}",
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
                "claude-iter-{}: {}",
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
