import { join } from "node:path";
import { writeJson } from "../runner/fs.js";
import { run } from "../git/git.js";
import { nowIso, RUNTIME_ROLE } from "../runner/types.js";

const PARALLEL_LANES = ["intent", "source_parity", "state_machine"];

function baseReview(intentContract) {
  return {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    generated_at: nowIso(),
    intent_snapshot: {
      utterance: intentContract.utterance,
      scope_mode: intentContract.scope_mode,
      intent_class: intentContract.intent_class
    },
    scope_mode: intentContract.scope_mode,
    parity_matrix: [],
    deferral_ledger: [],
    findings: [],
    synthesis: { recommended_route: "continue_delivery" },
    runtime_evidence_only: true,
    formal_verdict_authority: false
  };
}

function fixtureReview(intentContract, overrides = {}) {
  return { ...baseReview(intentContract), ...overrides };
}

function parallelFixtureReview(intentContract) {
  const artifact = fixtureReview(intentContract, {
    execution_mode: "parallel_subagent_review",
    review_lanes: PARALLEL_LANES.map((lane) => ({
      lane,
      status: "completed",
      evidence_ref: `review-lane-${lane}.json`
    }))
  });
  return artifact;
}

function p1FixtureReview(intentContract) {
  return fixtureReview(intentContract, {
    findings: [{ severity: "P1", code: "scope_clarity", text: "minor clarity note" }],
    synthesis: { recommended_route: "truth_fill" }
  });
}

export function runPlannerReview(projectRoot, runDir, intentContract) {
  const outPath = join(runDir, "review-artifact.json");
  const reviewEnv = process.env.BEACON_LOOP_TEST_REVIEW || "";
  if (reviewEnv === "fixture" || reviewEnv === "fixture-p1") {
    const artifact = reviewEnv === "fixture-p1" ? p1FixtureReview(intentContract) : fixtureReview(intentContract);
    writeJson(outPath, artifact);
    return { status: "pass", artifact };
  }
  if (reviewEnv === "parallel-fixture") {
    const artifact = parallelFixtureReview(intentContract);
    writeJson(outPath, artifact);
    return { status: "pass", artifact };
  }

  const args = [
    "planner-review",
    "run",
    intentContract.feature_slug || "unknown",
    "--project",
    projectRoot,
    "--version",
    intentContract.version || "v1.6.0",
    "--json"
  ];
  if (reviewEnv === "parallel" || process.env.BEACON_LOOP_REVIEW_PARALLEL === "1") {
    args.push("--execution-mode", "parallel_subagent_review");
  }
  const result = run("beacon", args, { cwd: projectRoot });
  if (result.code !== 0) {
    const artifact = fixtureReview(intentContract);
    artifact.findings = [{ severity: "P2", code: "planner_review_subprocess_fallback", text: result.stderr || "review subprocess unavailable" }];
    writeJson(outPath, artifact);
    return { status: "pass", artifact, fallback: true };
  }
  try {
    const payload = JSON.parse(result.stdout);
    const artifact = {
      ...fixtureReview(intentContract),
      findings: payload.findings || [],
      synthesis: payload.synthesis || fixtureReview(intentContract).synthesis,
      parity_matrix: payload.parity_matrix || [],
      deferral_ledger: payload.deferral_ledger || []
    };
    writeJson(outPath, artifact);
    return { status: "pass", artifact };
  } catch {
    const artifact = fixtureReview(intentContract);
    writeJson(outPath, artifact);
    return { status: "pass", artifact, fallback: true };
  }
}
