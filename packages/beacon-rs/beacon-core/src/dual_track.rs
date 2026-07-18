//! Dual-track isolation: track_v1 (production Beacon) vs track_v2 (Loom evolution).
//! Mixed changes without admission → dual_track_mixed_source (TC-148 / AC-147+).

use serde::{Deserialize, Serialize};

pub const REASON_DUAL_TRACK_MIXED: &str = "dual_track_mixed_source";
pub const REASON_CROSS_TRACK_FALLBACK: &str = "cross_track_fallback_forbidden";
pub const REASON_EARLY_DEFAULT_V2: &str = "early_default_beacon_v2_forbidden";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Track {
    V1,
    V2,
}

impl Track {
    pub fn as_str(self) -> &'static str {
        match self {
            Track::V1 => "track_v1",
            Track::V2 => "track_v2",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s.trim().to_ascii_lowercase().as_str() {
            "v1" | "track_v1" | "beacon" | "1.6.7" | "v1.6.7" => Some(Track::V1),
            "v2" | "track_v2" | "loom" | "2.0.0" | "v2.0.0" | "beacon-v2" => Some(Track::V2),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PathTrackHit {
    pub path: String,
    pub track: Track,
}

/// Classify a repo-relative path into a track (heuristic contract for CI path filters).
pub fn classify_path(path: &str) -> Option<Track> {
    let p = path.replace('\\', "/");
    if p.starts_with("packages/beacon-rs/")
        || p.starts_with("skills/loom/")
        || p.contains("/v2.0.0/")
        || p.contains("docs/beacon/v2.")
        || p.starts_with("loom/")
    {
        return Some(Track::V2);
    }
    if p.starts_with("beacon/")
        || p.starts_with("skills/beacon/")
        || p.contains("/v1.6.")
        || p.starts_with("tests/test_v167")
        || p.starts_with("tests/test_v16")
    {
        return Some(Track::V1);
    }
    None
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DualTrackAdmission {
    pub ok: bool,
    pub blocked: bool,
    pub reason_code: String,
    pub tracks_present: Vec<String>,
    pub hits: Vec<PathTrackHit>,
}

/// Fail-closed when a single change set mixes track_v1 and track_v2 without admission.
pub fn admit_path_set(paths: &[&str], admitted_mixed: bool) -> DualTrackAdmission {
    let mut hits = Vec::new();
    let mut has_v1 = false;
    let mut has_v2 = false;
    for p in paths {
        if let Some(t) = classify_path(p) {
            match t {
                Track::V1 => has_v1 = true,
                Track::V2 => has_v2 = true,
            }
            hits.push(PathTrackHit {
                path: (*p).to_string(),
                track: t,
            });
        }
    }
    let mixed = has_v1 && has_v2;
    let blocked = mixed && !admitted_mixed;
    DualTrackAdmission {
        ok: !blocked,
        blocked,
        reason_code: if blocked {
            REASON_DUAL_TRACK_MIXED.into()
        } else {
            String::new()
        },
        tracks_present: {
            let mut t = Vec::new();
            if has_v1 {
                t.push(Track::V1.as_str().into());
            }
            if has_v2 {
                t.push(Track::V2.as_str().into());
            }
            t
        },
        hits,
    }
}

/// v2 path must not silently fall back to v1 runtime (TC-062b).
pub fn forbid_cross_track_fallback(active: Track, fallback: Option<Track>) -> Result<(), String> {
    match (active, fallback) {
        (Track::V2, Some(Track::V1)) => Err(REASON_CROSS_TRACK_FALLBACK.into()),
        _ => Ok(()),
    }
}

/// W4: default BEACON_V2=1 / loom-as-default-beacon forbidden until human GO.
pub fn early_default_v2_forbidden(env_beacon_v2: Option<&str>, claim_loom_replaces_beacon: bool) -> DualTrackAdmission {
    let env_on = matches!(
        env_beacon_v2.map(|s| s.trim()),
        Some("1") | Some("true") | Some("TRUE") | Some("yes")
    );
    let blocked = env_on || claim_loom_replaces_beacon;
    DualTrackAdmission {
        ok: !blocked,
        blocked,
        reason_code: if blocked {
            REASON_EARLY_DEFAULT_V2.into()
        } else {
            String::new()
        },
        tracks_present: vec![],
        hits: vec![],
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mixed_without_admission_blocks() {
        let r = admit_path_set(
            &["beacon/utils/x.py", "packages/beacon-rs/beacon-core/src/lib.rs"],
            false,
        );
        assert!(r.blocked);
        assert_eq!(r.reason_code, REASON_DUAL_TRACK_MIXED);
    }

    #[test]
    fn mixed_with_admission_ok() {
        let r = admit_path_set(
            &["beacon/utils/x.py", "packages/beacon-rs/beacon-core/src/lib.rs"],
            true,
        );
        assert!(!r.blocked);
    }

    #[test]
    fn no_v2_to_v1_fallback() {
        assert!(forbid_cross_track_fallback(Track::V2, Some(Track::V1)).is_err());
        assert!(forbid_cross_track_fallback(Track::V2, None).is_ok());
    }
}
