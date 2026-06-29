//! P2 gate skeleton tests — AC-013 (gate_results write) + AC-020 (spine gate read).

use beacon_gate::{GateEngine, GateType, Verdict};
use beacon_store::{BeaconStore, FeatureDao, ProjectDao};
use beacon_core::RunStatus;
use beacon_store::RunDao;

fn seed_feature(store: &BeaconStore) -> i64 {
    let conn = store.connection();
    let pid = ProjectDao::insert(conn, "/tmp/p", "p").unwrap();
    FeatureDao::insert(conn, pid, "demo", "v2.0.0", "frozen", None).unwrap()
}

// ---- AC-013 gate evaluation writes gate_results ----

#[test]
fn tc013_gate_evaluate_writes_gate_results() {
    let store = BeaconStore::open_in_memory().unwrap();
    seed_feature(&store);
    let engine = GateEngine::new(&store);
    let id = engine
        .evaluate("demo", "v2.0.0", GateType::Qa, Verdict::Blocked, vec!["test_failed".into()])
        .unwrap();
    assert!(id > 0);
}

#[test]
fn tc013_gate_evaluate_pass_no_reason_codes() {
    let store = BeaconStore::open_in_memory().unwrap();
    seed_feature(&store);
    let engine = GateEngine::new(&store);
    let id = engine
        .evaluate("demo", "v2.0.0", GateType::TruthFreeze, Verdict::Pass, vec![])
        .unwrap();
    assert!(id > 0);
}

// ---- AC-020 spine gate reads latest verdict ----

#[test]
fn tc020_spine_gate_reads_latest_verdict() {
    let store = BeaconStore::open_in_memory().unwrap();
    seed_feature(&store);
    let engine = GateEngine::new(&store);
    // write two verdicts; latest should be returned
    engine
        .evaluate("demo", "v2.0.0", GateType::Qa, Verdict::Fail, vec!["broken".into()])
        .unwrap();
    engine
        .evaluate("demo", "v2.0.0", GateType::Qa, Verdict::Pass, vec![])
        .unwrap();
    let latest = engine.latest("demo", "v2.0.0", GateType::Qa).unwrap().expect("gate result");
    assert_eq!(latest.gate_type, "qa");
    assert_eq!(latest.verdict, "pass");
}

#[test]
fn tc020_spine_gate_none_when_no_results() {
    let store = BeaconStore::open_in_memory().unwrap();
    seed_feature(&store);
    let engine = GateEngine::new(&store);
    let latest = engine.latest("demo", "v2.0.0", GateType::Release).unwrap();
    assert!(latest.is_none());
}

// ---- GateType parse ----

#[test]
fn gate_type_parse_roundtrip() {
    for g in [GateType::TruthFreeze, GateType::Qa, GateType::Release, GateType::Implement] {
        let s = g.as_str();
        assert_eq!(GateType::parse(s).unwrap(), g);
    }
    assert!(GateType::parse("bogus").is_err());
}
