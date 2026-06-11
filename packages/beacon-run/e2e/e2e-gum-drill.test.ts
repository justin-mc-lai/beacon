import { execFileSync, spawn } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const distCliPath = join(repoRoot, "dist", "cli.mjs");
const fixtureBinDir = join(repoRoot, "e2e", "fixtures");
const drillEnabled = process.env.BEACON_RUN_E2E_DRILL === "1";

const emptyGitConfigDir = mkdtempSync(join(tmpdir(), "gnhf-gum-drill-gitconfig-"));
const emptyGitConfigPath = join(emptyGitConfigDir, "gitconfig");
writeFileSync(emptyGitConfigPath, "", "utf-8");

const sanitizedGitEnv: NodeJS.ProcessEnv = {
  GIT_CONFIG_GLOBAL: emptyGitConfigPath,
  GIT_CONFIG_SYSTEM: emptyGitConfigPath,
  GIT_TERMINAL_PROMPT: "0",
};

interface RunResult {
  code: number | null;
  stdout: string;
  stderr: string;
}

function git(args: string[], cwd: string): string {
  return execFileSync("git", args, {
    cwd,
    encoding: "utf-8",
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, ...sanitizedGitEnv },
  }).trim();
}

function createRepo(): string {
  const cwd = mkdtempSync(join(tmpdir(), "gnhf-gum-drill-"));
  git(["init", "-b", "main"], cwd);
  git(["config", "user.name", "gum drill tests"], cwd);
  git(["config", "user.email", "tests@example.com"], cwd);
  writeFileSync(join(cwd, "README.md"), "# gum drill fixture\n", "utf-8");
  git(["add", "README.md"], cwd);
  git(["commit", "-m", "init"], cwd);
  return cwd;
}

function seedFrozenBeaconTruth(
  cwd: string,
  feature: string,
  version: string,
): void {
  const featureDir = join(cwd, "docs/beacon", version, "features", feature);
  mkdirSync(featureDir, { recursive: true });
  writeFileSync(join(cwd, "docs/beacon/VERSION"), `${version}\n`, "utf-8");
  writeFileSync(
    join(featureDir, "truth.md"),
    `---\nstatus: frozen\nrevision_id: R1\nslug: ${feature}\n---\n\n# ${feature}\n`,
    "utf-8",
  );
  git(["add", "-A"], cwd);
  git(["commit", "-m", "seed frozen beacon truth"], cwd);
}

function findRunDir(cwd: string): string {
  const runsDir = join(cwd, ".gnhf", "runs");
  const runs = readdirSync(runsDir);
  if (runs.length !== 1) {
    throw new Error(`Expected one run dir, found ${runs.length}`);
  }
  return join(runsDir, runs[0]!);
}

function runCli(cwd: string, args: string[], env: NodeJS.ProcessEnv): Promise<RunResult> {
  return new Promise((resolveResult, reject) => {
    const child = spawn(process.execPath, [distCliPath, ...args], {
      cwd,
      env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      resolveResult({ code, stdout, stderr });
    });
  });
}

const describeDrill = drillEnabled ? describe : describe.skip;

describeDrill("e2e-gum-drill", () => {
  const tempDirs: string[] = [];

  afterEach(() => {
    for (const dir of tempDirs.splice(0)) {
      rmSync(dir, { recursive: true, force: true, maxRetries: 3, retryDelay: 200 });
    }
  });

  it("runs beacon lifecycle with truth iteration, commit, and qa harness", async () => {
    const cwd = createRepo();
    tempDirs.push(cwd);
    const feature = "gum-choose-filter-parity";
    const beaconVersion = "v1.6.0";
    seedFrozenBeaconTruth(cwd, feature, beaconVersion);
    const logDir = mkdtempSync(join(tmpdir(), "gnhf-gum-drill-logs-"));
    tempDirs.push(logDir);

    const utterance =
      "Deliver charmbracelet/gum choose and filter parity for interactive CLI selection";
    const env = {
      ...process.env,
      ...sanitizedGitEnv,
      HOME: mkdtempSync(join(tmpdir(), "gnhf-gum-drill-home-")),
      PATH: `${fixtureBinDir}${process.platform === "win32" ? ";" : ":"}${process.env.PATH ?? ""}`,
      GNHF_MOCK_OPENCODE_LOG_PATH: join(logDir, "mock-opencode.jsonl"),
      GNHF_MOCK_BEACON_PHASE_ADVANCE: "1",
      BEACON_RUN_MOCK_HARNESS: "1",
    };

    const result = await runCli(
      cwd,
      [
        utterance,
        "--beacon",
        "--feature",
        feature,
        "--beacon-version",
        beaconVersion,
        "--agent",
        "opencode",
        "--current-branch",
        "--max-iterations",
        "12",
      ],
      env,
    );

    expect(result.code).toBe(0);

    const runDir = findRunDir(cwd);
    expect(existsSync(join(runDir, "beacon-phase.json"))).toBe(true);
    expect(existsSync(join(runDir, "truth-promotion.json"))).toBe(true);

    const promotion = JSON.parse(
      readFileSync(join(runDir, "truth-promotion.json"), "utf8"),
    );
    expect(
      promotion.calls.some((call: { command?: string }) =>
        String(call.command || "").includes("qa run"),
      ),
    ).toBe(true);
    expect(
      promotion.calls.some((call: { phase?: string }) => call.phase === "truth"),
    ).toBe(true);

    const iterationLogs = readdirSync(runDir).filter((name) =>
      name.startsWith("iteration-"),
    );
    expect(iterationLogs.length).toBeGreaterThanOrEqual(1);

    const commitCount = Number(
      git(["rev-list", "--count", "HEAD"], cwd),
    );
    expect(commitCount).toBeGreaterThanOrEqual(2);

    const phaseState = JSON.parse(
      readFileSync(join(runDir, "beacon-phase.json"), "utf8"),
    );
    expect(phaseState.phases_completed).toContain("qa");
  }, 60_000);
});
