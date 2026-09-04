"""Product Goal Runtime — single public entry facade (v1.6.7 R3).

User-facing: beacon goal run / beacon-goal skill only.
Internal: progressive skill load, optional loop-goal support, ralph implement,
main_star_satellite_pool parallel plan. Complete requires verifier evidence.
"""

from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, resolve_target_version
from beacon.utils.version_defaults import resolve_goal_version
from beacon.utils.goal_queue import consume_next, list_queued
from beacon.utils.goal_durable_supervisor import (
    DEFAULT_HEARTBEAT_INTERVAL_SEC as DGS_DEFAULT_HEARTBEAT,
    MIN_HEARTBEAT_INTERVAL_SEC,
    REASON_HOST_INTERRUPTED as DGS_HOST_INTERRUPTED,
    append_execution_log,
    attach_supervisor as dgs_attach_supervisor,
    build_resume_pack,
    detach_supervisor as dgs_detach_supervisor,
    detect_stall,
    execution_log_path,
    goal_run_dir,
    load_checkpoint,
    mark_host_interrupted,
    memory_reindex,
    memory_search,
    normalize_interval,
    plan_tick_execute,
    record_heartbeat_on_payload,
    supervise_once as dgs_supervise_once,
    write_checkpoint,
)
from beacon.utils.multi_version_intent import (
    apply_multi_version_to_goal_payload,
    detect_multi_version_intent,
)
from beacon.utils.plan_subintent import plan_progressive_loads_for_utterance
from beacon.utils.plan_artifact import plan_to_truth_gate
from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate
from beacon.utils.goal_implement_admission import (
    apply_admission_to_goal_payload,
    ensure_goal_implement_admission,
)
from beacon.utils.goal_stage_exit_gates import (
    apply_stage_exit_block,
    evaluate_stage_exit,
)
from beacon.utils.program_admission import resolve_program_lake_topology
from beacon.utils.program_orchestrator import build_program_orchestrator_state, write_program_orchestrator_state
from beacon.utils.goal_agent_driver import (
    attach_longrun_to_goal_run,
    detect_longrun_intent,
    driver_start as gad_driver_start,
    driver_status as gad_driver_status,
    driver_stop as gad_driver_stop,
    driver_run_loop as gad_driver_run_loop,
    load_driver_state,
)

SCHEMA_VERSION = "1.0"
PUBLIC_ENTRY = "beacon-goal"
DESIGN_PHILOSOPHY_REF = "skills/beacon/references/design-philosophy-checklist.md"
DOMAIN_FSM_TRUTH_REF = "skills/beacon/references/domain-fsm-truth-checklist.md"

PUBLIC_CLI = "beacon goal run"
PUBLIC_ALIAS = "beacon run"
SUPPORT_LOOP = "beacon-goal"  # loop-goal is mode:loop-goal inside beacon-goal (1+6 merge)

WorktreeMode = Literal["single_worktree", "main_star_satellite_pool"]

PROGRESSIVE_SKILLS: dict[str, list[str]] = {
    # After 1+6 merge: only public cores + in-package mode tokens (not separate skill dirs).
    "discover": [PUBLIC_ENTRY],
    "plan": [
        "beacon-plan",
        "mode:pln-program",
        "mode:pln-program-auto",
        "mode:pln-program-interactive",
        "mode:pln-review",
        "mode:pln-friction",
        "mode:pln-brainstorm",
        "mode:pln-source",
    ],
    "truth": [
        "beacon-truth",
        "mode:gen-truth",
        "mode:gen-truth-init",
        "mode:gen-change",
        "mode:gen-refreeze",
    ],
    "design": [
        "beacon-design",
        "mode:gen-design",
        "mode:gen-design-init",
        "mode:gen-design-system",
        "mode:gen-design-explore",
        "mode:gen-design-polish",
        "mode:gen-prototype",
    ],
    "implement": ["beacon-implement", "mode:gen-implement"],
    "qa": [
        "beacon-qa",
        "mode:eval-qa",
        "mode:eval-qa-deep",
        "mode:eval-real-project",
        "mode:eval-agent",
    ],
    "release": ["beacon-release", "mode:eval-release"],
    "goal": [PUBLIC_ENTRY, "mode:loop-goal"],
}


_PROGRESSIVE_MAP_PATH = Path(__file__).resolve().parents[2] / "skills/beacon/references/public-surface-progressive-map.v1.json"


def load_progressive_map() -> dict[str, Any]:
    """Load Scheme A progressive map (public 1+6 → internal skills)."""
    try:
        if _PROGRESSIVE_MAP_PATH.is_file():
            return json.loads(_PROGRESSIVE_MAP_PATH.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        pass
    return {}


def progressive_loads_for_public_id(public_id: str) -> list[str]:
    """Resolve progressive internal skills for a public harness id or stage alias."""
    pid = str(public_id or "").strip().lower()
    # map rust / summary aliases
    aliases = {
        "loop": "plan",
        "qa-evidence": "qa",
        "generate": "implement",
        "evaluate": "qa",
    }
    pid = aliases.get(pid, pid)
    m = load_progressive_map()
    if pid == "goal":
        return list((m.get("goal_transversal") or {}).get("always_load") or [PUBLIC_ENTRY])
    harness = m.get("harness") if isinstance(m.get("harness"), dict) else {}
    meta = harness.get(pid) if isinstance(harness.get(pid), dict) else {}
    loads = meta.get("progressive_loads") if isinstance(meta.get("progressive_loads"), list) else None
    if loads:
        return [str(x) for x in loads if str(x).strip()]
    # fallback legacy table
    return list(PROGRESSIVE_SKILLS.get(pid, []))


def plan_goal_self_heal(*, phase: str = "pre") -> dict[str, Any]:
    """Gov self-heal band for goal lifecycle — user-facing language, not gov skill names."""
    m = load_progressive_map()
    sh = (m.get("goal_transversal") or {}).get("self_heal") if isinstance(m.get("goal_transversal"), dict) else {}
    sh = sh if isinstance(sh, dict) else {}
    key = "pre" if phase == "pre" else "mid_on_block" if phase in {"mid", "mid_on_block"} else "post_release"
    steps = sh.get(key) if isinstance(sh.get(key), list) else []
    return {
        "schema": "goal-self-heal.v1",
        "phase": key,
        "user_language": sh.get("user_language") or "never_expose_gov_skill_names_as_required_user_knowledge",
        "steps": steps,
        "note": "Framework rules run here automatically; users only confirm destructive steps.",
    }


def host_visible_whitelist(brand: str = "beacon") -> list[str]:
    m = load_progressive_map()
    wl = m.get("host_visible_whitelist") if isinstance(m.get("host_visible_whitelist"), dict) else {}
    items = wl.get(brand) if isinstance(wl.get(brand), list) else []
    return [str(x) for x in items if str(x).strip()]


# Shared git worktree process norm (AC-WT-SKILL / progressive always-on ref)
WORKTREE_FLOW_REF = "skills/beacon/references/git-worktree-execution-flow.md"
WORKTREE_EXAMPLE_REF = "skills/beacon/examples/git-worktree-process-correct-30s.md"
WORKTREE_FLOW_STAGES = frozenset(
    {"goal", "plan", "truth", "implement", "qa", "release", "discover", "loop"}
)

# Base order; `design` is inserted when UX/visual delivery is claimed.
STAGE_ORDER_BASE = ("plan", "truth", "implement", "qa", "release")
STAGE_ORDER = STAGE_ORDER_BASE  # backward-compatible alias

REASON_VERIFIER_REQUIRED = "product_goal_complete_requires_verifier"
REASON_NOT_FOUND = "product_goal_run_not_found"
REASON_BLOCKED_STREAK = "product_goal_blocked_streak"
REASON_DUAL_ENTRY = "product_goal_dual_public_entry_forbidden"
REASON_HOST_INTERRUPTED = "host_interrupted"
REASON_STAGE_BLOCKED = "stage_blocked"
DEFAULT_HEARTBEAT_INTERVAL_SEC = 120
MIN_HEARTBEAT_INTERVAL_SEC = 30


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
        "support_only": [],  # loop-goal merged into goal core
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


def progressive_skills_for_stage(stage: str, utterance: str = "") -> list[str]:
    """Stage → skills; Scheme A map + plan subintent primary-first routing."""
    st = str(stage or "").strip().lower()
    if st.startswith("beacon-") or st.startswith("loom-"):
        for prefix in ("beacon-", "loom-"):
            if st.startswith(prefix):
                st = st[len(prefix):]
                break
    aliases = {
        "loop": "plan",
        "qa-evidence": "qa",
        "generate": "implement",
        "evaluate": "qa",
    }
    st = aliases.get(st, st)

    # Plan harness: strong-intent primary_load (review/brainstorm/source/program/friction)
    if st == "plan" and str(utterance or "").strip():
        routed = plan_progressive_loads_for_utterance(utterance, brand="beacon")
        return list(routed.get("progressive_loads") or [])

    loads = progressive_loads_for_public_id(st)
    if loads:
        m = load_progressive_map()
        harness = m.get("harness") if isinstance(m.get("harness"), dict) else {}
        meta = harness.get(st) if isinstance(harness.get(st), dict) else {}
        shell = str(meta.get("beacon_skill") or "").strip()
        if shell and shell not in loads:
            return [shell, *loads]
        if st == "goal":
            return loads
        return loads
    return list(PROGRESSIVE_SKILLS.get(st, []))


def progressive_worktree_refs(stage: str) -> dict[str, Any]:
    """Always-on git worktree norms for progressive skill load (AC-WT-SKILL).

    ``goal`` is a facade entry (not a lifecycle stage). Callers that load
    ``beacon-goal`` should still request refs via stage="goal".
    """
    st = str(stage or "").strip().lower()
    if st not in WORKTREE_FLOW_STAGES:
        return {
            "schema": "git-worktree-execution-flow.v1",
            "required": False,
            "references": [],
            "examples": [],
            "bulk_history_forbidden": True,
        }
    refs = [WORKTREE_FLOW_REF]
    examples = [WORKTREE_EXAMPLE_REF] if st in ("goal", "implement", "discover", "loop") else []
    return {
        "schema": "git-worktree-execution-flow.v1",
        "required": True,
        "references": refs,
        "examples": examples,
        "bulk_history_forbidden": True,
    }


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
        skills = progressive_skills_for_stage(stage, utterance=utterance)
        item: dict[str, Any] = {
            "stage": stage,
            "skills": skills,
            "status": "planned",
            "loaded": False,
            **({"ux_gated": True} if stage == "design" else {}),
        }
        if stage == "plan":
            item["plan_subintent"] = plan_progressive_loads_for_utterance(
                utterance, brand="beacon"
            )
            # hoist plan_artifact for stage consumers
            pa = (item["plan_subintent"] or {}).get("plan_artifact")
            if isinstance(pa, dict):
                item["plan_artifact"] = pa
        # Lifecycle stages mount shared worktree norms (goal facade is separate).
        wt = progressive_worktree_refs(stage if stage != "design" else "plan")
        refs: list[str] = list(wt.get("references") or []) if wt.get("required") else []
        if stage == "design" and DESIGN_PHILOSOPHY_REF not in refs:
            refs.append(DESIGN_PHILOSOPHY_REF)
        if stage == "truth" and DOMAIN_FSM_TRUTH_REF not in refs:
            refs.append(DOMAIN_FSM_TRUTH_REF)
        if refs:
            item["references"] = refs
        if wt.get("required"):
            if stage == "implement":
                item["examples"] = list(wt.get("examples") or [WORKTREE_EXAMPLE_REF])
            item["worktree_flow"] = "git-worktree-execution-flow.v1"
        stages.append(item)
    # Public facade metadata for consumers (not a runnable lifecycle stage).
    stages[0]["public_entry_skill"] = PUBLIC_ENTRY
    stages[0]["public_entry_worktree_refs"] = progressive_worktree_refs("goal")
    if detect_parallel_intent(utterance) or (lakes and len(lakes) > 1):
        for item in stages:
            if item["stage"] == "implement":
                item["parallel"] = True
                item["worktree_mode"] = "main_star_satellite_pool"
    return stages


def utterance_requests_implement_delivery(utterance: str) -> bool:
    """Detect delivery/implement intent that must not bypass workspace admit."""
    text = str(utterance or "")
    low = text.lower()
    tokens = (
        "implement",
        "ralph",
        "coding",
        "write code",
        "实现",
        "交付",
        "写代码",
        "冻结并实现",
        "到交付",
        "implement到",
        "dev work",
    )
    if any(tok in text or tok in low for tok in tokens):
        return True
    # English bare "deliver" / "ship code"
    if "deliver" in low and ("code" in low or "feature" in low or "product" in low):
        return True
    return False



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
    _gv = resolve_goal_version(project_root, version, goal_mode="normal")
    resolved_version = str(_gv.get("version") or resolve_target_version(project_root, version))
    version_resolve_meta = _gv
    run_id = _new_run_id()
    parallel = build_parallel_plan(lakes=lakes, mode=worktree_mode, utterance=utterance)
    # harvest feature/package truth so ux_required frontmatter is honored
    truth_bits: list[str] = []
    try:
        resolved_for_truth = resolved_version
        if feature:
            tp = Path(project_root) / "docs" / "beacon" / resolved_for_truth / "features" / feature_slug(feature) / "truth.md"
            if tp.exists():
                truth_bits.append(tp.read_text(encoding="utf-8")[:12000])
        for lake in lakes or []:
            tp = Path(project_root) / "docs" / "beacon" / resolved_for_truth / "features" / feature_slug(lake) / "truth.md"
            if tp.exists():
                truth_bits.append(tp.read_text(encoding="utf-8")[:8000])
    except Exception:  # noqa: BLE001
        truth_bits = []
    truth_markdown = "\n".join(truth_bits)
    ux_required = detect_ux_intent(utterance, truth_markdown=truth_markdown, lakes=lakes)
    stages = build_stage_plan(
        utterance=utterance,
        lakes=lakes,
        truth_markdown=truth_markdown,
        ux_required=ux_required,
    )
    # P0: hoist plan_artifact; P1: host-subagent gate (no auto-spawn when off)
    _plan_item = next((s for s in stages if isinstance(s, dict) and s.get("stage") == "plan"), {})
    _plan_art = _plan_item.get("plan_artifact") if isinstance(_plan_item, dict) else None
    # Re-build plan artifact with lakes so journey seeds attach to multi-lake goals
    try:
        from beacon.utils.plan_artifact import build_plan_artifact as _build_pa
        from beacon.utils.plan_subintent import detect_plan_subintent as _det_psi

        _det = _det_psi(utterance)
        _plan_art = _build_pa(utterance, subintent_payload=_det, lakes=list(lakes or []))
        if isinstance(_plan_item, dict):
            _plan_item["plan_artifact"] = _plan_art
            if isinstance(_plan_item.get("plan_subintent"), dict):
                _plan_item["plan_subintent"]["plan_artifact"] = _plan_art
    except Exception:
        pass

    if not isinstance(_plan_art, dict):
        _ps = _plan_item.get("plan_subintent") if isinstance(_plan_item, dict) else None
        _plan_art = (_ps or {}).get("plan_artifact") if isinstance(_ps, dict) else {}
    if not isinstance(_plan_art, dict):
        _plan_art = {}
    _host_gate = evaluate_host_subagent_gate(utterance)
    default_done = ["domain_fsm", "evidence_chain", "continuous_qa"]
    if ux_required:
        default_done = ["design_baseline", "design_md_lint", "domain_fsm", "evidence_chain", "continuous_qa"]
    # ponytail: persistent goal — plan产持久目标，编排复刻 codex ThreadGoal 最小闭环
    _pg = (_plan_art.get("persistent_goal") if isinstance(_plan_art, dict) else {}) or {}
    _goal_objective = str(_pg.get("objective") or utterance or "").strip()
    _goal_status = str(_pg.get("status") or "active").strip() or "active"
    _goal_fingerprint = str(_pg.get("objective_fingerprint") or "").strip()
    if _goal_objective and not _goal_fingerprint:
        import hashlib as _hl
        _goal_fingerprint = _hl.sha256(_goal_objective.encode()).hexdigest()[:12]

    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "public_entry": PUBLIC_ENTRY,
        "status": "running",
        "blocked": False,
        "reason_code": "",
        "utterance": str(utterance or "").strip(),
        "goal_objective": _goal_objective,
        "goal_status": _goal_status,
        "goal_budget": _pg.get("token_budget"),
        "goal_fingerprint": _goal_fingerprint,
        "version": resolved_version,
        "version_resolve": version_resolve_meta,
        "feature": feature_slug(feature) if feature else "",
        "lakes": [feature_slug(x) for x in (lakes or []) if str(x).strip()],
        "done_when": done_when or default_done,
        "ux_required": ux_required,
        "stages": stages,
        "current_stage": stages[0]["stage"] if stages else "",
        "progressive_loaded_skills": [],
        "self_heal": {
            "pre": plan_goal_self_heal(phase="pre"),
            "mid_on_block": plan_goal_self_heal(phase="mid"),
            "post_release": plan_goal_self_heal(phase="post_release"),
        },
        "public_surface": {
            "scheme": "A",
            "whitelist": host_visible_whitelist("beacon"),
            "progressive_map": "skills/beacon/references/public-surface-progressive-map.v1.json",
        },
        "parallel_plan": parallel,
        "blocked_streak": 0,
        "heartbeat_interval_sec": DEFAULT_HEARTBEAT_INTERVAL_SEC,
        "last_heartbeat_at": "",
        "last_substep": "",
        "stall_flag": False,
        "supervisor": {
            "attached": False,
            "session_id": "",
            "state": "detached",
            "interval_sec": DEFAULT_HEARTBEAT_INTERVAL_SEC,
            "attached_at": "",
        },
        "implement_delegate": "",
        "verifier": {
            "required_for_complete": True,
            "present": False,
            "refs": [],
            "source": "",
        },
        "release_human_gate": True,
        "plan_artifact": _plan_art,
        "intent_decomposition": (_plan_art.get("intent_decomposition") if isinstance(_plan_art, dict) else {}),
        "journeys": (list(_plan_art.get("journeys") or []) if isinstance(_plan_art, dict) else []),

        "host_subagent": _host_gate,
        "stage_trace": {
            "schema": "goal-stage-trace.v1",
            "run_id": run_id,
            "log_relpath": f".beacon/state/product-goal/{run_id}/execution.jsonl",
            "per_stage": {
                (stages[0]["stage"] if stages else "plan"): {
                    "status": "active",
                    "trace_ref": f".beacon/state/product-goal/{run_id}/execution.jsonl",
                    "at": now_iso(),
                }
            },
        },
        "plan_to_truth_hint": plan_to_truth_gate(_plan_art) if _plan_art else plan_to_truth_gate(None),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "history": [{"event": "created", "at": now_iso()}],
        "completion_actor": "parent_goal",
        "open_closure_layers": [],
    }
    try:
        from beacon.utils.plan_goal_task_closure import (
            build_goal_task_closure_binding,
            version_requires_task_closure,
        )

        if version_requires_task_closure(resolved_version, feature):
            payload["task_closure"] = build_goal_task_closure_binding(
                run_id=run_id,
                version=resolved_version,
                feature=feature_slug(feature) if feature else "",
                lakes=[feature_slug(x) for x in (lakes or []) if str(x).strip()],
            )
    except Exception:  # noqa: BLE001
        pass

    # P0: delivery/implement intent → admit preflight at create (do not wait only for tick→ralph)
    try:
        wants_impl = utterance_requests_implement_delivery(str(utterance or ""))
        payload["implement_intent"] = wants_impl
        payload["discipline"] = {
            "must_tick_execute_for_ralph_dispatch": True,
            "must_not_edit_main_business_paths": True,
            "must_use_admitted_worktree_for_packages": True,
            "message": (
                "交付/实现类 goal：业务代码只允许在 admit worktree 写入；"
                "dispatch implement 须 `beacon goal tick --run-id <id> --execute`；"
                "禁止在 main 上直接改 packages/** 或 beacon/**。"
            ),
        }
        if wants_impl:
            has_target = bool(payload.get("feature") or payload.get("lakes"))
            if has_target:
                pre = ensure_goal_implement_admission(project_root, payload)
                payload = apply_admission_to_goal_payload(payload, pre)
                payload["implement_admission_preflight"] = {
                    "allow_implement": pre.get("allow_implement"),
                    "reason_code": pre.get("reason_code"),
                    "worktree_path": pre.get("worktree_path") or (pre.get("admission") or {}).get("worktree_path"),
                    "branch": pre.get("branch") or (pre.get("admission") or {}).get("branch"),
                    "goal_forced_worktree": pre.get("goal_forced_worktree"),
                    "at": now_iso(),
                }
                payload["recommended_implement_cwd"] = payload["implement_admission_preflight"].get("worktree_path") or ""
                hist = list(payload.get("history") or [])
                hist.append(
                    {
                        "event": "implement_admission_preflight",
                        "allow_implement": pre.get("allow_implement"),
                        "reason_code": pre.get("reason_code"),
                        "worktree_path": payload.get("recommended_implement_cwd"),
                        "at": now_iso(),
                    }
                )
                payload["history"] = hist
                if not pre.get("allow_implement"):
                    # Soft-block: do not prevent plan/truth; surface for operators/agents
                    payload["admission_preflight_blocked"] = True
                    payload["reason_code"] = str(
                        pre.get("reason_code") or "goal_implement_admission_preflight_blocked"
                    )
            else:
                payload["admission_preflight_warning"] = (
                    "implement/交付意图已识别，但缺少 --feature 或 lakes；"
                    "进入 implement 前必须提供 feature slug 并 workspace admit。"
                )
                hist = list(payload.get("history") or [])
                hist.append(
                    {
                        "event": "implement_admission_preflight_skipped",
                        "reason_code": "feature_required_for_admit",
                        "at": now_iso(),
                    }
                )
                payload["history"] = hist
    except Exception as exc:  # noqa: BLE001
        payload["admission_preflight_error"] = str(exc)[:240]

    # Multi-version / dual-track intent (e.g. v1.6.8\v2.0.0)
    try:
        payload = apply_multi_version_to_goal_payload(project_root, payload, str(utterance or ""))
        mv = payload.get("multi_version") or {}
        if mv.get("enabled"):
            payload.setdefault("history", []).append(
                {
                    "event": "multi_version_plan",
                    "versions": mv.get("versions"),
                    "parallel": mv.get("parallel"),
                    "at": now_iso(),
                }
            )
    except Exception:  # noqa: BLE001
        pass

    path = goal_state_path(project_root, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, payload)
    try:
        # ensure run dir + seed execution log (stage_trace)
        goal_run_dir(project_root, run_id).mkdir(parents=True, exist_ok=True)
        log_path = execution_log_path(project_root, run_id)
        try:
            log_rel = str(log_path.resolve().relative_to(Path(project_root).resolve()))
        except ValueError:
            log_rel = str(log_path)
        payload["stage_trace"]["log_relpath"] = log_rel
        for st in payload.get("stage_trace", {}).get("per_stage", {}).values():
            if isinstance(st, dict):
                st["trace_ref"] = log_rel
        append_execution_log(
            project_root,
            run_id,
            stage=str(payload.get("current_stage") or "plan"),
            event="created",
            summary=(
                f"goal created host_subagent={bool(_host_gate.get('gate_on'))} "
                f"plan_track={(_plan_art or {}).get('methodology_track', '')}"
            )[:240],
            refs=[log_rel],
        )
        write_json(path, payload)
    except Exception:  # noqa: BLE001
        pass
    try:
        payload["state_path"] = str(path.relative_to(project_root))
    except ValueError:
        payload["state_path"] = str(path)
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


def _goal_program_slug(project_root: Path, payload: dict[str, Any]) -> str:
    explicit = str(payload.get("program_slug") or "").strip()
    if explicit:
        return explicit
    feature = str(payload.get("feature") or "").strip()
    if not feature:
        return ""
    topo = resolve_program_lake_topology(project_root, version=str(payload.get("version") or "auto"), feature=feature)
    return str(topo.get("program_slug") or "").strip()


def _program_binding_diagnostics(root: Path, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Why did program binding fail? Add-only diagnostics for unbound goal payloads.

    Returns None when there is nothing meaningful to diagnose (no feature bound to
    the run, or no programs/ directory for the resolved version).
    """
    from beacon.utils.program_admission import (
        _is_program_frozen,
        _lake_rows,
        _read_frontmatter,
        _read_json,
    )
    from beacon.utils.program_graph import load_feature_graph

    feature = feature_slug(str(payload.get("feature") or ""))
    if not feature:
        return None
    try:
        resolved_version = resolve_target_version(root, str(payload.get("version") or "auto"))
    except Exception:  # noqa: BLE001
        return None
    programs_root = root / "docs" / "beacon" / resolved_version / "programs"
    if not programs_root.is_dir():
        return None
    checked: list[dict[str, Any]] = []
    for program_dir in sorted(path for path in programs_root.iterdir() if path.is_dir()):
        graph, errors = load_feature_graph(program_dir / "feature-graph.json")
        entry: dict[str, Any] = {"program": program_dir.name, "graph_valid": bool(graph) and not errors}
        if errors:
            entry["errors"] = errors
        lakes = _lake_rows(graph) if isinstance(graph, dict) else []
        entry["feature_in_graph"] = any(
            feature in {str(row.get("slug") or ""), str(row.get("feature_slug") or "")} for row in lakes
        )
        if isinstance(graph, dict):
            entry["frozen"] = _is_program_frozen(
                manifest=_read_frontmatter(program_dir / "program-manifest.md"),
                graph=graph,
                freeze=_read_json(program_dir / "program-truth-freeze.json"),
            )
        checked.append(entry)
    matched = [entry for entry in checked if entry.get("feature_in_graph")]
    if matched:
        reason_code = "program_not_frozen"
        hint = (
            "program plan is not frozen; freeze it first "
            "(program-truth-freeze.json status=frozen or graph/manifest program_plan_frozen=true)"
        )
    elif any(not entry.get("graph_valid") for entry in checked):
        reason_code = "graph_invalid"
        hint = "fix feature-graph.json validation errors (see checked[].errors)"
    else:
        reason_code = "feature_not_in_graph"
        hint = (
            f"add a lakes[] row containing '{feature}' to "
            f"docs/beacon/{resolved_version}/programs/<slug>/feature-graph.json"
        )
    return {
        "status": "unbound",
        "reason_code": reason_code,
        "feature": feature,
        "checked": checked,
        "hint": hint,
    }


def sync_program_orchestrator_route(
    project_root: Path,
    payload: dict[str, Any],
    *,
    persist_run_state: bool = True,
) -> dict[str, Any]:
    """Attach program orchestrator state to goal payload when run belongs to a program."""
    root = Path(project_root).expanduser().resolve()
    out = dict(payload)
    program_slug = _goal_program_slug(root, out)
    if not program_slug:
        binding = _program_binding_diagnostics(root, out)
        if binding is not None:
            out["program_binding"] = binding
        return out
    state = build_program_orchestrator_state(
        root,
        version=str(out.get("version") or "auto"),
        program_slug=program_slug,
    )
    out["program_slug"] = str(state.get("program_slug") or program_slug)
    out["program_binding"] = {"status": "bound", "program_slug": out["program_slug"]}
    out["program_orchestrator"] = state
    out["resume_action"] = str(state.get("resume_action") or out.get("resume_action") or "")
    out["next_action"] = str(state.get("next_action") or out.get("next_action") or "")
    out["next_action_target"] = str(state.get("next_action_target") or out.get("next_action_target") or "")
    out["next_action_source"] = str(state.get("next_action_source") or out.get("next_action_source") or "")
    out["recommended_command"] = str(state.get("recommended_command") or out.get("recommended_command") or "")
    if str(state.get("current_lake") or "").strip():
        out["current_lake"] = str(state.get("current_lake") or "")
    if persist_run_state and state.get("program_slug") and state.get("version"):
        write_program_orchestrator_state(root, state)
    return out


def goal_continue_run(
    project_root: Path,
    run_id: str,
    *,
    execute: bool = False,
    note: str = "",
) -> dict[str, Any]:
    """Continue goal by refreshing program route then ticking one step."""
    root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    payload = sync_program_orchestrator_route(root, payload, persist_run_state=True)
    payload = _save(root, payload)
    cont_note = note or "continue_with_program_orchestrator"
    return tick_goal_run(root, run_id, note=cont_note, execute=execute)


def _save(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    run_id = str(payload.get("run_id") or "")
    payload["updated_at"] = now_iso()
    root = Path(project_root).expanduser().resolve()
    path = goal_state_path(root, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, payload)
    try:
        payload["state_path"] = str(path.resolve().relative_to(root))
    except ValueError:
        payload["state_path"] = str(path)
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


def tick_goal_run(
    project_root: Path,
    run_id: str,
    *,
    note: str = "",
    execute: bool = False,
) -> dict[str, Any]:
    """Advance one stage; with execute=True may plan/dispatch stage workers (no self-cert)."""
    project_root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    payload = sync_program_orchestrator_route(project_root, payload, persist_run_state=True)
    stages = payload.get("stages") if isinstance(payload.get("stages"), list) else []
    current = str(payload.get("current_stage") or "")
    idx = next((i for i, s in enumerate(stages) if isinstance(s, dict) and s.get("stage") == current), 0)

    worker_plan = None
    if execute:
        worker_plan = plan_tick_execute(payload)
        payload["last_tick_execute"] = worker_plan
        append_execution_log(
            project_root,
            run_id,
            stage=current,
            event="tick",
            summary=f"tick --execute dispatch={worker_plan.get('dispatch')}",
            cmd=str(worker_plan.get("command") or ""),
        )
        # Soft dispatch hooks (do not claim QA/release)
        if worker_plan.get("dispatch") == "ralph":
            # UD-GIA: hard gate — workspace admit (+ pool / merge-main) before implement write path
            gate = ensure_goal_implement_admission(project_root, payload)
            payload = apply_admission_to_goal_payload(payload, gate)
            append_execution_log(
                project_root,
                run_id,
                stage="implement",
                event="implement_admission",
                summary=(
                    f"allow={gate.get('allow_implement')} reason={gate.get('reason_code')} "
                    f"forced={gate.get('goal_forced_worktree')}"
                )[:240],
                refs=[str(gate.get("worktree_path") or "")],
            )
            if not gate.get("allow_implement"):
                payload["blocked"] = True
                payload["status"] = "blocked"
                payload["reason_code"] = str(gate.get("reason_code") or "goal_implement_admission_blocked")
                hist = list(payload.get("history") or [])
                hist.append(
                    {
                        "event": "implement_admission_blocked",
                        "reason_code": payload["reason_code"],
                        "at": now_iso(),
                    }
                )
                payload["history"] = hist
                return _save(project_root, payload)
            _save(project_root, payload)
            payload = delegate_implement_to_ralph(
                project_root, run_id, feature=str(gate.get("feature_slug") or payload.get("feature") or "")
            )
            payload = load_goal_run(project_root, run_id)
            # re-attach gate if reload dropped it
            if not payload.get("implement_admission"):
                payload = apply_admission_to_goal_payload(payload, gate)
                payload = _save(project_root, payload)
        elif worker_plan.get("dispatch") == "design":
            try:
                payload = run_design_stage_for_goal(project_root, run_id)
            except Exception as exc:  # noqa: BLE001
                payload = record_blocker(project_root, run_id, reason_code=f"design_stage_error:{exc}")
                return payload
        elif worker_plan.get("dispatch") == "none" and worker_plan.get("action") == "human_release_gate":
            # never auto-confirm release
            append_execution_log(
                project_root,
                run_id,
                stage="release",
                event="blocker",
                summary="release requires human confirmation; tick --execute does not auto-release",
            )
        # qa dispatch is planned only here (caller/CLI may run beacon qa); do not fake scorecards
    else:
        append_execution_log(
            project_root,
            run_id,
            stage=current,
            event="tick",
            summary=f"tick record-only note={str(note)[:80]}",
        )

    # Hard stage-exit gates (fill-then-pass). Do not mark done or advance when blocked.
    exit_gate = evaluate_stage_exit(project_root, payload, stage=current)
    append_execution_log(
        project_root,
        run_id,
        stage=current or "unknown",
        event="stage_exit_gate",
        summary=f"allow={exit_gate.get('allow')} reason={exit_gate.get('reason_code')}"[:240],
    )
    if exit_gate.get("blocked") or not exit_gate.get("allow", True):
        payload = apply_stage_exit_block(payload, exit_gate)
        payload["stages"] = stages
        return _save(project_root, payload)

    if idx < len(stages) and isinstance(stages[idx], dict):
        stages[idx]["status"] = "done"
        stages[idx]["loaded"] = True
        stages[idx]["stage_exit_gate"] = exit_gate
        for skill in stages[idx].get("skills") or []:
            loaded = list(payload.get("progressive_loaded_skills") or [])
            if skill not in loaded:
                loaded.append(skill)
            payload["progressive_loaded_skills"] = loaded
    next_idx = idx + 1
    if next_idx < len(stages) and isinstance(stages[next_idx], dict):
        next_stage = str(stages[next_idx]["stage"])
        # Retain plan→truth diagnostics (now hard-gated above via evaluate_stage_exit)
        hint_local: dict[str, Any] | None = None
        if current == "plan" and next_stage == "truth":
            art = payload.get("plan_artifact") if isinstance(payload.get("plan_artifact"), dict) else {}
            if not art:
                for s in stages:
                    if isinstance(s, dict) and s.get("stage") == "plan":
                        art = s.get("plan_artifact") if isinstance(s.get("plan_artifact"), dict) else {}
                        if not art:
                            ps = s.get("plan_subintent") if isinstance(s.get("plan_subintent"), dict) else {}
                            art = ps.get("plan_artifact") if isinstance(ps.get("plan_artifact"), dict) else {}
                        break
            hint_local = plan_to_truth_gate(art if art else None)
            append_execution_log(
                project_root,
                run_id,
                stage="plan",
                event="plan_to_truth_hint",
                summary=str((hint_local or {}).get("reason_code") or "")[:240],
            )
            # v1.6.11: attach truth-fill readiness advisory when leaving plan
            try:
                from beacon.utils.plan_goal_task_closure import version_requires_task_closure

                ver = str(payload.get("version") or "")
                feat = str(payload.get("feature") or "")
                if version_requires_task_closure(ver, feat):
                    from beacon.utils.plan_goal_task_closure import (
                        build_context_envelope,
                        build_truth_fill_request,
                    )
                    from beacon.utils.feature_package import package_paths
                    from beacon.utils.truth_map import FEATURE_SURFACES, _sha256

                    resolved = ver
                    paths = package_paths(project_root, version=resolved, feature=feat) if feat else None
                    source_hashes = {}
                    if paths:
                        source_hashes = {
                            s: (_sha256(paths[s]) if paths[s].exists() else "pending")
                            for s in FEATURE_SURFACES
                        }
                    else:
                        source_hashes = {s: "pending" for s in FEATURE_SURFACES}
                    # pending hashes are placeholders until scaffold exists
                    if all(v != "pending" for v in source_hashes.values()):
                        env = build_context_envelope(
                            utterance=str(payload.get("utterance") or ""),
                            version=resolved,
                            baseline_commit=str((payload.get("version_resolve") or {}).get("requested") or "main"),
                            truth_refs={"truth": f"docs/beacon/{resolved}/features/{feat}/truth.md"} if feat else {"truth": "pending"},
                            code_entries=["beacon/utils/plan_goal_task_closure.py"],
                            test_entries=["tests/test_v1611_plan_goal_task_closure.py"],
                            change_history=[f"docs/beacon/{resolved}/change"],
                            inherited_contracts=["truth-core-authority-v1610"],
                            execution_authorities={
                                "subagent_runtime": "host_or_fallback",
                                "truth_canonical": "main",
                                "worktree_governance": "workspace_admit",
                                "trace_authority": "agent_trace.v1",
                            },
                            source_hashes=source_hashes,
                            semantic_compiler_refs=["beacon/utils/intent_first.py"],
                            host_transport={"capability": "host-response", "precedence": ["host", "cli"]},
                            program_refs={"program": "beacon-plan-goal-task-closure-v1611"},
                            pac_refs=["PAC-016", "PAC-017", "PAC-021"],
                        )
                        req = build_truth_fill_request(env)
                        payload["truth_fill_readiness"] = {
                            "schema": "truth-fill-readiness.v1",
                            "envelope": env,
                            "fill_request": req,
                            "next": "beacon truth fill-request" if req.get("pass") else "beacon truth init + fill-request",
                        }
                    else:
                        payload["truth_fill_readiness"] = {
                            "schema": "truth-fill-readiness.v1",
                            "status": "scaffold_pending",
                            "next": "beacon truth init -f <feature> -v v1.6.11 && beacon truth fill-request ...",
                        }
            except Exception as exc:  # noqa: BLE001
                payload["truth_fill_readiness"] = {
                    "schema": "truth-fill-readiness.v1",
                    "status": "error",
                    "error": str(exc)[:200],
                }
        # stage_trace per-stage refs (before skill load so we can re-apply after)
        st = payload.get("stage_trace") if isinstance(payload.get("stage_trace"), dict) else {}
        if not st:
            st = {"schema": "goal-stage-trace.v1", "run_id": run_id, "per_stage": {}}
        per = dict(st.get("per_stage") if isinstance(st.get("per_stage"), dict) else {})
        try:
            log_rel = str(
                execution_log_path(project_root, run_id).resolve().relative_to(Path(project_root).resolve())
            )
        except ValueError:
            log_rel = str(execution_log_path(project_root, run_id))
        st["log_relpath"] = log_rel
        if current:
            per[current] = {"status": "done", "trace_ref": log_rel, "at": now_iso()}
        per[next_stage] = {"status": "active", "trace_ref": log_rel, "at": now_iso()}
        st["per_stage"] = per
        if isinstance(stages[next_idx], dict):
            stages[next_idx]["trace_ref"] = log_rel

        payload["current_stage"] = next_stage
        payload["status"] = "running"
        if hint_local is not None:
            payload["plan_to_truth_hint"] = hint_local
        payload["stage_trace"] = st
        # persist hint/trace before load_stage_skills (which reloads from disk)
        _save(project_root, payload)

        payload = load_stage_skills(project_root, run_id, next_stage)
        payload = load_goal_run(project_root, run_id)
        if hint_local is not None:
            payload["plan_to_truth_hint"] = hint_local
        # merge stage_trace
        existing = payload.get("stage_trace") if isinstance(payload.get("stage_trace"), dict) else {}
        ep = existing.get("per_stage") if isinstance(existing.get("per_stage"), dict) else {}
        ep.update(per)
        existing["schema"] = existing.get("schema") or "goal-stage-trace.v1"
        existing["run_id"] = existing.get("run_id") or run_id
        existing["per_stage"] = ep
        existing["log_relpath"] = log_rel
        payload["stage_trace"] = existing
        if next_stage == "implement":
            # v1.6.11: seed path progress ledger snapshot (empty open set until tasks compile)
            try:
                from beacon.utils.plan_goal_task_closure import (
                    aggregate_path_progress,
                    version_requires_task_closure,
                )

                if version_requires_task_closure(str(payload.get("version") or ""), str(payload.get("feature") or "")):
                    nodes = list((payload.get("task_graph") or {}).get("nodes") or [])
                    payload["task_progress"] = aggregate_path_progress(nodes)
                    payload["task_progress"]["schema"] = "task-progress-ledger.v1"
                    payload["task_progress"]["revision"] = str(
                        ((payload.get("task_closure") or {}).get("revision_id") if isinstance(payload.get("task_closure"), dict) else "")
                        or "R2"
                    )
            except Exception:  # noqa: BLE001
                pass
            # Pre-warm implement admission (fail-closed only blocks write dispatch; record attempt)
            pre = ensure_goal_implement_admission(project_root, payload)
            payload = apply_admission_to_goal_payload(payload, pre)
            append_execution_log(
                project_root,
                run_id,
                stage="implement",
                event="implement_admission_prewarm",
                summary=f"allow={pre.get('allow_implement')} reason={pre.get('reason_code')}"[:240],
                refs=[str(pre.get("worktree_path") or "")],
            )
            if not pre.get("allow_implement"):
                payload["blocked"] = True
                payload["status"] = "blocked"
                payload["reason_code"] = str(pre.get("reason_code") or "goal_implement_admission_blocked")
        if next_stage == "design":
            payload = run_design_stage_for_goal(project_root, run_id)
    else:
        payload["status"] = "awaiting_verifier"
        payload["current_stage"] = "complete_gate"
    hist = list(payload.get("history") or [])
    hist.append({"event": "tick", "note": note, "execute": bool(execute), "at": now_iso()})
    payload["history"] = hist
    payload["stages"] = stages
    if worker_plan is not None:
        payload["last_tick_execute"] = worker_plan
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
    # keep task_closure verifier binding current
    try:
        tc = payload.get("task_closure") if isinstance(payload.get("task_closure"), dict) else None
        if tc is not None:
            tc = dict(tc)
            tc["verifier_ref"] = f".beacon/state/product-goal/{run_id}.json#verifier"
            payload["task_closure"] = tc
    except Exception:  # noqa: BLE001
        pass
    return _save(project_root, payload)


def _qa_stage_passed(payload: dict[str, Any]) -> bool:
    for item in payload.get("stages") or []:
        if isinstance(item, dict) and item.get("stage") == "qa":
            return str(item.get("status") or "").strip().lower() in {"done", "pass", "passed", "ok", "completed"}
    return False


def _goal_qa_evidence_refs(root: Path, version: str, slug: str) -> list[str]:
    """Real on-disk QA evidence paths (same candidates as the qa stage-exit gate)."""
    base = root / "docs" / "beacon" / version
    candidates = [
        base / "features" / slug / "evidence.md",
        base / "qa" / f"{slug}-scorecard.md",
        base / "qa" / f"{slug}-ac-closure.md",
        root / ".beacon" / "evidence" / "qa" / version / slug / "scorecard.json",
        base / "qa" / "smoke-evidence.md",
    ]
    refs: list[str] = []
    for path in candidates:
        if path.is_file():
            try:
                refs.append(str(path.relative_to(root)))
            except ValueError:
                refs.append(str(path))
    return refs


def _backfill_closure_artifacts(project_root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Materialize missing .machine execution closure markers citing real evidence only.

    Never fabricates: every written ref comes from verifier refs, existing QA evidence
    files, or a stage artifact path; otherwise the backfill is skipped with a history event.
    """
    root = Path(project_root).expanduser().resolve()
    events: list[dict[str, Any]] = []
    slug = feature_slug(str(payload.get("feature") or ""))
    if not slug:
        return events
    version = str(payload.get("version") or "")
    run_id = str(payload.get("run_id") or "")
    exec_dir = root / "docs" / "beacon" / version / ".machine" / "execution"
    verifier_refs = [
        str(ref).strip()
        for ref in ((payload.get("verifier") or {}).get("refs") or [])
        if str(ref).strip()
    ]

    impl_path = exec_dir / f"implementation-summary-{slug}.json"
    if not impl_path.exists():
        if verifier_refs:
            body = {
                "schema_version": "1.0",
                "feature": slug,
                "status": "passed",
                "run_id": run_id,
                "generated_by": "goal_complete_closure_backfill",
                "verifier_refs": verifier_refs,
                "evidence_refs": verifier_refs,
                "created_at": now_iso(),
            }
            impl_path.parent.mkdir(parents=True, exist_ok=True)
            impl_path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            events.append(
                {
                    "event": "closure_backfilled",
                    "kind": "implementation_summary",
                    "artifact": str(impl_path.relative_to(root)),
                    "at": now_iso(),
                }
            )
        else:
            events.append(
                {
                    "event": "closure_backfill_skipped",
                    "kind": "implementation_summary",
                    "reason_code": "no_verifier_refs",
                    "at": now_iso(),
                }
            )

    if not _qa_stage_passed(payload):
        return events
    qa_path = exec_dir / f"qa-acceptance-{slug}.json"
    if qa_path.exists():
        return events
    artifact_ref = ""
    for item in payload.get("stages") or []:
        if isinstance(item, dict) and item.get("stage") == "qa":
            value = item.get("artifact")
            if isinstance(value, str) and value.strip():
                artifact_ref = value.strip()
    evidence_refs = ([artifact_ref] if artifact_ref else []) + _goal_qa_evidence_refs(root, version, slug) + verifier_refs
    if not evidence_refs:
        events.append(
            {
                "event": "closure_backfill_skipped",
                "kind": "qa_acceptance",
                "reason_code": "no_qa_evidence_refs",
                "at": now_iso(),
            }
        )
        return events
    body = {
        "schema_version": "1.0",
        "feature": slug,
        "status": "passed",
        "verdict": "passed",
        "run_id": run_id,
        "generated_by": "goal_complete_closure_backfill",
        "scorecard_ref": evidence_refs[0],
        "evidence_refs": evidence_refs,
        "created_at": now_iso(),
    }
    qa_path.parent.mkdir(parents=True, exist_ok=True)
    qa_path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    events.append(
        {
            "event": "closure_backfilled",
            "kind": "qa_acceptance",
            "artifact": str(qa_path.relative_to(root)),
            "at": now_iso(),
        }
    )
    return events


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
    # v1.6.11+: task-closure / parent-only / lifecycle gate (still not auto-release)
    if not force:
        try:
            from beacon.utils.plan_goal_task_closure import evaluate_goal_run_closure_gate

            closure = evaluate_goal_run_closure_gate(payload)
            payload["task_closure_gate"] = closure
            if closure.get("blocked"):
                payload["status"] = "blocked"
                payload["blocked"] = True
                payload["reason_code"] = str(closure.get("reason_code") or "goal_run_closure_blocked")
                hist = list(payload.get("history") or [])
                hist.append(
                    {
                        "event": "complete_rejected",
                        "reason_code": payload["reason_code"],
                        "at": now_iso(),
                        "gate": "task_closure",
                    }
                )
                payload["history"] = hist
                return _save(project_root, payload)
        except Exception as exc:  # noqa: BLE001
            payload["task_closure_gate"] = {
                "status": "error",
                "blocked": False,
                "reason_code": "task_closure_gate_error",
                "error": str(exc)[:240],
            }
    payload["status"] = "completed"
    payload["blocked"] = False
    payload["reason_code"] = ""
    payload["completed_at"] = now_iso()
    hist = list(payload.get("history") or [])
    hist.append({"event": "completed", "at": now_iso(), "force": force})
    try:
        hist.extend(_backfill_closure_artifacts(project_root, payload))
    except Exception:  # noqa: BLE001
        pass
    payload["history"] = hist
    return _save(project_root, payload)


def attach_program_takeover_hint(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """R5 (v1.6.12): prompt-level hint to continue with the next program lake.

    Attached only when the program orchestrator route shows a pending next lake.
    Prompt-level only — goal never auto-spawns the program driver.
    """
    route = payload.get("program_orchestrator") if isinstance(payload.get("program_orchestrator"), dict) else {}
    next_lake = str(route.get("next_lake") or "").strip()
    if not next_lake or str(route.get("sea_completion_status") or "") == "all_lakes_complete":
        return payload
    slug = str(route.get("program_slug") or payload.get("program_slug") or "").strip()
    if not slug:
        return payload
    version = str(route.get("version") or payload.get("version") or "")
    command = f"beacon program drive {slug} --project-root {project_root} --version {version}"
    payload["program_takeover"] = {
        "schema_version": "1.0",
        "program_slug": slug,
        "next_lake": next_lake,
        "resume_action": str(route.get("resume_action") or ""),
        "command": command,
        "note": "prompt-level hint only; goal does not auto-spawn the program driver",
    }
    recommended = payload.get("recommended_next")
    if isinstance(recommended, dict):
        recommended.setdefault("program", f"{command}  # continue with next lake {next_lake}")
    hist = list(payload.get("history") or [])
    hist.append({"event": "program_takeover_hint", "program_slug": slug, "next_lake": next_lake, "at": now_iso()})
    payload["history"] = hist
    return payload


def run_goal_facade(
    project_root: Path,
    *,
    utterance: str,
    version: str = "auto",
    feature: str = "",
    lakes: list[str] | None = None,
    worktree_mode: WorktreeMode | None = None,
    auto_tick: bool = False,
    longrun: bool = False,
    driver_start: bool = True,
    driver_run_loop: bool = False,
    max_driver_turns: int | None = None,
    bridge_cmd: str | None = None,
    spawn_fn=None,
) -> dict[str, Any]:
    """Public facade: create goal run and optionally advance planning stages.

    longrun CLI default False means "do not force on"; project goal.longrun_default
    (default true for new projects) is honored without env gates. Explicit CLI/env opt-out wins.
    """
    # v1.6.8 UD-FC-002 / UD-V168-001: honor project longrun_default without env gate.
    # Priority: explicit CLI flag > utterance intent > project goal.longrun_default > False.
    # BEACON_GOAL_FORCE_LONGRUN / BEACON_GOAL_FORCE_NO_LONGRUN remain optional overrides only.
    try:
        import os

        force_on = str(os.environ.get("BEACON_GOAL_FORCE_LONGRUN", "")).strip().lower() in {"1", "true", "yes"}
        force_off = str(os.environ.get("BEACON_GOAL_FORCE_NO_LONGRUN", "")).strip().lower() in {"1", "true", "yes"}
        if force_off:
            effective_longrun = False
            longrun_source = "env_force_off"
        elif force_on:
            effective_longrun = True
            longrun_source = "env_force_on"
        elif longrun:
            effective_longrun = True
            longrun_source = "cli_flag"
        elif detect_longrun_intent(utterance):
            effective_longrun = True
            longrun_source = "utterance_intent"
        else:
            from beacon.utils.prod_ops_v168 import resolve_longrun_enabled

            _lr = resolve_longrun_enabled(project_root, cli_longrun=None)
            effective_longrun = bool(_lr.get("enabled"))
            longrun_source = str(_lr.get("source") or "project_default")
    except Exception:  # noqa: BLE001
        effective_longrun = bool(longrun) or detect_longrun_intent(utterance)
        longrun_source = "legacy"
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
        # advance plan only when journey decomposition allows; never skip ocean freeze;
        # never self-claim qa/release
        for _ in range(2):
            cur = str(payload.get("current_stage") or "")
            if cur == "plan":
                art = payload.get("plan_artifact") if isinstance(payload.get("plan_artifact"), dict) else {}
                hint = plan_to_truth_gate(art if art else None)
                payload["plan_to_truth_hint"] = hint
                if hint.get("blocks_auto_tick_past_plan") or hint.get("blocked"):
                    append_execution_log(
                        project_root,
                        payload["run_id"],
                        stage="plan",
                        event="auto_tick_blocked",
                        summary=str(hint.get("reason_code") or "auto_tick_blocked")[:240],
                    )
                    payload["status"] = "running"
                    payload["reason_code"] = str(hint.get("reason_code") or "plan_journey_decomposition_incomplete")
                    payload = _save(project_root, payload)
                    break
            payload = tick_goal_run(project_root, payload["run_id"], note="auto_tick_facade")
            payload = load_goal_run(project_root, payload["run_id"])
    payload["longrun"] = False
    payload["longrun_source"] = longrun_source
    payload["driver"] = {"state": "idle", "longrun": False}
    if effective_longrun:
        payload = attach_longrun_to_goal_run(
            project_root,
            payload,
            start_driver=driver_start,
            run_loop=driver_run_loop,
            max_loop_turns=max_driver_turns,
            spawn_fn=spawn_fn,
            bridge_cmd=bridge_cmd,
        )
        payload["longrun"] = True
    payload = sync_program_orchestrator_route(project_root, payload, persist_run_state=True)
    payload["entry_contract"] = public_entry_contract()
    payload["recommended_next"] = {
        "human": "continue via $beacon-goal or beacon goal tick/resume",
        "longrun": 'beacon goal run "..." --longrun  # auto requeue host turns',
        "complete": "requires verifier refs (beacon-eval-qa evidence), then beacon goal complete",
        "release": "human gate via beacon-eval-release",
    }
    payload = attach_program_takeover_hint(project_root, payload)
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


# --- Durable supervisor public API (v1.6.7) ---


def goal_heartbeat(
    project_root: Path,
    run_id: str,
    *,
    summary: str,
    substep: str = "",
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    payload = record_heartbeat_on_payload(payload, summary=summary, substep=substep)
    append_execution_log(
        project_root,
        run_id,
        stage=str(payload.get("current_stage") or ""),
        event="heartbeat",
        summary=summary,
        substep=substep,
    )
    return _save(project_root, payload)


def goal_checkpoint(
    project_root: Path,
    run_id: str,
    *,
    next_action: str,
    substep: str = "",
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    if substep:
        payload["last_substep"] = substep
    recent = []
    # heartbeats from history
    for h in reversed(list(payload.get("history") or [])):
        if isinstance(h, dict) and h.get("event") == "heartbeat":
            recent.append({"ts": str(h.get("at") or ""), "summary": str(h.get("summary") or "")})
        if len(recent) >= 5:
            break
    recent.reverse()
    blockers = []
    if payload.get("reason_code"):
        blockers.append({"reason_code": str(payload.get("reason_code")), "summary": str(payload.get("reason_code"))})
    pack = write_checkpoint(
        project_root,
        run_id,
        stage=str(payload.get("current_stage") or ""),
        last_substep=str(payload.get("last_substep") or substep or ""),
        next_action=next_action,
        open_blockers=blockers,
        last_heartbeat_at=str(payload.get("last_heartbeat_at") or ""),
        recent_heartbeats=recent,
    )
    payload["checkpoint"] = pack
    hist = list(payload.get("history") or [])
    hist.append({"event": "checkpoint", "next_action": next_action[:240], "at": now_iso()})
    payload["history"] = hist
    return _save(project_root, payload)


def goal_resume_pack(project_root: Path, run_id: str) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    # if stalled, mark interrupted for resume semantics
    if detect_stall(payload) and payload.get("reason_code") != DGS_HOST_INTERRUPTED:
        payload = mark_host_interrupted(payload)
        payload = _save(project_root, payload)
        append_execution_log(
            project_root,
            run_id,
            stage=str(payload.get("current_stage") or ""),
            event="host_interrupt",
            summary="resume-pack detected stall",
            substep=str(payload.get("last_substep") or ""),
        )
    pack = build_resume_pack(project_root, payload)
    return {
        "status": "ok",
        "run_id": run_id,
        "resume_pack": pack,
        "payload_status": payload.get("status"),
        "reason_code": payload.get("reason_code"),
        "authority_note": pack.get("authority_note"),
    }


def goal_supervise_attach(
    project_root: Path,
    run_id: str,
    *,
    interval_sec: int | None = None,
    once: bool = False,
) -> dict[str, Any]:
    """Opt-in supervisor attach (+ optional single poll). Never called from goal run."""
    project_root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    payload = dgs_attach_supervisor(payload, interval_sec=interval_sec)
    payload = _save(project_root, payload)
    append_execution_log(
        project_root,
        run_id,
        stage=str(payload.get("current_stage") or ""),
        event="supervise_attach",
        summary=f"supervisor attached interval={payload.get('heartbeat_interval_sec')}",
    )
    result: dict[str, Any] = {
        "status": "active",
        "run_id": run_id,
        "supervisor": payload.get("supervisor"),
        "opt_in": True,
        "auto_on_goal_run": False,
    }
    if once:
        poll = dgs_supervise_once(project_root, payload)
        if isinstance(poll.get("payload"), dict):
            payload = _save(project_root, poll["payload"])
        result["poll"] = {k: v for k, v in poll.items() if k != "payload"}
        result["payload"] = payload
    else:
        result["payload"] = payload
        result["note"] = "call again with --once or loop externally; not a system daemon by default"
    return result


def goal_supervise_detach(project_root: Path, run_id: str) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    payload = dgs_detach_supervisor(payload)
    payload = _save(project_root, payload)
    append_execution_log(
        project_root,
        run_id,
        stage=str(payload.get("current_stage") or ""),
        event="supervise_detach",
        summary="supervisor detached",
    )
    return {"status": "stopped", "run_id": run_id, "supervisor": payload.get("supervisor"), "payload": payload}


def goal_memory_reindex(project_root: Path, run_id: str) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    return memory_reindex(project_root, run_id)


def goal_memory_search(project_root: Path, run_id: str, query: str, *, limit: int = 10) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    payload = load_goal_run(project_root, run_id)
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    result = memory_search(project_root, run_id, query, limit=limit)
    result["can_complete"] = False
    result["authority"] = "support_advisory"
    return result


def enrich_goal_status(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Add stall / supervisor fields for status command."""
    project_root = Path(project_root).expanduser().resolve()
    if payload.get("reason_code") == REASON_NOT_FOUND:
        return payload
    out = dict(payload)
    stalled = detect_stall(out)
    out["stall_detected"] = stalled
    if stalled and out.get("reason_code") not in {DGS_HOST_INTERRUPTED, REASON_BLOCKED_STREAK}:
        out["stall_flag"] = True
    out["resume_pack_preview"] = build_resume_pack(project_root, out)
    return out


# --- AgentDriver public API (v1.6.7 Path C) ---


def goal_driver_start(
    project_root: Path,
    run_id: str,
    *,
    run_loop: bool = False,
    max_turns: int | None = None,
    turn_timeout_sec: int | None = None,
    bridge_cmd: str | None = None,
    spawn_fn=None,
) -> dict[str, Any]:
    """Start AgentDriver for an existing run (single lock)."""
    return gad_driver_start(
        project_root,
        run_id,
        longrun=True,
        attach_supervisor=True,
        run_loop=run_loop,
        max_loop_turns=max_turns,
        max_turns=max_turns,
        turn_timeout_sec=turn_timeout_sec,
        spawn_fn=spawn_fn,
        bridge_cmd=bridge_cmd,
    )


def goal_driver_status(project_root: Path, run_id: str) -> dict[str, Any]:
    return gad_driver_status(project_root, run_id)


def goal_driver_stop(project_root: Path, run_id: str) -> dict[str, Any]:
    return gad_driver_stop(project_root, run_id)


def goal_driver_run_loop(
    project_root: Path,
    run_id: str,
    *,
    max_loop_turns: int | None = None,
    bridge_cmd: str | None = None,
    spawn_fn=None,
) -> dict[str, Any]:
    return gad_driver_run_loop(
        project_root,
        run_id,
        max_loop_turns=max_loop_turns,
        bridge_cmd=bridge_cmd,
        spawn_fn=spawn_fn,
    )


def plan_multi_version(project_root: Path, utterance: str) -> dict[str, Any]:
    """Public helper: multi-version intent → dual-track lake plan (no run mutation)."""
    from beacon.utils.multi_version_intent import build_multi_version_execution_plan

    return build_multi_version_execution_plan(Path(project_root), utterance)
