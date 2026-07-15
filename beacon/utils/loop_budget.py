"""Loop token budget ledger and preflight helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.loop_patterns import registry_path, validate_pattern_registry

LEDGER_SCHEMA_VERSION = "loop-budget-ledger-v1"


def budget_ledger_path(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / ".beacon" / "loop" / "budget-ledger.json"


def pause_all_path(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / ".beacon" / "loop" / "pause-all"


def today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_budget_ledger(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"schema_version": LEDGER_SCHEMA_VERSION, "records": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema_version": LEDGER_SCHEMA_VERSION, "records": [], "corrupt": True}
    if not isinstance(payload, dict):
        return {"schema_version": LEDGER_SCHEMA_VERSION, "records": [], "corrupt": True}
    records = payload.get("records") if isinstance(payload.get("records"), list) else []
    return {**payload, "schema_version": str(payload.get("schema_version") or LEDGER_SCHEMA_VERSION), "records": [r for r in records if isinstance(r, dict)]}


def append_budget_record(
    project_root: Path,
    *,
    pattern_id: str,
    run_id: str,
    estimated_tokens: int,
    actual_tokens: int | None = None,
    date: str | None = None,
    source: str = "manual",
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    path = ledger_path or budget_ledger_path(project_root)
    payload = load_budget_ledger(path)
    record = {
        "pattern_id": pattern_id,
        "run_id": run_id,
        "estimated_tokens": int(estimated_tokens or 0),
        "actual_tokens": actual_tokens if actual_tokens is not None else None,
        "date": date or today_utc(),
        "source": source,
    }
    records = list(payload.get("records") or [])
    records.append(record)
    output = {"schema_version": LEDGER_SCHEMA_VERSION, "records": records}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def _record_tokens(record: dict[str, Any]) -> int:
    value = record.get("actual_tokens")
    if value is None:
        value = record.get("estimated_tokens")
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def daily_totals(records: list[dict[str, Any]], *, date: str) -> dict[str, Any]:
    per_pattern: dict[str, int] = {}
    total = 0
    for record in records:
        if str(record.get("date") or "") != date:
            continue
        tokens = _record_tokens(record)
        pattern_id = str(record.get("pattern_id") or "").strip()
        if not pattern_id:
            continue
        per_pattern[pattern_id] = per_pattern.get(pattern_id, 0) + tokens
        total += tokens
    return {"date": date, "per_pattern": per_pattern, "project_total": total}


def registry_budget_caps(project_root: Path, *, version: str) -> dict[str, int]:
    validation = validate_pattern_registry(registry_path(project_root, version=version))
    caps: dict[str, int] = {}
    for pattern in validation.get("patterns") or []:
        if not isinstance(pattern, dict):
            continue
        pattern_id = str(pattern.get("id") or "").strip()
        try:
            cap = int(pattern.get("daily_cap") or 0)
        except (TypeError, ValueError):
            cap = 0
        if pattern_id and cap > 0:
            caps[pattern_id] = cap
    return caps


def build_loop_budget_status(project_root: Path, *, version: str, date: str | None = None, ledger_path: Path | None = None) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    day = date or today_utc()
    ledger = load_budget_ledger(ledger_path or budget_ledger_path(root))
    totals = daily_totals(list(ledger.get("records") or []), date=day)
    caps = registry_budget_caps(root, version=version)
    remaining = {pattern: cap - int(totals["per_pattern"].get(pattern, 0)) for pattern, cap in caps.items()}
    exceeded = sorted(pattern for pattern, value in remaining.items() if value < 0)
    kill_switch = pause_all_path(root).exists()
    blocked = bool(exceeded or kill_switch)
    reason_code = "loop_kill_switch_active" if kill_switch else "loop_budget_exceeded" if exceeded else ""
    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "ok",
        "blocked": blocked,
        "reason_code": reason_code,
        "version": version,
        "date": day,
        "totals": totals,
        "caps": caps,
        "remaining": remaining,
        "exceeded_patterns": exceeded,
        "kill_switch_active": kill_switch,
        "ledger_path": str((ledger_path or budget_ledger_path(root)).resolve()),
    }


def unattended_loop_preflight(
    project_root: Path,
    *,
    version: str,
    pattern_id: str,
    estimated_tokens: int = 0,
    date: str | None = None,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    if pause_all_path(root).exists():
        return {"schema_version": "1.0", "status": "blocked", "blocked": True, "reason_code": "loop_kill_switch_active"}
    status = build_loop_budget_status(root, version=version, date=date, ledger_path=ledger_path)
    caps = status.get("caps") if isinstance(status.get("caps"), dict) else {}
    totals = status.get("totals") if isinstance(status.get("totals"), dict) else {}
    per_pattern = totals.get("per_pattern") if isinstance(totals.get("per_pattern"), dict) else {}
    cap = int(caps.get(pattern_id, 0) or 0)
    used = int(per_pattern.get(pattern_id, 0) or 0)
    if cap > 0 and used + int(estimated_tokens or 0) > cap:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "loop_budget_exceeded",
            "pattern_id": pattern_id,
            "used_tokens": used,
            "estimated_tokens": int(estimated_tokens or 0),
            "daily_cap": cap,
        }
    return {"schema_version": "1.0", "status": "pass", "blocked": False, "reason_code": "", "pattern_id": pattern_id}
