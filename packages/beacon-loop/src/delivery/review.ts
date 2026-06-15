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

function mapPlannerPayload(intentContract, payload) {
  const synthesis = payload.synthesis && typeof payload.synthesis === "object"
    ? payload.synthesis
    : { recommended_route: payload.recommended_route || "continue_delivery" };
  const reviewLanes = Array.isArray(payload.reviewer_lanes)
    ? payload.reviewer_lanes.map((lane) => ({
      lane: lane.lane || lane.reviewer || "unknown",
      status: lane.status || "completed",
      evidence_ref: lane.runtime_evidence_ref || lane.evidence_ref || ""
    }))
    : [];
  return {
    ...fixtureReview(intentContract),
    execution_mode: payload.execution_mode || "",
    review_lanes: reviewLanes,
    findings: Array.isArray(payload.findings) ? payload.findings : [],
    synthesis,
    parity_matrix: Array.isArray(payload.parity_matrix) ? payload.parity_matrix : [],
    deferral_ledger: Array.isArray(payload.deferral_ledger) ? payload.deferral_ledger : [],
    review_id: payload.review_id || "",
    planner_boundary: payload.planner_boundary || undefined,
    fallback_reason: payload.fallback_reason || ""
  };
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

  const prompt = String(intentContract.utterance || intentContract.feature_slug || "").trim();
  const args = [
    "planner-review",
    "run",
    intentContract.feature_slug || "unknown",
    "--project",
    projectRoot,
    "--version",
    intentContract.version || "auto",
    "--prompt",
    prompt || intentContract.feature_slug || "unknown",
    "--json"
  ];
  if (reviewEnv === "parallel" || process.env.BEACON_LOOP_REVIEW_PARALLEL === "1") {
    args.push("--execution-mode", "parallel_subagent_review");
  }
  const result = run("beacon", args, { cwd: projectRoot });
  if (result.code !== 0) {
    const artifact = fixtureReview(intentContract);
    artifact.findings = [{
      severity: "P1",
      code: "planner_review_subprocess_failed",
      text: result.stderr || result.stdout || "planner-review subprocess unavailable"
    }];
    artifact.synthesis = { recommended_route: "continue_delivery" };
    writeJson(outPath, artifact);
    return { status: "degraded", artifact, fallback: true, reason_code: "planner_review_subprocess_failed" };
  }
  try {
    const payload = JSON.parse(result.stdout);
    const artifact = mapPlannerPayload(intentContract, payload);
    writeJson(outPath, artifact);
    return { status: "pass", artifact, review_id: payload.review_id || "" };
  } catch (error) {
    const artifact = fixtureReview(intentContract);
    artifact.findings = [{
      severity: "P1",
      code: "planner_review_json_invalid",
      text: String(error)
    }];
    writeJson(outPath, artifact);
    return { status: "degraded", artifact, fallback: true, reason_code: "planner_review_json_invalid" };
  }
}
