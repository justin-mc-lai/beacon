"""Product Goal Runtime — single public entry facade (v1.6.7 R3).

User-facing: beacon goal run / beacon-goal skill only.
Internal: progressive skill load, optional loop-goal support, ralph implement,
main_star_satellite_pool parallel plan. Complete requires verifier evidence.
"""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, Literal

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, resolve_target_version
from beacon.utils.goal_queue import consume_next, list_queued

SCHEMA_VERSION = "1.0"
PUBLIC_ENTRY = "beacon-goal"
PUBLIC_CLI = "beacon goal run"
PUBLIC_ALIAS = "beacon run"
SUPPORT_LOOP = "beacon-loop-goal"

WorktreeMode = Literal["single_worktree", "main_star_satellite_pool"]

PROGRESSIVE_SKILLS: dict[str, list[str]] = {
    "discover": [SUPPORT_LOOP],  # support only
    "plan": ["beacon-pln-program", "beacon-pln-program-auto", "beacon-pln-program-interactive"],
    "truth": ["beacon-gen-truth", "beacon-gen-change"],
    "design": ["beacon-gen-design", "beacon-gen-design-system", "beacon-gen-design-polish"],
    "implement": ["beacon-gen-implement"],
    "qa": ["beacon-eval-qa", "beacon-eval-qa-deep"],
    "release": ["beacon-eval-release"],
}

# Base order; `design` is inserted when UX/visual delivery is claimed.
STAGE_ORDER_BASE = ("plan", "truth", "implement", "qa", "release")
STAGE_ORDER = STAGE_ORDER_BASE  # backward-compatible alias

REASON_VERIFIER_REQUIRED = "product_goal_complete_requires_verifier"
REASON_NOT_FOUND = "product_goal_run_not_found"
REASON_BLOCKED_STREAK = "product_goal_blocked_streak"
REASON_DUAL_ENTRY = "product_goal_dual_public_entry_forbidden"


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def product_goal_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 6, 7)


def public_entry_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "public_primary": PUBLIC_ENTRY,
        "public_cli": PUBLIC_CLI,
        "public_alias": PUBLIC_ALIAS,
        "support_only": [SUPPORT_LOOP],
        "forbidden_user_sequence": [f"{SUPPORT_LOOP} then {PUBLIC_ENTRY}"],
        "single_entry": True,
        "dual_public_orchestration": False,
    }


def goal_state_dir(project_root: Path) -> Path:
    return Path(project_root) / ".beacon" / "state" / "product-goal"


def goal_state_path(project_root: Path, run_id: str) -> Path:
    return goal_state_dir(project_root) / f"{run_id}.json"


def _new_run_id() -> str:
    return f"pgr-{uuid.uuid4().hex[:12]}"


def detect_parallel_intent(utterance: str) -> bool:
    text = str(utterance or "").lower()
    markers = (
        "parallel",
        "subagent",
        "sub-agent",
        "多湖",
        "并行",
        "satellite",
        "主星",
        "卫星",
        "worktree pool",
    )
    return any(m in text for m in markers)




def detect_ux_intent(utterance: str = "", *, truth_markdown: str = "", lakes: list[str] | None = None) -> bool:
    """Whether goal should insert design stage (ux_required / visual delivery)."""
    from beacon.utils.design_surfaces import scan_truth_for_ux

    if scan_truth_for_ux(truth_markdown).get("visual_delivery_claimed"):
        return True
    text = f"{utterance}\n{truth_markdown}".lower()
    markers = (
        "ux_required",
        "design.md",
        "ui-state-matrix",
        "视觉",
        "界面",
        "ui/ux",
        "ui design",
        "前端页面",
        "中台",
        "h5",
        "sidebar",
        "design baseline",
    )
    if any(m in text for m in markers):
        return True
    for lake in lakes or []:
        if any(tok in str(lake).lower() for tok in ("ui", "ux", "design", "前端", "中台")):
            return True
    return False


def build_stage_order(*, ux_required: bool = False) -> tuple[str, ...]:
    if ux_required:
        return ("plan", "truth", "design", "implement", "qa", "release")
    return STAGE_ORDER_BASE


def build_parallel_plan(
    *,
    lakes: list[str] | None = None,
    mode: WorktreeMode | None = None,
    utterance: str = "",
) -> dict[str, Any]:
    lake_list = [feature_slug(item) for item in (lakes or []) if str(item).strip()]
    resolved_mode: WorktreeMode
    if mode in ("single_worktree", "main_star_satellite_pool"):
        resolved_mode = mode  # type: ignore[assignment]
    elif detect_parallel_intent(utterance) or len(lake_list) > 1:
        resolved_mode = "main_star_satellite_pool"
    else:
        resolved_mode = "single_worktree"

    satellites: list[dict[str, Any]] = []
    if resolved_mode == "main_star_satellite_pool":
        for lake in lake_list or ["lake-placeholder"]:
            satellites.append(
                {
                    "lake": lake,
                    "role": "satellite",
                    "worktree": f".beacon/worktrees/satellite/{lake}",
                    "merge_target": "main_star",
                    "may_write_truth_on_main": False,
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": resolved_mode,
        "main_star": {
            "role": "main_star",
            "worktree": ".",
            "merge_policy": "satellites_merge_to_star_only",
        },
        "satellites": satellites,
        "one_lake_one_satellite": resolved_mode == "main_star_satellite_pool",
    }


def progressive_skills_for_stage(stage: str) -> list[str]:
    return list(PROGRESSIVE_SKILLS.get(str(stage or "").strip().lower(), []))


def build_stage_plan(
    *,
    utterance: str = "",
    lakes: list[str] | None = None,
    truth_markdown: str = "",
    ux_required: bool | None = None,
) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    ux = bool(ux_required) if ux_required is not None else detect_ux_intent(
        utterance, truth_markdown=truth_markdown, lakes=lakes
    )
    order = build_stage_order(ux_required=ux)
    for stage in order:
        skills = progressive_skills_for_stage(stage)
        stages.append(
            {
                "stage": stage,
                "skills": skills,
                "status": "planned",
                "loaded": False,
                **({"ux_gated": True} if stage == "design" else {}),
            }
        )
    if detect_parallel_intent(utterance) or (lakes and len(lakes) > 1):
        for item in stages:
            if item["stage"] == "implement":
                item["parallel"] = True
                item["worktree_mode"] = "main_star_satellite_pool"
    return stages


def create_goal_run(
    project_root: Path,
    *,
    utterance: str,
    version: str = "auto",
    feature: str = "",
    lakes: list[str] | None = None,
    worktree_mode: WorktreeMode | None = None,
    done_when: list[str] | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    run_id = _new_run_id()
    parallel = build_parallel_plan(lakes=lakes, mode=worktree_mode, utterance=utterance)
    ux_required = detect_ux_intent(utterance, lakes=lakes)
    stages = build_stage_plan(utterance=utterance, lakes=lakes, ux_required=ux_required)
    default_done = ["domain_fsm", "evidence_chain", "continuous_qa"]
    if ux_required:
        default_done = ["design_baseline", "design_md_lint", "domain_fsm", "evidence_chain", "continuous_qa"]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "public_entry": PUBLIC_ENTRY,
        "status": "running",
        "blocked": False,
        "reason_code": "",
        "utterance": str(utterance or "").strip(),
        "version": resolved_version,
        "feature": feature_slug(feature) if feature else "",
        "lakes": [feature_slug(x) for x in (lakes or []) if str(x).strip()],
        "done_when": done_when or default_done,
        "ux_required": ux_required,
        "stages": stages,
        "current_stage": stages[0]["stage"] if stages else "",
        "progressive_loaded_skills": [],
        "parallel_plan": parallel,
        "blocked_streak": 0,
        "implement_delegate": "",
        "verifier": {
            "required_for_complete": True,
            "present": False,
            "refs": [],
            "source": "",
        },
        "release_human_gate": True,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "history": [{"event": "created", "at": now_iso()}],
    }
    path = goal_state_path(project_root, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, payload)
    payload["state_path"] = str(path.relative_to(project_root))
    return payload


def load_goal_run(project_root: Path, run_id: str) -> dict[str, Any]:
    path = goal_state_path(project_root, run_id)
    if not path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_NOT_FOUND,
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"status": "blocked", "reason_code": REASON_NOT_FOUND}


def _save(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    run_id = str(payload.get("run_id") or "")
    payload["updated_at"] = now_iso()
    path = goal_state_path(project_root, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, payload)
    payload["state_path"] = str(path.relative_to(Path(project_root).resolve()))
    return payload


def load_stage_skills(project_root: Path, run_id: str, stage: str) -> dict[str, Any]:
    payload = load_goal_run(project_root, run_id)
    if payload.get("blocked") and payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    skills = progressive_skills_for_stage(stage)
    loaded = list(payload.get("progressive_loaded_skills") or [])
    for skill in skills:
        if skill not in loaded:
            loaded.append(skill)
    payload["progressive_loaded_skills"] = loaded
    for item in payload.get("stages") or []:
        if isinstance(item, dict) and item.get("stage") == stage:
            item["loaded"] = True
            item["status"] = "active" if item.get("status") == "planned" else item.get("status")
    payload["current_stage"] = stage
    hist = list(payload.get("history") or [])
    hist.append({"event": "stage_skills_loaded", "stage": stage, "skills": skills, "at": now_iso()})
    payload["history"] = hist
    return _save(project_root, payload)


def tick_goal_run(project_root: Path, run_id: str, *, note: str = "") -> dict[str, Any]:
    """Advance one stage in the facade plan (orchestration record, not self-certify)."""
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    stages = payload.get("stages") if isinstance(payload.get("stages"), list) else []
    current = str(payload.get("current_stage") or "")
    idx = next((i for i, s in enumerate(stages) if isinstance(s, dict) and s.get("stage") == current), 0)
    if idx < len(stages) and isinstance(stages[idx], dict):
        stages[idx]["status"] = "done"
        stages[idx]["loaded"] = True
        # progressive load for this stage if not yet
        for skill in stages[idx].get("skills") or []:
            loaded = list(payload.get("progressive_loaded_skills") or [])
            if skill not in loaded:
                loaded.append(skill)
            payload["progressive_loaded_skills"] = loaded
    next_idx = idx + 1
    if next_idx < len(stages) and isinstance(stages[next_idx], dict):
        next_stage = str(stages[next_idx]["stage"])
        payload["current_stage"] = next_stage
        payload["status"] = "running"
        payload = load_stage_skills(project_root, run_id, next_stage)
        payload = load_goal_run(project_root, run_id)
        if next_stage == "design":
            payload = run_design_stage_for_goal(project_root, run_id)
    else:
        payload["status"] = "awaiting_verifier"
        payload["current_stage"] = "complete_gate"
    hist = list(payload.get("history") or [])
    hist.append({"event": "tick", "note": note, "at": now_iso()})
    payload["history"] = hist
    payload["stages"] = stages
    return _save(project_root, payload)




def run_design_stage_for_goal(
    project_root: Path,
    run_id: str,
    *,
    force: bool = False,
    surface: str = "auto",
    company_template: str = "auto",
) -> dict[str, Any]:
    """Execute unattended design baseline + lint for the goal design stage."""
    from beacon.utils.design_baseline import synthesize_unattended_design_baseline
    from beacon.utils.design_company_templates import auto_select_company_template
    from beacon.utils.design_md_lint import run_design_md_lint
    from beacon.utils.design_surfaces import auto_select_surface_from_text

    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    project_root = Path(project_root).expanduser().resolve()
    version = str(payload.get("version") or "auto")
    utterance = str(payload.get("utterance") or "")
    lakes = list(payload.get("lakes") or [])
    truth_bits = [utterance]
    # harvest feature truth if feature set
    feature = str(payload.get("feature") or "")
    if feature:
        tp = project_root / "docs" / "beacon" / version / "features" / feature / "truth.md"
        if not tp.exists():
            # version may be auto-resolved already in payload
            from beacon.utils.versioning import resolve_target_version
            resolved = resolve_target_version(project_root, version)
            tp = project_root / "docs" / "beacon" / resolved / "features" / feature / "truth.md"
        if tp.exists():
            truth_bits.append(tp.read_text(encoding="utf-8")[:12000])
    surface_decision = auto_select_surface_from_text(*truth_bits) if surface == "auto" else {"surface": surface, "reason": "explicit"}
    company = auto_select_company_template(*truth_bits, surface=str(surface_decision.get("surface") or "web"))
    if company_template and company_template != "auto":
        from beacon.utils.design_company_templates import COMPANY_DESIGN_TEMPLATES
        meta = COMPANY_DESIGN_TEMPLATES.get(company_template) or {}
        company = {
            **company,
            "company_template": company_template,
            "label": meta.get("label") or company_template,
            "reason": "explicit",
            "default_preset": meta.get("default_preset") or company.get("default_preset"),
            "colors": meta.get("colors") or company.get("colors"),
        }
    baseline = synthesize_unattended_design_baseline(
        project_root,
        version,
        preset=str(company.get("default_preset") or "restrained-product"),
        surface=str(surface_decision.get("surface") or "web"),
        force=force,
        write_version_contracts=True,
        product_name=project_root.name,
        truth_markdown="\n".join(truth_bits),
    )
    # apply company colors overlay into machine projection note
    lint = run_design_md_lint(project_root, feature=feature or "project", version=version, write_evidence=True)
    design_state = {
        "baseline": {
            "status": baseline.get("status"),
            "mode": baseline.get("mode"),
            "surface": baseline.get("surface"),
            "surface_decision": baseline.get("surface_decision"),
            "design_path": baseline.get("design_path"),
            "fine_tune_proposal_path": baseline.get("fine_tune_proposal_path"),
            "writes": baseline.get("writes"),
        },
        "company_template": company,
        "lint": {
            "status": lint.get("status"),
            "blocked": lint.get("blocked"),
            "reason_code": lint.get("reason_code"),
            "evidence_path": lint.get("evidence_path"),
            "summary": lint.get("summary"),
            "runner": lint.get("runner"),
        },
        "completed_at": now_iso(),
    }
    payload["design_stage"] = design_state
    # mark design stage done if present
    for item in payload.get("stages") or []:
        if isinstance(item, dict) and item.get("stage") == "design":
            item["status"] = "done" if not lint.get("blocked") else "blocked"
            item["loaded"] = True
            item["artifact"] = design_state
    if lint.get("blocked"):
        payload["blocked"] = True
        payload["reason_code"] = str(lint.get("reason_code") or "design_md_lint_failed")
        payload["status"] = "blocked"
    hist = list(payload.get("history") or [])
    hist.append({"event": "design_stage_ran", "at": now_iso(), "lint_status": lint.get("status"), "surface": baseline.get("surface")})
    payload["history"] = hist
    return _save(project_root, payload)


def record_blocker(project_root: Path, run_id: str, *, reason_code: str) -> dict[str, Any]:
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    streak = int(payload.get("blocked_streak") or 0) + 1
    payload["blocked_streak"] = streak
    payload["blocked"] = True
    payload["reason_code"] = reason_code or REASON_BLOCKED_STREAK
    payload["status"] = "blocked" if streak >= 3 else "running"
    if streak >= 3:
        payload["reason_code"] = REASON_BLOCKED_STREAK
    hist = list(payload.get("history") or [])
    hist.append({"event": "blocked", "reason_code": reason_code, "streak": streak, "at": now_iso()})
    payload["history"] = hist
    return _save(project_root, payload)


def attach_verifier(
    project_root: Path,
    run_id: str,
    *,
    refs: list[str],
    source: str = "beacon-eval-qa",
) -> dict[str, Any]:
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    clean_refs = [str(r).strip() for r in refs if str(r).strip()]
    payload["verifier"] = {
        "required_for_complete": True,
        "present": bool(clean_refs),
        "refs": clean_refs,
        "source": source,
    }
    if clean_refs:
        payload["blocked"] = False
        if payload.get("status") == "blocked" and payload.get("blocked_streak", 0) < 3:
            payload["status"] = "awaiting_verifier"
    hist = list(payload.get("history") or [])
    hist.append({"event": "verifier_attached", "refs": clean_refs, "source": source, "at": now_iso()})
    payload["history"] = hist
    return _save(project_root, payload)


def complete_goal_run(project_root: Path, run_id: str, *, force: bool = False) -> dict[str, Any]:
    """Mark complete only when verifier evidence is present (no self-certify)."""
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    verifier = payload.get("verifier") if isinstance(payload.get("verifier"), dict) else {}
    if not force and not (bool(verifier.get("present")) and list(verifier.get("refs") or [])):
        payload["status"] = "blocked"
        payload["blocked"] = True
        payload["reason_code"] = REASON_VERIFIER_REQUIRED
        hist = list(payload.get("history") or [])
        hist.append({"event": "complete_rejected", "reason_code": REASON_VERIFIER_REQUIRED, "at": now_iso()})
        payload["history"] = hist
        return _save(project_root, payload)
    payload["status"] = "completed"
    payload["blocked"] = False
    payload["reason_code"] = ""
    payload["completed_at"] = now_iso()
    hist = list(payload.get("history") or [])
    hist.append({"event": "completed", "at": now_iso(), "force": force})
    payload["history"] = hist
    return _save(project_root, payload)


def run_goal_facade(
    project_root: Path,
    *,
    utterance: str,
    version: str = "auto",
    feature: str = "",
    lakes: list[str] | None = None,
    worktree_mode: WorktreeMode | None = None,
    auto_tick: bool = False,
) -> dict[str, Any]:
    """Public facade: create goal run and optionally advance planning stages."""
    payload = create_goal_run(
        project_root,
        utterance=utterance,
        version=version,
        feature=feature,
        lakes=lakes,
        worktree_mode=worktree_mode,
    )
    # progressive load first stage only
    first = str(payload.get("current_stage") or "plan")
    payload = load_stage_skills(project_root, payload["run_id"], first)
    if auto_tick:
        # advance through plan→truth record only; never self-claim qa/release
        for _ in range(2):
            payload = tick_goal_run(project_root, payload["run_id"], note="auto_tick_facade")
    payload["entry_contract"] = public_entry_contract()
    payload["recommended_next"] = {
        "human": "continue via $beacon-goal or beacon goal tick/resume",
        "complete": "requires verifier refs (beacon-eval-qa evidence), then beacon goal complete",
        "release": "human gate via beacon-eval-release",
    }
    return payload


def docs_forbid_dual_call(paths: list[Path]) -> dict[str, Any]:
    """Scan main docs for forbidden dual-call user paths."""
    violations: list[dict[str, str]] = []
    pattern = re.compile(
        r"(先\s*\$?beacon-loop-goal.*\$?beacon-goal)|(\$beacon-loop-goal\s*[\n\r]+.*\$beacon-goal)|(先\s*loop\s*后\s*goal)",
        re.IGNORECASE | re.DOTALL,
    )
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # allow explicit "不要这样用" negative examples
        for m in pattern.finditer(text):
            start = max(0, m.start() - 80)
            window = text[start : m.end() + 40]
            if any(tok in window for tok in ("不要", "❌", "禁止", "not", "Do **not**", "不要这样")):
                continue
            violations.append({"path": str(path), "snippet": window.replace("\n", " ")[:160]})
    return {
        "blocked": bool(violations),
        "violations": violations,
        "status": "blocked" if violations else "pass",
    }


def loop_goal_support_metadata(skill_md: str) -> dict[str, Any]:
    text = str(skill_md or "")
    lowered = text.lower()
    marked = any(
        token in lowered
        for token in (
            "support",
            "support/internal",
            "support only",
            "discovery",
            "发现",
            "非并列",
            "support discovery",
        )
    )
    # also check frontmatter role
    if "role: support" in lowered or "entry: support" in lowered or "support/internal" in lowered:
        marked = True
    return {"marked_support": marked, "status": "pass" if marked else "blocked"}


def delegate_implement_to_ralph(project_root: Path, run_id: str, *, feature: str = "") -> dict[str, Any]:
    """Product Goal records implement stage delegation to Ralph (not product complete)."""
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    payload["implement_delegate"] = "ralph"
    if feature:
        payload["feature"] = feature_slug(feature)
    # ensure implement stage annotated
    for item in payload.get("stages") or []:
        if isinstance(item, dict) and item.get("stage") == "implement":
            item["delegate"] = "ralph"
            item["status"] = item.get("status") or "planned"
    hist = list(payload.get("history") or [])
    hist.append({"event": "implement_delegate_ralph", "at": now_iso()})
    payload["history"] = hist
    payload = load_stage_skills(project_root, run_id, "implement")
    payload = load_goal_run(project_root, run_id)
    payload["implement_delegate"] = "ralph"
    return _save(project_root, payload)


def consume_discovery_queue(project_root: Path, *, version: str = "auto") -> dict[str, Any]:
    """Goal consumes one loop discovery queue item and starts a facade run."""
    queued = list_queued(project_root, status="queued")
    consumed = consume_next(project_root, consumer="beacon-goal")
    if consumed.get("status") == "empty":
        return {
            "status": "empty",
            "blocked": False,
            "reason_code": "goal_queue_empty",
            "queued_count": 0,
        }
    item = consumed.get("item") if isinstance(consumed.get("item"), dict) else {}
    run = run_goal_facade(
        project_root,
        utterance=str(item.get("utterance") or ""),
        version=str(item.get("version") or version or "auto"),
        feature=str(item.get("feature") or ""),
    )
    run["from_queue_item"] = item.get("id")
    run["discovery_source"] = item.get("source")
    return run
