#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const cli = join(root, "dist", "cli.js");
const project = process.argv[2] || process.cwd();
const goal = process.argv[3] || "demo closed loop";
const feature = process.argv[4] || "demo";
const version = process.argv[5] || "v1.6.0";

function runNode(args) {
  return spawnSync("node", [cli, ...args], { cwd: root, encoding: "utf8", env: process.env });
}

function runBeacon(args) {
  return spawnSync("beacon", args, { cwd: project, encoding: "utf8", env: process.env });
}

const started = runNode(["goal", goal, "--project", project, "--max-iterations", "2", "--json"]);
if (started.status !== 0) {
  console.error(started.stderr || started.stdout);
  process.exit(started.status || 1);
}
const payload = JSON.parse(started.stdout);
const runId = payload.run_id;
if (payload.status !== "implementation_candidate") {
  console.error(JSON.stringify({ step: "goal", blocked: payload }, null, 2));
  process.exit(2);
}

const imported = runNode(["import-evidence", runId, "--project", project, "--json"]);
if (imported.status !== 0 || JSON.parse(imported.stdout).status !== "imported") {
  console.error(imported.stderr || imported.stdout);
  process.exit(imported.status || 2);
}

const qa = runBeacon(["qa", "run", feature, "--project", project, "--version", version, "--json"]);
if (qa.status !== 0) {
  console.error(qa.stderr || qa.stdout);
  process.exit(qa.status || 3);
}

console.log(
  JSON.stringify(
    {
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "e2e-closed-loop",
      status: "completed",
      run_id: runId,
      qa: JSON.parse(qa.stdout || "{}")
    },
    null,
    2
  )
);
