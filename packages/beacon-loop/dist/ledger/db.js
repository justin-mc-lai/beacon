import { mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { spawnSync } from "node:child_process";

export function ledgerDbPath(projectRoot) {
  return join(projectRoot, ".beacon", "loop", "ledger", "loop-runs.db");
}

export function sqliteAvailable() {
  const probe = spawnSync("sqlite3", ["-version"], { encoding: "utf8" });
  return (probe.status ?? 1) === 0;
}

function escapeSql(value) {
  return String(value ?? "").replace(/'/g, "''");
}

export function execSql(projectRoot, sql, { json = false } = {}) {
  const dbPath = ledgerDbPath(projectRoot);
  mkdirSync(dirname(dbPath), { recursive: true });
  if (!existsSync(dbPath)) {
    spawnSync("sqlite3", [dbPath, "SELECT 1;"], { encoding: "utf8" });
  }
  const args = json ? ["-json", dbPath, sql] : [dbPath, sql];
  const result = spawnSync("sqlite3", args, { encoding: "utf8" });
  if ((result.status ?? 1) !== 0) {
    throw new Error(result.stderr || "sqlite3 command failed");
  }
  if (!json) return result.stdout || "";
  const text = (result.stdout || "").trim();
  if (!text) return [];
  return JSON.parse(text);
}

export function ensureLedgerSchema(projectRoot) {
  execSql(
    projectRoot,
    `
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  goal TEXT,
  feature TEXT,
  version TEXT,
  status TEXT,
  machine_state TEXT,
  iteration INTEGER DEFAULT 0,
  branch TEXT,
  run_dir TEXT,
  created_at TEXT,
  updated_at TEXT
);
CREATE TABLE IF NOT EXISTS runtime_tracking (
  run_id TEXT PRIMARY KEY,
  status TEXT,
  port INTEGER,
  notes TEXT,
  updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_feature ON runs(feature);
`
  );
}

export function upsertRunRecord(projectRoot, record) {
  ensureLedgerSchema(projectRoot);
  const fields = {
    run_id: record.run_id,
    goal: record.goal || "",
    feature: record.feature || "",
    version: record.version || "",
    status: record.status || "",
    machine_state: record.machine_state || "",
    iteration: Number(record.iteration || 0),
    branch: record.branch || "",
    run_dir: record.run_dir || "",
    created_at: record.created_at || record.updated_at || new Date().toISOString(),
    updated_at: record.updated_at || new Date().toISOString()
  };
  execSql(
    projectRoot,
    `INSERT INTO runs (run_id, goal, feature, version, status, machine_state, iteration, branch, run_dir, created_at, updated_at)
     VALUES ('${escapeSql(fields.run_id)}', '${escapeSql(fields.goal)}', '${escapeSql(fields.feature)}', '${escapeSql(fields.version)}',
             '${escapeSql(fields.status)}', '${escapeSql(fields.machine_state)}', ${fields.iteration},
             '${escapeSql(fields.branch)}', '${escapeSql(fields.run_dir)}', '${escapeSql(fields.created_at)}', '${escapeSql(fields.updated_at)}')
     ON CONFLICT(run_id) DO UPDATE SET
       goal=excluded.goal,
       feature=excluded.feature,
       version=excluded.version,
       status=excluded.status,
       machine_state=excluded.machine_state,
       iteration=excluded.iteration,
       branch=excluded.branch,
       run_dir=excluded.run_dir,
       updated_at=excluded.updated_at;`
  );
}
