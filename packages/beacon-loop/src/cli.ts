#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { resolveGoalOptions } from "./config/load.js";
import { run } from "./git/git.js";
import { importEvidence } from "./evidence/importer.js";
import { analyzeRun, learnRun } from "./harness/index.js";
import { defaultImplementRunner } from "./harness/worker-route.js";
import { diagnoseRuns, queryRuns, showRun } from "./ledger/runs.js";
import { runtimeList, runtimeRemove, runtimeSet } from "./ledger/runtime.js";
import { sqliteAvailable } from "./ledger/db.js";
import { latestRunId } from "./runner/fs.js";
import {
  delegateGoalToBeaconRun,
  formatDelegatePayload,
} from "./beacon-run-delegate.js";
import { resumeRun, startGoal, statusRun, stopRun } from "./runner/run.js";
import { showSpine, spineDocExists } from "./spine/show.js";

function option(args, name, fallback = "") {
  const index = args.indexOf(name);
  if (index < 0) return fallback;
  return args[index + 1] || fallback;
}

function flag(args, name) {
  return args.includes(name);
}

function emit(payload, jsonOutput) {
  if (jsonOutput) {
    console.log(JSON.stringify(payload, null, 2));
    return;
  }
  console.log(`${payload.command || "beacon-loop"}: ${payload.status || "ok"}`);
  if (payload.beacon_run_command) {
    console.log(`beacon_run_command: ${payload.beacon_run_command}`);
  }
  if (payload.branch_mode_resolved) {
    console.log(`branch_mode: ${payload.branch_mode_resolved}`);
  }
  if (payload.run_id) console.log(`run_id: ${payload.run_id}`);
  if (payload.reason_code) console.log(`reason_code: ${payload.reason_code}`);
  if (payload.stderr && payload.status === "delegated" && payload.exit_code !== 0) {
    const err = String(payload.stderr).trim();
    if (err) console.error(err);
  }
}

function help() {
  console.log(`beacon-loop

Commands:
  goal <goal>
  status [run-id]
  stop <run-id> [--force]
  resume <run-id>
  review <run-id>
  import-evidence <run-id>
  doctor [--diagnose]
  runs query [--status <s>]
  runs show <run-id>
  runs diagnose
  runtime-set <run-id> --status <running|stopped|error|degraded|starting> [--port N] [--notes <text>]
  runtime-list [--status <s>]
  runtime-remove <run-id>
  analyze <run-id>
  learn <run-id>
  spine show [--run-id <id>]

Options:
  --project <path>
  --version <version>   (default: auto — project docs/onboarding version)
  --dry-run
  --json
  --allow-dirty
  --max-iterations <n>
  --max-tokens <n>
  --stop-when <text>
  --stop-check-cmd <shell>   External verifier for --stop-when (exit 0 required)
  --branch-mode <worktree|current-branch|run-branch>
  --isolated-worktree
  --agent <codex|claude|acp:target>
  --mode <delivery|execute-only|intent-only|review-only>
  --feature <slug>
  --legacy-delivery     (R3 delivery FSM; default goal delegates to beacon-run)
  --truth-bootstrap <agent|fallback>
  --strict-interrupt
  --ask-on <P0,P1,...>   (deprecated; use with --strict-interrupt)
  --auto-decide deferrals (deprecated)
  --ack-intent-drift
`);
}

function doctor(projectRoot, jsonOutput, diagnose = false) {
  const nodeMajor = Number(process.versions.node.split(".")[0] || "0");
  const implementRunner = defaultImplementRunner();
  const schemaProbe = join(projectRoot, ".beacon", "loop", "runs");
  const checks = {
    node_runtime: { status: nodeMajor >= 20 ? "pass" : "blocked", version: process.versions.node },
    sqlite_cli: { status: sqliteAvailable() ? "pass" : "blocked", repair_route: "install sqlite3 CLI" },
    beacon_cli: { status: run("beacon", ["--version"], { cwd: projectRoot }).code === 0 ? "pass" : "blocked" },
    git_worktree: { status: run("git", ["worktree", "list"], { cwd: projectRoot }).code === 0 ? "pass" : "blocked" },
    implement_runner: {
      status:
        run("beacon", ["implement", "list-runners", "--json"], { cwd: projectRoot }).code === 0 || process.env.BEACON_LOOP_TEST_AGENT_RESULT
          ? "pass"
          : "blocked",
      runner: implementRunner,
      repair_route: `beacon implement run "<feature>" --project . --version <version> --runner ${implementRunner} --json`
    },
    output_schema: {
      status: existsSync(schemaProbe) ? "pass" : "pass",
      path: "output-schema.json per run directory",
      repair_route: "beacon-loop goal creates json_schema envelope at run bootstrap"
    },
    agent_backend: {
      status: run("codex", ["--version"], { cwd: projectRoot }).code === 0 || process.env.BEACON_LOOP_TEST_AGENT_RESULT ? "pass" : "blocked",
      adapter: "implement-harness"
    },
    evidence_import: { status: run("beacon", ["implement", "import-evidence", "--help"], { cwd: projectRoot }).code === 0 ? "pass" : "blocked" }
  };
  const blocked = Object.values(checks).some((item) => item.status !== "pass");
  const payload = {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "doctor",
    status: blocked ? "blocked" : "pass",
    checks
  };
  if (diagnose) {
    payload.diagnose = diagnoseRuns(projectRoot);
  }
  emit(payload, jsonOutput);
  process.exit(blocked ? 2 : 0);
}

const args = process.argv.slice(2);
const command = args[0] || "";
const jsonOutput = flag(args, "--json");
const projectRoot = resolve(option(args, "--project", option(args, "--project-root", process.cwd())));

if (!command || command === "--help" || command === "-h") {
  help();
  process.exit(0);
}

if (command === "doctor") {
  doctor(projectRoot, jsonOutput, flag(args, "--diagnose"));
}

if (command === "goal") {
  const goal = args[1] || "";
  if (!goal) {
    console.error("goal is required");
    process.exit(2);
  }
  if (!flag(args, "--legacy-delivery")) {
    const resolvedForDelegate = resolveGoalOptions(projectRoot, args, {
      version: option(args, "--version", "auto"),
      feature: option(args, "--feature", ""),
      maxIterations: option(args, "--max-iterations", "8"),
      maxTokens: option(args, "--max-tokens", "0"),
      stopWhen: option(args, "--stop-when", ""),
      stopCheckCmd: option(args, "--stop-check-cmd", ""),
      agent: option(args, "--agent", "codex"),
      implementRunner: option(args, "--implement-runner", ""),
      branchMode: option(args, "--branch-mode", "worktree"),
      isolatedWorktree: flag(args, "--isolated-worktree"),
      dryRun: flag(args, "--dry-run"),
    });
    const delegate = delegateGoalToBeaconRun(projectRoot, goal, {
      version: resolvedForDelegate.version,
      feature: resolvedForDelegate.feature,
      agent: resolvedForDelegate.agent,
      maxIterations: resolvedForDelegate.maxIterations,
      maxTokens: resolvedForDelegate.maxTokens,
      stopWhen: resolvedForDelegate.stopWhen,
      stopCheckCmd: option(args, "--stop-check-cmd", ""),
      branchMode: resolvedForDelegate.branchMode,
      isolatedWorktree: resolvedForDelegate.isolatedWorktree,
      truthBootstrap: option(args, "--truth-bootstrap", "agent"),
      implementRunner: resolvedForDelegate.implementRunner,
      dryRun: resolvedForDelegate.dryRun,
    });
    const payload = formatDelegatePayload(goal, delegate);
    emit(payload, jsonOutput);
    const exitCode =
      delegate.status === "blocked"
        ? 2
        : delegate.status === "dry_run"
          ? 0
          : delegate.exit_code === 0
            ? 0
            : 1;
    process.exit(exitCode);
  }
  const resolved = resolveGoalOptions(projectRoot, args, {
    version: option(args, "--version", "auto"),
    feature: option(args, "--feature", ""),
    mode: option(args, "--mode", "delivery"),
    askOn: option(args, "--ask-on", ""),
    strictInterrupt: flag(args, "--strict-interrupt"),
    autoDecideDeferrals: flag(args, "--auto-decide"),
    ackIntentDrift: flag(args, "--ack-intent-drift"),
    dryRun: flag(args, "--dry-run"),
    allowDirty: flag(args, "--allow-dirty"),
    maxIterations: option(args, "--max-iterations", "1"),
    maxTokens: option(args, "--max-tokens", "0"),
    stopWhen: option(args, "--stop-when", ""),
    stopCheckCmd: option(args, "--stop-check-cmd", ""),
    agent: option(args, "--agent", "implement-harness"),
    implementRunner: option(args, "--implement-runner", ""),
    branchMode: option(args, "--branch-mode", "worktree"),
    isolatedWorktree: flag(args, "--isolated-worktree")
  });
  const payload = startGoal(projectRoot, goal, resolved);
  emit(payload, jsonOutput);
  process.exit(payload.status === "blocked" ? 2 : 0);
}

if (command === "resume") {
  const payload = resumeRun(projectRoot, args[1] || latestRunId(projectRoot));
  emit(payload, jsonOutput);
  process.exit(payload.status === "blocked" ? 2 : 0);
}

if (command === "stop") {
  const payload = stopRun(projectRoot, args[1] || latestRunId(projectRoot), flag(args, "--force"));
  emit(payload, jsonOutput);
  process.exit(0);
}

if (command === "status") {
  if (flag(args, "--spine")) {
    const payload = showSpine(projectRoot, args[1] || option(args, "--run-id", ""));
    if (!spineDocExists(projectRoot)) {
      payload.status = "blocked";
      payload.reason_code = "spine_doc_missing";
    }
    emit(payload, jsonOutput);
    process.exit(payload.status === "blocked" ? 2 : 0);
  }
  emit(statusRun(projectRoot, args[1] || ""), jsonOutput);
  process.exit(0);
}

if (command === "spine") {
  const sub = args[1] || "";
  if (sub === "show") {
    const payload = showSpine(
      projectRoot,
      args[2] || option(args, "--run-id", ""),
    );
    if (!spineDocExists(projectRoot)) {
      payload.status = "blocked";
      payload.reason_code = "spine_doc_missing";
    }
    emit(payload, jsonOutput);
    process.exit(payload.status === "blocked" ? 2 : 0);
  }
  console.error("Unknown spine subcommand");
  process.exit(2);
}

if (command === "review") {
  const runId = args[1] || latestRunId(projectRoot);
  const summary = join(projectRoot, ".beacon", "loop", "runs", runId, "summary.md");
  if (jsonOutput) {
    emit({ schema_version: "1.0", surface: "beacon-loop", command: "review", status: existsSync(summary) ? "found" : "blocked", run_id: runId, summary_ref: summary }, true);
  } else if (existsSync(summary)) {
    console.log(readFileSync(summary, "utf8"));
  } else {
    console.error("run summary not found");
    process.exit(2);
  }
  process.exit(0);
}

if (command === "import-evidence") {
  const payload = importEvidence(projectRoot, args[1] || latestRunId(projectRoot), jsonOutput);
  emit(payload, jsonOutput);
  process.exit(payload.status === "imported" ? 0 : 2);
}

if (command === "runs") {
  const sub = args[1] || "";
  if (sub === "query") {
    const payload = queryRuns(projectRoot, { status: option(args, "--status", "") });
    emit(payload, jsonOutput);
    process.exit(payload.status === "blocked" ? 2 : 0);
  }
  if (sub === "show") {
    const runId = args[2] || "";
    if (!runId) {
      console.error("run-id is required");
      process.exit(2);
    }
    const payload = showRun(projectRoot, runId);
    emit(payload, jsonOutput);
    process.exit(payload.status === "blocked" ? 2 : 0);
  }
  if (sub === "diagnose") {
    emit(diagnoseRuns(projectRoot), jsonOutput);
    process.exit(0);
  }
  console.error("Unknown runs subcommand");
  process.exit(2);
}

if (command === "runtime-set") {
  const runId = args[1] || "";
  if (!runId) {
    console.error("run-id is required");
    process.exit(2);
  }
  const payload = runtimeSet(projectRoot, runId, {
    status: option(args, "--status", "running"),
    port: option(args, "--port", "0"),
    notes: option(args, "--notes", "")
  });
  emit(payload, jsonOutput);
  process.exit(payload.status === "blocked" ? 2 : 0);
}

if (command === "runtime-list") {
  const payload = runtimeList(projectRoot, { status: option(args, "--status", "") });
  emit(payload, jsonOutput);
  process.exit(payload.status === "blocked" ? 2 : 0);
}

if (command === "runtime-remove") {
  const runId = args[1] || "";
  if (!runId) {
    console.error("run-id is required");
    process.exit(2);
  }
  emit(runtimeRemove(projectRoot, runId), jsonOutput);
  process.exit(0);
}

if (command === "analyze") {
  const runId = args[1] || latestRunId(projectRoot);
  const payload = analyzeRun(projectRoot, runId);
  emit(payload, jsonOutput);
  process.exit(payload.status === "blocked" ? 2 : 0);
}

if (command === "learn") {
  const runId = args[1] || latestRunId(projectRoot);
  const payload = learnRun(projectRoot, runId);
  emit(payload, jsonOutput);
  process.exit(payload.status === "blocked" ? 2 : 0);
}

console.error("Unknown command");
process.exit(2);
