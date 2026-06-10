import { join } from "node:path";
import { run } from "../git/git.js";
import { readJson, writeJson } from "../runner/fs.js";
import { nowIso } from "../runner/types.js";
import { resolveTruth } from "../beacon/resolve.js";

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
    truthFrozen: !resolver.blocked && String(resolver.payload?.feature_truth?.truth_frontmatter?.status || "") === "frozen"
  };
}

export function runTruthFill(projectRoot, runDir, { version, feature, reviewArtifact }) {
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

  const sequence = [
    ["truth-map", "rebuild-machine", feature, "--project", projectRoot, "--version", version, "--json"],
    ["freeze", feature, "--project", projectRoot, "--version", version, "--json"]
  ];
  for (const args of sequence) {
    const cmd = `beacon ${args.join(" ")}`;
    const result = run("beacon", args, { cwd: projectRoot });
    appendTruthPromotion(runDir, { command: cmd, exit_code: result.code, stdout: result.stdout?.slice(0, 500), stderr: result.stderr?.slice(0, 500) });
    if (result.code !== 0) {
      return { status: "blocked", reason_code: "truth_fill_failed", gap };
    }
  }
  return { status: "completed", gap };
}
