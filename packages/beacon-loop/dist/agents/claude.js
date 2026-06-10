import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { normalizeIterationResult } from "./schema.js";

function runTestFixture(worktreePath, runId, mode, iteration = 1) {
  const iterSuffix = iteration > 1 ? `-iter-${iteration}` : "";
  if (mode === "failure") {
    return normalizeIterationResult({ success: false, summary: "mock claude failure", key_changes_made: [], key_learnings: [] }, "claude");
  }
  writeFileSync(join(worktreePath, `.beacon-loop-claude-${runId}${iterSuffix}.txt`), "claude fixture\n", "utf8");
  return normalizeIterationResult(
    {
      success: true,
      summary: `mock claude success iteration ${iteration}`,
      key_changes_made: [`.beacon-loop-claude-${runId}${iterSuffix}.txt`],
      key_learnings: ["claude adapter contract ok"]
    },
    "claude"
  );
}

export function runClaudeAdapter(worktreePath, runId, options = {}) {
  const fixtureMode = process.env.BEACON_LOOP_TEST_CLAUDE_RESULT || "";
  const iteration = Number(options.iteration || 1);
  if (fixtureMode) return runTestFixture(worktreePath, runId, fixtureMode, iteration);

  const prompt = String(options.prompt || "Run the Beacon implementation iteration and emit structured JSON.");
  const command = process.env.BEACON_LOOP_CLAUDE_BIN || "claude";
  const args = process.env.BEACON_LOOP_CLAUDE_ARGS
    ? process.env.BEACON_LOOP_CLAUDE_ARGS.split(/\s+/).filter(Boolean)
    : ["-p", prompt, "--output-format", "json"];
  const result = spawnSync(command, args, { cwd: worktreePath, env: { ...process.env }, encoding: "utf8" });
  if ((result.status ?? 1) !== 0) {
    return normalizeIterationResult(
      {
        success: false,
        summary: "claude adapter failed",
        key_changes_made: [],
        key_learnings: ["agent backend exited non-zero"]
      },
      "claude"
    );
  }
  try {
    const payload = JSON.parse(String(result.stdout || "").trim() || "{}");
    return normalizeIterationResult(payload, "claude");
  } catch {
    return normalizeIterationResult({ success: true, summary: String(result.stdout || "").slice(0, 2000), key_changes_made: [], key_learnings: [] }, "claude");
  }
}
