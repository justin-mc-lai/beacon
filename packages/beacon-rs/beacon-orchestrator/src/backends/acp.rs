//! AC backend: AcpBackend — true integration iteration (command-driven).
//!
//! Mirrors CodexBackend: each iterate runs a process, prefers IterationResult
//! JSON on stdout, and supports multi-round harnesses via env ITER variables.

use beacon_core::agent::{AgentBackend, IterationResult, TokenUsage};
use std::path::PathBuf;
use std::process::Command;

pub struct AcpBackend {
    name: String,
    command: Vec<String>,
    iteration: u32,
    max_iterations: u32,
    cwd: Option<PathBuf>,
    aborted: bool,
}

impl AcpBackend {
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

    pub fn new(max_iterations: u32) -> Self {
        Self::with_command(
            "acp",
            vec!["acp".into(), "--help".into()],
            max_iterations,
        )
    }

    /// AC-046 CLI form `acp:<target>` — store target in name and env.
    pub fn with_target(target: impl Into<String>, max_iterations: u32) -> Self {
        let target = target.into();
        let backend = Self::with_command(
            format!("acp:{target}"),
            vec!["acp".into(), "run".into(), target.clone()],
            max_iterations,
        );
        // Prefer harness override in tests via with_command.
        let _ = target;
        backend
    }

    pub fn with_cwd(mut self, cwd: impl Into<PathBuf>) -> Self {
        self.cwd = Some(cwd.into());
        self
    }

    pub fn iteration(&self) -> u32 {
        self.iteration
    }
}

impl AgentBackend for AcpBackend {
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
        cmd.arg("--help");
        if let Some(cwd) = &self.cwd {
            cmd.current_dir(cwd);
        }
        match cmd.output() {
            Ok(out) if out.status.success() || !out.stdout.is_empty() || !out.stderr.is_empty() => Ok(()),
            Ok(out) => Err(format!(
                "acp health failed: status={} stderr={}",
                out.status,
                String::from_utf8_lossy(&out.stderr)
            )),
            Err(e) => Err(format!("acp binary not runnable: {e}")),
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
            .map_err(|e| format!("acp iterate spawn failed: {e}"))?;
        if !output.status.success() {
            return Err(format!(
                "acp iterate exited {}: {}",
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
                "acp-iter-{}: {}",
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
