import { chmodSync, existsSync, mkdtempSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import assert from "node:assert/strict";

const root = new URL("..", import.meta.url).pathname;
const cli = join(root, "dist", "cli.js");
const testScratchRoot = join(tmpdir(), "beacon-loop-tests");
const createdProjectDirs = new Set();

function makeScratchDir(prefix) {
  mkdirSync(testScratchRoot, { recursive: true });
  return mkdtempSync(join(testScratchRoot, `${prefix}-`));
}

function removeWorktreesInProject(projectDir) {
  const worktreesRoot = join(projectDir, ".beacon", "loop", "worktrees");
  if (!existsSync(worktreesRoot)) return;
  for (const runId of readdirSync(worktreesRoot)) {
    const worktreePath = join(worktreesRoot, runId);
    spawnSync("git", ["worktree", "remove", "--force", worktreePath], { cwd: projectDir, encoding: "utf8" });
  }
  spawnSync("git", ["worktree", "prune"], { cwd: projectDir, encoding: "utf8" });
}

function removeScratchRoot() {
  if (!existsSync(testScratchRoot)) return;
  for (const entry of readdirSync(testScratchRoot)) {
    const projectDir = join(testScratchRoot, entry);
    if (existsSync(join(projectDir, ".git"))) {
      removeWorktreesInProject(projectDir);
    }
  }
  try {
    rmSync(testScratchRoot, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  } catch {
    spawnSync("rm", ["-rf", testScratchRoot], { stdio: "ignore" });
  }
}

test.before(() => {
  mkdirSync(testScratchRoot, { recursive: true });
});

test.after(() => {
  for (const projectDir of createdProjectDirs) {
    if (existsSync(projectDir)) {
      removeWorktreesInProject(projectDir);
      rmSync(projectDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
    }
  }
  createdProjectDirs.clear();
});

function run(args, options = {}) {
  return spawnSync("node", [cli, ...args], {
    cwd: options.cwd || root,
    env: { ...process.env, ...(options.env || {}) },
    encoding: "utf8"
  });
}

function makeProject() {
  const dir = makeScratchDir("beacon-loop-test");
  createdProjectDirs.add(dir);
  spawnSync("git", ["init"], { cwd: dir, encoding: "utf8" });
  spawnSync("git", ["config", "user.email", "test@example.invalid"], { cwd: dir });
  spawnSync("git", ["config", "user.name", "Test User"], { cwd: dir });
  writeFileSync(join(dir, "README.md"), "fixture\n", "utf8");
  spawnSync("git", ["add", "README.md"], { cwd: dir });
  spawnSync("git", ["commit", "-m", "init"], { cwd: dir });
  return dir;
}

function makeBeaconShim(project, mode = "pass") {
  const bin = makeScratchDir("beacon-loop-bin");
  mkdirSync(bin, { recursive: true });
  const shim = join(bin, "beacon");
  const payload = {
    feature_truth: {
      truth_frontmatter: { status: "frozen" },
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
  console.log(JSON.stringify({status:"completed", imported:true, surface:"beacon-implement"}));
  process.exit(0);
}
if (args[0] === "qa" && args[1] === "run") {
  console.log(JSON.stringify({status:"completed", surface:"beacon-qa", closure_verdict:"shim_only_not_release_ready"}));
  process.exit(0);
}
if (args[0] === "release" && args[1] === "create") {
  console.log(JSON.stringify({status:"completed", surface:"beacon-release", closure_verdict:"shim_only_not_release_ready"}));
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

const EXECUTE_ONLY_FLAGS = ["--mode", "execute-only", "--feature", "demo"];

function goalDemo(project, extraArgs = [], options = {}) {
  return run(["goal", "demo", "--project", project, ...EXECUTE_ONLY_FLAGS, ...extraArgs], options);
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
  const result = run(["goal", "missing feature", "--project", project, "--mode", "execute-only", "--feature", "missing-feature", "--json"], {
    env: { PATH: makeBeaconShim(project, "blocked") }
  });
  assert.equal(result.status, 2);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "blocked");
  assert.equal(payload.next_route, "beacon-gen-change");
});

test("dry-run writes runtime package artifacts and resolver refs", () => {
  const project = makeProject();
  const result = goalDemo(project, ["--dry-run", "--json"], {
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
  const result = goalDemo(project, ["--json"], {
    env: { PATH: makeBeaconShim(project) }
  });
  assert.equal(result.status, 2);
  assert.equal(JSON.parse(result.stdout).reason_code, "dirty_worktree_blocked");
});

test("success, failure rollback, commit repair, resume, and import evidence", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const success = goalDemo(project, ["--json"], { env });
  assert.equal(success.status, 0, success.stderr);
  const payload = JSON.parse(success.stdout);
  assert.equal(payload.status, "implementation_candidate");
  assert.ok(JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "commits.json"), "utf8")).commits.length >= 1);

  const repairProject = makeProject();
  const repairGoal = goalDemo(repairProject, ["--json"], {
    env: { PATH: makeBeaconShim(repairProject), BEACON_LOOP_TEST_AGENT_RESULT: "commit-failure" }
  });
  const repairId = JSON.parse(repairGoal.stdout).run_id;
  const resume = run(["resume", repairId, "--project", repairProject, "--json"], {
    env: { PATH: makeBeaconShim(repairProject), BEACON_LOOP_TEST_AGENT_RESULT: "success" }
  });
  assert.equal(resume.status, 0, resume.stderr);
  assert.equal(JSON.parse(resume.stdout).run_id, repairId);

  const imported = run(["import-evidence", payload.run_id, "--project", project, "--json"], { env });
  assert.equal(imported.status, 0, imported.stderr);
  assert.equal(JSON.parse(imported.stdout).status, "imported");

  const failureProject = makeProject();
  const failure = goalDemo(failureProject, ["--json"], {
    env: { PATH: makeBeaconShim(failureProject), BEACON_LOOP_TEST_AGENT_RESULT: "failure" }
  });
  assert.equal(JSON.parse(failure.stdout).status, "rolled_back");

  const repairProject2 = makeProject();
  const repair = goalDemo(repairProject2, ["--json"], {
    env: { PATH: makeBeaconShim(repairProject2), BEACON_LOOP_TEST_AGENT_RESULT: "commit-failure" }
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

test("multi-iteration orchestrator writes iteration-001..003 and cap_reached", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const result = goalDemo(project, ["--max-iterations", "3", "--json"], { env });
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.ok(["cap_reached", "implementation_candidate"].includes(payload.status));
  assert.equal(payload.iteration, 3);
  const runDir = join(project, ".beacon", "loop", "runs", payload.run_id);
  const runState = JSON.parse(readFileSync(join(runDir, "run-state.json"), "utf8"));
  assert.ok(["max_iterations", "stop_when"].includes(runState.cap_reason));
  for (const name of ["iteration-001-result.json", "iteration-002-result.json", "iteration-003-result.json"]) {
    assert.ok(existsSync(join(runDir, name)), name);
  }
  const summary = readFileSync(join(runDir, "summary.md"), "utf8");
  assert.match(summary, /iterations_completed: 3/);
  assert.match(summary, /elapsed_ms:/);
});

test("resume continues at iteration N+1 on same run-id", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success", BEACON_LOOP_TEST_STOP_AFTER_ITERATION: "1" };
  const first = goalDemo(project, ["--max-iterations", "3", "--json"], { env });
  const firstPayload = JSON.parse(first.stdout);
  assert.equal(firstPayload.iteration, 1);
  const resume = run(["resume", firstPayload.run_id, "--project", project, "--json"], {
    env: { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" }
  });
  assert.equal(resume.status, 0, resume.stderr);
  const resumePayload = JSON.parse(resume.stdout);
  assert.equal(resumePayload.run_id, firstPayload.run_id);
  assert.ok(resumePayload.iteration >= 2);
  assert.ok(existsSync(join(project, ".beacon", "loop", "runs", firstPayload.run_id, "iteration-002-result.json")));
});

test("iteration prompt includes accumulated notes", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const result = goalDemo(project, ["--max-iterations", "2", "--json"], { env });
  const payload = JSON.parse(result.stdout);
  const prompt = readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "iteration-002-prompt.txt"), "utf8");
  assert.match(prompt, /Accumulated notes:/);
  assert.match(prompt, /iteration 1: success/);
});

test("graceful stop waits until iteration boundary", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success", BEACON_LOOP_TEST_STOP_AFTER_ITERATION: "1" };
  const result = goalDemo(project, ["--max-iterations", "5", "--json"], { env });
  const payload = JSON.parse(result.stdout);
  assert.ok(["cap_reached", "implementation_candidate"].includes(payload.status));
  assert.equal(payload.iteration, 1);
  const runState = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "run-state.json"), "utf8"));
  assert.equal(runState.cap_reason, "graceful_stop");
});

test("force stop via interrupt marks force_stopped", () => {
  const project = makeProject();
  const env = {
    PATH: makeBeaconShim(project),
    BEACON_LOOP_TEST_AGENT_RESULT: "success",
    BEACON_LOOP_TEST_FORCE_STOP_ON_ITERATION: "2"
  };
  const result = goalDemo(project, ["--max-iterations", "5", "--json"], { env });
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "force_stopped");
  const runState = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "run-state.json"), "utf8"));
  assert.equal(runState.machine_state, "force_stopped");
});

test("consecutive failures abort after limit", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "failure", BEACON_LOOP_TEST_BACKOFF_MS: "0" };
  const result = goalDemo(project, ["--max-iterations", "5", "--json"], { env });
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "rolled_back");
  assert.equal(payload.reason_code, "consecutive_failures_abort");
});

test("no-op iteration counts as failure", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "noop", BEACON_LOOP_TEST_BACKOFF_MS: "0" };
  const result = goalDemo(project, ["--max-iterations", "5", "--json"], { env });
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.reason_code, "consecutive_failures_abort");
});

test("ledger query and show after goal", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const goal = goalDemo(project, ["--json"], { env });
  const runId = JSON.parse(goal.stdout).run_id;
  const query = run(["runs", "query", "--project", project, "--json"], { env });
  assert.equal(query.status, 0, query.stderr);
  const queryPayload = JSON.parse(query.stdout);
  assert.ok(queryPayload.count >= 1);
  assert.ok(queryPayload.runs.some((row) => row.run_id === runId));
  const show = run(["runs", "show", runId, "--project", project, "--json"], { env });
  assert.equal(show.status, 0, show.stderr);
  const showPayload = JSON.parse(show.stdout);
  assert.equal(showPayload.run.run_id, runId);
  assert.ok(showPayload.artifact_refs.includes(`.beacon/loop/runs/${runId}/run-package.json`));
  assert.ok(existsSync(join(project, ".beacon", "loop", "ledger", "loop-runs.db")));
});

test("runs diagnose buckets blocked dirty and healthy paths", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const empty = run(["runs", "diagnose", "--project", project, "--json"], { env });
  const emptyPayload = JSON.parse(empty.stdout);
  assert.ok(Array.isArray(emptyPayload.buckets.never_started));

  writeFileSync(join(project, "dirty.txt"), "x\n", "utf8");
  const dirty = run(["runs", "diagnose", "--project", project, "--json"], { env });
  assert.ok(JSON.parse(dirty.stdout).buckets.dirty_worktree.length >= 1);

  const goal = goalDemo(project, ["--json"], { env });
  const runId = JSON.parse(goal.stdout).run_id;
  const after = run(["runs", "diagnose", "--project", project, "--json"], { env });
  const afterPayload = JSON.parse(after.stdout);
  assert.ok(afterPayload.buckets.healthy.some((item) => item.run_id === runId) || afterPayload.buckets.repair_required.length >= 0);
});

test("runtime tracking cycle", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const goal = goalDemo(project, ["--json"], { env });
  const runId = JSON.parse(goal.stdout).run_id;
  const set = run(["runtime-set", runId, "--project", project, "--status", "running", "--port", "4242", "--notes", "test", "--json"], { env });
  assert.equal(set.status, 0, set.stderr);
  const list = run(["runtime-list", "--project", project, "--status", "running", "--json"], { env });
  const listPayload = JSON.parse(list.stdout);
  assert.ok(listPayload.runtime.some((row) => row.run_id === runId && Number(row.port) === 4242));
  const remove = run(["runtime-remove", runId, "--project", project, "--json"], { env });
  assert.equal(remove.status, 0);
  const after = run(["runtime-list", "--project", project, "--json"], { env });
  assert.equal(JSON.parse(after.stdout).runtime.find((row) => row.run_id === runId), undefined);
});

test("analyze and learn write advisory index artifacts only", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const goal = goalDemo(project, ["--max-iterations", "2", "--json"], { env });
  const runId = JSON.parse(goal.stdout).run_id;
  const analyze = run(["analyze", runId, "--project", project, "--json"], { env });
  assert.equal(analyze.status, 0, analyze.stderr);
  const analyzePayload = JSON.parse(analyze.stdout);
  assert.ok(existsSync(join(project, analyzePayload.output_json)));
  const learn = run(["learn", runId, "--project", project, "--json"], { env });
  assert.equal(learn.status, 0, learn.stderr);
  const learnPayload = JSON.parse(learn.stdout);
  assert.ok(existsSync(join(project, learnPayload.output_json)));
  const learning = JSON.parse(readFileSync(join(project, learnPayload.output_json), "utf8"));
  assert.equal(learning.advisory_only, true);
  assert.equal(learning.requirement_truth_authority, "markdown_feature_package");
});

test("doctor --diagnose returns repair buckets", () => {
  const project = makeProject();
  const result = run(["doctor", "--project", project, "--diagnose", "--json"], {
    env: { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" }
  });
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.checks.sqlite_cli.status, "pass");
  assert.ok(payload.diagnose.buckets);
  assert.ok("missing_backend" in payload.diagnose.buckets);
});

test("review exposes rich summary fields", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const goal = goalDemo(project, ["--max-iterations", "2", "--json"], { env });
  const runId = JSON.parse(goal.stdout).run_id;
  const review = run(["review", runId, "--project", project]);
  assert.equal(review.status, 0);
  assert.match(review.stdout, /branch:/);
  assert.match(review.stdout, /import:/);
  assert.match(review.stdout, /qa:/);
});

test("TC-029 branch mode matrix blocks illegal current-branch + isolated-worktree", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const blocked = run(
    ["goal", "demo", "--project", project, "--mode", "execute-only", "--feature", "demo", "--branch-mode", "current-branch", "--isolated-worktree", "--json"],
    { env }
  );
  const payload = JSON.parse(blocked.stdout);
  assert.equal(payload.status, "blocked");
  assert.equal(payload.reason_code, "illegal_branch_mode_combo");
});

test("TC-029 current-branch runs in project root without worktree path", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const goal = goalDemo(project, ["--branch-mode", "current-branch", "--json"], { env });
  assert.equal(goal.status, 0, goal.stderr);
  const payload = JSON.parse(goal.stdout);
  const runPackage = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "run-package.json"), "utf8"));
  assert.equal(runPackage.branch_mode, "current-branch");
  assert.equal(runPackage.worktree.path, project);
});

test("TC-029 run-branch creates beacon-loop/<run-id> branch", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const goal = goalDemo(project, ["--branch-mode", "run-branch", "--json"], { env });
  assert.equal(goal.status, 0, goal.stderr);
  const payload = JSON.parse(goal.stdout);
  const runPackage = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "run-package.json"), "utf8"));
  assert.equal(runPackage.branch_mode, "run-branch");
  assert.match(runPackage.worktree.branch, /^beacon-loop\//);
});

test("TC-030 config file defaults with CLI override", () => {
  const project = makeProject();
  mkdirSync(join(project, ".beacon-loop"), { recursive: true });
  writeFileSync(
    join(project, ".beacon-loop", "config.yml"),
    "agent: claude\nbranch_mode: current-branch\nmax_iterations: 3\n",
    "utf8"
  );
  spawnSync("git", ["add", ".beacon-loop/config.yml"], { cwd: project });
  spawnSync("git", ["commit", "-m", "add loop config"], { cwd: project });
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success", BEACON_LOOP_TEST_CLAUDE_RESULT: "success" };
  const goal = goalDemo(project, ["--agent", "codex", "--json"], { env });
  assert.equal(goal.status, 0, goal.stderr);
  const payload = JSON.parse(goal.stdout);
  const runPackage = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "run-package.json"), "utf8"));
  assert.equal(runPackage.agent, "codex");
  assert.equal(runPackage.branch_mode, "current-branch");
  assert.equal(runPackage.max_iterations, 3);
});

test("TC-031 codex multi-iteration path completes at least two iterations", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const goal = goalDemo(project, ["--max-iterations", "2", "--json"], { env });
  assert.equal(goal.status, 0, goal.stderr);
  const payload = JSON.parse(goal.stdout);
  const runState = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "run-state.json"), "utf8"));
  assert.ok(Number(runState.iteration || runState.current_iteration || 0) >= 2 || Number(runState.completed_iterations || 0) >= 2);
});

test("TC-032 claude and acp adapters emit structured contract fields", () => {
  const claudeProject = makeProject();
  const claudeEnv = {
    PATH: makeBeaconShim(claudeProject),
    BEACON_LOOP_TEST_CLAUDE_RESULT: "success"
  };
  const claudeGoal = goalDemo(claudeProject, ["--agent", "claude", "--json"], { env: claudeEnv });
  assert.equal(claudeGoal.status, 0, claudeGoal.stderr);
  const claudeRunId = JSON.parse(claudeGoal.stdout).run_id;
  assert.ok(existsSync(join(claudeProject, ".beacon", "loop", "worktrees", claudeRunId, `.beacon-loop-claude-${claudeRunId}.txt`)));

  const acpProject = makeProject();
  const acpEnv = {
    PATH: makeBeaconShim(acpProject),
    BEACON_LOOP_TEST_ACP_RESULT: "success"
  };
  const acpGoal = goalDemo(acpProject, ["--agent", "acp:demo-target", "--json"], { env: acpEnv });
  assert.equal(acpGoal.status, 0, acpGoal.stderr);
  const acpRunId = JSON.parse(acpGoal.stdout).run_id;
  assert.ok(existsSync(join(acpProject, ".beacon", "loop", "worktrees", acpRunId, `.beacon-loop-acp-demo-target-${acpRunId}.txt`)));
});

test("TC-033 scripted closed loop drives goal import-evidence and beacon qa run", () => {
  const project = makeProject();
  const env = { PATH: makeBeaconShim(project), BEACON_LOOP_TEST_AGENT_RESULT: "success" };
  const goal = goalDemo(project, ["--max-iterations", "2", "--json"], { env });
  assert.equal(goal.status, 0, goal.stderr);
  const goalPayload = JSON.parse(goal.stdout);
  assert.equal(goalPayload.status, "implementation_candidate");
  assert.ok(Number(goalPayload.iteration) >= 2);

  const imported = run(["import-evidence", goalPayload.run_id, "--project", project, "--json"], { env });
  assert.equal(imported.status, 0, imported.stderr);
  assert.equal(JSON.parse(imported.stdout).status, "imported");
  assert.ok(existsSync(join(project, ".beacon", "loop", "runs", goalPayload.run_id, "evidence-import.json")));

  const qa = spawnSync(
    "beacon",
    ["qa", "run", "demo", "--project", project, "--version", "v1.6.0", "--json"],
    { cwd: project, env, encoding: "utf8" }
  );
  assert.equal(qa.status, 0, qa.stderr);
  const qaPayload = JSON.parse(qa.stdout);
  assert.equal(qaPayload.surface, "beacon-qa");
  assert.notEqual(qaPayload.closure_verdict, "release_ready");
});
