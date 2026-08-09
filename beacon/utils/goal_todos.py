"""Goal todo ownership (LoopX distillation; CAP-2 of beacon-goal-loopx-hybrid-v1612).

Distills LoopX task-lease / claim / supersede semantics (IP-016/019/020/022):
todos carry owner, claim, lease, successor and a per-todo capability gate.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

TODO_SCHEMA = "goal-todo.v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _todos(state: dict[str, Any]) -> list[dict[str, Any]]:
    todos = state.get("todos")
    if not isinstance(todos, list):
        todos = []
        state["todos"] = todos
    return todos


def _find(todos: list[dict[str, Any]], todo_id: str) -> dict[str, Any] | None:
    return next((t for t in todos if str(t.get("id") or "") == str(todo_id)), None)


def new_todo(todo_id: str, title: str, *, capability_gate: str = "") -> dict[str, Any]:
    return {
        "schema": TODO_SCHEMA,
        "id": str(todo_id),
        "title": str(title),
        "status": "open",
        "owner": "",
        "claim": "",
        "lease": "",
        "successor": "",
        "capability_gate": str(capability_gate),
        "history": [],
    }


def claim_todo(
    state: dict[str, Any],
    todo_id: str,
    agent_id: str,
    *,
    lease: str = "",
) -> dict[str, Any]:
    """Bind one owner + lease to an open todo (AC-002). Double claim is rejected."""
    todo = _find(_todos(state), todo_id)
    if todo is None:
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "todo_missing"}
    if todo.get("status") == "claimed":
        return {
            "schema": TODO_SCHEMA,
            "ok": False,
            "blocked": True,
            "reason_code": "double_claim",
            "owner": str(todo.get("owner") or ""),
        }
    if todo.get("status") == "done":
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "todo_done"}
    todo["status"] = "claimed"
    todo["owner"] = str(agent_id)
    todo["claim"] = _now()
    todo["lease"] = str(lease or "")
    todo.setdefault("history", []).append({"event": "claimed", "agent": str(agent_id), "at": _now()})
    return {"schema": TODO_SCHEMA, "ok": True, "blocked": False, "reason_code": "", "todo": todo}


def release_todo(
    state: dict[str, Any],
    todo_id: str,
    *,
    agent_id: str = "",
) -> dict[str, Any]:
    todo = _find(_todos(state), todo_id)
    if todo is None:
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "todo_missing"}
    if todo.get("status") != "claimed":
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "todo_not_claimed"}
    if agent_id and str(todo.get("owner") or "") != str(agent_id):
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "not_owner"}
    todo["status"] = "open"
    todo["owner"] = ""
    todo["lease"] = ""
    todo.setdefault("history", []).append({"event": "released", "at": _now()})
    return {"schema": TODO_SCHEMA, "ok": True, "blocked": False, "reason_code": ""}


def update_todo(state: dict[str, Any], todo_id: str, **fields: Any) -> dict[str, Any]:
    todo = _find(_todos(state), todo_id)
    if todo is None:
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "todo_missing"}
    allowed = {"status", "title", "lease", "capability_gate"}
    for key, value in fields.items():
        if key in allowed:
            todo[key] = value
    return {"schema": TODO_SCHEMA, "ok": True, "blocked": False, "reason_code": "", "todo": todo}


def supersede_todo(
    state: dict[str, Any],
    todo_id: str,
    successor_id: str,
    title: str,
    *,
    capability_gate: str = "",
) -> dict[str, Any]:
    """Replace a claimed todo with a successor, keeping history (AC-002)."""
    todos = _todos(state)
    todo = _find(todos, todo_id)
    if todo is None:
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "todo_missing"}
    if todo.get("status") != "claimed":
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "todo_not_claimed"}
    if _find(todos, successor_id) is not None:
        return {"schema": TODO_SCHEMA, "ok": False, "blocked": True, "reason_code": "successor_exists"}
    successor = new_todo(successor_id, title, capability_gate=capability_gate)
    successor["successor"] = ""
    todo["status"] = "superseded"
    todo["successor"] = str(successor_id)
    todo.setdefault("history", []).append(
        {"event": "superseded", "successor": str(successor_id), "at": _now()}
    )
    todos.append(successor)
    return {
        "schema": TODO_SCHEMA,
        "ok": True,
        "blocked": False,
        "reason_code": "",
        "superseded": todo,
        "successor": successor,
    }


def next_open_todo(state: dict[str, Any]) -> dict[str, Any] | None:
    """First open todo (ordered); unclaimed work is the next actionable slice (AC-002)."""
    for todo in _todos(state):
        if todo.get("status") == "open":
            return todo
    return None
