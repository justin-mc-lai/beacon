import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { resolveProjectVersion } from "../beacon/version.js";
import { isGitRepo, gitStatus } from "../git/git.js";
import { resolveTruth, isFeatureTruthFrozen } from "../beacon/resolve.js";
import { ensureDir, readJson, writeJson, writeText } from "./fs.js";
import { runOrchestrator } from "./orchestrator.js";
import { validateBranchMode, resolveWorkspace } from "../git/branches.js";
import { RUNTIME_ROLE, nowIso } from "./types.js";
import { syncRunToLedger } from "../ledger/runs.js";
import { defaultRunState } from "./state.js";
import { classifyIntent } from "../intent/classify.js";
import { finalizeDeliveryAfterImplement, runDeliveryPipeline } from "../delivery/orchestrator.js";
import { readDeliveryState, transitionDeliveryState } from "../delivery/state.js";

export function createRunId() {
  return `run-${new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14)}-${Math.random().toString(36).slice(2, 8)}`;
}

function refsFromResolver(resolver) {
  const sourcePaths = resolver.source_paths || resolver.payload?.feature_truth?.source_paths || {};
  return {
    truth_refs: sourcePaths.truth ? [sourcePaths.truth] : [],
    test_refs: sourcePaths.tests ? [sourcePaths.tests] : [],
    task_refs: sourcePaths.tasks ? [sourcePaths.tasks] : [],
    evidence_refs: sourcePaths.evidence ? [sourcePaths.evidence] : []
  };
}

function bootstrapRuntimeFiles(runDir, runPackage, resolver) {
  writeJson(join(runDir, "run-package.json"), runPackage);
  writeText(join(runDir, "prompt.md"), `# Beacon Loop Prompt\n\nGoal: ${runPackage.goal}\nFeature: ${runPackage.feature}\n\nUse resolver-selected truth only. Do not claim QA pass, release ready, or feature complete.\n`);
  if (!existsSync(join(runDir, "notes.md"))) writeText(join(runDir, "notes.md"), "# Notes\n\n");
  writeJson(join(runDir, "output-schema.json"), {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    required: ["success", "summary", "key_changes_made", "key_learnings"]
  });
  writeJson(join(runDir, "commits.json"), { commits: [], repair_state: "" });
  writeJson(join(runDir, "run-state.json"), { ...defaultRunState(), started_at: nowIso() });
  writeJson(join(runDir, "evidence.json"), {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    surface: "beacon-loop",
    status: "initialized",
    closure_verdict: "not_provided_by_beacon_loop",
    feature: runPackage.feature,
    version: runPackage.version,
    run_id: runPackage.run_id,
    resolver_command: resolver.command || ""
  });
}

export function startGoal(projectRoot, goal, options = {}) {
  const version = resolveProjectVersion(projectRoot, options.version || "auto");
  const mode = options.mode || "delivery";
  const featureHint = String(options.feature || "").trim();

  let feature = featureHint;
  if (mode === "execute-only" && !feature) {
    feature = classifyIntent(goal, { mode: "execute-only", version, feature: featureHint }).feature_slug;
  }
  if (mode === "execute-only" && !feature) {
    return {
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: "blocked",
      reason_code: "feature_required_for_execute_only",
      next_route: "beacon-gen-change"
    };
  }

  if (!isGitRepo(projectRoot)) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "blocked", reason_code: "git_repo_required" };
  }
  const dirty = gitStatus(projectRoot);
  if (dirty && !options.allowDirty) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "blocked", reason_code: "dirty_worktree_blocked", next_route: "clean-worktree-or-use-controlled-mode" };
  }

  const branchValidation = validateBranchMode(options.branchMode || "worktree", {
    isolatedWorktree: options.isolatedWorktree,
    runInPlace: options.runInPlace
  });
  if (!branchValidation.ok) {
    return {
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "goal",
      status: "blocked",
      reason_code: branchValidation.reason_code,
      detail: branchValidation.detail || "",
      next_route: branchValidation.next_route || "fix-branch-mode-flags"
    };
  }

  const runId = options.runId || createRunId();
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  ensureDir(runDir);

  let resolver = { command: "", source_paths: {}, blocked: false, payload: {} };

  if (mode === "execute-only") {
    resolver = resolveTruth(projectRoot, version, feature);
    if (resolver.blocked) {
      return {
        schema_version: "1.0",
        surface: "beacon-loop",
        command: "goal",
        status: "blocked",
        reason_code: resolver.reason_code,
        next_route: "beacon-gen-change",
        resolver_command: resolver.command
      };
    }
    if (!isFeatureTruthFrozen(projectRoot, version, feature, resolver)) {
      return {
        schema_version: "1.0",
        surface: "beacon-loop",
        command: "goal",
        status: "blocked",
        reason_code: "truth_not_frozen",
        next_route: "beacon-freeze"
      };
    }
  }

  const refs = refsFromResolver(resolver);
  const maxIterations = Math.max(1, Number(options.maxIterations || 1));
  const runPackage = {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    surface: "beacon-loop",
    command: "goal",
    run_id: runId,
    goal,
    feature: feature || "",
    version,
    delivery_mode: mode,
    ...refs,
    agent: options.agent || "codex",
    branch_mode: options.branchMode || "worktree",
    push: false,
    max_iterations: maxIterations,
    max_tokens: Number(options.maxTokens || 0),
    stop_when: options.stopWhen || "resolver-selected tests have an implementation evidence candidate",
    beacon_commands: {
      resolve_truth: resolver.command || `beacon truth-map resolve ${feature || "<feature>"} --project ${projectRoot} --version ${version} --json`,
      import_evidence: `beacon implement import-evidence ${feature || "<feature>"} --project ${projectRoot} --version ${version}`,
      qa: `beacon qa run ${feature || "<feature>"} --project ${projectRoot} --version ${version}`,
      release: `beacon release create --project ${projectRoot} --version ${version}`
    },
    created_at: nowIso()
  };

  bootstrapRuntimeFiles(runDir, runPackage, resolver);

  if (mode !== "execute-only") {
    const pipeline = runDeliveryPipeline(projectRoot, runDir, { goal, options: { ...options, mode }, runPackage, dryRun: options.dryRun });
    if (!pipeline.continueImplement) {
      if (pipeline.status === "dry_run") {
        writeText(join(runDir, "iteration-001.jsonl"), `${JSON.stringify({ event: "dry_run", at: nowIso() })}\n`);
        writeJson(join(runDir, "iteration-001-result.json"), { success: false, dry_run: true, summary: "dry-run runtime package created", key_changes_made: [], key_learnings: [] });
        writeText(join(runDir, "summary.md"), `# Beacon Loop Summary\n\n- run_id: ${runId}\n- status: dry_run\n- delivery_mode: ${mode}\n`);
        try {
          syncRunToLedger(projectRoot, runId, { status: "dry_run", machine_state: "run_initialized", iteration: 0, goal, feature: runPackage.feature, version });
        } catch {
          // best-effort
        }
      }
      return pipeline;
    }
    feature = pipeline.feature;
    resolver = pipeline.resolver || resolveTruth(projectRoot, version, feature);
    runPackage.feature = feature;
    Object.assign(runPackage, refsFromResolver(resolver));
    writeJson(join(runDir, "run-package.json"), runPackage);
  }

  if (options.dryRun) {
    writeText(join(runDir, "iteration-001.jsonl"), `${JSON.stringify({ event: "dry_run", at: nowIso() })}\n`);
    writeJson(join(runDir, "iteration-001-result.json"), { success: false, dry_run: true, summary: "dry-run runtime package created", key_changes_made: [], key_learnings: [] });
    writeText(join(runDir, "summary.md"), `# Beacon Loop Summary\n\n- run_id: ${runId}\n- status: dry_run\n`);
    try {
      syncRunToLedger(projectRoot, runId, { status: "dry_run", machine_state: "run_initialized", iteration: 0, goal, feature, version });
    } catch {
      // harness ledger is best-effort for dry-run
    }
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "dry_run", run_id: runId, run_dir: runDir, delivery_mode: mode, closure_verdict: "not_provided_by_beacon_loop" };
  }

  const workspace = resolveWorkspace(projectRoot, runId, runPackage.branch_mode, null);
  if (workspace.create_result?.code !== 0 && !existsSync(workspace.path)) {
    writeJson(join(runDir, "repair-state.json"), { status: "repair_required", reason_code: "workspace_create_failed", stderr: workspace.create_result?.stderr || "" });
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "blocked", reason_code: "workspace_create_failed", run_id: runId };
  }
  runPackage.worktree = { branch: workspace.branch, path: workspace.path, base_head: workspace.base_head, branch_mode: workspace.branch_mode };
  writeJson(join(runDir, "run-package.json"), runPackage);

  const result = runOrchestrator(projectRoot, runDir, runPackage, resolver, { command: "goal", startIteration: 1 });
  const finalized = finalizeDeliveryAfterImplement(projectRoot, runDir, runPackage, result, { ...options, mode });
  if (finalized.status === "implementation_candidate" || finalized.status === "cap_reached" || finalized.status === "repair_from_qa") {
    return { ...finalized, commit: readJson(join(runDir, "commits.json"), {}).commits?.at(-1)?.commit || "" };
  }
  return finalized;
}

export function resumeRun(projectRoot, runId) {
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  const runPackage = readJson(join(runDir, "run-package.json"), null);
  if (!runPackage) return { schema_version: "1.0", surface: "beacon-loop", command: "resume", status: "blocked", reason_code: "run_not_found" };

  const deliveryState = readDeliveryState(runDir);
  if (deliveryState?.state === "repair_from_qa") {
    transitionDeliveryState(runDir, "implement_loop", { truthFrozen: true });
    appendResumeNote(runDir, "- resumed_from: repair_from_qa\n");
  } else if (deliveryState?.state === "user_decision_pending") {
    transitionDeliveryState(runDir, "truth_gap_scan");
    appendResumeNote(runDir, "- resumed_from: user_decision_pending\n");
  }

  const runState = readJson(join(runDir, "run-state.json"), {});
  const repair = readJson(join(runDir, "repair-state.json"), null);
  const resumable = ["repair_required", "cap_reached", "force_stopped", "implementation_candidate", "iteration_success_commit", "iteration_fail_rollback", "waiting_backoff", "graceful_stop_pending"].includes(runState.machine_state)
    || Boolean(repair?.status === "repair_required")
    || deliveryState?.state === "repair_from_qa"
    || deliveryState?.state === "user_decision_pending";

  if (!resumable && runState.iteration >= runPackage.max_iterations) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "resume", status: "blocked", reason_code: "run_not_resumable", run_id: runId };
  }

  appendResumeNote(runDir);
  const branchMode = runPackage.branch_mode || runPackage.worktree?.branch_mode || "worktree";
  const workspace = resolveWorkspace(projectRoot, runId, branchMode, runPackage.worktree);
  runPackage.worktree = { branch: workspace.branch, path: workspace.path, base_head: workspace.base_head || runPackage.worktree?.base_head, branch_mode: workspace.branch_mode };

  const retryRepair = repair?.status === "repair_required";
  const nextIteration = retryRepair ? Number(runState.iteration || 1) : Number(runState.iteration || 0) + 1;
  if (nextIteration > runPackage.max_iterations) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "resume", status: "blocked", reason_code: "max_iterations_reached", run_id: runId };
  }

  writeJson(join(runDir, "interrupt-state.json"), { cleared_at: nowIso() });
  const resolver = { command: runPackage.beacon_commands?.resolve_truth || "" };
  const result = runOrchestrator(projectRoot, runDir, runPackage, resolver, {
    command: "resume",
    startIteration: nextIteration
  });
  const mode = runPackage.delivery_mode || "delivery";
  const finalized = finalizeDeliveryAfterImplement(projectRoot, runDir, runPackage, result, { mode });
  return { ...finalized, resumed_from_iteration: runState.iteration, next_iteration: nextIteration, delivery_state: readDeliveryState(runDir)?.state };
}

function appendResumeNote(runDir, extra = "") {
  const notesPath = join(runDir, "notes.md");
  const previous = existsSync(notesPath) ? readFileSync(notesPath, "utf8") : "# Notes\n\n";
  writeText(notesPath, `${previous.replace(/\s*$/, "\n")}- resumed_at: ${nowIso()}\n${extra}`);
}

export function stopRun(projectRoot, runId, force = false) {
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  ensureDir(runDir);
  const payload = {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    surface: "beacon-loop",
    command: "stop",
    mode: force ? "force" : "graceful",
    status: force ? "force_stop_requested" : "graceful_stop_requested",
    run_id: runId,
    created_at: nowIso()
  };
  writeJson(join(runDir, "interrupt-state.json"), payload);
  writeJson(join(runDir, "stop.json"), payload);

  const runStatePath = join(runDir, "run-state.json");
  const runState = readJson(runStatePath, defaultRunState());
  if (force) {
    runState.machine_state = "force_stopped";
    runState.stop_reason = "force_stop_requested";
    runState.finished_at = nowIso();
    writeJson(runStatePath, runState);
    payload.status = "force_stopped";
  }
  return payload;
}

export function statusRun(projectRoot, runId = "") {
  const id = runId || "";
  if (id) {
    const runDir = join(projectRoot, ".beacon", "loop", "runs", id);
    return {
      schema_version: "1.0",
      surface: "beacon-loop",
      command: "status",
      run_id: id,
      exists: existsSync(runDir),
      run_package: readJson(join(runDir, "run-package.json"), {}),
      run_state: readJson(join(runDir, "run-state.json"), {}),
      delivery_state: readDeliveryState(runDir)
    };
  }
  const root = join(projectRoot, ".beacon", "loop", "runs");
  ensureDir(root);
  return { schema_version: "1.0", surface: "beacon-loop", command: "status", runs_root: root };
}
