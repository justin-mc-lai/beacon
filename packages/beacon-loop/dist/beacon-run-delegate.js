import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { inferFeatureSlugFromUtterance } from "./intent/feature-slug.js";

function moduleDir() {
  return dirname(fileURLToPath(import.meta.url));
}

export function resolveBeaconRunCli() {
  const envCli = process.env.BEACON_RUN_CLI?.trim();
  if (envCli && existsSync(envCli)) {
    return envCli;
  }

  const sibling = join(moduleDir(), "..", "..", "beacon-run", "dist", "cli.mjs");
  if (existsSync(sibling)) {
    return sibling;
  }

  const which = spawnSync("which", ["beacon-run"], { encoding: "utf8" });
  if (which.status === 0) {
    const path = which.stdout.trim();
    if (path) return path;
  }

  return null;
}

function mapAgent(agent) {
  const value = String(agent || "codex").trim();
  if (value === "implement-harness") return "codex";
  return value;
}

function buildBeaconRunArgs(projectRoot, goal, options) {
  const feature =
    String(options.feature || "").trim() ||
    inferFeatureSlugFromUtterance(goal) ||
    "";
  if (!feature) {
    throw new Error("feature_slug_required");
  }

  const args = [
    goal,
    "--beacon",
    "--project-root",
    projectRoot,
    "--beacon-version",
    options.version,
    "--feature",
    feature,
    "--agent",
    mapAgent(options.agent),
    "--max-iterations",
    String(options.maxIterations || "8"),
  ];

  if (options.maxTokens && options.maxTokens !== "0") {
    args.push("--max-tokens", String(options.maxTokens));
  }
  if (options.stopWhen) {
    args.push("--stop-when", options.stopWhen);
  }
  if (options.implementRunner) {
    args.push("--implement-runner", options.implementRunner);
  }
  if (options.truthBootstrap === "fallback") {
    args.push("--truth-bootstrap", "fallback");
  }

  const branchMode = options.branchMode || "worktree";
  if (options.isolatedWorktree || branchMode === "worktree") {
    args.push("--worktree");
  } else if (branchMode === "current-branch" || branchMode === "run-branch") {
    args.push("--current-branch");
  }

  return { args, feature };
}

export function delegateGoalToBeaconRun(projectRoot, goal, options) {
  const cli = resolveBeaconRunCli();
  if (!cli) {
    return {
      status: "blocked",
      reason_code: "beacon_run_cli_missing",
    };
  }

  let built;
  try {
    built = buildBeaconRunArgs(projectRoot, goal, options);
  } catch (error) {
    return {
      status: "blocked",
      reason_code:
        error instanceof Error && error.message === "feature_slug_required"
          ? "feature_slug_required"
          : "delegate_args_invalid",
      stderr: error instanceof Error ? error.message : String(error),
      beacon_run_cli: cli,
    };
  }

  const command = `${process.execPath} ${cli} ${built.args.join(" ")}`;
  if (options.dryRun) {
    return {
      status: "dry_run",
      command,
      feature: built.feature,
      beacon_run_cli: cli,
    };
  }

  const result = spawnSync(process.execPath, [cli, ...built.args], {
    cwd: projectRoot,
    encoding: "utf8",
    env: process.env,
  });

  return {
    status: "delegated",
    command,
    feature: built.feature,
    beacon_run_cli: cli,
    exit_code: result.status ?? 1,
    stdout: result.stdout,
    stderr: result.stderr,
  };
}

export function formatDelegatePayload(goal, delegate) {
  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "goal",
    delegation: "beacon-run",
    deprecated_legacy: "use beacon-run directly; pass --legacy-delivery to keep R3 FSM",
    goal,
    ...delegate,
  };
}
