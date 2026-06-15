import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
  resolveBeaconFeature,
  type FeatureResolveResult,
} from "./feature-resolve.js";

export type BeaconCliOptions = {
  beacon?: boolean;
  projectRoot?: string;
  version?: string;
  feature?: string;
  utterance?: string;
  truthBootstrap?: "agent" | "fallback";
  implementRunner?: string;
};

export function readBeaconVersionFile(projectRoot: string): string | undefined {
  const versionPath = join(projectRoot, "docs/beacon/VERSION");
  if (!existsSync(versionPath)) return undefined;
  const value = readFileSync(versionPath, "utf-8").trim();
  return value || undefined;
}

export function resolveBeaconRunContext(
  cwd: string,
  options: BeaconCliOptions,
): { ok: true; ctx: import("./phase-controller.js").BeaconRunContext } | { ok: false; error: string } {
  if (!options.beacon) {
    return { ok: false, error: "beacon mode disabled" };
  }

  const projectRoot = options.projectRoot || cwd;
  const version = options.version || readBeaconVersionFile(projectRoot);

  if (!version) {
    return {
      ok: false,
      error:
        "Beacon mode requires --beacon-version or docs/beacon/VERSION in the project root.",
    };
  }

  const resolved = resolveBeaconFeature({
    projectRoot,
    version,
    explicitFeature: options.feature,
    utterance: options.utterance,
  });
  if ("ok" in resolved) {
    return { ok: false, error: resolved.error };
  }
  const featureResolution: FeatureResolveResult = resolved;

  const truthBootstrap =
    options.truthBootstrap === "fallback" ? "fallback" : "agent";

  return {
    ok: true,
    ctx: {
      enabled: true,
      projectRoot,
      version,
      feature: featureResolution.feature,
      featureResolution,
      truthBootstrap,
      implementRunner:
        options.implementRunner ||
        process.env.BEACON_RUN_IMPLEMENT_RUNNER ||
        "codex-subagents",
    },
  };
}
