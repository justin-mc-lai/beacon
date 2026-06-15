import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  isFeatureTruthFrozen,
  isFeatureTruthFrozenFromPayload,
  readTruthFrontmatterStatus,
} from "./truth-frozen.js";

describe("truth-frozen (AC-068)", () => {
  let root: string;

  beforeEach(() => {
    root = mkdtempSync(join(tmpdir(), "beacon-run-frozen-"));
  });

  afterEach(() => {
    rmSync(root, { recursive: true, force: true });
  });

  function writeTruth(status: string) {
    const dir = join(root, "docs/beacon/v1.6.0/features/demo-feature");
    mkdirSync(dir, { recursive: true });
    writeFileSync(
      join(dir, "truth.md"),
      `---
slug: demo-feature
status: ${status}
---
# Demo
`,
      "utf8",
    );
  }

  it("reads frozen from truth frontmatter", () => {
    writeTruth("frozen");
    expect(readTruthFrontmatterStatus(root, "v1.6.0", "demo-feature")).toBe(
      "frozen",
    );
    expect(
      isFeatureTruthFrozenFromPayload(root, "v1.6.0", "demo-feature", {
        feature_truth: { frontmatter: { status: "draft" } },
      }),
    ).toBe(true);
    expect(
      isFeatureTruthFrozenFromPayload(root, "v1.6.0", "demo-feature", {
        feature_truth: { frontmatter: { status: "frozen" } },
      }),
    ).toBe(true);
  });

  it("draft resolver payload stays not frozen without machine or disk frozen", () => {
    writeTruth("draft");
    expect(
      isFeatureTruthFrozenFromPayload(root, "v1.6.0", "demo-feature", {
        feature_truth: { frontmatter: { status: "draft" } },
      }),
    ).toBe(false);
  });

  it("isFeatureTruthFrozen reads draft truth as not frozen (mock harness)", () => {
    writeTruth("draft");
    process.env.BEACON_RUN_MOCK_HARNESS = "1";
    expect(isFeatureTruthFrozen(root, "v1.6.0", "demo-feature")).toBe(false);
    delete process.env.BEACON_RUN_MOCK_HARNESS;
  });

  it("isFeatureTruthFrozen reads frozen truth (mock harness)", () => {
    writeTruth("frozen");
    process.env.BEACON_RUN_MOCK_HARNESS = "1";
    expect(isFeatureTruthFrozen(root, "v1.6.0", "demo-feature")).toBe(true);
    delete process.env.BEACON_RUN_MOCK_HARNESS;
  });

  it("resolver draft frontmatter is frozen when story machine is frozen", () => {
    writeTruth("draft");
    const storyDir = join(root, "docs/beacon/v1.6.0/.machine/user-story");
    mkdirSync(storyDir, { recursive: true });
    writeFileSync(
      join(storyDir, "demo-feature.json"),
      JSON.stringify({ lifecycle_status: "frozen" }),
      "utf8",
    );
    expect(
      isFeatureTruthFrozenFromPayload(root, "v1.6.0", "demo-feature", {
        feature_truth: { frontmatter: { status: "draft" } },
      }),
    ).toBe(true);
    process.env.BEACON_RUN_MOCK_HARNESS = "1";
    expect(isFeatureTruthFrozen(root, "v1.6.0", "demo-feature")).toBe(true);
    delete process.env.BEACON_RUN_MOCK_HARNESS;
  });
});
