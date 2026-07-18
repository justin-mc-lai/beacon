//! stagnation-report.v1 bound to TraceSpine event range (AC-117/118/134).

use crate::trace_spine::TraceSpine;
use serde::{Deserialize, Serialize};

pub const SCHEMA_STAGNATION: &str = "stagnation-report.v1";
pub const REASON_STAGNATION_NO_TRACE: &str = "stagnation_requires_trace_run_id";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraceEventRange {
    pub from_seq: u64,
    pub to_seq: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StagnationReport {
    pub schema: String,
    pub run_id: String,
    pub kind: String,
    pub reason_code: String,
    pub trace_event_range: TraceEventRange,
    pub pattern_refs: Vec<String>,
    pub catalog_refs: Vec<String>,
    pub detected: bool,
}

/// Detect simple stagnation from repeated failure/output summaries in TraceSpine.
pub fn detect_stagnation(spine: &TraceSpine) -> Result<StagnationReport, String> {
    if spine.events.is_empty() {
        return Err(REASON_STAGNATION_NO_TRACE.into());
    }
    let from = spine.events.first().map(|e| e.seq).unwrap_or(1);
    let to = spine.events.last().map(|e| e.seq).unwrap_or(from);

    // repeat_failure: consecutive failure events
    let mut fail_streak = 0u32;
    let mut last_summary = String::new();
    let mut labor_streak = 0u32;
    for ev in &spine.events {
        if ev.event_type == "failure" || ev.summary.contains("fail") {
            fail_streak += 1;
        } else {
            fail_streak = 0;
        }
        if ev.summary == last_summary && !last_summary.is_empty() {
            labor_streak += 1;
        } else {
            labor_streak = 0;
        }
        last_summary = ev.summary.clone();
    }

    let (detected, kind, reason) = if fail_streak >= 2 {
        (true, "repeat_failure", "stagnation_repeat_failure")
    } else if labor_streak >= 2 {
        (true, "repeat_labor", "stagnation_repeat_labor")
    } else if spine.events.len() >= 5 {
        // plateau heuristic: many events without stop
        let has_progress = spine.events.iter().any(|e| e.event_type == "output" && e.summary.contains("progress"));
        if !has_progress {
            (true, "plateau", "stagnation_plateau")
        } else {
            (false, "none", "")
        }
    } else {
        (false, "none", "")
    };

    Ok(StagnationReport {
        schema: SCHEMA_STAGNATION.into(),
        run_id: spine.run_id.clone(),
        kind: kind.into(),
        reason_code: reason.into(),
        trace_event_range: TraceEventRange {
            from_seq: from,
            to_seq: to,
        },
        pattern_refs: if detected {
            vec![format!("pattern:{kind}")]
        } else {
            vec![]
        },
        catalog_refs: if detected {
            vec!["failure_catalog:v1".into()]
        } else {
            vec![]
        },
        detected,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::trace_spine::{TraceContext, TraceSpine};

    #[test]
    fn requires_events() {
        let s = TraceSpine::create("r", TraceContext::new("r"));
        assert!(detect_stagnation(&s).is_err());
    }

    #[test]
    fn repeat_failure() {
        let ctx = TraceContext::new("r").with_bindings("b", "d", "i", "t", "x");
        let mut s = TraceSpine::create("r", ctx);
        s.append("failure", "fail A", "e1").unwrap();
        s.append("failure", "fail B", "e2").unwrap();
        let r = detect_stagnation(&s).unwrap();
        assert!(r.detected);
        assert_eq!(r.kind, "repeat_failure");
        assert_eq!(r.trace_event_range.from_seq, 1);
        assert_eq!(r.trace_event_range.to_seq, 2);
    }
}
