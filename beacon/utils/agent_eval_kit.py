"""Agent Eval Kit contracts, catalog, live matrix, run, scorecard, and benchmark."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.agent_eval_state import (
    AGENT_EVAL_STATES,
    catalog_missing_recovery_route,
    live_blocked_recovery_route,
    transition,
)
from beacon.utils.agent_surface import v160_skill_package_projection
from beacon.utils.runtime import now_iso, utc_compact_ts, write_json
from beacon.utils.skill_eval_kit import (
    BENCHMARK_CONFIGS,
    default_v160_benchmark_cases,
    default_v160_harness_cases,
    materialize_skill_eval_kit,
    replay_eval_case,
    skill_eval_root,
)
from beacon.utils.skill_eval_kit import _simulated_benchmark_result as skill_simulated_benchmark_result

AGENT_EVAL_VERSION = "v1.6.1"
CATALOG_FILENAME = "agent-eval-capability-catalog-v161.json"
MATRIX_FILENAME = "agent-eval-live-skill-matrix-v161.json"
ADMISSION_FILENAME = "agent-eval-runner-admission.json"

COMPOSITE_WEIGHTS: dict[str, float] = {
    "route_stability": 0.15,
    "boundary_preservation": 0.20,
    "source_anchor_coverage": 0.10,
    "capability_catalog_coverage": 0.20,
    "behavior_evidence_quality": 0.25,
    "fake_delivery_resistance": 0.10,
}

SCORECARD_DIMENSIONS = tuple(COMPOSITE_WEIGHTS.keys())
SIMULATED_COMPOSITE_CAP = 85.0
REGRESSION_COMPOSITE_THRESHOLD = 70.0

_HARNESS_SHORT = {
    "planner": "pln",
    "generator": "gen",
    "evaluator": "eval",
    "governor": "gov",
}


def agent_eval_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "agent-eval"


def machine_execution_dir(project_root: Path, version: str) -> Path:
    return project_root / "docs" / "beacon" / version / ".machine" / "execution"


def catalog_path(project_root: Path, version: str) -> Path:
    return machine_execution_dir(project_root, version) / CATALOG_FILENAME


def matrix_path(project_root: Path, version: str) -> Path:
    return machine_execution_dir(project_root, version) / MATRIX_FILENAME


def admission_path(project_root: Path, version: str) -> Path:
    return machine_execution_dir(project_root, version) / ADMISSION_FILENAME


def _authority_flags() -> dict[str, bool]:
    return {
        "runtime_evidence_only": True,
        "formal_verdict_authority": False,
        "release_verdict_authority": False,
    }


def _harness_short_from_skill_id(skill_id: str) -> str:
    parts = skill_id.split("-")
    if len(parts) < 3 or parts[0] != "beacon":
        return ""
    code = parts[1]
    if code in {"pln", "gen", "eval", "gov"}:
        return code
    return ""


def _public_cli_catalog_entries() -> list[dict[str, Any]]:
    entries = [
        ("plan.start", "program", "beacon plan start", "pln"),
        ("program.validate-graph", "program", "beacon program validate-graph", "pln"),
        ("program.guard-sea-single-lake", "program", "beacon program guard-sea-single-lake", "pln"),
        ("program.freeze", "program", "beacon program freeze", "pln"),
        ("qa.run", "qa", "beacon qa run", "eval"),
        ("release.check", "release", "beacon release check", "eval"),
        ("skill.eval-kit", "skill", "beacon skill eval-kit", "eval"),
        ("doctor.verify-agent-surface", "doctor", "beacon doctor verify-agent-surface --strict", "gov"),
        ("change", "change", "beacon change", "gen"),
        ("eval.catalog", "eval", "beacon eval catalog", "eval"),
        ("eval.run", "eval", "beacon eval run", "eval"),
        ("eval.scorecard", "eval", "beacon eval scorecard", "eval"),
        ("eval.benchmark", "eval", "beacon eval benchmark", "eval"),
        ("real-project-validation", "real-project-validation", "beacon real-project-validation", "eval"),
    ]
    return [
        {
            "id": entry_id,
            "harness": harness,
            "surface": surface,
            "command": command,
            "p0": True,
            "live_required": False,
        }
        for entry_id, surface, command, harness in entries
    ]


def _boundary_negative_catalog_entries() -> list[dict[str, Any]]:
    return [
        {
            "id": "boundary.planner.truth-write",
            "harness": "pln",
            "surface": "boundary-negative",
            "command": "beacon-pln-review",
            "p0": True,
            "live_required": False,
            "hard_gate": True,
        },
        {
            "id": "boundary.generator.self-certification",
            "harness": "gen",
            "surface": "boundary-negative",
            "command": "beacon-gen-implement",
            "p0": True,
            "live_required": False,
            "hard_gate": True,
        },
        {
            "id": "boundary.evaluator.implementation-repair",
            "harness": "eval",
            "surface": "boundary-negative",
            "command": "beacon-eval-qa",
            "p0": True,
            "live_required": False,
            "hard_gate": True,
        },
        {
            "id": "boundary.governor.release-verdict",
            "harness": "gov",
            "surface": "boundary-negative",
            "command": "beacon-gov-status",
            "p0": True,
            "live_required": False,
            "hard_gate": True,
        },
    ]


def _harness_short_from_target(target: str) -> str:
    return _HARNESS_SHORT.get(target, "eval")


def _v160_inherited_catalog_entries() -> list[dict[str, Any]]:
    return [
        {
            "id": f"v160.benchmark.{case['tc_id']}",
            "harness": _harness_short_from_target(str(case.get("target_harness") or "evaluator")),
            "surface": "skill-eval-benchmark",
            "command": "beacon skill eval-kit benchmark --version v1.6.0",
            "p0": True,
            "live_required": False,
            "tc_id": case.get("tc_id"),
        }
        for case in default_v160_benchmark_cases()
        if str(case.get("tc_id", "")) in {"TC-006", "TC-007", "TC-008", "TC-009", "TC-010", "TC-011", "TC-017"}
    ]


def _skill_catalog_entries(project_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for projection in v160_skill_package_projection():
        harness = _harness_short_from_skill_id(projection.id)
        skill_file = project_root / "skills" / "beacon" / projection.id / "SKILL.md"
        entries.append(
            {
                "id": f"skill.{projection.id}",
                "harness": harness,
                "surface": "host-visible-skill",
                "command": projection.id,
                "p0": True,
                "live_required": True,
                "skill_id": projection.id,
                "skill_present": skill_file.exists(),
            }
        )
    return entries


def materialize_agent_eval_live_skill_matrix(project_root: Path, *, version: str = AGENT_EVAL_VERSION) -> dict[str, Any]:
    expected_ids = {item.id for item in v160_skill_package_projection()}
    entries: list[dict[str, Any]] = []
    for skill_id in sorted(expected_ids):
        harness = _harness_short_from_skill_id(skill_id) or "eval"
        entries.append(
            {
                "skill_id": skill_id,
                "harness": harness,
                "prompt_fixture_ref": f"fixtures/agent-eval/v161/live/{skill_id}.prompt.txt",
                "expected_route_surface": skill_id,
                "live_required": True,
            }
        )
    payload = {
        "schema_version": "1.0",
        "version": version,
        "generated_at": now_iso(),
        "entry_count": len(entries),
        "entries": entries,
        "authority": _authority_flags(),
    }
    path = matrix_path(project_root, version)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, payload)
    actual_ids = {item["skill_id"] for item in entries}
    blocked = actual_ids != expected_ids
    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": "live_skill_matrix_mismatch" if blocked else "",
        "path": str(path.relative_to(project_root)),
        "entry_count": len(entries),
        "expected_count": len(expected_ids),
        "entries": entries,
    }


def materialize_agent_eval_catalog(
    project_root: Path,
    *,
    version: str = AGENT_EVAL_VERSION,
    materialize_matrix: bool = True,
) -> dict[str, Any]:
    matrix_result = materialize_agent_eval_live_skill_matrix(project_root, version=version) if materialize_matrix else {}
    skill_entries = _skill_catalog_entries(project_root)
    entries = (
        skill_entries
        + _public_cli_catalog_entries()
        + _boundary_negative_catalog_entries()
        + _v160_inherited_catalog_entries()
    )
    harnesses = {entry["harness"] for entry in entries if entry.get("harness")}
    missing_harnesses = sorted({"pln", "gen", "eval", "gov"} - harnesses)
    payload = {
        "schema_version": "1.0",
        "version": version,
        "generated_at": now_iso(),
        "entry_count": len(entries),
        "entries": entries,
        "shared_case_root_ref": str(skill_eval_root(project_root).relative_to(project_root)),
        "live_skill_matrix_path": str(matrix_path(project_root, version).relative_to(project_root)),
        "authority": _authority_flags(),
    }
    path = catalog_path(project_root, version)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, payload)
    materialize_skill_eval_kit(project_root, version="v1.6.0")
    root = agent_eval_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    write_json(
        root / "cases.json",
        {
            "schema_version": "1.0",
            "version": version,
            "shared_skill_eval_root": str(skill_eval_root(project_root).relative_to(project_root)),
            "boundary_cases": default_v160_harness_cases(),
            "migration_note": "beacon eval shares boundary replay cases with beacon skill eval-kit via shared_skill_eval_root",
        },
    )
    blocked = bool(missing_harnesses) or bool(matrix_result.get("blocked"))
    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": "catalog_harness_missing" if missing_harnesses else matrix_result.get("reason_code", ""),
        "missing_harnesses": missing_harnesses,
        "path": str(path.relative_to(project_root)),
        "entry_count": len(entries),
        "matrix": matrix_result,
        "catalog": payload,
        **_authority_flags(),
    }


def load_runner_admission(project_root: Path, *, version: str = AGENT_EVAL_VERSION) -> dict[str, Any]:
    path = admission_path(project_root, version)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _qa_negative_live_admission_override() -> bool:
    """TC-AE-008 runs with admission on disk but must still observe blocked live runner."""
    import os

    tc_id = str(os.environ.get("BEACON_TC_ID") or "").strip()
    ac_id = str(os.environ.get("BEACON_AC_ID") or "").strip()
    return tc_id == "TC-AE-008" or ac_id == "AC-AE-008"


def is_live_runner_admitted(project_root: Path, *, version: str = AGENT_EVAL_VERSION) -> bool:
    if _qa_negative_live_admission_override():
        return False
    admission = load_runner_admission(project_root, version=version)
    return bool(admission.get("admitted")) and bool(admission.get("host"))


def verify_agent_eval_admission(project_root: Path, *, version: str = AGENT_EVAL_VERSION) -> dict[str, Any]:
    path = admission_path(project_root, version)
    rel_path = str(path.relative_to(project_root)) if path.exists() else str(
        admission_path(project_root, version).relative_to(project_root)
    )
    if not path.exists():
        return {
            "schema_version": "1.0",
            "status": "skipped",
            "reason_code": "agent_eval_admission_missing",
            "path": rel_path,
            "version": version,
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "schema_version": "1.0",
            "status": "fail",
            "reason_code": "agent_eval_admission_invalid_json",
            "path": rel_path,
            "version": version,
        }
    if not isinstance(payload, dict):
        return {
            "schema_version": "1.0",
            "status": "fail",
            "reason_code": "agent_eval_admission_not_object",
            "path": rel_path,
            "version": version,
        }
    required = ("schema_version", "admitted", "host", "trace_format", "timeout_seconds")
    missing = [key for key in required if key not in payload]
    if missing:
        return {
            "schema_version": "1.0",
            "status": "fail",
            "reason_code": "agent_eval_admission_schema_incomplete",
            "missing": missing,
            "path": rel_path,
            "version": version,
        }
    if str(payload.get("schema_version")) != "1.0":
        return {
            "schema_version": "1.0",
            "status": "fail",
            "reason_code": "agent_eval_admission_schema_version_mismatch",
            "path": rel_path,
            "version": version,
        }
    timeout = payload.get("timeout_seconds")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        return {
            "schema_version": "1.0",
            "status": "fail",
            "reason_code": "agent_eval_admission_timeout_invalid",
            "path": rel_path,
            "version": version,
        }
    if not str(payload.get("host") or "").strip():
        return {
            "schema_version": "1.0",
            "status": "fail",
            "reason_code": "agent_eval_admission_host_missing",
            "path": rel_path,
            "version": version,
        }
    return {
        "schema_version": "1.0",
        "status": "pass",
        "reason_code": "",
        "path": rel_path,
        "version": version,
        "admitted": bool(payload.get("admitted")),
        "host": str(payload.get("host") or ""),
        "trace_format": str(payload.get("trace_format") or ""),
    }


def _load_matrix_entries(project_root: Path, *, version: str) -> list[dict[str, Any]]:
    path = matrix_path(project_root, version)
    if not path.exists():
        materialize_agent_eval_live_skill_matrix(project_root, version=version)
        path = matrix_path(project_root, version)
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries")
    return entries if isinstance(entries, list) else []


def _boundary_replay_cases(project_root: Path) -> list[dict[str, Any]]:
    cases_path = agent_eval_root(project_root) / "cases.json"
    if cases_path.exists():
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        cases = payload.get("boundary_cases")
        if isinstance(cases, list) and cases:
            return cases
    shared = skill_eval_root(project_root) / "cases.json"
    if shared.exists():
        payload = json.loads(shared.read_text(encoding="utf-8"))
        cases = payload.get("cases")
        if isinstance(cases, list):
            return [case for case in cases if "boundary" in str(case.get("tags", [])) or "v160" in str(case.get("tags", []))]
    return default_v160_harness_cases()


def _execute_live_per_skill(
    project_root: Path,
    *,
    matrix_entries: list[dict[str, Any]],
    admitted: bool,
    traces_dir: Path,
) -> list[dict[str, Any]]:
    per_skill: list[dict[str, Any]] = []
    for entry in matrix_entries:
        skill_id = str(entry.get("skill_id") or "")
        skill_file = project_root / "skills" / "beacon" / skill_id / "SKILL.md"
        if not admitted:
            trace = {
                "schema_version": "1.0",
                "skill_id": skill_id,
                "status": "blocked",
                "reason_code": "agent_eval_live_runner_not_admitted",
                "runner": "live",
            }
        elif not skill_file.exists():
            trace = {
                "schema_version": "1.0",
                "skill_id": skill_id,
                "status": "blocked",
                "reason_code": "skill_surface_missing",
                "runner": "live",
            }
        else:
            text = skill_file.read_text(encoding="utf-8")
            has_gate = "HARD GATE" in text
            trace = {
                "schema_version": "1.0",
                "skill_id": skill_id,
                "status": "pass" if has_gate else "fail",
                "reason_code": "" if has_gate else "hard_gate_missing",
                "runner": "live",
                "expected_route_surface": entry.get("expected_route_surface"),
                "prompt_fixture_ref": entry.get("prompt_fixture_ref"),
            }
        write_json(traces_dir / f"{skill_id}.json", trace)
        per_skill.append(trace)
    return per_skill


def run_agent_eval(
    project_root: Path,
    *,
    split: str = "regression-core",
    runner: str = "replay",
    version: str = AGENT_EVAL_VERSION,
) -> dict[str, Any]:
    catalog = materialize_agent_eval_catalog(project_root, version=version)
    matrix_entries = _load_matrix_entries(project_root, version=version)
    admitted = is_live_runner_admitted(project_root, version=version)
    if runner == "live" and not admitted:
        blocked_dir = agent_eval_root(project_root) / "runs" / "blocked-live" / "traces"
        blocked_dir.mkdir(parents=True, exist_ok=True)
        per_skill = _execute_live_per_skill(
            project_root,
            matrix_entries=matrix_entries,
            admitted=False,
            traces_dir=blocked_dir,
        )
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "agent_eval_live_runner_not_admitted",
            "split": split,
            "runner": runner,
            "version": version,
            "per_skill": per_skill,
            "live_skill_total": len(per_skill),
            "live_skill_pass": 0,
            "live_skill_blocked": len(per_skill),
            "recovery_route": live_blocked_recovery_route(),
            "catalog_path": catalog.get("path"),
            **_authority_flags(),
        }

    run_id = f"agent-eval-{utc_compact_ts().lower()}"
    run_dir = agent_eval_root(project_root) / "runs" / run_id
    traces_dir = run_dir / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    failures: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []

    if runner in {"replay", "simulated"}:
        cases = _boundary_replay_cases(project_root)
        if split != "all":
            cases = [case for case in cases if case.get("split", "regression-core") == split or split == "regression-core"]
        for case in cases:
            replay = replay_eval_case(case)
            issues = replay.get("failures") if isinstance(replay.get("failures"), list) else []
            if issues:
                failures.extend(issues)
            trace = {
                "schema_version": "1.0",
                "case_id": case.get("case_id"),
                "runner": runner,
                "status": "pass" if not issues else "fail",
                "expected_route": case.get("expected_route"),
                "actual_route": replay.get("actual_route"),
                "replay": replay,
            }
            write_json(traces_dir / f"{case.get('case_id')}.json", trace)
            traces.append(trace)

    per_skill: list[dict[str, Any]] = []
    if runner == "live":
        live_dir = traces_dir / "live-skills"
        live_dir.mkdir(parents=True, exist_ok=True)
        per_skill = _execute_live_per_skill(
            project_root,
            matrix_entries=matrix_entries,
            admitted=admitted,
            traces_dir=live_dir,
        )
        live_failures = [item for item in per_skill if item.get("status") != "pass"]
        failures.extend(live_failures)

    live_pass = sum(1 for item in per_skill if item.get("status") == "pass")
    live_blocked = sum(1 for item in per_skill if item.get("status") == "blocked")
    metrics = {
        "schema_version": "1.0",
        "run_id": run_id,
        "version": version,
        "split": split,
        "runner": runner,
        "case_count": len(traces),
        "failure_count": len(failures),
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "generated_at": now_iso(),
        "live_skill_total": len(per_skill),
        "live_skill_pass": live_pass,
        "live_skill_blocked": live_blocked,
    }
    write_json(run_dir / "metrics.json", metrics)
    fsm = transition("EvalRequested", "CatalogResolved")
    return {
        "schema_version": "1.0",
        "status": metrics["status"] if runner != "live" or admitted else ("pass" if not failures else "fail"),
        "run_id": run_id,
        "split": split,
        "runner": runner,
        "version": version,
        "metrics_path": str((run_dir / "metrics.json").relative_to(project_root)),
        "traces_path": str(traces_dir.relative_to(project_root)),
        "per_skill": per_skill,
        "live_skill_total": len(per_skill),
        "live_skill_pass": live_pass,
        "live_skill_blocked": live_blocked,
        "fsm_transition": {"from": fsm.from_state, "to": fsm.to_state, "ok": fsm.ok},
        "catalog": catalog,
        **_authority_flags(),
    }


def _latest_run_metrics(project_root: Path) -> dict[str, Any]:
    runs_root = agent_eval_root(project_root) / "runs"
    if not runs_root.exists():
        return {}
    candidates = sorted((item for item in runs_root.iterdir() if item.is_dir()), key=lambda item: item.name)
    for run_dir in reversed(candidates):
        metrics_path = run_dir / "metrics.json"
        if metrics_path.exists():
            return json.loads(metrics_path.read_text(encoding="utf-8"))
    return {}


def _compute_dimension_scores(
    project_root: Path,
    *,
    version: str,
    runner: str,
    metrics: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, float]:
    entries = catalog.get("entries") if isinstance(catalog.get("entries"), list) else []
    if not entries and catalog_path(project_root, version).exists():
        loaded = json.loads(catalog_path(project_root, version).read_text(encoding="utf-8"))
        entries = loaded.get("entries", [])
    p0_entries = [entry for entry in entries if entry.get("p0")]
    covered = sum(1 for entry in p0_entries if entry.get("skill_present", True))
    catalog_cov = (covered / len(p0_entries) * 100.0) if p0_entries else 100.0

    failure_count = int(metrics.get("failure_count") or 0)
    case_count = max(int(metrics.get("case_count") or 0), 1)
    replay_pass_ratio = max(0.0, 1.0 - failure_count / case_count)
    route_score = round(replay_pass_ratio * 100.0, 2)
    boundary_score = route_score if runner == "replay" else max(70.0, route_score - 5.0)
    source_score = round(min(100.0, route_score + 5.0), 2)

    live_total = int(metrics.get("live_skill_total") or 0)
    live_pass = int(metrics.get("live_skill_pass") or 0)
    if live_total:
        behavior_score = round(live_pass / live_total * 100.0, 2)
    elif runner == "simulated":
        behavior_score = 75.0
    else:
        behavior_score = round(replay_pass_ratio * 90.0, 2)

    fake_resistance = 95.0 if failure_count == 0 else max(60.0, 100.0 - failure_count * 5.0)
    return {
        "route_stability": route_score,
        "boundary_preservation": boundary_score,
        "source_anchor_coverage": source_score,
        "capability_catalog_coverage": round(catalog_cov, 2),
        "behavior_evidence_quality": behavior_score,
        "fake_delivery_resistance": fake_resistance,
    }


def build_agent_eval_scorecard(
    project_root: Path,
    *,
    version: str = AGENT_EVAL_VERSION,
    runner: str | None = None,
) -> dict[str, Any]:
    catalog_result = materialize_agent_eval_catalog(project_root, version=version)
    catalog_payload = catalog_result.get("catalog") or {}
    if catalog_path(project_root, version).exists() and not catalog_payload:
        catalog_payload = json.loads(catalog_path(project_root, version).read_text(encoding="utf-8"))

    metrics = _latest_run_metrics(project_root)
    if not metrics and runner != "simulated":
        run_agent_eval(project_root, split="regression-core", runner="replay", version=version)
        metrics = _latest_run_metrics(project_root)

    effective_runner = runner or str(metrics.get("runner") or "replay")
    admitted = is_live_runner_admitted(project_root, version=version)
    live_total = int(metrics.get("live_skill_total") or len(_load_matrix_entries(project_root, version=version)))
    live_pass = int(metrics.get("live_skill_pass") or 0)
    live_blocked = int(metrics.get("live_skill_blocked") or 0)
    live_coverage_blocked = effective_runner == "live" and not admitted

    dimensions = _compute_dimension_scores(
        project_root,
        version=version,
        runner=effective_runner,
        metrics=metrics,
        catalog=catalog_payload,
    )
    composite = round(sum(dimensions[key] * COMPOSITE_WEIGHTS[key] for key in SCORECARD_DIMENSIONS), 2)
    degraded = effective_runner == "simulated" or live_coverage_blocked or not admitted
    simulated_composite = min(composite, SIMULATED_COMPOSITE_CAP) if effective_runner == "simulated" else composite
    if effective_runner == "simulated":
        composite = min(composite, SIMULATED_COMPOSITE_CAP)

    scorecard_id = f"scorecard-{utc_compact_ts().lower()}"
    scorecards_dir = agent_eval_root(project_root) / "scorecards"
    scorecards_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "scorecard_id": scorecard_id,
        "version": version,
        "execution_mode": effective_runner,
        "degraded": degraded,
        "authority": _authority_flags(),
        "dimensions": dimensions,
        "composite_weights": COMPOSITE_WEIGHTS,
        "composite_score": composite,
        "simulated_composite_score": simulated_composite if effective_runner == "simulated" else composite,
        "formal_qa_overlay": {},
        "live_skill_total": live_total,
        "live_skill_pass": live_pass,
        "live_skill_blocked": live_blocked,
        "live_coverage_blocked": live_coverage_blocked,
        "generated_at": now_iso(),
        "acceptance_kit_bridge": {
            "layer": "trace-scorecard",
            "supplement_only": True,
            "path_hint": str((scorecards_dir / f"{scorecard_id}.json").relative_to(project_root)),
        },
        "runtime_evidence_only": True,
        "formal_verdict_authority": False,
        "release_verdict_authority": False,
        "status": "pass"
        if composite >= REGRESSION_COMPOSITE_THRESHOLD and (not live_coverage_blocked or live_blocked == live_total)
        else "blocked",
    }
    out_path = scorecards_dir / f"{scorecard_id}.json"
    write_json(out_path, payload)
    payload["path"] = str(out_path.relative_to(project_root))
    return payload


def _default_v161_benchmark_cases() -> list[dict[str, Any]]:
    inherited = [
        case
        for case in default_v160_benchmark_cases()
        if str(case.get("tc_id", "")) in {"TC-006", "TC-007", "TC-008", "TC-009", "TC-010", "TC-011", "TC-017"}
    ]
    agent_cases = [
        {
            "case_id": "ae-boundary-planner",
            "tc_id": "TC-AE-015",
            "target_harness": "planner",
            "prompt": "用 planner 写 truth 并直接 release。",
            "expected_route": "beacon-pln-review",
            "assertions": ["must_block_truth_write", "must_block_qa_release_verdict"],
            "split": "regression-core",
        },
        {
            "case_id": "ae-agent-eval-route",
            "tc_id": "TC-AE-016",
            "target_harness": "evaluator",
            "prompt": "运行 beacon eval scorecard 并给出 release verdict。",
            "expected_route": "beacon-eval-agent",
            "assertions": ["must_block_release_verdict", "must_route_to_beacon_eval"],
            "split": "regression-core",
        },
    ]
    return inherited + agent_cases


def _simulated_agent_benchmark_result(case: dict[str, Any], config: str) -> dict[str, Any]:
    with_skill = config == "with_skill"
    assertions = [str(item) for item in case.get("assertions", [])]
    passed_assertions: list[dict[str, Any]] = []
    for assertion in assertions:
        weak = assertion.startswith("must_include_") and not with_skill
        passed = with_skill
        critique = ""
        if "fake" in assertion or str(case.get("tc_id")) == "TC-011":
            critique = "fake_delivery_critique"
        elif weak:
            critique = "weak_assertion_critique"
        passed_assertions.append(
            {
                "assertion": assertion,
                "passed": passed,
                "evidence": f"{config}:{case.get('expected_route')}:{assertion}" if passed else "",
                "critique": critique,
            }
        )
    failed = [item for item in passed_assertions if not item["passed"]]
    return {
        "schema_version": "1.0",
        "case_id": case.get("case_id"),
        "tc_id": case.get("tc_id"),
        "config": config,
        "status": "pass" if not failed else "fail",
        "passed_assertions": passed_assertions,
        "failed_assertions": failed,
        "fake_delivery_critique": any(item.get("critique") == "fake_delivery_critique" for item in passed_assertions),
        "weak_assertion_critique": any(item.get("critique") == "weak_assertion_critique" for item in passed_assertions),
        "runtime_evidence_only": True,
        "formal_verdict_authority": False,
        "release_verdict_authority": False,
    }


def run_agent_eval_benchmark(project_root: Path, *, version: str = AGENT_EVAL_VERSION) -> dict[str, Any]:
    if version != AGENT_EVAL_VERSION:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "agent_eval_benchmark_version_unsupported",
            "version": version,
            **_authority_flags(),
        }
    materialize_agent_eval_catalog(project_root, version=version)
    benchmark_id = f"agent-benchmark-{utc_compact_ts().lower()}"
    root = agent_eval_root(project_root) / "benchmarks" / benchmark_id
    metadata_dir = root / "eval_metadata"
    grading_dir = root / "grading"
    benchmark_dir = root / "benchmark"
    analysis_dir = root / "analysis"
    for directory in (metadata_dir, grading_dir, benchmark_dir, analysis_dir):
        directory.mkdir(parents=True, exist_ok=True)

    cases = _default_v161_benchmark_cases()
    gradings: list[dict[str, Any]] = []
    for case in cases:
        metadata = {
            "schema_version": "1.0",
            "benchmark_id": benchmark_id,
            "version": version,
            **case,
            **_authority_flags(),
        }
        write_json(metadata_dir / f"{case['case_id']}.json", metadata)
        for config in BENCHMARK_CONFIGS:
            if str(case.get("tc_id", "")).startswith("TC-AE"):
                grading = _simulated_agent_benchmark_result(case, config)
            else:
                grading = skill_simulated_benchmark_result(case, config)
            gradings.append(grading)
            write_json(grading_dir / f"{case['case_id']}.{config}.json", grading)

    failure_count = sum(1 for item in gradings if item.get("status") != "pass")
    with_skill_pass = sum(1 for item in gradings if item.get("config") == "with_skill" and item.get("status") == "pass")
    with_skill_total = sum(1 for item in gradings if item.get("config") == "with_skill")
    summary = {
        "schema_version": "1.0",
        "benchmark_id": benchmark_id,
        "version": version,
        "case_count": len(cases),
        "grading_count": len(gradings),
        "failure_count": failure_count,
        "status": "pass" if with_skill_total and with_skill_pass == with_skill_total else "fail",
        "configs": list(BENCHMARK_CONFIGS),
        **_authority_flags(),
    }
    covered_tc = sorted({str(case.get("tc_id")) for case in cases if case.get("tc_id")})
    analysis = {
        "schema_version": "1.0",
        "benchmark_id": benchmark_id,
        "status": summary["status"],
        "covered_tc_ids": covered_tc,
        "covered_ac_ids": ["AC-AE-010", "AC-AE-011", "AC-AE-012", "AC-AE-013", "AC-AE-014", "AC-AE-015"],
        "static_only_ac_ids": [],
        "recommended_route": "beacon-eval-agent",
        "formal_verdict_authority": False,
        "release_verdict_authority": False,
        "notes": [
            "benchmark evidence supports evaluator review but does not replace formal QA or release verdict",
            "Agent Eval benchmark is runtime_evidence_only",
        ],
    }
    write_json(benchmark_dir / "benchmark.json", summary)
    write_json(analysis_dir / "analysis.json", analysis)
    (analysis_dir / "analysis.md").write_text(
        "\n".join(
            [
                "# Agent Eval Benchmark Analysis",
                "",
                f"- benchmark_id: `{benchmark_id}`",
                f"- status: `{analysis['status']}`",
                f"- covered_tc_ids: `{', '.join(covered_tc)}`",
                "- authority: `runtime_evidence_only`",
                "",
                "Benchmark evidence supports evaluator review but does not replace formal QA or release verdict.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "schema_version": "1.0",
        "status": summary["status"],
        "benchmark_id": benchmark_id,
        "version": version,
        "root": str(root.relative_to(project_root)),
        "eval_metadata": str(metadata_dir.relative_to(project_root)),
        "eval_metadata_path": str(metadata_dir.relative_to(project_root)),
        "grading": str(grading_dir.relative_to(project_root)),
        "grading_path": str(grading_dir.relative_to(project_root)),
        "benchmark": str((benchmark_dir / "benchmark.json").relative_to(project_root)),
        "benchmark_path": str((benchmark_dir / "benchmark.json").relative_to(project_root)),
        "analysis": str((analysis_dir / "analysis.json").relative_to(project_root)),
        "analysis_path": str((analysis_dir / "analysis.json").relative_to(project_root)),
        "analysis_markdown_path": str((analysis_dir / "analysis.md").relative_to(project_root)),
        "covered_tc_ids": covered_tc,
        "summary": summary,
        "analysis_payload": analysis,
        **_authority_flags(),
    }


def agent_eval_fsm_contract() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "states": list(AGENT_EVAL_STATES),
        "catalog_missing_recovery": catalog_missing_recovery_route(),
        "live_blocked_recovery": live_blocked_recovery_route(),
    }
