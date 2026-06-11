export function augmentIterationPromptWithBeacon(
  basePrompt: string,
  phaseDigest: string,
  phaseObjective: string,
): string {
  return `${basePrompt}

## Beacon Harness Context

${phaseDigest}

## Beacon Phase Objective

${phaseObjective}

Follow the harness boundary above. Use allowed Beacon CLI commands when you need governed truth, implementation, QA, or release actions. Do not self-certify QA or release completion.`;
}
