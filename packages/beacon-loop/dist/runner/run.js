import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { commitAll, createWorktree, currentHead, gitStatus, isGitRepo, rollback } from "../git/git.js";
import { resolveTruth } from "../beacon/resolve.js";
import { runCodexAdapter } from "../agents/codex.js";
import { ensureDir, readJson, writeJson, writeText } from "./fs.js";
import { RUNTIME_ROLE, nowIso, slugify } from "./types.js";

export function createRunId() {
  return `run-${new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14)}-${Math.random().toString(36).slice(2, 8)}`;
}

function refsFromResolver(resolver) {
  const sourcePaths = resolver.source_paths || {};
  return {
    truth_refs: sourcePaths.truth ? [sourcePaths.truth] : [],
    test_refs: sourcePaths.tests ? [sourcePaths.tests] : [],
    task_refs: sourcePaths.tasks ? [sourcePaths.tasks] : [],
    evidence_refs: sourcePaths.evidence ? [sourcePaths.evidence] : []
  };
}

function writeRuntimeFiles(runDir, runPackage, resolver, result = {}) {
  writeJson(join(runDir, "run-package.json"), runPackage);
  writeText(join(runDir, "prompt.md"), `# Beacon Loop Prompt\n\nGoal: ${runPackage.goal}\nFeature: ${runPackage.feature}\n\nUse resolver-selected truth only. Do not claim QA pass, release ready, or feature complete.\n`);
  if (!existsSync(join(runDir, "notes.md"))) writeText(join(runDir, "notes.md"), "# Notes\n\n");
  writeJson(join(runDir, "output-schema.json"), {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    required: ["success", "summary", "key_changes_made", "key_learnings"]
  });
  const evidence = {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    surface: "beacon-loop",
    status: result.status || "candidate",
    closure_verdict: "not_provided_by_beacon_loop",
    feature: runPackage.feature,
    version: runPackage.version,
    run_id: runPackage.run_id,
    changed_files: result.changed_files || [],
    summary_ref: `.beacon/loop/runs/${runPackage.run_id}/summary.md`,
    resolver_command: resolver.command
  };
  writeJson(join(runDir, "evidence.json"), evidence);
  writeText(join(runDir, "summary.md"), `# Beacon Loop Summary\n\n- run_id: ${runPackage.run_id}\n- status: ${evidence.status}\n- closure_verdict: not_provided_by_beacon_loop\n- qa_release_boundary: Beacon QA/release surfaces remain authoritative.\n`);
}

export function startGoal(projectRoot, goal, options = {}) {
  const version = options.version || "v1.6.0";
  const feature = slugify(options.feature || goal);
  const resolver = resolveTruth(projectRoot, version, feature);
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
  if (!isGitRepo(projectRoot)) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "blocked", reason_code: "git_repo_required" };
  }
  const dirty = gitStatus(projectRoot);
  if (dirty && !options.allowDirty) {
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "blocked", reason_code: "dirty_worktree_blocked", next_route: "clean-worktree-or-use-controlled-mode" };
  }

  const runId = options.runId || createRunId();
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  ensureDir(runDir);
  const refs = refsFromResolver(resolver);
  const runPackage = {
    schema_version: "1.0",
    runtime_json_role: RUNTIME_ROLE,
    surface: "beacon-loop",
    command: "goal",
    run_id: runId,
    goal,
    feature,
    version,
    ...refs,
    agent: options.agent || "codex",
    branch_mode: options.branchMode || "worktree",
    push: false,
    max_iterations: Number(options.maxIterations || 1),
    max_tokens: Number(options.maxTokens || 0),
    stop_when: options.stopWhen || "resolver-selected tests have an implementation evidence candidate",
    beacon_commands: {
      resolve_truth: resolver.command,
      import_evidence: `beacon implement import-evidence ${feature} --project ${projectRoot} --version ${version}`,
      qa: `beacon qa run ${feature} --project ${projectRoot} --version ${version}`,
      release: `beacon release create --project ${projectRoot} --version ${version}`
    },
    created_at: nowIso()
  };

  if (options.dryRun) {
    writeText(join(runDir, "iteration-001.jsonl"), `${JSON.stringify({ event: "dry_run", at: nowIso() })}\n`);
    writeJson(join(runDir, "iteration-001-result.json"), { success: false, dry_run: true, summary: "dry-run runtime package created", key_changes_made: [], key_learnings: [] });
    writeJson(join(runDir, "commits.json"), { commits: [], repair_state: "" });
    writeRuntimeFiles(runDir, runPackage, resolver, { status: "dry_run" });
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "dry_run", run_id: runId, run_dir: runDir, closure_verdict: "not_provided_by_beacon_loop" };
  }

  const head = currentHead(projectRoot);
  const worktree = createWorktree(projectRoot, runId);
  runPackage.worktree = { branch: worktree.branch, path: worktree.worktreePath, base_head: head };
  if (worktree.result.code !== 0) {
    writeJson(join(runDir, "repair-state.json"), { status: "repair_required", reason_code: "worktree_create_failed", stderr: worktree.result.stderr });
    writeRuntimeFiles(runDir, runPackage, resolver, { status: "repair_required" });
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "blocked", reason_code: "worktree_create_failed", run_id: runId };
  }

  const prompt = `Beacon loop implementation iteration.

Goal: ${goal}
Feature: ${feature}
Version: ${version}
Truth refs: ${refs.truth_refs.join(", ")}
Test refs: ${refs.test_refs.join(", ")}
Stop when: ${runPackage.stop_when}

Emit JSON with: success, summary, key_changes_made, key_learnings.
Do not claim QA pass, release readiness, or feature completion.`;
  const iteration = runCodexAdapter(worktree.worktreePath, runId, {
    prompt,
    maxTokens: runPackage.max_tokens,
    stopWhen: runPackage.stop_when
  });
  writeText(join(runDir, "iteration-001.jsonl"), `${JSON.stringify({ event: "agent_result", at: nowIso(), iteration })}\n`);
  writeJson(join(runDir, "iteration-001-result.json"), iteration);
  if (!iteration.success) {
    const rollbackResult = rollback(worktree.worktreePath, head);
    writeJson(join(runDir, "commits.json"), { commits: [], rollback: rollbackResult });
    writeRuntimeFiles(runDir, runPackage, resolver, { status: "rolled_back" });
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "rolled_back", run_id: runId, closure_verdict: "not_provided_by_beacon_loop" };
  }
  if (iteration.force_commit_failure) {
    writeJson(join(runDir, "repair-state.json"), { status: "repair_required", reason_code: "commit_failure_repair_required" });
    writeJson(join(runDir, "commits.json"), { commits: [], repair_state: "commit_failure_repair_required" });
    writeRuntimeFiles(runDir, runPackage, resolver, { status: "repair_required" });
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "repair_required", reason_code: "commit_failure_repair_required", run_id: runId };
  }
  const commit = commitAll(worktree.worktreePath, `beacon-loop: ${feature} ${runId}`);
  if (commit.code !== 0) {
    writeJson(join(runDir, "repair-state.json"), { status: "repair_required", reason_code: "commit_failure_repair_required", stderr: commit.stderr });
    writeJson(join(runDir, "commits.json"), { commits: [], repair_state: "commit_failure_repair_required" });
    writeRuntimeFiles(runDir, runPackage, resolver, { status: "repair_required" });
    return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "repair_required", reason_code: "commit_failure_repair_required", run_id: runId };
  }
  const commitHash = commit.stdout.match(/[a-f0-9]{7,40}/)?.[0] || "";
  writeJson(join(runDir, "commits.json"), { commits: [{ iteration: 1, commit: commitHash, message: `beacon-loop: ${feature} ${runId}` }] });
  writeRuntimeFiles(runDir, runPackage, resolver, { status: "implementation_candidate", changed_files: iteration.key_changes_made });
  return { schema_version: "1.0", surface: "beacon-loop", command: "goal", status: "implementation_candidate", run_id: runId, commit: commitHash, closure_verdict: "not_provided_by_beacon_loop" };
}

export function resumeRun(projectRoot, runId) {
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  const runPackage = readJson(join(runDir, "run-package.json"), null);
  if (!runPackage) return { schema_version: "1.0", surface: "beacon-loop", command: "resume", status: "blocked", reason_code: "run_not_found" };
  const notesPath = join(runDir, "notes.md");
  const previousNotes = existsSync(notesPath) ? readFileSync(notesPath, "utf8") : "# Notes\n\n";
  writeText(notesPath, `${previousNotes.replace(/\s*$/, "\n")}- resumed_at: ${nowIso()}\n`);
  const payload = { schema_version: "1.0", runtime_json_role: RUNTIME_ROLE, surface: "beacon-loop", command: "resume", status: "resumed", run_id: runId, worktree: runPackage.worktree || {}, notes_ref: `.beacon/loop/runs/${runId}/notes.md` };
  writeJson(join(runDir, "resume-result.json"), payload);
  return payload;
}

export function stopRun(projectRoot, runId, force = false) {
  const runDir = join(projectRoot, ".beacon", "loop", "runs", runId);
  ensureDir(runDir);
  const payload = { schema_version: "1.0", runtime_json_role: RUNTIME_ROLE, surface: "beacon-loop", command: "stop", status: force ? "force_stop_requested" : "graceful_stop_requested", run_id: runId, created_at: nowIso() };
  writeJson(join(runDir, "stop.json"), payload);
  return payload;
}

export function statusRun(projectRoot, runId = "") {
  const id = runId || "";
  if (id) {
    const runDir = join(projectRoot, ".beacon", "loop", "runs", id);
    return { schema_version: "1.0", surface: "beacon-loop", command: "status", run_id: id, exists: existsSync(runDir), run_package: readJson(join(runDir, "run-package.json"), {}) };
  }
  const root = join(projectRoot, ".beacon", "loop", "runs");
  mkdirSync(root, { recursive: true });
  return { schema_version: "1.0", surface: "beacon-loop", command: "status", runs_root: root };
}
