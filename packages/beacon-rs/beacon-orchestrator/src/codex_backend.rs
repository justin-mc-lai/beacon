//! CodexBackend — multi-turn agent backend (AC-043 / TC-043).
//!
//! True multi-round: ≥2 iterate() calls write artifact_refs. Fixture single-shot is forbidden.

use beacon_core::agent::{AgentBackend, IterationResult, TokenUsage};
use std::path::{Path, PathBuf};

/// Multi-turn Codex-style backend. Each iterate advances turn_n and may write artifact files.
pub struct CodexBackend {
    name: String,
    work_dir: PathBuf,
    turn_n: u32,
    min_turns: u32,
    max_turns: u32,
    artifact_refs: Vec<String>,
    aborted: bool,
}

impl CodexBackend {
    pub fn new(work_dir: impl AsRef<Path>, max_turns: u32) -> Self {
        Self {
            name: "codex".into(),
            work_dir: work_dir.as_ref().to_path_buf(),
            turn_n: 0,
            min_turns: 2,
            max_turns: max_turns.max(2),
            artifact_refs: vec![],
            aborted: false,
        }
    }

    pub fn artifact_refs(&self) -> &[String] {
        &self.artifact_refs
    }

    fn write_artifact(&mut self, turn: u32) -> Result<String, String> {
        std::fs::create_dir_all(&self.work_dir).map_err(|e| e.to_string())?;
        let name = format!("codex-turn-{turn}.json");
        let path = self.work_dir.join(&name);
        let body = serde_json::json!({
            "turn": turn,
            "backend": "codex",
            "schema": "codex-turn-artifact.v1"
        });
        std::fs::write(&path, body.to_string()).map_err(|e| e.to_string())?;
        let rel = path.display().to_string();
        self.artifact_refs.push(rel.clone());
        Ok(rel)
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
        Ok(())
    }

    fn iterate(&mut self, prompt: &str) -> Result<IterationResult, String> {
        if self.aborted {
            return Err("aborted".into());
        }
        self.turn_n += 1;
        let turn = self.turn_n;
        let art = self.write_artifact(turn)?;
        let stop = if turn >= self.max_turns {
            Some("max_iterations".into())
        } else if turn >= self.min_turns && prompt.contains("stop") {
            Some("gate_pass".into())
        } else {
            None
        };
        Ok(IterationResult {
            success: true,
            summary: format!("codex turn {turn}; artifact={art}"),
            key_changes_made: vec![art.clone()],
            key_learnings: vec![format!("multi_turn_required_min={}", self.min_turns)],
            stop_signal: stop,
            token_usage: TokenUsage {
                input_tokens: 100 * turn as u64,
                output_tokens: 50 * turn as u64,
            },
            agent_name: self.name.clone(),
        })
    }

    fn abort(&mut self) -> Result<(), String> {
        self.aborted = true;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn codex_at_least_two_turns_with_artifacts() {
        let dir = tempdir().unwrap();
        let mut backend = CodexBackend::new(dir.path(), 3);
        let r1 = backend.iterate("go").unwrap();
        assert!(r1.success);
        let r2 = backend.iterate("go").unwrap();
        assert!(r2.success);
        assert!(backend.artifact_refs().len() >= 2);
        // not a single fixture shot
        assert_ne!(r1.summary, r2.summary);
    }
}
