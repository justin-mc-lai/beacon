import { join } from "node:path";
import { run } from "../git/git.js";
import { readJson, writeJson } from "../runner/fs.js";
import { nowIso } from "../runner/types.js";
import { packageSurfacesMissing, resolveTruth, isFeatureTruthFrozen } from "../beacon/resolve.js";
import { applyColdStartClosurePatch } from "./truth-bootstrap.js";

export function readTruthPromotion(runDir) {
  return readJson(join(runDir, "truth-promotion.json"), { schema_version: "1.0", calls: [] });
}

export function appendTruthPromotion(runDir, entry) {
  const current = readTruthPromotion(runDir);
  const calls = Array.isArray(current.calls) ? current.calls : [];
  calls.push({ ...entry, at: nowIso() });
  writeJson(join(runDir, "truth-promotion.json"), { ...current, calls, updated_at: nowIso() });
}

export function scanTruthGap(projectRoot, version, feature, reviewArtifact) {
  const resolver = resolveTruth(projectRoot, version, feature);
  const parityMissing = Array.isArray(reviewArtifact?.parity_matrix)
    ? reviewArtifact.parity_matrix.some((row) => row && row.status === "missing" && row.user_decision !== "accepted")
    : false;
  const deferPending = Array.isArray(reviewArtifact?.deferral_ledger)
    ? reviewArtifact.deferral_ledger.some((row) => String(row?.user_decision || "") === "pending")
    : false;
  return {
    resolver,
    blocked: Boolean(resolver.blocked) || parityMissing,
    deferPending,
    truthFrozen: isFeatureTruthFrozen(projectRoot, version, feature, resolver)
  };
}

function runBeaconStep(projectRoot, runDir, args) {
  const cmd = `beacon ${args.join(" ")}`;
  const result = run("beacon", args, { cwd: projectRoot });
  appendTruthPromotion(runDir, {
    command: cmd,
    exit_code: result.code,
    stdout: result.stdout?.slice(0, 500),
    stderr: result.stderr?.slice(0, 500)
  });
  return result;
}

function beaconJsonSucceeded(result) {
  if (result.code !== 0) {
    return false;
  }
  try {
    const payload = JSON.parse(result.stdout);
    if (payload.blocked === true || payload.status === "blocked") {
      return false;
    }
    const gate = payload.result?.gate;
    if (gate && (gate.blocked === true || gate.status === "blocked")) {
      return false;
    }
    return true;
  } catch {
    return true;
  }
}

function bootstrapColdStartTruth(projectRoot, runDir, { version, feature, utterance }) {
  const prompt = String(utterance || feature).trim();
  const desc = prompt.slice(0, 500) || feature;
  const steps = [];

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
    "--json"
  ]);
  steps.push("prd-bootstrap");
  if (result.code !== 0) {
    result = runBeaconStep(projectRoot, runDir, [
      "truth",
      "init",
      "all",
      "-f",
      feature,
      "--version",
      version,
      "--project",
      projectRoot
    ]);
    steps.push("truth-init-fallback");
    if (result.code !== 0) {
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
    "--json"
  ]);
  steps.push("brainstorm");
  if (result.code !== 0) {
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
    "--json"
  ]);
  steps.push("materialize-feature-package");
  if (result.code !== 0) {
    return { ok: false, steps, detail: result.stderr || result.stdout };
  }

  const closure = applyColdStartClosurePatch(projectRoot, version, feature, prompt);
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
    "--json"
  ]);
  steps.push("sync-materials");
  if (result.code !== 0) {
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
    "--json"
  ]);
  steps.push("sync-requirement-clarity");
  if (!beaconJsonSucceeded(result)) {
    return { ok: false, steps, detail: result.stderr || result.stdout };
  }

  return { ok: true, steps };
}

export function runTruthFill(projectRoot, runDir, { version, feature, reviewArtifact, utterance = "" }) {
  const gap = scanTruthGap(projectRoot, version, feature, reviewArtifact);
  if (!gap.blocked && !gap.deferPending) {
    return { status: "skipped", gap };
  }
  if (gap.deferPending) {
    return { status: "blocked", reason_code: "deferral_pending", gap };
  }

  if (process.env.BEACON_LOOP_TEST_TRUTH_FILL === "fixture") {
    appendTruthPromotion(runDir, {
      command: `beacon truth-map rebuild-machine ${feature} --version ${version}`,
      exit_code: 0,
      mode: "fixture"
    });
    return { status: "completed", gap, fixture: true };
  }

  const bootstrapNeeded = packageSurfacesMissing(projectRoot, gap.resolver.payload);
  if (bootstrapNeeded) {
    const bootstrap = bootstrapColdStartTruth(projectRoot, runDir, { version, feature, utterance });
    if (!bootstrap.ok) {
      return { status: "blocked", reason_code: "truth_bootstrap_failed", gap, bootstrap_steps: bootstrap.steps, detail: bootstrap.detail };
    }
  }

  const sequence = [
    ["truth-map", "rebuild-machine", feature, "--project", projectRoot, "--version", version, "--json"],
    ["freeze", feature, "--project", projectRoot, "--version", version, "--json"]
  ];
  for (const args of sequence) {
    const result = runBeaconStep(projectRoot, runDir, args);
    if (!beaconJsonSucceeded(result)) {
      return { status: "blocked", reason_code: "truth_fill_failed", gap };
    }
  }
  return { status: "completed", gap };
}
