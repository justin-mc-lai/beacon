import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { buildIterationPrompt } from "../templates/iteration-prompt.js";
import { createBeaconOrchestratorHooks } from "./hooks.js";
import { BeaconPhaseController } from "./phase-controller.js";

describe("truth-phase-agent", () => {
  let runDir: string;

  beforeEach(() => {
    runDir = mkdtempSync(join(tmpdir(), "beacon-run-truth-phase-"));
    process.env.BEACON_RUN_MOCK_HARNESS = "1";
  });

  afterEach(() => {
    delete process.env.BEACON_RUN_MOCK_HARNESS;
    rmSync(runDir, { recursive: true, force: true });
  });

  it("truth phase routes through agent hooks, not harness-only loop (AC-055)", async () => {
    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot: "/tmp/project",
        version: "v1.6.0",
        feature: "gum-choose-filter-parity",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
        utterance: "deliver gum choose/filter parity",
      },
      runDir,
      "truth",
    );
    const hooks = createBeaconOrchestratorHooks(controller);

    const decision = await hooks.beforeAgentIteration?.();
    expect(decision).toBe("run_agent");
    expect(controller.isHarnessOnlyPhase()).toBe(false);

    const base = buildIterationPrompt({
      n: 1,
      runId: "run-truth",
      prompt: "deliver gum choose/filter parity",
    });
    const augmented = hooks.augmentIterationPrompt?.(base) ?? "";
    expect(augmented).toContain("Beacon phase: truth");
    expect(augmented).not.toContain("Harness-only phase");
  });
});
