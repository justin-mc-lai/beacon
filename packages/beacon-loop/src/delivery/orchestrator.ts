import { join } from "node:path";
import { writeJson, readJson } from "../runner/fs.js";
import { resolveTruth, isFeatureTruthFrozen } from "../beacon/resolve.js";
import { buildIntentCapture } from "../intent/capture.js";
import { classifyIntent } from "../intent/classify.js";
import { needsIntentTieBreak, runIntentTieBreak } from "../intent/tiebreak.js";
import { runDeliveryEvalChain } from "./eval-chain.js";
import { applyLifecycleRoute, shouldInterruptForReview } from "./review-gate.js";
import { runPlannerReview } from "./review.js";
import {
  defaultDeliveryState,
  readDeliveryState,
  transitionDeliveryState,
  writeDeliveryState
} from "./state.js";
import { runTruthFill, scanTruthGap } from "./truth-fill.js";
import { nowIso } from "../runner/types.js";

export function truthFrozen(resolver, projectRoot, version, feature) {
  return isFeatureTruthFrozen(projectRoot, version, feature, resolver);
}

export function writeIntentArtifacts(runDir, utterance, options) {
  const capture = buildIntentCapture(utterance);
  let contract = classifyIntent(utterance, options);
  writeJson(join(runDir, "intent-capture.json"), capture);
  if (needsIntentTieBreak(contract)) {
    const tiebreak = runIntentTieBreak(runDir, contract);
    contract = tiebreak.contract;
  }
  writeJson(join(runDir, "intent-contract.json"), contract);
  return { capture, contract };
}

export function initDeliveryState(runDir, runId) {
  const state = defaultDeliveryState(runId);
  writeDeliveryState(runDir, state);
  return state;
}

function deliveryReturn(base, runDir, mode) {
  return {
    ...base,
    delivery_mode: mode,
    delivery_state: readDeliveryState(runDir)?.state,
    closure_verdict: "not_provided_by_beacon_loop"
  };
}

export function runDeliveryPipeline(projectRoot, runDir, ctx) {
  const { goal, options, runPackage, dryRun } = ctx;
  const mode = options.mode || "delivery";
  initDeliveryState(runDir, runPackage.run_id);

  const { contract } = writeIntentArtifacts(runDir, goal, { ...options, mode });
  let step = transitionDeliveryState(runDir, "intent_review");
  if (!step.ok) return deliveryReturn({ status: "blocked", reason_code: step.reason_code }, runDir, mode);

  if (mode === "intent-only") {
    return deliveryReturn({
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: dryRun ? "dry_run" : "intent_captured",
      run_id: runPackage.run_id,
      run_dir: runDir
    }, runDir, mode);
  }

  const review = runPlannerReview(projectRoot, runDir, contract);

  const reviewInterrupt = shouldInterruptForReview(review.artifact, options);
  if (reviewInterrupt.interrupt) {
    transitionDeliveryState(runDir, "user_decision_pending");
    return deliveryReturn({
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: "user_decision_pending",
      reason_code: reviewInterrupt.reason_code,
      run_id: runPackage.run_id,
      run_dir: runDir
    }, runDir, mode);
  }

  const lifecycle = applyLifecycleRoute(review.artifact);
  if (!lifecycle.continueDelivery) {
    transitionDeliveryState(runDir, lifecycle.route === "terminal_aborted" ? "terminal_aborted" : "user_decision_pending");
    return deliveryReturn({
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: lifecycle.route === "terminal_aborted" ? "blocked" : "user_decision_pending",
      reason_code: lifecycle.reason_code,
      recommended_route: lifecycle.route,
      run_id: runPackage.run_id,
      run_dir: runDir
    }, runDir, mode);
  }

  step = transitionDeliveryState(runDir, "truth_gap_scan");
  if (!step.ok) return deliveryReturn({ status: "blocked", reason_code: step.reason_code }, runDir, mode);

  if (mode === "review-only") {
    return deliveryReturn({
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: dryRun ? "dry_run" : "review_complete",
      run_id: runPackage.run_id,
      run_dir: runDir,
      review_status: review.status
    }, runDir, mode);
  }

  const feature = String(options.feature || contract.feature_slug || "").trim();
  if (!feature) {
    transitionDeliveryState(runDir, "terminal_aborted");
    return deliveryReturn({
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: "blocked",
      reason_code: "feature_slug_required",
      next_route: "beacon-gen-change",
      run_id: runPackage.run_id
    }, runDir, mode);
  }
  runPackage.feature = feature;

  let gap = scanTruthGap(projectRoot, runPackage.version, feature, review.artifact);
  if (gap.blocked || gap.deferPending) {
    step = transitionDeliveryState(runDir, "truth_fill");
    if (!step.ok) return deliveryReturn({ status: "blocked", reason_code: step.reason_code }, runDir, mode);
    const fill = runTruthFill(projectRoot, runDir, {
      version: runPackage.version,
      feature,
      reviewArtifact: review.artifact,
      utterance: goal
    });
    step = transitionDeliveryState(runDir, "truth_freeze_gate");
    if (!step.ok) return deliveryReturn({ status: "blocked", reason_code: step.reason_code }, runDir, mode);
    if (fill.status === "blocked") {
      transitionDeliveryState(runDir, "terminal_aborted");
      return deliveryReturn({
        schema_version: "1.0",
        surface: "beacon-loop",
        command: "goal",
        status: "blocked",
        reason_code: fill.reason_code || "truth_fill_blocked",
        run_id: runPackage.run_id
      }, runDir, mode);
    }
    gap = scanTruthGap(projectRoot, runPackage.version, feature, review.artifact);
  }

  const frozen = truthFrozen(gap.resolver, projectRoot, runPackage.version, feature);
  if (!frozen) {
    if (dryRun) {
      return deliveryReturn({
        schema_version: "1.0",
        surface: "beacon-loop",
        command: "goal",
        status: "dry_run",
        run_id: runPackage.run_id,
        run_dir: runDir
      }, runDir, mode);
    }
    transitionDeliveryState(runDir, "terminal_aborted");
    return deliveryReturn({
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: "blocked",
      reason_code: "truth_not_frozen",
      run_id: runPackage.run_id
    }, runDir, mode);
  }

  step = transitionDeliveryState(runDir, "implement_loop", { truthFrozen: frozen });
  if (!step.ok) {
    return deliveryReturn({
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: "blocked",
      reason_code: "illegal_delivery_transition",
      run_id: runPackage.run_id
    }, runDir, mode);
  }

  writeJson(join(runDir, "run-package.json"), {
    ...runPackage,
    delivery_mode: mode,
    intent_refs: { capture: "intent-capture.json", contract: "intent-contract.json", review: "review-artifact.json" }
  });

  if (dryRun) {
    return deliveryReturn({
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: "dry_run",
      run_id: runPackage.run_id,
      run_dir: runDir
    }, runDir, mode);
  }

  return { continueImplement: true, feature, resolver: gap.resolver, review };
}

export function finalizeDeliveryAfterImplement(projectRoot, runDir, runPackage, implementResult, options) {
  const mode = options.mode || "delivery";
  if (mode !== "delivery") return implementResult;

  const commitsDoc = readJson(join(runDir, "commits.json"), { commits: [] });
  const commitCount = Array.isArray(commitsDoc.commits) ? commitsDoc.commits.length : 0;
  const noOpBlocked =
    commitCount === 0 ||
    implementResult.status === "rolled_back" ||
    implementResult.reason_code === "consecutive_failures_abort";

  if (noOpBlocked) {
    transitionDeliveryState(runDir, "implement_loop", { truthFrozen: true });
    const deliveryState = readDeliveryState(runDir);
    writeDeliveryState(runDir, {
      ...deliveryState,
      reason_code: "implement_no_op_blocked",
      blocked_at: nowIso(),
      commit_count: commitCount
    });
    return {
      ...implementResult,
      status: "blocked",
      reason_code: "implement_no_op_blocked",
      closure_verdict: "not_provided_by_beacon_loop",
      delivery_state: readDeliveryState(runDir)?.state
    };
  }

  let step = transitionDeliveryState(runDir, "evidence_import");
  if (!step.ok) return { ...implementResult, reason_code: step.reason_code };
  step = transitionDeliveryState(runDir, "qa_pending");
  if (!step.ok) return { ...implementResult, reason_code: step.reason_code };

  const evalResult = runDeliveryEvalChain(projectRoot, runDir, runPackage);
  if (evalResult.status === "qa_failed") {
    transitionDeliveryState(runDir, "repair_from_qa");
    return {
      ...implementResult,
      delivery_eval: evalResult,
      status: "repair_from_qa",
      reason_code: "beacon_qa_failed",
      closure_verdict: "not_provided_by_beacon_loop"
    };
  }

  transitionDeliveryState(runDir, "release_pending", { releaseInvoked: true });
  if (evalResult.status === "completed") {
    transitionDeliveryState(runDir, "terminal_closed", { releaseInvoked: true });
  }

  writeJson(join(runDir, "run-package.json"), {
    ...runPackage,
    delivery_mode: mode,
    closure_verdict: "not_provided_by_beacon_loop",
    beacon_qa_verdict_ref: evalResult.beacon_qa_verdict_ref,
    beacon_release_verdict_ref: evalResult.beacon_release_verdict_ref,
    delivery_completed_at: nowIso()
  });

  return {
    ...implementResult,
    delivery_eval: evalResult,
    closure_verdict: "not_provided_by_beacon_loop",
    beacon_qa_verdict_ref: evalResult.beacon_qa_verdict_ref,
    beacon_release_verdict_ref: evalResult.beacon_release_verdict_ref,
    delivery_state: readDeliveryState(runDir)?.state
  };
}
