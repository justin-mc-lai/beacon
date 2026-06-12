import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { inferFeatureSlugFromUtterance } from "./feature-slug.js";

function featureTruthPath(projectRoot, version, feature) {
  return join(projectRoot, "docs/beacon", version, "features", feature, "truth.md");
}

function listFeatureSlugs(projectRoot, version) {
  const featuresDir = join(projectRoot, "docs/beacon", version, "features");
  if (!existsSync(featuresDir)) return [];
  return readdirSync(featuresDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((slug) => existsSync(featureTruthPath(projectRoot, version, slug)))
    .sort();
}

function tokenize(text) {
  return [
    ...new Set(
      String(text || "")
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .filter((token) => token.length > 2),
    ),
  ];
}

function scoreFeatureMatch(utterance, slug, projectRoot, version) {
  const text = utterance.toLowerCase();
  const normalizedSlug = slug.toLowerCase();
  if (text.includes(normalizedSlug)) return 100;

  const slugStem = normalizedSlug.replace(/-(smoke|feature|parity)$/g, "");
  if (slugStem && text.includes(slugStem)) return 85;

  const pathMatches =
    text.match(/(?:examples|src|pkg|internal|cmd)\/[a-z0-9._/-]+/gi) || [];
  for (const rawPath of pathMatches) {
    const leaf = rawPath.split("/").filter(Boolean).pop() || "";
    const leafSlug = leaf.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    if (
      leafSlug &&
      (normalizedSlug.includes(leafSlug) ||
        leafSlug.includes(slugStem) ||
        normalizedSlug.startsWith(`${leafSlug}-`))
    ) {
      return 80;
    }
  }

  const utteranceTokens = tokenize(text);
  const slugTokens = normalizedSlug.split("-").filter((token) => token.length > 2);
  let score = slugTokens.filter((token) => utteranceTokens.includes(token)).length * 12;

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

export function resolveDelegateFeature(projectRoot, version, goal, explicitFeature = "") {
  const explicit = String(explicitFeature || "").trim();
  const utterance = String(goal || "").trim();
  const existing = listFeatureSlugs(projectRoot, version);
  const inferred = inferFeatureSlugFromUtterance(utterance, "");

  const bestMatch = existing
    .map((slug) => ({
      slug,
      score: scoreFeatureMatch(utterance, slug, projectRoot, version),
    }))
    .sort((a, b) => b.score - a.score)[0];

  if (explicit) {
    const normalized = explicit.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    if (existing.includes(normalized)) return normalized;
    if (bestMatch && bestMatch.score >= 40) return bestMatch.slug;
    return normalized;
  }
  if (inferred && existing.includes(inferred)) return inferred;
  if (bestMatch && bestMatch.score >= 40) return bestMatch.slug;
  return inferred || "";
}
