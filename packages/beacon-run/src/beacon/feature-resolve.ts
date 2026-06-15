import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { featureTruthPath } from "./scope-mode.js";

export type FeatureResolveResult = {
  feature: string;
  source:
    | "explicit"
    | "explicit_existing"
    | "inferred_existing"
    | "matched_existing"
    | "inferred_greenfield";
  inferred?: string;
  matched_score?: number;
};

export type FeatureResolveFailure = {
  ok: false;
  error: string;
};

const CAPABILITY_PATTERNS = [
  { pattern: /\bchoose\b/i, token: "choose" },
  { pattern: /\bfilters?\b/i, token: "filter" },
  { pattern: /parity|完整|全量|full[- ]?parity/i, token: "parity" },
  { pattern: /\bcrud\b/i, token: "crud" },
  { pattern: /\bsmoke\b/i, token: "smoke" },
];

function slugify(value: string): string {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function capabilitySuffix(text: string): string {
  const tokens = CAPABILITY_PATTERNS.filter((entry) =>
    entry.pattern.test(text),
  ).map((entry) => entry.token);
  return tokens.length ? tokens.join("-") : "feature";
}

export function inferFeatureSlugFromUtterance(
  utterance: string,
  explicitFeature = "",
): string {
  if (explicitFeature) return slugify(explicitFeature);

  const text = String(utterance || "").trim();
  const quoted = text.match(/feature[=:\s]+([a-z0-9-]+)/i);
  if (quoted?.[1]) return slugify(quoted[1]);

  const pathMatch = text.match(/features\/([a-z0-9-]+)/i);
  if (pathMatch?.[1]) return slugify(pathMatch[1]);

  if (/^[a-z0-9][a-z0-9-]*$/i.test(text)) return slugify(text);

  const codePath = text.match(
    /(?:examples|src|pkg|internal|cmd)\/([a-z0-9][a-z0-9._/-]*)/i,
  );
  if (codePath?.[1]) {
    const leaf = codePath[1].split("/").filter(Boolean).pop() || codePath[1];
    return slugify(`${leaf}-${capabilitySuffix(text)}`);
  }

  const github = text.match(/github\.com\/[a-z0-9._-]+\/([a-z0-9._-]+)/i);
  if (github?.[1]) return slugify(`${github[1]}-${capabilitySuffix(text)}`);

  const slashRepo = text.match(/\b([a-z0-9._-]+)\/([a-z0-9][a-z0-9._-]*)\b/i);
  if (slashRepo?.[2] && slashRepo[2].length >= 2) {
    return slugify(`${slashRepo[2]}-${capabilitySuffix(text)}`);
  }

  return "";
}

export function listFeatureSlugs(
  projectRoot: string,
  version: string,
): string[] {
  const featuresDir = join(projectRoot, "docs/beacon", version, "features");
  if (!existsSync(featuresDir)) return [];
  return readdirSync(featuresDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((slug) => existsSync(featureTruthPath(projectRoot, version, slug)))
    .sort();
}

function tokenize(text: string): string[] {
  return [
    ...new Set(
      String(text || "")
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .filter((token) => token.length > 2),
    ),
  ];
}

export function scoreFeatureMatch(
  utterance: string,
  slug: string,
  projectRoot: string,
  version: string,
): number {
  const text = utterance.toLowerCase();
  const normalizedSlug = slug.toLowerCase();
  if (text.includes(normalizedSlug)) return 100;

  const slugStem = normalizedSlug.replace(/-(smoke|feature|parity)$/g, "");
  if (slugStem && text.includes(slugStem)) return 85;

  const pathMatches =
    text.match(/(?:examples|src|pkg|internal|cmd)\/[a-z0-9._/-]+/gi) || [];
  for (const rawPath of pathMatches) {
    const leaf = rawPath.split("/").filter(Boolean).pop() || "";
    const leafSlug = slugify(leaf);
    if (!leafSlug) continue;
    if (
      normalizedSlug.includes(leafSlug) ||
      leafSlug.includes(slugStem) ||
      normalizedSlug.startsWith(`${leafSlug}-`)
    ) {
      return 80;
    }
  }

  const utteranceTokens = tokenize(text);
  const slugTokens = normalizedSlug.split("-").filter((token) => token.length > 2);
  const overlap = slugTokens.filter((token) => utteranceTokens.includes(token));
  let score = overlap.length * 12;

  const truthPath = featureTruthPath(projectRoot, version, slug);
  if (existsSync(truthPath)) {
    const truthText = readFileSync(truthPath, "utf8").toLowerCase();
    for (const token of utteranceTokens) {
      if (truthText.includes(token)) score += 2;
    }
    for (const rawPath of pathMatches) {
      if (truthText.includes(rawPath.toLowerCase())) score += 15;
    }
  }

  return score;
}

export function resolveBeaconFeature(input: {
  projectRoot: string;
  version: string;
  explicitFeature?: string;
  utterance?: string;
}): FeatureResolveResult | FeatureResolveFailure {
  const projectRoot = input.projectRoot;
  const version = input.version;
  const utterance = String(input.utterance || "").trim();
  const explicit = slugify(String(input.explicitFeature || "").trim());
  const existing = listFeatureSlugs(projectRoot, version);
  const inferred = inferFeatureSlugFromUtterance(utterance, "");

  const bestMatch = existing
    .map((slug) => ({
      slug,
      score: scoreFeatureMatch(utterance, slug, projectRoot, version),
    }))
    .sort((a, b) => b.score - a.score)[0];

  if (explicit) {
    if (existing.includes(explicit)) {
      return { feature: explicit, source: "explicit_existing" };
    }
    if (bestMatch && bestMatch.score >= 40) {
      return {
        feature: bestMatch.slug,
        source: "matched_existing",
        inferred: explicit,
        matched_score: bestMatch.score,
      };
    }
    return { feature: explicit, source: "explicit" };
  }

  if (inferred && existing.includes(inferred)) {
    return { feature: inferred, source: "inferred_existing", inferred };
  }

  if (bestMatch && bestMatch.score >= 40) {
    return {
      feature: bestMatch.slug,
      source: "matched_existing",
      inferred: inferred || undefined,
      matched_score: bestMatch.score,
    };
  }

  if (inferred) {
    return { feature: inferred, source: "inferred_greenfield", inferred };
  }

  return {
    ok: false,
    error:
      "Beacon mode requires --feature <slug> or an utterance that resolves to a feature slug.",
  };
}
