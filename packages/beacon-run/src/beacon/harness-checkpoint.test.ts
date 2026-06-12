import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  appendTruthPromotion,
  buildPhaseHarnessArgs,
  buildTruthFreezeGateArgs,
  readTruthPromotion,
  runPhaseHarness,
  runTruthPhaseExitHarness,
} from "./harness-checkpoint.js";

describe("harness-checkpoint", () => {
  let runDir: string;

  beforeEach(() => {
    runDir = mkdtempSync(join(tmpdir(), "beacon-run-harness-"));
    process.env.BEACON_RUN_MOCK_HARNESS = "1";
  });

  afterEach(() => {
    delete process.env.BEACON_RUN_MOCK_HARNESS;
    rmSync(runDir, { recursive: true, force: true });
  });

  it("records harness calls with phase + checkpoint (AC-057 / TC-057)", () => {
    appendTruthPromotion(runDir, {
      phase: "truth",
      checkpoint: "entry",
      command: "beacon truth-map resolve demo --json",
      exit_code: 0,
    });
    const promotion = readTruthPromotion(runDir);
    expect(promotion.calls).toHaveLength(1);
    expect(promotion.calls[0]?.phase).toBe("truth");
    expect(promotion.calls[0]?.checkpoint).toBe("entry");
    expect(promotion.calls[0]?.exit_code).toBe(0);
  });

  it("smoke-truth-exit uses truth-map resolve for smoke truth exit instead of sync-materials (AC-063 / TC-065)", () => {
    const args = buildPhaseHarnessArgs("truth", "exit", {
      projectRoot: "/tmp/worktree",
      version: "v1.6.0",
      feature: "go-todo-crud-smoke",
      scopeMode: "smoke",
    });
    expect(args?.[0]).toBe("truth-map");
    expect(args?.[1]).toBe("resolve");
    expect(args?.join(" ")).not.toContain("sync-materials");
  });

  it("builds worktree harness args with worktree project root (AC-061 / TC-063)", () => {
    const worktree = "/tmp/beacon-gnhf-worktrees/demo-run";
    const args = buildPhaseHarnessArgs("truth", "exit", {
      projectRoot: worktree,
      version: "v1.6.0",
      feature: "go-todo-crud-smoke",
      scopeMode: "full_parity",
    });
    expect(args).toContain(worktree);
    expect(args?.join(" ")).not.toContain("/Users/apple/Developer/Personal/products/beacon");
  });

  it("builds phase harness args for truth/generate/qa/release", () => {
    const ctx = {
      projectRoot: "/tmp/project",
      version: "v1.6.0",
      feature: "demo-feature",
      implementRunner: "codex-subagents",
    };
    expect(buildPhaseHarnessArgs("truth", "entry", ctx)).toEqual([
      "truth-map",
      "resolve",
      "demo-feature",
      "--project",
      "/tmp/project",
      "--version",
      "v1.6.0",
      "--json",
    ]);
    expect(buildPhaseHarnessArgs("qa", "phase", ctx)?.[0]).toBe("qa");
    expect(buildPhaseHarnessArgs("release", "phase", ctx)).toEqual([
      "release",
      "check",
      "v1.6.0",
      "--project",
      "/tmp/project",
      "--json",
    ]);
  });

  it("truth-freeze-gate runTruthPhaseExitHarness records freeze gate commands (AC-068 / TC-068)", () => {
    const projectRoot = mkdtempSync(join(tmpdir(), "beacon-run-harness-frozen-"));
    const featureDir = join(
      projectRoot,
      "docs/beacon/v1.6.0/features/demo-feature",
    );
    mkdirSync(featureDir, { recursive: true });
    writeFileSync(
      join(featureDir, "truth.md"),
      "---\nslug: demo-feature\nstatus: frozen\n---\n# Demo\n",
      "utf8",
    );

    const result = runTruthPhaseExitHarness(runDir, {
      projectRoot,
      version: "v1.6.0",
      feature: "demo-feature",
      scopeMode: "smoke",
    });
    expect(result.ok).toBe(true);
    const promotion = readTruthPromotion(runDir);
    expect(
      promotion.calls.some((call) => call.command.includes("freeze demo-feature")),
    ).toBe(true);
    expect(
      promotion.calls.some((call) => call.checkpoint === "freeze_gate"),
    ).toBe(true);

    rmSync(projectRoot, { recursive: true, force: true });
  });

  it("truth exit harness accepts draft frontmatter when story machine is frozen", () => {
    const projectRoot = mkdtempSync(join(tmpdir(), "beacon-run-harness-story-"));
    const featureDir = join(
      projectRoot,
      "docs/beacon/v1.6.0/features/demo-feature",
    );
    mkdirSync(featureDir, { recursive: true });
    writeFileSync(
      join(featureDir, "truth.md"),
      "---\nslug: demo-feature\nstatus: draft\n---\n# Demo\n",
      "utf8",
    );
    const storyDir = join(
      projectRoot,
      "docs/beacon/v1.6.0/.machine/user-story",
    );
    mkdirSync(storyDir, { recursive: true });
    writeFileSync(
      join(storyDir, "demo-feature.json"),
      JSON.stringify({ lifecycle_status: "frozen" }),
      "utf8",
    );

    const result = runTruthPhaseExitHarness(runDir, {
      projectRoot,
      version: "v1.6.0",
      feature: "demo-feature",
      scopeMode: "smoke",
    });
    expect(result.ok).toBe(true);

    rmSync(projectRoot, { recursive: true, force: true });
  });

  it("buildTruthFreezeGateArgs includes clarity + freeze (TC-065 reconciled)", () => {
    const steps = buildTruthFreezeGateArgs({
      projectRoot: "/tmp/worktree",
      version: "v1.6.0",
      feature: "go-todo-crud-smoke",
    });
    expect(steps).toHaveLength(2);
    expect(steps[0]?.[1]).toBe("sync-requirement-clarity");
    expect(steps[1]?.[0]).toBe("freeze");
  });

  it("runPhaseHarness writes truth-promotion.json", () => {
    runPhaseHarness(runDir, "truth", "entry", {
      projectRoot: "/tmp/project",
      version: "v1.6.0",
      feature: "demo-feature",
    });
    const raw = JSON.parse(readFileSync(join(runDir, "truth-promotion.json"), "utf8"));
    expect(raw.calls[0].command).toContain("truth-map resolve");
  });
});
