import {
  appendTruthPromotion,
  beaconJsonSucceeded,
  runBeaconCommand,
  type HarnessRunResult,
} from "./harness-checkpoint.js";
import { applyColdStartClosurePatch } from "./truth-closure-patch.js";

export type TruthBootstrapFallbackResult =
  | { ok: true; steps: string[] }
  | { ok: false; steps: string[]; detail: string };

function runBeaconStep(
  projectRoot: string,
  runDir: string,
  args: string[],
): HarnessRunResult {
  const result = runBeaconCommand(projectRoot, args);
  appendTruthPromotion(runDir, {
    command: result.command,
    exit_code: result.exit_code,
    stdout: result.stdout.slice(0, 500),
    stderr: result.stderr.slice(0, 500),
    mode: "truth-bootstrap-fallback",
  });
  return result;
}

export function bootstrapColdStartTruthFallback(
  projectRoot: string,
  runDir: string,
  options: { version: string; feature: string; utterance: string },
): TruthBootstrapFallbackResult {
  if (process.env.BEACON_RUN_TEST_TRUTH_BOOTSTRAP === "fixture") {
    appendTruthPromotion(runDir, {
      command: `beacon prd-bootstrap run ${options.feature} --fixture`,
      exit_code: 0,
      mode: "truth-bootstrap-fallback-fixture",
    });
    return { ok: true, steps: ["fixture"] };
  }

  const prompt = String(options.utterance || options.feature).trim();
  const desc = prompt.slice(0, 500) || options.feature;
  const steps: string[] = [];
  const { version, feature } = options;

  let result = runBeaconStep(projectRoot, runDir, [
    "prd-bootstrap",
    "run",
    feature,
    "--desc",
    desc,
    "--project-root",
    projectRoot,
    "--version",
    version,
    "--apply",
    "--skip-context-verify",
    "--json",
  ]);
  steps.push("prd-bootstrap");
  if (result.exit_code !== 0) {
    result = runBeaconStep(projectRoot, runDir, [
      "truth",
      "init",
      "all",
      "-f",
      feature,
      "--version",
      version,
      "--project",
      projectRoot,
    ]);
    steps.push("truth-init-fallback");
    if (result.exit_code !== 0) {
      return { ok: false, steps, detail: result.stderr || result.stdout };
    }
  }

  result = runBeaconStep(projectRoot, runDir, [
    "brainstorm",
    "run",
    prompt,
    "--project-root",
    projectRoot,
    "--version",
    version,
    "--mode",
    "requirement-convergence",
    "--feature",
    feature,
    "--json",
  ]);
  steps.push("brainstorm");
  if (result.exit_code !== 0) {
    return { ok: false, steps, detail: result.stderr || result.stdout };
  }

  result = runBeaconStep(projectRoot, runDir, [
    "materialize-feature-package",
    feature,
    "--project",
    projectRoot,
    "--version",
    version,
    "--force",
    "--json",
  ]);
  steps.push("materialize-feature-package");
  if (result.exit_code !== 0) {
    return { ok: false, steps, detail: result.stderr || result.stdout };
  }

  const closure = applyColdStartClosurePatch(
    projectRoot,
    version,
    feature,
    prompt,
  );
  if (closure.applied) {
    steps.push("closure-patch");
  }

  result = runBeaconStep(projectRoot, runDir, [
    "doctor",
    "sync-materials",
    "--project-root",
    projectRoot,
    "--version",
    version,
    "--feature",
    feature,
    "--single-feature",
    "--json",
  ]);
  steps.push("sync-materials");
  if (result.exit_code !== 0) {
    return { ok: false, steps, detail: result.stderr || result.stdout };
  }

  result = runBeaconStep(projectRoot, runDir, [
    "doctor",
    "sync-requirement-clarity",
    feature,
    "--project-root",
    projectRoot,
    "--version",
    version,
    "--json",
  ]);
  steps.push("sync-requirement-clarity");
  if (!beaconJsonSucceeded(result)) {
    return { ok: false, steps, detail: result.stderr || result.stdout };
  }

  return { ok: true, steps };
}
