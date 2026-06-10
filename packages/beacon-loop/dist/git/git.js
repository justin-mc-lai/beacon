import { existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

export function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd || process.cwd(),
    env: { ...process.env, ...(options.env || {}) },
    encoding: "utf8"
  });
  return {
    code: result.status ?? 1,
    stdout: result.stdout || "",
    stderr: result.stderr || ""
  };
}

export function isGitRepo(projectRoot) {
  return existsSync(join(projectRoot, ".git")) || run("git", ["rev-parse", "--git-dir"], { cwd: projectRoot }).code === 0;
}

export function gitStatus(projectRoot) {
  return run("git", ["status", "--porcelain"], { cwd: projectRoot }).stdout.trim();
}

export function currentHead(projectRoot) {
  return run("git", ["rev-parse", "HEAD"], { cwd: projectRoot }).stdout.trim();
}

export function createWorktree(projectRoot, runId) {
  const worktreePath = join(projectRoot, ".beacon", "loop", "worktrees", runId);
  const branch = `beacon-loop/${runId}`;
  const result = run("git", ["worktree", "add", "-b", branch, worktreePath, "HEAD"], { cwd: projectRoot });
  return { branch, worktreePath, result };
}

export function commitAll(worktreePath, message) {
  run("git", ["add", "-A"], { cwd: worktreePath });
  return run("git", ["commit", "-m", message], {
    cwd: worktreePath,
    env: {
      GIT_AUTHOR_NAME: process.env.GIT_AUTHOR_NAME || "Beacon Loop",
      GIT_AUTHOR_EMAIL: process.env.GIT_AUTHOR_EMAIL || "beacon-loop@example.invalid",
      GIT_COMMITTER_NAME: process.env.GIT_COMMITTER_NAME || "Beacon Loop",
      GIT_COMMITTER_EMAIL: process.env.GIT_COMMITTER_EMAIL || "beacon-loop@example.invalid"
    }
  });
}

export function rollback(worktreePath, head) {
  const reset = run("git", ["reset", "--hard", head], { cwd: worktreePath });
  const clean = run("git", ["clean", "-fd"], { cwd: worktreePath });
  return { reset, clean };
}
