import { join } from "node:path";
import { run } from "../git/git.js";
import { readJson, writeJson } from "../runner/fs.js";

export function importEvidence(projectRoot, runId, jsonOutput = false) {
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  const runPackage = readJson(join(runDir, "run-package.json"), {});
  const evidence = readJson(join(runDir, "evidence.json"), {});
  const feature = runPackage.feature || evidence.feature || runPackage.goal || runId;
  const version = runPackage.version || "v1.6.0";
  const changedFiles = Array.isArray(evidence.changed_files) && evidence.changed_files.length
    ? evidence.changed_files
    : ["packages/beacon-loop"];
  const sourceRefs = [
    `.beacon/loop/runs/${runId}/evidence.json`,
    `.beacon/loop/runs/${runId}/summary.md`
  ];
  const args = [
    "implement",
    "import-evidence",
    feature,
    "--project",
    projectRoot,
    "--version",
    version,
    "--run-id",
    runId,
    "--summary-ref",
    `.beacon/loop/runs/${runId}/summary.md`,
    "--approved-by",
    "beacon-loop"
  ];
  for (const ref of sourceRefs) args.push("--source-ref", ref);
  for (const file of changedFiles) args.push("--changed-file", file);
  const result = run("beacon", args, { cwd: projectRoot });
  const payload = {
    schema_version: "1.0",
    surface: "beacon-loop",
    command: "import-evidence",
    run_id: runId,
    status: result.code === 0 ? "imported" : "blocked",
    beacon_command: `beacon ${args.join(" ")}`,
    stdout: result.stdout,
    stderr: result.stderr
  };
  writeJson(join(runDir, "evidence-import.json"), payload);
  if (jsonOutput) return payload;
  return payload;
}
