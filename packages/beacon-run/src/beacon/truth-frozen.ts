import { existsSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { featureTruthPath } from "./scope-mode.js";

export type ResolvePayload = {
  blocked?: boolean;
  status?: string;
  feature_truth?: {
    frontmatter?: { status?: string };
    truth_frontmatter?: { status?: string };
  };
};

export function readTruthFrontmatterStatus(
  projectRoot: string,
  version: string,
  feature: string,
): string {
  const path = featureTruthPath(projectRoot, version, feature);
  if (!existsSync(path)) return "";
  const text = readFileSync(path, "utf8");
  const match = text.match(/^---[\s\S]*?^status:\s*(\S+)/m);
  return match?.[1] || "";
}

export function isFeatureTruthFrozenFromPayload(
  projectRoot: string,
  version: string,
  feature: string,
  payload: ResolvePayload | null | undefined,
  blocked = false,
): boolean {
  if (blocked || payload?.blocked) return false;
  const featureTruth = payload?.feature_truth || {};
  const frontmatterStatus = String(
    featureTruth.truth_frontmatter?.status ||
      featureTruth.frontmatter?.status ||
      "",
  );
  if (frontmatterStatus === "frozen") return true;
  if (frontmatterStatus && frontmatterStatus !== "frozen") return false;
  const storyPath = join(
    projectRoot,
    "docs/beacon",
    version,
    ".machine/user-story",
    `${feature}.json`,
  );
  if (existsSync(storyPath)) {
    try {
      const story = JSON.parse(readFileSync(storyPath, "utf8")) as {
        lifecycle_status?: string;
        current_revision?: { status?: string };
      };
      if (
        story.lifecycle_status === "frozen" ||
        story.current_revision?.status === "frozen"
      ) {
        return true;
      }
    } catch {
      /* ignore */
    }
  }
  return readTruthFrontmatterStatus(projectRoot, version, feature) === "frozen";
}

export function parseHarnessJsonReason(result: {
  stdout: string;
}): string {
  try {
    const payload = JSON.parse(result.stdout) as {
      reason_code?: string;
      blocked_reason?: string;
      result?: { reason_code?: string };
    };
    return (
      payload.reason_code ||
      payload.blocked_reason ||
      payload.result?.reason_code ||
      ""
    );
  } catch {
    return "";
  }
}

export function resolveFeatureTruthState(
  projectRoot: string,
  version: string,
  feature: string,
): {
  frozen: boolean;
  result: { command: string; exit_code: number; stdout: string; stderr: string };
  payload: ResolvePayload | null;
} {
  const args = [
    "truth-map",
    "resolve",
    feature,
    "--project",
    projectRoot,
    "--version",
    version,
    "--json",
  ];
  const command = `beacon ${args.join(" ")}`;
  if (process.env.BEACON_RUN_MOCK_HARNESS === "1") {
    const status = readTruthFrontmatterStatus(projectRoot, version, feature);
    const payload: ResolvePayload = {
      status: "resolved",
      feature_truth: { frontmatter: { status } },
    };
    return {
      frozen: status === "frozen",
      result: {
        command,
        exit_code: 0,
        stdout: JSON.stringify(payload),
        stderr: "",
      },
      payload,
    };
  }
  const spawned = spawnSync("beacon", args, {
    cwd: projectRoot,
    encoding: "utf-8",
    env: process.env,
  });
  const result = {
    command,
    exit_code: spawned.status ?? 1,
    stdout: String(spawned.stdout || ""),
    stderr: String(spawned.stderr || ""),
  };
  if (result.exit_code !== 0) {
    return { frozen: false, result, payload: null };
  }
  try {
    const payload = JSON.parse(result.stdout) as ResolvePayload;
    const blocked = payload.blocked === true || payload.status === "blocked";
    return {
      frozen: isFeatureTruthFrozenFromPayload(
        projectRoot,
        version,
        feature,
        payload,
        blocked,
      ),
      result,
      payload,
    };
  } catch {
    return { frozen: false, result, payload: null };
  }
}

export function isFeatureTruthFrozen(
  projectRoot: string,
  version: string,
  feature: string,
): boolean {
  return resolveFeatureTruthState(projectRoot, version, feature).frozen;
}
