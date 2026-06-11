import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  appendTruthPromotion,
  buildPhaseHarnessArgs,
  readTruthPromotion,
  runPhaseHarness,
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
    expect(buildPhaseHarnessArgs("release", "phase", ctx)?.[0]).toBe("release");
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
