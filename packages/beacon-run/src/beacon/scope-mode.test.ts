import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { buildPhaseHarnessArgs } from "./harness-checkpoint.js";
import {
  readFeatureScopeMode,
  smokeTruthPackageReady,
} from "./scope-mode.js";

describe("scope-mode (AC-063)", () => {
  let root: string;

  beforeEach(() => {
    root = mkdtempSync(join(tmpdir(), "beacon-run-scope-"));
  });

  afterEach(() => {
    rmSync(root, { recursive: true, force: true });
  });

  function writeSmokeTruth() {
    const dir = join(
      root,
      "docs/beacon/v1.6.0/features/go-todo-crud-smoke",
    );
    mkdirSync(dir, { recursive: true });
    writeFileSync(
      join(dir, "truth.md"),
      `---
slug: go-todo-crud-smoke
---
# Smoke

scope_mode = smoke

Body with enough content to satisfy smoke truth package readiness checks for beacon-run harness exit.
`,
      "utf8",
    );
  }

  it("reads smoke scope_mode from feature truth", () => {
    writeSmokeTruth();
    expect(
      readFeatureScopeMode(root, "v1.6.0", "go-todo-crud-smoke"),
    ).toBe("smoke");
  });

  it("smoke truth exit uses resolve only, not sync-materials (TC-065)", () => {
    const args = buildPhaseHarnessArgs("truth", "exit", {
      projectRoot: root,
      version: "v1.6.0",
      feature: "go-todo-crud-smoke",
      scopeMode: "smoke",
    });
    expect(args?.[0]).toBe("truth-map");
    expect(args?.[1]).toBe("resolve");
    expect(args).not.toContain("sync-materials");
  });

  it("full_parity truth exit still uses sync-materials", () => {
    const args = buildPhaseHarnessArgs("truth", "exit", {
      projectRoot: root,
      version: "v1.6.0",
      feature: "demo-feature",
      scopeMode: "full_parity",
    });
    expect(args?.[0]).toBe("doctor");
    expect(args?.[1]).toBe("sync-materials");
  });

  it("smokeTruthPackageReady requires non-trivial body", () => {
    writeSmokeTruth();
    expect(smokeTruthPackageReady(root, "v1.6.0", "go-todo-crud-smoke")).toBe(
      true,
    );
  });
});
