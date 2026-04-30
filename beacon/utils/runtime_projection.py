"""Runtime projection helpers for Beacon v1.3.4 global board/ledger."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from beacon import __toolkit_version__
from beacon.utils.help_support import build_help_payload, canonicalize_lifecycle_stage
from beacon.utils.project_skills import project_skill_config_path
from beacon.utils.qa_runtime import (
    list_qa_sessions,
    load_current_qa_session,
    load_qa_status,
    qa_session_manifest_path,
)
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


def _package_key(project_key: str, docs_version: str, feature: str) -> str:
    slug = feature_slug(feature) if feature else "workspace"
    return f"{project_key}:{docs_version}:{slug}"


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:  # noqa: BLE001
        return str(path)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _debug_issue_relevance(
    payload: dict[str, Any],
    *,
    docs_version: str,
    feature: str,
    active_run_ids: set[str],
) -> str:
    payload = payload if isinstance(payload, dict) else {}
    feature_candidates = {
        str(payload.get("feature") or "").strip(),
        str(payload.get("feature_slug") or "").strip(),
    }
    feature_candidates.discard("")
    if feature and (
        feature in feature_candidates
        or feature_slug(feature) in feature_candidates
    ):
        return "current_delivery"

    version_candidates = {
        str(payload.get("version") or "").strip(),
        str(payload.get("docs_version") or "").strip(),
    }
    version_candidates.discard("")
    if docs_version and docs_version in version_candidates:
        return "current_delivery"

    run_ids = {
        str(payload.get("run_id") or "").strip(),
        *(str(item).strip() for item in (payload.get("run_ids") or []) if str(item).strip()),
    }
    run_ids.discard("")
    if active_run_ids and run_ids.intersection(active_run_ids):
        return "current_delivery"

    return "historical_learning"


def _effective_debug_state(debug_issues: list[dict[str, Any]], debug_state: dict[str, Any]) -> dict[str, Any]:
    base = dict(debug_state if isinstance(debug_state, dict) else {})
    current_delivery_count = len(
        [
            item
            for item in debug_issues
            if str(item.get("delivery_relevance") or "") == "current_delivery"
            and str(item.get("materialization_state") or "") == "materialized_issue"
        ]
    )
    historical_count = len(
        [
            item
            for item in debug_issues
            if str(item.get("delivery_relevance") or "") == "historical_learning"
            and str(item.get("materialization_state") or "") == "materialized_issue"
        ]
    )
    base["current_delivery_issue_count"] = current_delivery_count
    base["historical_issue_count"] = historical_count
    if current_delivery_count > 0:
        base["state"] = "materialized_issue"
    elif historical_count > 0:
        base["state"] = "historical_learning_only"
    return base


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


def _feature_paths(project_root: Path, *, docs_version: str, feature: str) -> dict[str, Path]:
    slug = feature_slug(feature)
    base = project_root / "docs" / "beacon" / docs_version
    return {
        "prd": base / "prd" / f"{slug}.md",
        "user_story": base / "user-story" / f"{slug}.md",
        "test_case": base / "qa" / "test-cases" / f"{slug}.md",
    }


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
    paths = _feature_paths(project_root, docs_version=docs_version, feature=feature)
    return {
        "prd": _material_state(paths["prd"]),
        "user_story": _material_state(paths["user_story"]),
        "test_case": _material_state(paths["test_case"]),
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
    current_stage = canonicalize_lifecycle_stage(help_payload.get("current_stage"))
    if current_stage == "release":
        return "release"
    if current_stage == "qa":
        return "qa"
    if current_stage == "implement":
        return "implement"
    return "requirements"


def _derive_progress_label(help_payload: dict[str, Any], materials: dict[str, str]) -> str:
    stage = _derive_stage(help_payload)
    if stage == "requirements":
        ready_count = len([value for value in materials.values() if value in {"ready", "frozen"}])
        return f"materials:{ready_count}/3"
    next_step = help_payload.get("next_step") if isinstance(help_payload.get("next_step"), dict) else {}
    return str(next_step.get("action") or stage)


def _latest_implement_state(project_root: Path, *, docs_version: str, feature: str) -> dict[str, Any]:
    impl_root = project_root / ".beacon" / "implement"
    if not impl_root.exists():
        return {}
    feature_name = feature_slug(feature) if feature else ""
    latest_key = ""
    latest_payload: dict[str, Any] = {}
    for state_path in sorted(impl_root.glob("*/state.json")):
        payload = read_json(state_path, {})
        if not isinstance(payload, dict):
            continue
        if feature_name and str(payload.get("feature_slug") or "") not in {"", feature_name}:
            continue
        payload_version = str(payload.get("version") or "").strip()
        if payload_version and payload_version != docs_version:
            continue
        recency = str(
            payload.get("generated_at")
            or payload.get("updated_at")
            or payload.get("implemented_at")
            or state_path.parent.name
        )
        if recency >= latest_key:
            latest_key = recency
            latest_payload = payload
    return latest_payload


def _load_team_hud_payload(project_root: Path, help_payload: dict[str, Any]) -> dict[str, Any]:
    hud_refs = help_payload.get("hud") if isinstance(help_payload.get("hud"), dict) else {}
    team_hud_json = str(hud_refs.get("team_hud_json") or "").strip()
    if not team_hud_json:
        return {}
    return read_json(project_root / team_hud_json, {})


def _collect_feature_packages(
    project_root: Path,
    *,
    project_key: str,
    docs_version: str,
    feature: str,
    materials: dict[str, str],
) -> list[dict[str, Any]]:
    if not feature:
        return []
    paths = _feature_paths(project_root, docs_version=docs_version, feature=feature)
    package_key = _package_key(project_key, docs_version, feature)
    return [
        {
            "project_key": project_key,
            "package_key": package_key,
            "feature": feature,
            "feature_slug": feature_slug(feature),
            "docs_version": docs_version,
            "prd_path": _safe_relative(paths["prd"], project_root),
            "user_story_path": _safe_relative(paths["user_story"], project_root),
            "test_case_path": _safe_relative(paths["test_case"], project_root),
            "materials": materials,
        }
    ]


def _collect_feature_lifecycle(
    *,
    project_key: str,
    package_key: str,
    feature: str,
    help_payload: dict[str, Any],
    materials: dict[str, str],
    runtime_mode: str,
    debug_state: dict[str, Any],
    truth_refs: dict[str, str],
) -> list[dict[str, Any]]:
    next_step = help_payload.get("next_step") if isinstance(help_payload.get("next_step"), dict) else {}
    return [
        {
            "project_key": project_key,
            "package_key": package_key,
            "feature": feature,
            "current_stage": _derive_stage(help_payload),
            "progress_label": _derive_progress_label(help_payload, materials),
            "blocked": bool(help_payload.get("blocked", False)),
            "blocked_reason": str(help_payload.get("blocked_reason") or ""),
            "next_action": str(next_step.get("action") or ""),
            "runtime_mode": runtime_mode,
            "debug_state": str(debug_state.get("state") or "no_debug_feed"),
            "truth_refs": truth_refs,
        }
    ]


def _collect_stage_material_status(
    project_root: Path,
    *,
    project_key: str,
    package_key: str,
    docs_version: str,
    feature: str,
    materials: dict[str, str],
) -> list[dict[str, Any]]:
    if not feature:
        return []
    paths = _feature_paths(project_root, docs_version=docs_version, feature=feature)
    rows: list[dict[str, Any]] = []
    mapping = {
        "prd": "prd",
        "user_story": "user_story",
        "test_case": "test_case",
    }
    for material_type, key in mapping.items():
        rows.append(
            {
                "project_key": project_key,
                "package_key": package_key,
                "material_type": material_type,
                "status": str(materials.get(key) or "missing"),
                "truth_path": _safe_relative(paths[key], project_root),
            }
        )
    return rows


def _append_run_row(
    rows: list[dict[str, Any]],
    seen: set[str],
    *,
    run_id: str,
    payload: dict[str, Any],
    feature: str,
    docs_version: str,
    runtime_mode: str,
    source: str,
) -> None:
    normalized_run_id = str(run_id or payload.get("run_id") or "").strip()
    if not normalized_run_id or normalized_run_id in seen:
        return
    seen.add(normalized_run_id)
    rows.append(
        {
            "run_id": normalized_run_id,
            "feature": str(payload.get("feature") or feature or "").strip(),
            "docs_version": str(payload.get("version") or docs_version or "").strip(),
            "mode": str(payload.get("mode") or runtime_mode or "idle").strip() or "idle",
            "status": str(payload.get("status") or "unknown").strip() or "unknown",
            "started_at": str(
                payload.get("started_at")
                or payload.get("created_at")
                or payload.get("generated_at")
                or payload.get("updated_at")
                or ""
            ),
            "ended_at": str(payload.get("ended_at") or ""),
            "source": source,
            "truth_refs": list(payload.get("truth_refs") or []),
        }
    )


def _collect_runs(
    project_root: Path,
    *,
    docs_version: str,
    feature: str,
    runtime_mode: str,
    help_payload: dict[str, Any],
    current_session: dict[str, Any],
    implement_state: dict[str, Any],
    team_hud_payload: dict[str, Any],
    ralph_state: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    runs_root = project_root / ".beacon" / "runs"
    for state_path in sorted(runs_root.glob("*/state.json"), reverse=True):
        payload = read_json(state_path, {})
        if not isinstance(payload, dict):
            continue
        _append_run_row(
            rows,
            seen,
            run_id=state_path.parent.name,
            payload=payload,
            feature=feature,
            docs_version=docs_version,
            runtime_mode=runtime_mode,
            source="run_state",
        )

    help_run_state = help_payload.get("run_state") if isinstance(help_payload.get("run_state"), dict) else {}
    if help_run_state:
        _append_run_row(
            rows,
            seen,
            run_id=str(help_run_state.get("run_id") or newest_run_id(project_root) or ""),
            payload=help_run_state,
            feature=feature,
            docs_version=docs_version,
            runtime_mode=runtime_mode,
            source="help_payload",
        )

    if implement_state:
        _append_run_row(
            rows,
            seen,
            run_id=str(
                implement_state.get("run_id")
                or team_hud_payload.get("run_id")
                or ralph_state.get("active_run_id")
                or ""
            ),
            payload=implement_state,
            feature=feature,
            docs_version=docs_version,
            runtime_mode=runtime_mode,
            source="implement_state",
        )

    if ralph_state and str(ralph_state.get("active_run_id") or "").strip():
        _append_run_row(
            rows,
            seen,
            run_id=str(ralph_state.get("active_run_id") or ""),
            payload=ralph_state,
            feature=feature,
            docs_version=docs_version,
            runtime_mode="ralph",
            source="ralph_state",
        )

    if current_session:
        _append_run_row(
            rows,
            seen,
            run_id=str(current_session.get("run_id") or help_run_state.get("run_id") or ""),
            payload=current_session,
            feature=feature,
            docs_version=docs_version,
            runtime_mode=runtime_mode,
            source="qa_session",
        )

    return sorted(rows, key=lambda item: (str(item.get("started_at") or ""), str(item.get("run_id") or "")), reverse=True)


def _collect_run_workers(
    *,
    active_run_id: str,
    team_hud_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    roles = team_hud_payload.get("roles") if isinstance(team_hud_payload.get("roles"), list) else []
    run_id = str(team_hud_payload.get("run_id") or active_run_id or "")
    tmux_session = str(team_hud_payload.get("tmux_session") or "")
    rows: list[dict[str, Any]] = []
    for index, role in enumerate(roles, start=1):
        if not isinstance(role, dict):
            continue
        rows.append(
            {
                "run_id": run_id,
                "worker_id": str(role.get("worker_id") or f"worker-{index}"),
                "role": str(role.get("role") or f"worker-{index}"),
                "status": str(role.get("status") or "unknown"),
                "pane_id": str(role.get("pane_id") or ""),
                "tmux_session": tmux_session,
                "artifact_json_ref": str(role.get("json") or ""),
                "artifact_md_ref": str(role.get("markdown") or ""),
            }
        )
    return rows


def _collect_run_targets(
    *,
    runs: list[dict[str, Any]],
    git_scopes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in runs:
        run_id = str(run.get("run_id") or "")
        if not run_id:
            continue
        for scope in git_scopes:
            rows.append(
                {
                    "run_id": run_id,
                    "scope_key": str(scope.get("scope_key") or ""),
                    "target_branch": str(scope.get("branch") or ""),
                    "current_branch": str(scope.get("branch") or ""),
                    "service_name": str(scope.get("repo_name") or ""),
                    "scope_role": str(scope.get("role") or ""),
                }
            )
    return rows


def _collect_run_events(
    project_root: Path,
    *,
    runs: list[dict[str, Any]],
    ralph_state: dict[str, Any],
    debug_state: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sequence = 0
    for run in runs:
        run_id = str(run.get("run_id") or "")
        if not run_id:
            continue
        events_path = project_root / ".beacon" / "runs" / run_id / "events.jsonl"
        for event in _read_jsonl(events_path):
            sequence += 1
            rows.append(
                {
                    "run_id": run_id,
                    "event_seq": sequence,
                    "stage": str(event.get("stage") or ""),
                    "event": str(event.get("event") or event.get("action") or "event"),
                    "status": str(event.get("status") or ""),
                    "reason_code": str(event.get("reason_code") or ""),
                    "ts": str(event.get("ts") or event.get("timestamp") or ""),
                    "details_json": event,
                }
            )
    if ralph_state and str(ralph_state.get("active_run_id") or "").strip():
        sequence += 1
        rows.append(
            {
                "run_id": str(ralph_state.get("active_run_id") or ""),
                "event_seq": sequence,
                "stage": "ralph",
                "event": str(ralph_state.get("phase") or "ralph"),
                "status": str(ralph_state.get("status") or ""),
                "reason_code": str(ralph_state.get("current_blocker") or ""),
                "ts": str(ralph_state.get("updated_at") or ""),
                "details_json": ralph_state,
            }
        )
    if str(debug_state.get("state") or "") == "runtime_feed_only":
        sequence += 1
        rows.append(
            {
                "run_id": str(debug_state.get("latest_run_id") or ""),
                "event_seq": sequence,
                "stage": "debug",
                "event": "runtime_feed_only",
                "status": "warn",
                "reason_code": "runtime_feed_only",
                "ts": "",
                "details_json": debug_state,
            }
        )
    return rows


def _artifact_row(
    project_root: Path,
    *,
    run_id: str,
    artifact_type: str,
    path: Path,
    artifact_scope: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "artifact_type": artifact_type,
        "path": _safe_relative(path, project_root),
        "sha256": _sha256_file(path),
        "exists": path.exists(),
        "artifact_scope": artifact_scope,
    }


def _collect_artifact_refs(
    project_root: Path,
    *,
    docs_version: str,
    feature: str,
    help_payload: dict[str, Any],
    team_hud_payload: dict[str, Any],
    runs: list[dict[str, Any]],
    current_session: dict[str, Any],
    debug_state: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    default_run_id = str(runs[0].get("run_id") or "") if runs else ""
    if feature:
        for material_type, path in _feature_paths(project_root, docs_version=docs_version, feature=feature).items():
            key = (default_run_id, str(path))
            if key in seen:
                continue
            seen.add(key)
            rows.append(_artifact_row(project_root, run_id=default_run_id, artifact_type=material_type, path=path, artifact_scope="truth"))

    hud_refs = help_payload.get("hud") if isinstance(help_payload.get("hud"), dict) else {}
    for key, artifact_type in {
        "team_hud_json": "team_hud_json",
        "team_hud_html": "team_hud_html",
        "ralph_state_json": "ralph_state_json",
    }.items():
        rel_path = str(hud_refs.get(key) or "").strip()
        if not rel_path:
            continue
        path = project_root / rel_path
        artifact_key = (default_run_id, str(path))
        if artifact_key in seen:
            continue
        seen.add(artifact_key)
        rows.append(_artifact_row(project_root, run_id=default_run_id, artifact_type=artifact_type, path=path, artifact_scope="runtime"))

    if current_session and str(current_session.get("session_id") or "").strip():
        session_path = qa_session_manifest_path(project_root, str(current_session.get("session_id") or ""))
        artifact_key = (str(current_session.get("run_id") or default_run_id or ""), str(session_path))
        if artifact_key not in seen:
            seen.add(artifact_key)
            rows.append(
                _artifact_row(
                    project_root,
                    run_id=str(current_session.get("run_id") or default_run_id or ""),
                    artifact_type="qa_session_manifest",
                    path=session_path,
                    artifact_scope="runtime",
                )
            )

    for run in runs:
        run_id = str(run.get("run_id") or "")
        for artifact_type, relative in {
            "run_state": project_root / ".beacon" / "runs" / run_id / "state.json",
            "run_events": project_root / ".beacon" / "runs" / run_id / "events.jsonl",
        }.items():
            artifact_key = (run_id, str(relative))
            if artifact_key in seen:
                continue
            seen.add(artifact_key)
            rows.append(_artifact_row(project_root, run_id=run_id, artifact_type=artifact_type, path=relative, artifact_scope="runtime"))

    for role in team_hud_payload.get("roles", []) if isinstance(team_hud_payload.get("roles"), list) else []:
        if not isinstance(role, dict):
            continue
        run_id = str(team_hud_payload.get("run_id") or default_run_id or "")
        for field, artifact_type in {
            "json": "worker_json",
            "markdown": "worker_markdown",
        }.items():
            rel_path = str(role.get(field) or "").strip()
            if not rel_path:
                continue
            path = project_root / rel_path
            artifact_key = (run_id, str(path))
            if artifact_key in seen:
                continue
            seen.add(artifact_key)
            rows.append(_artifact_row(project_root, run_id=run_id, artifact_type=artifact_type, path=path, artifact_scope="runtime"))

    for rel_path in debug_state.get("paths", []) if isinstance(debug_state.get("paths"), list) else []:
        path = project_root / rel_path
        artifact_key = (default_run_id, str(path))
        if artifact_key in seen:
            continue
        seen.add(artifact_key)
        rows.append(_artifact_row(project_root, run_id=default_run_id, artifact_type="debug", path=path, artifact_scope="debug"))

    return rows


def _collect_git_workspace_bindings(
    *,
    project_key: str,
    package_key: str,
    git_scopes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scope in git_scopes:
        rows.append(
            {
                "project_key": project_key,
                "package_key": package_key,
                "repo_root": str(scope.get("repo_root") or ""),
                "branch": str(scope.get("branch") or ""),
                "commit_sha": str(scope.get("commit") or ""),
                "dirty": bool(scope.get("dirty")),
                "worktree_path": str(scope.get("worktree_path") or ""),
                "expected_branch_rule": "git_worktree_truth",
                "spec_status": "dirty" if bool(scope.get("dirty")) else "aligned",
                "updated_at": "",
            }
        )
    return rows


def _collect_host_sessions(
    project_root: Path,
    *,
    project_key: str,
    feature: str,
    current_session: dict[str, Any],
    qa_sessions: list[dict[str, Any]],
    help_payload: dict[str, Any],
    runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    execution_surface = help_payload.get("execution_surface") if isinstance(help_payload.get("execution_surface"), dict) else {}
    default_run_id = str(runs[0].get("run_id") or "") if runs else ""
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def append_session(payload: dict[str, Any], *, source: str) -> None:
        session_id = str(payload.get("session_id") or "").strip()
        host_runtime = str(payload.get("host_runtime") or execution_surface.get("host_runtime") or "").strip()
        run_id = str(payload.get("run_id") or default_run_id or "").strip()
        key = (host_runtime, session_id, run_id)
        if key in seen or (not session_id and not host_runtime):
            return
        seen.add(key)
        transcript_path = str(payload.get("transcript_path") or "").strip()
        transcript_ref = _safe_relative(project_root / transcript_path, project_root) if transcript_path else ""
        rows.append(
            {
                "project_key": project_key,
                "feature": str(payload.get("feature") or feature or ""),
                "run_id": run_id,
                "host_runtime": host_runtime,
                "session_id": session_id,
                "thread_id": str(payload.get("thread_id") or ""),
                "turn_id": str(payload.get("turn_id") or ""),
                "transcript_path": transcript_ref,
                "status": str(payload.get("status") or ("active" if source == "current" else "recorded")),
                "started_at": str(payload.get("started_at") or payload.get("created_at") or ""),
                "ended_at": str(payload.get("ended_at") or ""),
            }
        )

    for payload in qa_sessions:
        if isinstance(payload, dict):
            append_session(payload, source="history")
    if current_session:
        append_session(current_session, source="current")

    if not rows and str(execution_surface.get("host_runtime") or "").strip():
        rows.append(
            {
                "project_key": project_key,
                "feature": feature,
                "run_id": default_run_id,
                "host_runtime": str(execution_surface.get("host_runtime") or ""),
                "session_id": str(current_session.get("session_id") or f"host:{default_run_id}" if default_run_id else ""),
                "thread_id": "",
                "turn_id": "",
                "transcript_path": "",
                "status": "observed",
                "started_at": "",
                "ended_at": "",
            }
        )

    return rows


def _collect_debug_issues(
    project_root: Path,
    *,
    project_key: str,
    debug_state: dict[str, Any],
    docs_version: str,
    feature: str,
    active_run_ids: set[str],
) -> list[dict[str, Any]]:
    debug_root = project_root / ".beacon" / "debug"
    issues_root = debug_root / "issues"
    rows: list[dict[str, Any]] = []
    for issue_path in sorted(issues_root.glob("*.json")) if issues_root.exists() else []:
        payload = read_json(issue_path, {})
        payload = payload if isinstance(payload, dict) else {}
        relevance = _debug_issue_relevance(
            payload,
            docs_version=docs_version,
            feature=feature,
            active_run_ids=active_run_ids,
        )
        rows.append(
            {
                "project_key": project_key,
                "issue_id": issue_path.stem,
                "reason_code": str(payload.get("reason_code") or payload.get("code") or ""),
                "issue_status": str(payload.get("status") or "open"),
                "materialization_state": "materialized_issue",
                "delivery_relevance": relevance,
                "latest_event_at": str(payload.get("latest_event_at") or payload.get("updated_at") or payload.get("ts") or ""),
                "sample": str(payload.get("sample") or payload.get("summary") or payload.get("note") or issue_path.name),
                "suggested_capability": str(payload.get("suggested_capability") or "beacon-doctor"),
                "source_run_id": str(payload.get("run_id") or ""),
                "truth_refs": [_safe_relative(issue_path, project_root)],
            }
        )
    if not rows and str(debug_state.get("state") or "") == "runtime_feed_only":
        index_path = debug_root / "index.json"
        rows.append(
            {
                "project_key": project_key,
                "issue_id": str(debug_state.get("latest_run_id") or "runtime-feed"),
                "reason_code": "runtime_feed_only",
                "issue_status": "observed",
                "materialization_state": "runtime_feed_only",
                "delivery_relevance": "current_delivery",
                "latest_event_at": "",
                "sample": "debug runtime feed observed without materialized issue",
                "suggested_capability": "beacon-doctor",
                "source_run_id": str(debug_state.get("latest_run_id") or ""),
                "truth_refs": [_safe_relative(index_path, project_root)] if index_path.exists() else [],
            }
        )
    return rows


def _derive_health_status(
    *,
    preflight_status: str,
    blocked: bool,
    debug_state: dict[str, Any],
    git_scopes: list[dict[str, Any]],
    runtime_corroboration: dict[str, Any],
) -> str:
    if preflight_status in {"conflicted", "blocked"}:
        return "blocked"
    if blocked:
        return "blocked"
    if str(debug_state.get("state") or "") == "materialized_issue":
        return "warn"
    if any(bool(scope.get("dirty")) for scope in git_scopes):
        return "warn"
    if str(runtime_corroboration.get("status") or "") == "missing":
        return "degraded"
    return "healthy"


def _collect_health_snapshots(
    *,
    project_key: str,
    preflight_status: str,
    blocked: bool,
    debug_state: dict[str, Any],
    git_scopes: list[dict[str, Any]],
    runtime_corroboration: dict[str, Any],
    runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    status = _derive_health_status(
        preflight_status=preflight_status,
        blocked=blocked,
        debug_state=debug_state,
        git_scopes=git_scopes,
        runtime_corroboration=runtime_corroboration,
    )
    stale_runs = len([row for row in runs if str(row.get("status") or "") in {"stale", "timeout", "waiting_for_handoff"}])
    blocked_runs = len([row for row in runs if str(row.get("status") or "") in {"blocked", "failed", "human_blocked"}])
    failing_scopes = len([scope for scope in git_scopes if bool(scope.get("dirty"))])
    notes: list[str] = []
    if str(debug_state.get("state") or "") == "materialized_issue":
        notes.append("materialized_debug_issue_present")
    elif str(debug_state.get("state") or "") == "historical_learning_only":
        notes.append("historical_debug_issue_present")
    if str(runtime_corroboration.get("status") or "") == "missing":
        notes.append("runtime_corroboration_missing")
    return [
        {
            "project_key": project_key,
            "snapshot_at": "",
            "overall_status": status,
            "stale_runs": stale_runs,
            "blocked_runs": blocked_runs,
            "failing_scopes": failing_scopes,
            "sync_status": preflight_status,
            "notes": notes,
        }
    ]


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
    qa_sessions = list_qa_sessions(root)
    implement_state = _latest_implement_state(root, docs_version=resolved_version, feature=primary_feature)
    team_hud_payload = _load_team_hud_payload(root, help_payload)
    ralph_state = help_payload.get("ralph") if isinstance(help_payload.get("ralph"), dict) else {}

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
        "qa_status": load_qa_status(root),
        "qa_session_id": str(current_session.get("session_id") or ""),
        "implement_state": {
            "run_id": str(implement_state.get("run_id") or ""),
            "status": str(implement_state.get("status") or ""),
            "host_runtime": str(implement_state.get("host_runtime") or ""),
        },
        "team_hud": {
            "team_name": str(team_hud_payload.get("team_name") or ""),
            "run_id": str(team_hud_payload.get("run_id") or ""),
            "role_count": len(team_hud_payload.get("roles", []) if isinstance(team_hud_payload.get("roles"), list) else []),
        },
        "ralph": {
            "phase": str(ralph_state.get("phase") or ""),
            "active_run_id": str(ralph_state.get("active_run_id") or ""),
            "round_count": int(ralph_state.get("round_count", 0) or 0),
        },
    }
    source_hash = _stable_hash(source_snapshot)
    projection_seq = f"ps-{source_hash[:16]}"

    conflicts: list[str] = []
    warnings: list[str] = []
    if project_kind == "multi_repo_workspace" and not git_scopes:
        conflicts.append("workspace_without_git_scopes")
    if runtime_mode in {"team", "ralph"} and not (
        team_hud_payload
        or str(ralph_state.get("phase") or "").strip()
        or str(current_session.get("session_id") or "").strip()
    ):
        warnings.append("runtime_mode_without_runtime_refs")
    if any(not str(scope.get("branch") or "").strip() for scope in git_scopes):
        warnings.append("git_scope_missing_branch")

    preflight_status = "conflicted" if conflicts else "partial" if warnings else "pass"
    uncertainty_reason = conflicts[0] if conflicts else warnings[0] if warnings else ""
    project_key = _project_key(root)
    truth_refs = {
        "docs_root": str(root / "docs" / "beacon" / resolved_version),
        "state_root": str(root / ".beacon"),
    }
    package_key = _package_key(project_key, resolved_version, primary_feature)

    runs = _collect_runs(
        root,
        docs_version=resolved_version,
        feature=primary_feature,
        runtime_mode=runtime_mode,
        help_payload=help_payload,
        current_session=current_session,
        implement_state=implement_state,
        team_hud_payload=team_hud_payload,
        ralph_state=ralph_state,
    )
    active_run_id = str(runs[0].get("run_id") or "") if runs else ""
    run_workers = _collect_run_workers(active_run_id=active_run_id, team_hud_payload=team_hud_payload)
    run_targets = _collect_run_targets(runs=runs, git_scopes=git_scopes)
    run_events = _collect_run_events(root, runs=runs, ralph_state=ralph_state, debug_state=debug_state)
    artifact_refs = _collect_artifact_refs(
        root,
        docs_version=resolved_version,
        feature=primary_feature,
        help_payload=help_payload,
        team_hud_payload=team_hud_payload,
        runs=runs,
        current_session=current_session,
        debug_state=debug_state,
    )
    git_workspace_bindings = _collect_git_workspace_bindings(
        project_key=project_key,
        package_key=package_key,
        git_scopes=git_scopes,
    )
    host_sessions = _collect_host_sessions(
        root,
        project_key=project_key,
        feature=primary_feature,
        current_session=current_session,
        qa_sessions=qa_sessions,
        help_payload=help_payload,
        runs=runs,
    )
    active_run_ids = {
        str(active_run_id or "").strip(),
        str(debug_state.get("latest_run_id") or "").strip(),
        *(str(row.get("run_id") or "").strip() for row in runs if str(row.get("run_id") or "").strip()),
    }
    active_run_ids.discard("")
    debug_issues = _collect_debug_issues(
        root,
        project_key=project_key,
        debug_state=debug_state,
        docs_version=resolved_version,
        feature=primary_feature,
        active_run_ids=active_run_ids,
    )
    effective_debug_state = _effective_debug_state(debug_issues, debug_state)
    health_snapshots = _collect_health_snapshots(
        project_key=project_key,
        preflight_status=preflight_status,
        blocked=bool(help_payload.get("blocked", False)),
        debug_state=effective_debug_state,
        git_scopes=git_scopes,
        runtime_corroboration=runtime_corroboration,
        runs=runs,
    )

    feature_packages = _collect_feature_packages(
        root,
        project_key=project_key,
        docs_version=resolved_version,
        feature=primary_feature,
        materials=materials,
    )
    feature_lifecycle = _collect_feature_lifecycle(
        project_key=project_key,
        package_key=package_key,
        feature=primary_feature,
        help_payload=help_payload,
        materials=materials,
        runtime_mode=runtime_mode,
        debug_state=effective_debug_state,
        truth_refs=truth_refs,
    )
    stage_material_status = _collect_stage_material_status(
        root,
        project_key=project_key,
        package_key=package_key,
        docs_version=resolved_version,
        feature=primary_feature,
        materials=materials,
    )
    health_status = str(health_snapshots[0].get("overall_status") or "healthy") if health_snapshots else "healthy"
    active_statuses = {"active", "running", "blocked", "failed", "waiting_for_handoff", "human_blocked"}

    envelope = {
        "schema_version": "1.1",
        "project_key": project_key,
        "display_name": root.name,
        "workspace_root": str(root),
        "project_root": str(root),
        "docs_version": resolved_version,
        "docs_root": truth_refs["docs_root"],
        "state_root": truth_refs["state_root"],
        "beacon_runtime_version": __toolkit_version__,
        "feature": primary_feature,
        "package_key": package_key,
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
            "run_count": len(runs),
            "worker_count": len(run_workers),
            "host_session_count": len(host_sessions),
        },
        "debug": effective_debug_state,
        "git_scopes": git_scopes,
        "sessions": {
            "qa_session_id": str(current_session.get("session_id") or ""),
            "qa_runner_type": str(current_session.get("runner_type") or ""),
        },
        "feature_packages": feature_packages,
        "feature_lifecycle": feature_lifecycle,
        "stage_material_status": stage_material_status,
        "runs": runs,
        "run_workers": run_workers,
        "run_targets": run_targets,
        "run_events": run_events,
        "artifact_refs": artifact_refs,
        "git_workspace_bindings": git_workspace_bindings,
        "host_sessions": host_sessions,
        "health_snapshots": health_snapshots,
        "debug_issues": debug_issues,
        "projection": {
            "source_hash": source_hash,
            "projection_seq": projection_seq,
            "projection_version": "v1.3.4-runtime-ledger",
            "truth_refs": truth_refs,
            "preflight_status": preflight_status,
            "confidence": 1.0 if not conflicts and not warnings else 0.8 if warnings and not conflicts else 0.55,
            "uncertainty_reason": uncertainty_reason,
            "preflight": {
                "status": preflight_status,
                "conflicts": conflicts,
                "warnings": warnings,
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
            "debug_state": str(effective_debug_state.get("state") or "no_debug_feed"),
            "runtime_corroboration": str(runtime_corroboration.get("status") or "missing"),
            "health_status": health_status,
            "active_runs": len([row for row in runs if str(row.get("status") or "").strip() in active_statuses]),
            "active_agents": len(run_workers),
        },
    }
    return envelope
