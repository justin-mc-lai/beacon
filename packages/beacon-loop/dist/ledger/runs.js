import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { gitStatus, isGitRepo, run } from "../git/git.js";
import { readJson } from "../runner/fs.js";
import { ensureLedgerSchema, execSql, ledgerDbPath, sqliteAvailable, upsertRunRecord } from "./db.js";

function artifactRefs(projectRoot, runId) {
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  const refs = [];
  for (const name of ["run-package.json", "run-state.json", "summary.md", "evidence.json", "commits.json", "notes.md"]) {
    const path = join(runDir, name);
    if (existsSync(path)) refs.push(`.beacon/loop/runs/${runId}/${name}`);
  }
  if (existsSync(runDir)) {
    for (const name of readdirSync(runDir)) {
      if (/^iteration-\d{3}-result\.json$/.test(name)) refs.push(`.beacon/loop/runs/${runId}/${name}`);
    }
  }
  return refs;
}

export function syncRunToLedger(projectRoot, runId, overrides = {}) {
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  const runPackage = readJson(join(runDir, "run-package.json"), {});
  const runState = readJson(join(runDir, "run-state.json"), {});
  upsertRunRecord(projectRoot, {
    run_id: runId,
    goal: overrides.goal ?? runPackage.goal,
    feature: overrides.feature ?? runPackage.feature,
    version: overrides.version ?? runPackage.version,
    status: overrides.status ?? overrides.finalStatus ?? runState.machine_state,
    machine_state: overrides.machine_state ?? runState.machine_state,
    iteration: overrides.iteration ?? runState.iteration,
    branch: overrides.branch ?? runPackage.worktree?.branch,
    run_dir: `.beacon/loop/runs/${runId}`,
    created_at: runPackage.created_at,
    updated_at: runState.finished_at || runState.started_at || runPackage.created_at
  });
}

export function queryRuns(projectRoot, options = {}) {
  if (!sqliteAvailable()) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "runs query", status: "blocked", reason_code: "sqlite3_unavailable" };
  }
  ensureLedgerSchema(projectRoot);
  const statusFilter = options.status ? `WHERE status = '${String(options.status).replace(/'/g, "''")}'` : "";
  const rows = execSql(projectRoot, `SELECT * FROM runs ${statusFilter} ORDER BY updated_at DESC;`, { json: true });
  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "runs query",
    status: "ok",
    ledger_path: ledgerDbPath(projectRoot),
    count: rows.length,
    runs: rows
  };
}

export function showRun(projectRoot, runId) {
  if (!sqliteAvailable()) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "runs show", status: "blocked", reason_code: "sqlite3_unavailable", run_id: runId };
  }
  ensureLedgerSchema(projectRoot);
  const rows = execSql(projectRoot, `SELECT * FROM runs WHERE run_id = '${String(runId).replace(/'/g, "''")}' LIMIT 1;`, { json: true });
  const row = rows[0];
  if (!row) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "runs show", status: "blocked", reason_code: "run_not_found", run_id: runId };
  }
  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "runs show",
    status: "ok",
    run: row,
    artifact_refs: artifactRefs(projectRoot, runId)
  };
}

export function diagnoseRuns(projectRoot) {
  const buckets = {
    blocked: [],
    dirty_worktree: [],
    missing_backend: [],
    never_started: [],
    repair_required: [],
    healthy: []
  };

  if (!sqliteAvailable()) {
    buckets.missing_backend.push({ reason_code: "sqlite3_unavailable", repair_route: "install sqlite3 CLI" });
  }

  const dirty = isGitRepo(projectRoot) && Boolean(gitStatus(projectRoot));
  if (dirty) {
    buckets.dirty_worktree.push({ repair_route: "clean worktree or pass --allow-dirty for controlled runs" });
  }

  const codexOk = run("codex", ["--version"], { cwd: projectRoot }).code === 0 || Boolean(process.env.BEACON_LOOP_TEST_AGENT_RESULT);
  if (!codexOk) {
    buckets.missing_backend.push({ adapter: "codex", repair_route: "install codex CLI or set BEACON_LOOP_TEST_AGENT_RESULT for tests" });
  }

  const runsRoot = join(projectRoot, ".beacon", "loop", "runs");
  if (!existsSync(runsRoot)) {
    buckets.never_started.push({ repair_route: "beacon-loop goal \"<goal>\"" });
  } else {
    for (const runId of readdirSync(runsRoot)) {
      const runDir = join(runsRoot, runId);
      const runState = readJson(join(runDir, "run-state.json"), {});
      const repair = readJson(join(runDir, "repair-state.json"), null);
      if (repair?.status === "repair_required" || runState.machine_state === "repair_required") {
        buckets.repair_required.push({ run_id: runId, repair_route: `beacon-loop resume ${runId}` });
      } else if (["implementation_candidate", "cap_reached"].includes(runState.machine_state)) {
        buckets.healthy.push({ run_id: runId, repair_route: `beacon-loop import-evidence ${runId}` });
      } else if (runState.machine_state === "preflight_blocked") {
        buckets.blocked.push({ run_id: runId, repair_route: "beacon-gen-change" });
      }
    }
  }

  if (sqliteAvailable()) {
    ensureLedgerSchema(projectRoot);
    const ledgerRows = execSql(projectRoot, "SELECT run_id, status, machine_state FROM runs ORDER BY updated_at DESC LIMIT 50;", { json: true });
    for (const row of ledgerRows) {
      if (row.machine_state === "repair_required" && !buckets.repair_required.some((item) => item.run_id === row.run_id)) {
        buckets.repair_required.push({ run_id: row.run_id, repair_route: `beacon-loop resume ${row.run_id}` });
      }
    }
  }

  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "runs diagnose",
    status: "ok",
    buckets,
    ledger_path: sqliteAvailable() ? ledgerDbPath(projectRoot) : ""
  };
}
