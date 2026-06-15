import { spawnSync } from "node:child_process";
import { join } from "node:path";
import type { BeaconPhase } from "./phase-prompt.js";
import type { FeatureScopeMode } from "./scope-mode.js";
import { readJson, writeJson } from "./fs.js";
import {
  isFeatureTruthFrozen,
  parseHarnessJsonReason,
  readStoryLifecycleFrozen,
  readTruthFrontmatterStatus,
} from "./truth-frozen.js";

export type HarnessCheckpoint =
  | "entry"
  | "exit"
  | "phase"
  | "freeze_gate";

export type TruthPromotionEntry = {
  phase?: BeaconPhase;
  checkpoint?: HarnessCheckpoint;
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

function featureFromHarnessArgs(args: string[]): string {
  if (args[0] === "truth-map" && args[1] === "resolve") return args[2] || "";
  if (args[0] === "freeze") return args[1] || "";
  if (args[0] === "implement" && args[1] === "run") return args[2] || "";
  if (args[0] === "doctor" && args[1] === "sync-requirement-clarity") {
    return args[2] || "";
  }
  if (args[0] === "truth-cutover" && args[1] === "run") return args[2] || "";
  return "";
}

function versionFromHarnessArgs(args: string[]): string {
  const idx = args.indexOf("--version");
  return idx >= 0 ? args[idx + 1] || "v1.6.0" : "v1.6.0";
}

function mockHarnessResult(
  projectRoot: string,
  args: string[],
): HarnessRunResult {
  const command = `beacon ${args.join(" ")}`;
  const feature = featureFromHarnessArgs(args);
  const version = versionFromHarnessArgs(args);
  const status =
    feature && projectRoot
      ? readTruthFrontmatterStatus(projectRoot, version, feature)
      : "frozen";
  const frozen =
    status === "frozen" ||
    (feature && projectRoot
      ? readStoryLifecycleFrozen(projectRoot, version, feature)
      : false);

  if (args[0] === "truth-map" && args[1] === "resolve") {
    return {
      command,
      exit_code: 0,
      stdout: JSON.stringify({
        status: "resolved",
        feature_truth: { frontmatter: { status } },
      }),
      stderr: "",
    };
  }
  if (args[0] === "freeze") {
    if (frozen) {
      return {
        command,
        exit_code: 0,
        stdout: JSON.stringify({ status: "frozen" }),
        stderr: "",
      };
    }
    return {
      command,
      exit_code: 2,
      stdout: JSON.stringify({
        status: "blocked",
        blocked: true,
        reason_code: "revision_not_frozen",
      }),
      stderr: "",
    };
  }
  if (args[0] === "truth-cutover" && args[1] === "run") {
    return {
      command,
      exit_code: frozen ? 0 : 2,
      stdout: JSON.stringify(
        frozen
          ? { status: "pass" }
          : {
              status: "blocked",
              blocked: true,
              reason_code: "legacy_cutover_required",
            },
      ),
      stderr: "",
    };
  }
  if (args[0] === "qa" && args[1] === "run") {
    if (process.env.BEACON_RUN_MOCK_QA_INFRA_BLOCKED === "1") {
      return {
        command,
        exit_code: 2,
        stdout: JSON.stringify({
          status: "failed",
          scorecard: {
            continue_decision: "stop_for_repair",
            stop_reasons: [
              "junit_missing_or_invalid",
              "assertion_count_zero_pass",
            ],
          },
        }),
        stderr: "",
      };
    }
    if (process.env.BEACON_RUN_MOCK_QA_BLOCKED === "1") {
      return {
        command,
        exit_code: 2,
        stdout: JSON.stringify({
          status: "blocked",
          blocked: true,
          reason_codes: ["evidence_binding_missing"],
        }),
        stderr: "",
      };
    }
    return {
      command,
      exit_code: 0,
      stdout: JSON.stringify({ status: "pass" }),
      stderr: "",
    };
  }
  if (args[0] === "release" && args[1] === "check") {
    if (process.env.BEACON_RUN_MOCK_RELEASE_BLOCKED === "1") {
      return {
        command,
        exit_code: 2,
        stdout: JSON.stringify({
          status: "blocked",
          blocked: true,
          reason_codes: ["release_gate_failed"],
        }),
        stderr: "",
      };
    }
    return {
      command,
      exit_code: 0,
      stdout: JSON.stringify({ status: "pass" }),
      stderr: "",
    };
  }
  if (args[0] === "implement" && args[1] === "run") {
    if (process.env.BEACON_RUN_MOCK_IMPLEMENT_PREFLIGHT === "revision_not_frozen") {
      return {
        command,
        exit_code: 2,
        stdout: JSON.stringify({
          status: "blocked",
          blocked: true,
          reason_code: "revision_not_frozen",
        }),
        stderr: "",
      };
    }
    if (frozen) {
      return {
        command,
        exit_code: 0,
        stdout: JSON.stringify({ status: "pass" }),
        stderr: "",
      };
    }
    return {
      command,
      exit_code: 2,
      stdout: JSON.stringify({
        status: "blocked",
        blocked: true,
        reason_code: "revision_not_frozen",
      }),
      stderr: "",
    };
  }
  return {
    command,
    exit_code: 0,
    stdout: '{"status":"mock"}',
    stderr: "",
  };
}

export function runBeaconCommand(
  projectRoot: string,
  args: string[],
): HarnessRunResult {
  if (process.env.BEACON_RUN_MOCK_HARNESS === "1") {
    return mockHarnessResult(projectRoot, args);
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
  checkpoint: HarnessCheckpoint,
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

export function implementPreflightBlocked(result: HarnessRunResult): string {
  if (beaconJsonSucceeded(result)) return "";
  const reason = parseHarnessJsonReason(result);
  if (
    reason === "revision_not_frozen" ||
    reason === "legacy_cutover_required"
  ) {
    return reason;
  }
  if (result.stderr.includes("revision_not_frozen")) {
    return "revision_not_frozen";
  }
  if (result.stderr.includes("legacy_cutover_required")) {
    return "legacy_cutover_required";
  }
  return "";
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
      version,
      "--project",
      projectRoot,
      "--json",
    ];
  }

  return null;
}

export function buildTruthFreezeGateArgs(ctx: HarnessContext): string[][] {
  const { projectRoot, version, feature } = ctx;
  return [
    [
      "doctor",
      "sync-requirement-clarity",
      feature,
      "--project-root",
      projectRoot,
      "--version",
      version,
      "--json",
    ],
    ["freeze", feature, "--project", projectRoot, "--version", version, "--json"],
  ];
}

export function runRecordedBeaconCommand(
  runDir: string,
  phase: BeaconPhase,
  checkpoint: HarnessCheckpoint,
  ctx: HarnessContext,
  args: string[],
): HarnessRunResult {
  const result = runBeaconCommand(ctx.projectRoot, args);
  recordHarnessRun(runDir, phase, checkpoint, result);
  return result;
}

export type TruthExitHarnessResult = {
  ok: boolean;
  command: string;
  exit_code: number;
  reason_code?: string;
};

export function runTruthPhaseExitHarness(
  runDir: string,
  ctx: HarnessContext,
): TruthExitHarnessResult {
  const primary = runPhaseHarness(runDir, "truth", "exit", ctx);
  if (!primary || !beaconJsonSucceeded(primary)) {
    return {
      ok: false,
      command: primary?.command ?? "beacon truth exit",
      exit_code: primary?.exit_code ?? 1,
      reason_code: "harness_exit_failed",
    };
  }

  for (const args of buildTruthFreezeGateArgs(ctx)) {
    const step = runRecordedBeaconCommand(
      runDir,
      "truth",
      "freeze_gate",
      ctx,
      args,
    );
    if (!beaconJsonSucceeded(step)) {
      let reason = parseHarnessJsonReason(step) || "truth_not_frozen";
      if (reason === "legacy_cutover_required") {
        const cutover = runRecordedBeaconCommand(
          runDir,
          "truth",
          "freeze_gate",
          ctx,
          [
            "truth-cutover",
            "run",
            ctx.feature,
            "--project",
            ctx.projectRoot,
            "--version",
            ctx.version,
            "--apply",
            "--resume-intent",
            "implement",
            "--json",
          ],
        );
        if (beaconJsonSucceeded(cutover)) {
          const refreeze = runRecordedBeaconCommand(
            runDir,
            "truth",
            "freeze_gate",
            ctx,
            [
              "freeze",
              ctx.feature,
              "--project",
              ctx.projectRoot,
              "--version",
              ctx.version,
              "--json",
            ],
          );
          if (beaconJsonSucceeded(refreeze)) {
            return {
              ok: true,
              command: refreeze.command,
              exit_code: refreeze.exit_code,
            };
          }
          reason = parseHarnessJsonReason(refreeze) || "truth_not_frozen";
        }
      }
      return {
        ok: false,
        command: step.command,
        exit_code: step.exit_code,
        reason_code: reason === "revision_not_frozen" ? "truth_not_frozen" : reason,
      };
    }
  }

  const resolved = runRecordedBeaconCommand(
    runDir,
    "truth",
    "freeze_gate",
    ctx,
    [
      "truth-map",
      "resolve",
      ctx.feature,
      "--project",
      ctx.projectRoot,
      "--version",
      ctx.version,
      "--json",
    ],
  );
  const frozen = isFeatureTruthFrozen(
    ctx.projectRoot,
    ctx.version,
    ctx.feature,
  );
  if (!frozen) {
    return {
      ok: false,
      command: resolved.command,
      exit_code: resolved.exit_code,
      reason_code: "truth_not_frozen",
    };
  }

  return {
    ok: true,
    command: resolved.command,
    exit_code: resolved.exit_code,
  };
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
