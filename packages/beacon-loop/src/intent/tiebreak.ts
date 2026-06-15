import { join } from "node:path";
import { writeJson } from "../runner/fs.js";
import { nowIso, RUNTIME_ROLE } from "../runner/types.js";
import { inferFeatureSlugFromUtterance } from "./feature-slug.js";

export const TIE_BREAK_CONFIDENCE_THRESHOLD = 0.6;

export function needsIntentTieBreak(contract) {
  const confidence = Number(contract?.determinism?.confidence ?? 1);
  return Boolean(contract?.determinism?.ambiguous) || confidence < TIE_BREAK_CONFIDENCE_THRESHOLD;
}

function fixtureResolution(contract) {
  const utterance = String(contract?.utterance || "");
  const inferredFeature = contract.feature_slug
    || inferFeatureSlugFromUtterance(utterance)
    || (/\bdemo\b/i.test(utterance) ? "demo" : "");
  return {
    intent_class: contract.intent_class || "delivery_closed_loop",
    scope_mode: contract.scope_mode || "full_parity",
    feature_slug: inferredFeature,
    confidence: 0.72,
    rationale_summary: "fixture tie-break: default green-light continue"
  };
}

function defaultGreenLightResolution(contract) {
  const utterance = String(contract?.utterance || "");
  return {
    intent_class: contract.intent_class || "delivery_closed_loop",
    scope_mode: contract.scope_mode || "full_parity",
    feature_slug: contract.feature_slug || inferFeatureSlugFromUtterance(utterance),
    confidence: 0.7,
    rationale_summary: "default green-light tie-break: continue delivery without user interrupt"
  };
}

export function runIntentTieBreak(runDir, contract) {
  const rulesOutput = {
    intent_class: contract.intent_class,
    scope_mode: contract.scope_mode,
    feature_slug: contract.feature_slug,
    ambiguous: contract.determinism?.ambiguous,
    confidence: contract.determinism?.confidence,
    rules_hash: contract.determinism?.rules_hash
  };

  const llmResolution = process.env.BEACON_LOOP_TEST_TIEBREAK === "fixture"
    ? fixtureResolution(contract)
    : defaultGreenLightResolution(contract);

  const artifact = {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    generated_at: nowIso(),
    utterance: contract.utterance,
    rules_classifier_output: rulesOutput,
    llm_resolution: llmResolution,
    confidence: llmResolution.confidence,
    rationale_summary: llmResolution.rationale_summary,
    tiebreak_authority: "llm_default_green_light",
    runtime_evidence_only: true
  };

  writeJson(join(runDir, "intent-tiebreak.json"), artifact);

  const merged = {
    ...contract,
    intent_class: llmResolution.intent_class,
    scope_mode: llmResolution.scope_mode,
    feature_slug: llmResolution.feature_slug || contract.feature_slug,
    tiebreak: {
      authority: artifact.tiebreak_authority,
      artifact: "intent-tiebreak.json",
      applied_at: artifact.generated_at
    },
    determinism: {
      ...contract.determinism,
      ambiguous: false,
      confidence: llmResolution.confidence,
      tiebreak_applied: true
    }
  };

  return { artifact, contract: merged };
}
