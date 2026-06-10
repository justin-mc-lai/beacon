import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

function parseStructuredResult(stdout, stderr) {
  const lines = String(stdout || "").split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  for (const line of lines.toReversed()) {
    try {
      const payload = JSON.parse(line);
      if (payload && typeof payload === "object") {
        return {
          success: payload.success !== false,
          summary: String(payload.summary || payload.message || "codex iteration completed"),
          key_changes_made: Array.isArray(payload.key_changes_made) ? payload.key_changes_made : [],
          key_learnings: Array.isArray(payload.key_learnings) ? payload.key_learnings : [],
          raw: payload
        };
      }
    } catch {
      // Continue scanning for a structured line.
    }
  }
  return {
    success: true,
    summary: String(stdout || stderr || "codex iteration completed").slice(0, 2000),
    key_changes_made: [],
    key_learnings: []
  };
}

function runTestFixture(worktreePath, runId, mode) {
  if (mode === "failure") {
    writeFileSync(join(worktreePath, `.beacon-loop-failure-${runId}.txt`), "failure fixture\n", "utf8");
    return { success: false, summary: "mock failure requested", key_changes_made: [], key_learnings: ["rollback exercised"] };
  }
  if (mode === "commit-failure") {
    return { success: true, force_commit_failure: true, summary: "mock commit failure requested", key_changes_made: [], key_learnings: ["repair state exercised"] };
  }
  writeFileSync(join(worktreePath, `.beacon-loop-success-${runId}.txt`), "success fixture\n", "utf8");
  return { success: true, summary: "mock success iteration", key_changes_made: [`.beacon-loop-success-${runId}.txt`], key_learnings: [] };
}

export function runCodexAdapter(worktreePath, runId, options = {}) {
  const fixtureMode = process.env.BEACON_LOOP_TEST_AGENT_RESULT || "";
  if (fixtureMode) return runTestFixture(worktreePath, runId, fixtureMode);

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
    return {
      success: false,
      summary: "codex adapter failed",
      key_changes_made: [],
      key_learnings: ["agent backend exited non-zero"],
      adapter_error: {
        command: [command, ...args].join(" "),
        exit_code: result.status ?? 1,
        stderr: String(result.stderr || "").slice(0, 2000)
      }
    };
  }
  return parseStructuredResult(result.stdout, result.stderr);
}
