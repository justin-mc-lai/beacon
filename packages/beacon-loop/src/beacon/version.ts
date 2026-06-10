import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const VERSION_DIR_RE = /^v\d+\.\d+\.\d+$/;

function readOnboardingDocsVersion(projectRoot) {
  const path = join(projectRoot, ".beacon", "state", "project-onboarding.json");
  if (!existsSync(path)) {
    return null;
  }
  try {
    const payload = JSON.parse(readFileSync(path, "utf8"));
    const candidate = payload.docs_version ?? payload.version;
    return typeof candidate === "string" && candidate.trim() ? candidate.trim() : null;
  } catch {
    return null;
  }
}

function latestDocsVersion(projectRoot) {
  const docsRoot = join(projectRoot, "docs", "beacon");
  if (!existsSync(docsRoot)) {
    return null;
  }
  const versions = readdirSync(docsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && VERSION_DIR_RE.test(entry.name))
    .map((entry) => entry.name)
    .sort((left, right) => left.localeCompare(right, undefined, { numeric: true }));
  return versions.at(-1) ?? null;
}

/** Resolve Beacon docs/runtime version for a project (align loop with init-created docs). */
export function resolveProjectVersion(projectRoot, requested) {
  const normalized = String(requested ?? "auto").trim();
  if (normalized && normalized !== "auto") {
    return normalized;
  }
  return readOnboardingDocsVersion(projectRoot) ?? latestDocsVersion(projectRoot) ?? "v1.6.0";
}
