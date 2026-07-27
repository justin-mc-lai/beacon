"""Hard stage-exit gates for product-goal tick (fill-then-pass).

Decision (deep-interview): goal orchestrates across harnesses; boundary gates are hard;
incomplete materials must be filled; freeze ack required before implement (fill ≠ self-sign).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.goal_reason_codes import (
    FREEZE_ACK_REQUIRED,
    RESUME_AWAIT_FREEZE,
    RESUME_AWAIT_RELEASE,
    RESUME_LOAD_NEXT,
    RESUME_NONE,
    STAGE_EXIT_BLOCKED,
    STAGE_EXIT_DESIGN_INCOMPLETE,
    STAGE_EXIT_IMPLEMENT_BLOCKED,
    STAGE_EXIT_OK,
    STAGE_EXIT_PLAN_INCOMPLETE,
    STAGE_EXIT_QA_EVIDENCE_MISSING,
    STAGE_EXIT_RELEASE_HUMAN,
    STAGE_EXIT_TRUTH_MISSING,
    STAGE_EXIT_TRUTH_NOT_FROZEN,
)
from beacon.utils.plan_artifact import plan_to_truth_gate
from beacon.utils.revision_state import load_revision_state
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version

SCHEMA = "goal-stage-exit-gate.v1"

# Back-compat aliases (tests/import sites)
REASON_TRUTH_DRAFT = STAGE_EXIT_TRUTH_NOT_FROZEN
REASON_FREEZE_ACK = FREEZE_ACK_REQUIRED
REASON_DESIGN_MISSING = STAGE_EXIT_DESIGN_INCOMPLETE
REASON_QA_EVIDENCE = STAGE_EXIT_QA_EVIDENCE_MISSING
REASON_PLAN_INCOMPLETE = STAGE_EXIT_PLAN_INCOMPLETE
REASON_OK = STAGE_EXIT_OK


def _truth_path(project_root: Path, version: str, feature: str) -> Path:
    slug = feature_slug(feature)
    return project_root / "docs" / "beacon" / version / "features" / slug / "truth.md"


def parse_truth_frontmatter_status(truth_md: str) -> str:
    if not truth_md.startswith("---"):
        return ""
    end = truth_md.find("\n---", 3)
    if end < 0:
        return ""
    block = truth_md[3:end]
    m = re.search(r"^status:\s*(\S+)", block, re.MULTILINE)
    return (m.group(1) if m else "").strip().strip("\"'")


def feature_package_frozen(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """Freeze ack = revision lifecycle frozen OR truth frontmatter status frozen."""
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    slug = feature_slug(feature)
    truth = _truth_path(root, resolved, slug)
    fm_status = ""
    if truth.is_file():
        fm_status = parse_truth_frontmatter_status(truth.read_text(encoding="utf-8"))
    rev = load_revision_state(root, version=resolved, feature=slug, create_if_missing=False)
    rev_life = str((rev or {}).get("lifecycle_status") or (rev or {}).get("doc_status") or "")
    frozen = fm_status == "frozen" or rev_life == "frozen"
    return {
        "frozen": frozen,
        "feature": slug,
        "version": resolved,
        "frontmatter_status": fm_status or None,
        "revision_lifecycle": rev_life or None,
        "truth_path": str(truth) if truth.is_file() else None,
        "truth_exists": truth.is_file(),
    }


def resolve_features_from_payload(payload: dict[str, Any]) -> list[str]:
    feats: list[str] = []
    f = str(payload.get("feature") or "").strip()
    if f:
        feats.append(feature_slug(f))
    for lake in payload.get("lakes") or []:
        if isinstance(lake, str) and lake.strip():
            feats.append(feature_slug(lake.strip()))
        elif isinstance(lake, dict):
            s = str(lake.get("slug") or lake.get("feature") or "").strip()
            if s:
                feats.append(feature_slug(s))
    seen: set[str] = set()
    out: list[str] = []
    for x in feats:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _plan_artifact_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    art = payload.get("plan_artifact") if isinstance(payload.get("plan_artifact"), dict) else {}
    if art:
        return art
    for s in payload.get("stages") or []:
        if not isinstance(s, dict) or s.get("stage") != "plan":
            continue
        art = s.get("plan_artifact") if isinstance(s.get("plan_artifact"), dict) else {}
        if art:
            return art
        ps = s.get("plan_subintent") if isinstance(s.get("plan_subintent"), dict) else {}
        art = ps.get("plan_artifact") if isinstance(ps.get("plan_artifact"), dict) else {}
        if art:
            return art
    return {}


def _design_complete(payload: dict[str, Any], project_root: Path) -> bool:
    ds = payload.get("design_stage") if isinstance(payload.get("design_stage"), dict) else {}
    if ds:
        bas = ds.get("baseline") if isinstance(ds.get("baseline"), dict) else {}
        if bas.get("status") in {"ok", "pass", "written", "exists", "complete"}:
            return True
        if bas.get("design_path"):
            p = project_root / str(bas["design_path"])
            if p.is_file():
                return True
        lint = ds.get("lint") if isinstance(ds.get("lint"), dict) else {}
        if lint and not lint.get("blocked") and lint.get("status") in {"pass", "ok", "clean"}:
            return True
    if (project_root / "DESIGN.md").is_file():
        return True
    return False


def _qa_evidence_present(project_root: Path, *, version: str, features: list[str]) -> bool:
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    candidates: list[Path] = []
    for feat in features or ["_project"]:
        slug = feature_slug(feat) if feat != "_project" else ""
        base = root / "docs" / "beacon" / resolved
        if slug:
            candidates.append(base / "features" / slug / "evidence.md")
            candidates.append(base / "qa" / f"{slug}-scorecard.md")
            candidates.append(base / "qa" / f"{slug}-ac-closure.md")
            candidates.append(root / ".beacon" / "evidence" / "qa" / resolved / slug / "scorecard.json")
        candidates.append(base / "qa" / "smoke-evidence.md")
    for p in candidates:
        if p.is_file() and p.stat().st_size > 20:
            return True
    return False


def evaluate_stage_exit(
    project_root: Path | str,
    payload: dict[str, Any],
    *,
    stage: str,
) -> dict[str, Any]:
    """Return allow + fill routing for leaving *stage* (marking it done)."""
    root = Path(project_root).expanduser().resolve()
    version = str(payload.get("version") or "auto")
    features = resolve_features_from_payload(payload)
    stage = str(stage or "").strip()
    base: dict[str, Any] = {
        "schema": SCHEMA,
        "stage": stage,
        "allow": True,
        "blocked": False,
        "reason_code": STAGE_EXIT_OK,
        "fill_harness": None,
        "fill_mode": None,
        "resume_action": RESUME_NONE,
        "features": features,
        "details": {},
    }

    if stage == "plan":
        art = _plan_artifact_from_payload(payload)
        tr: dict[str, Any] = {}
        if isinstance(art.get("truth_readiness"), dict):
            tr = art["truth_readiness"]
        elif isinstance(art.get("intent_decomposition"), dict):
            nested = art["intent_decomposition"].get("truth_readiness")
            tr = nested if isinstance(nested, dict) else {}
        gate = plan_to_truth_gate(art if art else None)
        blocks = bool(gate.get("blocks_auto_tick_past_plan") or gate.get("blocked"))
        if isinstance(tr, dict) and tr.get("blocks_auto_tick_past_plan"):
            blocks = True
        if blocks:
            base.update(
                {
                    "allow": False,
                    "blocked": True,
                    "reason_code": str(
                        gate.get("reason_code") or tr.get("reason_code") or STAGE_EXIT_PLAN_INCOMPLETE
                    ),
                    "fill_harness": "truth",
                    "fill_mode": "gen-truth",
                    "resume_action": RESUME_LOAD_NEXT,
                    "details": {"plan_to_truth_gate": gate, "truth_readiness": tr},
                }
            )
        return base

    if stage == "truth":
        if not features:
            base["details"] = {"note": "no_feature_bound_skip_package_freeze_check"}
            return base
        # v1.6.11+: scaffold/unfilled package cannot exit truth stage
        try:
            from beacon.utils.plan_goal_task_closure import (
                detect_scaffold_truth_block,
                version_requires_task_closure,
            )

            if version_requires_task_closure(version, features[0] if features else ""):
                scaffold_hits: list[dict[str, Any]] = []
                for feat in features:
                    tpath = _truth_path(root, resolve_target_version(root, version), feat)
                    if tpath.is_file():
                        chk = detect_scaffold_truth_block(tpath.read_text(encoding="utf-8"))
                        if chk.get("blocked"):
                            scaffold_hits.append({"feature": feat, **chk})
                if scaffold_hits:
                    base.update(
                        {
                            "allow": False,
                            "blocked": True,
                            "reason_code": "truth_scaffold_not_filled",
                            "fill_harness": "truth",
                            "fill_mode": "gen-truth",
                            "resume_action": RESUME_LOAD_NEXT,
                            "details": {"scaffold_hits": scaffold_hits},
                        }
                    )
                    return base
        except Exception:  # noqa: BLE001
            pass
        unfrozen: list[dict[str, Any]] = []
        for feat in features:
            info = feature_package_frozen(root, version=version, feature=feat)
            if not info["frozen"]:
                unfrozen.append(info)
        if unfrozen:
            missing = [u for u in unfrozen if not u.get("truth_exists")]
            drafts = [u for u in unfrozen if u.get("truth_exists")]
            if missing and not drafts:
                reason = STAGE_EXIT_TRUTH_MISSING
                resume = RESUME_LOAD_NEXT
            elif drafts and any(u.get("frontmatter_status") == "draft" for u in drafts):
                reason = STAGE_EXIT_TRUTH_NOT_FROZEN
                resume = RESUME_AWAIT_FREEZE
            else:
                reason = FREEZE_ACK_REQUIRED
                resume = RESUME_AWAIT_FREEZE
            base.update(
                {
                    "allow": False,
                    "blocked": True,
                    "reason_code": reason,
                    "fill_harness": "truth",
                    "fill_mode": "gen-truth",
                    "resume_action": resume,
                    "details": {"unfrozen": unfrozen},
                }
            )
        return base

    if stage == "design":
        if not _design_complete(payload, root):
            base.update(
                {
                    "allow": False,
                    "blocked": True,
                    "reason_code": STAGE_EXIT_DESIGN_INCOMPLETE,
                    "fill_harness": "design",
                    "fill_mode": "gen-design",
                    "resume_action": RESUME_LOAD_NEXT,
                }
            )
        return base

    if stage == "implement":
        adm = payload.get("implement_admission") if isinstance(payload.get("implement_admission"), dict) else {}
        if adm and adm.get("allow_implement") is False:
            base.update(
                {
                    "allow": False,
                    "blocked": True,
                    "reason_code": str(adm.get("reason_code") or STAGE_EXIT_IMPLEMENT_BLOCKED),
                    "fill_harness": "implement",
                    "fill_mode": "gen-implement",
                    "resume_action": RESUME_LOAD_NEXT,
                    "details": {
                        "implement_admission": {
                            k: adm.get(k) for k in ("allow_implement", "reason_code", "worktree_path")
                        }
                    },
                }
            )
        return base

    if stage == "qa":
        if not _qa_evidence_present(root, version=version, features=features):
            base.update(
                {
                    "allow": False,
                    "blocked": True,
                    "reason_code": STAGE_EXIT_QA_EVIDENCE_MISSING,
                    "fill_harness": "qa",
                    "fill_mode": "eval-qa",
                    "resume_action": RESUME_LOAD_NEXT,
                }
            )
        return base

    if stage == "release":
        base.update(
            {
                "allow": False,
                "blocked": True,
                "reason_code": STAGE_EXIT_RELEASE_HUMAN,
                "fill_harness": "release",
                "fill_mode": "eval-release",
                "resume_action": RESUME_AWAIT_RELEASE,
            }
        )
        return base

    return base


def apply_stage_exit_block(payload: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    """Mutate goal payload with block + fill routing."""
    payload = dict(payload)
    payload["blocked"] = True
    payload["status"] = "blocked"
    payload["reason_code"] = str(gate.get("reason_code") or STAGE_EXIT_BLOCKED)
    payload["stage_exit_gate"] = gate
    payload["fill_harness"] = gate.get("fill_harness")
    payload["fill_mode"] = gate.get("fill_mode")
    payload["resume_action"] = gate.get("resume_action") or RESUME_LOAD_NEXT
    hist = list(payload.get("history") or [])
    hist.append(
        {
            "event": "stage_exit_blocked",
            "stage": gate.get("stage"),
            "reason_code": payload["reason_code"],
            "fill_harness": payload.get("fill_harness"),
            "resume_action": payload.get("resume_action"),
        }
    )
    payload["history"] = hist
    return payload
