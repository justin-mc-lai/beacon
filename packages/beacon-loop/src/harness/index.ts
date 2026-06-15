import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { ensureDir, readJson, writeJson, writeText } from "../runner/fs.js";
import { RUNTIME_ROLE, nowIso } from "../runner/types.js";

function runDir(projectRoot, runId) {
  return join(projectRoot, ".beacon", "loop", "runs", runId);
}

export function analyzeRun(projectRoot, runId) {
  const dir = runDir(projectRoot, runId);
  if (!existsSync(join(dir, "run-package.json"))) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "analyze", status: "blocked", reason_code: "run_not_found", run_id: runId };
  }
  const runPackage = readJson(join(dir, "run-package.json"), {});
  const runState = readJson(join(dir, "run-state.json"), {});
  const commits = readJson(join(dir, "commits.json"), { commits: [] });
  const analysis = {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    surface: "beacon-loop",
    command: "analyze",
    run_id: runId,
    feature: runPackage.feature,
    version: runPackage.version,
    machine_state: runState.machine_state,
    iteration: runState.iteration,
    commit_count: Array.isArray(commits.commits) ? commits.commits.length : 0,
    total_tokens: runState.total_tokens || 0,
    cap_reason: runState.cap_reason || "",
    generated_at: nowIso(),
    advisory_only: true,
    requirement_truth_authority: "markdown_feature_package"
  };
  const outDir = join(projectRoot, ".beacon", "loop", "index", "analysis");
  ensureDir(outDir);
  const outPath = join(outDir, `${runId}.json`);
  writeJson(outPath, analysis);
  writeText(
    join(outDir, `${runId}.md`),
    `# Loop Run Analysis (advisory)\n\n- run_id: ${runId}\n- machine_state: ${runState.machine_state}\n- iterations: ${runState.iteration}\n- commits: ${analysis.commit_count}\n\nThis file is harness output only; not requirement truth.\n`
  );
  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "analyze",
    status: "ok",
    run_id: runId,
    output_json: `.beacon/loop/index/analysis/${runId}.json`,
    output_markdown: `.beacon/loop/index/analysis/${runId}.md`
  };
}

export function learnRun(projectRoot, runId) {
  const analyze = analyzeRun(projectRoot, runId);
  if (analyze.status === "blocked") return { ...analyze, command: "learn" };
  const dir = runDir(projectRoot, runId);
  const notes = existsSync(join(dir, "notes.md")) ? readFileSync(join(dir, "notes.md"), "utf8") : "";
  const learning = {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    surface: "beacon-loop",
    command: "learn",
    run_id: runId,
    generated_at: nowIso(),
    key_learnings: notes
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.startsWith("- "))
      .slice(-20),
    advisory_only: true,
    requirement_truth_authority: "markdown_feature_package"
  };
  const outDir = join(projectRoot, ".beacon", "loop", "index", "learning");
  ensureDir(outDir);
  const outPath = join(outDir, `${runId}.json`);
  writeJson(outPath, learning);
  writeText(
    join(outDir, `${runId}.md`),
    `# Loop Run Learning (advisory)\n\n${learning.key_learnings.map((item) => `${item}`).join("\n") || "- none captured"}\n`
  );
  return {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "learn",
    status: "ok",
    run_id: runId,
    output_json: `.beacon/loop/index/learning/${runId}.json`,
    output_markdown: `.beacon/loop/index/learning/${runId}.md`
  };
}
