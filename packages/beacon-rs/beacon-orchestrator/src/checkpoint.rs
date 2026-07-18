//! Run checkpoints for graceful stop / resume (P2-004).

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Checkpoint {
    pub schema: String,
    pub run_id: String,
    pub phase: String,
    pub iteration: u32,
    pub next_action: String,
    pub graceful: bool,
    pub force_stop: bool,
}

impl Checkpoint {
    pub fn new(run_id: impl Into<String>, phase: impl Into<String>, iteration: u32) -> Self {
        Self {
            schema: "goal-checkpoint.v1".into(),
            run_id: run_id.into(),
            phase: phase.into(),
            iteration,
            next_action: String::new(),
            graceful: true,
            force_stop: false,
        }
    }
}

pub fn checkpoint_path(dir: &Path, run_id: &str) -> PathBuf {
    dir.join(format!("checkpoint-{run_id}.json"))
}

pub fn save_checkpoint(dir: &Path, cp: &Checkpoint) -> Result<PathBuf, String> {
    fs::create_dir_all(dir).map_err(|e| e.to_string())?;
    let path = checkpoint_path(dir, &cp.run_id);
    let json = serde_json::to_string_pretty(cp).map_err(|e| e.to_string())?;
    fs::write(&path, json).map_err(|e| e.to_string())?;
    Ok(path)
}

pub fn load_checkpoint(dir: &Path, run_id: &str) -> Result<Checkpoint, String> {
    let path = checkpoint_path(dir, run_id);
    let text = fs::read_to_string(&path).map_err(|e| e.to_string())?;
    serde_json::from_str(&text).map_err(|e| e.to_string())
}

pub fn stop_with_checkpoint(
    dir: &Path,
    run_id: &str,
    phase: &str,
    iteration: u32,
    force: bool,
) -> Result<Checkpoint, String> {
    let mut cp = Checkpoint::new(run_id, phase, iteration);
    cp.graceful = !force;
    cp.force_stop = force;
    cp.next_action = if force {
        "aborted".into()
    } else {
        "resume".into()
    };
    save_checkpoint(dir, &cp)?;
    Ok(cp)
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn roundtrip() {
        let d = tempdir().unwrap();
        let cp = Checkpoint::new("r1", "implement", 3);
        save_checkpoint(d.path(), &cp).unwrap();
        let loaded = load_checkpoint(d.path(), "r1").unwrap();
        assert_eq!(loaded.iteration, 3);
    }
}
