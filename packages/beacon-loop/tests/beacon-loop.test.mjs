import { chmodSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { spawnSync } from "node:child_process";
import test from "node:test";
import assert from "node:assert/strict";

const root = new URL("..", import.meta.url).pathname;
const cli = join(root, "dist", "cli.js");

function run(args, options = {}) {
  return spawnSync("node", [cli, ...args], {
    cwd: options.cwd || root,
    env: { ...process.env, ...(options.env || {}) },
    encoding: "utf8"
  });
}

function makeProject() {
  const dir = join(tmpdir(), `beacon-loop-test-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  mkdirSync(dir, { recursive: true });
  spawnSync("git", ["init"], { cwd: dir, encoding: "utf8" });
  spawnSync("git", ["config", "user.email", "test@example.invalid"], { cwd: dir });
  spawnSync("git", ["config", "user.name", "Test User"], { cwd: dir });
  writeFileSync(join(dir, "README.md"), "fixture\n", "utf8");
  spawnSync("git", ["add", "README.md"], { cwd: dir });
  spawnSync("git", ["commit", "-m", "init"], { cwd: dir });
  return dir;
}

function makeBeaconShim(project, mode = "pass") {
  const bin = join(tmpdir(), `beacon-loop-bin-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  mkdirSync(bin, { recursive: true });
  const shim = join(bin, "beacon");
  const payload = {
    feature_truth: {
      source_paths: {
        truth: "docs/beacon/v1.6.0/features/demo/truth.md",
        tests: "docs/beacon/v1.6.0/features/demo/tests.md",
        tasks: "docs/beacon/v1.6.0/features/demo/tasks.md",
        evidence: "docs/beacon/v1.6.0/features/demo/evidence.md"
      }
    }
  };
  writeFileSync(
    shim,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args[0] === "--version") { console.log("Beacon CLI v1.6.0"); process.exit(0); }
if (args[0] === "truth-map" && args[1] === "resolve") {
  if (${JSON.stringify(mode)} === "blocked") { console.error("missing truth"); process.exit(2); }
  console.log(${JSON.stringify(JSON.stringify(payload))});
  process.exit(0);
}
if (args[0] === "implement" && args[1] === "import-evidence") {
  if (args.includes("--help")) { console.log("import evidence help"); process.exit(0); }
  console.log(JSON.stringify({status:"completed", imported:true}));
  process.exit(0);
}
if (args[0] === "implement" && args[1] === "import-evidence" && args.includes("--help")) process.exit(0);
console.log("{}");
`,
    "utf8"
  );
  chmodSync(shim, 0o755);
  return `${bin}:${process.env.PATH}`;
}

test("help exposes goal and not the retired alias", () => {
  const result = run(["--help"]);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /goal <goal>/);
  assert.doesNotMatch(result.stdout, /\blfg\b/);

  const retired = run([`l${"fg"}`, "x"]);
  assert.equal(retired.status, 2);
});

test("resolver blocked fails closed to beacon-gen-change", () => {
  const project = makeProject();
  const result = run(["goal", "missing feature", "--project", project, "--json"], {
    env: { PATH: makeBeaconShim(project, "blocked") }
  });
  assert.equal(result.status, 2);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "blocked");
  assert.equal(payload.next_route, "beacon-gen-change");
});

test("dry-run writes runtime package artifacts and resolver refs", () => {
  const project = makeProject();
  const result = run(["goal", "demo", "--project", project, "--dry-run", "--json"], {
    env: { PATH: makeBeaconShim(project) }
  });
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  const runPackage = JSON.parse(readFileSync(join(payload.run_dir, "run-package.json"), "utf8"));
  assert.equal(runPackage.command, "goal");
  assert.deepEqual(runPackage.truth_refs, ["docs/beacon/v1.6.0/features/demo/truth.md"]);
  for (const name of ["prompt.md", "notes.md", "output-schema.json", "iteration-001.jsonl", "iteration-001-result.json", "evidence.json", "summary.md"]) {
    assert.ok(readFileSync(join(payload.run_dir, name), "utf8").length > 0);
  }
  const evidence = JSON.parse(readFileSync(join(payload.run_dir, "evidence.json"), "utf8"));
  assert.equal(evidence.runtime_json_role, "runtime_process_record_not_requirement_truth");
  assert.equal(evidence.closure_verdict, "not_provided_by_beacon_loop");
});

test("dirty worktree blocks by default", () => {
  const project = makeProject();
  writeFileSync(join(project, "dirty.txt"), "dirty\n", "utf8");
  const result = run(["goal", "demo", "--project", project, "--json"], {
    env: { PATH: makeBeaconShim(project) }
  });
  assert.equal(result.status, 2);
  assert.equal(JSON.parse(result.stdout).reason_code, "dirty_worktree_blocked");
});

test("success, failure rollback, commit repair, resume, and import evidence", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const success = run(["goal", "demo", "--project", project, "--json"], { env });
  assert.equal(success.status, 0, success.stderr);
  const payload = JSON.parse(success.stdout);
  assert.equal(payload.status, "implementation_candidate");
  assert.ok(JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "commits.json"), "utf8")).commits.length >= 1);

  const resume = run(["resume", payload.run_id, "--project", project, "--json"], { env });
  assert.equal(resume.status, 0);
  assert.equal(JSON.parse(resume.stdout).run_id, payload.run_id);

  const imported = run(["import-evidence", payload.run_id, "--project", project, "--json"], { env });
  assert.equal(imported.status, 0, imported.stderr);
  assert.equal(JSON.parse(imported.stdout).status, "imported");

  const failureProject = makeProject();
  const failure = run(["goal", "demo", "--project", failureProject, "--json"], {
    env: { PATH: makeBeaconShim(failureProject), BEACON_LOOP_TEST_AGENT_RESULT: "failure" }
  });
  assert.equal(JSON.parse(failure.stdout).status, "rolled_back");

  const repairProject = makeProject();
  const repair = run(["goal", "demo", "--project", repairProject, "--json"], {
    env: { PATH: makeBeaconShim(repairProject), BEACON_LOOP_TEST_AGENT_RESULT: "commit-failure" }
  });
  assert.equal(JSON.parse(repair.stdout).reason_code, "commit_failure_repair_required");
});

test("doctor checks runtime prerequisites", () => {
  const project = makeProject();
  const result = run(["doctor", "--project", project, "--json"], {
    env: { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" }
  });
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.checks.node_runtime.status, "pass");
  assert.equal(payload.checks.beacon_cli.status, "pass");
  assert.equal(payload.checks.git_worktree.status, "pass");
  assert.equal(payload.checks.evidence_import.status, "pass");
});
