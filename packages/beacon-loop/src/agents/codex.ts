import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { runTestFixture } from "./fixtures.js";
import { normalizeIterationResult } from "./schema.js";

export function runCodexAdapter(worktreePath, runId, options = {}) {
  const fixtureMode = process.env.BEACON_LOOP_TEST_AGENT_RESULT || "";
  const iteration = Number(options.iteration || 1);
  if (fixtureMode) return runTestFixture(worktreePath, runId, fixtureMode, iteration);

  return normalizeIterationResult(
    {
      success: false,
      summary: "bare codex exec bypass blocked; use implement harness worker",
      key_changes_made: [],
      key_learnings: ["route implement_loop through beacon implement run"],
      adapter_error: {
        reason_code: "codex_bypass_blocked",
        repair_route: "beacon implement run --runner codex-subagents"
      }
    },
    "codex"
  );
}
