import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  applyE2eProgramFixture,
  blockDeliveryWithoutP4,
  canSpawnPerLakeDelivery,
  createInitialProgramRunState,
  isValidTransition,
  programRunStatePath,
  readProgramRunState,
  transition,
  writeProgramRunState,
  type ProgramRunState,
} from "./program-outer-fsm.js";

describe("program-outer-fsm", () => {
  let root: string;

  beforeEach(() => {
    root = mkdtempSync(join(tmpdir(), "beacon-run-program-fsm-"));
  });

  afterEach(() => {
    rmSync(root, { recursive: true, force: true });
  });

  it("blocks invalid skip from intent to inventory", () => {
    const result = transition("program_intent_captured", "program_inventory");
    expect(result.ok).toBe(false);
    expect(result.reason_code).toBe("invalid_transition");
    expect(isValidTransition("program_intent_captured", "program_inventory")).toBe(
      false,
    );
  });

  it("blocks change_open to delivery with pln-review recovery", () => {
    const result = transition("program_change_open", "program_delivery");
    expect(result.ok).toBe(false);
    expect(result.recovery_route).toBe("beacon-pln-review");
  });

  it("allows happy-path chain through plan_mode to lakes_frozen", () => {
    const chain: Array<[ProgramRunState["fsm_state"], ProgramRunState["fsm_state"]]> =
      [
        ["program_intent_captured", "plan_mode_selected"],
        ["plan_mode_selected", "program_inventory"],
        ["program_inventory", "program_reviewed"],
        ["program_reviewed", "feature_graph_ack"],
        ["feature_graph_ack", "lakes_truth_in_progress"],
        ["lakes_truth_in_progress", "lakes_frozen"],
        ["lakes_frozen", "program_frozen"],
      ];
    for (const [from, to] of chain) {
      const result = transition(from, to);
      expect(result.ok, `${from}->${to}`).toBe(true);
    }
  });

  it("P4 gate blocks per-lake delivery without program-ack.json", () => {
    const state = createInitialProgramRunState({
      projectRoot: root,
      version: "v1.6.1",
      programSlug: "sea-demo",
      lakeOrOcean: "海",
    });
    writeProgramRunState(root, {
      ...state,
      program_phase: "P4",
      fsm_state: "feature_graph_ack",
    });
    const loaded = readProgramRunState(root, "v1.6.1", "sea-demo");
    expect(loaded).not.toBeNull();
    expect(canSpawnPerLakeDelivery(root, loaded!)).toBe(false);
    const block = blockDeliveryWithoutP4(root, loaded!);
    expect(block.blocked).toBe(true);
    expect(block.reason_code).toBeTruthy();
  });

  it("P4 gate opens after program-ack.json exists", () => {
    const slug = "sea-ack-demo";
    const artifactRoot = join(root, "docs/beacon/v1.6.1/programs", slug);
    mkdirSync(artifactRoot, { recursive: true });
    writeFileSync(
      join(artifactRoot, "program-ack.json"),
      JSON.stringify({ ack: true, phase: "P4" }),
      "utf8",
    );
    const state = createInitialProgramRunState({
      projectRoot: root,
      version: "v1.6.1",
      programSlug: slug,
      lakeOrOcean: "海",
    });
    writeProgramRunState(root, {
      ...state,
      program_phase: "P5",
      fsm_state: "lakes_truth_in_progress",
    });
    const loaded = readProgramRunState(root, "v1.6.1", slug);
    expect(canSpawnPerLakeDelivery(root, loaded!)).toBe(true);
  });

  it("persists program-run-state.json under programs/<slug>/", () => {
    const state = createInitialProgramRunState({
      projectRoot: root,
      version: "v1.6.1",
      programSlug: "persist-demo",
      lakeOrOcean: "海",
      planMode: "auto",
    });
    const path = writeProgramRunState(root, state);
    expect(path).toBe(programRunStatePath(root, "v1.6.1", "persist-demo"));
    const loaded = readProgramRunState(root, "v1.6.1", "persist-demo");
    expect(loaded?.program_phase).toBe("P0");
    expect(loaded?.fsm_state).toBe("program_intent_captured");
    expect(loaded?.lake_or_ocean).toBe("海");
  });

  it("e2e fixture fast-forwards to P5 with p4_ack", () => {
    const state = createInitialProgramRunState({
      projectRoot: root,
      version: "v1.6.1",
      programSlug: "e2e-demo",
      lakeOrOcean: "海",
    });
    const fixture = applyE2eProgramFixture(state);
    expect(fixture.program_phase).toBe("P5");
    expect(fixture.p4_ack).toBe(true);
    expect(canSpawnPerLakeDelivery(root, fixture)).toBe(true);
  });
});

describe("e2e-program-sea", () => {
  it("sea path requires program mode state before nested delivery", () => {
    const root = mkdtempSync(join(tmpdir(), "beacon-run-e2e-sea-"));
    try {
      const state = applyE2eProgramFixture(
        createInitialProgramRunState({
          projectRoot: root,
          version: "v1.6.1",
          programSlug: "e2e-sea-fixture",
          lakeOrOcean: "海",
        }),
      );
      writeProgramRunState(root, state);
      const loaded = readProgramRunState(root, "v1.6.1", "e2e-sea-fixture");
      expect(loaded?.program_phase).toBe("P5");
      expect(blockDeliveryWithoutP4(root, loaded!).blocked).toBe(false);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });
});
