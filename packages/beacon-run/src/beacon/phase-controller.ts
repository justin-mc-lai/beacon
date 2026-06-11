import { join } from "node:path";
import {
  buildBeaconPhaseArtifact,
  buildBeaconPhasePrompt,
  type BeaconPhase,
} from "./phase-prompt.js";
import { readJson, writeJson } from "./fs.js";
import {
  appendTruthPromotion,
  beaconJsonSucceeded,
  runPhaseHarness,
  type HarnessContext,
} from "./harness-checkpoint.js";
import { augmentIterationPromptWithBeacon } from "./iteration-prompt.js";
import { bootstrapColdStartTruthFallback } from "./truth-bootstrap-fallback.js";

export const AGENT_PHASES: BeaconPhase[] = ["truth", "generate"];
export const HARNESS_PHASES: BeaconPhase[] = ["qa", "release"];
export const BEACON_LIFECYCLE_PHASES: BeaconPhase[] = [
  ...AGENT_PHASES,
  ...HARNESS_PHASES,
];

export type BeaconRunContext = {
  enabled: boolean;
  projectRoot: string;
  version: string;
  feature: string;
  truthBootstrap: "agent" | "fallback";
  implementRunner: string;
  utterance?: string;
};

export type BeaconPhaseState = {
  schema_version: "1.0";
  phase: BeaconPhase;
  feature: string;
  version: string;
  project_root: string;
  truth_bootstrap: "agent" | "fallback";
  phases_completed: BeaconPhase[];
  prompt: string;
  allowed_harness: string[];
  forbidden_harness: string[];
  updated_at: string;
};

export type BeaconBeforeIterationDecision = "run_agent" | "retry" | "break";
export type BeaconAfterIterationDecision = "continue" | "break";

function beaconPhasePath(runDir: string): string {
  return join(runDir, "beacon-phase.json");
}

export function readBeaconPhaseState(runDir: string): BeaconPhaseState | null {
  const raw = readJson<BeaconPhaseState | null>(beaconPhasePath(runDir), null);
  if (!raw || !raw.phase) return null;
  return raw;
}

export function writeBeaconPhaseState(
  runDir: string,
  ctx: BeaconRunContext,
  phase: BeaconPhase,
  phasesCompleted: BeaconPhase[] = [],
): BeaconPhaseState {
  const artifact = buildBeaconPhaseArtifact({
    phase,
    feature: ctx.feature,
    version: ctx.version,
  });
  const state: BeaconPhaseState = {
    schema_version: "1.0",
    phase,
    feature: ctx.feature,
    version: ctx.version,
    project_root: ctx.projectRoot,
    truth_bootstrap: ctx.truthBootstrap,
    phases_completed: phasesCompleted,
    prompt: artifact.prompt,
    allowed_harness: artifact.allowed_harness,
    forbidden_harness: artifact.forbidden_harness,
    updated_at: new Date().toISOString(),
  };
  writeJson(beaconPhasePath(runDir), state);
  return state;
}

const PHASE_OBJECTIVES: Record<BeaconPhase, string> = {
  truth:
    "Advance requirement truth for this feature: research, parity notes, truth/tests/tasks drafts, and promotion-ready materials. Do not implement product code in this phase. Set should_fully_stop=true when truth materials are ready for Beacon sync/refreeze.",
  generate:
    "Implement toward the user objective with verifiable commits. Follow frozen truth when present. Set should_fully_stop=true when implementation is ready for Beacon QA.",
  repair:
    "Repair implementation using QA/release findings already recorded in notes. Set should_fully_stop=true when repair candidate is ready for QA re-run.",
  qa: "Harness-only phase: Beacon QA runs outside the agent loop.",
  release: "Harness-only phase: Beacon release check runs outside the agent loop.",
};

export class BeaconPhaseController {
  private phase: BeaconPhase;
  private phasesCompleted: BeaconPhase[];
  private entryHarnessDone = false;
  private truthFallbackDone = false;

  constructor(
    private readonly ctx: BeaconRunContext,
    private readonly runDir: string,
    initialPhase: BeaconPhase = "truth",
    phasesCompleted: BeaconPhase[] = [],
  ) {
    this.phase = initialPhase;
    this.phasesCompleted = [...phasesCompleted];
    writeBeaconPhaseState(this.runDir, this.ctx, this.phase, this.phasesCompleted);
  }

  static fromRunDir(runDir: string, ctx: BeaconRunContext): BeaconPhaseController {
    const saved = readBeaconPhaseState(runDir);
    if (saved) {
      return new BeaconPhaseController(
        ctx,
        runDir,
        saved.phase,
        saved.phases_completed || [],
      );
    }
    return new BeaconPhaseController(ctx, runDir);
  }

  currentPhase(): BeaconPhase {
    return this.phase;
  }

  isHarnessOnlyPhase(): boolean {
    return HARNESS_PHASES.includes(this.phase);
  }

  isDone(): boolean {
    return (
      this.phasesCompleted.length >= BEACON_LIFECYCLE_PHASES.length ||
      (this.phase === "release" &&
        this.phasesCompleted.includes("release"))
    );
  }

  harnessContext(): HarnessContext {
    return {
      projectRoot: this.ctx.projectRoot,
      version: this.ctx.version,
      feature: this.ctx.feature,
      implementRunner: this.ctx.implementRunner,
    };
  }

  augmentIterationPrompt(basePrompt: string): string {
    const digest = buildBeaconPhasePrompt({
      phase: this.phase,
      feature: this.ctx.feature,
      version: this.ctx.version,
    });
    const objective = PHASE_OBJECTIVES[this.phase];
    return augmentIterationPromptWithBeacon(basePrompt, digest, objective);
  }

  async beforeAgentIteration(): Promise<BeaconBeforeIterationDecision> {
    if (this.isDone()) return "break";

    if (this.isHarnessOnlyPhase()) {
      const result = runPhaseHarness(
        this.runDir,
        this.phase,
        "phase",
        this.harnessContext(),
      );
      this.completeCurrentPhase(result ? beaconJsonSucceeded(result) : true);
      if (this.isDone()) return "break";
      return "retry";
    }

    if (
      this.phase === "truth" &&
      this.ctx.truthBootstrap === "fallback" &&
      !this.truthFallbackDone
    ) {
      const bootstrap = bootstrapColdStartTruthFallback(
        this.ctx.projectRoot,
        this.runDir,
        {
          version: this.ctx.version,
          feature: this.ctx.feature,
          utterance: this.ctx.utterance || this.ctx.feature,
        },
      );
      this.truthFallbackDone = true;
      if (!bootstrap.ok) {
        appendTruthPromotion(this.runDir, {
          phase: "truth",
          checkpoint: "entry",
          command: "truth-bootstrap-fallback",
          exit_code: 1,
          stderr: bootstrap.detail.slice(0, 500),
          mode: "truth-bootstrap-fallback-failed",
        });
      }
    }

    if (!this.entryHarnessDone) {
      runPhaseHarness(
        this.runDir,
        this.phase,
        "entry",
        this.harnessContext(),
      );
      this.entryHarnessDone = true;
    }

    writeBeaconPhaseState(
      this.runDir,
      this.ctx,
      this.phase,
      this.phasesCompleted,
    );
    return "run_agent";
  }

  async afterAgentIteration(
    success: boolean,
    shouldFullyStop: boolean,
  ): Promise<BeaconAfterIterationDecision> {
    if (!success || !shouldFullyStop || this.isHarnessOnlyPhase()) {
      return "continue";
    }

    const exitResult = runPhaseHarness(
      this.runDir,
      this.phase,
      "exit",
      this.harnessContext(),
    );
    const ok = exitResult ? beaconJsonSucceeded(exitResult) : true;
    this.completeCurrentPhase(ok);
    if (this.isDone()) return "break";
    return "continue";
  }

  private completeCurrentPhase(ok: boolean): void {
    if (!this.phasesCompleted.includes(this.phase)) {
      this.phasesCompleted.push(this.phase);
    }
    const nextIndex = BEACON_LIFECYCLE_PHASES.indexOf(this.phase) + 1;
    if (nextIndex < BEACON_LIFECYCLE_PHASES.length && ok) {
      this.phase = BEACON_LIFECYCLE_PHASES[nextIndex]!;
      this.entryHarnessDone = false;
      writeBeaconPhaseState(
        this.runDir,
        this.ctx,
        this.phase,
        this.phasesCompleted,
      );
    }
  }
}
