import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

export type FeatureScopeMode = "smoke" | "full_parity" | "unknown";

export function featureTruthPath(
  projectRoot: string,
  version: string,
  feature: string,
): string {
  return join(projectRoot, "docs/beacon", version, "features", feature, "truth.md");
}

export function readFeatureScopeMode(
  projectRoot: string,
  version: string,
  feature: string,
): FeatureScopeMode {
  const path = featureTruthPath(projectRoot, version, feature);
  if (!existsSync(path)) return "unknown";
  const text = readFileSync(path, "utf8");
  if (/scope_mode\s*[=:]\s*[`\*]*smoke/i.test(text)) return "smoke";
  if (/scope_mode\s*[=:]\s*[`\*]*full_parity/i.test(text)) return "full_parity";
  return "unknown";
}

export function smokeTruthPackageReady(
  projectRoot: string,
  version: string,
  feature: string,
): boolean {
  const path = featureTruthPath(projectRoot, version, feature);
  if (!existsSync(path)) return false;
  const text = readFileSync(path, "utf8")
    .replace(/^---[\s\S]*?---\s*/m, "")
    .trim();
  return text.length > 80;
}
