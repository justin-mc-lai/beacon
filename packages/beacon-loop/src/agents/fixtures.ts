import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { normalizeIterationResult } from "./schema.js";

export function runTestFixture(worktreePath, runId, mode, iteration = 1) {
  const iterSuffix = iteration > 1 ? `-iter-${iteration}` : "";
  if (mode === "failure") {
    writeFileSync(join(worktreePath, `.beacon-loop-failure-${runId}${iterSuffix}.txt`), "failure fixture\n", "utf8");
    return normalizeIterationResult({ success: false, summary: "mock failure requested", key_changes_made: [], key_learnings: ["rollback exercised"] }, "implement-harness");
  }
  if (mode === "commit-failure") {
    return normalizeIterationResult({ success: true, force_commit_failure: true, summary: "mock commit failure requested", key_changes_made: [], key_learnings: ["repair state exercised"] }, "implement-harness");
  }
  if (mode === "fail-on-2" && iteration >= 2) {
    return normalizeIterationResult({ success: false, summary: `mock failure on iteration ${iteration}`, key_changes_made: [], key_learnings: [] }, "implement-harness");
  }
  if (mode === "hard-error" && iteration === 1) {
    return normalizeIterationResult({ success: false, retryable_hard_error: true, summary: "mock retryable hard error", key_changes_made: [], key_learnings: [] }, "implement-harness");
  }
  if (mode === "noop") {
    return normalizeIterationResult({ success: true, summary: "mock no-op iteration", key_changes_made: [], key_learnings: [] }, "implement-harness");
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
      "implement-harness"
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
    "implement-harness"
  );
}
