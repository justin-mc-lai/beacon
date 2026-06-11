export type BeaconPhase = "truth" | "generate" | "repair" | "qa" | "release";

export type BeaconPhasePromptInput = {
  phase: BeaconPhase;
  feature?: string;
  version?: string;
  allowedHarness?: string[];
  forbiddenHarness?: string[];
};

const DEFAULT_ALLOWED: Record<BeaconPhase, string[]> = {
  truth: ["beacon truth-map resolve", "beacon change", "beacon doctor sync-materials"],
  generate: ["beacon implement run", "beacon doctor verify-context"],
  repair: ["beacon implement run", "beacon-gov-debug"],
  qa: ["beacon qa run", "beacon-eval-qa"],
  release: ["beacon release check", "beacon-eval-release"]
};

const DEFAULT_FORBIDDEN: string[] = [
  "direct truth.md rewrite without refreeze",
  "self-certified QA/release verdict",
  "subprocess Skill MD execution"
];

export function buildBeaconPhasePrompt(input: BeaconPhasePromptInput): string {
  const phase = input.phase;
  const allowed = input.allowedHarness?.length ? input.allowedHarness : DEFAULT_ALLOWED[phase];
  const forbidden = input.forbiddenHarness?.length ? input.forbiddenHarness : DEFAULT_FORBIDDEN;
  const lines = [
    `## Beacon phase: ${phase}`,
    input.feature ? `- feature: ${input.feature}` : "",
    input.version ? `- version: ${input.version}` : "",
    "- harness boundary: planner does not implement; generator does not self-certify; evaluator does not rewrite truth",
    `- allowed harness: ${allowed.join("; ")}`,
    `- forbidden: ${forbidden.join("; ")}`
  ].filter(Boolean);
  return lines.join("\n");
}

export function buildBeaconPhaseArtifact(input: BeaconPhasePromptInput) {
  return {
    schema_version: "1.0",
    phase: input.phase,
    feature: input.feature || "",
    version: input.version || "",
    prompt: buildBeaconPhasePrompt(input),
    allowed_harness: input.allowedHarness?.length ? input.allowedHarness : DEFAULT_ALLOWED[input.phase],
    forbidden_harness: input.forbiddenHarness?.length ? input.forbiddenHarness : DEFAULT_FORBIDDEN
  };
}
