"""v1.1.9 learning-plane extraction and baseline helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from beacon.utils.qa_precision import refresh_qa_calibration_model
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.v115_delivery import ensure_eval_lab_skeleton

DEFAULT_SUBJECT_SURFACE = [
    "qa_policy",
    "design_policy",
    "contract_policy",
    "rewrite_policy",
    "debug_policy",
    "benchmark_policy",
]
DEFAULT_PROGRAM_SURFACE = [
    "benchmark_corpus",
    "decision_scorecard",
    "keep_discard_ledger",
]
FORBIDDEN_SUBJECT_SURFACE = [
    "project_skill_command_template",
    "project_ops_command",
    "repository_code_mutation",
    "release_verdict_override",
    "secret_state",
    "takeover_architecture_truth",
]
POLICY_FAMILY_TOPICS = {
    "qa_policy": [
        "scenario_expansion",
        "evidence_sufficiency",
        "false_complete_reduction",
        "continue_decision_calibration",
    ],
    "design_policy": [
        "design_brief_extraction",
        "design_system_normalization",
        "guideline_severity_mapping",
        "review_thresholds",
    ],
    "contract_policy": [
        "readonly_contract_inputs",
        "service_slice_alignment",
        "evidence_contract_match",
    ],
    "rewrite_policy": [
        "requirement_rewrite_inputs",
        "artifact_update_obligations",
        "version_research_writeback",
    ],
    "debug_policy": [
        "failure_streak_recovery",
        "structured_debug_repair",
        "recovery_handoff",
    ],
    "benchmark_policy": [
        "benchmark_corpus_curation",
        "keep_discard_scoring",
        "false_complete_rate",
    ],
}


def _learning_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "learning"


def _benchmark_corpus_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "eval-lab" / "benchmark-corpus.json"


def _keep_discard_log_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "eval-lab" / "keep-discard-log.jsonl"


def _evo_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "evo"


def _evo_scorecard_path(project_root: Path) -> Path:
    return _evo_root(project_root) / "scorecards" / "latest.json"


def _evo_ledger_path(project_root: Path) -> Path:
    return _evo_root(project_root) / "ledgers" / "latest.json"


def _evo_decision_engine_path(project_root: Path) -> Path:
    return _evo_root(project_root) / "decision-engine.json"


def _evo_ledger_log_path(project_root: Path) -> Path:
    return _evo_root(project_root) / "ledger.jsonl"


def _evo_experiments_root(project_root: Path) -> Path:
    return _evo_root(project_root) / "experiments"


def _evo_latest_experiment_path(project_root: Path) -> Path:
    return _evo_experiments_root(project_root) / "latest.json"


def requirement_rewrite_input_path(project_root: Path, *, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / ".machine" / "execution" / f"requirement-rewrite-input-{feature_slug(feature)}.json"


def execution_baseline_path(project_root: Path) -> Path:
    return _learning_root(project_root) / "execution-baseline.json"


def keep_discard_engine_path(project_root: Path) -> Path:
    return _evo_decision_engine_path(project_root)


def keep_discard_scorecard_path(project_root: Path) -> Path:
    return _evo_scorecard_path(project_root)


def load_keep_discard_engine(project_root: Path) -> dict[str, Any]:
    return _read_json(keep_discard_engine_path(project_root))


def load_latest_evo_experiment(project_root: Path) -> dict[str, Any]:
    return _read_json(_evo_latest_experiment_path(project_root))


def _normalize_text_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values.strip()] if values.strip() else []
    if not isinstance(values, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in values:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _read_json(path: Path) -> dict[str, Any]:
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def ensure_evo_skeleton(project_root: Path) -> None:
    ensure_eval_lab_skeleton(project_root, apply=True)
    evo_root = _evo_root(project_root)
    for rel in ("experiments", "ledgers", "scorecards"):
        (evo_root / rel).mkdir(parents=True, exist_ok=True)
    if not _evo_decision_engine_path(project_root).exists():
        write_json(
            _evo_decision_engine_path(project_root),
            {
                "schema_version": "1.0",
                "generated_at": now_iso(),
                "main_kpi": "false_complete_rate",
                "supporting_metrics": [
                    "evidence_coverage",
                    "recovery_success_rate",
                    "operator_load",
                    "cost_per_trial",
                ],
                "decision_thresholds": {
                    "keep": 75,
                    "discard": 35,
                },
                "budget_contract": {
                    "max_runtime_minutes": 30,
                    "max_iterations": 3,
                    "max_command_count": 12,
                    "max_evidence_budget": 20,
                },
                "subject_surface": DEFAULT_SUBJECT_SURFACE,
                "program_surface": DEFAULT_PROGRAM_SURFACE,
                "forbidden_subject_surface": FORBIDDEN_SUBJECT_SURFACE,
                "policy_topics": POLICY_FAMILY_TOPICS,
            },
        )


def load_learning_plane_contract(project_root: Path) -> dict[str, Any]:
    payload = _read_json(_evo_decision_engine_path(project_root))
    if not payload:
        payload = {
            "schema_version": "1.0",
            "main_kpi": "false_complete_rate",
            "supporting_metrics": [
                "evidence_coverage",
                "recovery_success_rate",
                "operator_load",
                "cost_per_trial",
            ],
            "budget_contract": {
                "max_runtime_minutes": 30,
                "max_iterations": 3,
                "max_command_count": 12,
                "max_evidence_budget": 20,
            },
        }
    return {
        **payload,
        "subject_surface": _normalize_text_list(payload.get("subject_surface")) or list(DEFAULT_SUBJECT_SURFACE),
        "program_surface": _normalize_text_list(payload.get("program_surface")) or list(DEFAULT_PROGRAM_SURFACE),
        "forbidden_subject_surface": _normalize_text_list(payload.get("forbidden_subject_surface"))
        or list(FORBIDDEN_SUBJECT_SURFACE),
        "policy_topics": payload.get("policy_topics")
        if isinstance(payload.get("policy_topics"), dict)
        else dict(POLICY_FAMILY_TOPICS),
    }


def validate_learning_surface_mutation(
    project_root: Path,
    *,
    subject_surface: list[str] | None = None,
) -> dict[str, Any]:
    contract = load_learning_plane_contract(project_root)
    requested = _normalize_text_list(subject_surface)
    allowed = set(_normalize_text_list(contract.get("subject_surface")))
    forbidden = set(_normalize_text_list(contract.get("forbidden_subject_surface")))
    issues: list[dict[str, Any]] = []
    for item in requested:
        if item in forbidden:
            issues.append(
                {
                    "reason_code": "learning_surface_forbidden",
                    "surface": item,
                    "message": f"learning surface is forbidden: {item}",
                }
            )
        elif item not in allowed:
            issues.append(
                {
                    "reason_code": "learning_surface_unknown",
                    "surface": item,
                    "message": f"learning surface is outside the typed contract: {item}",
                }
            )
    return {
        "status": "blocked" if issues else "pass",
        "requested_subject_surface": requested,
        "allowed_subject_surface": sorted(allowed),
        "forbidden_subject_surface": sorted(forbidden),
        "issues": issues,
    }


def _technical_learning_payload(*, version: str, feature: str, archive_payload: dict[str, Any], archive_path: str) -> dict[str, Any]:
    artifact_updates = archive_payload.get("artifact_updates") if isinstance(archive_payload.get("artifact_updates"), dict) else {}
    required_updates = [name for name, value in artifact_updates.items() if isinstance(value, dict) and bool(value.get("required"))]
    verification = archive_payload.get("verification") if isinstance(archive_payload.get("verification"), list) else []
    verification_commands = [str(item.get("command") or "") for item in verification if isinstance(item, dict) and str(item.get("command") or "").strip()]
    known_risks = _normalize_text_list(archive_payload.get("known_risks"))
    rollback_notes = _normalize_text_list(archive_payload.get("rollback_notes"))
    modules_touched = _normalize_text_list(archive_payload.get("modules_touched"))
    changed_files = _normalize_text_list(archive_payload.get("changed_files"))
    config_changes = _normalize_text_list(archive_payload.get("config_changes"))
    env_changes = _normalize_text_list(archive_payload.get("env_changes"))
    feature_flags = _normalize_text_list(archive_payload.get("feature_flags"))

    prd_inputs: list[str] = []
    test_case_inputs: list[str] = []
    version_inputs: list[str] = []
    baseline_uplift: list[str] = []

    api_changes = archive_payload.get("api_changes") if isinstance(archive_payload.get("api_changes"), dict) else {}
    if not bool(api_changes.get("none", True)):
        prd_inputs.append("API changes detected: ensure PRD and contract sections reflect endpoint deltas.")
        test_case_inputs.append("API changes detected: add or rerun interface/contract/integration cases for affected endpoints.")
        baseline_uplift.append("When api_changes.none=false, require endpoint diff + verification evidence.")

    db_changes = archive_payload.get("db_changes") if isinstance(archive_payload.get("db_changes"), dict) else {}
    if not bool(db_changes.get("none", True)):
        prd_inputs.append("Data/storage changes detected: clarify migration intent and rollback impact in requirements.")
        test_case_inputs.append("Data/storage changes detected: add integration/exception/regression coverage for migrations and rollback paths.")
        baseline_uplift.append("When db_changes.none=false, require rollback_notes and data verification evidence.")

    if required_updates:
        version_inputs.append(f"Open artifact writeback obligations: {required_updates}")
        baseline_uplift.append("artifact_updates.required items must become explicit follow-up obligations before closure.")

    if not verification_commands:
        baseline_uplift.append("Every technical archive should record at least one verification command/evidence ref.")

    if config_changes or env_changes or feature_flags:
        test_case_inputs.append("Config/env/feature-flag changes detected: add smoke/regression coverage for toggled paths.")

    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "generated_at": now_iso(),
        "technical_archive_path": archive_path,
        "run_id": str(archive_payload.get("run_id") or ""),
        "modules_touched": modules_touched,
        "changed_files": changed_files,
        "known_risks": known_risks,
        "rollback_notes": rollback_notes,
        "artifact_update_obligations": required_updates,
        "verification_commands": verification_commands,
        "rewrite_targets": {
            "prd": prd_inputs,
            "test_case": test_case_inputs,
            "version_research": version_inputs,
        },
        "baseline_uplift_candidates": baseline_uplift,
        "benchmark_refs": [archive_path],
    }
    return payload


def write_requirement_rewrite_input(
    project_root: Path,
    *,
    version: str,
    feature: str,
    archive_payload: dict[str, Any],
    archive_path: str,
) -> dict[str, Any]:
    ensure_eval_lab_skeleton(project_root, apply=True)
    payload = _technical_learning_payload(
        version=version,
        feature=feature,
        archive_payload=archive_payload,
        archive_path=archive_path,
    )
    out = requirement_rewrite_input_path(project_root, version=version, feature=feature)
    write_json(out, payload)
    append_keep_discard_entry(
        project_root,
        source="technical-archive",
        entry_id=f"{feature_slug(feature)}:{payload.get('run_id') or 'no-run'}",
        recommendation="keep-review",
        rationale="technical archive extracted structured requirement rewrite inputs",
        refs=[archive_path, str(out.relative_to(project_root))],
    )
    refresh_learning_loop(project_root)
    return {**payload, "path": str(out.relative_to(project_root))}


def write_prototype_design_rewrite_input(
    project_root: Path,
    *,
    version: str,
    feature: str,
    review_payload: dict[str, Any],
    guideline_payload: dict[str, Any],
    benchmark_refs: list[str] | None = None,
) -> dict[str, Any]:
    ensure_eval_lab_skeleton(project_root, apply=True)
    feature_id = feature_slug(feature)
    out = requirement_rewrite_input_path(project_root, version=version, feature=feature)
    existing = _read_json(out)
    rewrite_targets = existing.get("rewrite_targets") if isinstance(existing.get("rewrite_targets"), dict) else {}
    baseline_candidates = _normalize_text_list(existing.get("baseline_uplift_candidates"))
    artifact_obligations = _normalize_text_list(existing.get("artifact_update_obligations"))
    verification_commands = _normalize_text_list(existing.get("verification_commands"))
    benchmark_rows = _normalize_text_list(existing.get("benchmark_refs"))

    rewrite_targets.setdefault("design_brief", [])
    rewrite_targets.setdefault("prototype_plan", [])
    rewrite_targets.setdefault("guideline_fix", [])

    findings = guideline_payload.get("findings") if isinstance(guideline_payload.get("findings"), list) else []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        rule = str(finding.get("rule") or "").strip()
        message = str(finding.get("message") or "").strip()
        if not rule:
            continue
        if rule == "url-reflects-state":
            rewrite_targets["prototype_plan"].append("Reflect tab/filter state in URL for design-governed prototype flows.")
        elif rule in {"generic-font-stack", "generic-font-contract"}:
            rewrite_targets["design_brief"].append("Strengthen typography direction and anti-generic font rules in the design brief.")
        else:
            rewrite_targets["guideline_fix"].append(f"Fix guideline rule `{rule}`: {message}")
        baseline_candidates.append(f"Design governance candidate: {rule} -> {message}")

    if not findings:
        baseline_candidates.append("Keep design-governed prototype review in the learning loop as a baseline policy.")

    artifact_obligations.extend(["design_brief", "design_system_contract", "web_guideline_review"])
    verification_commands.append(f"beacon prototype review \"{feature}\" --version {version}")
    benchmark_rows.extend(_normalize_text_list(benchmark_refs))

    payload = {
        **existing,
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_id,
        "version": version,
        "generated_at": now_iso(),
        "source_type": "prototype_design_review",
        "design_review_outcome": str(review_payload.get("design_review_outcome") or guideline_payload.get("design_review_outcome") or "pass"),
        "artifact_update_obligations": sorted(set(_normalize_text_list(artifact_obligations))),
        "verification_commands": sorted(set(_normalize_text_list(verification_commands))),
        "rewrite_targets": {
            key: sorted(set(_normalize_text_list(value)))
            for key, value in rewrite_targets.items()
        },
        "baseline_uplift_candidates": sorted(set(_normalize_text_list(baseline_candidates))),
        "benchmark_refs": sorted(set(_normalize_text_list(benchmark_rows))),
        "path": str(out.relative_to(project_root)),
    }
    write_json(out, payload)
    append_keep_discard_entry(
        project_root,
        source="prototype-design-review",
        entry_id=f"{feature_id}:{payload.get('design_review_outcome') or 'pass'}",
        recommendation="review" if findings else "keep",
        rationale="prototype design review generated structured next-iteration inputs",
        refs=[str(out.relative_to(project_root)), *payload.get("benchmark_refs", [])],
    )
    refresh_learning_loop(project_root)
    return {**payload, "path": str(out.relative_to(project_root))}


def append_keep_discard_entry(
    project_root: Path,
    *,
    source: str,
    entry_id: str,
    recommendation: str,
    rationale: str,
    refs: list[str] | None = None,
) -> None:
    ensure_evo_skeleton(project_root)
    path = _keep_discard_log_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": now_iso(),
        "source": str(source or "").strip(),
        "entry_id": str(entry_id or "").strip(),
        "recommendation": str(recommendation or "candidate").strip(),
        "rationale": str(rationale or "").strip(),
        "refs": _normalize_text_list(refs),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    _append_jsonl(_evo_ledger_log_path(project_root), entry)


def _collect_requirement_rewrite_inputs(project_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(project_root.glob("docs/beacon/*/.machine/execution/requirement-rewrite-input-*.json")):
        payload = _read_json(path)
        if payload:
            rows.append({**payload, "path": str(path.relative_to(project_root))})
    return rows


def refresh_benchmark_corpus(project_root: Path) -> dict[str, Any]:
    ensure_evo_skeleton(project_root)
    rewrite_inputs = _collect_requirement_rewrite_inputs(project_root)
    debug_issues: list[dict[str, Any]] = []
    qa_audit_inputs: list[dict[str, Any]] = []
    issues_root = project_root / ".beacon" / "debug" / "issues"
    if issues_root.exists():
        for path in sorted(issues_root.glob("*.json")):
            payload = _read_json(path)
            if payload:
                debug_issues.append({**payload, "path": str(path.relative_to(project_root))})
    audits_root = project_root / ".beacon" / "state" / "qa-audits"
    if audits_root.exists():
        for path in sorted(audits_root.glob("*/*.json")):
            payload = _read_json(path)
            if payload:
                qa_audit_inputs.append({**payload, "path": str(path.relative_to(project_root)), "run_id": path.parent.name})

    corpus = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "technical_archive_inputs": rewrite_inputs,
        "debug_issue_inputs": debug_issues,
        "qa_audit_inputs": qa_audit_inputs,
        "counts": {
            "technical_archive_inputs": len(rewrite_inputs),
            "debug_issue_inputs": len(debug_issues),
            "qa_audit_inputs": len(qa_audit_inputs),
        },
    }
    write_json(_benchmark_corpus_path(project_root), corpus)
    return corpus


def _candidate_id(category: str, text: str) -> str:
    digest = hashlib.sha256(f"{category}:{text}".encode("utf-8")).hexdigest()[:12]
    return f"{category}:{digest}"


def _build_learning_candidates(project_root: Path) -> list[dict[str, Any]]:
    rewrite_inputs = _collect_requirement_rewrite_inputs(project_root)
    buckets: dict[tuple[str, str], dict[str, Any]] = {}

    def _bucket(category: str, text: str) -> dict[str, Any]:
        key = (category, text)
        if key not in buckets:
            buckets[key] = {
                "candidate_id": _candidate_id(category, text),
                "category": category,
                "subject_surface": category,
                "program_surface": "benchmark_corpus",
                "text": text,
                "sources": [],
                "benchmark_refs": [],
                "features": set(),
                "versions": set(),
                "recurrence_count": 0,
                "verification_support": 0,
                "artifact_pressure": 0,
            }
        return buckets[key]

    for item in rewrite_inputs:
        feature = str(item.get("feature_slug") or item.get("feature") or "").strip()
        version = str(item.get("version") or "").strip()
        refs = _normalize_text_list(item.get("benchmark_refs"))
        obligations = _normalize_text_list(item.get("artifact_update_obligations"))
        verification_commands = _normalize_text_list(item.get("verification_commands"))
        for candidate in _normalize_text_list(item.get("baseline_uplift_candidates")):
            category = "design_policy" if str(item.get("source_type") or "") == "prototype_design_review" else "benchmark_policy"
            bucket = _bucket(category, candidate)
            bucket["sources"].append(
                {
                    "source_type": "technical_archive",
                    "feature": feature,
                    "version": version,
                    "path": str(item.get("path") or ""),
                }
            )
            bucket["benchmark_refs"].extend(refs)
            if feature:
                bucket["features"].add(feature)
            if version:
                bucket["versions"].add(version)
            bucket["recurrence_count"] += 1
            bucket["verification_support"] += 1 if verification_commands else 0
            bucket["artifact_pressure"] += len(obligations)
        rewrite_targets = item.get("rewrite_targets") if isinstance(item.get("rewrite_targets"), dict) else {}
        for section, rows in rewrite_targets.items():
            if not isinstance(rows, list):
                continue
            for candidate in _normalize_text_list(rows):
                category = "design_policy" if section in {"design_brief", "prototype_plan", "guideline_fix"} else "rewrite_policy"
                bucket = _bucket(category, f"[{section}] {candidate}")
                bucket["sources"].append(
                    {
                        "source_type": "technical_archive",
                        "feature": feature,
                        "version": version,
                        "path": str(item.get("path") or ""),
                    }
                )
                bucket["benchmark_refs"].extend(refs)
                if feature:
                    bucket["features"].add(feature)
                if version:
                    bucket["versions"].add(version)
                bucket["recurrence_count"] += 1
                bucket["verification_support"] += 1 if verification_commands else 0

    issues_root = project_root / ".beacon" / "debug" / "issues"
    if issues_root.exists():
        for path in sorted(issues_root.glob("*.json")):
            payload = _read_json(path)
            if not payload:
                continue
            reason_code = str(payload.get("reason_code") or "").strip()
            if not reason_code:
                continue
            candidate = f"Investigate recurring debug reason_code `{reason_code}` before next release."
            bucket = _bucket("debug_policy", candidate)
            bucket["sources"].append(
                {
                    "source_type": "debug_issue",
                    "issue_id": str(payload.get("issue_id") or ""),
                    "path": str(path.relative_to(project_root)),
                }
            )
            bucket["benchmark_refs"].append(str(path.relative_to(project_root)))
            bucket["recurrence_count"] += int(payload.get("count", 1) or 1)

    audits_root = project_root / ".beacon" / "state" / "qa-audits"
    if audits_root.exists():
        for path in sorted(audits_root.glob("*/*.json")):
            payload = _read_json(path)
            if not payload:
                continue
            label = str(payload.get("label") or "").strip()
            feature = str(payload.get("feature_slug") or "").strip()
            benchmark_ref = str(path.relative_to(project_root))
            if label == "false_pass":
                candidate = "Tighten QA confidence/replay/evidence policy for false-pass samples."
                bucket = _bucket("qa_policy", candidate)
            elif label == "false_block":
                candidate = "Reduce false-block rate by improving review thresholds and evidence sufficiency policy."
                bucket = _bucket("qa_policy", candidate)
            elif label in {"runner_gap", "flake"}:
                candidate = "Adjust QA evidence and flake-handling policy for unstable runner samples."
                bucket = _bucket("qa_policy", candidate)
            else:
                candidate = f"Review QA audit label handling for `{label}` samples."
                bucket = _bucket("qa_policy", candidate)
            bucket["sources"].append(
                {
                    "source_type": "qa_audit",
                    "label": label,
                    "feature": feature,
                    "path": benchmark_ref,
                }
            )
            bucket["benchmark_refs"].append(benchmark_ref)
            if feature:
                bucket["features"].add(feature)
            bucket["recurrence_count"] += 1
            bucket["verification_support"] += 1

    rows: list[dict[str, Any]] = []
    for bucket in buckets.values():
        bucket["benchmark_refs"] = sorted(set(_normalize_text_list(bucket["benchmark_refs"])))
        bucket["feature_count"] = len(bucket["features"])
        bucket["version_count"] = len(bucket["versions"])
        bucket["source_count"] = len(bucket["sources"])
        bucket["source_diversity"] = len(
            {
                str(source.get("source_type") or "")
                for source in bucket["sources"]
                if isinstance(source, dict)
            }
        )
        bucket["features"] = sorted(bucket["features"])
        bucket["versions"] = sorted(bucket["versions"])
        rows.append(bucket)
    return sorted(rows, key=lambda item: (item["category"], item["text"]))


def _score_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    text = str(candidate.get("text") or "").strip()
    source_count = int(candidate.get("source_count", 0) or 0)
    source_diversity = int(candidate.get("source_diversity", 0) or 0)
    recurrence = int(candidate.get("recurrence_count", 0) or 0)
    benchmark_refs = len(candidate.get("benchmark_refs", []))
    verification_support = int(candidate.get("verification_support", 0) or 0)
    artifact_pressure = int(candidate.get("artifact_pressure", 0) or 0)
    feature_count = int(candidate.get("feature_count", 0) or 0)

    evidence_strength = min(35, source_count * 12 + source_diversity * 8)
    recurrence_score = min(20, max(0, recurrence - 1) * 5 + max(0, feature_count - 1) * 5)
    benchmark_score = min(20, benchmark_refs * 4)
    verifiability = min(15, verification_support * 5)
    pressure_score = min(10, artifact_pressure * 2)
    total = evidence_strength + recurrence_score + benchmark_score + verifiability + pressure_score
    structural = any(
        token in text.lower()
        for token in (
            "require ",
            "must ",
            "rollback",
            "evidence",
            "artifact_updates",
            "api_changes",
            "db_changes",
            "verification",
            "closure",
        )
    )

    decision = "review"
    if total >= 75 or (source_count >= 2 and source_diversity >= 2):
        decision = "keep"
    elif total <= 35 and recurrence <= 1 and source_count <= 1:
        decision = "review" if structural else "discard"

    confidence = "medium"
    if total >= 85 or total <= 20:
        confidence = "high"
    elif 35 < total < 75:
        confidence = "medium"

    reason = (
        "high recurring support across real benchmark inputs"
        if decision == "keep"
        else "low-signal or one-off input does not justify baseline uplift"
        if decision == "discard"
        else "mixed evidence: keep visible but require human review"
    )

    return {
        **candidate,
        "scorecard": {
            "main_kpi": "false_complete_rate",
            "evidence_strength": evidence_strength,
            "recurrence_score": recurrence_score,
            "benchmark_score": benchmark_score,
            "verifiability": verifiability,
            "pressure_score": pressure_score,
            "total_score": total,
        },
        "decision": decision,
        "confidence": confidence,
        "reason": reason,
        "structural": structural,
    }


def refresh_keep_discard_engine(project_root: Path) -> dict[str, Any]:
    ensure_evo_skeleton(project_root)
    previous = _read_json(_evo_ledger_path(project_root))
    previous_rows = previous.get("decisions") if isinstance(previous.get("decisions"), list) else []
    previous_by_id = {
        str(item.get("candidate_id") or ""): item
        for item in previous_rows
        if isinstance(item, dict) and str(item.get("candidate_id") or "").strip()
    }

    candidates = [_score_candidate(item) for item in _build_learning_candidates(project_root)]
    counts = {
        "keep": len([item for item in candidates if item.get("decision") == "keep"]),
        "review": len([item for item in candidates if item.get("decision") == "review"]),
        "discard": len([item for item in candidates if item.get("decision") == "discard"]),
    }
    scorecard_payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "main_kpi": "false_complete_rate",
        "counts": counts,
        "candidates": candidates,
    }
    ledger_payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "decisions": [
            {
                "candidate_id": item.get("candidate_id"),
                "category": item.get("category"),
                "text": item.get("text"),
                "decision": item.get("decision"),
                "confidence": item.get("confidence"),
                "reason": item.get("reason"),
                "score": item.get("scorecard", {}).get("total_score"),
                "benchmark_refs": item.get("benchmark_refs", []),
            }
            for item in candidates
        ],
    }
    engine_payload = _read_json(_evo_decision_engine_path(project_root))
    engine_payload.update(
        {
            "schema_version": "1.0",
            "generated_at": now_iso(),
            "decision_summary": counts,
            "scorecard_path": str(_evo_scorecard_path(project_root).relative_to(project_root)),
            "ledger_path": str(_evo_ledger_path(project_root).relative_to(project_root)),
        }
    )
    write_json(_evo_scorecard_path(project_root), scorecard_payload)
    write_json(_evo_ledger_path(project_root), ledger_payload)
    write_json(_evo_decision_engine_path(project_root), engine_payload)

    for item in candidates:
        candidate_id = str(item.get("candidate_id") or "")
        previous_item = previous_by_id.get(candidate_id, {})
        if (
            str(previous_item.get("decision") or "") == str(item.get("decision") or "")
            and int(previous_item.get("score") or -1) == int(item.get("scorecard", {}).get("total_score") or -1)
        ):
            continue
        entry = {
            "ts": now_iso(),
            "source": "auto-keep-discard-engine",
            "entry_id": candidate_id,
            "recommendation": str(item.get("decision") or "review"),
            "rationale": str(item.get("reason") or ""),
            "refs": _normalize_text_list(item.get("benchmark_refs")),
            "score": int(item.get("scorecard", {}).get("total_score") or 0),
            "category": str(item.get("category") or ""),
        }
        _append_jsonl(_evo_ledger_log_path(project_root), entry)
        _append_jsonl(_keep_discard_log_path(project_root), entry)

    return {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "decision_engine": str(_evo_decision_engine_path(project_root).relative_to(project_root)),
        "scorecard": str(_evo_scorecard_path(project_root).relative_to(project_root)),
        "ledger": str(_evo_ledger_path(project_root).relative_to(project_root)),
        "counts": counts,
    }


def _high_risk_candidate(candidate: dict[str, Any]) -> bool:
    category = str(candidate.get("category") or "").strip()
    text = str(candidate.get("text") or "").strip().lower()
    if category == "debug_policy":
        return True
    return any(
        token in text
        for token in (
            "false_complete",
            "evidence",
            "rollback",
            "verify",
            "artifact_updates",
            "closure",
            "recovery",
        )
    )


def _candidate_priority(candidate: dict[str, Any]) -> tuple[int, int, int, str]:
    category = str(candidate.get("category") or "")
    category_rank = {
        "qa_policy": 0,
        "design_policy": 1,
        "contract_policy": 2,
        "debug_policy": 3,
        "rewrite_policy": 4,
        "benchmark_policy": 5,
    }.get(category, 9)
    risk_rank = 0 if _high_risk_candidate(candidate) else 1
    score = int(candidate.get("scorecard", {}).get("total_score", 0) or 0)
    return (risk_rank, category_rank, -score, str(candidate.get("candidate_id") or ""))


def _supporting_metrics(*, selected: list[dict[str, Any]], budget: dict[str, int]) -> dict[str, float]:
    if not selected:
        return {
            "false_complete_rate": 1.0,
            "false_block_rate": 1.0,
            "human_audit_agreement": 0.0,
            "confidence_calibration_error": 1.0,
            "evidence_coverage": 0.0,
            "recovery_success_rate": 0.0,
            "operator_load": 0.0,
            "cost_per_trial": 0.0,
        }
    risky = [item for item in selected if _high_risk_candidate(item)]
    unresolved = [
        item
        for item in risky
        if str(item.get("decision") or "").strip() == "discard"
    ]
    debug_cases = [item for item in selected if str(item.get("category") or "") == "debug_policy"]
    debug_good = [
        item
        for item in debug_cases
        if str(item.get("decision") or "").strip() in {"keep", "review"}
    ]
    evidence_refs = sorted(
        {
            ref
            for item in selected
            for ref in _normalize_text_list(item.get("benchmark_refs"))
        }
    )
    command_count = min(int(budget.get("max_command_count", 0) or 0), max(1, len(selected) + 2))
    qa_audit_refs = [ref for ref in evidence_refs if "/qa-audits/" in ref]
    false_block_samples = len([item for item in selected if str(item.get("category") or "") == "qa_policy"])
    calibration_candidates = len([item for item in selected if str(item.get("category") or "") == "qa_policy"])
    return {
        "false_complete_rate": round(len(unresolved) / float(len(risky) or 1), 4),
        "false_block_rate": round(false_block_samples / float(len(selected) or 1), 4),
        "human_audit_agreement": round(len(qa_audit_refs) / float(len(selected) or 1), 4),
        "confidence_calibration_error": round(1.0 / float(max(1, calibration_candidates + len(qa_audit_refs))), 4),
        "evidence_coverage": round(len(evidence_refs) / float(max(1, int(budget.get("max_evidence_budget", len(evidence_refs)) or 1))), 4),
        "recovery_success_rate": round(len(debug_good) / float(len(debug_cases) or 1), 4),
        "operator_load": round(len(selected) / float(max(1, int(budget.get("max_iterations", len(selected)) or 1))), 4),
        "cost_per_trial": round(command_count / float(len(selected) or 1), 4),
    }


def _main_score(metrics: dict[str, float]) -> float:
    return round((1.0 - float(metrics.get("false_complete_rate", 1.0) or 1.0)) * 100.0, 2)


def _overall_score(metrics: dict[str, float]) -> float:
    return round(
        _main_score(metrics) * 0.6
        + float(metrics.get("evidence_coverage", 0.0) or 0.0) * 100.0 * 0.2
        + float(metrics.get("recovery_success_rate", 0.0) or 0.0) * 100.0 * 0.1
        + (1.0 - min(1.0, float(metrics.get("operator_load", 1.0) or 1.0))) * 100.0 * 0.05
        + (1.0 / max(1.0, float(metrics.get("cost_per_trial", 1.0) or 1.0))) * 100.0 * 0.05,
        2,
    )


def _experiment_verdict(*, current_score: float, previous_score: float | None, metrics: dict[str, float]) -> str:
    current_false_complete = float(metrics.get("false_complete_rate", 1.0) or 1.0)
    if previous_score is None:
        if current_false_complete <= 0.2:
            return "keep"
        if current_false_complete >= 0.8:
            return "discard"
        return "review"
    if current_score - previous_score >= 5.0:
        return "keep"
    if current_score - previous_score <= -5.0:
        return "discard"
    return "review"


def _select_candidates_for_budget(candidates: list[dict[str, Any]], *, budget: dict[str, int]) -> tuple[list[dict[str, Any]], list[str], int]:
    max_iterations = max(1, int(budget.get("max_iterations", 3) or 3))
    max_command_count = max(1, int(budget.get("max_command_count", 12) or 12))
    max_evidence_budget = max(1, int(budget.get("max_evidence_budget", 20) or 20))
    ordered = sorted(candidates, key=_candidate_priority)
    selected: list[dict[str, Any]] = []
    refs: list[str] = []
    command_count = 0
    for candidate in ordered:
        next_command_count = command_count + 1
        candidate_refs = _normalize_text_list(candidate.get("benchmark_refs"))
        tentative_refs = list(dict.fromkeys([*refs, *candidate_refs]))
        if len(selected) >= max_iterations:
            break
        if next_command_count > max_command_count:
            break
        if len(tentative_refs) > max_evidence_budget:
            continue
        selected.append(candidate)
        refs = tentative_refs
        command_count = next_command_count
    return selected, refs[:max_evidence_budget], command_count


def run_evo_experiment(
    project_root: Path,
    *,
    version: str,
    experiment_label: str = "",
    budget_overrides: dict[str, int] | None = None,
) -> dict[str, Any]:
    ensure_evo_skeleton(project_root)
    refresh_learning_loop(project_root)
    engine = load_keep_discard_engine(project_root)
    decision_config = _read_json(_evo_decision_engine_path(project_root))
    default_budget = decision_config.get("budget_contract") if isinstance(decision_config.get("budget_contract"), dict) else {}
    budget = {
        "max_runtime_minutes": int(default_budget.get("max_runtime_minutes", 30) or 30),
        "max_iterations": int(default_budget.get("max_iterations", 3) or 3),
        "max_command_count": int(default_budget.get("max_command_count", 12) or 12),
        "max_evidence_budget": int(default_budget.get("max_evidence_budget", 20) or 20),
    }
    for key, value in (budget_overrides or {}).items():
        if key in budget and int(value or 0) > 0:
            budget[key] = int(value)

    scorecard = _read_json(_evo_scorecard_path(project_root))
    candidates = scorecard.get("candidates") if isinstance(scorecard.get("candidates"), list) else []
    selected, refs, command_count = _select_candidates_for_budget(
        [item for item in candidates if isinstance(item, dict)],
        budget=budget,
    )
    metrics = _supporting_metrics(selected=selected, budget=budget)
    main_score = _main_score(metrics)
    overall_score = _overall_score(metrics)
    previous = load_latest_evo_experiment(project_root)
    previous_main = float(previous.get("main_kpi_score")) if previous and previous.get("main_kpi_score") is not None else None
    previous_overall = float(previous.get("overall_score")) if previous and previous.get("overall_score") is not None else None
    verdict = _experiment_verdict(current_score=main_score, previous_score=previous_main, metrics=metrics)
    run_id = f"evo-{now_iso().replace(':', '').replace('-', '').replace('+00:00', 'Z')}"
    label = str(experiment_label or "Beacon v1.1.10 evo harness").strip()
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "label": label,
        "version": version,
        "generated_at": now_iso(),
        "budget_contract": budget,
        "main_kpi": "false_complete_rate",
        "main_kpi_score": main_score,
        "overall_score": overall_score,
        "score_delta": {
            "main_kpi_score": None if previous_main is None else round(main_score - previous_main, 2),
            "overall_score": None if previous_overall is None else round(overall_score - previous_overall, 2),
            "false_complete_rate": None
            if not previous
            else round(
                float(previous.get("metrics", {}).get("false_complete_rate", 1.0) or 1.0)
                - float(metrics.get("false_complete_rate", 1.0) or 1.0),
                4,
            ),
        },
        "metrics": metrics,
        "verdict": verdict,
        "selected_candidates": selected,
        "selected_benchmark_refs": refs,
        "command_count": command_count,
        "experiment_surface": {
            "subject_surface": decision_config.get("subject_surface", []),
            "program_surface": decision_config.get("program_surface", []),
        },
        "artifacts": {
            "decision_engine": str(_evo_decision_engine_path(project_root).relative_to(project_root)),
            "scorecard": str(_evo_scorecard_path(project_root).relative_to(project_root)),
            "ledger": str(_evo_ledger_path(project_root).relative_to(project_root)),
        },
    }
    experiments_root = _evo_experiments_root(project_root)
    experiments_root.mkdir(parents=True, exist_ok=True)
    experiment_path = experiments_root / f"{run_id}.json"
    write_json(experiment_path, payload)
    write_json(_evo_latest_experiment_path(project_root), payload)
    _append_jsonl(
        _evo_ledger_log_path(project_root),
        {
            "ts": now_iso(),
            "source": "evo-experiment-runner",
            "entry_id": run_id,
            "recommendation": verdict,
            "rationale": f"main_kpi_score={main_score}; delta={payload['score_delta']['main_kpi_score']}",
            "refs": refs,
        },
    )
    write_evo_contract_docs(project_root, version=version)
    return {**payload, "path": str(experiment_path.relative_to(project_root))}


def refresh_execution_baseline(project_root: Path) -> dict[str, Any]:
    ensure_evo_skeleton(project_root)
    decisions = _read_json(_evo_scorecard_path(project_root))
    rows = decisions.get("candidates") if isinstance(decisions.get("candidates"), list) else []
    selected = [
        item
        for item in rows
        if isinstance(item, dict) and str(item.get("decision") or "") in {"keep", "review"}
    ]
    recommendations = [
        f"[{item.get('decision')}/{item.get('scorecard', {}).get('total_score', 0)}] {item.get('text')}"
        for item in sorted(
            selected,
            key=lambda item: (
                {"keep": 0, "review": 1}.get(str(item.get("decision") or ""), 9),
                -int(item.get("scorecard", {}).get("total_score", 0) or 0),
                str(item.get("text") or ""),
            ),
        )
    ]
    payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "recommendations": recommendations,
        "decision_summary": decisions.get("counts", {}),
        "source_scorecard": str(_evo_scorecard_path(project_root).relative_to(project_root)),
    }
    write_json(execution_baseline_path(project_root), payload)
    return payload


def write_evo_contract_docs(project_root: Path, *, version: str) -> dict[str, str]:
    ensure_evo_skeleton(project_root)
    resolved_version = str(version or "").strip()
    execution_root = project_root / "docs" / "beacon" / resolved_version / "execution"
    execution_root.mkdir(parents=True, exist_ok=True)
    decision_engine = _read_json(_evo_decision_engine_path(project_root))
    scorecard = _read_json(_evo_scorecard_path(project_root))
    latest_experiment = load_latest_evo_experiment(project_root)
    decision_summary = scorecard.get("counts", {}) if isinstance(scorecard.get("counts"), dict) else {}
    budget = decision_engine.get("budget_contract", {}) if isinstance(decision_engine.get("budget_contract"), dict) else {}
    subject_surface = [f"- `{item}`" for item in _normalize_text_list(decision_engine.get("subject_surface"))] or ["- none"]
    program_surface = [f"- `{item}`" for item in _normalize_text_list(decision_engine.get("program_surface"))] or ["- none"]

    harness_path = execution_root / "evo-harness-contract.md"
    scorecard_path = execution_root / "evo-scorecard-contract.md"

    harness_text = "\n".join(
        [
            f"# Evo Harness Contract ({resolved_version})",
            "",
            "## Goal",
            "",
            "- Run fixed-budget, real-input experiments over Beacon learning-plane candidates.",
            "- Keep the editable surface small and auditable.",
            "- Produce explicit keep/review/discard decisions instead of open-ended drift.",
            "",
            "## Budget Contract",
            "",
            f"- max_runtime_minutes: `{budget.get('max_runtime_minutes', 30)}`",
            f"- max_iterations: `{budget.get('max_iterations', 3)}`",
            f"- max_command_count: `{budget.get('max_command_count', 12)}`",
            f"- max_evidence_budget: `{budget.get('max_evidence_budget', 20)}`",
            "",
            "## Subject Surface",
            *subject_surface,
            "",
            "## Program Surface",
            *program_surface,
            "",
            "## Real Benchmark Inputs",
            f"- benchmark_corpus: `{_benchmark_corpus_path(project_root).relative_to(project_root)}`",
            f"- scorecard: `{_evo_scorecard_path(project_root).relative_to(project_root)}`",
            f"- ledger: `{_evo_ledger_path(project_root).relative_to(project_root)}`",
            "",
            "## Latest Experiment",
            f"- run_id: `{latest_experiment.get('run_id', '-')}`",
            f"- label: `{latest_experiment.get('label', '-')}`",
            f"- selected_candidates: `{len(latest_experiment.get('selected_candidates', [])) if isinstance(latest_experiment, dict) else 0}`",
            f"- verdict: `{latest_experiment.get('verdict', '-')}`",
            "",
        ]
    ) + "\n"

    scorecard_text = "\n".join(
        [
            f"# Evo Scorecard Contract ({resolved_version})",
            "",
            "## Single Main KPI",
            "",
            "- `false_complete_rate`",
            "- Definition: high-risk benchmark cases that still resolve to `discard`, divided by total high-risk benchmark cases in the selected experiment set.",
            "- Lower is better.",
            "",
            "## Supporting Metrics",
            "",
            "- `evidence_coverage`",
            "- `recovery_success_rate`",
            "- `operator_load`",
            "- `cost_per_trial`",
            "",
            "## Decision Thresholds",
            "",
            f"- keep threshold: `{decision_engine.get('decision_thresholds', {}).get('keep', 75)}`",
            f"- discard threshold: `{decision_engine.get('decision_thresholds', {}).get('discard', 35)}`",
            "- review: any score between discard and keep, or mixed evidence cases.",
            "",
            "## Current Decision Summary",
            "",
            f"- keep: `{decision_summary.get('keep', 0)}`",
            f"- review: `{decision_summary.get('review', 0)}`",
            f"- discard: `{decision_summary.get('discard', 0)}`",
            "",
            "## Latest Score Delta",
            "",
            f"- main_kpi_score: `{latest_experiment.get('main_kpi_score', '-')}`",
            f"- score_delta.main_kpi_score: `{(latest_experiment.get('score_delta') or {}).get('main_kpi_score', '-') if isinstance(latest_experiment, dict) else '-'}`",
            f"- score_delta.false_complete_rate: `{(latest_experiment.get('score_delta') or {}).get('false_complete_rate', '-') if isinstance(latest_experiment, dict) else '-'}`",
            "",
            "## Artifacts",
            "",
            f"- decision_engine: `{_evo_decision_engine_path(project_root).relative_to(project_root)}`",
            f"- scorecard: `{_evo_scorecard_path(project_root).relative_to(project_root)}`",
            f"- latest_experiment: `{_evo_latest_experiment_path(project_root).relative_to(project_root)}`",
            "",
        ]
    ) + "\n"

    harness_path.write_text(harness_text, encoding="utf-8")
    scorecard_path.write_text(scorecard_text, encoding="utf-8")

    index_path = execution_root / "index.md"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
    else:
        text = f"# Execution Index ({resolved_version})\n\n## Human Primary Surface\n"
    additions = []
    for rel in ("./evo-harness-contract.md", "./evo-scorecard-contract.md"):
        if rel not in text:
            additions.append(f"- `{rel}`")
    if additions:
        text = text.rstrip() + "\n" + "\n".join(additions) + "\n"
    index_path.write_text(text, encoding="utf-8")

    return {
        "evo_harness_contract": str(harness_path.relative_to(project_root)),
        "evo_scorecard_contract": str(scorecard_path.relative_to(project_root)),
    }


def refresh_learning_loop(project_root: Path) -> dict[str, Any]:
    corpus = refresh_benchmark_corpus(project_root)
    calibration = refresh_qa_calibration_model(project_root)
    decision_engine = refresh_keep_discard_engine(project_root)
    baseline = refresh_execution_baseline(project_root)
    docs = {}
    versions = sorted({str(item.get("version") or "").strip() for item in _collect_requirement_rewrite_inputs(project_root) if str(item.get("version") or "").strip()})
    if not versions and (project_root / "docs" / "beacon" / "v1.1.9").exists():
        versions = ["v1.1.9"]
    for version in versions:
        docs = write_evo_contract_docs(project_root, version=version)
    return {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "benchmark_corpus": str(_benchmark_corpus_path(project_root).relative_to(project_root)),
        "execution_baseline": str(execution_baseline_path(project_root).relative_to(project_root)),
        "decision_engine": decision_engine.get("decision_engine"),
        "decision_scorecard": decision_engine.get("scorecard"),
        "decision_ledger": decision_engine.get("ledger"),
        "docs": docs,
        "counts": {
            "technical_archive_inputs": corpus.get("counts", {}).get("technical_archive_inputs", 0),
            "debug_issue_inputs": corpus.get("counts", {}).get("debug_issue_inputs", 0),
            "qa_audit_inputs": corpus.get("counts", {}).get("qa_audit_inputs", 0),
            "baseline_recommendations": len(baseline.get("recommendations", [])),
            "keep_decisions": decision_engine.get("counts", {}).get("keep", 0),
            "review_decisions": decision_engine.get("counts", {}).get("review", 0),
            "discard_decisions": decision_engine.get("counts", {}).get("discard", 0),
        },
        "qa_calibration_model": calibration,
    }
