import { existsSync } from "node:fs";
import { join } from "node:path";
import { createWorktree, currentHead, run } from "./git.js";

export const BRANCH_MODES = ["worktree", "current-branch", "run-branch"];

export function validateBranchMode(branchMode, options = {}) {
  if (!BRANCH_MODES.includes(branchMode)) {
    return { ok: false, reason_code: "invalid_branch_mode", next_route: "use worktree|current-branch|run-branch" };
  }
  if (branchMode === "current-branch" && options.isolatedWorktree) {
    return { ok: false, reason_code: "illegal_branch_mode_combo", detail: "current-branch cannot combine with isolated worktree" };
  }
  if (branchMode === "worktree" && options.runInPlace) {
    return { ok: false, reason_code: "illegal_branch_mode_combo", detail: "worktree cannot combine with run-in-place" };
  }
  return { ok: true };
}

export function currentBranchName(projectRoot) {
  return run("git", ["rev-parse", "--abbrev-ref", "HEAD"], { cwd: projectRoot }).stdout.trim();
}

export function resolveWorkspace(projectRoot, runId, branchMode, existing = null) {
  if (existing?.path && existsSync(existing.path)) {
    return { ...existing, branch_mode: branchMode || existing.branch_mode };
  }

  const head = currentHead(projectRoot);
  if (branchMode === "worktree") {
    const worktree = createWorktree(projectRoot, runId);
    return {
      branch: worktree.branch,
      path: worktree.worktreePath,
      base_head: head,
      branch_mode: "worktree",
      create_result: worktree.result
    };
  }

  if (branchMode === "current-branch") {
    return {
      branch: currentBranchName(projectRoot),
      path: projectRoot,
      base_head: head,
      branch_mode: "current-branch",
      create_result: { code: 0 }
    };
  }

  if (branchMode === "run-branch") {
    const branch = `beacon-loop/${runId}`;
    const createResult = run("git", ["checkout", "-b", branch], { cwd: projectRoot });
    return {
      branch,
      path: projectRoot,
      base_head: head,
      branch_mode: "run-branch",
      create_result: createResult
    };
  }

  return {
    branch: "",
    path: projectRoot,
    base_head: head,
    branch_mode: branchMode,
    create_result: { code: 1, stderr: "unknown branch mode" }
  };
}

export function workspaceLabel(workspace) {
  return join(workspace.path || "", workspace.branch || "");
}
