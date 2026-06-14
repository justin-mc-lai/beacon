import { basename, dirname, join } from "node:path";
import { existsSync, readdirSync, statSync } from "node:fs";
import { readJson, latestRunId } from "../runner/fs.js";
import { ledgerDbPath, sqliteAvailable } from "../ledger/db.js";

const BEACON_PHASES = ["truth", "generate", "qa", "release", "repair"];

function collectGnhfRuns(root, relRoot) {
  const entries = [];
  const runsRoot = join(root, ".gnhf", "runs");
  if (!existsSync(runsRoot)) return entries;
  for (const runId of readdirSync(runsRoot)) {
    const absRunDir = join(runsRoot, runId);
    try {
      if (!statSync(absRunDir).isDirectory()) continue;
    } catch {
      continue;
    }
    entries.push({
      run_id: runId,
      run_dir: join(relRoot, ".gnhf", "runs", runId),
      abs_run_dir: absRunDir,
    });
  }
  return entries;
}

function listGnhfRunDirs(projectRoot) {
  const dirs = collectGnhfRuns(projectRoot, ".");
  const worktreesRoot = join(
    dirname(projectRoot),
    `${basename(projectRoot)}-gnhf-worktrees`,
  );
  if (existsSync(worktreesRoot)) {
    for (const entry of readdirSync(worktreesRoot)) {
      const wtPath = join(worktreesRoot, entry);
      try {
        if (!statSync(wtPath).isDirectory()) continue;
      } catch {
        continue;
      }
      dirs.push(...collectGnhfRuns(wtPath, wtPath));
    }
  }

  return dirs.sort((a, b) => {
    const aPhase = join(a.abs_run_dir, "beacon-phase.json");
    const bPhase = join(b.abs_run_dir, "beacon-phase.json");
    const aTime = existsSync(aPhase) ? statSync(aPhase).mtimeMs : 0;
    const bTime = existsSync(bPhase) ? statSync(bPhase).mtimeMs : 0;
    return bTime - aTime;
  });
}

function inferNextAction(phase, phasePromoted, phasesCompleted) {
  if (phasesCompleted?.includes("release")) {
    return { status: "done", action: "import_evidence_or_qa_release_review" };
  }
  if (phase === "repair") {
    return { status: "in_progress", action: "repair_iteration_or_harness" };
  }
  if (phasePromoted === false) {
    return { status: "in_progress", action: "resolve_harness_blocker" };
  }
  if (BEACON_PHASES.includes(phase)) {
    return { status: "in_progress", action: `phase:${phase}` };
  }
  return { status: "unknown", action: "inspect_spine_artifacts" };
}

function inferNextHarness(phase, phasePromoted) {
  if (phasePromoted === false) return "harness_repair";
  if (phase === "truth") return "beacon truth-map / sync-materials / freeze";
  if (phase === "generate") return "beacon implement run";
  if (phase === "qa") return "beacon qa run";
  if (phase === "release") return "beacon release create";
  if (phase === "repair") return "beacon implement run (repair)";
  return "";
}

export function showSpine(projectRoot, runId = "") {
  const authoritative_paths = [];
  const loopRunId = runId || latestRunId(projectRoot) || "";
  const loopRunDir = loopRunId
    ? join(projectRoot, ".beacon", "loop", "runs", loopRunId)
    : "";

  if (loopRunId && existsSync(loopRunDir)) {
    for (const name of [
      "run-package.json",
      "run-state.json",
      "evidence.json",
      "commits.json",
      "notes.md",
      "summary.md",
    ]) {
      const rel = `.beacon/loop/runs/${loopRunId}/${name}`;
      if (existsSync(join(projectRoot, rel))) authoritative_paths.push(rel);
    }
  }

  const gnhfRuns = listGnhfRunDirs(projectRoot);
  const selected =
    gnhfRuns.find((entry) => entry.run_id === runId) || gnhfRuns[0] || null;

  let phase = "";
  let phases_completed = [];
  let phase_promoted;
  let resolvedRunId = loopRunId || runId;
  let run_dir = loopRunId ? `.beacon/loop/runs/${loopRunId}` : "";

  if (selected) {
    resolvedRunId = selected.run_id;
    run_dir = selected.run_dir;
    authoritative_paths.push(join(selected.run_dir, "beacon-phase.json"));
    authoritative_paths.push(join(selected.run_dir, "truth-promotion.json"));
    authoritative_paths.push(join(selected.run_dir, "prompt.md"));
    authoritative_paths.push(join(selected.run_dir, "notes.md"));

    const phaseState = readJson(join(selected.abs_run_dir, "beacon-phase.json"), {});
    phase = phaseState.phase || "";
    phases_completed = phaseState.phases_completed || [];
    phase_promoted = phaseState.phase_promoted;
  } else if (loopRunId && existsSync(loopRunDir)) {
    const runState = readJson(join(loopRunDir, "run-state.json"), {});
    phase = runState.machine_state || "";
    phases_completed = [];
    phase_promoted = undefined;
    authoritative_paths.push(run_dir);
  }

  if (sqliteAvailable()) {
    authoritative_paths.push(
      ledgerDbPath(projectRoot).replace(`${projectRoot}/`, ""),
    );
  }

  const next = inferNextAction(phase, phase_promoted, phases_completed);

  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "spine show",
    status: selected || loopRunId ? "ok" : "empty",
    run_id: resolvedRunId || "",
    run_dir,
    phase,
    phases_completed,
    ...(phase_promoted !== undefined ? { phase_promoted } : {}),
    next_harness: inferNextHarness(phase, phase_promoted),
    next_action: next.action,
    progress_status: next.status,
    authoritative_paths: [...new Set(authoritative_paths.filter(Boolean))],
    delegation: selected ? "beacon-run" : loopRunId ? "beacon-loop-legacy" : "none",
    doc_ref: "docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md",
  };
}

export function spineDocExists(projectRoot) {
  return existsSync(
    join(projectRoot, "docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md"),
  );
}
