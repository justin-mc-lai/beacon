"""Compile browser-native tasks for agent-browser / browser-use runners."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.qa9 import normalize_qa_type
from beacon.utils.runtime import now_iso


def browser_task_path(tc_dir: Path) -> Path:
    return tc_dir / "browser-task.json"


def build_browser_task(
    *,
    item: dict[str, Any],
    qa_type: str,
    mode: str,
    project_root: Path,
    session: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_qa = normalize_qa_type(qa_type)
    scenario_family = str(item.get("scenario_family") or "happy").strip().lower() or "happy"
    scenario_id = str(item.get("scenario_id") or item.get("tc_id") or "").strip()
    feature = str(item.get("feature") or item.get("feature_slug") or "").strip()
    title = str(item.get("title") or item.get("assertion") or scenario_id or "browser scenario").strip()
    action_hint = {
        "happy": "Complete the primary browser flow and confirm success state.",
        "negative": "Trigger the negative path and verify the error or guard state.",
        "boundary": "Use boundary values and verify validation or resilience.",
        "recovery": "Refresh, navigate back, or retry and confirm recovery behavior.",
        "compatibility": "Verify equivalent behavior for compatibility/browser pair coverage.",
    }.get(scenario_family, "Execute the scenario and capture browser evidence.")
    payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "project_root": str(project_root),
        "feature": feature,
        "ac_id": str(item.get("ac_id") or "").strip(),
        "tc_id": str(item.get("tc_id") or "").strip(),
        "source_tc_id": str(item.get("source_tc_id") or item.get("tc_id") or "").strip(),
        "scenario_id": scenario_id,
        "scenario_family": scenario_family,
        "qa_type": normalized_qa,
        "mode": mode,
        "title": title,
        "assertion": str(item.get("assertion") or "").strip(),
        "target_url": str(item.get("target_url") or item.get("url") or "/").strip() or "/",
        "steps": [
            {
                "kind": "navigate",
                "target": str(item.get("target_url") or item.get("url") or "/").strip() or "/",
            },
            {
                "kind": "verify",
                "target": str(item.get("assertion") or title),
            },
        ],
        "runner_contract": {
            "exploratory_runner": str(item.get("exploratory_runner") or "playwright").strip() or "playwright",
            "deterministic_runner": str(item.get("deterministic_runner") or "playwright").strip() or "playwright",
            "replay_required": bool(item.get("replay_required")),
        },
        "coverage_axes": item.get("coverage_axes") if isinstance(item.get("coverage_axes"), list) else [],
        "instruction": f"{title}\n\n{action_hint}",
    }
    if isinstance(session, dict) and session:
        payload["session"] = {
            key: value
            for key, value in {
                "session_id": str(session.get("session_id") or "").strip(),
                "runner_type": str(session.get("runner_type") or "").strip(),
                "origin": str(session.get("origin") or "").strip(),
                "manifest_ref": str(session.get("manifest_ref") or "").strip(),
                "profile_ref": str(session.get("profile_ref") or "").strip(),
                "cookies_ref": str(session.get("cookies_ref") or "").strip(),
                "storage_state_ref": str(session.get("storage_state_ref") or "").strip(),
                "scopes": session.get("scopes") if isinstance(session.get("scopes"), list) else [],
            }.items()
            if value is not None and value != "" and value != []
        }
    return payload


def write_browser_task(
    *,
    tc_dir: Path,
    payload: dict[str, Any],
) -> Path:
    path = browser_task_path(tc_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def default_browser_runner_command(runner: str, *, qa_type: str) -> str:
    normalized_runner = str(runner or "").strip().lower()
    mode = "compatibility" if normalize_qa_type(qa_type) == "compatibility" else "functional"
    if normalized_runner == "browser-use":
        return f"python3 -m beacon.adapters.browser_use_runner --mode {mode}"
    if normalized_runner == "agent-browser":
        return f"python3 -m beacon.adapters.agent_browser_runner --mode {mode}"
    return ""
