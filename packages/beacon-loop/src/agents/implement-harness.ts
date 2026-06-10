import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { buildImplementWorkerCommand, defaultImplementRunner } from "../harness/worker-route.js";
import { runTestFixture } from "./fixtures.js";
import { assertIterationContract, normalizeIterationResult } from "./schema.js";

function parseStrictIterationPayload(text, adapter = "implement-harness") {
  const lines = String(text || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  for (const line of lines.toReversed()) {
    try {
      const payload = JSON.parse(line);
      if (payload?.iteration_result && typeof payload.iteration_result === "object") {
        const nested = payload.iteration_result;
        if (!assertIterationContract(normalizeIterationResult(nested, adapter))) {
          continue;
        }
        return normalizeIterationResult(nested, adapter);
      }
      if (payload && typeof payload === "object" && "success" in payload) {
        const normalized = normalizeIterationResult(payload, adapter);
        if (assertIterationContract(normalized)) return normalized;
      }
    } catch {
      // scan for structured line
    }
  }
  return null;
}

function mapImplementPayload(payload, adapter = "implement-harness") {
  if (payload?.iteration_result && typeof payload.iteration_result === "object") {
    return normalizeIterationResult(payload.iteration_result, adapter);
  }
  const changed = Array.isArray(payload?.changed_files) ? payload.changed_files : [];
  const status = String(payload?.status || "").toLowerCase();
  const success = status === "completed" || status === "implementation_candidate" || payload?.success === true;
  return normalizeIterationResult(
    {
      success,
      summary: String(payload?.summary || payload?.message || "implement harness worker completed"),
      key_changes_made: changed,
      key_learnings: Array.isArray(payload?.key_learnings) ? payload.key_learnings : [],
      raw: payload
    },
    adapter
  );
}

export function runImplementHarnessAdapter(worktreePath, runId, options = {}) {
  const fixtureMode = process.env.BEACON_LOOP_TEST_AGENT_RESULT || "";
  const iteration = Number(options.iteration || 1);
  const useFixtureOnly = Boolean(fixtureMode) && process.env.BEACON_LOOP_IMPLEMENT_WORKER !== "1";

  if (useFixtureOnly) {
    return runTestFixture(worktreePath, runId, fixtureMode, iteration);
  }

  const projectRoot = String(options.projectRoot || worktreePath);
  const feature = String(options.feature || "").trim();
  const version = String(options.version || "auto");
  const runner = String(options.runner || defaultImplementRunner());
  const runDir = String(options.runDir || "");
  const schemaPath = runDir ? join(runDir, "output-schema.json") : join(worktreePath, "output-schema.json");
  const prompt = String(options.prompt || "Run the Beacon implementation iteration and emit structured JSON.");
  const workerCommand = buildImplementWorkerCommand(projectRoot, feature, version, runner);

  const command = process.env.BEACON_LOOP_BEACON_BIN || "beacon";
  const args = [
    "implement",
    "run",
    feature,
    "--project",
    projectRoot,
    "--version",
    version,
    "--runner",
    runner,
    "--mode",
    "single",
    "--json",
    "--no-auto-qa",
    "--host-prompt",
    prompt
  ];
  if (existsSync(schemaPath)) {
    args.push("--output-schema", schemaPath);
  }

  const result = spawnSync(command, args, {
    cwd: worktreePath,
    env: { ...process.env },
    encoding: "utf8"
  });

  const stdout = String(result.stdout || "");
  const stderr = String(result.stderr || "");
  let payload = null;
  if (stdout.trim()) {
    try {
      payload = JSON.parse(stdout);
    } catch {
      payload = parseStrictIterationPayload(stdout);
    }
  }

  if ((result.status ?? 1) !== 0 && !payload) {
    return normalizeIterationResult(
      {
        success: false,
        summary: "implement harness worker failed",
        key_changes_made: [],
        key_learnings: ["beacon implement run exited non-zero"],
        adapter_error: {
          command: workerCommand,
          exit_code: result.status ?? 1,
          stderr: stderr.slice(0, 2000)
        }
      },
      "implement-harness"
    );
  }

  const strict = payload ? mapImplementPayload(payload) : parseStrictIterationPayload(stdout);
  if (!strict || !assertIterationContract(strict)) {
    return normalizeIterationResult(
      {
        success: false,
        summary: "implement harness worker returned invalid iteration JSON",
        key_changes_made: [],
        key_learnings: ["strict schema parse failed"],
        adapter_error: {
          command: workerCommand,
          schema_path: existsSync(schemaPath) ? schemaPath : "",
          stderr: stderr.slice(0, 2000)
        }
      },
      "implement-harness"
    );
  }

  strict.worker_command = workerCommand;
  strict.harness = "gen-implement";
  strict.implement_runner = runner;
  return strict;
}
