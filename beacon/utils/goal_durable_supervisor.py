"""Durable supervisor + heartbeat/log/checkpoint for product-goal (v1.6.7).

Opt-in only: attach via ``beacon goal supervise``.
Default heartbeat interval: 120 seconds.
P2 memory: sqlite FTS (non-authoritative).
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json

DEFAULT_HEARTBEAT_INTERVAL_SEC = 120
MIN_HEARTBEAT_INTERVAL_SEC = 30
REASON_HOST_INTERRUPTED = "host_interrupted"
REASON_STAGE_BLOCKED = "stage_blocked"
REASON_VERIFIER_REQUIRED = "product_goal_complete_requires_verifier"
REASON_NOT_FOUND = "product_goal_run_not_found"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except Exception:  # noqa: BLE001
        return None


def goal_run_dir(project_root: Path, run_id: str) -> Path:
    return Path(project_root) / ".beacon" / "state" / "product-goal" / run_id


def execution_log_path(project_root: Path, run_id: str) -> Path:
    return goal_run_dir(project_root, run_id) / "execution.jsonl"


def checkpoint_path(project_root: Path, run_id: str) -> Path:
    return goal_run_dir(project_root, run_id) / "checkpoint.json"


def memory_db_path(project_root: Path, run_id: str) -> Path:
    return goal_run_dir(project_root, run_id) / "memory.fts.sqlite"


def ensure_run_dir(project_root: Path, run_id: str) -> Path:
    d = goal_run_dir(project_root, run_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def append_execution_log(
    project_root: Path,
    run_id: str,
    *,
    stage: str,
    event: str,
    summary: str,
    substep: str = "",
    cmd: str = "",
    exit_code: int | None = None,
    refs: list[str] | None = None,
    host: str = "cli",
) -> dict[str, Any]:
    """Append-only execution log. Never truncates/overwrites the JSONL file."""
    ensure_run_dir(project_root, run_id)
    path = execution_log_path(project_root, run_id)
    row: dict[str, Any] = {
        "ts": now_iso(),
        "run_id": run_id,
        "stage": str(stage or ""),
        "event": str(event or ""),
        "substep": str(substep or ""),
        "cmd": str(cmd or ""),
        "summary": str(summary or "")[:240],
        "refs": list(refs or []),
        "host": host,
    }
    if exit_code is not None:
        row["exit_code"] = int(exit_code)
    # Append only — open in append mode, never 'w'
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_execution_log_tail(project_root: Path, run_id: str, *, limit: int = 5) -> list[dict[str, Any]]:
    path = execution_log_path(project_root, run_id)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-max(1, limit) :]:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                out.append(obj)
        except Exception:  # noqa: BLE001
            continue
    return out


def write_checkpoint(
    project_root: Path,
    run_id: str,
    *,
    stage: str,
    last_substep: str,
    next_action: str,
    open_blockers: list[dict[str, str]] | None = None,
    last_heartbeat_at: str = "",
    recent_heartbeats: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    ensure_run_dir(project_root, run_id)
    pack = {
        "schema_version": "1.0",
        "run_id": run_id,
        "stage": str(stage or ""),
        "last_substep": str(last_substep or ""),
        "next_action": str(next_action or "")[:240],
        "open_blockers": list(open_blockers or []),
        "last_heartbeat_at": last_heartbeat_at or "",
        "recent_heartbeats": list(recent_heartbeats or [])[:5],
        "log_path": str(execution_log_path(project_root, run_id).relative_to(Path(project_root))),
        "refs": [],
        "updated_at": now_iso(),
    }
    write_json(checkpoint_path(project_root, run_id), pack)
    append_execution_log(
        project_root,
        run_id,
        stage=stage,
        event="checkpoint",
        summary=f"checkpoint next_action={pack['next_action'][:80]}",
        substep=last_substep,
    )
    return pack


def load_checkpoint(project_root: Path, run_id: str) -> dict[str, Any]:
    path = checkpoint_path(project_root, run_id)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def normalize_interval(interval_sec: int | None) -> int:
    value = int(interval_sec if interval_sec is not None else DEFAULT_HEARTBEAT_INTERVAL_SEC)
    if value < MIN_HEARTBEAT_INTERVAL_SEC:
        return MIN_HEARTBEAT_INTERVAL_SEC
    return value


def build_resume_pack(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Digest-only resume injection. Never embeds full execution.jsonl or chat."""
    run_id = str(payload.get("run_id") or "")
    project_root = Path(project_root)
    cp = load_checkpoint(project_root, run_id)
    recent = read_execution_log_tail(project_root, run_id, limit=5)
    heartbeats = [
        {"ts": str(r.get("ts") or ""), "summary": str(r.get("summary") or "")}
        for r in recent
        if str(r.get("event") or "") == "heartbeat"
    ]
    if not heartbeats:
        heartbeats = [{"ts": str(r.get("ts") or ""), "summary": str(r.get("summary") or "")} for r in recent]
    blockers: list[dict[str, str]] = []
    if payload.get("reason_code"):
        blockers.append(
            {
                "reason_code": str(payload.get("reason_code") or ""),
                "summary": str(payload.get("reason_code") or ""),
            }
        )
    if payload.get("stall_flag"):
        blockers.append({"reason_code": "stall_flag", "summary": "idle without heartbeat"})
    for item in cp.get("open_blockers") or []:
        if isinstance(item, dict):
            blockers.append(
                {
                    "reason_code": str(item.get("reason_code") or ""),
                    "summary": str(item.get("summary") or "")[:240],
                }
            )
    pack = {
        "schema_version": "1.0",
        "run_id": run_id,
        "utterance": str(payload.get("utterance") or "")[:500],
        "done_when": list(payload.get("done_when") or []),
        "current_stage": str(payload.get("current_stage") or ""),
        "status": str(payload.get("status") or ""),
        "last_substep": str(payload.get("last_substep") or cp.get("last_substep") or ""),
        "next_action": str(cp.get("next_action") or "continue current stage against frozen truth"),
        "recent_heartbeats": heartbeats[-5:],
        "open_blockers": blockers[:10],
        "log_path": str(execution_log_path(project_root, run_id).as_posix()),
        "checkpoint_path": str(checkpoint_path(project_root, run_id).as_posix()),
        "authority_note": "digest only; full chat/jsonl are not authority; complete needs verifier refs",
        "supervisor_attached": bool((payload.get("supervisor") or {}).get("attached")),
        "last_heartbeat_at": str(payload.get("last_heartbeat_at") or ""),
        "stall_flag": bool(payload.get("stall_flag")),
    }
    return pack


def detect_stall(payload: dict[str, Any], *, now: datetime | None = None) -> bool:
    """True if stage needs work and idle >= heartbeat_interval without heartbeat."""
    status = str(payload.get("status") or "")
    if status in {"completed", "blocked"}:
        return False
    stage = str(payload.get("current_stage") or "")
    # stages that typically need ongoing host/worker activity
    if stage not in {"implement", "qa", "design", "truth", "plan"}:
        # still allow stall if explicitly stage_active-ish
        if stage in {"release", "complete_gate", ""}:
            return False
    interval = normalize_interval(payload.get("heartbeat_interval_sec"))
    last = _parse_iso(str(payload.get("last_heartbeat_at") or ""))
    created = _parse_iso(str(payload.get("created_at") or ""))
    anchor = last or created
    if anchor is None:
        return False
    current = now or _utc_now()
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=timezone.utc)
    idle = (current - anchor).total_seconds()
    return idle >= float(interval)


def mark_host_interrupted(payload: dict[str, Any], *, substep: str = "") -> dict[str, Any]:
    payload = dict(payload)
    payload["status"] = "running"
    payload["blocked"] = False
    payload["reason_code"] = REASON_HOST_INTERRUPTED
    payload["stall_flag"] = True
    if substep:
        payload["last_substep"] = substep
    elif not payload.get("last_substep"):
        payload["last_substep"] = str(payload.get("current_stage") or "unknown")
    hist = list(payload.get("history") or [])
    hist.append(
        {
            "event": "host_interrupted",
            "reason_code": REASON_HOST_INTERRUPTED,
            "substep": payload.get("last_substep"),
            "at": now_iso(),
        }
    )
    payload["history"] = hist
    return payload


def attach_supervisor(
    payload: dict[str, Any],
    *,
    interval_sec: int | None = None,
) -> dict[str, Any]:
    """Opt-in attach. Must never be called from goal run creation."""
    payload = dict(payload)
    interval = normalize_interval(interval_sec if interval_sec is not None else payload.get("heartbeat_interval_sec"))
    session_id = f"sup-{uuid.uuid4().hex[:10]}"
    payload["supervisor"] = {
        "attached": True,
        "session_id": session_id,
        "state": "active",
        "interval_sec": interval,
        "attached_at": now_iso(),
    }
    payload["heartbeat_interval_sec"] = interval
    hist = list(payload.get("history") or [])
    hist.append({"event": "supervise_attach", "session_id": session_id, "interval_sec": interval, "at": now_iso()})
    payload["history"] = hist
    return payload


def detach_supervisor(payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    sup = dict(payload.get("supervisor") or {})
    sup["attached"] = False
    sup["state"] = "stopped"
    payload["supervisor"] = sup
    hist = list(payload.get("history") or [])
    hist.append({"event": "supervise_detach", "at": now_iso()})
    payload["history"] = hist
    return payload


def record_heartbeat_on_payload(
    payload: dict[str, Any],
    *,
    summary: str,
    substep: str = "",
) -> dict[str, Any]:
    payload = dict(payload)
    ts = now_iso()
    payload["last_heartbeat_at"] = ts
    payload["stall_flag"] = False
    if payload.get("reason_code") == REASON_HOST_INTERRUPTED:
        payload["reason_code"] = ""
    if substep:
        payload["last_substep"] = substep
    hist = list(payload.get("history") or [])
    hist.append({"event": "heartbeat", "summary": str(summary)[:240], "substep": substep, "at": ts})
    payload["history"] = hist
    return payload


def plan_tick_execute(payload: dict[str, Any]) -> dict[str, Any]:
    """Return worker dispatch plan for tick --execute (does not claim QA pass)."""
    stage = str(payload.get("current_stage") or "")
    if stage == "implement":
        return {
            "dispatch": "ralph",
            "action": "delegate_ralph",
            "command": "beacon goal delegate-ralph --run-id {run_id}",
            "resume_action": "load_next_skill",
            "skill_hint": "beacon-gen-implement",
        }
    if stage == "qa":
        lakes = list(payload.get("lakes") or [])
        feature = str(payload.get("feature") or (lakes[0] if lakes else ""))
        return {
            "dispatch": "qa",
            "action": "beacon_qa_run",
            "command": f'beacon qa run {feature or "<feature>"} -v {payload.get("version") or "auto"}',
            "feature": feature,
            "resume_action": "run_cli",
        }
    if stage == "design":
        return {
            "dispatch": "design",
            "action": "design_stage",
            "command": "beacon goal design-stage --run-id {run_id}",
            "resume_action": "run_cli",
        }
    if stage == "release":
        return {
            "dispatch": "none",
            "action": "human_release_gate",
            "command": "",
            "resume_action": "await_human_confirmation",
            "note": "release never auto-confirmed by supervise/tick",
        }
    return {
        "dispatch": "none",
        "action": "record_only",
        "command": "",
        "resume_action": "load_next_skill",
    }


def supervise_once(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Single supervise poll: detect stall, optional dispatch plan, heartbeat."""
    project_root = Path(project_root)
    run_id = str(payload.get("run_id") or "")
    sup = payload.get("supervisor") if isinstance(payload.get("supervisor"), dict) else {}
    if not bool(sup.get("attached")):
        return {
            "status": "detached",
            "blocked": False,
            "reason_code": "supervisor_not_attached",
            "payload": payload,
            "note": "opt-in only: run `beacon goal supervise --run-id ...`",
        }
    result: dict[str, Any] = {"status": "ok", "actions": []}
    # stall detection
    if detect_stall(payload):
        payload = mark_host_interrupted(payload)
        append_execution_log(
            project_root,
            run_id,
            stage=str(payload.get("current_stage") or ""),
            event="host_interrupt",
            summary="stall: idle >= heartbeat_interval without heartbeat",
            substep=str(payload.get("last_substep") or ""),
        )
        result["actions"].append("host_interrupted_stall")
        result["stall"] = True
    # heartbeat from supervisor poll
    payload = record_heartbeat_on_payload(
        payload,
        summary="supervisor poll heartbeat",
        substep=str(payload.get("last_substep") or payload.get("current_stage") or ""),
    )
    append_execution_log(
        project_root,
        run_id,
        stage=str(payload.get("current_stage") or ""),
        event="heartbeat",
        summary="supervisor poll heartbeat",
        substep=str(payload.get("last_substep") or ""),
        host="cli",
    )
    result["actions"].append("heartbeat")
    # worker plan (advisory; actual exec may be requested by tick --execute)
    plan = plan_tick_execute(payload)
    result["worker_plan"] = plan
    if plan.get("dispatch") in {"ralph", "qa", "design"}:
        append_execution_log(
            project_root,
            run_id,
            stage=str(payload.get("current_stage") or ""),
            event="worker_dispatch",
            summary=f"plan dispatch={plan.get('dispatch')} action={plan.get('action')}",
            cmd=str(plan.get("command") or ""),
        )
        result["actions"].append(f"planned_{plan.get('dispatch')}")
    if str(payload.get("current_stage") or "") == "release":
        result["actions"].append("release_human_gate_only")
    # never complete without verifier
    if payload.get("status") == "completed":
        verifier = payload.get("verifier") if isinstance(payload.get("verifier"), dict) else {}
        if not (verifier.get("present") and list(verifier.get("refs") or [])):
            payload["status"] = "awaiting_verifier"
            payload["reason_code"] = REASON_VERIFIER_REQUIRED
            result["actions"].append("blocked_self_cert_complete")
    # update supervisor state
    sup = dict(payload.get("supervisor") or {})
    sup["state"] = "polling"
    sup["last_poll_at"] = now_iso()
    payload["supervisor"] = sup
    result["payload"] = payload
    result["resume_pack"] = build_resume_pack(project_root, payload)
    return result


# --- P2 sqlite FTS (non-authoritative) ---


def memory_reindex(project_root: Path, run_id: str) -> dict[str, Any]:
    project_root = Path(project_root)
    ensure_run_dir(project_root, run_id)
    db_path = memory_db_path(project_root, run_id)
    log_path = execution_log_path(project_root, run_id)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("DROP TABLE IF EXISTS goal_log_fts")
        conn.execute(
            """
            CREATE VIRTUAL TABLE goal_log_fts USING fts5(
                summary, stage, event, substep, ts,
                content=''
            )
            """
        )
        count = 0
        if log_path.exists():
            for line in log_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                if not isinstance(row, dict):
                    continue
                conn.execute(
                    "INSERT INTO goal_log_fts(summary, stage, event, substep, ts) VALUES (?,?,?,?,?)",
                    (
                        str(row.get("summary") or ""),
                        str(row.get("stage") or ""),
                        str(row.get("event") or ""),
                        str(row.get("substep") or ""),
                        str(row.get("ts") or ""),
                    ),
                )
                count += 1
        conn.commit()
        return {
            "status": "ok",
            "indexed": count,
            "db_path": str(db_path),
            "authority": "support_advisory",
            "note": "FTS results must not complete a goal or replace verifier",
        }
    finally:
        conn.close()


def memory_search(project_root: Path, run_id: str, query: str, *, limit: int = 10) -> dict[str, Any]:
    project_root = Path(project_root)
    db_path = memory_db_path(project_root, run_id)
    if not db_path.exists():
        return {
            "status": "empty",
            "hits": [],
            "authority": "support_advisory",
            "note": "run memory reindex first; non-authoritative",
        }
    q = str(query or "").strip()
    if not q:
        return {"status": "empty", "hits": [], "authority": "support_advisory"}
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute(
            "SELECT summary, stage, event, substep, ts FROM goal_log_fts WHERE goal_log_fts MATCH ? LIMIT ?",
            (q, int(limit)),
        )
        hits = [
            {
                "summary": r[0],
                "stage": r[1],
                "event": r[2],
                "substep": r[3],
                "ts": r[4],
            }
            for r in cur.fetchall()
        ]
        return {
            "status": "ok",
            "hits": hits,
            "authority": "support_advisory",
            "note": "must not override verifier/scorecard",
            "can_complete": False,
        }
    except sqlite3.OperationalError as exc:
        return {
            "status": "error",
            "error": str(exc),
            "hits": [],
            "authority": "support_advisory",
            "can_complete": False,
        }
    finally:
        conn.close()


def assert_log_append_only_policy() -> None:
    """Documentation/test helper: public API only opens JSONL in append mode."""
    # Implemented by append_execution_log using open(..., "a")
    return None
