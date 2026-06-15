import { describe, expect, it } from "vitest";
import { augmentIterationPromptWithBeacon } from "./iteration-prompt.js";

describe("augmentIterationPromptWithBeacon", () => {
  it("documents beacon output-schema alignment including should_fully_stop", () => {
    const result = augmentIterationPromptWithBeacon(
      "base prompt",
      "## Beacon phase: truth",
      "Finish truth materials for refreeze.",
    );
    expect(result).toContain("Beacon Output Contract");
    expect(result).toContain("should_fully_stop");
    expect(result).toContain("output-schema.json");
    expect(result).toContain("Finish truth materials for refreeze.");
  });
});
