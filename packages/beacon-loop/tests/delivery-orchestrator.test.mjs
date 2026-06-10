import { chmodSync, existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import assert from "node:assert/strict";
import { canTransition } from "../dist/delivery/state.js";
import { classifyIntent } from "../dist/intent/classify.js";
import { resolveProjectVersion } from "../dist/beacon/version.js";

const root = new URL("..", import.meta.url).pathname;
const cli = join(root, "dist", "cli.js");
const testScratchRoot = join(tmpdir(), "beacon-loop-delivery-tests");
const createdProjectDirs = new Set();

function makeScratchDir(prefix) {
  mkdirSync(testScratchRoot, { recursive: true });
  return mkdtempSync(join(testScratchRoot, `${prefix}-`));
}

function run(args, options = {}) {
  return spawnSync("node", [cli, ...args], {
    cwd: options.cwd || root,
    env: { ...process.env, ...(options.env || {}) },
    encoding: "utf8"
  });
}

function makeProject() {
  const dir = makeScratchDir("delivery-test");
  createdProjectDirs.add(dir);
  spawnSync("git", ["init"], { cwd: dir, encoding: "utf8" });
  spawnSync("git", ["config", "user.email", "test@example.invalid"], { cwd: dir });
  spawnSync("git", ["config", "user.name", "Test User"], { cwd: dir });
  writeFileSync(join(dir, "README.md"), "fixture\n", "utf8");
  spawnSync("git", ["add", "README.md"], { cwd: dir });
  spawnSync("git", ["commit", "-m", "init"], { cwd: dir });
  return dir;
}

function makeDeliveryBeaconShim(project, { resolveMode = "frozen", qaMode = "pass" } = {}) {
  const bin = makeScratchDir("delivery-beacon-bin");
  mkdirSync(bin, { recursive: true });
  const shim = join(bin, "beacon");
  const frozenPayload = {
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
  const draftPayload = {
    feature_truth: {
      truth_frontmatter: { status: "draft" },
      source_paths: frozenPayload.feature_truth.source_paths
    }
  };
  writeFileSync(
    shim,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
const resolveMode = ${JSON.stringify(resolveMode)};
const qaMode = ${JSON.stringify(qaMode)};
const frozenPayload = ${JSON.stringify(frozenPayload)};
const draftPayload = ${JSON.stringify(draftPayload)};
const phantomPathsPayload = {
  feature_truth: {
    status: "blocked",
    truth_frontmatter: { status: "draft" },
    frontmatter_errors: ["frontmatter_missing"],
    source_paths: {
      truth: "docs/beacon/v1.6.0/features/demo/truth.md",
      tests: "docs/beacon/v1.6.0/features/demo/tests.md",
      tasks: "docs/beacon/v1.6.0/features/demo/tasks.md",
      evidence: "docs/beacon/v1.6.0/features/demo/evidence.md"
    },
    surfaces: {
      truth: { exists: false },
      tests: { exists: false },
      tasks: { exists: false },
      evidence: { exists: false }
    }
  }
};
if (args[0] === "--version") { console.log("Beacon CLI v1.6.0"); process.exit(0); }
if (args[0] === "truth-map" && args[1] === "resolve") {
  if (resolveMode === "blocked") { console.error("missing truth"); process.exit(2); }
  if (resolveMode === "phantom_paths") {
    console.log(JSON.stringify(phantomPathsPayload));
    process.exit(0);
  }
  const payload = resolveMode === "draft" ? draftPayload : frozenPayload;
  console.log(JSON.stringify(payload));
  process.exit(0);
}
if (args[0] === "truth" && args[1] === "init") {
  console.log("truth init ok");
  process.exit(0);
}
if (args[0] === "prd-bootstrap" && args[1] === "run") {
  console.log(JSON.stringify({ status: "completed", feature: args[2] || "demo" }));
  process.exit(0);
}
if (args[0] === "brainstorm" && args[1] === "run") {
  console.log(JSON.stringify({ status: "completed", output_path: "docs/beacon/v1.6.0/features/demo/research.md" }));
  process.exit(0);
}
if (args[0] === "doctor" && args[1] === "sync-materials") {
  console.log(JSON.stringify({ status: "completed", result: { feature_count: 1 } }));
  process.exit(0);
}
if (args[0] === "doctor" && args[1] === "sync-requirement-clarity") {
  console.log(JSON.stringify({ status: "completed", result: { gate: { status: "pass" } } }));
  process.exit(0);
}
if (args[0] === "materialize-feature-package") {
  console.log(JSON.stringify({ status: "materialized", written: ["docs/beacon/v1.6.0/features/demo/truth.md"] }));
  process.exit(0);
}
if (args[0] === "truth-map" && args[1] === "rebuild-machine") {
  console.log(JSON.stringify({ status: "rebuilt", validation_status: "pass" }));
  process.exit(0);
}
if (args[0] === "freeze") {
  console.log(JSON.stringify({ status: "frozen", revision_id: "R1" }));
  process.exit(0);
}
if (args[0] === "planner-review" && args[1] === "run") {
  console.log(JSON.stringify({ findings: [], synthesis: { recommended_route: "continue_delivery" }, parity_matrix: [], deferral_ledger: [] }));
  process.exit(0);
}
if (args[0] === "implement" && args[1] === "import-evidence") {
  console.log(JSON.stringify({ status: "imported", imported: true, surface: "beacon-implement" }));
  process.exit(0);
}
if (args[0] === "qa" && args[1] === "run") {
  if (qaMode === "fail") {
    console.log(JSON.stringify({ status: "blocked", surface: "beacon-qa", reason_code: "qa_findings_open" }));
    process.exit(2);
  }
  console.log(JSON.stringify({ status: "completed", surface: "beacon-qa", closure_verdict: "shim_only_not_release_ready" }));
  process.exit(0);
}
if (args[0] === "release" && args[1] === "create") {
  console.log(JSON.stringify({ status: "completed", surface: "beacon-release", closure_verdict: "shim_only_not_release_ready" }));
  process.exit(0);
}
console.log("{}");
process.exit(0);
`,
    "utf8"
  );
  chmodSync(shim, 0o755);
  return `${bin}:${process.env.PATH}`;
}

test.after(() => {
  for (const projectDir of createdProjectDirs) {
    if (existsSync(projectDir)) {
      rmSync(projectDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
    }
  }
  createdProjectDirs.clear();
});

test("intent-capture: delivery goal writes intent artifacts (AC-031 / TC-031)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project),
    BEACON_LOOP_TEST_REVIEW: "fixture",
    BEACON_LOOP_TEST_EVAL_CHAIN: "fixture",
    BEACON_LOOP_TEST_AGENT_RESULT: "success"
  };
  const result = run(
    ["goal", "deliver demo feature", "--project", project, "--feature", "demo", "--mode", "intent-only", "--json"],
    { env }
  );
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "intent_captured");
  const runDir = join(project, ".beacon", "loop", "runs", payload.run_id);
  const capture = JSON.parse(readFileSync(join(runDir, "intent-capture.json"), "utf8"));
  const contract = JSON.parse(readFileSync(join(runDir, "intent-contract.json"), "utf8"));
  assert.equal(capture.utterance, "deliver demo feature");
  assert.equal(contract.utterance, "deliver demo feature");
  assert.ok(contract.determinism?.rules_hash);
});

test("cold-start-slug-inference: gum utterance infers feature slug without --feature", () => {
  const contract = classifyIntent(
    "复刻 charmbracelet/gum 的 choose/filter 交互，在本项目 parity 交付",
    { version: "v1.0.0", mode: "delivery" }
  );
  assert.equal(contract.feature_slug, "gum-choose-filter-parity");
});

test("project-version-auto: resolves docs version from onboarding (P2)", () => {
  const project = makeProject();
  mkdirSync(join(project, ".beacon", "state"), { recursive: true });
  writeFileSync(
    join(project, ".beacon", "state", "project-onboarding.json"),
    JSON.stringify({ docs_version: "v1.0.0", runtime_version: "v1.6.0" }),
    "utf8"
  );
  assert.equal(resolveProjectVersion(project, "auto"), "v1.0.0");
  assert.equal(resolveProjectVersion(project, "v1.6.0"), "v1.6.0");
});

test("phantom-truth-paths: missing surfaces enter truth_fill bootstrap (P0 cold-start)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project, { resolveMode: "phantom_paths" }),
    BEACON_LOOP_TEST_REVIEW: "fixture",
    BEACON_LOOP_TEST_TRUTH_FILL: "fixture"
  };
  const result = run(
    ["goal", "deliver demo", "--project", project, "--feature", "demo", "--mode", "delivery", "--json"],
    { env }
  );
  assert.equal(result.status, 2);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.reason_code, "truth_not_frozen");
  const promotion = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "truth-promotion.json"), "utf8"));
  assert.ok(promotion.calls.length >= 1);
  const deliveryState = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "delivery-state.json"), "utf8"));
  assert.notEqual(deliveryState.state, "implement_loop");
});

test("intent-classify-deterministic: same utterance yields same contract (AC-032 / TC-032)", () => {
  const a = classifyIntent("deliver full parity closed loop for demo", { feature: "demo", version: "v1.6.0", mode: "delivery" });
  const b = classifyIntent("deliver full parity closed loop for demo", { feature: "demo", version: "v1.6.0", mode: "delivery" });
  assert.equal(a.intent_class, b.intent_class);
  assert.equal(a.scope_mode, b.scope_mode);
  assert.equal(a.determinism.rules_hash, b.determinism.rules_hash);
});

test("planner-review-artifact: review-only writes review artifact (AC-033 / TC-033)", () => {
  const project = makeProject();
  const env = { PATH: makeDeliveryBeaconShim(project), BEACON_LOOP_TEST_REVIEW: "fixture" };
  const result = run(
    ["goal", "beacon-loop orchestrator review", "--project", project, "--feature", "demo", "--mode", "review-only", "--json"],
    { env }
  );
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  const artifact = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "review-artifact.json"), "utf8"));
  assert.equal(artifact.runtime_evidence_only, true);
  assert.equal(artifact.formal_verdict_authority, false);
  assert.ok(artifact.intent_snapshot?.utterance);
  assert.ok(artifact.scope_mode);
});

test("truth-fill-on-blocked: blocked resolve enters truth_fill (AC-034 / TC-034)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project, { resolveMode: "blocked" }),
    BEACON_LOOP_TEST_REVIEW: "fixture",
    BEACON_LOOP_TEST_TRUTH_FILL: "fixture"
  };
  const result = run(
    ["goal", "deliver demo", "--project", project, "--feature", "demo", "--mode", "delivery", "--json"],
    { env }
  );
  assert.equal(result.status, 2);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.reason_code, "truth_not_frozen");
  const promotion = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "truth-promotion.json"), "utf8"));
  assert.ok(Array.isArray(promotion.calls));
  assert.ok(promotion.calls.length >= 1);
});

test("frozen-gate-before-implement: draft truth blocks implement loop (AC-035 / TC-035)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project, { resolveMode: "draft" }),
    BEACON_LOOP_TEST_REVIEW: "fixture"
  };
  const result = run(
    ["goal", "deliver demo", "--project", project, "--feature", "demo", "--mode", "delivery", "--json"],
    { env }
  );
  assert.equal(result.status, 2);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.reason_code, "truth_not_frozen");
  const deliveryState = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "delivery-state.json"), "utf8"));
  assert.notEqual(deliveryState.state, "implement_loop");
});

test("delivery-eval-chain: delivery mode invokes eval chain fixtures (AC-036 / TC-036)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project),
    BEACON_LOOP_TEST_REVIEW: "fixture",
    BEACON_LOOP_TEST_EVAL_CHAIN: "fixture",
    BEACON_LOOP_TEST_AGENT_RESULT: "success"
  };
  const result = run(
    ["goal", "demo", "--project", project, "--feature", "demo", "--mode", "delivery", "--max-iterations", "1", "--json"],
    { env }
  );
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.closure_verdict, "not_provided_by_beacon_loop");
  assert.ok(existsSync(join(project, ".beacon", "loop", "runs", payload.run_id, "eval-chain.json")));
});

test("qa-fail-repair-loop: qa failure routes to repair_from_qa (AC-037 / TC-037)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project, { qaMode: "fail" }),
    BEACON_LOOP_TEST_REVIEW: "fixture",
    BEACON_LOOP_TEST_AGENT_RESULT: "success"
  };
  const result = run(
    ["goal", "demo", "--project", project, "--feature", "demo", "--mode", "delivery", "--max-iterations", "1", "--json"],
    { env }
  );
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "repair_from_qa");
  const deliveryState = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "delivery-state.json"), "utf8"));
  assert.equal(deliveryState.state, "repair_from_qa");
  assert.match(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "notes.md"), "utf8"), /./);
});

test("delivery-state-machine: illegal transitions blocked (AC-038 / TC-038)", () => {
  assert.equal(canTransition("intent_capture", "implement_loop"), false);
  assert.equal(canTransition("truth_gap_scan", "implement_loop", { truthFrozen: false }), false);
  assert.equal(canTransition("truth_gap_scan", "implement_loop", { truthFrozen: true }), true);
  assert.equal(canTransition("implement_loop", "terminal_closed"), false);
  assert.equal(canTransition("qa_pending", "terminal_closed", { releaseInvoked: false }), false);
});

test("e2e-utterance-to-release: frozen fixture delivery chain (AC-039 / TC-039)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project),
    BEACON_LOOP_TEST_REVIEW: "fixture",
    BEACON_LOOP_TEST_EVAL_CHAIN: "fixture",
    BEACON_LOOP_TEST_AGENT_RESULT: "success"
  };
  const result = run(
    ["goal", "deliver demo closed loop", "--project", project, "--feature", "demo", "--mode", "delivery", "--max-iterations", "1", "--json"],
    { env }
  );
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  const runDir = join(project, ".beacon", "loop", "runs", payload.run_id);
  assert.ok(existsSync(join(runDir, "intent-capture.json")));
  assert.ok(existsSync(join(runDir, "review-artifact.json")));
  assert.equal(payload.closure_verdict, "not_provided_by_beacon_loop");
  const deliveryState = JSON.parse(readFileSync(join(runDir, "delivery-state.json"), "utf8"));
  assert.equal(deliveryState.state, "terminal_closed");
});

test("llm-tiebreak-green-light: ambiguous utterance continues without user_decision_pending (AC-040 / TC-042)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project),
    BEACON_LOOP_TEST_REVIEW: "fixture",
    BEACON_LOOP_TEST_TIEBREAK: "fixture"
  };
  const result = run(
    ["goal", "maybe improve something vague", "--project", project, "--mode", "review-only", "--json"],
    { env }
  );
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "review_complete");
  assert.notEqual(payload.status, "user_decision_pending");
  const runDir = join(project, ".beacon", "loop", "runs", payload.run_id);
  const tiebreak = JSON.parse(readFileSync(join(runDir, "intent-tiebreak.json"), "utf8"));
  assert.equal(tiebreak.tiebreak_authority, "llm_default_green_light");
  assert.equal(tiebreak.runtime_evidence_only, true);
  const contract = JSON.parse(readFileSync(join(runDir, "intent-contract.json"), "utf8"));
  assert.equal(contract.determinism.ambiguous, false);
  assert.equal(contract.determinism.tiebreak_applied, true);
  const deliveryState = JSON.parse(readFileSync(join(runDir, "delivery-state.json"), "utf8"));
  assert.equal(deliveryState.state, "truth_gap_scan");
});

test("parallel-review-lanes: parallel fixture writes per-lane refs (AC-041 / TC-043)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project),
    BEACON_LOOP_TEST_REVIEW: "parallel-fixture"
  };
  const result = run(
    ["goal", "beacon-loop orchestrator review", "--project", project, "--feature", "demo", "--mode", "review-only", "--json"],
    { env }
  );
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  const artifact = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "review-artifact.json"), "utf8"));
  assert.equal(artifact.execution_mode, "parallel_subagent_review");
  assert.ok(Array.isArray(artifact.review_lanes));
  assert.ok(artifact.review_lanes.length >= 2);
  assert.ok(artifact.review_lanes.every((lane) => lane.evidence_ref));
});

test("lifecycle-auto-route: P1 finding continues on recommended_route (AC-042 / TC-044)", () => {
  const project = makeProject();
  const env = {
    PATH: makeDeliveryBeaconShim(project),
    BEACON_LOOP_TEST_REVIEW: "fixture-p1"
  };
  const result = run(
    ["goal", "deliver demo", "--project", project, "--feature", "demo", "--mode", "review-only", "--json"],
    { env }
  );
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "review_complete");
  assert.notEqual(payload.status, "user_decision_pending");
  const artifact = JSON.parse(readFileSync(join(project, ".beacon", "loop", "runs", payload.run_id, "review-artifact.json"), "utf8"));
  assert.ok(artifact.findings.some((item) => item.severity === "P1"));
  assert.equal(artifact.synthesis.recommended_route, "truth_fill");
});
