"""Domain FSM / entity-precedence implement admission (v1.6.8 friction-closeout).

Prevents air-castle implementation order: downstream entities cannot be
implemented while required predecessors are not closed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.domain_fsm import (
    domain_fsm_is_required,
    parse_domain_fsm_from_truth,
)
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version

REASON_PREDECESSOR_OPEN = "fsm_implement_predecessor_open"
REASON_ORDER_VIOLATION = "fsm_implement_order_violation"


def _truth_path(project_root: Path, version: str, feature: str) -> Path:
    slug = feature_slug(feature)
    return project_root / "docs" / "beacon" / version / "features" / slug / "truth.md"


def _feature_closed(project_root: Path, *, version: str, feature: str) -> bool:
    """Heuristic: QA scorecard release_ready or implementation summary accepted."""
    slug = feature_slug(feature)
    score = project_root / ".beacon" / "qa" / "features" / slug / "scorecard.json"
    if score.exists():
        try:
            import json

            data = json.loads(score.read_text(encoding="utf-8"))
            if bool(data.get("release_ready")):
                return True
        except Exception:  # noqa: BLE001
            pass
    # technical implementation / revision accepted
    for name in (
        f"technical-implementation-{slug}.json",
        f"{slug}.revision.json",
    ):
        path = project_root / "docs" / "beacon" / version / ".machine" / "execution" / name
        if not path.exists():
            continue
        try:
            import json

            data = json.loads(path.read_text(encoding="utf-8"))
            status = str(data.get("delivery_status") or data.get("status") or "").lower()
            if status in {"accepted", "implemented", "verified", "released", "pass"}:
                return True
            if bool(data.get("release_ready")):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def evaluate_fsm_implement_order(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> dict[str, Any]:
    """Block implement when domain entity precedence predecessors are open."""
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    slug = feature_slug(feature)
    truth = _truth_path(root, resolved, slug)
    if not truth.exists():
        # legacy paths
        for alt in (
            root / "docs" / "beacon" / resolved / "prd" / f"{slug}.md",
        ):
            if alt.exists():
                truth = alt
                break

    if not truth.exists():
        return {
            "schema_version": "1.0",
            "status": "pass",
            "blocked": False,
            "reason_code": "",
            "required": False,
            "note": "truth_missing_skip",
            "feature": slug,
            "version": resolved,
        }

    markdown = truth.read_text(encoding="utf-8")
    req = domain_fsm_is_required(truth_markdown=markdown, version=resolved)
    if not req.get("required"):
        return {
            "schema_version": "1.0",
            "status": "pass",
            "blocked": False,
            "reason_code": "",
            "required": False,
            "requirement": req,
            "feature": slug,
            "version": resolved,
        }

    projection = parse_domain_fsm_from_truth(markdown)
    entities = projection.get("entities") if isinstance(projection.get("entities"), list) else []
    # entities expected: [{name, order, requires: [..]}] or similar
    by_name: dict[str, dict[str, Any]] = {}
    ordered: list[dict[str, Any]] = []
    for ent in entities:
        if not isinstance(ent, dict):
            continue
        name = str(ent.get("entity") or ent.get("name") or ent.get("id") or "").strip()
        if not name:
            continue
        requires = ent.get("requires") if isinstance(ent.get("requires"), list) else []
        requires = [str(x).strip() for x in requires if str(x).strip()]
        row = {"name": name, "requires": requires, "raw": ent}
        by_name[name.lower()] = row
        ordered.append(row)

    # If current feature name matches an entity, enforce its requires
    current_keys = {slug.lower(), slug.replace("-", "_").lower()}
    # also last path segment after version prefix
    for part in slug.split("-"):
        if part:
            current_keys.add(part.lower())

    target = None
    for name, row in by_name.items():
        if name in current_keys or name.replace("_", "-") in current_keys:
            target = row
            break
    # If feature is the domain package itself (not entity-named), pass with advisory
    if target is None:
        return {
            "schema_version": "1.0",
            "status": "pass",
            "blocked": False,
            "reason_code": "",
            "required": True,
            "requirement": req,
            "entities": [r["name"] for r in ordered],
            "note": "no_entity_match_for_feature_slug",
            "feature": slug,
            "version": resolved,
        }

    open_preds: list[str] = []
    for pred in target.get("requires") or []:
        # predecessor may be feature slug or entity name; check closed by feature slug heuristics
        pred_slug = feature_slug(pred)
        if not _feature_closed(root, version=resolved, feature=pred_slug):
            # also try entity-named feature patterns
            if not _feature_closed(root, version=resolved, feature=pred):
                open_preds.append(pred)

    if open_preds:
        first = open_preds[0]
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_PREDECESSOR_OPEN,
            "reason_codes": [REASON_PREDECESSOR_OPEN, REASON_ORDER_VIOLATION],
            "required": True,
            "feature": slug,
            "version": resolved,
            "entity": target.get("name"),
            "open_predecessors": open_preds,
            "recommended_command": (
                f'beacon implement run "{feature_slug(first)}" --project {root} --version {resolved}'
            ),
            "message": f"entity precedence blocks implement of {slug}; open predecessors: {open_preds}",
        }

    return {
        "schema_version": "1.0",
        "status": "pass",
        "blocked": False,
        "reason_code": "",
        "required": True,
        "feature": slug,
        "version": resolved,
        "entity": target.get("name"),
        "predecessors": target.get("requires") or [],
    }
