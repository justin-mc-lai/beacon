import type { RepairKind } from "./repair-routing.js";

export type BeaconPhase = "truth" | "generate" | "repair" | "qa" | "release";

export type BeaconPhasePromptInput = {
  phase: BeaconPhase;
  feature?: string;
  version?: string;
  repairKind?: RepairKind;
  allowedHarness?: string[];
  forbiddenHarness?: string[];
};

const DEFAULT_ALLOWED: Record<BeaconPhase, string[]> = {
  truth: [
    "beacon truth-map resolve",
    "beacon change",
    "beacon doctor sync-materials",
    "beacon doctor sync-requirement-clarity",
    "beacon freeze",
    "beacon truth-cutover run",
  ],
  generate: ["beacon implement run", "beacon doctor verify-context"],
  repair: ["beacon implement run", "beacon-gov-debug"],
  qa: ["beacon qa run", "beacon-eval-qa"],
  release: ["beacon release check", "beacon-eval-release"]
};

const GOVERNANCE_REPAIR_ALLOWED = [
  "beacon change",
  "beacon-gov-doctor",
  "beacon doctor sync-version-surfaces",
  "beacon doctor verify-version-surfaces",
  "beacon qa run",
  "beacon truth-cutover run",
];

const DEFAULT_FORBIDDEN: string[] = [
  "direct truth.md rewrite without refreeze",
  "self-certified QA/release verdict",
  "subprocess Skill MD execution"
];

function resolveAllowedHarness(input: BeaconPhasePromptInput): string[] {
  if (input.allowedHarness?.length) return input.allowedHarness;
  if (input.phase === "repair" && input.repairKind === "governance") {
    return GOVERNANCE_REPAIR_ALLOWED;
  }
  return DEFAULT_ALLOWED[input.phase];
}

export function buildBeaconPhasePrompt(input: BeaconPhasePromptInput): string {
  const phase = input.phase;
  const allowed = resolveAllowedHarness(input);
  const forbidden = input.forbiddenHarness?.length ? input.forbiddenHarness : DEFAULT_FORBIDDEN;
  const repairNote =
    phase === "repair" && input.repairKind === "governance"
      ? "- repair route: governance/change (infrastructure blockers — do not rewrite product code)"
      : phase === "repair"
        ? "- repair route: implementation (product code defects only)"
        : "";
  const lines = [
    `## Beacon phase: ${phase}`,
    input.feature ? `- feature: ${input.feature}` : "",
    input.version ? `- version: ${input.version}` : "",
    "- harness boundary: planner does not implement; generator does not self-certify; evaluator does not rewrite truth",
    repairNote,
    `- allowed harness: ${allowed.join("; ")}`,
    `- forbidden: ${forbidden.join("; ")}`
  ].filter(Boolean);
  return lines.join("\n");
}

export function buildBeaconPhaseArtifact(input: BeaconPhasePromptInput) {
  const allowed = resolveAllowedHarness(input);
  return {
    schema_version: "1.0",
    phase: input.phase,
    feature: input.feature || "",
    version: input.version || "",
    ...(input.repairKind ? { repair_kind: input.repairKind } : {}),
    prompt: buildBeaconPhasePrompt(input),
    allowed_harness: allowed,
    forbidden_harness: input.forbiddenHarness?.length ? input.forbiddenHarness : DEFAULT_FORBIDDEN
  };
}
