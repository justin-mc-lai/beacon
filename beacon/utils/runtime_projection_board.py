"""Generate the public Beacon management board from runtime projection mirrors."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PAGES = (
    "portfolio-overview",
    "project-detail",
    "runtime-center",
    "recovery-diagnostics",
)

PAGE_META = {
    "board-home": {
        "nav": "首页",
        "headline": "Beacon 管理看板",
        "title": "首页",
        "description": "面向一人公司 CEO 与项目负责人的多项目管理首页，先看推进、阻塞、交付与是否需要介入。",
    },
    "portfolio-overview": {
        "nav": "管理总览",
        "headline": "Beacon 管理看板",
        "title": "管理总览",
        "description": "跨项目查看需求、实现、验收、运行态与阻塞项。正式真相仍以 docs/beacon 与 .beacon 为准。",
    },
    "project-detail": {
        "nav": "项目详情",
        "headline": "项目详情",
        "title": "项目详情",
        "description": "查看项目当前版本、需求物料完整度、Git / Worktree 约束，以及下一步应进入的 Beacon 生命周期动作。",
    },
    "runtime-center": {
        "nav": "运行中心",
        "headline": "运行中心",
        "title": "运行中心",
        "description": "查看 single / team / ralph 等运行态摘要，只暴露必要结论，不展开机器噪音洪流。",
    },
    "recovery-diagnostics": {
        "nav": "恢复诊断",
        "headline": "恢复诊断",
        "title": "恢复诊断",
        "description": "当 SQLite / PocketBase 降级时，确认如何从 docs/beacon 与 .beacon 重建最小可用看板状态。",
    },
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _trim(value: Any, *, limit: int = 220) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _recommended_skill(action: Any, command: Any, *, blocked: bool = False) -> str:
    command_text = str(command or "").strip()
    if "beacon-" in command_text:
        token = command_text.split("beacon-", 1)[1].split()[0].strip()
        if token:
            return f"beacon-{token}"

    action_text = str(action or "").strip().lower().replace("_", "-")
    mapping = {
        "prd": "beacon-prd",
        "requirements": "beacon-prd",
        "user-story": "beacon-user-story",
        "story": "beacon-user-story",
        "test-case": "beacon-test-case",
        "qa": "beacon-qa",
        "qa-run": "beacon-qa",
        "qa-evolve": "beacon-qa",
        "verify": "beacon-qa",
        "implement": "beacon-implement",
        "release": "beacon-release",
        "release-check": "beacon-release",
        "doctor": "beacon-doctor",
        "rebuild": "beacon-doctor",
        "recover": "beacon-doctor",
        "takeover-baseline": "beacon-doctor",
    }
    if action_text in mapping:
        return mapping[action_text]
    if blocked:
        return "beacon-doctor"
    return ""


def _status_tone(value: str) -> str:
    text = str(value or "").strip().lower()
    if text in {"ready", "healthy", "pass", "ok", "release-ready", "available"}:
        return "good"
    if text in {"blocked", "fail", "degraded", "warn", "materialized_issue"}:
        return "bad"
    if text in {"qa-run", "qa-evolve", "release-check"}:
        return "warn"
    return "neutral"


def _project_card(payload: dict[str, Any]) -> dict[str, Any]:
    lifecycle = payload.get("lifecycle") if isinstance(payload.get("lifecycle"), dict) else {}
    materials = payload.get("materials") if isinstance(payload.get("materials"), dict) else {}
    runtime = payload.get("runtime") if isinstance(payload.get("runtime"), dict) else {}
    debug = payload.get("debug") if isinstance(payload.get("debug"), dict) else {}
    board = payload.get("board") if isinstance(payload.get("board"), dict) else {}
    next_step = lifecycle.get("next_step") if isinstance(lifecycle.get("next_step"), dict) else {}
    execution_surface = runtime.get("execution_surface") if isinstance(runtime.get("execution_surface"), dict) else {}
    blocked = bool(lifecycle.get("blocked"))
    stage = str(lifecycle.get("stage") or board.get("current_stage") or lifecycle.get("current_stage") or "")
    stage_detail = str(lifecycle.get("current_stage") or board.get("stage_detail") or "")
    next_action = str(next_step.get("action") or board.get("next_action") or "")
    next_command = str(next_step.get("command") or "")

    return {
        "project_key": str(payload.get("project_key") or ""),
        "display_name": str(payload.get("display_name") or ""),
        "docs_version": str(payload.get("docs_version") or ""),
        "project_kind": str(payload.get("project_kind") or ""),
        "feature": str(payload.get("feature") or ""),
        "current_stage": stage,
        "stage_detail": stage_detail if stage_detail and stage_detail != stage else "",
        "progress_label": str(lifecycle.get("progress_label") or board.get("progress_label") or ""),
        "blocked": blocked,
        "blocked_reason": _trim(lifecycle.get("blocked_reason") or board.get("blocker") or "", limit=160),
        "next_action": next_action,
        "next_reason": _trim(next_step.get("reason") or "", limit=180),
        "recommended_skill": _recommended_skill(next_action, next_command, blocked=blocked),
        "recommended_command": next_command,
        "runtime_mode": str(runtime.get("mode") or ""),
        "runtime_surface": str(execution_surface.get("selected_surface") or ""),
        "runtime_corroboration": str((runtime.get("runtime_corroboration") or {}).get("status") or board.get("runtime_corroboration") or ""),
        "health_status": str(board.get("health_status") or ""),
        "debug_state": str(debug.get("state") or board.get("debug_state") or ""),
        "debug_issue_count": int(debug.get("issue_count", 0) or 0),
        "run_count": int(runtime.get("run_count", 0) or 0),
        "worker_count": int(runtime.get("worker_count", 0) or 0),
        "host_session_count": int(runtime.get("host_session_count", 0) or 0),
        "materials": {
            "prd": str(materials.get("prd") or ""),
            "user_story": str(materials.get("user_story") or ""),
            "test_case": str(materials.get("test_case") or ""),
        },
    }


def _git_scope_card(scope: dict[str, Any]) -> dict[str, Any]:
    worktree_path = str(scope.get("worktree_path") or "").strip()
    return {
        "repo_name": str(scope.get("repo_name") or ""),
        "role": str(scope.get("role") or ""),
        "branch": str(scope.get("branch") or ""),
        "dirty": bool(scope.get("dirty")),
        "worktree_name": Path(worktree_path).name if worktree_path else "",
        "source_priority": str(scope.get("source_priority") or ""),
    }


def _package_card(item: dict[str, Any]) -> dict[str, Any]:
    materials = item.get("materials") if isinstance(item.get("materials"), dict) else {}
    return {
        "feature": str(item.get("feature") or ""),
        "feature_slug": str(item.get("feature_slug") or ""),
        "docs_version": str(item.get("docs_version") or ""),
        "materials": {
            "prd": str(materials.get("prd") or ""),
            "user_story": str(materials.get("user_story") or ""),
            "test_case": str(materials.get("test_case") or ""),
        },
    }


def _lifecycle_card(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "feature": str(item.get("feature") or ""),
        "current_stage": str(item.get("current_stage") or ""),
        "progress_label": str(item.get("progress_label") or ""),
        "blocked": bool(item.get("blocked")),
        "blocked_reason": _trim(item.get("blocked_reason") or "", limit=160),
        "next_action": str(item.get("next_action") or ""),
        "runtime_mode": str(item.get("runtime_mode") or ""),
        "debug_state": str(item.get("debug_state") or ""),
    }


def _run_card(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": str(item.get("run_id") or ""),
        "feature": str(item.get("feature") or ""),
        "docs_version": str(item.get("docs_version") or ""),
        "mode": str(item.get("mode") or ""),
        "status": str(item.get("status") or ""),
        "started_at": str(item.get("started_at") or ""),
        "ended_at": str(item.get("ended_at") or ""),
        "source": str(item.get("source") or ""),
    }


def _worker_card(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": str(item.get("run_id") or ""),
        "worker_id": str(item.get("worker_id") or ""),
        "role": str(item.get("role") or ""),
        "status": str(item.get("status") or ""),
        "tmux_session": str(item.get("tmux_session") or ""),
        "pane_id": str(item.get("pane_id") or ""),
    }


def _debug_card(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "issue_id": str(item.get("issue_id") or ""),
        "reason_code": str(item.get("reason_code") or ""),
        "issue_status": str(item.get("issue_status") or ""),
        "materialization_state": str(item.get("materialization_state") or ""),
        "suggested_capability": str(item.get("suggested_capability") or ""),
        "sample": _trim(item.get("sample") or "", limit=200),
    }


def _health_card(item: dict[str, Any]) -> dict[str, Any]:
    notes = item.get("notes")
    return {
        "snapshot_at": str(item.get("snapshot_at") or ""),
        "overall_status": str(item.get("overall_status") or ""),
        "stale_runs": int(item.get("stale_runs", 0) or 0),
        "blocked_runs": int(item.get("blocked_runs", 0) or 0),
        "failing_scopes": int(item.get("failing_scopes", 0) or 0),
        "sync_status": str(item.get("sync_status") or ""),
        "notes": [str(note) for note in notes] if isinstance(notes, list) else [],
    }


def _session_card(item: dict[str, Any]) -> dict[str, Any]:
    transcript_path = str(item.get("transcript_path") or "")
    transcript_ref = transcript_path if transcript_path and not transcript_path.startswith("/") else Path(transcript_path).name
    return {
        "feature": str(item.get("feature") or ""),
        "run_id": str(item.get("run_id") or ""),
        "host_runtime": str(item.get("host_runtime") or ""),
        "session_id": str(item.get("session_id") or ""),
        "thread_id": str(item.get("thread_id") or ""),
        "turn_id": str(item.get("turn_id") or ""),
        "transcript_ref": transcript_ref,
        "status": str(item.get("status") or ""),
        "started_at": str(item.get("started_at") or ""),
        "ended_at": str(item.get("ended_at") or ""),
    }


def _document_key(relative_path: str) -> str:
    text = str(relative_path or "").strip()
    if not text:
        return ""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]  # noqa: S324


def _document_section(relative_path: str) -> str:
    path = Path(relative_path)
    parts = path.parts
    if path.name == "SUMMARY.md":
        return "版本摘要"
    if parts and parts[0] == "execution":
        return "执行蓝图"
    if parts and parts[0] == "prd":
        return "PRD"
    if parts and parts[0] == "user-story":
        return "用户故事"
    if len(parts) >= 2 and parts[0] == "qa" and parts[1] == "test-cases":
        return "测试用例"
    return "其他资料"


def _document_title(content: str, path: Path) -> str:
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            return line.lstrip("#").strip() or path.stem
        return _trim(line, limit=80)
    return path.stem


def _document_excerpt(content: str) -> str:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return ""
    if lines[0].startswith("#"):
        lines = lines[1:]
    return _trim(" ".join(lines[:4]), limit=180)


def _collect_project_documents(project_payload: dict[str, Any]) -> list[dict[str, Any]]:
    docs_root_value = str(project_payload.get("docs_root") or "").strip()
    project_root_value = str(project_payload.get("project_root") or "").strip()
    if not docs_root_value or not project_root_value:
        return []

    docs_root = Path(docs_root_value).expanduser()
    project_root = Path(project_root_value).expanduser()
    if not docs_root.exists() or not docs_root.is_dir():
        return []

    ordered_paths: list[Path] = []
    seen: set[str] = set()

    def append(path: Path) -> None:
        if not path.exists() or not path.is_file():
            return
        try:
            relative = str(path.relative_to(docs_root))
        except Exception:  # noqa: BLE001
            return
        if relative in seen:
            return
        seen.add(relative)
        ordered_paths.append(path)

    for path in (
        docs_root / "SUMMARY.md",
        docs_root / "execution" / "index.md",
        docs_root / "execution" / "architecture-blueprint.md",
    ):
        append(path)

    for folder in (
        docs_root / "execution",
        docs_root / "prd",
        docs_root / "user-story",
        docs_root / "qa" / "test-cases",
    ):
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*.md")):
            append(path)

    documents: list[dict[str, Any]] = []
    for path in ordered_paths:
        try:
            relative_path = str(path.relative_to(docs_root))
        except Exception:  # noqa: BLE001
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        documents.append(
            {
                "doc_key": _document_key(relative_path),
                "relative_path": relative_path,
                "section": _document_section(relative_path),
                "title": _document_title(content, path),
                "excerpt": _document_excerpt(content),
                "line_count": len(content.splitlines()),
                "project_ref": str(path.relative_to(project_root)) if path.is_relative_to(project_root) else relative_path,
            }
        )
    return documents


def _detail_view(project_payload: dict[str, Any], collections_root: Path) -> dict[str, Any]:
    project_key = str(project_payload.get("project_key") or "")
    runtime = project_payload.get("runtime") if isinstance(project_payload.get("runtime"), dict) else {}
    execution_surface = runtime.get("execution_surface") if isinstance(runtime.get("execution_surface"), dict) else {}
    detail = {
        "project": _project_card(project_payload),
        "truth": {
            "source_of_truth": str((project_payload.get("truth") or {}).get("source_of_truth") or "docs/beacon + .beacon"),
            "docs_version": str(project_payload.get("docs_version") or ""),
            "beacon_runtime_version": str(project_payload.get("beacon_runtime_version") or ""),
        },
        "runtime": {
            "mode": str(runtime.get("mode") or ""),
            "run_count": int(runtime.get("run_count", 0) or 0),
            "worker_count": int(runtime.get("worker_count", 0) or 0),
            "host_session_count": int(runtime.get("host_session_count", 0) or 0),
            "runtime_corroboration": dict(runtime.get("runtime_corroboration") or {}),
            "execution_surface": {
                "project_mode": str(execution_surface.get("project_mode") or ""),
                "profile_id": str(execution_surface.get("profile_id") or ""),
                "selected_surface": str(execution_surface.get("selected_surface") or ""),
                "host_runtime": str(execution_surface.get("host_runtime") or ""),
                "implement_mode": str(execution_surface.get("implement_mode") or ""),
                "qa_execution_mode": str(execution_surface.get("qa_execution_mode") or ""),
                "ralph_phase": str(execution_surface.get("ralph_phase") or ""),
                "ralph_next_action": str(execution_surface.get("ralph_next_action") or ""),
                "ralph_round_count": int(execution_surface.get("ralph_round_count", 0) or 0),
                "ralph_failure_streak": int(execution_surface.get("ralph_failure_streak", 0) or 0),
                "subagent_runtime_status": str(execution_surface.get("subagent_runtime_status") or ""),
                "subagent_delegation_status": str(execution_surface.get("subagent_delegation_status") or ""),
                "takeover_gate": dict(execution_surface.get("takeover_gate") or {}),
            },
        },
        "git_scopes": [_git_scope_card(item) for item in project_payload.get("git_scopes", []) if isinstance(item, dict)],
        "feature_packages": [],
        "feature_lifecycle": [],
        "runs": [],
        "run_workers": [],
        "debug_issues": [],
        "health_snapshots": [],
        "host_sessions": [],
        "documents": _collect_project_documents(project_payload),
    }

    loaders = {
        "feature_packages": _package_card,
        "feature_lifecycle": _lifecycle_card,
        "runs": _run_card,
        "run_workers": _worker_card,
        "debug_issues": _debug_card,
        "health_snapshots": _health_card,
        "host_sessions": _session_card,
    }
    for collection, mapper in loaders.items():
        payload = _read_json(collections_root / collection / f"{project_key}.json")
        rows = payload.get("rows")
        detail[collection] = [mapper(item) for item in rows if isinstance(rows, list) and isinstance(item, dict)]

    detail["runs"] = detail["runs"][:12]
    detail["run_workers"] = detail["run_workers"][:20]
    detail["debug_issues"] = detail["debug_issues"][:12]
    detail["health_snapshots"] = detail["health_snapshots"][:12]
    detail["host_sessions"] = detail["host_sessions"][:12]
    return detail


def _portfolio_view(project_payloads: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    projects = [_project_card(item) for item in project_payloads]
    blocked_count = sum(1 for item in projects if item["blocked"])
    debug_issue_count = sum(int(item.get("debug_issue_count", 0) or 0) for item in projects)
    runtime_active_count = sum(1 for item in projects if item.get("run_count", 0) or item.get("worker_count", 0))
    healthy_count = sum(1 for item in projects if _status_tone(str(item.get("health_status") or "")) == "good")
    warning_count = sum(1 for item in projects if _status_tone(str(item.get("health_status") or "")) != "good")
    return {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "summary": {
            "project_count": len(projects),
            "blocked_count": blocked_count,
            "runtime_active_count": runtime_active_count,
            "debug_issue_count": debug_issue_count,
            "healthy_count": healthy_count,
            "warning_count": warning_count,
        },
        "projects": projects,
    }


def _board_css() -> str:
    return """
:root {
  color-scheme: dark;
  --bg: #09090b;
  --bg-soft: #111113;
  --panel: #111113;
  --panel-soft: #151518;
  --panel-elev: #18181b;
  --ink: #fafafa;
  --muted: #a1a1aa;
  --line: #27272a;
  --line-strong: #3f3f46;
  --focus: #60a5fa;
  --good-bg: #f5f5f5;
  --good-text: #09090b;
  --warn-bg: rgba(245, 158, 11, 0.16);
  --warn-text: #fbbf24;
  --bad-bg: rgba(239, 68, 68, 0.14);
  --bad-text: #fda4af;
  --neutral-bg: #18181b;
  --neutral-text: #d4d4d8;
  --shadow-border: inset 0 0 0 1px rgba(255, 255, 255, 0.04);
  --shadow-card: inset 0 0 0 1px rgba(255, 255, 255, 0.04), 0 24px 80px -48px rgba(0, 0, 0, 0.95);
}

* { box-sizing: border-box; }
html, body { min-height: 100%; }
body {
  margin: 0;
  font-family: "Geist", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.04), transparent 0, transparent 28%),
    radial-gradient(circle at top center, rgba(99, 102, 241, 0.08), transparent 0, transparent 22%),
    linear-gradient(180deg, #09090b 0%, #09090b 100%);
  color: var(--ink);
}
a { color: inherit; }
.app-shell {
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
  min-height: 100vh;
}
.sidebar {
  position: sticky;
  top: 0;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 100vh;
  padding: 22px 18px;
  border-right: 1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0) 100%),
    rgba(9, 9, 11, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.brand-block {
  display: grid;
  gap: 10px;
}
.brand-kicker,
.sidebar-label,
.eyebrow {
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  color: var(--muted);
  font-family: "Geist Mono", "SFMono-Regular", monospace;
}
.brand-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--line-strong);
  background: linear-gradient(180deg, #1a1a1d 0%, #0c0c0e 100%);
  font-family: "Geist Mono", "SFMono-Regular", monospace;
  font-size: 0.95rem;
  letter-spacing: -0.05em;
}
.brand-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: -0.04em;
}
.brand-copy,
.sidebar-note,
.section-desc,
.subtle,
.attention-card p,
.role-card p,
.lane-card p,
.project-mainline,
.registry-meta,
.doc-meta {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}
.sidebar-section {
  display: grid;
  gap: 10px;
}
.sidebar-note {
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.02);
  font-size: 0.9rem;
}
.nav-tabs,
.summary-grid,
.chips,
.section-grid,
.project-actions,
.topbar-meta,
.registry-actions,
.metric-strip,
.attention-grid,
.stack,
.list,
.project-list,
.role-grid,
.doc-layout {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.nav-tabs {
  flex-direction: column;
  gap: 6px;
}
.nav-link, .chip, .pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  text-decoration: none;
  font-size: 0.82rem;
  font-weight: 500;
}
.nav-link {
  border-radius: 12px;
  border: 1px solid transparent;
  color: #d4d4d8;
  background: transparent;
  transition: transform 180ms ease, background 180ms ease, border-color 180ms ease, color 180ms ease;
}
.nav-link.active {
  background: #f5f5f5;
  color: #09090b;
  border-color: #f5f5f5;
  box-shadow: none;
}
.nav-link:hover {
  transform: translateY(-1px);
  color: var(--ink);
  background: rgba(255, 255, 255, 0.03);
  border-color: var(--line);
}
.chip, .pill {
  border: 1px solid var(--line);
  background: var(--neutral-bg);
  color: var(--neutral-text);
}
.chip.good, .pill.good { background: var(--good-bg); color: var(--good-text); }
.chip.warn, .pill.warn { background: var(--warn-bg); color: var(--warn-text); }
.chip.bad, .pill.bad { background: var(--bad-bg); color: var(--bad-text); }
.chip.neutral, .pill.neutral { background: var(--neutral-bg); color: var(--neutral-text); }
.workspace {
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  padding: 20px 24px 18px;
  border-bottom: 1px solid var(--line);
  background: rgba(9, 9, 11, 0.86);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.topbar-kicker {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-family: "Geist Mono", "SFMono-Regular", monospace;
}
.topbar-title {
  margin: 0;
  font-size: clamp(1.7rem, 3vw, 2.4rem);
  line-height: 1.02;
  letter-spacing: -0.08em;
}
.topbar-desc {
  margin: 10px 0 0;
  max-width: 68ch;
  color: var(--muted);
  font-size: 0.96rem;
  line-height: 1.65;
}
.shell {
  width: 100%;
  max-width: 1480px;
  margin: 0 auto;
  padding: 24px;
}
.summary-grid,
.section-grid,
.project-layout,
.doc-layout,
.project-list,
.list,
.stack,
.attention-grid,
.role-grid,
.metric-strip {
  display: grid;
  gap: 12px;
}
.summary-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.metric-strip {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.85fr);
  gap: 12px;
}
.summary-card, .panel, .project-card, .lane-card, .attention-card, .role-card, .doc-viewer {
  background: linear-gradient(180deg, #121214 0%, #0d0d10 100%);
  border: 1px solid var(--line);
  border-radius: 18px;
  box-shadow: var(--shadow-card);
}
.summary-card {
  min-width: 0;
  padding: 18px;
}
.summary-card h2, .panel h2, .panel h3 {
  margin: 0 0 10px;
  font-weight: 600;
  letter-spacing: -0.04em;
  font-size: 1.1rem;
}
.metric {
  font-size: 2.15rem;
  font-weight: 600;
  letter-spacing: -0.08em;
}
.panel {
  padding: 20px;
}
.group-title {
  margin: 0 0 12px;
  font-size: 1.15rem;
  letter-spacing: -0.04em;
  font-weight: 600;
}
.lane-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
.lane-card {
  padding: 18px;
}
.lane-card strong {
  display: block;
  margin-top: 12px;
  font-size: 2rem;
  letter-spacing: -0.08em;
}
.attention-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.attention-card {
  padding: 18px;
}
.attention-card h3 {
  margin: 0 0 8px;
  font-size: 1.02rem;
  letter-spacing: -0.04em;
}
.role-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.role-card {
  padding: 18px;
}
.role-card h3 {
  margin: 8px 0 6px;
  font-size: 1.02rem;
  letter-spacing: -0.04em;
}
.role-metric {
  margin-top: 10px;
  font-size: 1.8rem;
  font-weight: 600;
  letter-spacing: -0.08em;
}
.section-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: flex-start;
}
.section-title {
  margin: 0 0 6px;
  font-size: 1.45rem;
  font-weight: 600;
  letter-spacing: -0.06em;
}
.project-card {
  padding: 18px;
}
.project-card header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}
.project-grid {
  grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr);
  gap: 12px;
}
.title {
  font-size: 1.18rem;
  font-weight: 600;
  letter-spacing: -0.06em;
}
.kv {
  display: grid;
  grid-template-columns: 138px minmax(0, 1fr);
  gap: 10px 18px;
  font-size: 0.95rem;
}
.kv div:nth-child(odd) {
  color: var(--muted);
  font-family: "Geist Mono", "SFMono-Regular", monospace;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.registry-table {
  display: grid;
  gap: 10px;
}
.registry-head,
.registry-row {
  display: grid;
  grid-template-columns: minmax(220px, 1.35fr) minmax(120px, 0.72fr) minmax(170px, 0.95fr) minmax(160px, 0.85fr) minmax(180px, 1fr) minmax(146px, 0.78fr);
  gap: 12px;
  align-items: start;
}
.registry-head {
  padding: 0 14px;
  color: var(--muted);
  font-family: "Geist Mono", "SFMono-Regular", monospace;
  font-size: 0.74rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.registry-row {
  padding: 15px 14px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: linear-gradient(180deg, #141417 0%, #0f0f12 100%);
}
.registry-cell {
  min-width: 0;
}
.registry-cell strong {
  display: block;
  margin: 0;
  font-size: 0.98rem;
  letter-spacing: -0.03em;
}
.registry-actions {
  display: grid;
  gap: 8px;
}
.list-item {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: var(--panel-soft);
  box-shadow: var(--shadow-border);
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
select {
  min-width: 240px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: var(--panel-soft);
  color: var(--ink);
  font: inherit;
  box-shadow: none;
}
select:focus {
  outline: 2px solid var(--focus);
  outline-offset: 2px;
}
.action-link {
  text-decoration: none;
  color: var(--ink);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: var(--panel-soft);
  transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
}
.action-link:hover {
  transform: translateY(-1px);
  border-color: var(--line-strong);
  background: var(--panel-elev);
}
.doc-layout {
  grid-template-columns: minmax(300px, 0.9fr) minmax(0, 1.5fr);
}
.doc-list {
  display: grid;
  gap: 10px;
}
.doc-link {
  display: block;
  padding: 14px 16px;
  border-radius: 14px;
  background: var(--panel-soft);
  border: 1px solid var(--line);
  text-decoration: none;
}
.doc-link.active {
  background: #f5f5f5;
  color: #09090b;
  border-color: #f5f5f5;
}
.doc-link strong {
  display: block;
  margin-top: 4px;
  font-size: 0.98rem;
  letter-spacing: -0.03em;
}
.doc-link small {
  display: block;
  margin-top: 8px;
  color: var(--muted);
  line-height: 1.5;
}
.doc-viewer {
  min-height: 360px;
  padding: 20px;
}
.markdown {
  color: var(--ink);
  line-height: 1.75;
  font-size: 0.98rem;
}
.markdown h1, .markdown h2, .markdown h3 {
  margin: 22px 0 10px;
  letter-spacing: -0.05em;
}
.markdown h1 { font-size: 1.9rem; }
.markdown h2 { font-size: 1.35rem; }
.markdown h3 { font-size: 1.08rem; }
.markdown p, .markdown ul, .markdown ol, .markdown blockquote, .markdown pre {
  margin: 0 0 14px;
}
.markdown ul, .markdown ol {
  padding-left: 20px;
}
.markdown code {
  padding: 0.12rem 0.32rem;
  border-radius: 8px;
  background: #1a1a1d;
  border: 1px solid var(--line);
  font-family: "Geist Mono", "SFMono-Regular", monospace;
  font-size: 0.92em;
}
.markdown pre {
  overflow-x: auto;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: #050506;
  color: #f5f5f5;
}
.markdown pre code {
  padding: 0;
  background: transparent;
  border: 0;
  color: inherit;
}
.markdown blockquote {
  padding-left: 14px;
  border-left: 3px solid var(--line);
  color: var(--muted);
}
.empty {
  padding: 24px;
  border-radius: 16px;
  color: var(--muted);
  border: 1px dashed var(--line-strong);
  background: rgba(255, 255, 255, 0.02);
}
@media (max-width: 1200px) {
  .summary-grid,
  .metric-strip,
  .lane-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .dashboard-grid,
  .section-grid,
  .doc-layout,
  .project-grid,
  .attention-grid,
  .role-grid {
    grid-template-columns: 1fr;
  }
  .registry-head,
  .registry-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 860px) {
  .app-shell {
    grid-template-columns: 1fr;
  }
  .sidebar {
    position: static;
    min-height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }
  .topbar {
    position: static;
    padding: 18px 14px;
  }
  .shell {
    padding: 18px 14px 32px;
  }
  .summary-grid,
  .metric-strip,
  .lane-grid,
  .attention-grid,
  .role-grid,
  .section-grid,
  .doc-layout,
  .project-grid,
  .registry-row {
    grid-template-columns: 1fr;
  }
  .registry-head {
    display: none;
  }
  .kv {
    grid-template-columns: 1fr;
  }
  select {
    width: 100%;
    min-width: 0;
  }
}
""".strip() + "\n"


def _board_js() -> str:
    return """
const PAGE = document.body.dataset.page || "portfolio-overview";
const PAGE_META = {
  "board-home": { nav: "首页" },
  "portfolio-overview": { nav: "管理总览" },
  "project-detail": { nav: "项目详情" },
  "runtime-center": { nav: "运行中心" },
  "recovery-diagnostics": { nav: "恢复诊断" },
};

const I18N = {
  stage: {
    requirements: "需求阶段",
    implement: "实现阶段",
    qa: "验收阶段",
    release: "发布阶段",
    think: "需求研判",
    draft: "草稿中",
    verified: "已验证",
    frozen: "已冻结",
  },
  runtime: {
    single: "单进程",
    team: "多代理",
    ralph: "Ralph 闭环",
    idle: "空闲",
  },
  projectKind: {
    single_repo: "单仓项目",
    multi_repo_workspace: "多仓工作区",
  },
  debug: {
    materialized_issue: "已物化问题",
    runtime_feed_only: "仅运行反馈",
    no_debug_feed: "无调试流",
  },
  material: {
    missing: "缺失",
    draft: "草稿",
    ready: "就绪",
    frozen: "冻结",
  },
  health: {
    blocked: "阻塞",
    warn: "关注",
    healthy: "健康",
    ready: "就绪",
    degraded: "降级",
    pass: "通过",
  },
  nextAction: {
    "release-check": "进入发布核查",
    "user-story": "补齐用户故事",
    "test-case": "补齐测试用例",
    "takeover-baseline": "补齐接管基线",
    "qa-run": "继续 QA 验证",
    "qa-evolve": "演进 QA 覆盖",
    "implement": "继续实现",
  },
};

async function readJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load ${url}: ${response.status}`);
  }
  return response.json();
}

function qs(name) {
  return new URLSearchParams(window.location.search).get(name) || "";
}

function label(kind, value) {
  const raw = String(value || "");
  return I18N[kind]?.[raw] || raw || "-";
}

function tone(value) {
  const raw = String(value || "").toLowerCase();
  if (["ready", "healthy", "pass", "ok", "available"].includes(raw)) return "good";
  if (["blocked", "warn", "degraded", "fail", "materialized_issue"].includes(raw)) return "bad";
  if (["qa-run", "qa-evolve", "release-check"].includes(raw)) return "warn";
  return "neutral";
}

function chip(text, value) {
  const klass = tone(value || text);
  return `<span class="chip ${klass}">${text}</span>`;
}

function badge(text, href = "") {
  if (href) {
    return `<a class="pill" href="${href}">${text}</a>`;
  }
  return `<span class="pill">${text}</span>`;
}

function pair(labelText, valueText) {
  return `<div>${labelText}</div><div>${valueText || "-"}</div>`;
}

function nav(projectKey) {
  const links = [
    ["board-home", "/"],
    ["portfolio-overview", "/portfolio-overview/"],
    ["project-detail", `/project-detail/?project=${encodeURIComponent(projectKey)}`],
    ["runtime-center", `/runtime-center/?project=${encodeURIComponent(projectKey)}`],
    ["recovery-diagnostics", `/recovery-diagnostics/?project=${encodeURIComponent(projectKey)}`],
  ];
  return links.map(([page, href]) => `<a class="nav-link ${PAGE === page ? "active" : ""}" href="${href}">${PAGE_META[page]?.nav || page}</a>`).join("");
}

function ensure(container, html) {
  container.innerHTML = html;
}

function renderList(title, rows, mapper) {
  if (!rows.length) {
    return `<div class="empty">当前没有${title}。</div>`;
  }
  return `<div class="list">${rows.map(mapper).join("")}</div>`;
}

function sectionHeader(title, desc) {
  return `
    <div>
      <h2 class="section-title">${title}</h2>
      <p class="section-desc">${desc}</p>
    </div>
  `;
}

function projectRegistryRow(project, options = {}) {
  const showMaterials = Boolean(options.showMaterials);
  return `
    <article class="registry-row">
      <div class="registry-cell">
        <strong>${project.display_name}</strong>
        <div class="registry-meta">${label("projectKind", project.project_kind)} · Docs ${project.docs_version || "-"}</div>
        <div class="registry-meta">${project.feature || "暂无记录中的主线 feature"}</div>
      </div>
      <div class="registry-cell">
        <strong>${label("stage", project.current_stage || "requirements")}</strong>
        <div class="registry-meta">${project.progress_label || "暂无阶段摘要"}</div>
        ${project.stage_detail ? `<div class="registry-meta">细分：${label("stage", project.stage_detail)}</div>` : ""}
      </div>
      <div class="registry-cell">
        <strong>${label("nextAction", project.next_action || "-")}</strong>
        <div class="registry-meta">${project.recommended_skill || "待判断"}${project.next_reason ? ` · ${project.next_reason}` : ""}</div>
        ${showMaterials ? `
          <div class="chips" style="margin-top:10px">
            ${chip(`PRD ${label("material", project.materials?.prd)}`, project.materials?.prd)}
            ${chip(`故事 ${label("material", project.materials?.user_story)}`, project.materials?.user_story)}
            ${chip(`用例 ${label("material", project.materials?.test_case)}`, project.materials?.test_case)}
          </div>
        ` : ""}
      </div>
      <div class="registry-cell">
        <strong>${label("runtime", project.runtime_mode || "idle")}</strong>
        <div class="registry-meta">${project.run_count || 0} runs · ${project.worker_count || 0} agents</div>
        <div class="registry-meta">${project.host_session_count || 0} host sessions</div>
      </div>
      <div class="registry-cell">
        <div class="chips">
          ${chip(label("health", project.health_status || "warn"), project.health_status)}
          ${chip(label("debug", project.debug_state || "no_debug_feed"), project.debug_state)}
        </div>
        <div class="registry-meta" style="margin-top:10px">${project.blocked_reason || "当前无 blocker"}</div>
      </div>
      <div class="registry-cell">
        <div class="registry-actions">
          <a class="action-link" href="/project-detail/?project=${encodeURIComponent(project.project_key)}">项目详情</a>
          <a class="action-link" href="/runtime-center/?project=${encodeURIComponent(project.project_key)}">运行中心</a>
        </div>
      </div>
    </article>
  `;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderInline(text) {
  return escapeHtml(text).replace(/`([^`]+)`/g, "<code>$1</code>");
}

function renderMarkdown(markdown) {
  const lines = String(markdown || "").replace(/\\r\\n/g, "\\n").split("\\n");
  const blocks = [];
  let paragraph = [];
  let listItems = [];
  let listTag = "";
  let codeFence = null;
  let codeLines = [];

  function flushParagraph() {
    if (!paragraph.length) return;
    blocks.push(`<p>${renderInline(paragraph.join(" "))}</p>`);
    paragraph = [];
  }

  function flushList() {
    if (!listItems.length) return;
    blocks.push(`<${listTag}>${listItems.join("")}</${listTag}>`);
    listItems = [];
    listTag = "";
  }

  function flushCodeFence() {
    if (codeFence === null) return;
    blocks.push(`<pre><code>${escapeHtml(codeLines.join("\\n"))}</code></pre>`);
    codeFence = null;
    codeLines = [];
  }

  for (const rawLine of lines) {
    const line = rawLine.replace(/\\t/g, "  ");
    const trimmed = line.trim();
    if (trimmed.startsWith("```")) {
      flushParagraph();
      flushList();
      if (codeFence === null) {
        codeFence = trimmed.slice(3).trim() || "text";
      } else {
        flushCodeFence();
      }
      continue;
    }
    if (codeFence !== null) {
      codeLines.push(rawLine);
      continue;
    }
    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }
    const headingMatch = trimmed.match(/^(#{1,3})\\s+(.*)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      const level = headingMatch[1].length;
      blocks.push(`<h${level}>${renderInline(headingMatch[2])}</h${level}>`);
      continue;
    }
    if (trimmed.startsWith("> ")) {
      flushParagraph();
      flushList();
      blocks.push(`<blockquote>${renderInline(trimmed.slice(2))}</blockquote>`);
      continue;
    }
    const orderedMatch = trimmed.match(/^\\d+\\.\\s+(.*)$/);
    if (orderedMatch) {
      flushParagraph();
      if (listTag && listTag !== "ol") flushList();
      listTag = "ol";
      listItems.push(`<li>${renderInline(orderedMatch[1])}</li>`);
      continue;
    }
    const bulletMatch = trimmed.match(/^[-*]\\s+(.*)$/);
    if (bulletMatch) {
      flushParagraph();
      if (listTag && listTag !== "ul") flushList();
      listTag = "ul";
      listItems.push(`<li>${renderInline(bulletMatch[1])}</li>`);
      continue;
    }
    flushList();
    paragraph.push(trimmed);
  }

  flushParagraph();
  flushList();
  flushCodeFence();
  return blocks.join("");
}

function lifecycleBucket(stage) {
  const raw = String(stage || "").toLowerCase();
  if (["requirements", "think", "draft", "verified", "frozen"].includes(raw)) return "requirements";
  if (raw === "implement") return "implement";
  if (raw === "qa") return "qa";
  if (raw === "release") return "release";
  return "requirements";
}

function projectActionHref(page, projectKey) {
  if (page === "board-home") return "/";
  if (page === "portfolio-overview") return "/portfolio-overview/";
  return `/${page}/?project=${encodeURIComponent(projectKey)}`;
}

async function renderBoardHome() {
  const data = await readJson("/data/portfolio-summary.json");
  const summary = data.summary || {};
  const projects = Array.isArray(data.projects) ? data.projects : [];
  const roleCards = [
    {
      eyebrow: "CEO / 经营者",
      title: "只看推进、交付与介入点",
      metric: `${summary.blocked_count || 0}`,
      desc: "把多项目推进、阻塞数量和是否需要你介入压缩成有限判断，不让 runtime 噪音抢前台。",
      href: "/portfolio-overview/",
      action: "打开管理总览",
    },
    {
      eyebrow: "项目负责人",
      title: "看版本线与需求闭环",
      metric: `${projects.length}`,
      desc: "每个项目都要能看到当前版本、主线 feature、PRD / 用户故事 / 测试用例，以及推荐 skill。",
      href: projectActionHref("project-detail", projects[0]?.project_key || ""),
      action: "查看项目详情",
    },
    {
      eyebrow: "运行治理者",
      title: "看 run 是否真的在推进",
      metric: `${summary.runtime_active_count || 0}`,
      desc: "single / team / ralph 只在运行中心展开，判断是否仍在有效实现，而不是只剩机器自说自话。",
      href: projectActionHref("runtime-center", projects[0]?.project_key || ""),
      action: "打开运行中心",
    },
    {
      eyebrow: "恢复维护者",
      title: "看投影异常与重建路径",
      metric: `${summary.debug_issue_count || 0}`,
      desc: "确认问题是在 docs/.beacon 真相层，还是 SQLite / PocketBase 投影层，并给出最小恢复路径。",
      href: projectActionHref("recovery-diagnostics", projects[0]?.project_key || ""),
      action: "查看恢复诊断",
    },
  ];
  const spotlight = projects.filter((project) =>
    project.blocked
    || ["materialized_issue", "degraded"].includes(String(project.debug_state || "").toLowerCase())
    || ["warn", "blocked", "degraded"].includes(String(project.health_status || "").toLowerCase())
  ).slice(0, 3);
  const primaryProject = projects[0]?.project_key || "";
  ensure(document.querySelector("#nav"), nav(primaryProject));
  ensure(document.querySelector("#content"), `
    <section class="metric-strip">
      <article class="summary-card"><h2>受管项目</h2><div class="metric">${summary.project_count || 0}</div><div class="subtle">已进入 Beacon 管理看板的项目数量</div></article>
      <article class="summary-card"><h2>需要介入</h2><div class="metric">${summary.blocked_count || 0}</div><div class="subtle">存在阻塞、漂移或治理缺口，需要人类判断</div></article>
      <article class="summary-card"><h2>活跃运行态</h2><div class="metric">${summary.runtime_active_count || 0}</div><div class="subtle">当前存在 run / agent / session 的项目数</div></article>
      <article class="summary-card"><h2>调试信号</h2><div class="metric">${summary.debug_issue_count || 0}</div><div class="subtle">已物化 issue 或运行摩擦信号总数</div></article>
    </section>
    <section class="dashboard-grid" style="margin-top:18px">
      <article class="panel">
        ${sectionHeader("按角色看", "同一个管理看板服务 CEO、项目负责人、运行治理者与恢复维护者，但每一层只看自己该做的判断。")}
        <div class="role-grid" style="margin-top:18px">
          ${roleCards.map((item) => `
            <article class="role-card">
              <div class="eyebrow">${item.eyebrow}</div>
              <h3>${item.title}</h3>
              <div class="role-metric">${item.metric}</div>
              <p>${item.desc}</p>
              <div class="project-actions" style="margin-top:12px">
                <a class="action-link" href="${item.href}">${item.action}</a>
              </div>
            </article>
          `).join("")}
        </div>
      </article>
      <div class="stack">
        <article class="panel">
          ${sectionHeader("重点介入", "把真正需要你判断的项目压缩成少量异常卡，不让平均化噪音抢前台。")}
          ${spotlight.length ? `
            <div class="list" style="margin-top:18px">
              ${spotlight.map((project) => `
                <div class="list-item">
                  <div><strong>${project.display_name}</strong></div>
                  <div class="subtle">${project.blocked_reason || project.next_reason || "需要进一步判断下一步。"}</div>
                  <div class="chips" style="margin-top:10px">
                    ${chip(label("health", project.health_status || "warn"), project.health_status)}
                    ${chip(label("debug", project.debug_state || "no_debug_feed"), project.debug_state)}
                    ${badge("查看详情", `/project-detail/?project=${encodeURIComponent(project.project_key)}`)}
                  </div>
                </div>
              `).join("")}
            </div>
          ` : `<div class="empty" style="margin-top:18px">当前没有需要额外介入的项目。</div>`}
        </article>
        <article class="panel">
          ${sectionHeader("控制台入口", "结构参考 Supabase 管理台，但边界保持 Beacon：PocketBase 只做可视化控制面，正式真相仍在 docs/.beacon。")}
          <div class="list" style="margin-top:18px">
            <div class="list-item"><strong>管理总览</strong><div class="subtle">看多项目总进度、生命周期泳道与项目登记表。</div><div class="project-actions" style="margin-top:10px"><a class="action-link" href="/portfolio-overview/">打开管理总览</a></div></div>
            <div class="list-item"><strong>项目详情</strong><div class="subtle">看当前版本文档、需求闭环、Git / Worktree 与建议技能。</div><div class="project-actions" style="margin-top:10px"><a class="action-link" href="${projectActionHref("project-detail", primaryProject)}">查看项目详情</a></div></div>
            <div class="list-item"><strong>运行中心</strong><div class="subtle">single / team / ralph 只在这里下钻，不抢首页叙事。</div><div class="project-actions" style="margin-top:10px"><a class="action-link" href="${projectActionHref("runtime-center", primaryProject)}">查看运行中心</a></div></div>
            <div class="list-item"><strong>恢复诊断</strong><div class="subtle">确认是 truth 层还是 projection 层异常，并给出重建路径。</div><div class="project-actions" style="margin-top:10px"><a class="action-link" href="${projectActionHref("recovery-diagnostics", primaryProject)}">查看恢复诊断</a></div></div>
          </div>
        </article>
      </div>
    </section>
    <section class="panel" style="margin-top:18px">
      ${sectionHeader("项目登记表", "首页只暴露有限的人类治理信息，默认不展示 tmux pane、raw debug event 或完整 transcript。")}
      ${projects.length ? `
        <div class="registry-table" style="margin-top:18px">
          <div class="registry-head">
            <div>项目</div>
            <div>阶段</div>
            <div>下一步</div>
            <div>运行态</div>
            <div>健康与调试</div>
            <div>操作</div>
          </div>
          ${projects.map((project) => projectRegistryRow(project)).join("")}
        </div>
      ` : `<div class="empty" style="margin-top:18px">当前还没有进入管理看板的项目。</div>`}
    </section>
  `);
}

async function renderPortfolio() {
  const data = await readJson("/data/portfolio-summary.json");
  const summary = data.summary || {};
  const projects = Array.isArray(data.projects) ? data.projects : [];
  const buckets = {
    requirements: projects.filter((project) => lifecycleBucket(project.current_stage) === "requirements"),
    implement: projects.filter((project) => lifecycleBucket(project.current_stage) === "implement"),
    qa: projects.filter((project) => lifecycleBucket(project.current_stage) === "qa"),
    release: projects.filter((project) => lifecycleBucket(project.current_stage) === "release"),
  };
  const attention = projects.filter((project) =>
    project.blocked
    || ["materialized_issue", "degraded"].includes(String(project.debug_state || "").toLowerCase())
    || ["warn", "blocked", "degraded"].includes(String(project.health_status || "").toLowerCase())
  ).slice(0, 4);
  ensure(document.querySelector("#nav"), nav(projects[0]?.project_key || ""));
  ensure(document.querySelector("#content"), `
    <section class="metric-strip">
      <article class="summary-card"><h2>受管项目</h2><div class="metric">${summary.project_count || 0}</div><div class="subtle">已经进入 Beacon 看板治理的项目数量</div></article>
      <article class="summary-card"><h2>当前阻塞</h2><div class="metric">${summary.blocked_count || 0}</div><div class="subtle">需要补材料、补基线或停止误推进的项目</div></article>
      <article class="summary-card"><h2>活跃运行态</h2><div class="metric">${summary.runtime_active_count || 0}</div><div class="subtle">存在 run / worker / session 观测信号</div></article>
      <article class="summary-card"><h2>调试信号</h2><div class="metric">${summary.debug_issue_count || 0}</div><div class="subtle">已物化或已沉淀的摩擦与问题记录</div></article>
    </section>
    <section class="dashboard-grid" style="margin-top:18px">
      <article class="panel">
        ${sectionHeader("生命周期泳道", "先按需求、实现、验收、待发布判断项目推进位置。Runtime 细节只在下钻页展开。")}
        <div class="lane-grid" style="margin-top:18px">
          <article class="lane-card">
            <div class="eyebrow">需求中</div>
            <strong>${buckets.requirements.length}</strong>
            <p>PRD、用户故事或测试用例尚未补齐，重点看 requirement closure。</p>
          </article>
          <article class="lane-card">
            <div class="eyebrow">实现中</div>
            <strong>${buckets.implement.length}</strong>
            <p>代码推进与 runtime 在此阶段观察，但不让机器洪流抢占首页。</p>
          </article>
          <article class="lane-card">
            <div class="eyebrow">验收中</div>
            <strong>${buckets.qa.length}</strong>
            <p>已经进入 QA 判断，重点看阻塞、覆盖和是否可继续收口。</p>
          </article>
          <article class="lane-card">
            <div class="eyebrow">待发布</div>
            <strong>${buckets.release.length}</strong>
            <p>已经接近交付，重点判断 release readiness 与最后的治理状态。</p>
          </article>
        </div>
      </article>
      <div class="stack">
        <article class="panel">
          ${sectionHeader("需介入项目", "只列出当前真正需要人类关注的项目，避免总览被平均信息稀释。")}
          ${attention.length ? `
            <div class="list" style="margin-top:18px">
              ${attention.map((project) => `
                <div class="list-item">
                  <div><strong>${project.display_name}</strong></div>
                  <div class="subtle">${project.blocked_reason || project.next_reason || "当前项目需要进一步判断下一步。"}</div>
                  <div class="chips" style="margin-top:10px">
                    ${chip(label("stage", project.current_stage), project.current_stage)}
                    ${chip(label("debug", project.debug_state || "no_debug_feed"), project.debug_state)}
                    ${chip(project.recommended_skill || "继续判断", project.blocked ? "warn" : "neutral")}
                  </div>
                </div>
              `).join("")}
            </div>
          ` : `<div class="empty" style="margin-top:18px">当前没有需要额外介入的项目，全部项目都处于可继续推进状态。</div>`}
        </article>
        <article class="panel">
          ${sectionHeader("总览约束", "管理总览回答的是经营判断和项目推进，不是把 PocketBase 伪装成项目真相数据库。")}
          <div class="list" style="margin-top:18px">
            <div class="list-item"><strong>正式真相</strong><div class="subtle">PRD、User Story、Test Case 与 docs/.beacon 仍是 Beacon requirement truth。</div></div>
            <div class="list-item"><strong>运行态下钻</strong><div class="subtle">single、team、ralph 只在运行中心展开，不上升成总览首页主叙事。</div></div>
            <div class="list-item"><strong>恢复优先级</strong><div class="subtle">SQLite / PocketBase 异常时，优先回到本地 truth 重建最小可用状态。</div></div>
          </div>
        </article>
      </div>
    </section>
    <section class="panel" style="margin-top:18px">
      ${sectionHeader("项目注册表", "结构参考 Supabase 控制台的密集列表，但字段语义完全服从 Beacon 生命周期与版本治理。")}
      ${projects.length ? `
        <div class="registry-table" style="margin-top:18px">
          <div class="registry-head">
            <div>项目</div>
            <div>阶段</div>
            <div>下一步 / 材料</div>
            <div>运行态</div>
            <div>健康与调试</div>
            <div>操作</div>
          </div>
          ${projects.map((project) => projectRegistryRow(project, { showMaterials: true })).join("")}
        </div>
      ` : `<div class="empty">当前还没有可展示的项目投影数据。</div>`}
    </section>
  `);
}

async function renderDetail(page) {
  const portfolio = await readJson("/data/portfolio-summary.json");
  const projects = Array.isArray(portfolio.projects) ? portfolio.projects : [];
  const key = qs("project") || projects[0]?.project_key || "";
  ensure(document.querySelector("#nav"), nav(key));
  if (!key) {
    ensure(document.querySelector("#content"), `<div class="empty">当前没有可展示的项目。</div>`);
    return;
  }

  const detail = await readJson(`/data/projects/${encodeURIComponent(key)}.json`);
  const project = detail.project || {};
  const runtime = detail.runtime || {};
  const execution = runtime.execution_surface || {};
  const documents = Array.isArray(detail.documents) ? detail.documents : [];
  const selectedDocKey = qs("doc") || documents[0]?.doc_key || "";
  let selectedDocument = null;
  if (page === "project-detail" && selectedDocKey) {
    try {
      selectedDocument = await readJson(`/data/documents/${encodeURIComponent(key)}/${encodeURIComponent(selectedDocKey)}.json`);
    } catch (_error) {
      selectedDocument = null;
    }
  }
  const toolbar = `
    <div class="toolbar">
      <div>
        <div class="eyebrow">${label("projectKind", project.project_kind)} · Docs ${project.docs_version || ""}</div>
        <h2 class="section-title" style="margin-top:8px">${project.display_name || key}</h2>
        <p class="section-desc">当前主线：${project.feature || "暂无记录中的 feature"}</p>
      </div>
      <label class="subtle">切换项目
        <select id="project-switcher">
          ${projects.map((row) => `<option value="${row.project_key}" ${row.project_key === key ? "selected" : ""}>${row.display_name}</option>`).join("")}
        </select>
      </label>
    </div>
  `;
  const overview = `
    <section class="panel">
      ${toolbar}
      <div class="chips">
        ${chip(label("health", project.health_status || "warn"), project.health_status)}
        ${chip(label("runtime", project.runtime_mode || "idle"), project.runtime_mode)}
        ${chip(label("debug", project.debug_state || "no_debug_feed"), project.debug_state)}
        ${chip(project.runtime_corroboration === "available" ? "运行态已佐证" : "仅本地真相", project.runtime_corroboration)}
      </div>
      <div class="project-grid" style="margin-top:18px">
        <div class="kv">
          ${pair("主阶段", label("stage", project.current_stage))}
          ${pair("细分阶段", label("stage", project.stage_detail))}
          ${pair("进度摘要", project.progress_label || "-")}
          ${pair("下一步", label("nextAction", project.next_action || "-"))}
          ${pair("建议技能", project.recommended_skill || "-")}
          ${pair("推荐命令", project.recommended_command || "-")}
          ${pair("阻塞项", project.blocked_reason || "无")}
          ${pair("真相来源", detail.truth?.source_of_truth || "docs/beacon + .beacon")}
          ${pair("运行时版本", detail.truth?.beacon_runtime_version || "-")}
          ${pair("版本文档数", documents.length || 0)}
        </div>
        <div class="stack">
          <div class="panel" style="padding:16px">
            <div class="eyebrow">材料完整度</div>
            <div class="chips" style="margin-top:10px">
              ${chip(`PRD ${label("material", project.materials?.prd)}`, project.materials?.prd)}
              ${chip(`用户故事 ${label("material", project.materials?.user_story)}`, project.materials?.user_story)}
              ${chip(`测试用例 ${label("material", project.materials?.test_case)}`, project.materials?.test_case)}
            </div>
          </div>
          <div class="panel" style="padding:16px">
            <div class="eyebrow">运行态摘要</div>
            <div class="subtle" style="margin-top:10px">${runtime.run_count || 0} 个 run · ${runtime.worker_count || 0} 个代理 · ${runtime.host_session_count || 0} 个宿主会话</div>
          </div>
        </div>
      </div>
    </section>
  `;

  let body = "";
  if (page === "project-detail") {
    body = `
      <section class="section-grid" style="margin-top:18px">
        <article class="panel">
          ${sectionHeader("版本与需求包", "帮助项目负责人快速判断当前版本下 PRD / User Story / Test Case 是否闭环。")}
          ${renderList("版本与需求包", detail.feature_packages || [], (item) => `
            <div class="list-item">
              <div class="title" style="font-size:1.05rem">${item.feature}</div>
              <div class="subtle">版本 ${item.docs_version} · 标识 ${item.feature_slug}</div>
              <div class="chips" style="margin-top:10px">
                ${chip(`PRD ${label("material", item.materials?.prd)}`, item.materials?.prd)}
                ${chip(`用户故事 ${label("material", item.materials?.user_story)}`, item.materials?.user_story)}
                ${chip(`测试用例 ${label("material", item.materials?.test_case)}`, item.materials?.test_case)}
              </div>
            </div>`)}
        </article>
        <article class="panel">
          ${sectionHeader("Git / Worktree 治理", "确认当前项目是否处于预期分支、是否脏工作区、以及多仓工作区是否按约束运行。")}
          ${renderList("Git / Worktree 治理", detail.git_scopes || [], (item) => `
            <div class="list-item">
              <div><strong>${item.repo_name}</strong> · ${item.role}</div>
              <div class="subtle">${item.branch} · worktree ${item.worktree_name || "-"}</div>
              <div class="chips" style="margin-top:10px">${chip(item.dirty ? "工作区有变更" : "工作区干净", item.dirty ? "warn" : "good")} ${chip(item.source_priority || "source", item.source_priority)}</div>
            </div>`)}
        </article>
        <article class="panel">
          ${sectionHeader("生命周期行", "展示 feature 当前落在需求、实现、验收还是发布前核查，并给出简洁解释。")}
          ${renderList("生命周期行", detail.feature_lifecycle || [], (item) => `
            <div class="list-item">
              <div><strong>${item.feature}</strong></div>
              <div class="subtle">${label("stage", item.current_stage)} · ${item.progress_label}</div>
              <div class="chips" style="margin-top:10px">
                ${chip(label("runtime", item.runtime_mode || "idle"), item.runtime_mode)}
                ${chip(label("debug", item.debug_state || "no_debug_feed"), item.debug_state)}
                ${chip(item.blocked ? "存在阻塞" : "可继续推进", item.blocked ? "bad" : "good")}
              </div>
            </div>`)}
        </article>
      </section>
      <section class="panel" style="margin-top:18px">
        ${sectionHeader("版本文档列表与网页查看", "把目标项目当前 Beacon 版本下的人类文档投影到管理看板中，支持列表浏览与只读网页查看，但正式真相仍是项目本地 docs/beacon。")}
        ${documents.length ? `
        <div class="doc-layout" style="margin-top:18px">
          <div class="doc-list">
            ${documents.map((item) => `
              <a class="doc-link ${item.doc_key === selectedDocKey ? "active" : ""}" href="/project-detail/?project=${encodeURIComponent(key)}&doc=${encodeURIComponent(item.doc_key)}">
                <div class="eyebrow">${item.section}</div>
                <strong>${item.title}</strong>
                <small>${item.project_ref || item.relative_path}</small>
                <small>${item.excerpt || "当前文档暂无摘要。"} </small>
              </a>
            `).join("")}
          </div>
          <article class="doc-viewer">
            ${selectedDocument && selectedDocument.content ? `
              <div class="eyebrow">${selectedDocument.section || "文档"}</div>
              <h3 style="margin:8px 0 0">${selectedDocument.title || "未命名文档"}</h3>
              <div class="doc-meta">${selectedDocument.project_ref || selectedDocument.relative_path || "-"} · ${selectedDocument.line_count || 0} 行 · 只读投影视图</div>
              <div class="markdown">${renderMarkdown(selectedDocument.content || "")}</div>
            ` : `<div class="empty">当前文档内容未能加载，请切换其他文档或重新生成运行态看板。</div>`}
          </article>
        </div>` : `<div class="empty" style="margin-top:18px">当前项目还没有可展示的版本文档。</div>`}
      </section>
    `;
  } else if (page === "runtime-center") {
    body = `
      <section class="section-grid" style="margin-top:18px">
        <article class="panel">
          ${sectionHeader("运行态总览", "只给人类展示必要控制结论，不把 tmux pane、原始事件流和代理 transcript 直接暴露出来。")}
          <div class="kv">
            ${pair("运行模式", label("runtime", runtime.mode))}
            ${pair("执行面", execution.selected_surface || "-")}
            ${pair("项目模式", execution.project_mode || "-")}
            ${pair("宿主运行时", execution.host_runtime || "-")}
            ${pair("实现模式", label("runtime", execution.implement_mode) || execution.implement_mode || "-")}
            ${pair("QA 模式", execution.qa_execution_mode || "-")}
            ${pair("Ralph 阶段", execution.ralph_phase || "-")}
            ${pair("Ralph 下一步", execution.ralph_next_action || "-")}
            ${pair("Ralph 轮次", execution.ralph_round_count || 0)}
            ${pair("失败连续数", execution.ralph_failure_streak || 0)}
            ${pair("代理运行态", execution.subagent_runtime_status || "-")}
            ${pair("代理委派态", execution.subagent_delegation_status || "-")}
          </div>
        </article>
        <article class="panel">
          ${sectionHeader("最近运行", "查看近期 run 结果，判断项目是否在推进、是否卡在某一轮。")}
          ${renderList("最近运行", detail.runs || [], (item) => `
            <div class="list-item">
              <div><strong>${item.run_id}</strong></div>
              <div class="subtle">${item.feature} · ${label("runtime", item.mode)} · ${item.status}</div>
              <div class="subtle">${item.started_at || "-"} ${item.ended_at ? `→ ${item.ended_at}` : ""}</div>
            </div>`)}
        </article>
        <article class="panel">
          ${sectionHeader("代理视图", "team / ralph 模式下只展示角色、状态、pane 摘要，不展开完整机器交互。")}
          ${renderList("代理视图", detail.run_workers || [], (item) => `
            <div class="list-item">
              <div><strong>${item.worker_id}</strong> · ${item.role}</div>
              <div class="subtle">${item.status} · tmux ${item.tmux_session || "-"} / pane ${item.pane_id || "-"}</div>
            </div>`)}
        </article>
        <article class="panel">
          ${sectionHeader("宿主会话", "保留 Codex / Claude 的最小会话元数据，方便追 run，不泄露完整宿主上下文。")}
          ${renderList("宿主会话", detail.host_sessions || [], (item) => `
            <div class="list-item">
              <div><strong>${item.host_runtime}</strong> · ${item.session_id}</div>
              <div class="subtle">${item.feature || "-"} · run ${item.run_id || "-"} · ${item.status}</div>
              <div class="subtle">${item.started_at || "-"}${item.ended_at ? ` → ${item.ended_at}` : ""}</div>
              <div class="subtle">thread ${item.thread_id || "-"} · turn ${item.turn_id || "-"} · 会话记录 ${item.transcript_ref || "-"}</div>
            </div>`)}
        </article>
      </section>
    `;
  } else {
    body = `
      <section class="section-grid" style="margin-top:18px">
        <article class="panel">
          ${sectionHeader("调试与摩擦", "收口 materialized_issue / runtime_feed_only / no_debug_feed 三态，帮助人类判断这是不是 Beacon 缺陷。")}
          ${renderList("调试与摩擦", detail.debug_issues || [], (item) => `
            <div class="list-item">
              <div><strong>${item.reason_code}</strong></div>
              <div class="subtle">${item.issue_status} · ${item.materialization_state}</div>
              <div class="subtle">${item.sample || "-"}</div>
              <div class="chips" style="margin-top:10px">${chip(item.suggested_capability || "none", item.suggested_capability)}</div>
            </div>`)}
        </article>
        <article class="panel">
          ${sectionHeader("健康快照", "确认 stale run、blocked run、failing scope 是否已经让这个项目进入降级或观察态。")}
          ${renderList("健康快照", detail.health_snapshots || [], (item) => `
            <div class="list-item">
              <div><strong>${label("health", item.overall_status || "warn")}</strong> · 同步 ${item.sync_status || "-"}</div>
              <div class="subtle">stale ${item.stale_runs || 0} · blocked ${item.blocked_runs || 0} · failing scopes ${item.failing_scopes || 0}</div>
              <div class="subtle">${(item.notes || []).join("，") || "暂无附加说明"}</div>
            </div>`)}
        </article>
        <article class="panel">
          ${sectionHeader("恢复合同", "强调 SQLite / PocketBase 只是 projection / control plane，项目仍可从本地 truth 继续推进。")}
          <div class="kv">
            ${pair("真相拥有者", detail.truth?.source_of_truth || "docs/beacon + .beacon")}
            ${pair("控制面角色", "PocketBase 仅用于可视化与备份，不改写正式交付真相")}
            ${pair("降级策略", "SQLite / PocketBase 不可用时，从本地 truth 重建最小可用状态")}
            ${pair("接管门状态", execution.takeover_gate?.status || "-")}
            ${pair("接管原因", execution.takeover_gate?.reason_code || "-")}
            ${pair("运行档案", execution.profile_id || "无")}
          </div>
        </article>
      </section>
    `;
  }

  ensure(document.querySelector("#content"), overview + body);
  const switcher = document.querySelector("#project-switcher");
  if (switcher) {
    switcher.addEventListener("change", (event) => {
      const target = event.target;
      if (target && target.value) {
        window.location.href = `/${page}/?project=${encodeURIComponent(target.value)}`;
      }
    });
  }
}

async function main() {
  if (PAGE === "board-home") {
    await renderBoardHome();
  } else if (PAGE === "portfolio-overview") {
    await renderPortfolio();
  } else {
    await renderDetail(PAGE);
  }
}

main().catch((error) => {
  ensure(document.querySelector("#content"), `<div class="empty">看板加载失败：${error.message}</div>`);
});
""".strip() + "\n"


def _page_shell(page: str) -> str:
    meta = PAGE_META.get(page, PAGE_META["portfolio-overview"])
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{meta["headline"]} · {meta["title"]}</title>
    <link rel="stylesheet" href="/assets/board.css">
  </head>
  <body data-page="{page}">
    <div class="app-shell">
      <aside class="sidebar">
        <section class="brand-block">
          <div class="brand-kicker">Beacon Runtime Projection</div>
          <div class="brand-row">
            <div class="brand-mark">B</div>
            <div>
              <p class="brand-title">Beacon 管理看板</p>
              <p class="brand-copy">Supabase 式控制台结构，Vercel / getdesign 风格表达。</p>
            </div>
          </div>
        </section>
        <section class="sidebar-section">
          <div class="sidebar-label">看板视图</div>
          <nav id="nav" class="nav-tabs" aria-label="Board sections"></nav>
        </section>
        <section class="sidebar-section">
          <div class="sidebar-label">产品边界</div>
          <div class="sidebar-note">PocketBase 只管理 Beacon 的投影运行态、可视化与备份；正式交付真相仍然是项目本地 `docs/beacon` 与 `.beacon`。</div>
        </section>
      </aside>
      <div class="workspace">
        <header class="topbar">
          <div>
            <div class="topbar-kicker">Beacon / PocketBase Control Plane</div>
            <h1 class="topbar-title">{meta["title"]}</h1>
            <p class="topbar-desc">{meta["description"]}</p>
          </div>
          <div class="topbar-meta">
            <span class="pill">Projection Only</span>
            <span class="pill">正式真相 = docs/.beacon</span>
            <span class="pill">中文治理视图</span>
          </div>
        </header>
        <main class="shell">
          <section id="content" aria-live="polite"></section>
        </main>
      </div>
    </div>
    <script src="/assets/board.js" defer></script>
  </body>
</html>
"""


def _root_index() -> str:
    return _page_shell("board-home")


def write_public_board_pack(*, pocketbase_root: Path, control_plane: dict[str, Any], generated_at: str) -> dict[str, str]:
    collections_root = pocketbase_root / "collections"
    public_root = pocketbase_root / "pb_public"
    data_root = public_root / "data"
    projects_root = data_root / "projects"
    documents_root = data_root / "documents"
    assets_root = public_root / "assets"
    projects_root.mkdir(parents=True, exist_ok=True)
    documents_root.mkdir(parents=True, exist_ok=True)
    assets_root.mkdir(parents=True, exist_ok=True)

    project_payloads = []
    for path in sorted((collections_root / "projects").glob("*.json")):
        payload = _read_json(path)
        if payload:
            project_payloads.append(payload)

    portfolio_view = _portfolio_view(project_payloads, generated_at)
    _write_text(data_root / "portfolio-summary.json", json.dumps(portfolio_view, ensure_ascii=False, indent=2) + "\n")
    for payload in project_payloads:
        project_key = str(payload.get("project_key") or "").strip()
        if not project_key:
            continue
        detail_view = _detail_view(payload, collections_root)
        detail = {
            "schema_version": "1.0",
            "generated_at": generated_at,
            **detail_view,
        }
        _write_text(projects_root / f"{project_key}.json", json.dumps(detail, ensure_ascii=False, indent=2) + "\n")
        project_documents_root = documents_root / project_key
        for item in detail_view.get("documents", []):
            if not isinstance(item, dict):
                continue
            relative_path = str(item.get("relative_path") or "").strip()
            doc_key = str(item.get("doc_key") or "").strip()
            docs_root_value = str(payload.get("docs_root") or "").strip()
            if not relative_path or not doc_key or not docs_root_value:
                continue
            path = Path(docs_root_value).expanduser() / relative_path
            if not path.exists() or not path.is_file():
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            doc_payload = {
                "schema_version": "1.0",
                "generated_at": generated_at,
                "project_key": project_key,
                "doc_key": doc_key,
                "section": str(item.get("section") or ""),
                "title": str(item.get("title") or ""),
                "relative_path": relative_path,
                "project_ref": str(item.get("project_ref") or relative_path),
                "line_count": int(item.get("line_count", 0) or 0),
                "content": content,
            }
            _write_text(project_documents_root / f"{doc_key}.json", json.dumps(doc_payload, ensure_ascii=False, indent=2) + "\n")

    _write_text(assets_root / "board.css", _board_css())
    _write_text(assets_root / "board.js", _board_js())
    _write_text(public_root / "index.html", _root_index())
    for page in PAGES:
        _write_text(public_root / page / "index.html", _page_shell(page))

    manifest = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "pages": list(PAGES),
        "project_count": len(project_payloads),
        "public_root": str(public_root),
        "admin_ui": str(control_plane.get("admin_ui") or ""),
    }
    _write_text(public_root / "board-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    return {
        "public_root": str(public_root),
        "portfolio": str(data_root / "portfolio-summary.json"),
        "manifest": str(public_root / "board-manifest.json"),
        "index": str(public_root / "index.html"),
        "documents_root": str(documents_root),
        "portfolio_page": str(public_root / "portfolio-overview" / "index.html"),
        "detail_page": str(public_root / "project-detail" / "index.html"),
        "runtime_page": str(public_root / "runtime-center" / "index.html"),
        "recovery_page": str(public_root / "recovery-diagnostics" / "index.html"),
    }
