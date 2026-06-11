import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

export type BeaconCliOptions = {
  beacon?: boolean;
  projectRoot?: string;
  version?: string;
  feature?: string;
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
  const feature = String(options.feature || "").trim();

  if (!version) {
    return {
      ok: false,
      error:
        "Beacon mode requires --beacon-version or docs/beacon/VERSION in the project root.",
    };
  }
  if (!feature) {
    return {
      ok: false,
      error: "Beacon mode requires --feature <slug>.",
    };
  }

  const truthBootstrap =
    options.truthBootstrap === "fallback" ? "fallback" : "agent";

  return {
    ok: true,
    ctx: {
      enabled: true,
      projectRoot,
      version,
      feature,
      truthBootstrap,
      implementRunner:
        options.implementRunner ||
        process.env.BEACON_RUN_IMPLEMENT_RUNNER ||
        "codex-subagents",
    },
  };
}
