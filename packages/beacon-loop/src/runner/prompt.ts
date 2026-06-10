import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

export function loadNotes(runDir) {
  const notesPath = join(runDir, "notes.md");
  if (!existsSync(notesPath)) return "# Notes\n\n";
  return readFileSync(notesPath, "utf8");
}

export function buildIterationPrompt(runPackage, refs, iteration, notes) {
  return `Beacon loop implementation iteration ${iteration}.

Goal: ${runPackage.goal}
Feature: ${runPackage.feature}
Version: ${runPackage.version}
Iteration: ${iteration} of ${runPackage.max_iterations}
Truth refs: ${(refs.truth_refs || []).join(", ")}
Test refs: ${(refs.test_refs || []).join(", ")}
Stop when: ${runPackage.stop_when}

Accumulated notes:
${notes}

Emit JSON with: success, summary, key_changes_made, key_learnings.
Do not claim QA pass, release readiness, or feature completion.`;
}
