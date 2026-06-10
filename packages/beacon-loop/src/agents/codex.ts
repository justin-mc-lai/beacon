import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { normalizeIterationResult } from "./schema.js";

function parseStructuredResult(stdout, stderr) {
  const lines = String(stdout || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  for (const line of lines.toReversed()) {
    try {
      const payload = JSON.parse(line);
      if (payload && typeof payload === "object") {
        return normalizeIterationResult(payload, "codex");
      }
    } catch {
      // Continue scanning for a structured line.
    }
  }
  return normalizeIterationResult(
    {
      success: true,
      summary: String(stdout || stderr || "codex iteration completed").slice(0, 2000),
      key_changes_made: [],
      key_learnings: []
    },
    "codex"
  );
}

function runTestFixture(worktreePath, runId, mode, iteration = 1) {
  const iterSuffix = iteration > 1 ? `-iter-${iteration}` : "";
  if (mode === "failure") {
    writeFileSync(join(worktreePath, `.beacon-loop-failure-${runId}${iterSuffix}.txt`), "failure fixture\n", "utf8");
    return normalizeIterationResult({ success: false, summary: "mock failure requested", key_changes_made: [], key_learnings: ["rollback exercised"] }, "codex");
  }
  if (mode === "commit-failure") {
    return normalizeIterationResult({ success: true, force_commit_failure: true, summary: "mock commit failure requested", key_changes_made: [], key_learnings: ["repair state exercised"] }, "codex");
  }
  if (mode === "fail-on-2" && iteration >= 2) {
    return normalizeIterationResult({ success: false, summary: `mock failure on iteration ${iteration}`, key_changes_made: [], key_learnings: [] }, "codex");
  }
  if (mode === "hard-error" && iteration === 1) {
    return normalizeIterationResult({ success: false, retryable_hard_error: true, summary: "mock retryable hard error", key_changes_made: [], key_learnings: [] }, "codex");
  }
  if (mode === "noop") {
    return normalizeIterationResult({ success: true, summary: "mock no-op iteration", key_changes_made: [], key_learnings: [] }, "codex");
  }
  if (mode === "stop-when" && iteration >= 2) {
    return normalizeIterationResult(
      {
        success: true,
        summary: "stop-when matched for tests",
        key_changes_made: [`.beacon-loop-success-${runId}${iterSuffix}.txt`],
        key_learnings: [],
        raw: { stop_signal: true }
      },
      "codex"
    );
  }
  writeFileSync(join(worktreePath, `.beacon-loop-success-${runId}${iterSuffix}.txt`), "success fixture\n", "utf8");
  return normalizeIterationResult(
    {
      success: true,
      summary: `mock success iteration ${iteration}`,
      key_changes_made: [`.beacon-loop-success-${runId}${iterSuffix}.txt`],
      key_learnings: []
    },
    "codex"
  );
}

export function runCodexAdapter(worktreePath, runId, options = {}) {
  const fixtureMode = process.env.BEACON_LOOP_TEST_AGENT_RESULT || "";
  const iteration = Number(options.iteration || 1);
  if (fixtureMode) return runTestFixture(worktreePath, runId, fixtureMode, iteration);

  const prompt = String(options.prompt || "Run the Beacon implementation iteration and emit structured JSON.");
  const command = process.env.BEACON_LOOP_CODEX_BIN || "codex";
  const configuredArgs = process.env.BEACON_LOOP_CODEX_ARGS
    ? process.env.BEACON_LOOP_CODEX_ARGS.split(/\s+/).filter(Boolean)
    : ["exec", "--skip-git-repo-check", prompt];
  const args = configuredArgs.includes("{prompt}")
    ? configuredArgs.map((item) => (item === "{prompt}" ? prompt : item))
    : configuredArgs;
  const result = spawnSync(command, args, {
    cwd: worktreePath,
    env: { ...process.env },
    encoding: "utf8"
  });
  if ((result.status ?? 1) !== 0) {
    return normalizeIterationResult(
      {
        success: false,
        summary: "codex adapter failed",
        key_changes_made: [],
        key_learnings: ["agent backend exited non-zero"],
        adapter_error: {
          command: [command, ...args].join(" "),
          exit_code: result.status ?? 1,
          stderr: String(result.stderr || "").slice(0, 2000)
        }
      },
      "codex"
    );
  }
  return parseStructuredResult(result.stdout, result.stderr);
}
