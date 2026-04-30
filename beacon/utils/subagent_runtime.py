"""Shared runtime helpers for bounded subagent/team execution."""

from __future__ import annotations

import html
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_trace_dir
from beacon.utils.runtime import now_iso, write_json


def resolve_team_runtime(requested: str) -> str:
    value = str(requested or "file").strip().lower()
    if value not in {"file", "tmux", "auto"}:
        return "file"
    if value == "auto":
        return "file"
    return value


def tmux_available() -> bool:
    result = subprocess.run(["/bin/sh", "-lc", "command -v tmux >/dev/null 2>&1"], capture_output=True, text=True, check=False)
    return result.returncode == 0


def team_session_name(team_name: str) -> str:
    return str(team_name or "").replace("/", "-").replace(" ", "-")


def worker_spec_path(project_root: Path, *, team_name: str, role: str) -> Path:
    return project_root / ".beacon" / "subagents" / team_name / "workers" / f"{role}.spec.json"


def worker_result_path(project_root: Path, *, team_name: str, role: str) -> Path:
    return project_root / ".beacon" / "subagents" / team_name / "workers" / f"{role}.result.json"


def write_worker_spec(project_root: Path, *, team_name: str, role: str, payload: dict[str, Any]) -> Path:
    path = worker_spec_path(project_root, team_name=team_name, role=role)
    write_json(path, payload)
    return path


def load_worker_spec(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"invalid worker spec: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"worker spec must be object: {path}")
    return payload


def team_hud_json_path(project_root: Path, *, team_name: str) -> Path:
    return project_root / ".beacon" / "state" / "team-hud" / f"{team_name}.json"


def team_hud_html_path(project_root: Path, *, version: str, feature: str, run_id: str, surface_dir: str) -> Path:
    if surface_dir in {"qa-team", "native-team", "codex-subagents"}:
        return machine_trace_dir(project_root, version, surface_dir, feature, run_id) / "index.html"
    return (
        project_root
        / "docs"
        / "beacon"
        / version
        / "execution"
        / surface_dir
        / feature
        / run_id
        / "index.html"
    )


def _render_team_hud_html(payload: dict[str, Any]) -> str:
    roles = payload.get("roles") if isinstance(payload.get("roles"), list) else []
    cards = []
    for item in roles:
        if not isinstance(item, dict):
            continue
        cards.append(
            "".join(
                [
                    '<article class="card">',
                    f"<h2>{html.escape(str(item.get('role', '')))}</h2>",
                    f"<p><strong>Status:</strong> {html.escape(str(item.get('status', '')))}</p>",
                    f"<p><strong>Worker:</strong> {html.escape(str(item.get('worker_id', '')))}</p>",
                    f"<p><strong>Pane:</strong> {html.escape(str(item.get('pane_id', '')))}</p>",
                    f"<p><strong>JSON:</strong> {html.escape(str(item.get('json', '')))}</p>",
                    f"<p><strong>Markdown:</strong> {html.escape(str(item.get('markdown', '')))}</p>",
                    "</article>",
                ]
            )
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Beacon Team HUD</title>
  <style>
    body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin: 24px; background: #0f172a; color: #e2e8f0; }}
    .meta {{ margin-bottom: 24px; padding: 16px; border: 1px solid #334155; border-radius: 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
    .card {{ border: 1px solid #334155; border-radius: 12px; padding: 16px; background: #111827; }}
    h1, h2 {{ margin-top: 0; }}
    p {{ word-break: break-word; }}
  </style>
</head>
<body>
  <section class="meta">
    <h1>{html.escape(str(payload.get("team_name", "")))}</h1>
    <p><strong>Feature:</strong> {html.escape(str(payload.get("feature", "")))}</p>
    <p><strong>Version:</strong> {html.escape(str(payload.get("version", "")))}</p>
    <p><strong>Runtime:</strong> {html.escape(str(payload.get("runtime", "")))}</p>
    <p><strong>tmux session:</strong> {html.escape(str(payload.get("tmux_session", "")))}</p>
    <p><strong>Generated:</strong> {html.escape(str(payload.get("generated_at", "")))}</p>
  </section>
  <section class="grid">
    {''.join(cards)}
  </section>
</body>
</html>
"""


def write_team_hud(
    project_root: Path,
    *,
    team_name: str,
    version: str,
    feature: str,
    run_id: str,
    surface_dir: str,
    runtime: str,
    tmux_session: str,
    roles: list[dict[str, Any]],
) -> dict[str, str]:
    payload = {
        "schema_version": "1.0",
        "team_name": team_name,
        "feature": feature,
        "version": version,
        "run_id": run_id,
        "runtime": runtime,
        "tmux_session": tmux_session,
        "generated_at": now_iso(),
        "roles": roles,
    }
    json_path = team_hud_json_path(project_root, team_name=team_name)
    html_path = team_hud_html_path(project_root, version=version, feature=feature, run_id=run_id, surface_dir=surface_dir)
    write_json(json_path, payload)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(_render_team_hud_html(payload), encoding="utf-8")
    return {
        "json": str(json_path.relative_to(project_root)),
        "html": str(html_path.relative_to(project_root)),
    }


def spawn_tmux_workers(
    project_root: Path,
    *,
    team_name: str,
    worker_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    if not tmux_available():
        raise RuntimeError("tmux is not available")
    session = team_session_name(team_name)
    root_text = shlex.quote(str(project_root))
    if not worker_specs:
        return {"tmux_session": session, "workers": []}
    first_role = str(worker_specs[0].get("role", "worker-1"))
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", session, "-n", first_role],
        check=True,
        capture_output=True,
        text=True,
    )
    for index, spec in enumerate(worker_specs[1:], start=1):
        subprocess.run(
            ["tmux", "split-window", "-t", session, "-d"],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(["tmux", "select-layout", "-t", session, "tiled"], check=True, capture_output=True, text=True)
    panes = subprocess.run(
        ["tmux", "list-panes", "-t", session, "-F", "#{pane_id} #{pane_index}"],
        check=True,
        capture_output=True,
        text=True,
    )
    pane_rows = [line.strip().split(" ", 1) for line in panes.stdout.splitlines() if line.strip()]
    pane_ids = [row[0] for row in pane_rows]
    for index, spec in enumerate(worker_specs):
        spec["pane_id"] = pane_ids[index] if index < len(pane_ids) else ""
        spec["tmux_session"] = session
        spec_path = shlex.quote(str(spec["spec_path"]))
        command = (
            f"cd {root_text} && "
            f"{shlex.quote(sys.executable)} -m beacon.main team worker-run --spec {spec_path}"
        )
        target = spec["pane_id"] or f"{session}.{index}"
        subprocess.run(
            ["tmux", "send-keys", "-t", str(target), command, "C-m"],
            check=True,
            capture_output=True,
            text=True,
        )
    return {"tmux_session": session, "workers": worker_specs}


def wait_for_worker_results(
    project_root: Path,
    *,
    team_name: str,
    roles: list[str],
    timeout_sec: int = 30,
) -> dict[str, dict[str, Any]]:
    deadline = time.time() + max(timeout_sec, 1)
    remaining = set(roles)
    results: dict[str, dict[str, Any]] = {}
    while remaining and time.time() < deadline:
        for role in list(remaining):
            path = worker_result_path(project_root, team_name=team_name, role=role)
            if not path.exists():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            if isinstance(payload, dict):
                results[role] = payload
                remaining.discard(role)
        if remaining:
            time.sleep(0.1)
    if remaining:
        raise RuntimeError(f"worker results missing for roles: {sorted(remaining)}")
    return results
