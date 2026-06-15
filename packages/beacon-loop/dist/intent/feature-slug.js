import { slugify } from "../runner/types.js";

const CAPABILITY_PATTERNS = [
  { pattern: /\bchoose\b/i, token: "choose" },
  { pattern: /\bfilters?\b/i, token: "filter" },
  { pattern: /parity|完整|全量|full[- ]?parity/i, token: "parity" },
  { pattern: /\bcrud\b/i, token: "crud" },
  { pattern: /\bsmoke\b/i, token: "smoke" },
];

function capabilitySuffix(text) {
  const tokens = CAPABILITY_PATTERNS.filter((entry) => entry.pattern.test(text)).map((entry) => entry.token);
  return tokens.length ? tokens.join("-") : "feature";
}

export function inferFeatureSlugFromUtterance(utterance, explicitFeature = "") {
  if (explicitFeature) return slugify(explicitFeature);

  const text = String(utterance || "").trim();
  const quoted = text.match(/feature[=:\s]+([a-z0-9-]+)/i);
  if (quoted?.[1]) return slugify(quoted[1]);

  const pathMatch = text.match(/features\/([a-z0-9-]+)/i);
  if (pathMatch?.[1]) return slugify(pathMatch[1]);

  const codePath = text.match(
    /(?:examples|src|pkg|internal|cmd)\/([a-z0-9][a-z0-9._/-]*)/i,
  );
  if (codePath?.[1]) {
    const leaf = codePath[1].split("/").filter(Boolean).pop() || codePath[1];
    return slugify(`${leaf}-${capabilitySuffix(text)}`);
  }

  if (/^[a-z0-9][a-z0-9-]*$/i.test(text)) return slugify(text);

  const github = text.match(/github\.com\/[a-z0-9._-]+\/([a-z0-9._-]+)/i);
  if (github?.[1]) return slugify(`${github[1]}-${capabilitySuffix(text)}`);

  const slashRepo = text.match(/\b([a-z0-9._-]+)\/([a-z0-9][a-z0-9._-]*)\b/i);
  if (slashRepo?.[2] && slashRepo[2].length >= 2) {
    return slugify(`${slashRepo[2]}-${capabilitySuffix(text)}`);
  }

  const replica = text.match(/(?:复刻|对标|clone|replicate)\s+([a-z0-9._-]+)/i);
  if (replica?.[1]) return slugify(`${replica[1]}-${capabilitySuffix(text)}`);

  const named = text.match(/\b([a-z][a-z0-9_-]{1,24})\b\s*(?:的\s*)?(?:choose|filter)/i);
  if (named?.[1] && named[1].length >= 2) {
    return slugify(`${named[1]}-${capabilitySuffix(text)}`);
  }

  return "";
}
