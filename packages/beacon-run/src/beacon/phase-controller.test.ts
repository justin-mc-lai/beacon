import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
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

  it("phase-promotion-visibility records phase_promoted false when smoke truth package is missing (AC-064 / TC-066)", async () => {
    const projectRoot = mkdtempSync(join(tmpdir(), "beacon-run-phase-smoke-"));
    const featureDir = join(
      projectRoot,
      "docs/beacon/v1.6.0/features/go-todo-crud-smoke",
    );
    mkdirSync(featureDir, { recursive: true });
    writeFileSync(
      join(featureDir, "truth.md"),
      "---\nslug: go-todo-crud-smoke\n---\nscope_mode = smoke\n",
      "utf8",
    );

    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot,
        version: "v1.6.0",
        feature: "go-todo-crud-smoke",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
      },
      runDir,
      "truth",
    );

    await controller.beforeAgentIteration();
    await controller.afterAgentIteration(true, true);

    const artifact = JSON.parse(
      readFileSync(join(runDir, "beacon-phase.json"), "utf8"),
    );
    expect(artifact.phase).toBe("truth");
    expect(artifact.phase_promoted).toBe(false);
    expect(artifact.last_harness_exit?.ok).toBe(false);
    expect(artifact.last_harness_exit?.reason_code).toBe(
      "smoke_truth_package_missing",
    );

    rmSync(projectRoot, { recursive: true, force: true });
  });

  it("advances agent phase on should_fully_stop + exit harness when truth is frozen (AC-068)", async () => {
    const projectRoot = mkdtempSync(join(tmpdir(), "beacon-run-phase-frozen-"));
    const featureDir = join(
      projectRoot,
      "docs/beacon/v1.6.0/features/demo",
    );
    mkdirSync(featureDir, { recursive: true });
    writeFileSync(
      join(featureDir, "truth.md"),
      "---\nslug: demo\nstatus: frozen\n---\n# Demo\n\nFrozen truth package for harness promotion.\n",
      "utf8",
    );

    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot,
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

    rmSync(projectRoot, { recursive: true, force: true });
  });

  it("truth-freeze-gate does not promote to generate when truth remains draft (AC-068 / TC-068)", async () => {
    const projectRoot = mkdtempSync(join(tmpdir(), "beacon-run-phase-draft-"));
    const featureDir = join(
      projectRoot,
      "docs/beacon/v1.6.0/features/demo",
    );
    mkdirSync(featureDir, { recursive: true });
    writeFileSync(
      join(featureDir, "truth.md"),
      "---\nslug: demo\nstatus: draft\n---\n# Demo\n\nDraft truth package that must not unlock generate.\n",
      "utf8",
    );

    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot,
        version: "v1.6.0",
        feature: "demo",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
      },
      runDir,
      "truth",
    );

    await controller.beforeAgentIteration();
    await controller.afterAgentIteration(true, true);

    const artifact = JSON.parse(
      readFileSync(join(runDir, "beacon-phase.json"), "utf8"),
    );
    expect(artifact.phase).toBe("truth");
    expect(artifact.phase_promoted).toBe(false);
    expect(artifact.last_harness_exit?.reason_code).toBe("truth_not_frozen");

    rmSync(projectRoot, { recursive: true, force: true });
  });

  it("generate-blocked-without-frozen blocks generate agent iteration when truth is not frozen (AC-068 / TC-069)", async () => {
    const projectRoot = mkdtempSync(join(tmpdir(), "beacon-run-phase-gen-block-"));
    const featureDir = join(
      projectRoot,
      "docs/beacon/v1.6.0/features/demo",
    );
    mkdirSync(featureDir, { recursive: true });
    writeFileSync(
      join(featureDir, "truth.md"),
      "---\nslug: demo\nstatus: draft\n---\n# Demo\n\nDraft truth must demote generate.\n",
      "utf8",
    );

    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot,
        version: "v1.6.0",
        feature: "demo",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
      },
      runDir,
      "generate",
    );

    const decision = await controller.beforeAgentIteration();
    expect(decision).toBe("run_agent");
    expect(controller.currentPhase()).toBe("truth");

    rmSync(projectRoot, { recursive: true, force: true });
  });

  it("implement-preflight-demote demotes generate to truth on implement preflight revision_not_frozen (AC-068 / TC-070)", async () => {
    const projectRoot = mkdtempSync(join(tmpdir(), "beacon-run-phase-demote-"));
    const featureDir = join(
      projectRoot,
      "docs/beacon/v1.6.0/features/demo",
    );
    mkdirSync(featureDir, { recursive: true });
    writeFileSync(
      join(featureDir, "truth.md"),
      "---\nslug: demo\nstatus: frozen\n---\n# Demo\n\nFrozen at generate entry; implement preflight still blocked.\n",
      "utf8",
    );
    process.env.BEACON_RUN_MOCK_IMPLEMENT_PREFLIGHT = "revision_not_frozen";

    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot,
        version: "v1.6.0",
        feature: "demo",
        truthBootstrap: "agent",
        implementRunner: "codex-subagents",
      },
      runDir,
      "generate",
    );

    await controller.beforeAgentIteration();
    await controller.afterAgentIteration(true, true);

    expect(controller.currentPhase()).toBe("truth");
    const promotion = JSON.parse(
      readFileSync(join(runDir, "truth-promotion.json"), "utf8"),
    );
    expect(
      promotion.calls.some(
        (call: { mode?: string }) => call.mode === "truth_not_frozen",
      ),
    ).toBe(true);

    delete process.env.BEACON_RUN_MOCK_IMPLEMENT_PREFLIGHT;
    rmSync(projectRoot, { recursive: true, force: true });
  });
});
