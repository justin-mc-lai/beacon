use beacon_core::{
    admit_path_set, early_default_v2_forbidden, forbid_cross_track_fallback, HarnessSurface,
    TraceContext, TraceSpine, Track, REASON_DUAL_TRACK_MIXED, REASON_EARLY_DEFAULT_V2,
};

#[test]
fn harness_six_abilities() {
    let s = HarnessSurface::v2_default();
    assert_eq!(s.abilities.len(), 6);
    assert!(HarnessSurface::is_public("implement"));
    assert!(!HarnessSurface::is_public("doctor"));
}

#[test]
fn dual_track_and_early_default() {
    let mixed = admit_path_set(
        &["skills/beacon/beacon-goal/SKILL.md", "skills/loom/loom-goal/SKILL.md"],
        false,
    );
    assert!(mixed.blocked);
    assert_eq!(mixed.reason_code, REASON_DUAL_TRACK_MIXED);
    assert!(forbid_cross_track_fallback(Track::V2, Some(Track::V1)).is_err());
    let early = early_default_v2_forbidden(Some("1"), false);
    assert!(early.blocked);
    assert_eq!(early.reason_code, REASON_EARLY_DEFAULT_V2);
}

#[test]
fn trace_spine_completeness() {
    let mut spine = TraceSpine::create("run-1", TraceContext::new("run-1"));
    spine.append("decision", "start", "ev/1").unwrap();
    spine.append("output", "done", "ev/2").unwrap();
    spine.completeness_gate("qa-evidence").unwrap();
}
