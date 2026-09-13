"""Machine-local store for v1.3.4 runtime projection envelopes."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from beacon.utils.runtime_projection_board import write_public_board_pack
from beacon.utils.runtime import now_iso, read_json, write_json


def runtime_ledger_root() -> Path:
    override = str(os.environ.get("BEACON_RUNTIME_LEDGER_ROOT", "") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / ".beacon" / "runtime-ledger").expanduser().resolve()


def runtime_ledger_db_path() -> Path:
    return runtime_ledger_root() / "runtime-ledger.sqlite3"


def runtime_ledger_projection_root() -> Path:
    return runtime_ledger_root() / "projections"


def runtime_ledger_backups_root() -> Path:
    return runtime_ledger_root() / "backups"


def runtime_ledger_exports_root() -> Path:
    return runtime_ledger_root() / "exports"


def pocketbase_projection_root() -> Path:
    return runtime_ledger_root() / "pocketbase"


def pocketbase_public_root() -> Path:
    return pocketbase_projection_root() / "pb_public"


def pocketbase_managed_bin_path() -> Path:
    return pocketbase_projection_root() / "bin" / "pocketbase"


def pocketbase_control_plane_manifest_path() -> Path:
    return pocketbase_projection_root() / "control-plane.json"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_executable(path: Path, content: str) -> None:
    _ensure_parent(path)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def _sqlite_disabled() -> bool:
    value = str(os.environ.get("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", "") or "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _stable_hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_hash_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _transaction_events_root() -> Path:
    return runtime_ledger_root() / "transactions"


def _record_transaction_event(payload: dict[str, Any]) -> str:
    transaction_id = str(payload.get("transaction_id") or "").strip() or "unknown-transaction"
    target = _transaction_events_root() / f"{transaction_id}.json"
    write_json(target, payload)
    return str(target)


def pocketbase_binary_path() -> str:
    managed = pocketbase_managed_bin_path()
    if managed.exists():
        return str(managed)
    override = str(os.environ.get("BEACON_POCKETBASE_BIN", "") or "").strip()
    if override:
        return override
    detected = shutil.which("pocketbase")
    return detected or ""


def pocketbase_binary_available() -> bool:
    return bool(pocketbase_binary_path())


def _default_pocketbase_urls() -> dict[str, str]:
    host = str(os.environ.get("BEACON_POCKETBASE_HOST", "") or "127.0.0.1:8090").strip() or "127.0.0.1:8090"
    return {
        "listen": host,
        "admin_ui": f"http://{host}/_/",
        "api": f"http://{host}/api/",
    }


def _projection_collections() -> list[str]:
    return [
        "projects",
        "git_scopes",
        "feature_packages",
        "feature_lifecycle",
        "stage_material_status",
        "runs",
        "run_workers",
        "run_targets",
        "run_events",
        "artifact_refs",
        "git_workspace_bindings",
        "host_sessions",
        "health_snapshots",
        "debug_issues",
        "projection_writes",
    ]


def _control_plane_schema() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "projection_only": True,
        "collections": _projection_collections(),
        "truth_boundary": "docs/beacon + .beacon",
        "notes": [
            "PocketBase consumes projection artifacts only.",
            "PocketBase is not Beacon requirement or release truth.",
            "If SQLite or PocketBase is unavailable, rebuild from local truth remains valid.",
        ],
    }


def ensure_pocketbase_control_plane() -> dict[str, Any]:
    root = pocketbase_projection_root()
    collections_root = _ensure_dir(root / "collections")
    public_root = _ensure_dir(root / "pb_public")
    _ensure_dir(root / "bin")
    _ensure_dir(root / "pb_data")
    backups_root = _ensure_dir(root / "backups")
    exports_root = _ensure_dir(root / "exports")
    scripts_root = _ensure_dir(root / "scripts")
    schema_path = root / "collection-schema.json"
    write_json(schema_path, _control_plane_schema())
    for collection in _projection_collections():
        _ensure_dir(collections_root / collection)

    urls = _default_pocketbase_urls()
    binary_path = pocketbase_binary_path()
    serve_script = scripts_root / "serve-pocketbase.sh"
    backup_script = scripts_root / "backup-runtime-ledger.sh"
    _write_executable(
        serve_script,
        "\n".join(
            [
                "#!/bin/sh",
                "set -eu",
                'ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"',
                'BIN="${BEACON_POCKETBASE_BIN:-$ROOT/bin/pocketbase}"',
                '[ -x "$BIN" ] || BIN="pocketbase"',
                f'LISTEN="${{BEACON_POCKETBASE_HOST:-{urls["listen"]}}}"',
                'exec "$BIN" serve --dir "$ROOT/pb_data" --publicDir "$ROOT/pb_public" --http "$LISTEN"',
                "",
            ]
        ),
    )
    _write_executable(
        backup_script,
        "\n".join(
            [
                "#!/bin/sh",
                "set -eu",
                'ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"',
                'STAMP="$(date -u +%Y%m%dT%H%M%SZ)"',
                'TARGET="$ROOT/backups/pocketbase-$STAMP"',
                'mkdir -p "$TARGET"',
                '[ -d "$ROOT/pb_data" ] && cp -R "$ROOT/pb_data" "$TARGET/pb_data"',
                '[ -f "$ROOT/control-plane.json" ] && cp "$ROOT/control-plane.json" "$TARGET/control-plane.json"',
                '[ -f "$ROOT/collection-schema.json" ] && cp "$ROOT/collection-schema.json" "$TARGET/collection-schema.json"',
                '[ -d "$ROOT/collections" ] && cp -R "$ROOT/collections" "$TARGET/collections"',
                'printf "%s\n" "$TARGET"',
                "",
            ]
        ),
    )

    manifest = {
        "schema_version": "1.0",
        "projection_only": True,
        "binary_available": bool(binary_path),
        "binary_path": binary_path,
        "binary_status": "ready" if binary_path else "missing_binary",
        "listen": urls["listen"],
        "admin_ui": urls["admin_ui"],
        "api": urls["api"],
        "collections_root": str(collections_root),
        "public_root": str(public_root),
        "schema_path": str(schema_path),
        "backups_root": str(backups_root),
        "exports_root": str(exports_root),
        "serve_script": str(serve_script),
        "backup_script": str(backup_script),
        "updated_at": now_iso(),
    }
    write_json(pocketbase_control_plane_manifest_path(), manifest)
    return manifest


def inspect_pocketbase_control_plane() -> dict[str, Any]:
    manifest = read_json(pocketbase_control_plane_manifest_path(), {})
    manifest = manifest if isinstance(manifest, dict) else {}
    root = pocketbase_projection_root()
    collections_root = root / "collections"
    missing: list[str] = []
    if not collections_root.exists():
        missing.append("collections_root")
    public_root = pocketbase_public_root()
    if not public_root.exists():
        missing.append("public_root")
    if not (root / "collection-schema.json").exists():
        missing.append("collection_schema")
    if not (root / "scripts" / "serve-pocketbase.sh").exists():
        missing.append("serve_script")
    if not (root / "scripts" / "backup-runtime-ledger.sh").exists():
        missing.append("backup_script")
    binary_path = pocketbase_binary_path()
    binary_available = bool(binary_path)
    return {
        **manifest,
        "root": str(root),
        "public_root": str(public_root),
        "exists": root.exists(),
        "status": "ready" if root.exists() and not missing else "degraded" if root.exists() else "missing",
        "missing": missing,
        "binary_available": binary_available,
        "binary_path": binary_path,
        "binary_status": "ready" if binary_available else "missing_binary",
    }


def projection_envelope_path(envelope: dict[str, Any]) -> Path:
    project_key = str(envelope.get("project_key") or "unknown")
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    projection_seq = str(projection.get("projection_seq") or "unknown")
    return runtime_ledger_projection_root() / project_key / f"{projection_seq}.json"


def write_projection_envelope(envelope: dict[str, Any]) -> str:
    path = projection_envelope_path(envelope)
    write_json(path, envelope)
    return str(path)


def _connect() -> sqlite3.Connection:
    if _sqlite_disabled():
        raise RuntimeError("sqlite_disabled")
    db_path = runtime_ledger_db_path()
    _ensure_parent(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    ensure_runtime_projection_schema(conn)
    return conn


def _ensure_columns(conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
    existing = {
        str(row[1])
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    for column, ddl in columns.items():
        if column in existing:
            continue
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


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
            health_status TEXT NOT NULL DEFAULT '',
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

        CREATE TABLE IF NOT EXISTS feature_packages (
            project_key TEXT NOT NULL,
            package_key TEXT NOT NULL,
            feature TEXT NOT NULL,
            feature_slug TEXT NOT NULL,
            docs_version TEXT NOT NULL,
            prd_path TEXT NOT NULL,
            user_story_path TEXT NOT NULL,
            test_case_path TEXT NOT NULL,
            materials_json TEXT NOT NULL,
            PRIMARY KEY (project_key, package_key)
        );

        CREATE TABLE IF NOT EXISTS feature_lifecycle (
            project_key TEXT NOT NULL,
            package_key TEXT NOT NULL,
            feature TEXT NOT NULL,
            current_stage TEXT NOT NULL,
            progress_label TEXT NOT NULL,
            blocked INTEGER NOT NULL DEFAULT 0,
            blocked_reason TEXT NOT NULL,
            next_action TEXT NOT NULL,
            runtime_mode TEXT NOT NULL,
            debug_state TEXT NOT NULL,
            truth_refs_json TEXT NOT NULL,
            PRIMARY KEY (project_key, package_key)
        );

        CREATE TABLE IF NOT EXISTS stage_material_status (
            project_key TEXT NOT NULL,
            package_key TEXT NOT NULL,
            material_type TEXT NOT NULL,
            status TEXT NOT NULL,
            truth_path TEXT NOT NULL,
            PRIMARY KEY (project_key, package_key, material_type)
        );

        CREATE TABLE IF NOT EXISTS runs (
            project_key TEXT NOT NULL,
            run_id TEXT NOT NULL,
            feature TEXT NOT NULL,
            docs_version TEXT NOT NULL,
            mode TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT NOT NULL,
            source TEXT NOT NULL,
            truth_refs_json TEXT NOT NULL,
            PRIMARY KEY (project_key, run_id)
        );

        CREATE TABLE IF NOT EXISTS run_workers (
            project_key TEXT NOT NULL,
            run_id TEXT NOT NULL,
            worker_id TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            pane_id TEXT NOT NULL,
            tmux_session TEXT NOT NULL,
            artifact_json_ref TEXT NOT NULL,
            artifact_md_ref TEXT NOT NULL,
            PRIMARY KEY (project_key, run_id, worker_id, role)
        );

        CREATE TABLE IF NOT EXISTS run_targets (
            project_key TEXT NOT NULL,
            run_id TEXT NOT NULL,
            scope_key TEXT NOT NULL,
            target_branch TEXT NOT NULL,
            current_branch TEXT NOT NULL,
            service_name TEXT NOT NULL,
            scope_role TEXT NOT NULL,
            PRIMARY KEY (project_key, run_id, scope_key)
        );

        CREATE TABLE IF NOT EXISTS run_events (
            project_key TEXT NOT NULL,
            run_id TEXT NOT NULL,
            event_seq INTEGER NOT NULL,
            stage TEXT NOT NULL,
            event TEXT NOT NULL,
            status TEXT NOT NULL,
            reason_code TEXT NOT NULL,
            ts TEXT NOT NULL,
            details_json TEXT NOT NULL,
            PRIMARY KEY (project_key, run_id, event_seq)
        );

        CREATE TABLE IF NOT EXISTS artifact_refs (
            project_key TEXT NOT NULL,
            run_id TEXT NOT NULL,
            artifact_type TEXT NOT NULL,
            path TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            exists_flag INTEGER NOT NULL DEFAULT 0,
            artifact_scope TEXT NOT NULL,
            PRIMARY KEY (project_key, run_id, path)
        );

        CREATE TABLE IF NOT EXISTS git_workspace_bindings (
            project_key TEXT NOT NULL,
            package_key TEXT NOT NULL,
            repo_root TEXT NOT NULL,
            branch TEXT NOT NULL,
            commit_sha TEXT NOT NULL,
            dirty INTEGER NOT NULL DEFAULT 0,
            worktree_path TEXT NOT NULL,
            expected_branch_rule TEXT NOT NULL,
            spec_status TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (project_key, package_key, repo_root)
        );

        CREATE TABLE IF NOT EXISTS host_sessions (
            project_key TEXT NOT NULL,
            feature TEXT NOT NULL,
            run_id TEXT NOT NULL,
            host_runtime TEXT NOT NULL,
            session_id TEXT NOT NULL,
            thread_id TEXT NOT NULL,
            turn_id TEXT NOT NULL,
            transcript_path TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT NOT NULL,
            PRIMARY KEY (project_key, host_runtime, session_id, run_id)
        );

        CREATE TABLE IF NOT EXISTS health_snapshots (
            project_key TEXT NOT NULL,
            snapshot_at TEXT NOT NULL,
            overall_status TEXT NOT NULL,
            stale_runs INTEGER NOT NULL DEFAULT 0,
            blocked_runs INTEGER NOT NULL DEFAULT 0,
            failing_scopes INTEGER NOT NULL DEFAULT 0,
            sync_status TEXT NOT NULL,
            notes_json TEXT NOT NULL,
            PRIMARY KEY (project_key, snapshot_at)
        );

        CREATE TABLE IF NOT EXISTS debug_issues (
            project_key TEXT NOT NULL,
            issue_id TEXT NOT NULL,
            reason_code TEXT NOT NULL,
            issue_status TEXT NOT NULL,
            materialization_state TEXT NOT NULL,
            latest_event_at TEXT NOT NULL,
            sample TEXT NOT NULL,
            suggested_capability TEXT NOT NULL,
            source_run_id TEXT NOT NULL,
            truth_refs_json TEXT NOT NULL,
            PRIMARY KEY (project_key, issue_id)
        );

        CREATE TABLE IF NOT EXISTS friction_items (
            project_key TEXT NOT NULL,
            item_id TEXT NOT NULL,
            docs_version TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            item_class TEXT NOT NULL,
            severity TEXT NOT NULL,
            domain TEXT NOT NULL,
            queue_status TEXT NOT NULL,
            requirement_route_status TEXT NOT NULL DEFAULT 'queue_only',
            feature TEXT NOT NULL DEFAULT '',
            feature_slug TEXT NOT NULL DEFAULT '',
            host_runtime TEXT NOT NULL DEFAULT '',
            source_run_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            project_root TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            occurrence_count INTEGER NOT NULL DEFAULT 1,
            accepted_at TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (project_key, item_id)
        );

        CREATE TABLE IF NOT EXISTS friction_refs (
            project_key TEXT NOT NULL,
            item_id TEXT NOT NULL,
            ref_path TEXT NOT NULL,
            ref_kind TEXT NOT NULL,
            ref_scope TEXT NOT NULL,
            sha256 TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (project_key, item_id, ref_path)
        );

        CREATE TABLE IF NOT EXISTS friction_events (
            event_id TEXT PRIMARY KEY,
            project_key TEXT NOT NULL,
            item_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_at TEXT NOT NULL,
            from_status TEXT NOT NULL DEFAULT '',
            to_status TEXT NOT NULL DEFAULT '',
            payload_json TEXT NOT NULL DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS projection_writes (
            projection_seq TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL DEFAULT '',
            project_key TEXT NOT NULL,
            source_hash TEXT NOT NULL,
            write_status TEXT NOT NULL,
            preflight_status TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 0,
            uncertainty_reason TEXT NOT NULL DEFAULT '',
            sqlite_status TEXT NOT NULL DEFAULT '',
            pocketbase_status TEXT NOT NULL DEFAULT '',
            sink_checksums_json TEXT NOT NULL DEFAULT '{}',
            occurred_at TEXT NOT NULL DEFAULT '',
            wrote_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );
        """
    )
    _ensure_columns(conn, "projects", {"health_status": "TEXT NOT NULL DEFAULT ''"})
    _ensure_columns(
        conn,
        "projection_writes",
        {
            "transaction_id": "TEXT NOT NULL DEFAULT ''",
            "confidence": "REAL NOT NULL DEFAULT 0",
            "uncertainty_reason": "TEXT NOT NULL DEFAULT ''",
            "sqlite_status": "TEXT NOT NULL DEFAULT ''",
            "pocketbase_status": "TEXT NOT NULL DEFAULT ''",
            "sink_checksums_json": "TEXT NOT NULL DEFAULT '{}'",
            "occurred_at": "TEXT NOT NULL DEFAULT ''",
        },
    )
    conn.commit()


def ensure_project_metadata_schema(conn: sqlite3.Connection) -> None:
    """Ensure the project_metadata_* tables exist on both read and write paths.

    These tables are written by ``project_metadata`` but read via the shared
    ``_connect()``; without this the read path raises on a fresh runtime ledger
    (`no such table: project_metadata_current`, issue #22).
    """
    existing = {
        str(row[0])
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    if {"project_metadata_current", "project_metadata_events"} <= existing:
        # Cheap common path: schema already present.
        return
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS project_metadata_current (
            project_root TEXT PRIMARY KEY,
            topology_kind TEXT NOT NULL,
            default_execution_service TEXT NOT NULL,
            transaction_id TEXT NOT NULL,
            committed_at TEXT NOT NULL,
            source_hash TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS project_metadata_events (
            transaction_id TEXT PRIMARY KEY,
            project_root TEXT NOT NULL,
            event_type TEXT NOT NULL,
            committed_at TEXT NOT NULL,
            source_hash TEXT NOT NULL DEFAULT '',
            payload_json TEXT NOT NULL
        );
        """
    )
    _ensure_columns(conn, "project_metadata_events", {"source_hash": "TEXT NOT NULL DEFAULT ''"})
    conn.commit()


def runtime_ledger_probe() -> dict[str, Any]:
    """Non-raising health probe for the runtime ledger (issues #22 / #26).

    Distinguishes an unwritable ledger root from a missing table so callers can
    emit a specific reason code instead of an unhandled traceback.
    """
    if _sqlite_disabled():
        return {
            "ledger_reason_code": "runtime_ledger_disabled",
            "ledger_hint": "BEACON_RUNTIME_LEDGER_DISABLE_SQLITE is set",
        }
    root = runtime_ledger_root()
    try:
        root.mkdir(parents=True, exist_ok=True)
        probe = root / ".beacon-ledger-write-probe"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
    except OSError:
        return {
            "ledger_reason_code": "runtime_ledger_unwritable",
            "ledger_hint": f"set BEACON_RUNTIME_LEDGER_ROOT to a writable dir (current: {root})",
        }
    try:
        with _connect() as conn:
            ensure_project_metadata_schema(conn)
            conn.execute("SELECT 1 FROM project_metadata_current LIMIT 1").fetchone()
    except (sqlite3.Error, RuntimeError) as exc:
        return {
            "ledger_reason_code": "runtime_ledger_schema_missing",
            "ledger_hint": f"runtime ledger schema incomplete at {runtime_ledger_db_path()}: {exc}",
        }
    return {"ledger_reason_code": "", "ledger_hint": ""}


def preflight_projection_write(envelope: dict[str, Any]) -> dict[str, Any]:
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    preflight = projection.get("preflight") if isinstance(projection.get("preflight"), dict) else {}
    conflicts = preflight.get("conflicts") if isinstance(preflight.get("conflicts"), list) else []
    warnings = preflight.get("warnings") if isinstance(preflight.get("warnings"), list) else []
    raw_status = str(
        projection.get("preflight_status")
        or preflight.get("status")
        or ("conflicted" if conflicts else "partial" if warnings else "pass")
    ).strip()
    normalized_status = {
        "ok": "pass",
        "pass": "pass",
        "partial": "partial",
        "conflicted": "conflicted",
        "blocked": "blocked",
    }.get(raw_status, "conflicted" if conflicts else "partial" if warnings else "pass")
    return {
        "status": normalized_status,
        "conflicts": [str(item) for item in conflicts if str(item).strip()],
        "warnings": [str(item) for item in warnings if str(item).strip()],
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
        str(board.get("health_status") or ""),
        str(projection.get("source_hash") or ""),
        str(projection.get("projection_seq") or ""),
        now_iso(),
        json.dumps(envelope, ensure_ascii=False, sort_keys=True),
    )


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _stable_json_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _insert_rows(conn: sqlite3.Connection, table: str, columns: list[str], rows: list[tuple[Any, ...]]) -> None:
    if not rows:
        return
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    conn.executemany(sql, rows)


def _delete_project_rows(conn: sqlite3.Connection, project_key: str) -> None:
    for table in (
        "git_scopes",
        "feature_packages",
        "feature_lifecycle",
        "stage_material_status",
        "runs",
        "run_workers",
        "run_targets",
        "run_events",
        "artifact_refs",
        "git_workspace_bindings",
        "host_sessions",
        "health_snapshots",
        "debug_issues",
    ):
        conn.execute(f"DELETE FROM {table} WHERE project_key = ?", (project_key,))


def _git_scope_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for scope in envelope.get("git_scopes", []) if isinstance(envelope.get("git_scopes"), list) else []:
        if not isinstance(scope, dict):
            continue
        rows.append(
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
            )
        )
    return rows


def _feature_package_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for package in envelope.get("feature_packages", []) if isinstance(envelope.get("feature_packages"), list) else []:
        if not isinstance(package, dict):
            continue
        rows.append(
            (
                project_key,
                str(package.get("package_key") or ""),
                str(package.get("feature") or ""),
                str(package.get("feature_slug") or ""),
                str(package.get("docs_version") or ""),
                str(package.get("prd_path") or ""),
                str(package.get("user_story_path") or ""),
                str(package.get("test_case_path") or ""),
                _json_text(package.get("materials") or {}),
            )
        )
    return rows


def _feature_lifecycle_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for lifecycle in envelope.get("feature_lifecycle", []) if isinstance(envelope.get("feature_lifecycle"), list) else []:
        if not isinstance(lifecycle, dict):
            continue
        rows.append(
            (
                project_key,
                str(lifecycle.get("package_key") or ""),
                str(lifecycle.get("feature") or ""),
                str(lifecycle.get("current_stage") or ""),
                str(lifecycle.get("progress_label") or ""),
                1 if bool(lifecycle.get("blocked")) else 0,
                str(lifecycle.get("blocked_reason") or ""),
                str(lifecycle.get("next_action") or ""),
                str(lifecycle.get("runtime_mode") or ""),
                str(lifecycle.get("debug_state") or ""),
                _json_text(lifecycle.get("truth_refs") or {}),
            )
        )
    return rows


def _stage_material_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("stage_material_status", []) if isinstance(envelope.get("stage_material_status"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("package_key") or ""),
                str(item.get("material_type") or ""),
                str(item.get("status") or ""),
                str(item.get("truth_path") or ""),
            )
        )
    return rows


def _runs_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("runs", []) if isinstance(envelope.get("runs"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("run_id") or ""),
                str(item.get("feature") or ""),
                str(item.get("docs_version") or ""),
                str(item.get("mode") or ""),
                str(item.get("status") or ""),
                str(item.get("started_at") or ""),
                str(item.get("ended_at") or ""),
                str(item.get("source") or ""),
                _json_text(item.get("truth_refs") or []),
            )
        )
    return rows


def _run_workers_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("run_workers", []) if isinstance(envelope.get("run_workers"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("run_id") or ""),
                str(item.get("worker_id") or ""),
                str(item.get("role") or ""),
                str(item.get("status") or ""),
                str(item.get("pane_id") or ""),
                str(item.get("tmux_session") or ""),
                str(item.get("artifact_json_ref") or ""),
                str(item.get("artifact_md_ref") or ""),
            )
        )
    return rows


def _run_targets_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("run_targets", []) if isinstance(envelope.get("run_targets"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("run_id") or ""),
                str(item.get("scope_key") or ""),
                str(item.get("target_branch") or ""),
                str(item.get("current_branch") or ""),
                str(item.get("service_name") or ""),
                str(item.get("scope_role") or ""),
            )
        )
    return rows


def _run_events_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("run_events", []) if isinstance(envelope.get("run_events"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("run_id") or ""),
                int(item.get("event_seq", 0) or 0),
                str(item.get("stage") or ""),
                str(item.get("event") or ""),
                str(item.get("status") or ""),
                str(item.get("reason_code") or ""),
                str(item.get("ts") or ""),
                _json_text(item.get("details_json") or {}),
            )
        )
    return rows


def _artifact_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("artifact_refs", []) if isinstance(envelope.get("artifact_refs"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("run_id") or ""),
                str(item.get("artifact_type") or ""),
                str(item.get("path") or ""),
                str(item.get("sha256") or ""),
                1 if bool(item.get("exists")) else 0,
                str(item.get("artifact_scope") or ""),
            )
        )
    return rows


def _workspace_binding_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("git_workspace_bindings", []) if isinstance(envelope.get("git_workspace_bindings"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("package_key") or ""),
                str(item.get("repo_root") or ""),
                str(item.get("branch") or ""),
                str(item.get("commit_sha") or ""),
                1 if bool(item.get("dirty")) else 0,
                str(item.get("worktree_path") or ""),
                str(item.get("expected_branch_rule") or ""),
                str(item.get("spec_status") or ""),
                str(item.get("updated_at") or ""),
            )
        )
    return rows


def _host_session_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("host_sessions", []) if isinstance(envelope.get("host_sessions"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("feature") or ""),
                str(item.get("run_id") or ""),
                str(item.get("host_runtime") or ""),
                str(item.get("session_id") or ""),
                str(item.get("thread_id") or ""),
                str(item.get("turn_id") or ""),
                str(item.get("transcript_path") or ""),
                str(item.get("status") or ""),
                str(item.get("started_at") or ""),
                str(item.get("ended_at") or ""),
            )
        )
    return rows


def _health_snapshot_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for index, item in enumerate(envelope.get("health_snapshots", []) if isinstance(envelope.get("health_snapshots"), list) else [], start=1):
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("snapshot_at") or f"{now_iso()}#{index}"),
                str(item.get("overall_status") or ""),
                int(item.get("stale_runs", 0) or 0),
                int(item.get("blocked_runs", 0) or 0),
                int(item.get("failing_scopes", 0) or 0),
                str(item.get("sync_status") or ""),
                _json_text(item.get("notes") or []),
            )
        )
    return rows


def _debug_issue_rows(project_key: str, envelope: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for item in envelope.get("debug_issues", []) if isinstance(envelope.get("debug_issues"), list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                project_key,
                str(item.get("issue_id") or ""),
                str(item.get("reason_code") or ""),
                str(item.get("issue_status") or ""),
                str(item.get("materialization_state") or ""),
                str(item.get("latest_event_at") or ""),
                str(item.get("sample") or ""),
                str(item.get("suggested_capability") or ""),
                str(item.get("source_run_id") or ""),
                _json_text(item.get("truth_refs") or []),
            )
        )
    return rows


def _write_projection_history(
    conn: sqlite3.Connection,
    *,
    envelope: dict[str, Any],
    preflight: dict[str, Any],
    write_status: str,
    sqlite_status: str,
    pocketbase_status: str,
    transaction_id: str,
    sink_checksums: dict[str, Any],
) -> None:
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    conn.execute(
        """
        INSERT INTO projection_writes (
            projection_seq, transaction_id, project_key, source_hash, write_status, preflight_status,
            confidence, uncertainty_reason, sqlite_status, pocketbase_status, sink_checksums_json, occurred_at, wrote_at, payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(projection_seq) DO UPDATE SET
            transaction_id=excluded.transaction_id,
            project_key=excluded.project_key,
            source_hash=excluded.source_hash,
            write_status=excluded.write_status,
            preflight_status=excluded.preflight_status,
            confidence=excluded.confidence,
            uncertainty_reason=excluded.uncertainty_reason,
            sqlite_status=excluded.sqlite_status,
            pocketbase_status=excluded.pocketbase_status,
            sink_checksums_json=excluded.sink_checksums_json,
            occurred_at=excluded.occurred_at,
            wrote_at=excluded.wrote_at,
            payload_json=excluded.payload_json
        """,
        (
            str(projection.get("projection_seq") or ""),
            str(transaction_id or ""),
            str(envelope.get("project_key") or ""),
            str(projection.get("source_hash") or ""),
            write_status,
            str(preflight.get("status") or "pass"),
            float(projection.get("confidence", 0) or 0),
            str(projection.get("uncertainty_reason") or ""),
            sqlite_status,
            pocketbase_status,
            json.dumps(sink_checksums if isinstance(sink_checksums, dict) else {}, ensure_ascii=False, sort_keys=True),
            now_iso(),
            now_iso(),
            json.dumps(envelope, ensure_ascii=False, sort_keys=True),
        ),
    )


def write_pocketbase_projection_pack(envelope: dict[str, Any]) -> dict[str, str]:
    control_plane = ensure_pocketbase_control_plane()
    root = pocketbase_projection_root()
    collections_root = root / "collections"
    project_key = str(envelope.get("project_key") or "")
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    projection_seq = str(projection.get("projection_seq") or "projection")

    sections: dict[str, Any] = {
        "projects": envelope,
        "git_scopes": {"project_key": project_key, "rows": envelope.get("git_scopes", [])},
        "feature_packages": {"project_key": project_key, "rows": envelope.get("feature_packages", [])},
        "feature_lifecycle": {"project_key": project_key, "rows": envelope.get("feature_lifecycle", [])},
        "stage_material_status": {"project_key": project_key, "rows": envelope.get("stage_material_status", [])},
        "runs": {"project_key": project_key, "rows": envelope.get("runs", [])},
        "run_workers": {"project_key": project_key, "rows": envelope.get("run_workers", [])},
        "run_targets": {"project_key": project_key, "rows": envelope.get("run_targets", [])},
        "run_events": {"project_key": project_key, "rows": envelope.get("run_events", [])},
        "artifact_refs": {"project_key": project_key, "rows": envelope.get("artifact_refs", [])},
        "git_workspace_bindings": {"project_key": project_key, "rows": envelope.get("git_workspace_bindings", [])},
        "host_sessions": {"project_key": project_key, "rows": envelope.get("host_sessions", [])},
        "health_snapshots": {"project_key": project_key, "rows": envelope.get("health_snapshots", [])},
        "debug_issues": {"project_key": project_key, "rows": envelope.get("debug_issues", [])},
        "projection_writes": {"project_key": project_key, "projection": projection},
    }

    written: dict[str, str] = {
        "control_plane": str(pocketbase_control_plane_manifest_path()),
    }
    for collection, payload in sections.items():
        collection_dir = _ensure_dir(collections_root / collection)
        filename = f"{projection_seq}.json" if collection == "projection_writes" else f"{project_key}.json"
        path = collection_dir / filename
        write_json(path, payload)
        written[collection if collection != "projects" else "project"] = str(path)
    write_json(
        root / "portfolio-summary.json",
        {
            "schema_version": "1.0",
            "generated_at": now_iso(),
            "collections": _projection_collections(),
            "control_plane": control_plane,
        },
    )
    board_paths = write_public_board_pack(
        pocketbase_root=root,
        control_plane=control_plane,
        generated_at=now_iso(),
    )
    for key, value in board_paths.items():
        written[f"board_{key}"] = value
    return written


def sync_projection(envelope: dict[str, Any]) -> dict[str, Any]:
    preflight = preflight_projection_write(envelope)
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    project_key = str(envelope.get("project_key") or "")
    source_hash = str(projection.get("source_hash") or "")
    projection_seq = str(projection.get("projection_seq") or "")
    transaction_id = str(projection.get("transaction_id") or "").strip() or f"tx-{project_key}-{projection_seq or 'projection'}"
    sink_checksums: dict[str, Any] = {
        "machine": "missing",
        "human": "missing",
        "sqlite": "missing",
        "pocketbase": "missing",
    }
    failed_sinks: list[str] = []
    envelope_path = write_projection_envelope(envelope)
    sink_checksums["machine"] = _stable_hash_file(Path(envelope_path)) or "missing"
    control_plane = ensure_pocketbase_control_plane()
    occurred_at = now_iso()

    if preflight["status"] in {"conflicted", "blocked"}:
        transaction_payload = {
            "schema_version": "1.0",
            "transaction_id": transaction_id,
            "project_key": project_key,
            "source_hash": source_hash,
            "projection_seq": projection_seq,
            "status": "blocked_transaction",
            "preflight_status": str(preflight.get("status") or ""),
            "failed_sinks": ["preflight"],
            "sink_checksums": sink_checksums,
            "occurred_at": occurred_at,
            "committed_at": "",
            "error": "preflight blocked projection commit",
        }
        transaction_path = _record_transaction_event(transaction_payload)
        return {
            "status": "blocked_transaction",
            "sqlite_status": "skipped",
            "pocketbase_status": "skipped",
            "preflight": preflight,
            "db_path": str(runtime_ledger_db_path()),
            "pocketbase_root": str(pocketbase_projection_root()),
            "envelope_path": envelope_path,
            "control_plane": control_plane,
            "transaction_id": transaction_id,
            "projection_seq": projection_seq,
            "source_hash": source_hash,
            "sink_checksums": sink_checksums,
            "failed_sinks": ["preflight"],
            "transaction_path": transaction_path,
        }

    mirror_paths: dict[str, str] = {}
    pocketbase_status = "skipped"
    pocketbase_error = ""
    try:
        mirror_paths = write_pocketbase_projection_pack(envelope)
        pocketbase_status = "ready" if bool(control_plane.get("binary_available")) else "projection_only"
        sink_checksums["pocketbase"] = _stable_hash_payload(mirror_paths)
        human_ref = (
            mirror_paths.get("board_portfolio")
            or mirror_paths.get("board_index")
            or mirror_paths.get("project")
            or ""
        )
        sink_checksums["human"] = _stable_hash_file(Path(str(human_ref))) if human_ref else "missing"
        if not sink_checksums["human"]:
            sink_checksums["human"] = "missing"
    except Exception as exc:  # noqa: BLE001
        pocketbase_status = "failed"
        pocketbase_error = str(exc)
        failed_sinks.append("pocketbase")

    sqlite_status = "skipped"
    sqlite_error = ""
    committed_at = ""
    history_written = False
    write_status = "failed_transaction" if failed_sinks else "applied"
    try:
        with _connect() as conn:
            sqlite_status = "applied"
            conn.execute(
                """
                INSERT INTO projects (
                    project_key, display_name, project_root, docs_version, project_kind, current_stage,
                    progress_label, blocker, next_action, runtime_mode, debug_state, runtime_corroboration,
                    health_status, source_hash, projection_seq, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    health_status=excluded.health_status,
                    source_hash=excluded.source_hash,
                    projection_seq=excluded.projection_seq,
                    updated_at=excluded.updated_at,
                    payload_json=excluded.payload_json
                """,
                _project_row(envelope),
            )
            project_key = str(envelope.get("project_key") or "")
            _delete_project_rows(conn, project_key)
            _insert_rows(
                conn,
                "git_scopes",
                ["project_key", "scope_key", "repo_root", "repo_name", "branch", "commit_sha", "dirty", "role", "worktree_path", "source_priority"],
                _git_scope_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "feature_packages",
                ["project_key", "package_key", "feature", "feature_slug", "docs_version", "prd_path", "user_story_path", "test_case_path", "materials_json"],
                _feature_package_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "feature_lifecycle",
                ["project_key", "package_key", "feature", "current_stage", "progress_label", "blocked", "blocked_reason", "next_action", "runtime_mode", "debug_state", "truth_refs_json"],
                _feature_lifecycle_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "stage_material_status",
                ["project_key", "package_key", "material_type", "status", "truth_path"],
                _stage_material_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "runs",
                ["project_key", "run_id", "feature", "docs_version", "mode", "status", "started_at", "ended_at", "source", "truth_refs_json"],
                _runs_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "run_workers",
                ["project_key", "run_id", "worker_id", "role", "status", "pane_id", "tmux_session", "artifact_json_ref", "artifact_md_ref"],
                _run_workers_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "run_targets",
                ["project_key", "run_id", "scope_key", "target_branch", "current_branch", "service_name", "scope_role"],
                _run_targets_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "run_events",
                ["project_key", "run_id", "event_seq", "stage", "event", "status", "reason_code", "ts", "details_json"],
                _run_events_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "artifact_refs",
                ["project_key", "run_id", "artifact_type", "path", "sha256", "exists_flag", "artifact_scope"],
                _artifact_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "git_workspace_bindings",
                ["project_key", "package_key", "repo_root", "branch", "commit_sha", "dirty", "worktree_path", "expected_branch_rule", "spec_status", "updated_at"],
                _workspace_binding_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "host_sessions",
                ["project_key", "feature", "run_id", "host_runtime", "session_id", "thread_id", "turn_id", "transcript_path", "status", "started_at", "ended_at"],
                _host_session_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "health_snapshots",
                ["project_key", "snapshot_at", "overall_status", "stale_runs", "blocked_runs", "failing_scopes", "sync_status", "notes_json"],
                _health_snapshot_rows(project_key, envelope),
            )
            _insert_rows(
                conn,
                "debug_issues",
                ["project_key", "issue_id", "reason_code", "issue_status", "materialization_state", "latest_event_at", "sample", "suggested_capability", "source_run_id", "truth_refs_json"],
                _debug_issue_rows(project_key, envelope),
            )
            sink_checksums["sqlite"] = _stable_hash_payload(
                {
                    "project_key": project_key,
                    "projection_seq": projection_seq,
                    "source_hash": source_hash,
                    "write_status": write_status,
                    "sqlite_status": sqlite_status,
                    "pocketbase_status": pocketbase_status,
                }
            )
            _write_projection_history(
                conn,
                envelope=envelope,
                preflight=preflight,
                write_status=write_status,
                sqlite_status=sqlite_status,
                pocketbase_status=pocketbase_status,
                transaction_id=transaction_id,
                sink_checksums=sink_checksums,
            )
            conn.commit()
            history_written = True
            committed_at = now_iso()
    except Exception as exc:  # noqa: BLE001
        sqlite_error = str(exc)
        sqlite_status = "unavailable" if _sqlite_disabled() or sqlite_error == "sqlite_disabled" else "failed"
        failed_sinks.append("sqlite")
        write_status = "failed_transaction"

    if not history_written and sqlite_status == "applied":
        sqlite_status = "failed"
        failed_sinks.append("sqlite")
        write_status = "failed_transaction"

    sink_checksums["sqlite"] = sink_checksums.get("sqlite") or "missing"
    if sink_checksums["sqlite"] == "":
        sink_checksums["sqlite"] = "missing"
    if sink_checksums["pocketbase"] == "":
        sink_checksums["pocketbase"] = "missing"

    projection["transaction_id"] = transaction_id
    projection["committed_at"] = committed_at
    projection["write_status"] = write_status
    projection["failed_sinks"] = sorted({str(item) for item in failed_sinks if str(item).strip()})
    projection["sink_checksums"] = sink_checksums
    envelope["projection"] = projection
    write_json(Path(envelope_path), envelope)
    sink_checksums["machine"] = _stable_hash_file(Path(envelope_path)) or sink_checksums.get("machine") or "missing"

    transaction_payload = {
        "schema_version": "1.0",
        "transaction_id": transaction_id,
        "project_key": project_key,
        "source_hash": source_hash,
        "projection_seq": projection_seq,
        "status": write_status,
        "preflight_status": str(preflight.get("status") or ""),
        "failed_sinks": projection.get("failed_sinks") or [],
        "sink_checksums": sink_checksums,
        "occurred_at": occurred_at,
        "committed_at": committed_at,
        "sqlite_status": sqlite_status,
        "pocketbase_status": pocketbase_status,
        "errors": {
            "sqlite": sqlite_error,
            "pocketbase": pocketbase_error,
        },
        "envelope_path": envelope_path,
    }
    transaction_path = _record_transaction_event(transaction_payload)

    if history_written and write_status == "failed_transaction":
        try:
            with _connect() as conn:
                _write_projection_history(
                    conn,
                    envelope=envelope,
                    preflight=preflight,
                    write_status=write_status,
                    sqlite_status=sqlite_status,
                    pocketbase_status=pocketbase_status,
                    transaction_id=transaction_id,
                    sink_checksums=sink_checksums,
                )
                conn.commit()
        except Exception:  # noqa: BLE001
            pass

    status = "applied" if write_status == "applied" else "failed_transaction"

    return {
        "status": status,
        "sqlite_status": sqlite_status,
        "pocketbase_status": pocketbase_status,
        "preflight": preflight,
        "db_path": str(runtime_ledger_db_path()),
        "pocketbase_root": str(pocketbase_projection_root()),
        "mirror_paths": mirror_paths,
        "envelope_path": envelope_path,
        "control_plane": control_plane,
        "projection_seq": projection_seq,
        "transaction_id": transaction_id,
        "source_hash": source_hash,
        "sink_checksums": sink_checksums,
        "failed_sinks": projection.get("failed_sinks") or [],
        "transaction_path": transaction_path,
        "error": sqlite_error or pocketbase_error,
    }


def _list_projects_from_mirror(limit: int) -> list[dict[str, Any]]:
    root = pocketbase_projection_root() / "collections" / "projects"
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json"), reverse=True):
        payload = read_json(path, {})
        if not isinstance(payload, dict):
            continue
        board = payload.get("board") if isinstance(payload.get("board"), dict) else {}
        runtime = payload.get("runtime") if isinstance(payload.get("runtime"), dict) else {}
        projection = payload.get("projection") if isinstance(payload.get("projection"), dict) else {}
        rows.append(
            {
                "project_key": str(payload.get("project_key") or ""),
                "display_name": str(payload.get("display_name") or ""),
                "project_root": str(payload.get("project_root") or ""),
                "docs_version": str(payload.get("docs_version") or ""),
                "project_kind": str(payload.get("project_kind") or ""),
                "current_stage": str(board.get("current_stage") or ""),
                "progress_label": str(board.get("progress_label") or ""),
                "blocker": str(board.get("blocker") or ""),
                "next_action": str(board.get("next_action") or ""),
                "runtime_mode": str(runtime.get("mode") or ""),
                "debug_state": str(board.get("debug_state") or ""),
                "runtime_corroboration": str(board.get("runtime_corroboration") or ""),
                "health_status": str(board.get("health_status") or ""),
                "source_hash": str(projection.get("source_hash") or ""),
                "projection_seq": str(projection.get("projection_seq") or ""),
                "updated_at": str(path.stat().st_mtime_ns),
            }
        )
    rows.sort(key=lambda item: (str(item.get("updated_at") or ""), str(item.get("project_key") or "")), reverse=True)
    return rows[: max(1, limit)]


def list_projects(limit: int = 20) -> list[dict[str, Any]]:
    try:
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT project_key, display_name, project_root, docs_version, project_kind, current_stage,
                       progress_label, blocker, next_action, runtime_mode, debug_state, runtime_corroboration,
                       health_status, source_hash, projection_seq, updated_at
                FROM projects
                ORDER BY updated_at DESC, project_key ASC
                LIMIT ?
                """,
                (max(1, limit),),
            ).fetchall()
        return [dict(row) for row in rows]
    except Exception:  # noqa: BLE001
        return _list_projects_from_mirror(limit)


def load_project_detail(project_key: str) -> dict[str, Any]:
    try:
        with _connect() as conn:
            row = conn.execute("SELECT payload_json FROM projects WHERE project_key = ?", (project_key,)).fetchone()
        if row is not None:
            payload = json.loads(str(row["payload_json"]))
            return payload if isinstance(payload, dict) else {}
    except Exception:  # noqa: BLE001
        pass
    path = pocketbase_projection_root() / "collections" / "projects" / f"{project_key}.json"
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def _runtime_project_key(project_root: Path) -> str:
    root = project_root.expanduser().resolve()
    path_hash = hashlib.sha1(str(root).encode("utf-8")).hexdigest()[:10]  # noqa: S324
    return f"{root.name}--{path_hash}"


def _friction_event_id(project_key: str, item_id: str, event_type: str, event_at: str, payload: dict[str, Any]) -> str:
    digest = _stable_json_hash(
        {
            "project_key": project_key,
            "item_id": item_id,
            "event_type": event_type,
            "event_at": event_at,
            "payload": payload,
        }
    )[:16]
    return f"{project_key}:{item_id}:{event_type}:{digest}"


def write_friction_queue_batch(
    *,
    project_root: Path,
    docs_version: str,
    tool_name: str,
    run_id: str,
    source_type: str,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    project_root = project_root.expanduser().resolve()
    project_key = _runtime_project_key(project_root)
    db_path = runtime_ledger_db_path()
    item_ids: list[str] = []
    try:
        with _connect() as conn:
            for item in items:
                if not isinstance(item, dict):
                    continue
                item_id = str(item.get("item_id") or item.get("candidate_id") or "").strip()
                if not item_id:
                    continue
                now = str(item.get("observed_at") or now_iso())
                row = conn.execute(
                    """
                    SELECT first_seen_at, occurrence_count, queue_status, requirement_route_status
                    FROM friction_items
                    WHERE project_key = ? AND item_id = ?
                    """,
                    (project_key, item_id),
                ).fetchone()
                first_seen_at = str((row["first_seen_at"] if row else "") or now)
                occurrence_count = int((row["occurrence_count"] if row else 0) or 0) + 1
                queue_status = str((row["queue_status"] if row else "") or item.get("queue_status") or "queued")
                requirement_route_status = str(
                    (row["requirement_route_status"] if row else "")
                    or item.get("requirement_route_status")
                    or "queue_only"
                )
                conn.execute(
                    """
                    INSERT INTO friction_items (
                        project_key, item_id, docs_version, tool_name, source_type, item_class, severity, domain,
                        queue_status, requirement_route_status, feature, feature_slug, host_runtime, source_run_id,
                        summary, project_root, first_seen_at, last_seen_at, occurrence_count, accepted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(project_key, item_id) DO UPDATE SET
                        docs_version=excluded.docs_version,
                        tool_name=excluded.tool_name,
                        source_type=excluded.source_type,
                        item_class=excluded.item_class,
                        severity=excluded.severity,
                        domain=excluded.domain,
                        queue_status=excluded.queue_status,
                        requirement_route_status=excluded.requirement_route_status,
                        feature=excluded.feature,
                        feature_slug=excluded.feature_slug,
                        host_runtime=excluded.host_runtime,
                        source_run_id=excluded.source_run_id,
                        summary=excluded.summary,
                        project_root=excluded.project_root,
                        last_seen_at=excluded.last_seen_at,
                        occurrence_count=excluded.occurrence_count,
                        accepted_at=CASE
                            WHEN excluded.requirement_route_status = 'accepted_for_requirement' AND excluded.accepted_at <> ''
                            THEN excluded.accepted_at
                            ELSE friction_items.accepted_at
                        END
                    """,
                    (
                        project_key,
                        item_id,
                        str(docs_version or ""),
                        str(tool_name or ""),
                        str(source_type or ""),
                        str(item.get("item_class") or "improvement"),
                        str(item.get("severity") or "P2"),
                        str(item.get("domain") or "workflow"),
                        queue_status,
                        requirement_route_status,
                        str(item.get("feature") or ""),
                        str(item.get("feature_slug") or ""),
                        str(item.get("host_runtime") or ""),
                        str(run_id or ""),
                        str(item.get("summary") or item.get("friction_summary") or ""),
                        str(project_root),
                        first_seen_at,
                        now,
                        occurrence_count,
                        str(item.get("accepted_at") or ""),
                    ),
                )
                conn.execute(
                    "DELETE FROM friction_refs WHERE project_key = ? AND item_id = ?",
                    (project_key, item_id),
                )
                for ref in item.get("evidence_refs", []) if isinstance(item.get("evidence_refs"), list) else []:
                    ref_path = str(ref or "").strip()
                    if not ref_path:
                        continue
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO friction_refs (
                            project_key, item_id, ref_path, ref_kind, ref_scope, sha256
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            project_key,
                            item_id,
                            ref_path,
                            "evidence",
                            "project_local",
                            "",
                        ),
                    )
                event_type = "captured" if row is None else "observed"
                payload = {
                    "tool_name": tool_name,
                    "source_type": source_type,
                    "summary": str(item.get("summary") or item.get("friction_summary") or ""),
                    "run_id": str(run_id or ""),
                }
                conn.execute(
                    """
                    INSERT OR REPLACE INTO friction_events (
                        event_id, project_key, item_id, event_type, event_at, from_status, to_status, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        _friction_event_id(project_key, item_id, event_type, now, payload),
                        project_key,
                        item_id,
                        event_type,
                        now,
                        str((row["queue_status"] if row else "") or ""),
                        queue_status,
                        _json_text(payload),
                    ),
                )
                item_ids.append(item_id)
            conn.commit()
        return {
            "status": "ok",
            "db_path": str(db_path),
            "project_key": project_key,
            "item_ids": item_ids,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "db_path": str(db_path),
            "project_key": project_key,
            "item_ids": item_ids,
            "error": str(exc),
        }


def list_friction_items(*, project_root: Path, limit: int = 20) -> list[dict[str, Any]]:
    project_key = _runtime_project_key(project_root)
    try:
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT project_key, item_id, docs_version, tool_name, source_type, item_class, severity, domain,
                       queue_status, requirement_route_status, feature, feature_slug, host_runtime, source_run_id,
                       summary, project_root, first_seen_at, last_seen_at, occurrence_count, accepted_at
                FROM friction_items
                WHERE project_key = ?
                ORDER BY last_seen_at DESC, item_id ASC
                LIMIT ?
                """,
                (project_key, max(1, limit)),
            ).fetchall()
        return [dict(row) for row in rows]
    except Exception:  # noqa: BLE001
        return []


def transition_friction_item(*, project_root: Path, item_id: str, action: str) -> dict[str, Any]:
    normalized_action = str(action or "").strip().lower()
    transitions = {
        "claim": ("queue_status", "claimed", "claimed"),
        "resolve": ("queue_status", "resolved", "resolved"),
        "reopen": ("queue_status", "reopened", "reopened"),
        "accept": ("requirement_route_status", "accepted_for_requirement", "accepted_for_requirement"),
    }
    if normalized_action not in transitions:
        raise ValueError(f"unsupported friction action: {action}")
    field_name, next_value, event_type = transitions[normalized_action]
    project_key = _runtime_project_key(project_root)
    now = now_iso()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT project_key, item_id, queue_status, requirement_route_status
            FROM friction_items
            WHERE project_key = ? AND item_id = ?
            """,
            (project_key, item_id),
        ).fetchone()
        if row is None:
            raise ValueError(f"friction item not found: {item_id}")
        from_status = str(row[field_name] or "")
        conn.execute(
            f"""
            UPDATE friction_items
            SET {field_name} = ?, accepted_at = CASE
                WHEN ? = 'accept' THEN ?
                ELSE accepted_at
            END, last_seen_at = ?
            WHERE project_key = ? AND item_id = ?
            """,
            (next_value, normalized_action, now, now, project_key, item_id),
        )
        payload = {"action": normalized_action}
        conn.execute(
            """
            INSERT OR REPLACE INTO friction_events (
                event_id, project_key, item_id, event_type, event_at, from_status, to_status, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _friction_event_id(project_key, item_id, event_type, now, payload),
                project_key,
                item_id,
                event_type,
                now,
                from_status,
                next_value,
                _json_text(payload),
            ),
        )
        conn.commit()
        updated = conn.execute(
            """
            SELECT project_key, item_id, queue_status, requirement_route_status, accepted_at, last_seen_at
            FROM friction_items
            WHERE project_key = ? AND item_id = ?
            """,
            (project_key, item_id),
        ).fetchone()
    return dict(updated) if updated is not None else {}


def _latest_projection_write_from_sqlite(
    project_key: str,
    *,
    source_hash: str = "",
    projection_seq: str = "",
) -> dict[str, Any]:
    if not project_key:
        return {}
    try:
        where_clauses = ["project_key = ?"]
        params: list[Any] = [project_key]
        if source_hash:
            where_clauses.append("source_hash = ?")
            params.append(source_hash)
        if projection_seq:
            where_clauses.append("projection_seq = ?")
            params.append(projection_seq)
        with _connect() as conn:
            row = conn.execute(
                f"""
                SELECT projection_seq, transaction_id, project_key, source_hash, write_status,
                       preflight_status, confidence, uncertainty_reason, sqlite_status, pocketbase_status,
                       sink_checksums_json, occurred_at, wrote_at, payload_json
                FROM projection_writes
                WHERE {" AND ".join(where_clauses)}
                ORDER BY wrote_at DESC
                LIMIT 1
                """,
                tuple(params),
            ).fetchone()
        if row is None:
            return {}
        payload = dict(row)
        try:
            payload["sink_checksums"] = json.loads(str(payload.get("sink_checksums_json") or "{}"))
        except Exception:  # noqa: BLE001
            payload["sink_checksums"] = {}
        payload_raw = str(payload.get("payload_json") or "")
        try:
            payload["envelope"] = json.loads(payload_raw) if payload_raw else {}
        except Exception:  # noqa: BLE001
            payload["envelope"] = {}
        return payload
    except Exception:  # noqa: BLE001
        return {}


def _latest_projection_write_from_event_log(
    project_key: str,
    *,
    source_hash: str = "",
    projection_seq: str = "",
) -> dict[str, Any]:
    root = _transaction_events_root()
    if not root.exists():
        return {}
    candidates = sorted(root.glob("*.json"), key=lambda path: path.stat().st_mtime_ns, reverse=True)
    for path in candidates:
        payload = read_json(path, {})
        if not isinstance(payload, dict):
            continue
        if project_key and str(payload.get("project_key") or "") != project_key:
            continue
        payload_source_hash = str(payload.get("source_hash") or "")
        payload_projection_seq = str(payload.get("projection_seq") or "")
        if source_hash and payload_source_hash != source_hash:
            continue
        if projection_seq and payload_projection_seq != projection_seq:
            continue
        sink_checksums = payload.get("sink_checksums") if isinstance(payload.get("sink_checksums"), dict) else {}
        return {
            "projection_seq": payload_projection_seq,
            "transaction_id": str(payload.get("transaction_id") or ""),
            "project_key": str(payload.get("project_key") or ""),
            "source_hash": payload_source_hash,
            "write_status": str(payload.get("status") or ""),
            "preflight_status": str(payload.get("preflight_status") or ""),
            "sqlite_status": str(payload.get("sqlite_status") or ""),
            "pocketbase_status": str(payload.get("pocketbase_status") or ""),
            "occurred_at": str(payload.get("occurred_at") or ""),
            "wrote_at": str(payload.get("committed_at") or payload.get("occurred_at") or ""),
            "sink_checksums": sink_checksums,
            "envelope": {},
            "event_path": str(path),
        }
    return {}


def runtime_projection_transaction_contract(
    *,
    project_root: Path,
    docs_version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    from beacon.utils.runtime_projection import build_runtime_projection

    envelope = build_runtime_projection(project_root, docs_version=docs_version, feature=feature)
    project_key = str(envelope.get("project_key") or "")
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), dict) else {}
    expected_source_hash = str(projection.get("source_hash") or "")
    expected_projection_seq = str(projection.get("projection_seq") or "")

    latest = _latest_projection_write_from_sqlite(
        project_key,
        source_hash=expected_source_hash,
        projection_seq=expected_projection_seq,
    ) or _latest_projection_write_from_event_log(
        project_key,
        source_hash=expected_source_hash,
        projection_seq=expected_projection_seq,
    )
    matched_projection_context = bool(latest)
    if not latest:
        latest = _latest_projection_write_from_sqlite(project_key) or _latest_projection_write_from_event_log(project_key)
    if not latest:
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "runtime_projection_transaction_missing",
            "message": "runtime projection transaction record missing",
            "project_key": project_key,
            "expected_source_hash": expected_source_hash,
            "expected_projection_seq": expected_projection_seq,
            "details": {},
        }
    if not matched_projection_context:
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "runtime_projection_transaction_context_missing",
            "message": "runtime projection transaction for current context is missing; rebuild runtime ledger for this docs/feature context",
            "project_key": project_key,
            "expected_source_hash": expected_source_hash,
            "expected_projection_seq": expected_projection_seq,
            "details": latest,
        }

    sink_checksums = latest.get("sink_checksums") if isinstance(latest.get("sink_checksums"), dict) else {}
    write_status = str(latest.get("write_status") or "").strip().lower()
    sqlite_status = str(latest.get("sqlite_status") or "").strip().lower()
    pocketbase_status = str(latest.get("pocketbase_status") or "").strip().lower()
    metadata_ok = bool(latest.get("transaction_id")) and bool(latest.get("source_hash")) and bool(latest.get("projection_seq"))
    checksum_ok = (
        bool(sink_checksums.get("machine"))
        and bool(sink_checksums.get("human"))
        and bool(sink_checksums.get("sqlite"))
        and str(sink_checksums.get("machine")) not in {"missing", "failed"}
        and str(sink_checksums.get("human")) not in {"missing", "failed"}
        and str(sink_checksums.get("sqlite")) not in {"missing", "failed"}
    )
    alignment_ok = (
        str(latest.get("source_hash") or "") == expected_source_hash
        and str(latest.get("projection_seq") or "") == expected_projection_seq
    )

    if write_status == "failed_transaction" or sqlite_status in {"failed", "unavailable"} or pocketbase_status == "failed":
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "runtime_projection_failed_transaction",
            "message": "runtime projection transaction failed; release/freeze must be blocked until rebuild",
            "project_key": project_key,
            "expected_source_hash": expected_source_hash,
            "expected_projection_seq": expected_projection_seq,
            "details": latest,
        }

    if not metadata_ok or not checksum_ok or not alignment_ok:
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "runtime_projection_drift",
            "message": "runtime projection metadata/checksum drift detected across sinks",
            "project_key": project_key,
            "expected_source_hash": expected_source_hash,
            "expected_projection_seq": expected_projection_seq,
            "details": latest,
        }

    return {
        "status": "pass",
        "blocked": False,
        "reason_code": "runtime_projection_transaction_ok",
        "message": "runtime projection transaction metadata is consistent",
        "project_key": project_key,
        "expected_source_hash": expected_source_hash,
        "expected_projection_seq": expected_projection_seq,
        "details": latest,
    }


def verify_runtime_ledger(
    *,
    project_root: Path,
    docs_version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    from beacon.utils.runtime_projection import build_runtime_projection

    envelope1 = build_runtime_projection(project_root, docs_version=docs_version, feature=feature)
    envelope2 = build_runtime_projection(project_root, docs_version=docs_version, feature=feature)
    preflight = preflight_projection_write(envelope1)
    deterministic = (
        str((envelope1.get("projection") or {}).get("source_hash") or "")
        == str((envelope2.get("projection") or {}).get("source_hash") or "")
        and str((envelope1.get("projection") or {}).get("projection_seq") or "")
        == str((envelope2.get("projection") or {}).get("projection_seq") or "")
    )
    envelope_path = projection_envelope_path(envelope1)
    control_plane = inspect_pocketbase_control_plane()
    db_path = runtime_ledger_db_path()
    transaction_contract = runtime_projection_transaction_contract(
        project_root=project_root,
        docs_version=docs_version,
        feature=feature,
    )
    checks = [
        {
            "name": "projection_determinism",
            "status": "pass" if deterministic else "fail",
            "details": {
                "source_hash": str((envelope1.get("projection") or {}).get("source_hash") or ""),
                "projection_seq": str((envelope1.get("projection") or {}).get("projection_seq") or ""),
            },
        },
        {
            "name": "projection_preflight",
            "status": "fail" if preflight["status"] in {"conflicted", "blocked"} else "warn" if preflight["status"] == "partial" else "pass",
            "details": preflight,
        },
        {
            "name": "projection_envelope_anchor",
            "status": "pass" if envelope_path.exists() else "warn",
            "details": {"path": str(envelope_path), "exists": envelope_path.exists()},
        },
        {
            "name": "sqlite_store",
            "status": "warn" if _sqlite_disabled() else "pass" if db_path.exists() else "warn",
            "details": {"path": str(db_path), "exists": db_path.exists(), "disabled": _sqlite_disabled()},
        },
        {
            "name": "pocketbase_control_plane",
            "status": "pass" if control_plane.get("status") == "ready" else "warn",
            "details": control_plane,
        },
        {
            "name": "pocketbase_binary",
            "status": "pass" if bool(control_plane.get("binary_available")) else "warn",
            "details": {
                "binary_available": bool(control_plane.get("binary_available")),
                "binary_path": str(control_plane.get("binary_path") or ""),
                "admin_ui": str(control_plane.get("admin_ui") or ""),
            },
        },
        {
            "name": "pocketbase_board_surface",
            "status": "pass"
            if (pocketbase_public_root() / "index.html").exists()
            and (pocketbase_public_root() / "portfolio-overview" / "index.html").exists()
            and (pocketbase_public_root() / "data" / "portfolio-summary.json").exists()
            else "warn",
            "details": {
                "public_root": str(pocketbase_public_root()),
                "index": str((pocketbase_public_root() / "index.html")),
                "portfolio_page": str((pocketbase_public_root() / "portfolio-overview" / "index.html")),
                "portfolio_data": str((pocketbase_public_root() / "data" / "portfolio-summary.json")),
            },
        },
        {
            "name": "runtime_projection_transaction_contract",
            "status": str(transaction_contract.get("status") or "warn"),
            "details": transaction_contract,
        },
    ]
    status = "pass"
    if any(item["status"] == "fail" for item in checks):
        status = "fail"
    elif any(item["status"] == "warn" for item in checks):
        status = "warn"
    return {
        "schema_version": "1.0",
        "status": status,
        "project_root": str(project_root),
        "checks": checks,
        "preflight": preflight,
        "envelope_path": str(envelope_path),
        "db_path": str(db_path),
        "control_plane": control_plane,
    }


def export_runtime_ledger(*, label: str | None = None) -> dict[str, Any]:
    stamp = label or now_iso().replace(":", "").replace("-", "")
    export_root = runtime_ledger_exports_root() / stamp
    _ensure_dir(export_root)
    copied: dict[str, str] = {}

    db_path = runtime_ledger_db_path()
    if db_path.exists():
        target = export_root / db_path.name
        _ensure_parent(target)
        shutil.copy2(db_path, target)
        copied["sqlite"] = str(target)

    projections_root = runtime_ledger_projection_root()
    if projections_root.exists():
        target = export_root / "projections"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(projections_root, target)
        copied["projections"] = str(target)

    pocketbase_root = pocketbase_projection_root()
    if pocketbase_root.exists():
        target = export_root / "pocketbase"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(pocketbase_root, target)
        copied["pocketbase"] = str(target)

    manifest = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "export_root": str(export_root),
        "copied": copied,
    }
    write_json(export_root / "export-manifest.json", manifest)
    return manifest


def rebuild_runtime_ledger(
    *,
    project_root: Path,
    docs_version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    from beacon.utils.runtime_projection import build_runtime_projection

    envelope = build_runtime_projection(project_root, docs_version=docs_version, feature=feature)
    result = sync_projection(envelope)
    return {
        "schema_version": "1.0",
        "project_root": str(project_root),
        "docs_version": str(envelope.get("docs_version") or ""),
        "project_key": str(envelope.get("project_key") or ""),
        "status": str(result.get("status") or ""),
        "sync": result,
        "envelope_path": str(result.get("envelope_path") or projection_envelope_path(envelope)),
    }
