"""QA precision artifacts for Beacon v1.1.10."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug

DEFAULT_AUTO_ACCEPT_THRESHOLD = 0.85
DEFAULT_REVIEW_THRESHOLD = 0.60


def feature_qa_ac_closure_path(project_root: Path, *, feature: str) -> Path:
    return project_root / ".beacon" / "qa" / "features" / feature_slug(feature) / "ac-closure.json"


def feature_qa_scorecard_path(project_root: Path, *, feature: str) -> Path:
    return project_root / ".beacon" / "qa" / "features" / feature_slug(feature) / "scorecard.json"


def qa_calibration_model_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "qa-calibration" / "latest.json"


def qa_audit_label_path(project_root: Path, *, run_id: str, scenario_id: str) -> Path:
    return project_root / ".beacon" / "state" / "qa-audits" / run_id / f"{scenario_id}.json"


def load_feature_qa_scorecard(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(feature_qa_scorecard_path(project_root, feature=feature), {})
    return payload if isinstance(payload, dict) else {}


def load_feature_qa_ac_closure(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(feature_qa_ac_closure_path(project_root, feature=feature), {})
    return payload if isinstance(payload, dict) else {}


def load_qa_calibration_model(project_root: Path) -> dict[str, Any]:
    payload = read_json(qa_calibration_model_path(project_root), {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("model_type", "identity")
    payload.setdefault(
        "risk_bands",
        {
            "auto_accept": DEFAULT_AUTO_ACCEPT_THRESHOLD,
            "review_required": DEFAULT_REVIEW_THRESHOLD,
        },
    )
    return payload


def load_qa_audit_label(project_root: Path, *, run_id: str, scenario_id: str) -> dict[str, Any]:
    payload = read_json(qa_audit_label_path(project_root, run_id=run_id, scenario_id=scenario_id), {})
    return payload if isinstance(payload, dict) else {}


def write_qa_audit_label(project_root: Path, *, run_id: str, scenario_id: str, payload: dict[str, Any]) -> Path:
    path = qa_audit_label_path(project_root, run_id=run_id, scenario_id=scenario_id)
    write_json(path, payload)
    return path


def write_feature_qa_ac_closure(project_root: Path, *, feature: str, payload: dict[str, Any]) -> Path:
    path = feature_qa_ac_closure_path(project_root, feature=feature)
    write_json(path, payload)
    return path


def write_feature_qa_scorecard(project_root: Path, *, feature: str, payload: dict[str, Any]) -> Path:
    path = feature_qa_scorecard_path(project_root, feature=feature)
    write_json(path, payload)
    return path


def _label_correctness(label: str) -> float | None:
    normalized = str(label or "").strip().lower()
    mapping = {
        "true_pass": 1.0,
        "true_block": 1.0,
        "false_pass": 0.0,
        "false_block": 0.0,
    }
    return mapping.get(normalized)


def _collect_scenario_results(project_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((project_root / ".beacon" / "qa" / "features").glob("*/status.json")):
        payload = read_json(path, {})
        if not isinstance(payload, dict):
            continue
        run_id = str(payload.get("run_id") or "").strip()
        feature_slug_value = str(payload.get("feature_slug") or "").strip()
        scenarios = payload.get("scenario_results_v2") if isinstance(payload.get("scenario_results_v2"), list) else []
        for item in scenarios:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    **item,
                    "run_id": run_id,
                    "feature_slug": str(item.get("feature_slug") or feature_slug_value),
                }
            )
    return rows


def refresh_qa_calibration_model(project_root: Path) -> dict[str, Any]:
    scenario_rows = _collect_scenario_results(project_root)
    by_key = {
        (str(item.get("run_id") or ""), str(item.get("scenario_id") or "")): item
        for item in scenario_rows
        if str(item.get("run_id") or "").strip() and str(item.get("scenario_id") or "").strip()
    }
    samples: list[tuple[float, float]] = []
    audits_root = project_root / ".beacon" / "state" / "qa-audits"
    if audits_root.exists():
        for path in sorted(audits_root.glob("*/*.json")):
            payload = read_json(path, {})
            if not isinstance(payload, dict):
                continue
            run_id = str(path.parent.name)
            scenario_id = str(payload.get("scenario_id") or path.stem).strip()
            correctness = _label_correctness(str(payload.get("label") or ""))
            if correctness is None:
                continue
            scenario = by_key.get((run_id, scenario_id))
            if not scenario:
                continue
            confidence = float(scenario.get("confidence_raw") or scenario.get("confidence_calibrated") or 0.0)
            samples.append((confidence, correctness))

    risk_bands = {
        "auto_accept": DEFAULT_AUTO_ACCEPT_THRESHOLD,
        "review_required": DEFAULT_REVIEW_THRESHOLD,
    }
    bins: list[dict[str, Any]] = []
    ece = 0.0
    brier_score = 0.0
    model_type = "identity"
    if samples:
        model_type = "histogram-binning"
        bucket_count = 5
        for idx in range(bucket_count):
            lower = idx / float(bucket_count)
            upper = (idx + 1) / float(bucket_count)
            bucket: list[tuple[float, float]] = []
            for sample in samples:
                confidence = float(sample[0])
                in_bucket = lower <= confidence <= upper if idx == bucket_count - 1 else lower <= confidence < upper
                if in_bucket:
                    bucket.append(sample)
            if not bucket:
                continue
            predicted = sum(item[0] for item in bucket) / float(len(bucket))
            actual = sum(item[1] for item in bucket) / float(len(bucket))
            ece += abs(predicted - actual) * (len(bucket) / float(len(samples)))
            brier_score += sum((item[0] - item[1]) ** 2 for item in bucket)
            bins.append(
                {
                    "lower": round(lower, 4),
                    "upper": round(upper, 4),
                    "sample_count": len(bucket),
                    "predicted_mean": round(predicted, 4),
                    "empirical_accuracy": round(actual, 4),
                }
            )
        brier_score = brier_score / float(len(samples))
        for item in sorted(samples):
            confidence, correctness = item
            if correctness == 1.0:
                if confidence >= 0.85:
                    risk_bands["auto_accept"] = min(risk_bands["auto_accept"], round(confidence, 4))
                if confidence >= 0.60:
                    risk_bands["review_required"] = min(risk_bands["review_required"], round(confidence, 4))

    payload = {
        "schema_version": "1.0",
        "model_type": model_type,
        "trained_at": now_iso() if samples else "",
        "training_sample_count": len(samples),
        "ece": round(ece, 4),
        "brier_score": round(brier_score, 4),
        "risk_bands": risk_bands,
        "bins": bins,
    }
    write_json(qa_calibration_model_path(project_root), payload)
    return payload
