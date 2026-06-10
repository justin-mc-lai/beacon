import { join } from "node:path";
import { writeJson } from "../runner/fs.js";
import { nowIso } from "../runner/types.js";

export const HARNESS_WORKER_ROUTES = [
  {
    delivery_state: "intent_review",
    harness: "pln",
    worker_command: 'beacon planner-review run "<feature>" --project <project> --version <version> --json'
  },
  {
    delivery_state: "truth_fill",
    harness: "gen-truth",
    worker_command: "beacon prd-bootstrap / truth / freeze chain"
  },
  {
    delivery_state: "implement_loop",
    harness: "gen-implement",
    worker_command:
      'beacon implement run "<feature>" --project <project> --version <version> --runner <runner> --mode single --json --no-auto-qa'
  },
  {
    delivery_state: "repair_from_qa",
    harness: "gen-implement",
    worker_command:
      'beacon implement run "<feature>" --project <project> --version <version> --runner <runner> --mode single --json --no-auto-qa'
  },
  {
    delivery_state: "qa_pending",
    harness: "eval",
    worker_command: 'beacon qa run "<feature>" --project <project> --version <version> --json'
  },
  {
    delivery_state: "release_pending",
    harness: "eval-release",
    worker_command: "beacon release create --project <project> --version <version> --json"
  }
];

export function defaultImplementRunner() {
  return process.env.BEACON_LOOP_IMPLEMENT_RUNNER || "codex-subagents";
}

export function buildImplementWorkerCommand(projectRoot, feature, version, runner = defaultImplementRunner()) {
  return [
    "beacon",
    "implement",
    "run",
    `"${feature}"`,
    "--project",
    projectRoot,
    "--version",
    version,
    "--runner",
    runner,
    "--mode",
    "single",
    "--json",
    "--no-auto-qa"
  ].join(" ");
}

export function writeWorkerRoute(runDir, projectRoot, feature, version, runner = defaultImplementRunner()) {
  const payload = {
    schema_version: "1.0",
    generated_at: nowIso(),
    feature,
    version,
    implement_runner: runner,
    routes: HARNESS_WORKER_ROUTES.map((route) => ({
      ...route,
      worker_command: route.worker_command
        .replace("<feature>", feature)
        .replace("<project>", projectRoot)
        .replace("<version>", version)
        .replace("<runner>", runner)
    })),
    implement_worker_command: buildImplementWorkerCommand(projectRoot, feature, version, runner)
  };
  writeJson(join(runDir, "worker-route.json"), payload);
  return payload;
}
