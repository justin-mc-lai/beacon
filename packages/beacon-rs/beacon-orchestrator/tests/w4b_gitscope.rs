//! W4b GitScope topology gates AC-171–173.

use beacon_core::branch_context::BranchContext;
use beacon_orchestrator::{
    apply_gitscope_to_branch_context, build_gitscope, require_topology_gate, TopologyKind,
    REASON_TOPOLOGY_GATE_MISSING,
};
use tempfile::tempdir;

#[test]
fn tc171_gsg_parity() {
    let d = tempdir().unwrap();
    let g = build_gitscope(d.path(), TopologyKind::SingleRepo);
    assert_eq!(g.schema, "gitscope-graph.v1");
    assert!(!g.topology_gate_ref.is_empty());
    let bc = BranchContext::new("r1", "/c", d.path().to_string_lossy(), d.path().to_string_lossy(), "main")
        .mark_admitted();
    let ext = apply_gitscope_to_branch_context(bc, &g).unwrap();
    assert_eq!(ext.topology, "single_repo");
}

#[test]
fn tc172_three_topo() {
    let d = tempdir().unwrap();
    for t in [
        TopologyKind::SingleRepo,
        TopologyKind::Monorepo,
        TopologyKind::MultiGitWorkspace,
    ] {
        let g = build_gitscope(d.path(), t);
        assert_eq!(g.topology, t.as_str());
        let gate = require_topology_gate(Some(&g), Some(&g.topology_gate_ref));
        assert!(!gate.blocked, "{:?}", gate);
    }
}

#[test]
fn tc173_missing_topology() {
    let r = require_topology_gate(None, None);
    assert!(r.blocked);
    assert_eq!(r.reason_code, REASON_TOPOLOGY_GATE_MISSING);
}
