"""Machine-local store for v1.3.4 runtime projection envelopes."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json


def runtime_ledger_root() -> Path:
    override = str(os.environ.get("BEACON_RUNTIME_LEDGER_ROOT", "") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / ".beacon" / "runtime-ledger").expanduser().resolve()


def runtime_ledger_db_path() -> Path:
    return runtime_ledger_root() / "runtime-ledger.sqlite3"


def pocketbase_projection_root() -> Path:
    return runtime_ledger_root() / "pocketbase"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _connect() -> sqlite3.Connection:
    db_path = runtime_ledger_db_path()
    _ensure_parent(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    ensure_runtime_projection_schema(conn)
    return conn


def ensure_runtime_projection_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_key TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            project_root TEXT NOT NULL,
            docs_version TEXT NOT NULL,
            project_kind TEXT NOT NULL,
            current_stage TEXT NOT NULL,
            progress_label TEXT NOT NULL,
            blocker TEXT NOT NULL,
            next_action TEXT NOT NULL,
            runtime_mode TEXT NOT NULL,
            debug_state TEXT NOT NULL,
            runtime_corroboration TEXT NOT NULL,
            source_hash TEXT NOT NULL,
            projection_seq TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS git_scopes (
            project_key TEXT NOT NULL,
            scope_key TEXT NOT NULL,
            repo_root TEXT NOT NULL,
            repo_name TEXT NOT NULL,
            branch TEXT NOT NULL,
            commit_sha TEXT NOT NULL,
            dirty INTEGER NOT NULL DEFAULT 0,
            role TEXT NOT NULL,
            worktree_path TEXT NOT NULL,
            source_priority TEXT NOT NULL,
            PRIMARY KEY (project_key, scope_key)
        );

        CREATE TABLE IF NOT EXISTS projection_writes (
            projection_seq TEXT PRIMARY KEY,
            project_key TEXT NOT NULL,
            source_hash TEXT NOT NULL,
            write_status TEXT NOT NULL,
            preflight_status TEXT NOT NULL,
            wrote_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );
        """
    )
    conn.commit()


def preflight_projection_write(envelope: dict[str, Any]) -> dict[str, Any]:
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    preflight = projection.get("preflight") if isinstance(projection.get("preflight"), dict) else {}
    conflicts = preflight.get("conflicts") if isinstance(preflight.get("conflicts"), list) else []
    raw_status = str(
        projection.get("preflight_status")
        or preflight.get("status")
        or ("conflicted" if conflicts else "pass")
    ).strip()
    normalized_status = {
        "ok": "pass",
        "pass": "pass",
        "partial": "partial",
        "conflicted": "conflicted",
        "blocked": "blocked",
    }.get(raw_status, "conflicted" if conflicts else "pass")
    return {
        "status": normalized_status,
        "conflicts": [str(item) for item in conflicts if str(item).strip()],
        "source_hash": str(projection.get("source_hash") or ""),
        "projection_seq": str(projection.get("projection_seq") or ""),
    }


def _project_row(envelope: dict[str, Any]) -> tuple[Any, ...]:
    board = envelope.get("board") if isinstance(envelope.get("board"), dict) else {}
    lifecycle = envelope.get("lifecycle") if isinstance(envelope.get("lifecycle"), dict) else {}
    runtime = envelope.get("runtime") if isinstance(envelope.get("runtime"), dict) else {}
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    runtime_corroboration = runtime.get("runtime_corroboration") if isinstance(runtime.get("runtime_corroboration"), dict) else {}
    next_step = lifecycle.get("next_step") if isinstance(lifecycle.get("next_step"), dict) else {}
    return (
        str(envelope.get("project_key") or ""),
        str(envelope.get("display_name") or ""),
        str(envelope.get("project_root") or ""),
        str(envelope.get("docs_version") or ""),
        str(envelope.get("project_kind") or ""),
        str(board.get("current_stage") or ""),
        str(board.get("progress_label") or ""),
        str(board.get("blocker") or ""),
        str(board.get("next_action") or str(next_step.get("action") or "")),
        str((runtime.get("mode") or "idle")),
        str(board.get("debug_state") or ""),
        str(runtime_corroboration.get("status") or "missing"),
        str(projection.get("source_hash") or ""),
        str(projection.get("projection_seq") or ""),
        now_iso(),
        json.dumps(envelope, ensure_ascii=False, sort_keys=True),
    )


def sync_projection(envelope: dict[str, Any]) -> dict[str, Any]:
    preflight = preflight_projection_write(envelope)
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    if preflight["status"] in {"conflicted", "blocked"}:
        return {
            "status": preflight["status"],
            "preflight": preflight,
            "db_path": str(runtime_ledger_db_path()),
            "pocketbase_root": str(pocketbase_projection_root()),
        }

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO projects (
                project_key, display_name, project_root, docs_version, project_kind, current_stage,
                progress_label, blocker, next_action, runtime_mode, debug_state, runtime_corroboration,
                source_hash, projection_seq, updated_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_key) DO UPDATE SET
                display_name=excluded.display_name,
                project_root=excluded.project_root,
                docs_version=excluded.docs_version,
                project_kind=excluded.project_kind,
                current_stage=excluded.current_stage,
                progress_label=excluded.progress_label,
                blocker=excluded.blocker,
                next_action=excluded.next_action,
                runtime_mode=excluded.runtime_mode,
                debug_state=excluded.debug_state,
                runtime_corroboration=excluded.runtime_corroboration,
                source_hash=excluded.source_hash,
                projection_seq=excluded.projection_seq,
                updated_at=excluded.updated_at,
                payload_json=excluded.payload_json
            """,
            _project_row(envelope),
        )
        project_key = str(envelope.get("project_key") or "")
        conn.execute("DELETE FROM git_scopes WHERE project_key = ?", (project_key,))
        for scope in envelope.get("git_scopes", []) if isinstance(envelope.get("git_scopes"), list) else []:
            if not isinstance(scope, dict):
                continue
            conn.execute(
                """
                INSERT INTO git_scopes (
                    project_key, scope_key, repo_root, repo_name, branch, commit_sha, dirty, role, worktree_path, source_priority
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_key,
                    str(scope.get("scope_key") or ""),
                    str(scope.get("repo_root") or ""),
                    str(scope.get("repo_name") or ""),
                    str(scope.get("branch") or ""),
                    str(scope.get("commit") or ""),
                    1 if bool(scope.get("dirty")) else 0,
                    str(scope.get("role") or ""),
                    str(scope.get("worktree_path") or ""),
                    str(scope.get("source_priority") or ""),
                ),
            )
        conn.execute(
            """
            INSERT INTO projection_writes (
                projection_seq, project_key, source_hash, write_status, preflight_status, wrote_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(projection_seq) DO UPDATE SET
                project_key=excluded.project_key,
                source_hash=excluded.source_hash,
                write_status=excluded.write_status,
                preflight_status=excluded.preflight_status,
                wrote_at=excluded.wrote_at,
                payload_json=excluded.payload_json
            """,
            (
                str(projection.get("projection_seq") or ""),
                project_key,
                str(projection.get("source_hash") or ""),
                "applied",
                str(preflight.get("status") or "pass"),
                now_iso(),
                json.dumps(envelope, ensure_ascii=False, sort_keys=True),
            ),
        )
        conn.commit()

    mirror_paths = write_pocketbase_projection_pack(envelope)
    return {
        "status": "applied",
        "preflight": preflight,
        "db_path": str(runtime_ledger_db_path()),
        "pocketbase_root": str(pocketbase_projection_root()),
        "mirror_paths": mirror_paths,
    }


def write_pocketbase_projection_pack(envelope: dict[str, Any]) -> dict[str, str]:
    root = pocketbase_projection_root()
    collections_root = root / "collections"
    project_key = str(envelope.get("project_key") or "")
    project_path = collections_root / "projects" / f"{project_key}.json"
    scopes_path = collections_root / "git_scopes" / f"{project_key}.json"
    writes_path = collections_root / "projection_writes" / f"{project_key}.json"

    write_json(project_path, envelope)
    write_json(
        scopes_path,
        {
            "project_key": project_key,
            "git_scopes": envelope.get("git_scopes", []),
        },
    )
    write_json(
        writes_path,
        {
            "project_key": project_key,
            "projection": envelope.get("projection", {}),
        },
    )
    return {
        "project": str(project_path),
        "git_scopes": str(scopes_path),
        "projection_writes": str(writes_path),
    }


def list_projects(limit: int = 20) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT project_key, display_name, project_root, docs_version, project_kind, current_stage,
                   progress_label, blocker, next_action, runtime_mode, debug_state, runtime_corroboration,
                   source_hash, projection_seq, updated_at
            FROM projects
            ORDER BY updated_at DESC, project_key ASC
            LIMIT ?
            """,
            (max(1, limit),),
        ).fetchall()
    return [dict(row) for row in rows]


def load_project_detail(project_key: str) -> dict[str, Any]:
    with _connect() as conn:
        row = conn.execute("SELECT payload_json FROM projects WHERE project_key = ?", (project_key,)).fetchone()
    if row is None:
        return {}
    try:
        payload = json.loads(str(row["payload_json"]))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}
