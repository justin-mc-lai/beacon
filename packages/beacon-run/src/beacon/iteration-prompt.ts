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

Follow the harness boundary above. Use allowed Beacon CLI commands when you need governed truth, implementation, QA, or release actions. Do not self-certify QA or release completion.

## Beacon Output Contract

- Your final message must include a JSON object that matches output-schema.json for this run (all required keys, including should_fully_stop).
- Set should_fully_stop=true only when the Beacon Phase Objective above is fully met for this iteration; otherwise set it to false.
- End with the raw JSON object as the final answer when possible. Do not omit required keys even if you also include explanatory prose.`;
}
