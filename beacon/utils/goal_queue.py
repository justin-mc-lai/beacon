"""Goal queue — support discovery handoff from loop-goal to product-goal (v1.6.7).

Loop discovers and enqueues; Goal consumes. Loop never marks product complete.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug

SCHEMA_VERSION = "goal-queue.v1"
REASON_LOOP_CANNOT_COMPLETE = "loop_cannot_mark_product_complete"
REASON_QUEUE_EMPTY = "goal_queue_empty"


def goal_queue_dir(project_root: Path) -> Path:
    return Path(project_root).expanduser().resolve() / ".beacon" / "state" / "goal-queue"


def goal_queue_path(project_root: Path) -> Path:
    return goal_queue_dir(project_root) / "queue.json"


def _empty_queue() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "items": [],
        "updated_at": now_iso(),
    }


def load_goal_queue(project_root: Path) -> dict[str, Any]:
    path = goal_queue_path(project_root)
    if not path.exists():
        return _empty_queue()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_queue()
    if not isinstance(data, dict):
        return _empty_queue()
    items = data.get("items") if isinstance(data.get("items"), list) else []
    return {
        "schema_version": SCHEMA_VERSION,
        "items": [item for item in items if isinstance(item, dict)],
        "updated_at": str(data.get("updated_at") or now_iso()),
    }


def save_goal_queue(project_root: Path, payload: dict[str, Any]) -> Path:
    path = goal_queue_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "items": list(payload.get("items") or []),
        "updated_at": now_iso(),
    }
    write_json(path, payload)
    return path


def enqueue_discovery(
    project_root: Path,
    *,
    utterance: str,
    version: str = "",
    feature: str = "",
    source: str = "beacon-loop-goal",
    priority: str = "normal",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Loop/support discovery writes one queue item for goal consumption."""
    queue = load_goal_queue(project_root)
    item = {
        "id": f"gq-{uuid.uuid4().hex[:12]}",
        "utterance": str(utterance or "").strip(),
        "version": str(version or "").strip(),
        "feature": feature_slug(feature) if feature else "",
        "source": source,
        "tier": "support_discovery",
        "priority": priority,
        "status": "queued",
        "created_at": now_iso(),
        "metadata": metadata if isinstance(metadata, dict) else {},
        # Explicit non-authority: discovery never claims product complete
        "product_complete": False,
        "may_mark_product_complete": False,
    }
    items = list(queue.get("items") or [])
    items.append(item)
    queue["items"] = items
    path = save_goal_queue(project_root, queue)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "blocked": False,
        "item": item,
        "queue_path": str(path.relative_to(Path(project_root).resolve())),
        "queue_depth": len(items),
    }


def list_queued(project_root: Path, *, status: str = "queued") -> list[dict[str, Any]]:
    queue = load_goal_queue(project_root)
    return [
        item
        for item in (queue.get("items") or [])
        if isinstance(item, dict) and (not status or str(item.get("status") or "") == status)
    ]


def consume_next(
    project_root: Path,
    *,
    consumer: str = "beacon-goal",
) -> dict[str, Any]:
    """Product Goal consumes the oldest queued discovery item."""
    queue = load_goal_queue(project_root)
    items = list(queue.get("items") or [])
    target = next((item for item in items if str(item.get("status") or "") == "queued"), None)
    if not target:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "empty",
            "blocked": False,
            "reason_code": REASON_QUEUE_EMPTY,
            "item": None,
        }
    target["status"] = "consumed"
    target["consumed_at"] = now_iso()
    target["consumed_by"] = consumer
    save_goal_queue(project_root, {"items": items})
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "blocked": False,
        "item": target,
        "consumer": consumer,
    }


def reject_loop_product_complete(*, attempted_by: str = "beacon-loop-goal") -> dict[str, Any]:
    """Hard guard: loop/support surfaces cannot mark product complete."""
    return {
        "schema_version": SCHEMA_VERSION,
        "allowed": False,
        "blocked": True,
        "status": "blocked",
        "reason_code": REASON_LOOP_CANNOT_COMPLETE,
        "attempted_by": attempted_by,
        "redirect": "beacon-goal",
        "message": "loop-goal is support discovery only; use beacon-goal for product delivery complete",
    }


def assert_not_product_complete_authority(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Strip/forbid product-complete authority fields from loop-produced payloads."""
    data = dict(payload or {})
    forbidden_hits: list[str] = []
    for key in (
        "product_complete",
        "product_goal_complete",
        "qa_verdict",
        "release_verdict",
        "release_ready",
        "final_verdict",
    ):
        if key in data and data.get(key) not in (False, None, "", "not_applicable", "n/a"):
            # truthy complete claims are forbidden
            if key in {"product_complete", "product_goal_complete"} and data.get(key) is True:
                forbidden_hits.append(key)
            elif key in {"qa_verdict", "release_verdict", "final_verdict"} and str(data.get(key) or "").lower() in {
                "pass",
                "passed",
                "complete",
                "completed",
                "ready",
            }:
                forbidden_hits.append(key)
            elif key == "release_ready" and bool(data.get(key)):
                forbidden_hits.append(key)
            # always clear authority fields from loop payload projection
            if key in {"product_complete", "product_goal_complete"}:
                data[key] = False
            elif key == "release_ready":
                data[key] = False
            else:
                data[key] = None
    data["may_mark_product_complete"] = False
    data["product_complete_authority"] = "beacon-goal+evaluator"
    if forbidden_hits:
        data["status"] = "blocked"
        data["blocked"] = True
        data["reason_code"] = REASON_LOOP_CANNOT_COMPLETE
        data["forbidden_fields"] = forbidden_hits
    return data
