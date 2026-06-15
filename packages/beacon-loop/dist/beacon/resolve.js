import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { run } from "../git/git.js";

const REQUIRED_SURFACES = ["truth", "tests"];

function surfaceMissing(projectRoot, featureTruth, key) {
  const surfaces = featureTruth?.surfaces || {};
  const surface = surfaces[key];
  if (surface && typeof surface === "object" && "exists" in surface) {
    return !surface.exists;
  }
  const path = String(featureTruth?.source_paths?.[key] || "").trim();
  if (!path) return true;
  if (!Object.keys(surfaces).length) {
    return false;
  }
  return !existsSync(join(projectRoot, path));
}

export function packageSurfacesMissing(projectRoot, payload) {
  const featureTruth = payload?.feature_truth || {};
  return REQUIRED_SURFACES.some((key) => surfaceMissing(projectRoot, featureTruth, key));
}

function readStoryLifecycleStatus(projectRoot, version, feature) {
  const path = join(projectRoot, "docs", "beacon", version, ".machine", "user-story", `${feature}.json`);
  if (!existsSync(path)) {
    return "";
  }
  try {
    const payload = JSON.parse(readFileSync(path, "utf8"));
    return String(payload.lifecycle_status || payload.current_revision?.status || "");
  } catch {
    return "";
  }
}

export function isFeatureTruthFrozen(projectRoot, version, feature, resolver) {
  if (resolver?.blocked) {
    return false;
  }
  const featureTruth = resolver?.payload?.feature_truth || {};
  const frontmatterStatus = String(
    featureTruth.truth_frontmatter?.status
    || featureTruth.frontmatter?.status
    || ""
  );
  if (frontmatterStatus === "frozen") {
    return true;
  }
  if (projectRoot && version && feature) {
    return readStoryLifecycleStatus(projectRoot, version, feature) === "frozen";
  }
  return false;
}

export function resolveTruth(projectRoot, version, feature) {
  const args = ["truth-map", "resolve", feature, "--project", projectRoot, "--version", version, "--json"];
  const command = `beacon ${args.join(" ")}`;
  const result = run("beacon", args, { cwd: projectRoot });
  if (result.code !== 0) {
    return {
      status: "blocked",
      blocked: true,
      reason_code: "beacon_truth_resolver_failed",
      command,
      stderr: result.stderr,
      stdout: result.stdout,
      next_route: "beacon-gen-change"
    };
  }
  try {
    const payload = JSON.parse(result.stdout);
    const featureTruth = payload?.feature_truth || {};
    const missing = REQUIRED_SURFACES.filter((key) => surfaceMissing(projectRoot, featureTruth, key));
    const statusBlocked = String(featureTruth.status || payload?.status || "") === "blocked";
    const frontmatterErrors = Array.isArray(featureTruth.frontmatter_errors) ? featureTruth.frontmatter_errors : [];
    const blocked =
      missing.length > 0
      || statusBlocked
      || Boolean(payload?.blocked)
      || (frontmatterErrors.length > 0 && packageSurfacesMissing(projectRoot, payload));
    return {
      status: blocked ? "blocked" : "pass",
      blocked,
      reason_code: blocked ? (missing.length ? "beacon_truth_package_gap" : "beacon_truth_resolver_blocked") : "",
      command,
      payload,
      source_paths: featureTruth.source_paths || {},
      next_route: blocked ? "beacon-gen-change" : "",
      frozen: isFeatureTruthFrozen(projectRoot, version, feature, { blocked, payload })
    };
  } catch (error) {
    return {
      status: "blocked",
      blocked: true,
      reason_code: "beacon_truth_resolver_json_invalid",
      command,
      stderr: String(error),
      stdout: result.stdout,
      next_route: "beacon-gen-change"
    };
  }
}
