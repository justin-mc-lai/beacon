import { spawnSync } from "node:child_process";
import { existsSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  applyE2eProgramFixture,
  blockDeliveryWithoutP4,
  createInitialProgramRunState,
  readProgramRunState,
  slugifyProgram,
  writeProgramRunState,
  type ProgramRunState,
} from "./program-outer-fsm.js";

export type ProgramModeInput = {
  projectRoot: string;
  version: string;
  utterance: string;
  programSlug?: string;
  planMode?: string;
  lakeOrOcean?: "湖" | "海";
  runDir: string;
  deliveryMode: "delivery" | "program";
};

export type ProgramModeResult =
  | { ok: true; state: ProgramRunState; state_path: string }
  | {
      ok: false;
      blocked: true;
      reason_code: string;
      message: string;
      recovery_route?: string;
      state?: ProgramRunState;
    };

function runBeaconPlanStart(
  projectRoot: string,
  version: string,
  utterance: string,
  programSlug: string,
): Record<string, unknown> | null {
  const result = spawnSync(
    "beacon",
    [
      "plan",
      "start",
      utterance,
      "--project-root",
      projectRoot,
      "--version",
      version,
      "--program",
      programSlug,
      "--json",
    ],
    { cwd: projectRoot, encoding: "utf8" },
  );
  if (result.status !== 0 || !result.stdout?.trim()) return null;
  try {
    return JSON.parse(result.stdout) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export function prepareProgramRun(input: ProgramModeInput): ProgramModeResult {
  if (input.deliveryMode !== "program") {
    return {
      ok: false,
      blocked: true,
      reason_code: "not_program_mode",
      message: "prepareProgramRun called without program delivery mode",
    };
  }

  const slug =
    input.programSlug?.trim() || slugifyProgram(input.utterance, "");
  const existing = readProgramRunState(input.projectRoot, input.version, slug);

  let state = createInitialProgramRunState({
    projectRoot: input.projectRoot,
    version: input.version,
    programSlug: slug,
    planMode: input.planMode,
    lakeOrOcean: input.lakeOrOcean || "海",
    runDir: input.runDir,
    resumeFrom: existing,
  });

  if (!existing) {
    const planPayload = runBeaconPlanStart(
      input.projectRoot,
      input.version,
      input.utterance,
      slug,
    );
    if (planPayload?.plan_mode) {
      state.plan_mode = String(planPayload.plan_mode);
    }
    if (planPayload?.state && typeof planPayload.state === "string") {
      state.fsm_state = planPayload.state as ProgramRunState["fsm_state"];
    }
  }

  if (process.env.BEACON_RUN_E2E_PROGRAM === "1") {
    state = applyE2eProgramFixture(state);
  }

  const statePath = writeProgramRunState(input.projectRoot, {
    ...state,
    run_dir: input.runDir,
  });

  const runDirState = join(input.runDir, "program-run-state.json");
  writeFileSync(runDirState, `${JSON.stringify(state, null, 2)}\n`, "utf8");

  return { ok: true, state, state_path: statePath };
}

export function assertProgramDeliveryAllowed(
  projectRoot: string,
  state: ProgramRunState,
): ProgramModeResult | { ok: true } {
  const gate = blockDeliveryWithoutP4(projectRoot, state);
  if (gate.blocked && state.lake_or_ocean === "海") {
    return {
      ok: false,
      blocked: true,
      reason_code: gate.reason_code,
      message: gate.recovery_route,
      recovery_route: gate.recovery_route,
      state,
    };
  }
  return { ok: true };
}

export function copyProgramStateToRunDir(
  projectRoot: string,
  runDir: string,
  version: string,
  programSlug: string,
): ProgramRunState | null {
  const state = readProgramRunState(projectRoot, version, programSlug);
  if (!state) return null;
  const path = join(runDir, "program-run-state.json");
  if (!existsSync(path)) {
    writeFileSync(path, `${JSON.stringify(state, null, 2)}\n`, "utf8");
  }
  return state;
}
