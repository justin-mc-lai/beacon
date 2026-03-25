"""Machine-backed story/revision state helpers for Beacon v1.1.6."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from beacon.utils.versioning import resolve_target_version


def feature_slug(text: str) -> str:
    return "-".join(str(text or "").strip().lower().split())


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def _version_root(project_root: Path, version: str) -> Path:
    resolved = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved


def machine_story_dir(project_root: Path, version: str) -> Path:
    return _version_root(project_root, version) / ".machine" / "user-story"


def machine_story_path(project_root: Path, version: str, feature: str) -> Path:
    return machine_story_dir(project_root, version) / f"{feature_slug(feature)}.json"


def user_story_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    return _version_root(project_root, version) / "user-story" / f"{feature_slug(feature)}.md"


def _prd_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    return _version_root(project_root, version) / "prd" / f"{feature_slug(feature)}.md"


def _test_case_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    return _version_root(project_root, version) / "qa" / "test-cases" / f"{feature_slug(feature)}.md"


def _read_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return fallback
    return payload if isinstance(payload, dict) else fallback


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _extract_acceptance_criteria(markdown: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in str(markdown or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("| AC-"):
            parts = [p.strip() for p in stripped.strip("|").split("|")]
            if len(parts) >= 3:
                items.append({"id": parts[0], "theme": parts[1], "text": parts[2]})
        elif stripped.startswith("- [ ] AC-"):
            rest = stripped[len("- [ ] ") :]
            ac_id, _, desc = rest.partition(" ")
            items.append({"id": ac_id.strip(), "theme": "general", "text": desc.strip() or "TBD"})
    return items


def _default_items(markdown: str) -> list[dict[str, Any]]:
    ac_seed = _extract_acceptance_criteria(markdown)
    if not ac_seed:
        ac_seed = [{"id": "AC-001", "theme": "general", "text": "Acceptance criteria TBD"}]
    items: list[dict[str, Any]] = []
    for ac in ac_seed:
        items.append(
            {
                "id": ac["id"],
                "kind": "ac",
                "theme": ac.get("theme", "general"),
                "text": ac.get("text", "TBD"),
                "required": True,
                "status": "draft",
                "implemented_by_run_id": None,
                "verified_by_run_id": None,
                "accepted_at": None,
                "changed_in_revision": None,
            }
        )
    items.append(
        {
            "id": "TASK-001",
            "kind": "task",
            "text": "Implement current frozen revision",
            "required": True,
            "status": "draft",
            "implemented_by_run_id": None,
            "verified_by_run_id": None,
            "accepted_at": None,
            "changed_in_revision": None,
        }
    )
    for idx, ac in enumerate(ac_seed, start=1):
        items.append(
            {
                "id": f"TEST-{idx:03d}",
                "kind": "test",
                "text": f"Verify {ac['id']} — {ac['text']}",
                "required": True,
                "status": "draft",
                "implemented_by_run_id": None,
                "verified_by_run_id": None,
                "accepted_at": None,
                "changed_in_revision": None,
                "covers": [ac["id"]],
            }
        )
    return items


def _next_revision_id(root_state: dict[str, Any]) -> str:
    max_num = 0
    for rev in root_state.get("revisions", []):
        if not isinstance(rev, dict):
            continue
        rid = str(rev.get("revision_id", ""))
        if rid.startswith("R"):
            try:
                max_num = max(max_num, int(rid[1:]))
            except Exception:  # noqa: BLE001
                pass
    return f"R{max_num + 1}"


def _baseline_hash(project_root: Path, version: str, feature: str) -> str:
    parts: list[str] = []
    for path in (user_story_markdown_path(project_root, version, feature), _prd_markdown_path(project_root, version, feature), _test_case_markdown_path(project_root, version, feature)):
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
    return "sha256:" + hashlib.sha256("\n\n".join(parts).encode("utf-8")).hexdigest()


def ensure_story_state(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    path = machine_story_path(project_root, resolved_version, feature)
    existing = _read_json(path, {})
    if existing:
        return existing
    markdown = user_story_markdown_path(project_root, resolved_version, feature).read_text(encoding="utf-8") if user_story_markdown_path(project_root, resolved_version, feature).exists() else ""
    revision_id = "R1"
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "current_revision_id": revision_id,
        "lifecycle_status": "draft",
        "updated_at": _now_iso(),
        "revisions": [
            {
                "revision_id": revision_id,
                "feature_slug": feature_slug(feature),
                "source_revision_id": None,
                "reason": "draft",
                "doc_status": "draft",
                "delivery_status": "idle",
                "baseline_hash": None,
                "superseded_by": None,
                "created_at": _now_iso(),
                "frozen_at": None,
                "accepted_at": None,
                "accepted_by": None,
            }
        ],
        "stories": [
            {
                "story_id": "US-001",
                "revision_id": revision_id,
                "title": feature,
                "priority": "medium",
                "status": "draft",
                "items": _default_items(markdown),
            }
        ],
    }
    _write_json(path, payload)
    return payload


def load_story_state(
    project_root: Path,
    version: str,
    feature: str,
    *,
    create_if_missing: bool = False,
    revision_id: str = "R1",
) -> dict[str, Any] | None:
    resolved_version = resolve_target_version(project_root, version)
    path = machine_story_path(project_root, resolved_version, feature)
    if not path.exists():
        if create_if_missing:
            ensure_story_state(project_root, resolved_version, feature)
        else:
            return None
    root_state = _read_json(path, {})
    if not root_state:
        return None
    target_revision = str(root_state.get("current_revision_id", "") or revision_id)
    for story in root_state.get("stories", []):
        if isinstance(story, dict) and str(story.get("revision_id", "")) == target_revision:
            out = dict(story)
            out.setdefault("feature", feature)
            out.setdefault("feature_slug", feature_slug(feature))
            out.setdefault("version", resolved_version)
            out.setdefault("revision_id", target_revision)
            return out
    return None


def save_story_state(
    project_root: Path,
    version: str,
    feature: str,
    payload: dict[str, Any] | None = None,
    *,
    state: dict[str, Any] | None = None,
) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    path = machine_story_path(project_root, resolved_version, feature)
    root_state = _read_json(path, {}) or ensure_story_state(project_root, resolved_version, feature)
    effective = dict(state if state is not None else payload if payload is not None else {})
    target_revision = str(effective.get("revision_id", root_state.get("current_revision_id", "R1")) or "R1")
    stories = root_state.get("stories") if isinstance(root_state.get("stories"), list) else []
    replaced = False
    for idx, story in enumerate(stories):
        if isinstance(story, dict) and str(story.get("revision_id", "")) == target_revision:
            merged = dict(story)
            merged.update(effective)
            merged["revision_id"] = target_revision
            merged["title"] = merged.get("title") or feature
            stories[idx] = merged
            replaced = True
            break
    if not replaced:
        effective.setdefault("story_id", "US-001")
        effective.setdefault("title", feature)
        effective.setdefault("priority", "medium")
        effective.setdefault("status", "draft")
        effective["revision_id"] = target_revision
        stories.append(effective)
    root_state["stories"] = stories
    root_state["version"] = resolved_version
    root_state["updated_at"] = _now_iso()
    _write_json(path, root_state)
    return path


def get_active_revision(payload: dict[str, Any]) -> dict[str, Any] | None:
    rid = str(payload.get("current_revision_id", "") or "")
    for rev in payload.get("revisions", []):
        if isinstance(rev, dict) and str(rev.get("revision_id", "")) == rid:
            return rev
    return None


def _active_story(root_state: dict[str, Any]) -> dict[str, Any] | None:
    rid = str(root_state.get("current_revision_id", "") or "")
    for story in root_state.get("stories", []):
        if isinstance(story, dict) and str(story.get("revision_id", "")) == rid:
            return story
    return None


def freeze_story_state(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    root_state = ensure_story_state(project_root, version, feature)
    rev = get_active_revision(root_state)
    if rev is None:
        raise ValueError("active revision missing")
    rev["doc_status"] = "frozen"
    rev["reason"] = rev.get("reason") or "freeze"
    rev["frozen_at"] = _now_iso()
    rev["baseline_hash"] = _baseline_hash(project_root, version, feature)
    root_state["lifecycle_status"] = "frozen"
    story = _active_story(root_state)
    if story is not None:
        story["status"] = "frozen"
    _write_json(machine_story_path(project_root, resolve_target_version(project_root, version), feature), root_state)
    return root_state


def reopen_story_state(project_root: Path, version: str, feature: str, *, reason: str = "reopen") -> dict[str, Any]:
    root_state = ensure_story_state(project_root, version, feature)
    current = get_active_revision(root_state)
    if current is None:
        raise ValueError("active revision missing")
    next_revision_id = _next_revision_id(root_state)
    current["superseded_by"] = next_revision_id
    current["doc_status"] = "superseded"
    current["delivery_status"] = "superseded"
    previous_story = _active_story(root_state)
    if previous_story is not None:
        previous_story["status"] = "superseded"
    new_revision = {
        "revision_id": next_revision_id,
        "feature_slug": root_state.get("feature_slug"),
        "source_revision_id": current.get("revision_id"),
        "reason": reason,
        "doc_status": "draft",
        "delivery_status": "idle",
        "baseline_hash": None,
        "superseded_by": None,
        "created_at": _now_iso(),
        "frozen_at": None,
        "accepted_at": None,
        "accepted_by": None,
    }
    root_state.setdefault("revisions", []).append(new_revision)
    root_state["current_revision_id"] = next_revision_id
    root_state["lifecycle_status"] = "draft"
    items: list[dict[str, Any]] = []
    if isinstance(previous_story, dict):
        for item in previous_story.get("items", []):
            if not isinstance(item, dict):
                continue
            cloned = dict(item)
            cloned["status"] = "draft"
            cloned["implemented_by_run_id"] = None
            cloned["verified_by_run_id"] = None
            cloned["accepted_at"] = None
            cloned["changed_in_revision"] = next_revision_id
            items.append(cloned)
    root_state.setdefault("stories", []).append(
        {
            "story_id": "US-001",
            "revision_id": next_revision_id,
            "title": feature,
            "priority": "medium",
            "status": "draft",
            "items": items,
        }
    )
    _write_json(machine_story_path(project_root, resolve_target_version(project_root, version), feature), root_state)
    return root_state


def mark_revision_implemented(project_root: Path, version: str, feature: str, *, run_id: str, changed_files: list[str] | None = None) -> dict[str, Any]:
    root_state = ensure_story_state(project_root, version, feature)
    rev = get_active_revision(root_state)
    story = _active_story(root_state)
    if rev is None or story is None:
        raise ValueError("active revision/story missing")
    if str(rev.get("doc_status", "draft")) != "frozen":
        raise ValueError("revision_not_frozen")
    rev["delivery_status"] = "implemented"
    root_state["lifecycle_status"] = "implemented"
    story["status"] = "implemented"
    for item in story.get("items", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("kind", "")) in {"task", "ac"} and bool(item.get("required", True)):
            item["status"] = "implemented"
            item["implemented_by_run_id"] = run_id
            item["changed_in_revision"] = str(rev.get("revision_id", "R1"))
    if changed_files is not None:
        rev["changed_files"] = list(changed_files)
    _write_json(machine_story_path(project_root, resolve_target_version(project_root, version), feature), root_state)
    return root_state


def mark_revision_verified(project_root: Path, version: str, feature: str, *, run_id: str, passed: bool) -> dict[str, Any]:
    root_state = ensure_story_state(project_root, version, feature)
    rev = get_active_revision(root_state)
    story = _active_story(root_state)
    if rev is None or story is None:
        raise ValueError("active revision/story missing")
    rev["delivery_status"] = "verified" if passed else "blocked"
    root_state["lifecycle_status"] = rev["delivery_status"]
    story["status"] = "verified" if passed else "blocked"
    for item in story.get("items", []):
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", ""))
        if kind == "test":
            item["status"] = "passed" if passed else "failed"
            item["verified_by_run_id"] = run_id
        elif kind == "ac" and str(item.get("status", "")) == "implemented":
            item["status"] = "verified" if passed else "failed"
            item["verified_by_run_id"] = run_id
    _write_json(machine_story_path(project_root, resolve_target_version(project_root, version), feature), root_state)
    return root_state


def accept_revision(project_root: Path, version: str, feature: str, *, actor: str = "review.accept") -> dict[str, Any]:
    root_state = ensure_story_state(project_root, version, feature)
    rev = get_active_revision(root_state)
    story = _active_story(root_state)
    if rev is None or story is None:
        raise ValueError("active revision/story missing")
    items = [item for item in story.get("items", []) if isinstance(item, dict)]
    required_acs = [i for i in items if i.get("kind") == "ac" and bool(i.get("required", True))]
    required_tests = [i for i in items if i.get("kind") == "test" and bool(i.get("required", True))]
    if any(str(i.get("status", "")) != "verified" for i in required_acs):
        raise ValueError("acceptance_ac_not_verified")
    if any(str(i.get("status", "")) != "passed" for i in required_tests):
        raise ValueError("acceptance_tests_not_passed")
    accepted_at = _now_iso()
    rev["delivery_status"] = "accepted"
    rev["accepted_at"] = accepted_at
    rev["accepted_by"] = actor
    root_state["lifecycle_status"] = "accepted"
    story["status"] = "accepted"
    story["accepted_at"] = accepted_at
    story["accepted_by"] = actor
    for item in items:
        if str(item.get("status", "")) in {"verified", "passed", "implemented"}:
            item["status"] = "accepted"
            item["accepted_at"] = accepted_at
    _write_json(machine_story_path(project_root, resolve_target_version(project_root, version), feature), root_state)
    return root_state


def story_state_summary(payload: dict[str, Any]) -> dict[str, Any]:
    story = payload if isinstance(payload, dict) and "items" in payload else (_active_story(payload or {}) or {})
    rev = payload if isinstance(payload, dict) and payload.get("revision_id") and "items" not in payload else (get_active_revision(payload or {}) or {})
    items = [item for item in story.get("items", []) if isinstance(item, dict)]
    by_kind: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        by_kind.setdefault(str(item.get("kind", "unknown")), []).append(item)
    return {
        "feature": str(payload.get("feature", story.get("feature", "")) if isinstance(payload, dict) else story.get("feature", "")),
        "feature_slug": str(payload.get("feature_slug", story.get("feature_slug", "")) if isinstance(payload, dict) else story.get("feature_slug", "")),
        "version": str(payload.get("version", story.get("version", "")) if isinstance(payload, dict) else story.get("version", "")),
        "revision_id": str(rev.get("revision_id", story.get("revision_id", ""))),
        "doc_status": str(rev.get("doc_status", payload.get("lifecycle_status", "draft") if isinstance(payload, dict) else "draft")),
        "delivery_status": str(rev.get("delivery_status", "idle")),
        "story_status": str(story.get("status", "draft")),
        "item_counts": {
            kind: {
                "total": len(rows),
                "completed_like": len([r for r in rows if str(r.get("status", "")) in {"implemented", "verified", "passed", "accepted"}]),
                "verified_like": len([r for r in rows if str(r.get("status", "")) in {"verified", "passed", "accepted"}]),
            }
            for kind, rows in by_kind.items()
        },
    }


def summarize_story_items(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"total": 0, "implemented": 0, "verified": 0, "accepted": 0, "by_kind": {}}
    story = payload if "items" in payload else (_active_story(payload) or {})
    items = [item for item in story.get("items", []) if isinstance(item, dict)]
    by_kind: dict[str, dict[str, int]] = {}
    implemented = verified = accepted = 0
    for item in items:
        kind = str(item.get("kind", "unknown"))
        status = str(item.get("status", "draft"))
        bucket = by_kind.setdefault(kind, {"total": 0, "implemented": 0, "verified": 0, "accepted": 0, "failed": 0})
        bucket["total"] += 1
        if status in {"implemented", "verified", "passed", "accepted"}:
            implemented += 1
            bucket["implemented"] += 1
        if status in {"verified", "passed", "accepted"}:
            verified += 1
            bucket["verified"] += 1
        if status == "accepted":
            accepted += 1
            bucket["accepted"] += 1
        if status == "failed":
            bucket["failed"] += 1
    return {"total": len(items), "implemented": implemented, "verified": verified, "accepted": accepted, "by_kind": by_kind}
