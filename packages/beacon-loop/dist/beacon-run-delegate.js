import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolveDelegateFeature } from "./intent/feature-resolve.js";
import {
  buildScopeIntentContract,
  classifyLakeOrOcean,
  resolveDeliveryMode,
} from "./intent/scope-classify.js";

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

function currentGitBranch(projectRoot) {
  const result = spawnSync("git", ["rev-parse", "--abbrev-ref", "HEAD"], {
    cwd: projectRoot,
    encoding: "utf8",
  });
  return result.status === 0 ? result.stdout.trim() : "";
}

function isGnhfBranch(branch) {
  return branch.startsWith("gnhf/");
}

function resolveBranchMode(projectRoot, options) {
  const requested = options.branchMode || "worktree";
  if (options.isolatedWorktree) {
    return { branchMode: "worktree", branchModeResolved: "worktree" };
  }
  if (requested !== "worktree") {
    return { branchMode: requested, branchModeResolved: requested };
  }
  const branch = currentGitBranch(projectRoot);
  if (isGnhfBranch(branch)) {
    return {
      branchMode: "current-branch",
      branchModeResolved: "current-branch (auto: gnhf branch)",
    };
  }
  return { branchMode: "worktree", branchModeResolved: "worktree" };
}

function buildBeaconRunArgs(projectRoot, goal, options) {
  const feature = resolveDelegateFeature(
    projectRoot,
    options.version,
    goal,
    String(options.feature || "").trim(),
  );
  if (!feature) {
    throw new Error("feature_slug_required");
  }

  const scope = classifyLakeOrOcean(goal, {
    lakeOrOcean: options.lakeOrOcean,
    mcqAnswer: options.mcqAnswer,
  });
  const deliveryMode = resolveDeliveryMode(scope, options.mode);

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
    "--mode",
    deliveryMode,
  ];

  if (options.program) {
    args.push("--program", String(options.program));
  }
  if (scope.lake_or_ocean) {
    args.push("--lake-or-ocean", scope.lake_or_ocean);
  }
  if (options.evalMatrix) {
    args.push("--eval-matrix");
  }
  if (options.evalScorecard) {
    args.push("--eval-scorecard");
  }

  if (options.maxTokens && options.maxTokens !== "0") {
    args.push("--max-tokens", String(options.maxTokens));
  }
  if (options.stopWhen) {
    args.push("--stop-when", options.stopWhen);
  }
  if (options.stopCheckCmd) {
    args.push("--stop-check-cmd", options.stopCheckCmd);
  }
  if (options.implementRunner) {
    args.push("--implement-runner", options.implementRunner);
  }
  if (options.truthBootstrap === "fallback") {
    args.push("--truth-bootstrap", "fallback");
  }

  const { branchMode, branchModeResolved } = resolveBranchMode(projectRoot, options);
  if (branchMode === "worktree") {
    args.push("--worktree");
  } else if (branchMode === "current-branch" || branchMode === "run-branch") {
    args.push("--current-branch");
  }

  return {
    args,
    feature,
    branchModeResolved,
    scope,
    deliveryMode,
    intentContract: buildScopeIntentContract(goal, scope, {
      mode: deliveryMode,
      program: options.program,
      version: options.version,
    }),
  };
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

  const scopeMcqRequired =
    built.scope?.ambiguous &&
    !options.lakeOrOcean &&
    !options.mcqAnswer &&
    !process.env.BEACON_LOOP_SCOPE_MCQ;

  // Dry-run is non-mutating inspection: show the provisional delegate command and
  // surface MCQ metadata without blocking (UD-007 still applies on real execution).
  if (scopeMcqRequired && !options.dryRun) {
    return {
      status: "blocked",
      reason_code: "scope_mcq_required",
      scope: built.scope,
      mcq: built.scope.mcq,
      beacon_run_cli: cli,
    };
  }

  const intentDir = join(projectRoot, ".beacon", "loop", "intent");
  mkdirSync(intentDir, { recursive: true });
  writeFileSync(
    join(intentDir, "intent-contract.json"),
    `${JSON.stringify(built.intentContract, null, 2)}\n`,
    "utf8",
  );

  const beaconRunCommand = `${process.execPath} ${cli} ${built.args.join(" ")}`;
  if (options.dryRun) {
    return {
      status: "dry_run",
      beacon_run_command: beaconRunCommand,
      feature: built.feature,
      beacon_run_cli: cli,
      branch_mode_resolved: built.branchModeResolved,
      delivery_mode: built.deliveryMode,
      lake_or_ocean: built.scope?.lake_or_ocean,
      scope: built.scope,
    };
  }

  // encoding forces piped stdio and breaks beacon-run's alt-screen TUI (needs a TTY).
  const interactive =
    process.stdout.isTTY === true && process.stdin.isTTY === true;
  const spawnOptions = {
    cwd: projectRoot,
    env: process.env,
    stdio: interactive ? "inherit" : "pipe",
  };
  if (!interactive) {
    spawnOptions.encoding = "utf8";
  }
  const result = spawnSync(process.execPath, [cli, ...built.args], spawnOptions);

  return {
    status: "delegated",
    beacon_run_command: beaconRunCommand,
    feature: built.feature,
    beacon_run_cli: cli,
    branch_mode_resolved: built.branchModeResolved,
    delivery_mode: built.deliveryMode,
    lake_or_ocean: built.scope?.lake_or_ocean,
    exit_code: result.status ?? 1,
    ...(interactive
      ? {}
      : {
          stdout: result.stdout,
          stderr: result.stderr,
        }),
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
