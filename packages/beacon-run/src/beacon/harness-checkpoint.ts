import { spawnSync } from "node:child_process";
import { join } from "node:path";
import type { BeaconPhase } from "./phase-prompt.js";
import type { FeatureScopeMode } from "./scope-mode.js";
import { readJson, writeJson } from "./fs.js";

export type TruthPromotionEntry = {
  phase?: BeaconPhase;
  checkpoint?: "entry" | "exit" | "phase";
  command: string;
  exit_code: number;
  stdout?: string;
  stderr?: string;
  at?: string;
  mode?: string;
};

export type TruthPromotionFile = {
  schema_version: string;
  calls: TruthPromotionEntry[];
  updated_at?: string;
};

export function truthPromotionPath(runDir: string): string {
  return join(runDir, "truth-promotion.json");
}

export function readTruthPromotion(runDir: string): TruthPromotionFile {
  return readJson(truthPromotionPath(runDir), {
    schema_version: "1.0",
    calls: [],
  });
}

export function appendTruthPromotion(
  runDir: string,
  entry: TruthPromotionEntry,
): TruthPromotionFile {
  const current = readTruthPromotion(runDir);
  const calls = Array.isArray(current.calls) ? current.calls : [];
  calls.push({ ...entry, at: new Date().toISOString() });
  const next: TruthPromotionFile = {
    ...current,
    schema_version: "1.0",
    calls,
    updated_at: new Date().toISOString(),
  };
  writeJson(truthPromotionPath(runDir), next);
  return next;
}

export type HarnessRunResult = {
  command: string;
  exit_code: number;
  stdout: string;
  stderr: string;
};

export function runBeaconCommand(
  projectRoot: string,
  args: string[],
): HarnessRunResult {
  if (process.env.BEACON_RUN_MOCK_HARNESS === "1") {
    return {
      command: `beacon ${args.join(" ")}`,
      exit_code: 0,
      stdout: '{"status":"mock"}',
      stderr: "",
    };
  }

  const result = spawnSync("beacon", args, {
    cwd: projectRoot,
    encoding: "utf-8",
    env: process.env,
  });
  return {
    command: `beacon ${args.join(" ")}`,
    exit_code: result.status ?? 1,
    stdout: String(result.stdout || ""),
    stderr: String(result.stderr || ""),
  };
}

export function recordHarnessRun(
  runDir: string,
  phase: BeaconPhase,
  checkpoint: TruthPromotionEntry["checkpoint"],
  result: HarnessRunResult,
): HarnessRunResult {
  appendTruthPromotion(runDir, {
    phase,
    checkpoint,
    command: result.command,
    exit_code: result.exit_code,
    stdout: result.stdout.slice(0, 500),
    stderr: result.stderr.slice(0, 500),
  });
  return result;
}

export function beaconJsonSucceeded(result: HarnessRunResult): boolean {
  if (result.exit_code !== 0) return false;
  try {
    const payload = JSON.parse(result.stdout) as {
      blocked?: boolean;
      status?: string;
      result?: { gate?: { blocked?: boolean; status?: string } };
    };
    if (payload.blocked === true || payload.status === "blocked") {
      return false;
    }
    const gate = payload.result?.gate;
    if (gate && (gate.blocked === true || gate.status === "blocked")) {
      return false;
    }
    return true;
  } catch {
    return true;
  }
}

export type HarnessContext = {
  projectRoot: string;
  version: string;
  feature: string;
  implementRunner?: string;
  scopeMode?: FeatureScopeMode;
};

export function buildPhaseHarnessArgs(
  phase: BeaconPhase,
  checkpoint: "entry" | "exit" | "phase",
  ctx: HarnessContext,
): string[] | null {
  const { projectRoot, version, feature } = ctx;
  const runner = ctx.implementRunner || "codex-subagents";

  if (phase === "truth") {
    if (checkpoint === "entry") {
      return [
        "truth-map",
        "resolve",
        feature,
        "--project",
        projectRoot,
        "--version",
        version,
        "--json",
      ];
    }
    if (checkpoint === "exit") {
      if (ctx.scopeMode === "smoke") {
        return [
          "truth-map",
          "resolve",
          feature,
          "--project",
          projectRoot,
          "--version",
          version,
          "--json",
        ];
      }
      return [
        "doctor",
        "sync-materials",
        "--project-root",
        projectRoot,
        "--version",
        version,
        "--feature",
        feature,
        "--single-feature",
        "--json",
      ];
    }
    return null;
  }

  if (phase === "generate") {
    if (checkpoint === "entry") {
      return [
        "doctor",
        "verify-context",
        "--project-root",
        projectRoot,
        "--strict",
      ];
    }
    if (checkpoint === "exit") {
      return [
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
      ];
    }
    return null;
  }

  if (phase === "qa" && checkpoint === "phase") {
    return [
      "qa",
      "run",
      feature,
      "--project",
      projectRoot,
      "--version",
      version,
      "--json",
    ];
  }

  if (phase === "release" && checkpoint === "phase") {
    return [
      "release",
      "check",
      "--project",
      projectRoot,
      "--version",
      version,
      "--json",
    ];
  }

  return null;
}

export function runPhaseHarness(
  runDir: string,
  phase: BeaconPhase,
  checkpoint: "entry" | "exit" | "phase",
  ctx: HarnessContext,
): HarnessRunResult | null {
  const args = buildPhaseHarnessArgs(phase, checkpoint, ctx);
  if (!args) return null;
  const result = runBeaconCommand(ctx.projectRoot, args);
  recordHarnessRun(runDir, phase, checkpoint, result);
  return result;
}
