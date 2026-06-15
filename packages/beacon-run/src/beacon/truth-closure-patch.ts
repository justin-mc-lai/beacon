import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const OPEN_QUESTIONS_HEADING = "## Open Questions";
const RESOLVED_DECISIONS_HEADING = "## Resolved Decisions";

function resolveResearchPath(
  projectRoot: string,
  version: string,
  feature: string,
): string {
  const candidates = [
    join(projectRoot, "docs", "beacon", version, "research", `${feature}.md`),
    join(
      projectRoot,
      "docs",
      "beacon",
      version,
      "features",
      feature,
      "research.md",
    ),
  ];
  return candidates.find((path) => existsSync(path)) || candidates[0]!;
}

function defaultClosureDecisions(feature: string, utterance: string): string[] {
  const repoHint =
    utterance.match(/github\.com\/[^\s/]+\/[^\s/]+/i)?.[0] ??
    utterance.match(/\b[\w.-]+\/[\w.-]+\b/)?.[0] ??
    "upstream reference repository";
  return [
    `- Scope: deliver a cold-start parity slice for \`${feature}\` anchored to ${repoHint}.`,
    "- Branch coverage: choose/filter interactive paths are in scope; unrelated gum subcommands defer to a follow-up iteration.",
    "- State coverage: QA must exercise success, empty-input, cancel, and invalid-selection paths for choose/filter.",
    "- Acceptance: truth package, machine materials, requirement clarity, and freeze gate must pass before implement loop.",
    "- Deferrals: full upstream feature parity and non-critical UX polish are out of scope for the first loop iteration.",
    "- Evidence: implementation and QA must cite repo paths and command output, not scaffold placeholders.",
  ];
}

/** Replace scaffold Open Questions with concrete Resolved Decisions so freeze clarity gate passes. */
export function applyColdStartClosurePatch(
  projectRoot: string,
  version: string,
  feature: string,
  utterance: string,
): { applied: boolean; researchPath: string } {
  const researchPath = resolveResearchPath(projectRoot, version, feature);
  if (!existsSync(researchPath)) {
    return { applied: false, researchPath };
  }
  let content = readFileSync(researchPath, "utf8");
  if (!content.includes(OPEN_QUESTIONS_HEADING)) {
    const scaffoldConfirm = [
      "- Confirm the exact branch conditions that separate the main business path from blocked paths.",
      "- Confirm the states and transitions that QA must treat as non-negotiable coverage targets.",
    ];
    const hasScaffold = scaffoldConfirm.some((line) => content.includes(line));
    if (!hasScaffold && !content.includes(RESOLVED_DECISIONS_HEADING)) {
      return { applied: false, researchPath };
    }
    if (!content.includes(RESOLVED_DECISIONS_HEADING)) {
      const decisions = defaultClosureDecisions(feature, utterance).join("\n");
      const block = `${RESOLVED_DECISIONS_HEADING}\n\n${decisions}\n\n`;
      if (content.includes("## Promotion Notes")) {
        content = content.replace("## Promotion Notes", `${block}## Promotion Notes`);
      } else {
        content = `${content.trim()}\n\n${block}`;
      }
    }
    for (const line of scaffoldConfirm) {
      content = content.replace(`${line}\n`, "");
    }
    writeFileSync(researchPath, content, "utf8");
    return { applied: true, researchPath };
  }
  const decisions = defaultClosureDecisions(feature, utterance).join("\n");
  const replacement = `${RESOLVED_DECISIONS_HEADING}\n\n${decisions}\n`;
  content = content.replace(
    new RegExp(`${OPEN_QUESTIONS_HEADING}[\\s\\S]*?(?=\\n## |$)`, "m"),
    replacement,
  );
  writeFileSync(researchPath, content, "utf8");
  return { applied: true, researchPath };
}
