import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { buildIterationPrompt } from "../templates/iteration-prompt.js";
import { BeaconPhaseController } from "./phase-controller.js";

describe("beacon phase-controller", () => {
  let runDir: string;

  beforeEach(() => {
    runDir = mkdtempSync(join(tmpdir(), "beacon-run-phase-"));
    process.env.BEACON_RUN_MOCK_HARNESS = "1";
  });

  afterEach(() => {
    delete process.env.BEACON_RUN_MOCK_HARNESS;
    rmSync(runDir, { recursive: true, force: true });
  });

  it("writes beacon-phase.json on init (AC-054)", () => {
    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot: "/tmp/project",
        version: "v1.6.0",
        feature: "gum-choose-filter-parity",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
      },
      runDir,
    );
    expect(controller.currentPhase()).toBe("truth");
    const artifact = JSON.parse(
      readFileSync(join(runDir, "beacon-phase.json"), "utf8"),
    );
    expect(artifact.phase).toBe("truth");
    expect(artifact.feature).toBe("gum-choose-filter-parity");
    expect(artifact.prompt).toContain("Beacon phase: truth");
  });

  it("injects beacon digest into iteration prompt (AC-054 / TC-056)", () => {
    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot: "/tmp/project",
        version: "v1.6.0",
        feature: "demo",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
      },
      runDir,
      "generate",
    );
    const base = buildIterationPrompt({
      n: 1,
      runId: "run-1",
      prompt: "deliver gum choose/filter parity",
      requireShouldFullyStop: true,
    });
    const augmented = controller.augmentIterationPrompt(base);
    expect(augmented).toContain("Beacon Harness Context");
    expect(augmented).toContain("Beacon phase: generate");
    expect(augmented).toContain("subprocess Skill MD execution");
    expect(augmented).toContain("deliver gum choose/filter parity");
    expect(augmented).toContain("should_fully_stop");
    expect(augmented).toContain("Beacon Output Contract");
    expect(augmented).toContain("output-schema.json");
  });

  it("runs harness-only qa/release phases without agent iterations", async () => {
    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot: "/tmp/project",
        version: "v1.6.0",
        feature: "demo",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
      },
      runDir,
      "qa",
    );

    const qaDecision = await controller.beforeAgentIteration();
    expect(qaDecision).toBe("retry");
    expect(controller.currentPhase()).toBe("release");

    const releaseDecision = await controller.beforeAgentIteration();
    expect(releaseDecision).toBe("break");
    expect(controller.isDone()).toBe(true);

    const promotion = JSON.parse(
      readFileSync(join(runDir, "truth-promotion.json"), "utf8"),
    );
    expect(promotion.calls.some((call: { command: string }) => call.command.includes("qa run"))).toBe(
      true,
    );
    expect(
      promotion.calls.some((call: { command: string }) => call.command.includes("release check")),
    ).toBe(true);
  });

  it("advances agent phase on should_fully_stop + exit harness", async () => {
    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot: "/tmp/project",
        version: "v1.6.0",
        feature: "demo",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
      },
      runDir,
      "truth",
    );

    await controller.beforeAgentIteration();
    const after = await controller.afterAgentIteration(true, true);
    expect(after).toBe("continue");
    expect(controller.currentPhase()).toBe("generate");
  });
});
