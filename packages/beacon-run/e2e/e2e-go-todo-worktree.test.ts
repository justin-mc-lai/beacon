import { execFileSync, spawnSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const distCliPath = join(repoRoot, "packages/beacon-run/dist/cli.mjs");
const enabled = process.env.BEACON_RUN_E2E_GO_TODO === "1";

function git(args: string[], cwd: string): string {
  return execFileSync("git", args, {
    cwd,
    encoding: "utf-8",
    stdio: ["ignore", "pipe", "pipe"],
  }).trim();
}

function seedGoTodoSmokeTruth(cwd: string): void {
  const feature = "go-todo-crud-smoke";
  const version = "v1.6.0";
  const featureDir = join(cwd, "docs/beacon", version, "features", feature);
  mkdirSync(featureDir, { recursive: true });
  writeFileSync(join(cwd, "docs/beacon/VERSION"), `${version}\n`, "utf-8");
  writeFileSync(
    join(featureDir, "truth.md"),
    `---\nstatus: frozen\nrevision_id: R1\nslug: ${feature}\nscope_mode: smoke\n---\n\n# ${feature}\n`,
    "utf-8",
  );
  writeFileSync(join(featureDir, "tests.md"), `# Tests\n\n| AC | TC |\n`, "utf-8");
  writeFileSync(join(featureDir, "tasks.md"), `# Tasks\n`, "utf-8");
  writeFileSync(join(featureDir, "evidence.md"), `# Evidence\n`, "utf-8");
  git(["add", "-A"], cwd);
  git(["commit", "-m", "seed go-todo smoke truth"], cwd);
}

describe.skipIf(!enabled)("e2e go-todo worktree harness (BEACON_RUN_E2E_GO_TODO=1)", () => {
  it("runs beacon-run --worktree --beacon with harness project-root in worktree", () => {
    expect(existsSync(distCliPath)).toBe(true);
    const cwd = mkdtempSync(join(tmpdir(), "beacon-go-todo-e2e-"));
    try {
      git(["init", "-b", "main"], cwd);
      git(["config", "user.name", "e2e"], cwd);
      git(["config", "user.email", "e2e@test.invalid"], cwd);
      writeFileSync(join(cwd, "README.md"), "# fixture\n", "utf-8");
      git(["add", "README.md"], cwd);
      git(["commit", "-m", "init"], cwd);
      seedGoTodoSmokeTruth(cwd);

      const loopCli = join(repoRoot, "packages/beacon-loop/dist/cli.js");
      const result = spawnSync(
        process.execPath,
        [
          loopCli,
          "goal",
          "smoke go todo crud",
          "--project",
          cwd,
          "--version",
          "v1.6.0",
          "--feature",
          "go-todo-crud-smoke",
          "--worktree",
          "--dry-run",
          "--json",
        ],
        { encoding: "utf-8", cwd: repoRoot },
      );

      expect(result.status).toBe(0);
      const payload = JSON.parse(result.stdout);
      expect(payload.status).toBe("dry_run");
      expect(String(payload.beacon_run_command)).toContain("--worktree");
      expect(String(payload.beacon_run_command)).toContain("--project-root");
    } finally {
      rmSync(cwd, { recursive: true, force: true });
    }
  });
});

describe("e2e go-todo worktree dry-run (always on)", () => {
  it("beacon-loop delegate command includes worktree + feature + beacon", () => {
    const loopCli = join(repoRoot, "packages/beacon-loop/dist/cli.js");
    expect(existsSync(loopCli)).toBe(true);
    const result = spawnSync(
      process.execPath,
      [
        loopCli,
        "goal",
        "smoke go todo crud",
        "--project",
        repoRoot,
        "--version",
        "v1.6.0",
        "--feature",
        "go-todo-crud-smoke",
        "--worktree",
        "--dry-run",
        "--json",
      ],
      { encoding: "utf-8", cwd: repoRoot },
    );
    expect(result.status).toBe(0);
    const payload = JSON.parse(result.stdout);
    expect(payload.beacon_run_command).toMatch(/--worktree/);
    expect(payload.beacon_run_command).toMatch(/go-todo-crud-smoke/);
    expect(payload.beacon_run_command).toMatch(/--beacon/);
  });
});
