"""v1.6.8 production ops hardening: hotfix lane, release profiles, longrun default, version fleet."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json

REASON_HF_MISSING_BASELINE = "hotfix_baseline_missing"
REASON_HF_FORWARD_PORT = "hotfix_forward_port_required"
REASON_HF_ROLLBACK = "hotfix_rollback_notes_required"
REASON_MANIFEST_MISMATCH = "evidence_sha256_manifest_mismatch"
REASON_DUAL_VERSION_INCOMPLETE = "dual_version_contract_incomplete"

RELEASE_PROFILES = ("full", "hotfix", "docs_only")

HOTFIX_REQUIRED_GATES = (
    "evidence_manifest",
    "hotfix_baseline",
    "forward_port_plan",
    "rollback_notes",
    "minimal_qa",
    "human_release",
)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return data if isinstance(data, dict) else {}


def project_metadata_path(project_root: Path) -> Path:
    return Path(project_root) / ".beacon" / "project-metadata.json"


def load_goal_ops_config(project_root: Path) -> dict[str, Any]:
    meta = _read_json(project_metadata_path(project_root))
    goal = meta.get("goal") if isinstance(meta.get("goal"), dict) else {}
    # Default true for greenfield; if file missing treat as true (v1.6.8 policy)
    longrun_default = goal.get("longrun_default")
    if longrun_default is None:
        longrun_default = True
    return {
        "longrun_default": bool(longrun_default),
        "hotfix_branch_naming_rule": str(goal.get("hotfix_branch_naming_rule") or "hotfix/*"),
        "release_profile_default": str(goal.get("release_profile_default") or "full"),
    }


def set_goal_ops_config(project_root: Path, **kwargs: Any) -> dict[str, Any]:
    path = project_metadata_path(project_root)
    meta = _read_json(path)
    goal = meta.get("goal") if isinstance(meta.get("goal"), dict) else {}
    for key, value in kwargs.items():
        if value is not None:
            goal[key] = value
    meta["goal"] = goal
    meta["updated_at"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, meta)
    return load_goal_ops_config(project_root)


def resolve_longrun_enabled(project_root: Path, *, cli_longrun: bool | None = None) -> dict[str, Any]:
    cfg = load_goal_ops_config(project_root)
    if cli_longrun is True:
        return {"enabled": True, "source": "cli_flag", "config": cfg}
    if cli_longrun is False:
        return {"enabled": False, "source": "cli_flag_off", "config": cfg}
    return {"enabled": bool(cfg["longrun_default"]), "source": "project_default", "config": cfg}


def build_hotfix_plan(
    *,
    utterance: str,
    from_version: str = "",
    production_tag: str = "",
    forward_port_target: str = "",
    rollback_notes: str = "",
) -> dict[str, Any]:
    baseline = (from_version or production_tag or "").strip()
    blocked = False
    reasons: list[str] = []
    if not baseline:
        blocked = True
        reasons.append(REASON_HF_MISSING_BASELINE)
    if not str(forward_port_target or "").strip():
        # plan may be drafted later; mark required not satisfied until filled
        reasons.append(REASON_HF_FORWARD_PORT)
    if not str(rollback_notes or "").strip():
        reasons.append(REASON_HF_ROLLBACK)
    # release-ready for hotfix requires all
    release_ready = (not blocked) and not reasons
    return {
        "schema_version": "1.0",
        "mode": "hotfix",
        "utterance": utterance,
        "from_version": from_version,
        "production_tag": production_tag,
        "baseline_ref": baseline,
        "forward_port_target": forward_port_target,
        "rollback_notes": rollback_notes,
        "release_profile": "hotfix",
        "required_gates": list(HOTFIX_REQUIRED_GATES),
        "blocked": blocked or bool(reasons),
        "reason_codes": reasons,
        "release_ready": release_ready,
        "generated_at": now_iso(),
        "illegal": [
            "I-HF-001 hotfix without baseline",
            "I-HF-002 hotfix without forward_port plan",
            "I-HF-003 next_feature as first_production_fix",
            "I-HF-004 HotfixLane completes GoalRun",
        ],
    }


def validate_hotfix_for_release(plan: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if not str(plan.get("baseline_ref") or "").strip():
        reasons.append(REASON_HF_MISSING_BASELINE)
    if not str(plan.get("forward_port_target") or "").strip():
        reasons.append(REASON_HF_FORWARD_PORT)
    if not str(plan.get("rollback_notes") or "").strip():
        reasons.append(REASON_HF_ROLLBACK)
    return {
        "ok": not reasons,
        "blocked": bool(reasons),
        "reason_codes": reasons,
        "release_profile": "hotfix",
        "recommended_commands": [
            "beacon goal hotfix-plan --from-version <tag> --forward-port <branch> --rollback-notes \"...\"",
        ],
    }


def select_release_profile(name: str) -> dict[str, Any]:
    profile = str(name or "full").strip().lower()
    if profile not in RELEASE_PROFILES:
        return {
            "ok": False,
            "blocked": True,
            "reason_code": "release_profile_invalid",
            "profile": profile,
            "allowed": list(RELEASE_PROFILES),
        }
    if profile == "hotfix":
        gates = list(HOTFIX_REQUIRED_GATES)
    elif profile == "docs_only":
        gates = ["docs_consistency", "human_release"]
    else:
        gates = ["full_suite"]
    return {
        "ok": True,
        "blocked": False,
        "profile": profile,
        "gates": gates,
        "reason_code": "",
    }


def repair_evidence_manifest(project_root: Path, *, version: str = "v1.6.8") -> dict[str, Any]:
    root = Path(project_root).resolve()
    manifest_path = root / ".beacon" / "evidence-manifest.json"
    payload = _read_json(manifest_path)
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    rebuilt: list[dict[str, Any]] = []
    dropped: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rel = str(entry.get("path") or "").strip()
        if not rel or rel.startswith("/") or "\\" in rel:
            continue
        if "/_bak" in rel or "/_backup" in rel:
            dropped.append(rel)
            continue
        path = root / rel
        if not path.is_file():
            dropped.append(rel)
            continue
        rebuilt.append(
            {
                "path": rel,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "updated_at": now_iso(),
            }
        )
    out = {
        "schema_version": "1.0",
        "entries": rebuilt,
        "updated_at": now_iso(),
        "version": version,
        "rebuild_reason": "doctor repair-evidence-manifest",
        "dropped_count": len(dropped),
        "dropped_sample": dropped[:20],
    }
    if payload.get("run_id"):
        out["run_id"] = payload.get("run_id")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(manifest_path, out)
    return {
        "ok": True,
        "path": str(manifest_path.relative_to(root)),
        "entry_count": len(rebuilt),
        "dropped_count": len(dropped),
        "recommended_command": "beacon gate check release -v <version> -p .",
    }


def align_run_id(project_root: Path, *, run_id: str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    rid = str(run_id or "").strip()
    if not rid:
        return {"ok": False, "blocked": True, "reason_code": "run_id_required"}
    updated: list[str] = []
    for rel in (
        ".beacon/auto-test-status.json",
        ".beacon/qa/status.json",
        ".beacon/coverage-summary.json",
        ".beacon/evidence-manifest.json",
    ):
        path = root / rel
        if not path.exists():
            continue
        data = _read_json(path)
        if not data and rel.endswith("evidence-manifest.json"):
            continue
        data["run_id"] = rid
        if isinstance(data.get("execution"), dict):
            data["execution"]["run_id"] = rid
        write_json(path, data)
        updated.append(rel)
    # signature chain append
    chain_path = root / ".beacon" / "evidence-signature-chain.json"
    chain: list[Any] = []
    if chain_path.exists():
        try:
            loaded = json.loads(chain_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                chain = loaded
        except Exception:  # noqa: BLE001
            chain = []
    chain = [e for e in chain if not (isinstance(e, dict) and e.get("run_id") == rid)]
    summary = root / ".beacon" / "auto-test-status.json"
    chain.append(
        {
            "run_id": rid,
            "summary_path": ".beacon/auto-test-status.json",
            "summary_sha256": hashlib.sha256(summary.read_bytes()).hexdigest() if summary.exists() else "",
            "created_at": now_iso(),
        }
    )
    write_json(chain_path, chain)
    updated.append(".beacon/evidence-signature-chain.json")
    return {"ok": True, "run_id": rid, "updated": updated}


def build_version_fleet(project_root: Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    catalog = root / "docs" / "beacon" / "governance" / "version-truth-catalog.md"
    versions: list[str] = []
    if catalog.exists():
        text = catalog.read_text(encoding="utf-8")
        versions = re.findall(r"### (v\d+\.\d+\.\d+)", text)
    # active roots
    docs = root / "docs" / "beacon"
    roots = sorted(
        p.name for p in docs.iterdir() if p.is_dir() and re.match(r"v\d+\.\d+\.\d+$", p.name)
    ) if docs.exists() else []
    vt = _read_json(root / "beacon" / "version-truth.json")
    current = str(vt.get("current_runtime_release_line") or vt.get("runtime_version") or "").strip()
    planning = vt.get("planning_lines") if isinstance(vt.get("planning_lines"), list) else []
    return {
        "schema_version": "1.0",
        "prod": current,
        "maint": current,
        "next": (planning[0] if planning else (roots[-1] if roots else "")),
        "planning": planning,
        "active_roots": roots,
        "catalog_versions": versions,
        "generated_at": now_iso(),
    }


def dual_version_contract_path(project_root: Path) -> Path:
    return Path(project_root) / ".beacon" / "dual-version-contract.json"


def init_dual_version(
    project_root: Path,
    *,
    previous_baseline: str,
    next_feature: str,
    hotfix_rule: str = "hotfix/*",
) -> dict[str, Any]:
    contract = {
        "schema_version": "1.0",
        "template_name": "previous-hotfix-forward-port",
        "previous_version_baseline_branch": previous_baseline,
        "next_version_feature_branch": next_feature,
        "hotfix_branch_naming_rule": hotfix_rule,
        "merge_direction_policy": [
            "previous_baseline->hotfix",
            "hotfix->uat",
            "hotfix->next_feature",
        ],
        "forbidden_directions": ["next_feature->first_production_fix"],
        "evidence_contract": [
            "source_commit",
            "forward_port_commit",
            "origin_uat_head",
            "pipeline_run_id",
        ],
        "generated_at": now_iso(),
    }
    path = dual_version_contract_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, contract)
    set_goal_ops_config(project_root, hotfix_branch_naming_rule=hotfix_rule)
    return {"ok": True, "path": str(path), "contract": contract}


def verify_dual_version(project_root: Path) -> dict[str, Any]:
    path = dual_version_contract_path(project_root)
    contract = _read_json(path)
    missing = []
    for key in (
        "previous_version_baseline_branch",
        "next_version_feature_branch",
        "hotfix_branch_naming_rule",
    ):
        if not str(contract.get(key) or "").strip():
            missing.append(key)
    if not path.exists() or missing:
        return {
            "ok": False,
            "blocked": True,
            "reason_code": REASON_DUAL_VERSION_INCOMPLETE,
            "missing": missing,
            "recommended_command": (
                "beacon doctor init-dual-version --previous-baseline <branch> "
                "--next-feature <branch> --hotfix-rule 'hotfix/*'"
            ),
        }
    return {"ok": True, "blocked": False, "contract": contract, "path": str(path)}


def forbidden_production_fix_from_next(direction: str, dual_on: bool) -> dict[str, Any]:
    d = str(direction or "").strip()
    if dual_on and d in {
        "next_feature->first_production_fix",
        "next->prod_fix",
        "next_feature->prod",
    }:
        return {
            "ok": False,
            "blocked": True,
            "reason_code": "forbidden_direction_next_to_prod_fix",
            "direction": d,
        }
    return {"ok": True, "blocked": False, "direction": d}
