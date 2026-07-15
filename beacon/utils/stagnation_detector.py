"""Loop stagnation detector — deterministic detection over agent trace events.

Reads agent trace JSONL, cross-references pattern registry and failure catalog,
and produces a stagnation-report.v1 for governor consumption.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.agent_trace import read_trace_events
from beacon.utils.loop_failure_catalog import catalog_path, parse_failure_catalog, validate_failure_catalog
from beacon.utils.loop_patterns import registry_path, validate_pattern_registry

SCHEMA_VERSION = "stagnation-report.v1"

DEFAULT_PARAMS = {
    "window_size": 5,
    "repeat_threshold": 3,
    "labor_window": 4,
    "labor_threshold": 3,
    "summary_prefix_len": 20,
    "plateau_min_events": 3,
    "plateau_summary_similarity": 0.8,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two strings (word-level)."""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def _detect_repeat_failure(
    events: list[dict[str, Any]],
    *,
    window_size: int = 5,
    repeat_threshold: int = 3,
) -> list[dict[str, Any]]:
    """Detect repeat_failure: same reason_code appears >= threshold times in a sliding window."""
    findings: list[dict[str, Any]] = []
    failure_events = [e for e in events if e.get("event_type") == "failure" and e.get("reason_code")]
    if len(failure_events) < repeat_threshold:
        return findings
    for i in range(len(failure_events)):
        window = failure_events[i : i + window_size]
        if len(window) < repeat_threshold:
            break
        reason_codes = [e.get("reason_code", "") for e in window]
        counter = Counter(reason_codes)
        for reason_code, count in counter.items():
            if count >= repeat_threshold:
                findings.append({
                    "stagnation_type": "repeat_failure",
                    "reason_code": reason_code,
                    "severity": "S1",
                    "window_events": len(window),
                    "matched_count": count,
                    "pattern_ref": "",
                    "failure_ref": "",
                    "recommendation": "retry-with-backoff",
                })
    return findings


def _detect_repeat_labor(
    events: list[dict[str, Any]],
    *,
    labor_window: int = 4,
    labor_threshold: int = 3,
    summary_prefix_len: int = 20,
) -> list[dict[str, Any]]:
    """Detect repeat_labor: same (feature_slug, event_type, summary_prefix) repeated >= threshold."""
    findings: list[dict[str, Any]] = []
    iteration_events = [
        e for e in events
        if e.get("event_type") in ("decision", "failure", "retry", "output")
    ]
    if len(iteration_events) < labor_threshold:
        return findings
    for i in range(len(iteration_events)):
        window = iteration_events[i : i + labor_window]
        if len(window) < labor_threshold:
            break
        fingerprints: list[str] = []
        for e in window:
            feature_slug = str(e.get("feature_slug") or e.get("payload", {}).get("feature_slug") or "")
            event_type = str(e.get("event_type") or "")
            summary = str(e.get("summary") or "")
            prefix = summary[:summary_prefix_len]
            fingerprints.append(f"{feature_slug}|{event_type}|{prefix}")
        counter = Counter(fingerprints)
        for fp, count in counter.items():
            if count >= labor_threshold:
                parts = fp.split("|", 2)
                findings.append({
                    "stagnation_type": "repeat_labor",
                    "reason_code": "repeat_labor_detected",
                    "severity": "S2",
                    "window_events": len(window),
                    "matched_count": count,
                    "pattern_ref": "",
                    "failure_ref": "",
                    "recommendation": "skip-and-continue",
                    "fingerprint": fp,
                    "feature_slug": parts[0] if len(parts) > 0 else "",
                    "event_type": parts[1] if len(parts) > 1 else "",
                })
    return findings


def _detect_plateau(
    events: list[dict[str, Any]],
    *,
    plateau_min_events: int = 3,
    plateau_summary_similarity: float = 0.8,
) -> list[dict[str, Any]]:
    """Detect plateau: consecutive output events with iteration increasing, reason_code empty, summary similar."""
    findings: list[dict[str, Any]] = []
    output_events = [
        e for e in events
        if e.get("event_type") == "output" and not e.get("reason_code")
    ]
    if len(output_events) < plateau_min_events:
        return findings
    consecutive: list[dict[str, Any]] = []
    for i, event in enumerate(output_events):
        if not consecutive:
            consecutive = [event]
            continue
        prev = consecutive[-1]
        prev_iter = int(prev.get("iteration") or 0)
        curr_iter = int(event.get("iteration") or 0)
        if curr_iter > prev_iter:
            sim = _jaccard_similarity(
                str(prev.get("summary") or ""),
                str(event.get("summary") or ""),
            )
            if sim >= plateau_summary_similarity:
                consecutive.append(event)
            else:
                if len(consecutive) >= plateau_min_events:
                    findings.append(_make_plateau_finding(consecutive))
                consecutive = [event]
        else:
            if len(consecutive) >= plateau_min_events:
                findings.append(_make_plateau_finding(consecutive))
            consecutive = [event]
    if len(consecutive) >= plateau_min_events:
        findings.append(_make_plateau_finding(consecutive))
    return findings


def _make_plateau_finding(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "stagnation_type": "plateau",
        "reason_code": "plateau_detected",
        "severity": "S3",
        "window_events": len(events),
        "matched_count": len(events),
        "pattern_ref": "",
        "failure_ref": "",
        "recommendation": "break-on-plateau",
        "iteration_range": [
            int(events[0].get("iteration") or 0),
            int(events[-1].get("iteration") or 0),
        ],
    }


def _correlate_upstream(
    project_root: Path,
    *,
    version: str,
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    """Cross-reference pattern registry and failure catalog."""
    registry = validate_pattern_registry(registry_path(project_root, version=version))
    catalog = validate_failure_catalog(catalog_path(project_root, version=version))

    # Load failure catalog entries for matching
    catalog_entries: list[dict[str, str]] = []
    cat_path = catalog_path(project_root, version=version)
    if cat_path.is_file():
        catalog_entries = parse_failure_catalog(cat_path.read_text(encoding="utf-8"))

    for finding in findings:
        # Try to match failure_ref from catalog
        reason_code = finding.get("reason_code", "")
        for entry in catalog_entries:
            if entry.get("id") == reason_code or reason_code in entry.get("symptom", ""):
                finding["failure_ref"] = entry.get("id", "")
                break
        # Try to match pattern_ref from registry
        stag_type = finding.get("stagnation_type", "")
        patterns = registry.get("patterns", []) if isinstance(registry.get("patterns"), list) else []
        for pattern in patterns:
            if isinstance(pattern, dict):
                pattern_id = str(pattern.get("id") or "")
                if stag_type in pattern_id or pattern_id in stag_type:
                    finding["pattern_ref"] = pattern_id
                    break

    return {
        "pattern_registry_status": str(registry.get("status") or "warn"),
        "failure_catalog_status": str(catalog.get("status") or "warn"),
        "token_budget_status": "ok",
    }


def detect_stagnation(
    project_root: Path,
    *,
    run_id: str,
    version: str = "",
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run stagnation detection on a trace and return a stagnation-report.v1.

    Deterministic: same trace + same params → same report.
    """
    root = project_root.expanduser().resolve()
    p = {**DEFAULT_PARAMS, **(params or {})}

    events = read_trace_events(root, run_id)
    if not events:
        return {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "detected_at": _now_iso(),
            "status": "clean",
            "findings": [],
            "upstream_signals": {
                "pattern_registry_status": "warn",
                "failure_catalog_status": "warn",
                "token_budget_status": "ok",
            },
            "event_count": 0,
        }

    # Run all three detectors
    findings: list[dict[str, Any]] = []
    findings.extend(_detect_repeat_failure(
        events,
        window_size=p["window_size"],
        repeat_threshold=p["repeat_threshold"],
    ))
    findings.extend(_detect_repeat_labor(
        events,
        labor_window=p["labor_window"],
        labor_threshold=p["labor_threshold"],
        summary_prefix_len=p["summary_prefix_len"],
    ))
    findings.extend(_detect_plateau(
        events,
        plateau_min_events=p["plateau_min_events"],
        plateau_summary_similarity=p["plateau_summary_similarity"],
    ))

    # Correlate with upstream
    upstream_signals = _correlate_upstream(
        root,
        version=version,
        findings=findings,
    ) if version else {
        "pattern_registry_status": "warn",
        "failure_catalog_status": "warn",
        "token_budget_status": "ok",
    }

    status = "stagnant" if findings else "clean"

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "detected_at": _now_iso(),
        "status": status,
        "findings": findings,
        "upstream_signals": upstream_signals,
        "event_count": len(events),
        "params": p,
    }


def stagnation_detection_signal(project_root: Path, *, version: str = "") -> dict[str, Any]:
    """Return a signal dict for doctor loop-audit integration."""
    root = project_root.expanduser().resolve()
    traces_dir = root / ".beacon" / "traces"
    if not traces_dir.is_dir() or not any(traces_dir.glob("*.jsonl")):
        return {
            "signal": "stagnation_detection",
            "status": "missing",
            "reason_code": "stagnation_no_traces",
            "findings": [{"message": "no agent trace files under .beacon/traces/"}],
        }
    # Check if stagnation_detector module is available (it always is since we're in it)
    return {
        "signal": "stagnation_detection",
        "status": "pass",
        "reason_code": "",
        "findings": [],
    }
