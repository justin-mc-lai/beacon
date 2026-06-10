import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { normalizeIterationResult } from "./schema.js";

function runTestFixture(worktreePath, runId, target, mode, iteration = 1) {
  const iterSuffix = iteration > 1 ? `-iter-${iteration}` : "";
  if (mode === "failure") {
    return normalizeIterationResult({ success: false, summary: `mock acp:${target} failure`, key_changes_made: [], key_learnings: [] }, `acp:${target}`);
  }
  const file = `.beacon-loop-acp-${target}-${runId}${iterSuffix}.txt`;
  writeFileSync(join(worktreePath, file), "acp fixture\n", "utf8");
  return normalizeIterationResult(
    {
      success: true,
      summary: `mock acp:${target} success iteration ${iteration}`,
      key_changes_made: [file],
      key_learnings: [`acp target ${target} contract ok`]
    },
    `acp:${target}`
  );
}

export function runAcpAdapter(worktreePath, runId, options = {}) {
  const target = String(options.target || "default");
  const adapter = `acp:${target}`;
  const fixtureMode = process.env.BEACON_LOOP_TEST_ACP_RESULT || "";
  const iteration = Number(options.iteration || 1);
  if (fixtureMode) return runTestFixture(worktreePath, runId, target, fixtureMode, iteration);

  const prompt = String(options.prompt || "Run the Beacon implementation iteration and emit structured JSON.");
  const command = process.env.BEACON_LOOP_ACP_BIN || "npx";
  const args = process.env.BEACON_LOOP_ACP_ARGS
    ? process.env.BEACON_LOOP_ACP_ARGS.split(/\s+/).filter(Boolean).map((item) => (item === "{target}" ? target : item === "{prompt}" ? prompt : item))
    : ["acp", "run", target, "--prompt", prompt, "--json"];
  const result = spawnSync(command, args, { cwd: worktreePath, env: { ...process.env }, encoding: "utf8" });
  if ((result.status ?? 1) !== 0) {
    return normalizeIterationResult(
      {
        success: false,
        summary: `${adapter} adapter failed`,
        key_changes_made: [],
        key_learnings: ["acp backend unavailable; use BEACON_LOOP_TEST_ACP_RESULT in CI"],
        adapter_error: { exit_code: result.status ?? 1, stderr: String(result.stderr || "").slice(0, 2000) }
      },
      adapter
    );
  }
  try {
    const payload = JSON.parse(String(result.stdout || "").trim() || "{}");
    return normalizeIterationResult(payload, adapter);
  } catch {
    return normalizeIterationResult(
      { success: true, summary: String(result.stdout || "").slice(0, 2000), key_changes_made: [], key_learnings: [] },
      adapter
    );
  }
}
