import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { join } from "node:path";

export type EvalSupplementOptions = {
  projectRoot: string;
  version: string;
  runDir: string;
  evalMatrix?: boolean;
  evalScorecard?: boolean;
};

function runBeaconJson(args: string[], projectRoot: string): Record<string, unknown> | null {
  const result = spawnSync("beacon", args, {
    cwd: projectRoot,
    encoding: "utf8",
  });
  if (result.status !== 0 || !result.stdout?.trim()) {
    return {
      status: "blocked",
      reason_code: "beacon_eval_failed",
      stderr: result.stderr?.trim() || "",
      exit_code: result.status ?? 1,
    };
  }
  try {
    return JSON.parse(result.stdout) as Record<string, unknown>;
  } catch {
    return { status: "blocked", reason_code: "beacon_eval_invalid_json" };
  }
}

export function runEvalSupplement(options: EvalSupplementOptions): {
  paths: string[];
  artifacts: Record<string, unknown>;
} {
  const paths: string[] = [];
  const artifacts: Record<string, unknown> = {
    schema_version: "1.0",
    surface: "beacon-run",
    formal_verdict_authority: false,
    supplement_only: true,
  };

  if (options.evalMatrix) {
    const payload =
      runBeaconJson(
        [
          "eval",
          "catalog",
          "--project-root",
          options.projectRoot,
          "--version",
          options.version,
          "--materialize",
          "--json",
        ],
        options.projectRoot,
      ) || {};
    const matrixArtifact = {
      ...payload,
      formal_verdict_authority: false,
      supplement_only: true,
      command: "beacon eval catalog --materialize --json",
    };
    const matrixPath = join(options.runDir, "eval-matrix.json");
    writeFileSync(matrixPath, `${JSON.stringify(matrixArtifact, null, 2)}\n`, "utf8");
    paths.push(matrixPath);
    artifacts.eval_matrix = matrixArtifact;
  }

  if (options.evalScorecard) {
    const payload =
      runBeaconJson(
        [
          "eval",
          "scorecard",
          "--project-root",
          options.projectRoot,
          "--version",
          options.version,
          "--json",
        ],
        options.projectRoot,
      ) || {};
    const scorecardArtifact = {
      ...payload,
      formal_verdict_authority: false,
      supplement_only: true,
      command: "beacon eval scorecard --json",
    };
    const scorecardPath = join(options.runDir, "eval-scorecard.json");
    writeFileSync(
      scorecardPath,
      `${JSON.stringify(scorecardArtifact, null, 2)}\n`,
      "utf8",
    );
    paths.push(scorecardPath);
    artifacts.eval_scorecard = scorecardArtifact;
  }

  return { paths, artifacts };
}
