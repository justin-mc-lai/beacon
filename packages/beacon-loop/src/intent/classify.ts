import { CLASSIFIER_ID, rulesHash } from "./rules.js";
import { slugify } from "../runner/types.js";

const DELIVERY_SIGNALS = ["闭环", "交付", "验收", "release", "truth", "delivery", "closed loop", "closed-loop"];
const FULL_PARITY_SIGNALS = ["完整", "全量", "parity", "不要mvp", "full parity", "full_parity"];
const PATCH_SIGNALS = ["hotfix", "bug", "修复", "patch"];
const RESEARCH_SIGNALS = ["调研", "探索", "brainstorm", "research"];

function lower(text) {
  return String(text || "").toLowerCase();
}

function hasAny(text, signals) {
  const hay = lower(text);
  return signals.some((signal) => hay.includes(lower(signal)));
}

function extractFeatureSlug(utterance, explicitFeature) {
  if (explicitFeature) return slugify(explicitFeature);
  const quoted = utterance.match(/feature[=:\s]+([a-z0-9-]+)/i);
  if (quoted?.[1]) return slugify(quoted[1]);
  const pathMatch = utterance.match(/features\/([a-z0-9-]+)/i);
  if (pathMatch?.[1]) return slugify(pathMatch[1]);
  const token = String(utterance || "").trim();
  if (/^[a-z0-9][a-z0-9-]*$/i.test(token)) return slugify(token);
  return "";
}

export function classifyIntent(utterance, options = {}) {
  const text = String(utterance || "").trim();
  const explicitFeature = String(options.feature || "").trim();
  const mode = options.mode || "delivery";
  let intentClass = "delivery_closed_loop";
  let scopeMode = "full_parity";
  let ambiguous = false;

  if (mode === "execute-only") {
    intentClass = "execute_bound";
    scopeMode = "full_parity";
  } else if (hasAny(text, RESEARCH_SIGNALS)) {
    intentClass = "research";
    scopeMode = "research";
  } else if (hasAny(text, PATCH_SIGNALS)) {
    intentClass = "patch";
    scopeMode = "patch";
  } else if (hasAny(text, DELIVERY_SIGNALS) || mode === "delivery") {
    intentClass = "delivery_closed_loop";
    scopeMode = hasAny(text, FULL_PARITY_SIGNALS) ? "full_parity" : "full_parity";
  }

  const featureSlug = extractFeatureSlug(text, explicitFeature);
  if (!featureSlug && (mode === "execute-only" || intentClass === "execute_bound")) {
    ambiguous = true;
  }
  if (!featureSlug && intentClass === "delivery_closed_loop" && !explicitFeature) {
    ambiguous = !/beacon-loop|orchestrator|goal/i.test(text);
  }

  const capabilityRequests = [];
  if (hasAny(text, DELIVERY_SIGNALS)) capabilityRequests.push("delivery_closed_loop");
  if (hasAny(text, FULL_PARITY_SIGNALS)) capabilityRequests.push("full_parity");

  return {
    schema_version: "1.0",
    utterance: text,
    intent_class: intentClass,
    scope_mode: scopeMode,
    closure_shape: {
      requires_truth: intentClass !== "research",
      requires_implementation: intentClass !== "research",
      requires_qa: intentClass === "delivery_closed_loop",
      requires_release: intentClass === "delivery_closed_loop"
    },
    capability_requests: capabilityRequests,
    strong_intent_signals: capabilityRequests,
    feature_slug: featureSlug,
    version: options.version || "v1.6.0",
    determinism: {
      classifier: CLASSIFIER_ID,
      rules_hash: rulesHash(),
      confidence: ambiguous ? 0.4 : 0.85,
      ambiguous
    }
  };
}
