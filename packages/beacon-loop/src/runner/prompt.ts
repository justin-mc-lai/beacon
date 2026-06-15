import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

export function loadNotes(runDir) {
  const notesPath = join(runDir, "notes.md");
  if (!existsSync(notesPath)) return "# Notes\n\n";
  return readFileSync(notesPath, "utf8");
}

export function buildGnhfIterationPrompt({ n, runId, prompt, stopWhen = "", notesPath = "notes.md" }) {
  const outputFields = [
    "- success: whether you made meaningful progress. A complete no-op (no file changes AND no new meaningful learnings) is NOT success — set success=false",
    "- summary: one-sentence summary of this iteration",
    "- key_changes_made: array of logical units of work (not grouped by file)",
    "- key_learnings: array of surprising learnings not already in notes"
  ];
  if (stopWhen) {
    outputFields.push("- should_fully_stop: true ONLY when the stop condition is fully met; default false");
  }

  const stopSection = stopWhen
    ? `\n\n## Stop Condition\n\n${stopWhen}\nIf fully met, set should_fully_stop=true. Otherwise false.`
    : "";

  return `You are working autonomously towards an objective given below.
This is iteration ${n}. Each iteration makes incremental progress, not the entire objective.

## Instructions

1. Read ${notesPath} first for prior iteration context. Do NOT modify notes.md — the orchestrator maintains it
2. Pick the next smallest verifiable unit of work toward the objective
3. If work did not move the needle, record success=false with learnings rather than spinning
4. Run build/tests/linters if available. Do NOT git commit — the orchestrator commits automatically
5. Stop background processes before finishing
6. Emit final JSON only after validation is complete

## Output

${outputFields.join("\n")}${stopSection}

## Objective

${prompt}

Do not claim QA pass, release readiness, or feature completion.`;
}

export function buildIterationPrompt(runPackage, refs, iteration, notes, runId = "") {
  const objective = [
    `Goal: ${runPackage.goal}`,
    `Feature: ${runPackage.feature}`,
    `Version: ${runPackage.version}`,
    `Truth refs: ${(refs.truth_refs || runPackage.truth_refs || []).join(", ")}`,
    `Test refs: ${(refs.test_refs || runPackage.test_refs || []).join(", ")}`,
    "",
    "Accumulated notes:",
    notes
  ].join("\n");

  return buildGnhfIterationPrompt({
    n: iteration,
    runId: runId || runPackage.run_id || "run",
    prompt: objective,
    stopWhen: runPackage.stop_when || "",
    notesPath: `.beacon/loop/runs/${runPackage.run_id || runId}/notes.md`
  });
}
