//! GitScope topology gates (AC-171 / AC-172 / AC-173 / W4b).

use beacon_core::branch_context::BranchContext;
use serde::{Deserialize, Serialize};
use std::path::Path;

pub const REASON_GSG_PARITY_FAILED: &str = "gitscope_branch_context_parity_failed";
pub const REASON_TOPOLOGY_GATE_MISSING: &str = "topology_gate_missing";
pub const REASON_TOPOLOGY_GATE_BLOCKED: &str = "topology_gate_blocked";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TopologyKind {
    SingleRepo,
    Monorepo,
    MultiGitWorkspace,
}

impl TopologyKind {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::SingleRepo => "single_repo",
            Self::Monorepo => "monorepo",
            Self::MultiGitWorkspace => "multi_git_workspace",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s.trim().to_ascii_lowercase().as_str() {
            "single_repo" | "single" => Some(Self::SingleRepo),
            "monorepo" | "mono" => Some(Self::Monorepo),
            "multi_git_workspace" | "multi_git" | "multi" => Some(Self::MultiGitWorkspace),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GitScopeNode {
    pub root: String,
    pub topology: String,
    pub is_primary: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GitScopeGraph {
    pub schema: String,
    pub topology: String,
    pub nodes: Vec<GitScopeNode>,
    pub topology_gate_status: String,
    pub topology_gate_ref: String,
    pub reason_codes: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TopologyGateResult {
    pub blocked: bool,
    pub status: String,
    pub reason_code: String,
    pub topology_gate_ref: String,
    pub topology: String,
}

/// Build a simple GSG projection for a project root.
pub fn build_gitscope(project_root: &Path, topology: TopologyKind) -> GitScopeGraph {
    let root = project_root.to_string_lossy().to_string();
    let mut nodes = vec![GitScopeNode {
        root: root.clone(),
        topology: topology.as_str().into(),
        is_primary: true,
    }];
    if topology == TopologyKind::MultiGitWorkspace {
        nodes.push(GitScopeNode {
            root: format!("{root}/nested-lib"),
            topology: TopologyKind::SingleRepo.as_str().into(),
            is_primary: false,
        });
    }
    if topology == TopologyKind::Monorepo {
        nodes.push(GitScopeNode {
            root: format!("{root}/packages/a"),
            topology: topology.as_str().into(),
            is_primary: false,
        });
        nodes.push(GitScopeNode {
            root: format!("{root}/packages/b"),
            topology: topology.as_str().into(),
            is_primary: false,
        });
    }
    let ref_id = format!("gsg:{}:{}", topology.as_str(), simple_hash(&root));
    GitScopeGraph {
        schema: "gitscope-graph.v1".into(),
        topology: topology.as_str().into(),
        nodes,
        topology_gate_status: "pass".into(),
        topology_gate_ref: ref_id,
        reason_codes: vec![],
    }
}

/// Extend BranchContext with GSG topology (AC-171).
pub fn apply_gitscope_to_branch_context(
    mut bc: BranchContext,
    gsg: &GitScopeGraph,
) -> Result<BranchContext, String> {
    if gsg.topology_gate_status != "pass" || gsg.topology_gate_ref.is_empty() {
        return Err(REASON_GSG_PARITY_FAILED.into());
    }
    if gsg.nodes.is_empty() {
        return Err(REASON_GSG_PARITY_FAILED.into());
    }
    bc.topology = gsg.topology.clone();
    Ok(bc)
}

/// Force topology_gate_ref for implement/loop admission (AC-173).
pub fn require_topology_gate(
    gsg: Option<&GitScopeGraph>,
    topology_gate_ref: Option<&str>,
) -> TopologyGateResult {
    let Some(g) = gsg else {
        return TopologyGateResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_TOPOLOGY_GATE_MISSING.into(),
            topology_gate_ref: String::new(),
            topology: String::new(),
        };
    };
    if g.topology_gate_ref.is_empty() {
        return TopologyGateResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_TOPOLOGY_GATE_MISSING.into(),
            topology_gate_ref: String::new(),
            topology: g.topology.clone(),
        };
    }
    if let Some(r) = topology_gate_ref {
        if r != g.topology_gate_ref {
            return TopologyGateResult {
                blocked: true,
                status: "blocked".into(),
                reason_code: REASON_TOPOLOGY_GATE_BLOCKED.into(),
                topology_gate_ref: g.topology_gate_ref.clone(),
                topology: g.topology.clone(),
            };
        }
    }
    if g.topology_gate_status != "pass" {
        return TopologyGateResult {
            blocked: true,
            status: "blocked".into(),
            reason_code: REASON_TOPOLOGY_GATE_BLOCKED.into(),
            topology_gate_ref: g.topology_gate_ref.clone(),
            topology: g.topology.clone(),
        };
    }
    TopologyGateResult {
        blocked: false,
        status: "pass".into(),
        reason_code: String::new(),
        topology_gate_ref: g.topology_gate_ref.clone(),
        topology: g.topology.clone(),
    }
}

/// Load fixture graph from JSON path (v1.6.7 compatible projection).
pub fn load_gitscope_fixture(path: &Path) -> Result<GitScopeGraph, String> {
    let raw = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
    serde_json::from_str(&raw).map_err(|e| format!("gitscope_fixture_parse:{e}"))
}

fn simple_hash(s: &str) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for b in s.as_bytes() {
        h ^= u64::from(*b);
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn three_topo() {
        let d = tempdir().unwrap();
        for t in [
            TopologyKind::SingleRepo,
            TopologyKind::Monorepo,
            TopologyKind::MultiGitWorkspace,
        ] {
            let g = build_gitscope(d.path(), t);
            assert_eq!(g.topology, t.as_str());
            assert!(!g.topology_gate_ref.is_empty());
            assert_eq!(g.topology_gate_status, "pass");
            assert!(!g.nodes.is_empty());
        }
    }

    #[test]
    fn missing_topology_blocks_implement() {
        let r = require_topology_gate(None, None);
        assert!(r.blocked);
        assert_eq!(r.reason_code, REASON_TOPOLOGY_GATE_MISSING);
    }
}
