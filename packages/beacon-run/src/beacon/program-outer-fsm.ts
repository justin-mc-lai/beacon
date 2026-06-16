import {
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { join } from "node:path";

/** Program plan loop phases (P0–P6) per program-plan-contract.md */
export const PROGRAM_PHASES = [
  "P0",
  "P1",
  "P2",
  "P3",
  "P4",
  "P5",
  "P6",
] as const;

export type ProgramPhase = (typeof PROGRAM_PHASES)[number];

export const PROGRAM_PLAN_STATES = [
  "program_intent_captured",
  "plan_mode_selected",
  "program_inventory",
  "program_reviewed",
  "feature_graph_ack",
  "lakes_truth_in_progress",
  "lakes_frozen",
  "program_frozen",
  "program_delivery",
  "program_change_open",
  "program_change_review",
  "program_refreeze",
] as const;

export type ProgramPlanState = (typeof PROGRAM_PLAN_STATES)[number];

const VALID_TRANSITIONS: Record<ProgramPlanState, readonly ProgramPlanState[]> =
  {
    program_intent_captured: ["plan_mode_selected"],
    plan_mode_selected: ["program_inventory"],
    program_inventory: ["program_reviewed"],
    program_reviewed: ["feature_graph_ack"],
    feature_graph_ack: ["lakes_truth_in_progress"],
    lakes_truth_in_progress: ["lakes_frozen", "lakes_truth_in_progress"],
    lakes_frozen: ["program_frozen"],
    program_frozen: ["program_delivery", "program_change_open"],
    program_delivery: [],
    program_change_open: ["program_change_review"],
    program_change_review: ["program_refreeze"],
    program_refreeze: ["program_frozen"],
  };

const INVALID_TRANSITIONS = new Set<string>([
  "program_intent_captured|lakes_frozen",
  "program_intent_captured|program_inventory",
  "program_intent_captured|program_frozen",
  "program_change_open|program_delivery",
  "program_change_open|program_frozen",
  "feature_graph_ack|program_frozen",
]);

export const PHASE_TO_FSM: Record<ProgramPhase, ProgramPlanState> = {
  P0: "program_inventory",
  P1: "program_inventory",
  P2: "program_reviewed",
  P3: "feature_graph_ack",
  P4: "feature_graph_ack",
  P5: "lakes_truth_in_progress",
  P6: "program_frozen",
};

export type ProgramRunState = {
  schema_version: "1.0";
  program_slug: string;
  version: string;
  plan_mode: string;
  program_phase: ProgramPhase;
  fsm_state: ProgramPlanState;
  lake_or_ocean: "湖" | "海";
  p4_ack: boolean;
  next_action: string;
  run_dir?: string;
  updated_at: string;
};

export type TransitionResult = {
  ok: boolean;
  from_state: ProgramPlanState;
  to_state: ProgramPlanState;
  reason_code?: string;
  recovery_route?: string;
};

const RECOVERY_ROUTES: Record<string, string> = {
  "program_change_open|program_delivery": "beacon-pln-review",
  "program_change_open|program_frozen": "beacon-pln-review",
};

export function isValidTransition(
  fromState: ProgramPlanState,
  toState: ProgramPlanState,
): boolean {
  const key = `${fromState}|${toState}`;
  if (INVALID_TRANSITIONS.has(key)) return false;
  return VALID_TRANSITIONS[fromState]?.includes(toState) ?? false;
}

export function transition(
  fromState: ProgramPlanState,
  toState: ProgramPlanState,
): TransitionResult {
  if (
    !PROGRAM_PLAN_STATES.includes(fromState) ||
    !PROGRAM_PLAN_STATES.includes(toState)
  ) {
    return {
      ok: false,
      from_state: fromState,
      to_state: toState,
      reason_code: "unknown_state",
    };
  }
  const key = `${fromState}|${toState}`;
  if (INVALID_TRANSITIONS.has(key)) {
    return {
      ok: false,
      from_state: fromState,
      to_state: toState,
      reason_code: "invalid_transition",
      recovery_route: RECOVERY_ROUTES[key] || "",
    };
  }
  if (!VALID_TRANSITIONS[fromState]?.includes(toState)) {
    return {
      ok: false,
      from_state: fromState,
      to_state: toState,
      reason_code: "transition_not_allowed",
      recovery_route: RECOVERY_ROUTES[key] || "",
    };
  }
  return { ok: true, from_state: fromState, to_state: toState };
}

export function programArtifactsRoot(
  projectRoot: string,
  version: string,
  programSlug: string,
): string {
  return join(
    projectRoot,
    "docs/beacon",
    version,
    "programs",
    programSlug,
  );
}

export function programRunStatePath(
  projectRoot: string,
  version: string,
  programSlug: string,
): string {
  return join(
    programArtifactsRoot(projectRoot, version, programSlug),
    "program-run-state.json",
  );
}

export function programAckPath(
  projectRoot: string,
  version: string,
  programSlug: string,
): string {
  return join(
    programArtifactsRoot(projectRoot, version, programSlug),
    "program-ack.json",
  );
}

function nowIso(): string {
  return new Date().toISOString();
}

export function slugifyProgram(utterance: string, explicit = ""): string {
  if (explicit.trim()) return explicit.trim();
  const tokens = utterance.toLowerCase().match(/[a-z0-9]+/g) || [];
  const base = tokens.slice(0, 6).join("-") || "program";
  return base.slice(0, 48);
}

export function readProgramRunState(
  projectRoot: string,
  version: string,
  programSlug: string,
): ProgramRunState | null {
  const path = programRunStatePath(projectRoot, version, programSlug);
  if (!existsSync(path)) return null;
  try {
    return JSON.parse(readFileSync(path, "utf-8")) as ProgramRunState;
  } catch {
    return null;
  }
}

export function writeProgramRunState(
  projectRoot: string,
  state: ProgramRunState,
): string {
  const dir = programArtifactsRoot(
    projectRoot,
    state.version,
    state.program_slug,
  );
  mkdirSync(dir, { recursive: true });
  const path = join(dir, "program-run-state.json");
  const payload = { ...state, updated_at: nowIso() };
  writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`, "utf-8");
  return path;
}

export function hasP4Ack(
  projectRoot: string,
  version: string,
  programSlug: string,
  state?: ProgramRunState | null,
): boolean {
  if (state?.p4_ack === true) return true;
  const ackPath = programAckPath(projectRoot, version, programSlug);
  return existsSync(ackPath);
}

/** P4 user ack must exist before spawning per-lake delivery (AC-073 / AC-PBP-016). */
export function canSpawnPerLakeDelivery(
  projectRoot: string,
  state: ProgramRunState,
): boolean {
  if (state.lake_or_ocean === "湖") return true;
  if (!hasP4Ack(projectRoot, state.version, state.program_slug, state)) {
    return false;
  }
  const skipP4 = transition(state.fsm_state, "program_delivery");
  if (!skipP4.ok && state.fsm_state !== "program_delivery") {
    const advance = transition("feature_graph_ack", "lakes_truth_in_progress");
    return advance.ok && hasP4Ack(projectRoot, state.version, state.program_slug, state);
  }
  return true;
}

export function blockDeliveryWithoutP4(
  projectRoot: string,
  state: ProgramRunState,
): { blocked: boolean; reason_code: string; recovery_route: string } {
  if (canSpawnPerLakeDelivery(projectRoot, state)) {
    return { blocked: false, reason_code: "", recovery_route: "" };
  }
  const illegal = transition(state.fsm_state, "program_delivery");
  if (!illegal.ok && state.fsm_state !== "program_frozen") {
    return {
      blocked: true,
      reason_code: illegal.reason_code || "p4_ack_required",
      recovery_route:
        illegal.recovery_route ||
        "Complete P4 user ack (program-ack.json) before per-lake delivery",
    };
  }
  return {
    blocked: true,
    reason_code: "p4_ack_required",
    recovery_route:
      "Write program-ack.json or set p4_ack=true after P4 user acknowledgment",
  };
}

export function inferNextAction(state: ProgramRunState): string {
  if (state.program_phase === "P4" && !state.p4_ack) {
    return "await_p4_user_ack";
  }
  if (state.program_phase === "P5") {
    return "per_lake_truth_promotion";
  }
  if (state.program_phase === "P6") {
    return "program_freeze_gate";
  }
  return `program_phase:${state.program_phase}`;
}

export function createInitialProgramRunState(input: {
  projectRoot: string;
  version: string;
  programSlug: string;
  planMode?: string;
  lakeOrOcean?: "湖" | "海";
  runDir?: string;
  resumeFrom?: ProgramRunState | null;
}): ProgramRunState {
  if (input.resumeFrom) {
    return {
      ...input.resumeFrom,
      run_dir: input.runDir || input.resumeFrom.run_dir,
      updated_at: nowIso(),
    };
  }
  const lakeOrOcean = input.lakeOrOcean || "海";
  const phase: ProgramPhase = lakeOrOcean === "湖" ? "P5" : "P0";
  const fsm: ProgramPlanState =
    lakeOrOcean === "湖" ? "lakes_truth_in_progress" : "program_intent_captured";
  return {
    schema_version: "1.0",
    program_slug: input.programSlug,
    version: input.version,
    plan_mode: input.planMode || "auto-detect",
    program_phase: phase,
    fsm_state: fsm,
    lake_or_ocean: lakeOrOcean,
    p4_ack: false,
    next_action: inferNextAction({
      schema_version: "1.0",
      program_slug: input.programSlug,
      version: input.version,
      plan_mode: input.planMode || "auto-detect",
      program_phase: phase,
      fsm_state: fsm,
      lake_or_ocean: lakeOrOcean,
      p4_ack: false,
      next_action: "",
      updated_at: nowIso(),
    }),
    run_dir: input.runDir,
    updated_at: nowIso(),
  };
}

export function applyE2eProgramFixture(state: ProgramRunState): ProgramRunState {
  return {
    ...state,
    program_phase: "P5",
    fsm_state: "lakes_truth_in_progress",
    p4_ack: true,
    next_action: "e2e_fixture_per_lake_delivery",
    updated_at: nowIso(),
  };
}

export function advanceProgramPhase(
  state: ProgramRunState,
  targetPhase: ProgramPhase,
): { ok: boolean; state: ProgramRunState; reason_code?: string } {
  const targetFsm = PHASE_TO_FSM[targetPhase];
  const result = transition(state.fsm_state, targetFsm);
  if (!result.ok && state.fsm_state !== targetFsm) {
    return { ok: false, state, reason_code: result.reason_code };
  }
  const next: ProgramRunState = {
    ...state,
    program_phase: targetPhase,
    fsm_state: targetFsm,
    next_action: inferNextAction({
      ...state,
      program_phase: targetPhase,
      fsm_state: targetFsm,
    }),
    updated_at: nowIso(),
  };
  return { ok: true, state: next };
}
