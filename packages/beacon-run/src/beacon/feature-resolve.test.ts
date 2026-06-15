import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  inferFeatureSlugFromUtterance,
  resolveBeaconFeature,
  scoreFeatureMatch,
} from "./feature-resolve.js";

const tmpRoots: string[] = [];

afterEach(() => {
  while (tmpRoots.length) {
    tmpRoots.pop();
  }
});

function seedFeature(
  root: string,
  version: string,
  slug: string,
  truthBody: string,
) {
  const dir = join(root, "docs/beacon", version, "features", slug);
  mkdirSync(dir, { recursive: true });
  writeFileSync(
    join(dir, "truth.md"),
    `---\nstatus: frozen\nfeature: ${slug}\n---\n${truthBody}\n`,
    "utf8",
  );
}

describe("feature-resolve", () => {
  it("matches utterance path to existing go-todo-crud-smoke feature", () => {
    const root = join("/tmp", `beacon-feature-resolve-${Date.now()}`);
    tmpRoots.push(root);
    mkdirSync(join(root, "docs/beacon"), { recursive: true });
    writeFileSync(join(root, "docs/beacon/VERSION"), "v1.6.0\n", "utf8");
    seedFeature(
      root,
      "v1.6.0",
      "go-todo-crud-smoke",
      "Minimal smoke for examples/go-todo-crud CRUD API.",
    );

    const utterance =
      "在 examples/go-todo-crud 实现最小 Go HTTP CRUD，要求 go test 通过";
    expect(inferFeatureSlugFromUtterance(utterance)).toBe("go-todo-crud-crud");

    const resolved = resolveBeaconFeature({
      projectRoot: root,
      version: "v1.6.0",
      utterance,
    });
    expect("ok" in resolved).toBe(false);
    if ("ok" in resolved) return;
    expect(resolved.feature).toBe("go-todo-crud-smoke");
    expect(resolved.source).toBe("matched_existing");
    expect(scoreFeatureMatch(utterance, "go-todo-crud-smoke", root, "v1.6.0")).toBeGreaterThanOrEqual(
      40,
    );
  });

  it("uses explicit slug for greenfield when no existing match", () => {
    const root = join("/tmp", `beacon-feature-resolve-greenfield-${Date.now()}`);
    tmpRoots.push(root);
    mkdirSync(join(root, "docs/beacon"), { recursive: true });
    writeFileSync(join(root, "docs/beacon/VERSION"), "v1.6.0\n", "utf8");

    const resolved = resolveBeaconFeature({
      projectRoot: root,
      version: "v1.6.0",
      explicitFeature: "new-feature-smoke",
      utterance: "deliver a tiny smoke feature",
    });
    expect("ok" in resolved).toBe(false);
    if ("ok" in resolved) return;
    expect(resolved.feature).toBe("new-feature-smoke");
    expect(resolved.source).toBe("explicit");
  });
});
