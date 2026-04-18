"""Runtime projection helpers for Beacon v1.3.4 global board/ledger."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from beacon import __toolkit_version__
from beacon.utils.help_support import build_help_payload
from beacon.utils.project_skills import project_skill_config_path
from beacon.utils.qa_runtime import load_current_qa_session, load_qa_status
from beacon.utils.runtime import newest_run_id, read_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _project_key(project_root: Path) -> str:
    root = project_root.expanduser().resolve()
    path_hash = hashlib.sha1(str(root).encode("utf-8")).hexdigest()[:10]  # noqa: S324
    return f"{root.name}--{path_hash}"


def _run_git(path: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:  # noqa: BLE001
        return ""
    return completed.stdout.strip()


def _git_root(path: Path) -> Path | None:
    output = _run_git(path, "rev-parse", "--show-toplevel")
    if not output:
        return None
    try:
        return Path(output).expanduser().resolve()
    except Exception:  # noqa: BLE001
        return None


def _is_probable_child_repo(path: Path) -> bool:
    if not path.is_dir():
        return False
    if path.name.startswith("."):
        return False
    if path.name in {"node_modules", "vendor", "tmp", "dist", "build", "__pycache__"}:
        return False
    git_marker = path / ".git"
    return git_marker.exists()


def discover_git_scopes(project_root: Path) -> list[dict[str, Any]]:
    root = project_root.expanduser().resolve()
    scopes: list[dict[str, Any]] = []
    seen: set[str] = set()

    def append_scope(repo_root: Path, *, role: str) -> None:
        resolved = repo_root.expanduser().resolve()
        key = str(resolved)
        if key in seen:
            return
        seen.add(key)
        branch = _run_git(resolved, "branch", "--show-current")
        commit = _run_git(resolved, "rev-parse", "HEAD")
        dirty = bool(_run_git(resolved, "status", "--short"))
        scopes.append(
            {
                "scope_key": hashlib.sha1(key.encode("utf-8")).hexdigest()[:12],  # noqa: S324
                "repo_root": key,
                "repo_name": resolved.name,
                "branch": branch,
                "commit": commit,
                "dirty": dirty,
                "role": role,
                "worktree_path": key,
                "source_priority": "git_worktree",
            }
        )

    root_repo = _git_root(root)
    if root_repo is not None:
        append_scope(root_repo, role="primary")

    for child in sorted(root.iterdir()) if root.exists() else []:
        if not _is_probable_child_repo(child):
            continue
        repo_root = _git_root(child)
        if repo_root is None:
            continue
        append_scope(repo_root, role="service")

    return scopes


def detect_project_kind(project_root: Path, git_scopes: list[dict[str, Any]] | None = None) -> str:
    root = project_root.expanduser().resolve()
    scopes = git_scopes if isinstance(git_scopes, list) else discover_git_scopes(root)
    if len(scopes) > 1:
        return "multi_repo_workspace"
    if not scopes:
        config_path = project_skill_config_path(root)
        if config_path.exists():
            return "multi_repo_workspace"
    return "single_repo"


def detect_debug_state(project_root: Path) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    debug_root = root / ".beacon" / "debug"
    issues_root = debug_root / "issues"
    issues = sorted(issues_root.glob("*.json")) if issues_root.exists() else []
    index_path = debug_root / "index.json"
    index_payload = read_json(index_path, {}) if index_path.exists() else {}
    if issues:
        return {
            "state": "materialized_issue",
            "issue_count": len(issues),
            "index_exists": index_path.exists(),
            "paths": [str(path.relative_to(root)) for path in issues[:20]],
        }
    if index_path.exists():
        return {
            "state": "runtime_feed_only",
            "issue_count": 0,
            "index_exists": True,
            "paths": [str(index_path.relative_to(root))],
            "latest_run_id": str(index_payload.get("latest_run_id", "") or index_payload.get("run_id", "") or ""),
        }
    return {
        "state": "no_debug_feed",
        "issue_count": 0,
        "index_exists": False,
        "paths": [],
    }


def _resolve_primary_feature(project_root: Path, docs_version: str, feature: str | None = None) -> str:
    explicit = str(feature or "").strip()
    if explicit:
        return explicit
    qa_status = load_qa_status(project_root)
    qa_feature = str(qa_status.get("feature") or "").strip()
    if qa_feature:
        return qa_feature
    latest = newest_run_id(project_root)
    if latest:
        state = read_json(project_root / ".beacon" / "runs" / latest / "state.json", {})
        run_feature = str(state.get("feature") or "").strip()
        if run_feature:
            return run_feature
    help_payload = build_help_payload(project_root, version=docs_version, feature="", run_id=None)
    workflow_feature = str((help_payload.get("workflow_progress") or {}).get("feature") or "").strip()
    if workflow_feature:
        return workflow_feature
    return ""


def _material_state(path: Path) -> str:
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "Status" in text and "frozen" in text.lower():
        return "frozen"
    if "Status" in text and "ready" in text.lower():
        return "ready"
    return "draft"


def build_material_completeness(project_root: Path, *, docs_version: str, feature: str) -> dict[str, str]:
    if not feature:
        return {"prd": "missing", "user_story": "missing", "test_case": "missing"}
    slug = feature_slug(feature)
    base = project_root / "docs" / "beacon" / docs_version
    prd = base / "prd" / f"{slug}.md"
    user_story = base / "user-story" / f"{slug}.md"
    test_case = base / "qa" / "test-cases" / f"{slug}.md"
    return {
        "prd": _material_state(prd),
        "user_story": _material_state(user_story),
        "test_case": _material_state(test_case),
    }


def _runtime_mode(help_payload: dict[str, Any]) -> str:
    execution_surface = help_payload.get("execution_surface") if isinstance(help_payload.get("execution_surface"), dict) else {}
    if str(execution_surface.get("ralph_phase") or "").strip():
        return "ralph"
    implement_mode = str(execution_surface.get("implement_mode") or "").strip()
    if implement_mode:
        return implement_mode
    if str(execution_surface.get("qa_execution_mode") or "").strip():
        return "single"
    return "idle"


def _runtime_corroboration(help_payload: dict[str, Any], debug_state: dict[str, Any]) -> dict[str, Any]:
    execution_surface = help_payload.get("execution_surface") if isinstance(help_payload.get("execution_surface"), dict) else {}
    session_id = str(execution_surface.get("qa_current_session_id") or "").strip()
    mode = str(execution_surface.get("implement_mode") or "").strip()
    ralph_phase = str(execution_surface.get("ralph_phase") or "").strip()
    if session_id or mode or ralph_phase or str(debug_state.get("state") or "") != "no_debug_feed":
        return {
            "status": "available",
            "source": "runtime-cache",
            "reason": "runtime/session/debug evidence available as corroboration only",
        }
    return {
        "status": "missing",
        "source": "truth-only",
        "reason": "runtime cache absent; fallback to docs/beacon and formal evidence",
    }


def _derive_stage(help_payload: dict[str, Any]) -> str:
    current_stage = str(help_payload.get("current_stage") or "").strip()
    if current_stage in {"accepted", "released"}:
        return "release"
    if current_stage in {"verify", "verified"}:
        return "qa"
    if current_stage in {"implemented", "implementation"}:
        return "implement"
    return "requirements"


def _derive_progress_label(help_payload: dict[str, Any], materials: dict[str, str]) -> str:
    stage = _derive_stage(help_payload)
    if stage == "requirements":
        ready_count = len([value for value in materials.values() if value in {"ready", "frozen"}])
        return f"materials:{ready_count}/3"
    next_step = help_payload.get("next_step") if isinstance(help_payload.get("next_step"), dict) else {}
    return str(next_step.get("action") or stage)


def build_runtime_projection(
    project_root: Path,
    *,
    docs_version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    resolved_version = resolve_target_version(root, docs_version or "auto")
    primary_feature = _resolve_primary_feature(root, resolved_version, feature=feature)
    help_payload = build_help_payload(root, version=resolved_version, feature=primary_feature or "", run_id=None)
    git_scopes = discover_git_scopes(root)
    project_kind = detect_project_kind(root, git_scopes)
    debug_state = detect_debug_state(root)
    materials = build_material_completeness(root, docs_version=resolved_version, feature=primary_feature)
    runtime_mode = _runtime_mode(help_payload)
    runtime_corroboration = _runtime_corroboration(help_payload, debug_state)
    current_session = load_current_qa_session(root)

    source_snapshot = {
        "project_root": str(root),
        "docs_version": resolved_version,
        "feature": primary_feature,
        "project_kind": project_kind,
        "git_scopes": [
            {
                "repo_root": scope.get("repo_root"),
                "branch": scope.get("branch"),
                "commit": scope.get("commit"),
                "dirty": scope.get("dirty"),
                "role": scope.get("role"),
            }
            for scope in git_scopes
        ],
        "debug_state": debug_state.get("state"),
        "materials": materials,
        "stage": _derive_stage(help_payload),
        "next_step": (help_payload.get("next_step") or {}).get("action", ""),
        "blocked_reason": help_payload.get("blocked_reason", ""),
        "runtime_mode": runtime_mode,
        "qa_session_id": str(current_session.get("session_id") or ""),
    }
    source_hash = _stable_hash(source_snapshot)
    projection_seq = f"ps-{source_hash[:16]}"

    conflicts: list[str] = []
    if project_kind == "multi_repo_workspace" and not git_scopes:
        conflicts.append("workspace_without_git_scopes")

    preflight_status = "conflicted" if conflicts else "pass"
    uncertainty_reason = conflicts[0] if conflicts else ""
    project_key = _project_key(root)
    truth_refs = {
        "docs_root": str(root / "docs" / "beacon" / resolved_version),
        "state_root": str(root / ".beacon"),
    }

    envelope = {
        "schema_version": "1.0",
        "project_key": project_key,
        "display_name": root.name,
        "workspace_root": str(root),
        "project_root": str(root),
        "docs_version": resolved_version,
        "docs_root": truth_refs["docs_root"],
        "state_root": truth_refs["state_root"],
        "beacon_runtime_version": __toolkit_version__,
        "feature": primary_feature,
        "project_kind": project_kind,
        "truth": {
            **truth_refs,
            "source_of_truth": "docs/beacon + .beacon",
        },
        "lifecycle": {
            "stage": _derive_stage(help_payload),
            "current_stage": str(help_payload.get("current_stage") or ""),
            "progress_label": _derive_progress_label(help_payload, materials),
            "blocked": bool(help_payload.get("blocked", False)),
            "blocked_reason": str(help_payload.get("blocked_reason") or ""),
            "next_step": help_payload.get("next_step", {}),
        },
        "materials": materials,
        "runtime": {
            "mode": runtime_mode,
            "execution_surface": help_payload.get("execution_surface", {}),
            "runtime_corroboration": runtime_corroboration,
            "qa_session": current_session,
            "hud": help_payload.get("hud", {}),
        },
        "debug": debug_state,
        "git_scopes": git_scopes,
        "sessions": {
            "qa_session_id": str(current_session.get("session_id") or ""),
            "qa_runner_type": str(current_session.get("runner_type") or ""),
        },
        "projection": {
            "source_hash": source_hash,
            "projection_seq": projection_seq,
            "projection_version": "v1.3.4-runtime-ledger",
            "truth_refs": truth_refs,
            "preflight_status": preflight_status,
            "confidence": 1.0 if not conflicts else 0.6,
            "uncertainty_reason": uncertainty_reason,
            "preflight": {
                "status": preflight_status,
                "conflicts": conflicts,
                "source_priority": [
                    "user_explicit",
                    "git_worktree",
                    "project_config",
                    "truth_binding",
                    "heuristic",
                ],
            },
        },
        "board": {
            "version": resolved_version,
            "project_kind": project_kind,
            "current_stage": _derive_stage(help_payload),
            "progress_label": _derive_progress_label(help_payload, materials),
            "blocker": str(help_payload.get("blocked_reason") or "none"),
            "next_action": str((help_payload.get("next_step") or {}).get("action") or "none"),
            "debug_state": str(debug_state.get("state") or "no_debug_feed"),
            "runtime_corroboration": str(runtime_corroboration.get("status") or "missing"),
        },
    }
    return envelope
