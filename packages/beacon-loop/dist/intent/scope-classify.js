const SEA_SIGNALS = [
  "全功能",
  "完整复刻",
  "full parity",
  "full_parity",
  "多模块",
  "program",
  "sea",
  "ocean",
  "海",
  "整站",
  "multi-lake",
  "多湖",
];

const LAKE_SIGNALS = [
  "单 feature",
  "single feature",
  "本 package",
  "单湖",
  "lake",
  "湖",
  "one feature",
  "this feature",
];

function lower(text) {
  return String(text || "").toLowerCase();
}

function scoreSignals(text, signals) {
  const hay = lower(text);
  return signals.reduce(
    (count, signal) => count + (hay.includes(lower(signal)) ? 1 : 0),
    0,
  );
}

function normalizeLakeOrOcean(value) {
  const v = String(value || "").trim().toLowerCase();
  if (v === "湖" || v === "lake") return "湖";
  if (v === "海" || v === "sea" || v === "ocean") return "海";
  return "";
}

/**
 * Classify utterance scope as 湖 (single-lake delivery) or 海 (program outer FSM).
 * UD-007: low confidence requires one MCQ unless `--lake-or-ocean` override provided.
 */
export function classifyLakeOrOcean(utterance, options = {}) {
  const text = String(utterance || "").trim();
  const override = normalizeLakeOrOcean(options.lakeOrOcean);
  if (override) {
    return {
      lake_or_ocean: override,
      confidence: 100,
      ambiguous: false,
      reason: "cli_override",
      recommended_mode: override === "海" ? "program" : "delivery",
    };
  }

  const mcqAnswer = normalizeLakeOrOcean(options.mcqAnswer || process.env.BEACON_LOOP_SCOPE_MCQ);
  if (mcqAnswer) {
    return {
      lake_or_ocean: mcqAnswer,
      confidence: 95,
      ambiguous: false,
      reason: "mcq_answer",
      recommended_mode: mcqAnswer === "海" ? "program" : "delivery",
      tiebreak: { method: "mcq", answer: mcqAnswer },
    };
  }

  const seaScore = scoreSignals(text, SEA_SIGNALS);
  const lakeScore = scoreSignals(text, LAKE_SIGNALS);

  if (seaScore > lakeScore && seaScore >= 1) {
    return {
      lake_or_ocean: "海",
      confidence: Math.min(60 + seaScore * 15, 95),
      ambiguous: false,
      reason: "sea_signals",
      recommended_mode: "program",
    };
  }
  if (lakeScore > seaScore && lakeScore >= 1) {
    return {
      lake_or_ocean: "湖",
      confidence: Math.min(60 + lakeScore * 15, 95),
      ambiguous: false,
      reason: "lake_signals",
      recommended_mode: "delivery",
    };
  }

  return {
    lake_or_ocean: "湖",
    confidence: 35,
    ambiguous: true,
    reason: "low_confidence_needs_one_question",
    recommended_mode: "delivery",
    mcq: {
      prompt: "Scope ambiguous: is this a single-lake delivery (湖) or sea-level program (海)?",
      options: [
        { id: "lake", label: "湖 — single feature/package delivery", maps_to: "湖" },
        { id: "sea", label: "海 — program with multiple lakes", maps_to: "海" },
      ],
    },
  };
}

export function resolveDeliveryMode(scope, explicitMode) {
  const mode = String(explicitMode || "").trim().toLowerCase();
  if (mode === "program" || mode === "delivery") {
    return mode;
  }
  if (scope.lake_or_ocean === "海") {
    return "program";
  }
  return "delivery";
}

export function buildScopeIntentContract(utterance, scope, options = {}) {
  return {
    schema_version: "1.0",
    utterance,
    lake_or_ocean: scope.lake_or_ocean,
    scope_classification: scope,
    delivery_mode: resolveDeliveryMode(scope, options.mode),
    program_slug: options.program || "",
    version: options.version || "v1.6.1",
    determinism: {
      ambiguous: scope.ambiguous === true,
      confidence: scope.confidence,
      classifier: "beacon-loop-scope-v161",
    },
    ...(scope.tiebreak ? { tiebreak: scope.tiebreak } : {}),
    ...(scope.mcq && scope.ambiguous ? { mcq: scope.mcq } : {}),
  };
}
