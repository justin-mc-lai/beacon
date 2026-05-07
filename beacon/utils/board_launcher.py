"""Board launcher helpers for prototype-backed operator workbench surfaces."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any

from beacon.utils.implementation_plan import load_implementation_plan_progress
from beacon.utils.acceptance_kit import build_acceptance_kit_projection
from beacon.utils.prototype_utils import evaluate_prototype_status, slugify_feature
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.runtime import read_json
from beacon.utils.runtime_projection import build_runtime_projection


BOARD_BUNDLE_RENDERER_VERSION = "v4-cn-surface-localization"


def list_prototype_feature_candidates(project_root: Path, version: str) -> list[str]:
    root = project_root / "docs" / "beacon" / version / "prototype"
    if not root.exists():
        return []
    return [path.name for path in sorted(root.iterdir()) if path.is_dir()]


def _entrypoint_relpath(status: dict[str, Any]) -> str:
    files = status.get("files") if isinstance(status.get("files"), dict) else {}
    preferred = (
        ("preview_html", "preview.html"),
        ("preview_dark_html", "preview-dark.html"),
    )
    for key, fallback in preferred:
        path = files.get(key)
        if isinstance(path, Path) and path.exists():
            return path.name
        if fallback and isinstance(files.get("root"), Path) and (files["root"] / fallback).exists():
            return fallback
    return "preview.html"


def resolve_board_feature(project_root: Path, version: str, feature: str | None = None) -> dict[str, Any]:
    requested = str(feature or "").strip()
    if requested:
        status = evaluate_prototype_status(project_root, version, requested)
        return {
            "feature": requested,
            "feature_slug": slugify_feature(requested),
            "selection_mode": "explicit",
            "status": status,
            "reason": "",
        }

    candidates = list_prototype_feature_candidates(project_root, version)
    evaluated: list[dict[str, Any]] = []
    for item in candidates:
        status = evaluate_prototype_status(project_root, version, item)
        evaluated.append(
            {
                "feature": item,
                "feature_slug": slugify_feature(item),
                "status": status,
            }
        )

    gate_ready = [item for item in evaluated if bool((item.get("status") or {}).get("gate_ready"))]
    if len(gate_ready) == 1:
        selected = gate_ready[0]
        return {
            "feature": str(selected.get("feature") or ""),
            "feature_slug": str(selected.get("feature_slug") or ""),
            "selection_mode": "auto-single-gate-ready",
            "status": selected.get("status") or {},
            "reason": "",
        }

    if len(gate_ready) > 1:
        names = ", ".join(str(item.get("feature") or "") for item in gate_ready)
        return {
            "feature": "",
            "feature_slug": "",
            "selection_mode": "ambiguous",
            "status": {},
            "reason": f"multiple gate-ready prototypes found under {version}: {names}",
            "candidates": [str(item.get("feature") or "") for item in gate_ready],
        }

    if len(evaluated) == 1:
        selected = evaluated[0]
        return {
            "feature": str(selected.get("feature") or ""),
            "feature_slug": str(selected.get("feature_slug") or ""),
            "selection_mode": "auto-single-candidate",
            "status": selected.get("status") or {},
            "reason": "",
        }

    if not evaluated:
        return {
            "feature": "",
            "feature_slug": "",
            "selection_mode": "missing",
            "status": {},
            "reason": f"no prototype bundles found under docs/beacon/{version}/prototype",
            "candidates": [],
        }

    return {
        "feature": "",
        "feature_slug": "",
        "selection_mode": "ambiguous",
        "status": {},
        "reason": "multiple prototype bundles found; pass --feature to choose one",
        "candidates": [str(item.get("feature") or "") for item in evaluated],
    }


def _status_group(status: str) -> str:
    normalized = str(status or "").strip().lower()
    if normalized in {"planned", "queued", "draft"}:
        return "queued"
    if normalized in {"running", "active", "in_progress"}:
        return "active"
    if normalized in {"retry_waiting", "retry_scheduled"}:
        return "retry_scheduled"
    if normalized in {"completed", "accepted", "passed"}:
        return "needs_review"
    if normalized in {"blocked", "failed", "human_blocked", "waiting_for_handoff", "timeout", "stale"}:
        return "blocked"
    return "queued"


def _canonicalize_command_for_project(command: str, project_root: Path) -> str:
    rendered = str(command or "").strip()
    if not rendered:
        return ""
    project_text = str(project_root)
    replacements = {
        "--project-root .": f'--project-root "{project_text}"',
        "--project .": f'--project "{project_text}"',
        "--project-root ./": f'--project-root "{project_text}/"',
        "--project ./": f'--project "{project_text}/"',
    }
    for source, target in replacements.items():
        rendered = rendered.replace(source, target)
    return rendered


def _group_label(group: str) -> str:
    return {
        "queued": "Queued",
        "active": "Active",
        "blocked": "Blocked",
        "retry_scheduled": "Retry Scheduled",
        "needs_review": "Needs Review",
    }.get(group, group.replace("_", " ").title())


def _load_run_state_detail(project_root: Path, run_id: str) -> dict[str, Any]:
    candidates = [
        project_root / ".beacon" / "implement" / run_id / "state.json",
        project_root / ".beacon" / "runs" / run_id / "state.json",
    ]
    for path in candidates:
        payload = read_json(path, {})
        if isinstance(payload, dict) and payload:
            return payload
    return {}


def _derive_execution_groups(runs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped = {
        "queued": [],
        "active": [],
        "blocked": [],
        "retry_scheduled": [],
        "needs_review": [],
    }
    for run in runs:
        group = _status_group(str(run.get("status") or ""))
        grouped.setdefault(group, []).append(run)
    return grouped


def _derive_selected_run(runs: list[dict[str, Any]]) -> dict[str, Any]:
    priority = {"active": 0, "blocked": 1, "retry_scheduled": 2, "needs_review": 3, "queued": 4}
    ranked = sorted(
        runs,
        key=lambda item: (
            priority.get(_status_group(str(item.get("status") or "")), 9),
            str(item.get("started_at") or ""),
        ),
        reverse=False,
    )
    return ranked[0] if ranked else {}


def _build_operator_actions(
    *,
    project_root: Path,
    version: str,
    feature: str,
    selected_run: dict[str, Any],
    selected_run_state: dict[str, Any],
    diagnostics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    run_id = str(selected_run.get("run_id") or "")
    status = str((selected_run_state.get("status") or selected_run.get("status") or "")).strip().lower()
    source = str(selected_run.get("source") or "")
    recommended_command = str(
        selected_run_state.get("recommended_command")
        or selected_run_state.get("resume_command")
        or ""
    ).strip()
    recommended_command = _canonicalize_command_for_project(recommended_command, project_root)
    workflow_run = source in {"run_state", "help_payload"} or bool(selected_run_state.get("workflow"))

    def action(
        action_id: str,
        label: str,
        command: str,
        *,
        availability: str,
        reason: str,
        governance: str,
    ) -> dict[str, Any]:
        return {
            "action_id": action_id,
            "label": label,
            "command": command,
            "availability": availability,
            "reason": reason,
            "governance": governance,
        }

    continue_command = (
        f'beacon resume continue --run-id {run_id} --project-root "{project_root}" --version {version}'
        if run_id and workflow_run
        else f'beacon help --project-root {project_root} --version {version} --feature "{feature}"'
    )
    stop_command = (
        f'beacon workflow continue --project "{project_root}" --version {version} --run-id {run_id} --interactive --on-timeout abort'
        if run_id and workflow_run
        else ""
    )
    retry_command = (
        recommended_command
        or (
            f'beacon resume continue --run-id {run_id} --project-root "{project_root}" --version {version}'
            if run_id and workflow_run
            else f'beacon implement run "{feature}" --project "{project_root}" --version {version}'
        )
    )
    repair_command = (
        diagnostics[0].get("recommendation")
        if diagnostics
        else f'beacon doctor advise --project-root {project_root} --version {version}'
    )
    repair_command = _canonicalize_command_for_project(str(repair_command or ""), project_root)

    actions = [
        action(
            "continue",
            "Continue",
            continue_command,
            availability="enabled" if status in {"planned", "paused", "running", "active"} and workflow_run else "guarded",
            reason="resume the current workflow run through the existing resume/workflow control plane",
            governance="must execute through workflow/resume runtime contract; UI cannot mutate state files directly",
        ),
        action(
            "stop",
            "Stop",
            stop_command,
            availability="guarded" if stop_command else "unavailable",
            reason="stop remains a guarded interactive abort because there is no standalone force-stop write surface",
            governance="must route through workflow interactive abort path; board only surfaces the exact command",
        ),
        action(
            "retry",
            "Retry",
            retry_command,
            availability="enabled" if status in {"blocked", "failed", "aborted", "timeout", "stale", "human_blocked"} or recommended_command else "guarded",
            reason="retry uses the recorded recommended command when available, otherwise falls back to the narrowest safe resume path",
            governance="must respect the recommended repair command or resume contract; no direct file rewrite",
        ),
        action(
            "repair",
            "Open Repair Path",
            str(repair_command or ""),
            availability="enabled",
            reason="open the highest-priority repair path derived from diagnostics/help/runtime evidence",
            governance="repair path is advisory and CLI-routed; board stays read-only on requirement truth",
        ),
    ]
    return actions


def _board_jump_target(kind: str) -> str:
    return {
        "prd": "beacon prd create",
        "user-story": "beacon user-story create",
        "test-case": "beacon test-case create",
        "prototype": "#feature-detail",
    }.get(kind, "#feature-detail")


def _review_hints(release_scorecard: dict[str, Any], run_state: dict[str, Any]) -> list[str]:
    hints: list[str] = []
    qa_status = (release_scorecard.get("acceptance") or {}).get("status") if isinstance(release_scorecard.get("acceptance"), dict) else ""
    delivery_type = (release_scorecard.get("delivery") or {}).get("type") if isinstance(release_scorecard.get("delivery"), dict) else ""
    if qa_status:
        hints.append(f"acceptance:{qa_status}")
    if delivery_type:
        hints.append(f"delivery:{delivery_type}")
    artifact_updates = run_state.get("artifact_updates") if isinstance(run_state.get("artifact_updates"), dict) else {}
    if artifact_updates:
        for key, payload in artifact_updates.items():
            if isinstance(payload, dict) and payload.get("required"):
                hints.append(f"{key}:required")
    return hints[:6]


def _build_recovery_diagnostics(
    *,
    project_root: Path,
    version: str,
    feature: str,
    prototype_status: dict[str, Any],
    runtime_projection: dict[str, Any],
    implementation_plan_progress: dict[str, Any],
    selected_run_state: dict[str, Any],
) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []

    def add(reason_code: str, title: str, affected: str, recommendation: str, *, self_repair: bool = True) -> None:
        diagnostics.append(
            {
                "reason_code": reason_code,
                "title": title,
                "affected": affected,
                "recommendation": recommendation,
                "self_repair": self_repair,
            }
        )

    for reason in prototype_status.get("inconsistent_reasons", []) if isinstance(prototype_status.get("inconsistent_reasons"), list) else []:
        add(
            f"prototype:{reason}",
            "Prototype contract drift",
            feature,
            f"beacon prototype review \"{feature}\" --project {project_root} --version {version} --json",
        )

    for issue in runtime_projection.get("debug_issues", []) if isinstance(runtime_projection.get("debug_issues"), list) else []:
        reason_code = str(issue.get("reason_code") or "debug_issue")
        affected = str(issue.get("sample") or issue.get("issue_id") or feature)
        add(
            reason_code,
            "Debug issue",
            affected,
            f"beacon doctor advise --project-root {project_root} --version {version}",
        )

    health = runtime_projection.get("health_snapshots", []) if isinstance(runtime_projection.get("health_snapshots"), list) else []
    if health:
        snapshot = health[0] if isinstance(health[0], dict) else {}
        if int(snapshot.get("failing_scopes", 0) or 0) > 0:
            add(
                "workspace_drift",
                "Workspace drift detected",
                feature,
                f"beacon doctor verify-git-alignment --project-root {project_root} --version {version}",
            )
        if int(snapshot.get("blocked_runs", 0) or 0) > 0:
            add(
                "blocked_dependency",
                "Blocked runs present",
                feature,
                f"beacon status --project-root {project_root} --version {version} --feature \"{feature}\"",
            )
        if str(snapshot.get("sync_status") or "") not in {"pass", "healthy", "available"}:
            add(
                "stale_baseline_host",
                "Runtime projection sync degraded",
                feature,
                f"beacon doctor rebuild-runtime-ledger --project-root {project_root}",
            )
        for note in snapshot.get("notes", []) if isinstance(snapshot.get("notes"), list) else []:
            if str(note) == "runtime_corroboration_missing":
                add(
                    "missing_evidence_sink",
                    "Runtime corroboration missing",
                    feature,
                    f"beacon status --board --project-root {project_root} --version {version}",
                )

    blocked_task_ids = implementation_plan_progress.get("blocked_task_ids", []) if isinstance(implementation_plan_progress.get("blocked_task_ids"), list) else []
    if blocked_task_ids:
        add(
            "blocked_implementation_plan",
            "Implementation plan has blocked tasks",
            ", ".join(str(item) for item in blocked_task_ids[:4]),
            f"beacon implement plan \"{feature}\" --project {project_root} --version {version}",
        )

    reason_code = str(selected_run_state.get("reason_code") or "")
    if reason_code:
        add(
            f"run:{reason_code}",
            "Selected run is not healthy",
            str(selected_run_state.get("run_id") or feature),
            str(selected_run_state.get("recommended_command") or f"beacon help --project-root {project_root} --version {version} --feature \"{feature}\""),
        )

    if not diagnostics:
        add(
            "healthy_warning",
            "No blocking diagnostics",
            feature,
            f"beacon status --board --project-root {project_root} --version {version}",
        )
    return diagnostics


def build_operator_workbench_payload(
    project_root: Path,
    *,
    version: str,
    feature: str,
    prototype_status: dict[str, Any],
) -> dict[str, Any]:
    runtime_projection = build_runtime_projection(project_root, docs_version=version, feature=feature)
    implementation_plan_progress = load_implementation_plan_progress(project_root, version=version, feature=feature)
    release_scorecard = build_release_scorecard(project_root, version=version)

    runs = runtime_projection.get("runs") if isinstance(runtime_projection.get("runs"), list) else []
    execution_groups = _derive_execution_groups(runs)
    selected_run = _derive_selected_run(runs)
    selected_run_id = str(selected_run.get("run_id") or "")
    selected_run_state = _load_run_state_detail(project_root, selected_run_id) if selected_run_id else {}
    selected_run_events = [
        item
        for item in (runtime_projection.get("run_events") if isinstance(runtime_projection.get("run_events"), list) else [])
        if str(item.get("run_id") or "") == selected_run_id
    ]
    selected_run_artifacts = [
        item
        for item in (runtime_projection.get("artifact_refs") if isinstance(runtime_projection.get("artifact_refs"), list) else [])
        if str(item.get("run_id") or "") == selected_run_id
    ]

    git_workflow = selected_run_state.get("git_workflow") if isinstance(selected_run_state.get("git_workflow"), dict) else {}
    writable_services = [str(item) for item in git_workflow.get("writable_services", []) if str(item).strip()] if git_workflow else []
    direct_delivery_services = [str(item) for item in git_workflow.get("direct_delivery_services", []) if str(item).strip()] if git_workflow else []

    diagnostics = _build_recovery_diagnostics(
        project_root=project_root,
        version=version,
        feature=feature,
        prototype_status=prototype_status,
        runtime_projection=runtime_projection,
        implementation_plan_progress=implementation_plan_progress,
        selected_run_state=selected_run_state,
    )

    lifecycle = runtime_projection.get("lifecycle") if isinstance(runtime_projection.get("lifecycle"), dict) else {}
    board = runtime_projection.get("board") if isinstance(runtime_projection.get("board"), dict) else {}
    materials = runtime_projection.get("materials") if isinstance(runtime_projection.get("materials"), dict) else {}
    requirement_completeness = (
        runtime_projection.get("requirement_completeness")
        if isinstance(runtime_projection.get("requirement_completeness"), dict)
        else {}
    )
    supplement_task = runtime_projection.get("supplement_task") if isinstance(runtime_projection.get("supplement_task"), dict) else {}
    re_freeze_transaction = runtime_projection.get("re_freeze_transaction") if isinstance(runtime_projection.get("re_freeze_transaction"), dict) else {}
    acceptance_kit = build_acceptance_kit_projection(project_root, version=version, feature=feature)
    operator_actions = _build_operator_actions(
        project_root=project_root,
        version=version,
        feature=feature,
        selected_run=selected_run,
        selected_run_state=selected_run_state,
        diagnostics=diagnostics,
    )

    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slugify_feature(feature),
        "version": version,
        "prototype_status": {
            "status": str(prototype_status.get("status") or ""),
            "review_status": str(prototype_status.get("review_status") or ""),
            "gate_ready": bool(prototype_status.get("gate_ready")),
            "drift_status": str(prototype_status.get("drift_status") or ""),
        },
        "requirement_completeness": {
            "status": str(requirement_completeness.get("status") or ""),
            "target_stage": str(requirement_completeness.get("target_stage") or ""),
            "blocked_subgates": list(requirement_completeness.get("blocked_subgates") or []),
            "downgraded_subgates": list(requirement_completeness.get("downgraded_subgates") or []),
            "focus_areas": list(requirement_completeness.get("focus_areas") or []),
            "trace_loop_status": str(requirement_completeness.get("trace_loop_status") or ""),
            "acceptance_kit": acceptance_kit,
        },
        "views": [
            "portfolio-board",
            "execution-board",
            "feature-detail",
            "run-detail",
            "review-surface",
            "recovery-diagnostics",
        ],
        "portfolio_board": {
            "project_name": str(runtime_projection.get("display_name") or project_root.name),
            "project_key": str(runtime_projection.get("project_key") or ""),
            "current_stage": str(board.get("current_stage") or lifecycle.get("current_stage") or ""),
            "progress_label": str(board.get("progress_label") or lifecycle.get("progress_label") or ""),
            "health_status": str(board.get("health_status") or ""),
            "next_action": str(board.get("next_action") or ""),
            "requirement_completeness": {
                "status": str(requirement_completeness.get("status") or ""),
                "target_stage": str(requirement_completeness.get("target_stage") or ""),
                "blocked_subgates": list(requirement_completeness.get("blocked_subgates") or []),
            },
            "materials": {
                "prd": str(materials.get("prd") or ""),
                "user_story": str(materials.get("user_story") or ""),
                "test_case": str(materials.get("test_case") or ""),
            },
        },
        "execution_board": {
            "groups": {
                key: {
                    "label": _group_label(key),
                    "count": len(value),
                    "runs": value[:8],
                }
                for key, value in execution_groups.items()
            },
            "baseline_host_health": {
                "health_status": str(board.get("health_status") or ""),
                "runtime_corroboration": str(board.get("runtime_corroboration") or ""),
                "git_scopes": runtime_projection.get("git_scopes", []),
            },
            "wave_grouping": {
                "implementation_plan_status": str(implementation_plan_progress.get("status") or "missing"),
                "next_task_id": str(implementation_plan_progress.get("next_task_id") or ""),
                "blocked_task_ids": list(implementation_plan_progress.get("blocked_task_ids") or []),
                "counts": implementation_plan_progress.get("counts", {}),
            },
            "operator_actions": operator_actions,
        },
        "feature_detail": {
            "feature": feature,
            "version": version,
            "current_stage": str(lifecycle.get("current_stage") or ""),
            "blocked": bool(lifecycle.get("blocked")),
            "blocked_reason": str(lifecycle.get("blocked_reason") or ""),
            "next_step": lifecycle.get("next_step", {}),
            "requirement_completeness": {
                "status": str(requirement_completeness.get("status") or ""),
                "target_stage": str(requirement_completeness.get("target_stage") or ""),
                "blocked_subgates": list(requirement_completeness.get("blocked_subgates") or []),
                "downgraded_subgates": list(requirement_completeness.get("downgraded_subgates") or []),
                "focus_areas": list(requirement_completeness.get("focus_areas") or []),
                "human_loop_handoff": requirement_completeness.get("human_loop_handoff", {}),
                "acceptance_kit": acceptance_kit,
            },
            "supplement_task": supplement_task,
            "re_freeze_transaction": re_freeze_transaction,
            "implementation_plan_progress": implementation_plan_progress,
            "git_scopes": runtime_projection.get("git_scopes", []),
            "writable_services": writable_services,
            "direct_delivery_services": direct_delivery_services,
        },
        "run_detail": {
            "selected_run_id": selected_run_id,
            "selected_run": selected_run,
            "run_state": selected_run_state,
            "timeline": selected_run_events[:20],
            "artifacts": selected_run_artifacts[:20],
            "writable_services": writable_services,
            "operator_recommendation": str(selected_run_state.get("recommended_command") or board.get("next_action") or ""),
            "retry_history": [
                item
                for item in runs
                if str(item.get("feature") or "") == str(selected_run.get("feature") or "")
            ][:8],
            "operator_actions": operator_actions,
        },
        "review_surface": {
            "release_scorecard_summary": {
                "delivery_type": str(((release_scorecard.get("delivery") or {}).get("type")) if isinstance(release_scorecard.get("delivery"), dict) else ""),
                "acceptance_status": str(((release_scorecard.get("acceptance") or {}).get("status")) if isinstance(release_scorecard.get("acceptance"), dict) else ""),
                "revision_id": str(((release_scorecard.get("revision_binding") or {}).get("revision_id")) if isinstance(release_scorecard.get("revision_binding"), dict) else ""),
            },
            "artifact_refs": selected_run_artifacts[:10],
            "review_hints": _review_hints(release_scorecard, selected_run_state),
            "related_feature": feature,
        },
        "acceptance_kit": acceptance_kit,
        "recovery_diagnostics": diagnostics,
        "operator_action_contract": {
            "source_of_truth": "workflow/resume/implement/doctor/release cli surfaces",
            "actions": operator_actions,
            "ui_write_prohibited": True,
        },
    }


def _html_escape(value: Any) -> str:
    return html.escape(str(value or ""))


def _chip(label: str, tone: str = "neutral") -> str:
    return f'<span class="chip chip-{tone}">{_html_escape(label)}</span>'


def _tone_from_status(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"ready", "healthy", "pass", "completed", "available"}:
        return "good"
    if normalized in {"blocked", "failed", "degraded", "inconsistent", "not_ready"}:
        return "bad"
    return "warn"


def _cn_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _cn_feature_label(value: Any) -> str:
    text = str(value or "").strip()
    mapping = {
        "beacon-operator-workbench-and-board-launcher": "执行工作台看板",
        "beacon-execution-runtime-kernel": "执行运行内核",
    }
    return mapping.get(text, text or "未命名需求")


def _cn_status(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    mapping = {
        "ready": "就绪",
        "healthy": "健康",
        "pass": "通过",
        "completed": "已完成",
        "available": "可用",
        "blocked": "阻塞",
        "failed": "失败",
        "degraded": "降级",
        "inconsistent": "不一致",
        "not_ready": "未就绪",
        "planned": "已规划",
        "draft": "草稿",
        "frozen": "已冻结",
        "release": "发版",
        "single": "单人",
        "team": "协作",
        "manual": "手动",
        "needs_review": "待审阅",
        "needs review": "待审阅",
        "retry_scheduled": "待重试",
        "retry scheduled": "待重试",
        "queued": "排队中",
        "running": "进行中",
        "active": "进行中",
        "stopped": "已停止",
        "dry-run": "演练",
        "warning": "告警",
        "consistent": "一致",
        "missing": "缺失",
        "exists": "存在",
        "guarded": "受控",
        "enabled": "可执行",
        "unavailable": "不可用",
        "technical-review-contract": "技术评审合同",
    }
    return mapping.get(normalized, str(value or "").strip() or "-")


def _cn_reason(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    mapping = {
        "technical_review_contract_missing": "缺少技术评审合同",
        "workspace_drift": "工作区漂移",
        "blocked_dependency": "依赖阻塞",
        "missing-memory-friction-subskill": "缺少记忆摩擦子技能",
        "pocketbase-control-plane-admin-surface-missing": "PocketBase 控制平面缺失",
        "prd-create-generic-template-only": "PRD 生成器仍是通用模板",
        "prd-implement-delivery-drift-gate-missing": "PRD 与实现交付缺少漂移门禁",
        "prototype-reference-pack-visual-quality-drift": "原型参考包视觉质量漂移",
        "runtime_feedback": "运行时反馈待整理",
    }
    return mapping.get(normalized, str(value or "").strip() or "未说明")


def _cn_view_label(view_id: str) -> str:
    mapping = {
        "portfolio-board": "全局看板",
        "execution-board": "执行看板",
        "feature-detail": "需求详情",
        "run-detail": "运行详情",
        "review-surface": "评审界面",
        "recovery-diagnostics": "恢复诊断",
    }
    return mapping.get(view_id, view_id)


def _cn_diag_title(value: Any, reason_code: Any) -> str:
    normalized = str(reason_code or "").strip().lower()
    mapping = {
        "workspace_drift": "工作区漂移",
        "runtime_feedback": "运行反馈",
        "blocked_dependency": "依赖阻塞",
    }
    if normalized in mapping:
        return mapping[normalized]
    text = str(value or "").strip()
    if text == "Debug issue":
        return "治理诊断"
    return text or "恢复诊断"


def _cn_diag_affected(reason_code: Any, affected: Any) -> str:
    normalized = str(reason_code or "").strip().lower()
    mapping = {
        "missing-memory-friction-subskill": "当前版本承诺的记忆摩擦工具链仍缺少对外可见的子技能入口，导致技能路由无法直接使用这条能力。",
        "pocketbase-control-plane-admin-surface-missing": "PocketBase 控制平面仍停留在材料或镜像层，没有形成可运行的管理后台与运维入口。",
        "prd-create-generic-template-only": "PRD 创建能力仍输出通用模板，缺少按版本和场景收敛的正式骨架。",
        "prd-implement-delivery-drift-gate-missing": "PRD 承诺面与实际交付面之间还没有稳定的阻断门禁，存在实现漂移风险。",
        "prototype-reference-pack-visual-quality-drift": "原型参考包的视觉质量与信息表达还不稳定，难以直接支撑高质量管理工作台评审。",
        "runtime_feedback": "当前存在一条运行时反馈，需要先整理成正式需求或修复项，再继续推进执行。",
        "workspace_drift": "当前工作区与预期执行面存在漂移，继续操作前应先核对 git 对齐状态。",
        "blocked_dependency": "当前运行被上游依赖阻塞，继续前需要先解除前置条件。",
    }
    return mapping.get(normalized, str(affected or "").strip() or "当前存在需要处理的恢复诊断。")


def _render_runs_table(runs: list[dict[str, Any]]) -> str:
    if not runs:
        return '<div class="empty">当前分组没有运行项。</div>'
    rows = []
    for run in runs:
        rows.append(
            "<tr>"
            f"<td>{_html_escape(run.get('run_id'))}</td>"
            f"<td>{_html_escape(_cn_feature_label(run.get('feature')))}</td>"
            f"<td>{_chip(_cn_status(run.get('status')), _tone_from_status(str(run.get('status') or '')))}</td>"
            f"<td>{_html_escape(_cn_status(run.get('mode')))}</td>"
            f"<td>{_html_escape(run.get('started_at'))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>运行 ID</th><th>需求</th><th>状态</th><th>模式</th><th>开始时间</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _render_kv_list(items: list[tuple[str, Any]]) -> str:
    rows = []
    for key, value in items:
        rows.append(f"<div class='kv'><span>{_html_escape(key)}</span><strong>{_html_escape(value)}</strong></div>")
    return "".join(rows)


def _render_link_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<div class="empty">当前没有可跳转的补料项。</div>'
    rows = []
    for item in items:
        label = str(item.get("label") or "").strip() or "补料项"
        href = str(item.get("href") or "").strip() or "#feature-detail"
        note = str(item.get("note") or "").strip()
        rows.append(
            f'<a class="jump-link" href="{_html_escape(href)}">'
            f"<strong>{_html_escape(label)}</strong>"
            f"<span>{_html_escape(note)}</span>"
            "</a>"
        )
    return "".join(rows)


def _render_link_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<div class="empty">当前没有可跳转的补料项。</div>'
    rows = []
    for item in items:
        label = str(item.get("label") or "").strip() or "补料项"
        href = str(item.get("href") or "").strip() or "#feature-detail"
        note = str(item.get("note") or "").strip()
        rows.append(
            f'<a class="jump-link" href="{_html_escape(href)}">'
            f"<strong>{_html_escape(label)}</strong>"
            f"<span>{_html_escape(note)}</span>"
            "</a>"
        )
    return "".join(rows)


def render_operator_workbench_html(payload: dict[str, Any]) -> str:
    portfolio = payload.get("portfolio_board") if isinstance(payload.get("portfolio_board"), dict) else {}
    execution = payload.get("execution_board") if isinstance(payload.get("execution_board"), dict) else {}
    feature_detail = payload.get("feature_detail") if isinstance(payload.get("feature_detail"), dict) else {}
    run_detail = payload.get("run_detail") if isinstance(payload.get("run_detail"), dict) else {}
    review = payload.get("review_surface") if isinstance(payload.get("review_surface"), dict) else {}
    diagnostics = payload.get("recovery_diagnostics") if isinstance(payload.get("recovery_diagnostics"), list) else []
    action_contract = payload.get("operator_action_contract") if isinstance(payload.get("operator_action_contract"), dict) else {}
    actions = action_contract.get("actions") if isinstance(action_contract.get("actions"), list) else []
    groups = execution.get("groups") if isinstance(execution.get("groups"), dict) else {}
    plan_progress = feature_detail.get("implementation_plan_progress") if isinstance(feature_detail.get("implementation_plan_progress"), dict) else {}
    review_summary = review.get("release_scorecard_summary") if isinstance(review.get("release_scorecard_summary"), dict) else {}
    artifacts = run_detail.get("artifacts") if isinstance(run_detail.get("artifacts"), list) else []
    timeline = run_detail.get("timeline") if isinstance(run_detail.get("timeline"), list) else []
    selected_run = run_detail.get("selected_run") if isinstance(run_detail.get("selected_run"), dict) else {}
    selected_diag = diagnostics[0] if diagnostics else {}
    next_action = _cn_status(portfolio.get("next_action") or run_detail.get("operator_recommendation") or "doctor-suggested")
    primary_judgment = _cn_reason(feature_detail.get("blocked_reason") or selected_diag.get("reason_code") or portfolio.get("health_status"))
    feature_title = "Beacon 执行工作台"
    supplement_task = feature_detail.get("supplement_task") if isinstance(feature_detail.get("supplement_task"), dict) else {}
    re_freeze_transaction = feature_detail.get("re_freeze_transaction") if isinstance(feature_detail.get("re_freeze_transaction"), dict) else {}
    supplement_links: list[dict[str, Any]] = []
    if supplement_task.get("target_artifact"):
        target_artifact = str(supplement_task.get("target_artifact") or "")
        note = str(supplement_task.get("recommended_route") or "")
        focus_areas = supplement_task.get("candidate_payload", {}) if isinstance(supplement_task.get("candidate_payload"), dict) else {}
        if not note:
            focus_areas_list = focus_areas.get("focus_areas") if isinstance(focus_areas.get("focus_areas"), list) else []
            note = str(focus_areas_list[0] if focus_areas_list else "")
        supplement_links.append(
            {
                "label": f"跳到 {target_artifact}",
                "href": _board_jump_target(target_artifact),
                "note": note or "查看补料提示",
            }
        )
    if re_freeze_transaction:
        supplement_links.append(
            {
                "label": "查看重冻结",
                "href": "#feature-detail",
                "note": f"refreeze={re_freeze_transaction.get('refreeze_required')} revalidate={re_freeze_transaction.get('revalidate_required')}",
            }
        )
    acceptance_kit = payload.get("acceptance_kit") if isinstance(payload.get("acceptance_kit"), dict) else {}
    acceptance_summary = acceptance_kit.get("summary") if isinstance(acceptance_kit.get("summary"), dict) else {}
    acceptance_links = []
    for item in acceptance_kit.get("links", []) if isinstance(acceptance_kit.get("links"), list) else []:
        layer = str(item.get("layer") or "")
        acceptance_links.append(
            {
                "label": f"{layer} / {item.get('status') or 'missing'}",
                "href": "#feature-detail",
                "note": str(item.get("source_truth_ref") or item.get("evidence_ref") or ""),
            }
        )
    supplement_links.extend(acceptance_links)

    group_summary_cards = []
    for key in ("queued", "active", "blocked", "retry_scheduled", "needs_review"):
        item = groups.get(key) if isinstance(groups.get(key), dict) else {}
        runs = item.get("runs") if isinstance(item.get("runs"), list) else []
        group_summary_cards.append(
            "<article class='metric-card'>"
            f"<div class='subtle'>{_html_escape(_cn_status(item.get('label') or _group_label(key)))}</div>"
            f"<strong class='metric-value'>{_html_escape(item.get('count') or 0)}</strong>"
            f"<div class='subtle'>{_html_escape(_cn_feature_label((runs[0] if runs else {}).get('feature')) if runs else '当前无重点项')}</div>"
            "</article>"
        )

    timeline_rows = []
    for event in timeline[:12]:
        timeline_rows.append(
            "<tr>"
            f"<td>{_html_escape(event.get('ts'))}</td>"
            f"<td>{_html_escape(event.get('stage'))}</td>"
            f"<td>{_html_escape(event.get('event'))}</td>"
            f"<td>{_html_escape(event.get('reason_code'))}</td>"
            "</tr>"
        )
    artifact_rows = []
    for item in artifacts[:10]:
        artifact_rows.append(
            "<tr>"
            f"<td>{_html_escape(item.get('artifact_type'))}</td>"
            f"<td>{_html_escape(item.get('path'))}</td>"
            f"<td>{_chip(_cn_status('exists' if item.get('exists') else 'missing'), 'good' if item.get('exists') else 'bad')}</td>"
            "</tr>"
        )

    diagnostic_cards = []
    for item in diagnostics:
        diagnostic_cards.append(
            "<article class='diag'>"
            f"<div class='diag-head'><strong>{_html_escape(_cn_diag_title(item.get('title'), item.get('reason_code')))}</strong>{_chip(_cn_reason(item.get('reason_code')), 'warn')}</div>"
            f"<p>{_html_escape(_cn_diag_affected(item.get('reason_code'), item.get('affected')))}</p>"
            f"<code>{_html_escape(item.get('recommendation'))}</code>"
            f"<div class='subtle'>可自修复：{'是' if item.get('self_repair') else '否'}</div>"
            "</article>"
        )

    action_cards = []
    for item in actions:
        tone = "good" if str(item.get("availability") or "") == "enabled" else "warn" if str(item.get("availability") or "") == "guarded" else "bad"
        action_cards.append(
            "<article class='diag'>"
            f"<div class='diag-head'><strong>{_html_escape(item.get('label'))}</strong>{_chip(_cn_status(item.get('availability')), tone)}</div>"
            f"<p>{_html_escape(item.get('reason'))}</p>"
            f"<code>{_html_escape(item.get('command') or 'not available')}</code>"
            f"<div class='subtle'>{_html_escape(item.get('governance'))}</div>"
            "</article>"
        )

    review_hints = "".join(f"<li>{_html_escape(item)}</li>" for item in (review.get("review_hints") or []))

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Beacon 执行工作台</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f5f7;
      --panel: #ffffff;
      --muted: #6e6e73;
      --fg: #1d1d1f;
      --line: #d2d2d7;
      --accent: #0071e3;
      --good: #1d7f4e;
      --warn: #9a6700;
      --bad: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif; background: var(--bg); color: var(--fg); }}
    a {{ color: var(--accent); text-decoration: none; }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px; display: grid; gap: 20px; }}
    header {{ display: grid; gap: 10px; }}
    .eyebrow {{ color: var(--accent); font-size: 12px; text-transform: uppercase; letter-spacing: 0; }}
    .hero {{ display: flex; align-items: start; justify-content: space-between; gap: 16px; }}
    .hero h1 {{ margin: 0; font-size: 28px; }}
    .subtle {{ color: var(--muted); font-size: 13px; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 12px; font-size: 14px; }}
    .hero-copy {{ display: grid; gap: 8px; }}
    .hero-kicker {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
    .hero-kicker strong {{ font-size: 18px; }}
    .judgment-grid {{ display: grid; gap: 16px; grid-template-columns: 1.2fr 0.8fr; }}
    .summary-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; display: grid; gap: 12px; }}
    .metric-grid {{ display: grid; gap: 12px; grid-template-columns: repeat(5, minmax(0, 1fr)); }}
    .metric-card {{ border: 1px solid var(--line); border-radius: 8px; padding: 12px; background: #fcfcfd; display: grid; gap: 6px; }}
    .metric-value {{ font-size: 24px; line-height: 1; }}
    .action-row {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .action-pill {{ display: inline-flex; align-items: center; gap: 8px; border-radius: 999px; border: 1px solid var(--line); padding: 8px 12px; background: #fff; }}
    .jump-grid {{ display: grid; gap: 10px; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .jump-link {{ display: grid; gap: 4px; padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    .jump-link span {{ color: var(--muted); font-size: 13px; }}
    details.panel-details {{ border: 1px solid var(--line); border-radius: 8px; background: #fcfcfd; padding: 14px; }}
    details.panel-details > summary {{ cursor: pointer; font-weight: 600; }}
    section.panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; display: grid; gap: 14px; }}
    .grid-3 {{ display: grid; gap: 16px; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .grid-2 {{ display: grid; gap: 16px; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .lane-grid {{ display: grid; gap: 16px; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .lane, .diag {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: #fcfcfd; display: grid; gap: 10px; }}
    .lane-head, .diag-head {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
    .kv {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px; padding: 8px 0; border-bottom: 1px solid #ececef; }}
    .kv:last-child {{ border-bottom: 0; }}
    .chip {{ display: inline-flex; align-items: center; border-radius: 999px; padding: 3px 8px; font-size: 12px; border: 1px solid var(--line); }}
    .chip-good {{ color: var(--good); border-color: color-mix(in srgb, var(--good) 24%, white); background: color-mix(in srgb, var(--good) 9%, white); }}
    .chip-warn {{ color: var(--warn); border-color: color-mix(in srgb, var(--warn) 24%, white); background: color-mix(in srgb, var(--warn) 10%, white); }}
    .chip-bad {{ color: var(--bad); border-color: color-mix(in srgb, var(--bad) 24%, white); background: color-mix(in srgb, var(--bad) 10%, white); }}
    .chip-neutral {{ color: var(--fg); background: #f0f1f4; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #ececef; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 600; }}
    ul {{ margin: 0; padding-left: 18px; }}
    code {{ white-space: pre-wrap; word-break: break-word; background: #f7f7fa; border: 1px solid #ececef; border-radius: 6px; padding: 8px; display: block; font-size: 12px; }}
    .empty {{ color: var(--muted); font-size: 13px; }}
    @media (max-width: 980px) {{
      .grid-3, .grid-2, .lane-grid, .judgment-grid, .metric-grid {{ grid-template-columns: 1fr; }}
      .hero {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="eyebrow">Beacon 执行工作台 · Runtime Backed</div>
      <div class="hero">
        <div class="hero-copy">
          <h1>{feature_title}</h1>
          <div class="hero-kicker">
            <strong>{_html_escape(primary_judgment)}</strong>
            {_chip(_cn_status(portfolio.get("health_status") or "warn"), _tone_from_status(str(portfolio.get("health_status") or "")))}
          </div>
          <div class="subtle">版本 {_html_escape(payload.get("version"))} · 原型 {_html_escape(_cn_status((payload.get("prototype_status") or {}).get("status")))} · 漂移 {_html_escape(_cn_status((payload.get("prototype_status") or {}).get("drift_status")))}</div>
        </div>
        <div>{_chip(_cn_status(portfolio.get("current_stage") or "release"), _tone_from_status(str(portfolio.get("health_status") or "")))}</div>
      </div>
      <nav>
        <a href="#recovery-diagnostics">恢复诊断</a>
        <a href="#portfolio-board">全局看板</a>
        <a href="#execution-board">执行看板</a>
        <a href="#feature-detail">需求详情</a>
        <a href="#run-detail">运行详情</a>
        <a href="#review-surface">评审界面</a>
        <a href="./preview.html">原型预览</a>
      </nav>
    </header>

    <section class="summary-card" id="recovery-diagnostics">
      <div class="eyebrow">首屏判断</div>
      <div class="judgment-grid">
        <div>
          <h2>恢复判断</h2>
          <p>{_html_escape(_cn_diag_affected(selected_diag.get("reason_code"), selected_diag.get("affected")) or "当前运行态存在治理阻塞，需要先判断是否进入恢复路径。")}</p>
          <div class="subtle">当前主要原因：{_html_escape(primary_judgment)}</div>
        </div>
        <div>
          <h2>下一步动作</h2>
          <div class="action-row">
            <span class="action-pill"><strong>建议动作</strong><span>{_html_escape(next_action)}</span></span>
            <span class="action-pill"><strong>当前需求</strong><span>{_html_escape(_cn_feature_label(payload.get("feature")))}</span></span>
          </div>
          <div class="subtle">优先先确认阻塞原因，再决定继续、重试或进入 doctor 修复。</div>
        </div>
      </div>
      <div class="grid-2">
          <div>{_render_kv_list([("恢复标题", _cn_diag_title(selected_diag.get("title"), selected_diag.get("reason_code"))), ("原因代码", _cn_reason(selected_diag.get("reason_code"))), ("可自修复", "是" if selected_diag.get("self_repair") else "否")])}</div>
        <div>{_render_kv_list([("推荐命令", selected_diag.get("recommendation") or "beacon doctor advise"), ("当前阶段", _cn_status(portfolio.get("current_stage"))), ("总体健康", _cn_status(portfolio.get("health_status")))])}</div>
      </div>
    </section>

    <section class="panel" id="execution-board">
      <h2>执行看板</h2>
      <div class="grid-2">
        <div>{_render_kv_list([("执行计划", _cn_status(execution.get("wave_grouping", {}).get("implementation_plan_status"))), ("下一任务", execution.get("wave_grouping", {}).get("next_task_id") or "待生成"), ("阻塞任务", ", ".join(execution.get("wave_grouping", {}).get("blocked_task_ids", [])) or "无")])}</div>
        <div>{_render_kv_list([("Baseline 宿主", _cn_status(execution.get("baseline_host_health", {}).get("health_status"))), ("运行佐证", _cn_status(execution.get("baseline_host_health", {}).get("runtime_corroboration"))), ("Git 范围", len(execution.get("baseline_host_health", {}).get("git_scopes", [])))])}</div>
      </div>
      <div class="metric-grid">{''.join(group_summary_cards)}</div>
      <details class="panel-details">
        <summary>展开运行明细</summary>
        <div class="lane-grid" style="margin-top:12px;">
          <section class='lane'><div class='lane-head'><h3>排队中</h3>{_chip(groups.get('queued', {}).get('count') or 0, 'neutral')}</div>{_render_runs_table(groups.get('queued', {}).get('runs') if isinstance(groups.get('queued', {}).get('runs'), list) else [])}</section>
          <section class='lane'><div class='lane-head'><h3>进行中</h3>{_chip(groups.get('active', {}).get('count') or 0, 'neutral')}</div>{_render_runs_table(groups.get('active', {}).get('runs') if isinstance(groups.get('active', {}).get('runs'), list) else [])}</section>
          <section class='lane'><div class='lane-head'><h3>阻塞</h3>{_chip(groups.get('blocked', {}).get('count') or 0, 'neutral')}</div>{_render_runs_table(groups.get('blocked', {}).get('runs') if isinstance(groups.get('blocked', {}).get('runs'), list) else [])}</section>
          <section class='lane'><div class='lane-head'><h3>待重试</h3>{_chip(groups.get('retry_scheduled', {}).get('count') or 0, 'neutral')}</div>{_render_runs_table(groups.get('retry_scheduled', {}).get('runs') if isinstance(groups.get('retry_scheduled', {}).get('runs'), list) else [])}</section>
          <section class='lane'><div class='lane-head'><h3>待审阅</h3>{_chip(groups.get('needs_review', {}).get('count') or 0, 'neutral')}</div>{_render_runs_table(groups.get('needs_review', {}).get('runs') if isinstance(groups.get('needs_review', {}).get('runs'), list) else [])}</section>
        </div>
      </details>
    </section>

    <section class="panel" id="portfolio-board">
      <h2>全局看板</h2>
      <div class="grid-3">
        <div>{_render_kv_list([("项目", portfolio.get("project_name")), ("阶段", _cn_status(portfolio.get("current_stage"))), ("推进状态", _cn_status(portfolio.get("progress_label")))])}</div>
        <div>{_render_kv_list([("下一步", _cn_status(portfolio.get("next_action"))), ("健康度", _cn_status(portfolio.get("health_status"))), ("PRD", _cn_status((portfolio.get("materials") or {}).get("prd")))])}</div>
        <div>{_render_kv_list([("用户故事", _cn_status((portfolio.get("materials") or {}).get("user_story"))), ("测试用例", _cn_status((portfolio.get("materials") or {}).get("test_case"))), ("项目键", portfolio.get("project_key"))])}</div>
      </div>
    </section>

    <section class="panel" id="feature-detail">
      <h2>需求详情</h2>
      <div class="grid-2">
        <div>{_render_kv_list([("需求", _cn_feature_label(feature_detail.get("feature"))), ("阶段", _cn_status(feature_detail.get("current_stage"))), ("是否阻塞", "是" if feature_detail.get("blocked") else "否"), ("阻塞原因", _cn_reason(feature_detail.get("blocked_reason")) if feature_detail.get("blocked_reason") else "无")])}</div>
        <div>{_render_kv_list([("计划状态", _cn_status(plan_progress.get("status"))), ("计划编号", plan_progress.get("plan_id") or "未生成"), ("下一任务", plan_progress.get("next_task_id") or "待生成"), ("可写服务", ", ".join(feature_detail.get("writable_services", [])) or "未声明"), ("Acceptance Kit", _cn_status(acceptance_summary.get("summary"))), ("Kit verdict", _cn_status(acceptance_summary.get("verdict")))])}</div>
      </div>
      <div>
        <h3>补料跳转</h3>
        <div class="jump-grid">{_render_link_list(supplement_links)}</div>
      </div>
    </section>

    <section class="panel" id="run-detail">
      <h2>运行详情</h2>
      <div class="grid-2">
        <div>{_render_kv_list([("当前运行", run_detail.get("selected_run_id") or "未选择"), ("状态", _cn_status(selected_run.get("status"))), ("模式", _cn_status(selected_run.get("mode"))), ("操作者建议", _cn_status(run_detail.get("operator_recommendation") or "observe"))])}</div>
        <div>{_render_kv_list([("可写服务", ", ".join(run_detail.get("writable_services", [])) or "未声明"), ("重试历史", len(run_detail.get("retry_history", []))), ("证据数量", len(artifacts)), ("时间线事件", len(timeline))])}</div>
      </div>
      <div>
        <h3>建议动作</h3>
        <div class="grid-2">{''.join(action_cards) if action_cards else '<div class="empty">No operator actions available.</div>'}</div>
      </div>
      <details class="panel-details">
        <summary>展开运行证据与时间线</summary>
        <div class="grid-2" style="margin-top:12px;">
          <div>
            <h3>时间线</h3>
            {"<table><thead><tr><th>时间</th><th>阶段</th><th>事件</th><th>原因</th></tr></thead><tbody>" + "".join(timeline_rows) + "</tbody></table>" if timeline_rows else '<div class="empty">当前没有时间线事件。</div>'}
          </div>
          <div>
            <h3>证据</h3>
            {"<table><thead><tr><th>类型</th><th>路径</th><th>状态</th></tr></thead><tbody>" + "".join(artifact_rows) + "</tbody></table>" if artifact_rows else '<div class="empty">当前运行没有关联证据。</div>'}
          </div>
        </div>
      </details>
    </section>

    <section class="panel" id="review-surface">
      <h2>评审界面</h2>
      <div class="grid-2">
        <div>{_render_kv_list([("修订", review_summary.get("revision_id") or "无"), ("验收", _cn_status(review_summary.get("acceptance_status"))), ("交付类型", _cn_text(review_summary.get("delivery_type"), "未声明"))])}</div>
        <div>
          <h3>评审提示</h3>
          {"<ul>" + review_hints + "</ul>" if review_hints else '<div class="empty">当前没有显式评审提示。</div>'}
        </div>
      </div>
    </section>
    <details class="panel-details">
      <summary>展开全部恢复诊断</summary>
      <div class="grid-2" style="margin-top:12px;">{''.join(diagnostic_cards)}</div>
    </details>
  </main>
</body>
</html>
"""


def prepare_board_runtime_bundle(project_root: Path, contract: dict[str, Any]) -> str:
    prototype_root = Path(str(contract.get("prototype_root") or ""))
    version = str(contract.get("version") or "unknown")
    feature_slug = str(contract.get("feature_slug") or "board")
    bundle_root = project_root / ".beacon" / "board-bundles" / version / feature_slug
    if bundle_root.exists():
        shutil.rmtree(bundle_root, ignore_errors=True)
    bundle_root.mkdir(parents=True, exist_ok=True)
    if prototype_root.exists():
        for name in ("preview.html", "preview-dark.html", "tokens.css", "theme.json", "DESIGN.md", "ux-prd.md"):
            source = prototype_root / name
            if source.exists():
                shutil.copy2(source, bundle_root / name)
    payload = contract.get("operator_workbench") if isinstance(contract.get("operator_workbench"), dict) else {}
    manifest = {
        "renderer_version": BOARD_BUNDLE_RENDERER_VERSION,
        "feature_slug": feature_slug,
        "version": version,
    }
    (bundle_root / "operator-workbench.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (bundle_root / "bundle-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (bundle_root / "index.html").write_text(render_operator_workbench_html(payload), encoding="utf-8")
    return str(bundle_root)


def ensure_board_runtime_bundle(project_root: Path, contract: dict[str, Any]) -> str:
    version = str(contract.get("version") or "unknown")
    feature_slug = str(contract.get("feature_slug") or "board")
    bundle_root = project_root / ".beacon" / "board-bundles" / version / feature_slug
    index_path = bundle_root / "index.html"
    payload_path = bundle_root / "operator-workbench.json"
    manifest_path = bundle_root / "bundle-manifest.json"
    manifest = read_json(manifest_path, {})
    if (
        index_path.exists()
        and payload_path.exists()
        and str((manifest or {}).get("renderer_version") or "") == BOARD_BUNDLE_RENDERER_VERSION
    ):
        return str(bundle_root)
    return prepare_board_runtime_bundle(project_root, contract)


def build_board_launcher_contract(
    project_root: Path,
    *,
    version: str,
    feature: str | None = None,
    host: str = "127.0.0.1",
    port: int = 4173,
    desktop: bool = False,
    open_browser: bool = False,
) -> dict[str, Any]:
    resolution = resolve_board_feature(project_root, version, feature)
    selected_feature = str(resolution.get("feature") or "")
    status = resolution.get("status") if isinstance(resolution.get("status"), dict) else {}

    mode = "desktop-planned" if desktop else "local-web"
    readiness_status = "not_ready"
    failure_reason = str(resolution.get("reason") or "")
    prototype_root = ""
    entry_html = "index.html"
    board_url = f"http://{host}:{port}/{entry_html}"
    operator_workbench: dict[str, Any] = {}
    runtime_projection = build_runtime_projection(project_root, docs_version=version, feature=selected_feature or None)
    board = runtime_projection.get("board") if isinstance(runtime_projection.get("board"), dict) else {}
    lifecycle = runtime_projection.get("lifecycle") if isinstance(runtime_projection.get("lifecycle"), dict) else {}
    runtime = runtime_projection.get("runtime") if isinstance(runtime_projection.get("runtime"), dict) else {}

    if selected_feature and status:
        prototype_root_path = status.get("root")
        prototype_root = str(prototype_root_path) if isinstance(prototype_root_path, Path) else str(prototype_root_path or "")
        operator_workbench = build_operator_workbench_payload(
            project_root,
            version=version,
            feature=selected_feature,
            prototype_status=status,
        )
        if desktop:
            readiness_status = "planned"
            failure_reason = failure_reason or "desktop launcher is not implemented yet; local web mode is the active contract"
        elif bool(status.get("gate_ready")):
            readiness_status = "ready"
        else:
            failure_reason = failure_reason or (
                f"prototype `{selected_feature}` is not gate ready: "
                f"status={status.get('status')} review={status.get('review_status')}"
            )
    elif desktop and not failure_reason:
        readiness_status = "planned"
        failure_reason = "desktop launcher is not implemented yet; local web mode is the active contract"

    return {
        "feature": selected_feature,
        "feature_slug": str(resolution.get("feature_slug") or ""),
        "version": version,
        "mode": mode,
        "selection_mode": str(resolution.get("selection_mode") or ""),
        "readiness_status": readiness_status,
        "failure_reason": failure_reason,
        "project_root": str(project_root),
        "prototype_root": prototype_root,
        "entry_html": entry_html,
        "board_url": board_url,
        "host": host,
        "port": int(port),
        "open_requested": bool(open_browser),
        "runtime_source": {
            "surface": "operator-workbench-bundle",
            "prototype_status": {
                "status": str(status.get("status") or "missing"),
                "review_status": str(status.get("review_status") or "missing"),
                "gate_ready": bool(status.get("gate_ready")),
                "drift_status": str(status.get("drift_status") or "missing"),
            },
            "runtime_projection": {
                "project_key": str(runtime_projection.get("project_key") or ""),
                "current_stage": str(board.get("current_stage") or lifecycle.get("current_stage") or ""),
                "progress_label": str(board.get("progress_label") or lifecycle.get("progress_label") or ""),
                "next_action": str(board.get("next_action") or ""),
                "runtime_mode": str(runtime.get("mode") or ""),
                "health_status": str(board.get("health_status") or ""),
            },
        },
        "operator_surface": {
            "workbench": "operator",
            "public_summary_command": f"beacon status --board --project-root {project_root} --version {version}",
            "launcher_command": (
                f"beacon board --project {project_root} --version {version}"
                + (f" --feature {selected_feature}" if selected_feature else "")
            ),
            "prototype_preview": _entrypoint_relpath(status) if status else "preview.html",
        },
        "view_contract": {
            "views": list((operator_workbench.get("views") if isinstance(operator_workbench.get("views"), list) else [])),
            "lifecycle_first": True,
            "public_vs_operator_boundary": "separated",
        },
        "operator_workbench": operator_workbench,
        "candidates": list(resolution.get("candidates") or []),
    }
