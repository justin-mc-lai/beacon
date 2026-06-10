import { existsSync } from "node:fs";
import { join } from "node:path";
import { resolveWorkspace } from "../git/branches.js";
import { commitAll, currentHead, rollback } from "../git/git.js";
import { runAgentAdapter } from "../agents/index.js";
import { ensureDir, readJson, writeJson, writeText } from "./fs.js";
import { buildIterationPrompt, loadNotes } from "./prompt.js";
import { syncRunToLedger } from "../ledger/runs.js";
import { RUN_STATES, defaultRunState, shouldForceStop, shouldGracefulStop, sleepMs } from "./state.js";
import { RUNTIME_ROLE, nowIso } from "./types.js";

const DEFAULT_CONSECUTIVE_FAILURE_LIMIT = 3;

function padIteration(n) {
  return String(n).padStart(3, "0");
}

function iterationPaths(runDir, n) {
  const id = padIteration(n);
  return {
    jsonl: join(runDir, `iteration-${id}.jsonl`),
    result: join(runDir, `iteration-${id}-result.json`)
  };
}

function appendNote(runDir, line) {
  const notesPath = join(runDir, "notes.md");
  const previous = loadNotes(runDir);
  writeText(notesPath, `${previous.replace(/\s*$/, "\n")}${line}\n`);
}

function tokenEstimate(result) {
  const usage = result?.raw?.token_usage || result?.raw?.usage || {};
  const total = Number(usage.total_tokens || usage.total || 0);
  if (total > 0) return total;
  const summary = String(result?.summary || "");
  return Math.max(1, Math.ceil(summary.length / 4));
}

function stopWhenMatched(stopWhen, iterationResult, iteration, maxIterations) {
  const needle = String(stopWhen || "").toLowerCase();
  if (!needle) return false;
  if (iterationResult?.raw?.stop_signal === true) return true;
  const summary = String(iterationResult?.summary || "").toLowerCase();
  if (summary.includes("stop-when matched")) return true;
  if (needle.includes("implementation evidence candidate") && iterationResult?.success && iteration >= maxIterations) return true;
  return false;
}

function isNoOpFailure(result) {
  return Boolean(result?.success) && (!Array.isArray(result.key_changes_made) || result.key_changes_made.length === 0);
}

function writeSummary(runDir, runPackage, runState, resolver) {
  const elapsedMs = runState.started_at
    ? Date.now() - Date.parse(runState.started_at)
    : 0;
  const branch = runPackage.worktree?.branch || "";
  const lines = [
    "# Beacon Loop Summary",
    "",
    `- run_id: ${runPackage.run_id}`,
    `- status: ${runState.machine_state}`,
    `- iterations_completed: ${runState.iteration}`,
    `- total_tokens: ${runState.total_tokens}`,
    `- elapsed_ms: ${elapsedMs}`,
    `- branch: ${branch}`,
    `- worktree: ${runPackage.worktree?.path || ""}`,
    `- cap_reason: ${runState.cap_reason || "none"}`,
    `- stop_reason: ${runState.stop_reason || "none"}`,
    `- closure_verdict: not_provided_by_beacon_loop`,
    `- qa_release_boundary: Beacon QA/release surfaces remain authoritative.`,
    "",
    "## Artifact paths",
    `- run_package: .beacon/loop/runs/${runPackage.run_id}/run-package.json`,
    `- notes: .beacon/loop/runs/${runPackage.run_id}/notes.md`,
    `- commits: .beacon/loop/runs/${runPackage.run_id}/commits.json`,
    "",
    "## Next commands",
    `- review: beacon-loop review ${runPackage.run_id}`,
    `- import: ${runPackage.beacon_commands?.import_evidence || "beacon implement import-evidence"}`,
    `- qa: ${runPackage.beacon_commands?.qa || "beacon qa run"}`,
    `- release: ${runPackage.beacon_commands?.release || "beacon release create"}`,
    `- resolver: ${resolver.command || ""}`
  ];
  writeText(join(runDir, "summary.md"), `${lines.join("\n")}\n`);
}

function writeRuntimeEvidence(runDir, runPackage, resolver, runState, changedFiles = []) {
  const evidence = {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    surface: "beacon-loop",
    status: runState.machine_state,
    closure_verdict: "not_provided_by_beacon_loop",
    feature: runPackage.feature,
    version: runPackage.version,
    run_id: runPackage.run_id,
    iterations: runState.iteration,
    changed_files: changedFiles,
    summary_ref: `.beacon/loop/runs/${runPackage.run_id}/summary.md`,
    resolver_command: resolver.command
  };
  writeJson(join(runDir, "evidence.json"), evidence);
}

export function runOrchestrator(projectRoot, runDir, runPackage, resolver, options = {}) {
  const runStatePath = join(runDir, "run-state.json");
  const runState = { ...defaultRunState(), ...readJson(runStatePath, {}) };
  if (!runState.started_at) runState.started_at = nowIso();

  const maxIterations = Number(runPackage.max_iterations || 1);
  const maxTokens = Number(runPackage.max_tokens || 0);
  const consecutiveLimit = Number(options.consecutiveFailureLimit || DEFAULT_CONSECUTIVE_FAILURE_LIMIT);
  const backoffBaseMs = Number(process.env.BEACON_LOOP_TEST_BACKOFF_MS ?? 250);
  const worktreePath = runPackage.worktree?.path || "";
  const baseHead = runPackage.worktree?.base_head || currentHead(projectRoot);
  const commitsPath = join(runDir, "commits.json");
  const commitsDoc = readJson(commitsPath, { commits: [], repair_state: "" });
  let changedFiles = [];

  const startIteration = Number(options.startIteration || runState.iteration + 1);
  let finalStatus = "implementation_candidate";
  let reasonCode = "";

  for (let n = startIteration; n <= maxIterations; n += 1) {
    if (shouldForceStop(runDir, readJson)) {
      runState.machine_state = RUN_STATES.FORCE_STOPPED;
      runState.stop_reason = "force_stop_requested";
      finalStatus = "force_stopped";
      reasonCode = "force_stopped";
      break;
    }
    if (n > startIteration && shouldGracefulStop(runDir, readJson)) {
      runState.machine_state = RUN_STATES.CAP_REACHED;
      runState.cap_reason = "graceful_stop";
      runState.stop_reason = "graceful_stop_requested";
      finalStatus = "cap_reached";
      break;
    }

    if (process.env.BEACON_LOOP_TEST_FORCE_STOP_ON_ITERATION === String(n)) {
      writeJson(join(runDir, "interrupt-state.json"), { mode: "force", requested_at: nowIso() });
      runState.machine_state = RUN_STATES.FORCE_STOPPED;
      runState.stop_reason = "force_stop_requested";
      finalStatus = "force_stopped";
      reasonCode = "force_stopped";
      break;
    }

    runState.machine_state = RUN_STATES.ITERATING;
    writeJson(runStatePath, runState);

    const notes = loadNotes(runDir);
    const prompt = buildIterationPrompt(runPackage, runPackage, n, notes);
    writeText(join(runDir, "prompt.md"), `${prompt}\n`);
    writeText(join(runDir, `iteration-${padIteration(n)}-prompt.txt`), `${prompt}\n`);

    const iteration = runAgentAdapter(runPackage.agent || "codex", worktreePath, runPackage.run_id, {
      prompt,
      iteration: n,
      maxTokens: runPackage.max_tokens,
      stopWhen: runPackage.stop_when
    });
    const paths = iterationPaths(runDir, n);
    writeText(paths.jsonl, `${JSON.stringify({ event: "agent_result", at: nowIso(), iteration: n, result: iteration })}\n`);
    writeJson(paths.result, iteration);

    const tokens = tokenEstimate(iteration);
    runState.total_tokens += tokens;

    if (iteration.force_commit_failure) {
      writeJson(join(runDir, "repair-state.json"), { status: "repair_required", reason_code: "commit_failure_repair_required", iteration: n });
      commitsDoc.repair_state = "commit_failure_repair_required";
      writeJson(commitsPath, commitsDoc);
      runState.machine_state = RUN_STATES.REPAIR_REQUIRED;
      runState.iteration = n;
      finalStatus = "repair_required";
      reasonCode = "commit_failure_repair_required";
      break;
    }

    const hardError = iteration.retryable_hard_error === true;
    const treatedAsFailure = !iteration.success || isNoOpFailure(iteration) || hardError;

    if (treatedAsFailure) {
      rollback(worktreePath, baseHead);
      runState.machine_state = RUN_STATES.ITERATION_FAIL_ROLLBACK;
      runState.consecutive_failures += 1;
      appendNote(runDir, `- iteration ${n}: failure (${iteration.summary || "agent failure"})`);

      if (hardError && runState.consecutive_failures < consecutiveLimit) {
        const backoffMs = backoffBaseMs * 2 ** Math.max(0, runState.consecutive_failures - 1);
        runState.machine_state = RUN_STATES.WAITING_BACKOFF;
        writeJson(runStatePath, runState);
        sleepMs(backoffMs);
        n -= 1;
        continue;
      }

      if (runState.consecutive_failures >= consecutiveLimit) {
        runState.machine_state = RUN_STATES.CAP_REACHED;
        runState.cap_reason = "consecutive_failures_abort";
        finalStatus = "rolled_back";
        reasonCode = "consecutive_failures_abort";
        break;
      }
      runState.iteration = n;
      writeJson(runStatePath, runState);
      continue;
    }

    const commit = commitAll(worktreePath, `beacon-loop: ${runPackage.feature} ${runPackage.run_id} iteration ${n}`);
    if (commit.code !== 0) {
      writeJson(join(runDir, "repair-state.json"), { status: "repair_required", reason_code: "commit_failure_repair_required", iteration: n, stderr: commit.stderr });
      commitsDoc.repair_state = "commit_failure_repair_required";
      writeJson(commitsPath, commitsDoc);
      runState.machine_state = RUN_STATES.REPAIR_REQUIRED;
      runState.iteration = n;
      finalStatus = "repair_required";
      reasonCode = "commit_failure_repair_required";
      break;
    }

    const commitHash = commit.stdout.match(/[a-f0-9]{7,40}/)?.[0] || "";
    commitsDoc.commits.push({ iteration: n, commit: commitHash, message: `beacon-loop: ${runPackage.feature} ${runPackage.run_id} iteration ${n}` });
    commitsDoc.repair_state = "";
    writeJson(commitsPath, commitsDoc);
    changedFiles = [...changedFiles, ...(iteration.key_changes_made || [])];
    runState.consecutive_failures = 0;
    runState.iteration = n;
    runState.machine_state = RUN_STATES.ITERATION_SUCCESS_COMMIT;
    appendNote(runDir, `- iteration ${n}: success (${iteration.summary || "ok"})`);

    if (maxTokens > 0 && runState.total_tokens >= maxTokens) {
      runState.machine_state = RUN_STATES.CAP_REACHED;
      runState.cap_reason = "max_tokens";
      finalStatus = "cap_reached";
      break;
    }
    if (stopWhenMatched(runPackage.stop_when, iteration, n, maxIterations)) {
      runState.machine_state = RUN_STATES.CAP_REACHED;
      runState.cap_reason = "stop_when";
      finalStatus = "cap_reached";
      break;
    }
    if (process.env.BEACON_LOOP_TEST_STOP_AFTER_ITERATION === String(n)) {
      runState.machine_state = RUN_STATES.CAP_REACHED;
      runState.cap_reason = "graceful_stop";
      runState.stop_reason = "graceful_stop_requested";
      finalStatus = "cap_reached";
      break;
    }
    if (n >= maxIterations) {
      runState.machine_state = RUN_STATES.CAP_REACHED;
      runState.cap_reason = "max_iterations";
      finalStatus = "cap_reached";
      break;
    }
    writeJson(runStatePath, runState);
  }

  if (finalStatus === "implementation_candidate" && commitsDoc.commits.length === 0 && runState.consecutive_failures > 0) {
    finalStatus = "rolled_back";
    if (!reasonCode) reasonCode = "iteration_failed";
  }

  const importableCapReasons = ["max_iterations", "stop_when"];
  if (finalStatus === "cap_reached" && importableCapReasons.includes(runState.cap_reason) && commitsDoc.commits.length > 0) {
    finalStatus = "implementation_candidate";
    runState.machine_state = RUN_STATES.IMPLEMENTATION_CANDIDATE;
  } else if (finalStatus === "implementation_candidate" && runState.machine_state === RUN_STATES.ITERATION_SUCCESS_COMMIT) {
    runState.machine_state = RUN_STATES.IMPLEMENTATION_CANDIDATE;
  }
  runState.finished_at = nowIso();
  writeJson(runStatePath, runState);
  writeJson(join(runDir, "run-package.json"), runPackage);
  writeSummary(runDir, runPackage, runState, resolver);
  writeRuntimeEvidence(runDir, runPackage, resolver, runState, changedFiles);
  try {
    syncRunToLedger(projectRoot, runPackage.run_id, {
      status: finalStatus,
      machine_state: runState.machine_state,
      iteration: runState.iteration,
      finalStatus
    });
  } catch {
    // Ledger is harness support; runner completion must not fail on sqlite edge cases.
  }

  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: options.command || "goal",
    status: finalStatus,
    reason_code: reasonCode,
    run_id: runPackage.run_id,
    run_dir: runDir,
    iteration: runState.iteration,
    machine_state: runState.machine_state,
    closure_verdict: "not_provided_by_beacon_loop"
  };
}

export { resolveWorkspace } from "../git/branches.js";
