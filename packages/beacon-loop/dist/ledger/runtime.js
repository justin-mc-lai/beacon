import { ensureLedgerSchema, execSql, ledgerDbPath, sqliteAvailable } from "./db.js";
import { nowIso } from "../runner/types.js";

function escapeSql(value) {
  return String(value ?? "").replace(/'/g, "''");
}

export function runtimeSet(projectRoot, runId, options = {}) {
  if (!sqliteAvailable()) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "runtime-set", status: "blocked", reason_code: "sqlite3_unavailable" };
  }
  ensureLedgerSchema(projectRoot);
  const status = options.status || "running";
  const port = Number(options.port || 0);
  const notes = options.notes || "";
  const updatedAt = nowIso();
  execSql(
    projectRoot,
    `INSERT INTO runtime_tracking (run_id, status, port, notes, updated_at)
     VALUES ('${escapeSql(runId)}', '${escapeSql(status)}', ${port}, '${escapeSql(notes)}', '${escapeSql(updatedAt)}')
     ON CONFLICT(run_id) DO UPDATE SET status=excluded.status, port=excluded.port, notes=excluded.notes, updated_at=excluded.updated_at;`
  );
  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "runtime-set",
    status: "ok",
    run_id: runId,
    runtime: { status, port, notes, updated_at: updatedAt },
    ledger_path: ledgerDbPath(projectRoot)
  };
}

export function runtimeList(projectRoot, options = {}) {
  if (!sqliteAvailable()) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "runtime-list", status: "blocked", reason_code: "sqlite3_unavailable" };
  }
  ensureLedgerSchema(projectRoot);
  const statusFilter = options.status ? `WHERE status = '${escapeSql(options.status)}'` : "";
  const rows = execSql(projectRoot, `SELECT * FROM runtime_tracking ${statusFilter} ORDER BY updated_at DESC;`, { json: true });
  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "runtime-list",
    status: "ok",
    count: rows.length,
    runtime: rows
  };
}

export function runtimeRemove(projectRoot, runId) {
  if (!sqliteAvailable()) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "runtime-remove", status: "blocked", reason_code: "sqlite3_unavailable" };
  }
  ensureLedgerSchema(projectRoot);
  execSql(projectRoot, `DELETE FROM runtime_tracking WHERE run_id = '${escapeSql(runId)}';`);
  return { schema_version: "1.0", surface: "beacon-loop", command: "runtime-remove", status: "ok", run_id: runId };
}
