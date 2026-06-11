import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { BeaconPhaseController } from "./phase-controller.js";

describe("truth-bootstrap fallback (AC-056)", () => {
  let runDir: string;

  beforeEach(() => {
    runDir = mkdtempSync(join(tmpdir(), "beacon-run-truth-bootstrap-"));
    process.env.BEACON_RUN_MOCK_HARNESS = "1";
  });

  afterEach(() => {
    delete process.env.BEACON_RUN_MOCK_HARNESS;
    delete process.env.BEACON_RUN_TEST_TRUTH_BOOTSTRAP;
    rmSync(runDir, { recursive: true, force: true });
  });

  it("no-default-template-truth: agent mode does not call prd-bootstrap", async () => {
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

    await controller.beforeAgentIteration();
    const promotion = JSON.parse(
      readFileSync(join(runDir, "truth-promotion.json"), "utf8"),
    );
    expect(
      promotion.calls.some((call: { command: string }) =>
        call.command.includes("prd-bootstrap"),
      ),
    ).toBe(false);
  });

  it("no-default-template-truth: fallback mode runs template chain once", async () => {
    process.env.BEACON_RUN_TEST_TRUTH_BOOTSTRAP = "fixture";
    const controller = new BeaconPhaseController(
      {
        enabled: true,
        projectRoot: "/tmp/project",
        version: "v1.6.0",
        feature: "gum-choose-filter-parity",
        truthBootstrap: "fallback",
        implementRunner: "codex-subagents",
        utterance: "deliver gum choose/filter parity",
      },
      runDir,
      "truth",
    );

    await controller.beforeAgentIteration();
    await controller.beforeAgentIteration();
    const promotion = JSON.parse(
      readFileSync(join(runDir, "truth-promotion.json"), "utf8"),
    );
    const bootstrapCalls = promotion.calls.filter((call: { mode?: string }) =>
      String(call.mode || "").startsWith("truth-bootstrap-fallback"),
    );
    expect(bootstrapCalls.length).toBe(1);
  });
});
