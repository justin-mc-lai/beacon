import { describe, expect, it } from "vitest";
import { buildBeaconPhaseArtifact, buildBeaconPhasePrompt } from "./phase-prompt.js";

describe("beacon-phase-prompt", () => {
  it("injects Beacon phase and skill boundary digest (AC-054 / TC-056)", () => {
    const prompt = buildBeaconPhasePrompt({
      phase: "truth",
      feature: "gum-choose-filter-parity",
      version: "v1.6.0"
    });
    expect(prompt).toMatch(/Beacon phase: truth/);
    expect(prompt).toMatch(/harness boundary/);
    expect(prompt).toMatch(/allowed harness/);
    expect(prompt).toMatch(/forbidden/);
    expect(prompt).toMatch(/subprocess Skill MD execution/);
  });

  it("builds beacon-phase.json artifact shape", () => {
    const artifact = buildBeaconPhaseArtifact({ phase: "generate", feature: "demo", version: "v1.6.0" });
    expect(artifact.schema_version).toBe("1.0");
    expect(artifact.phase).toBe("generate");
    expect(artifact.prompt).toContain("Beacon phase: generate");
    expect(Array.isArray(artifact.allowed_harness)).toBe(true);
  });
});
