import { join } from "node:path";
import { run } from "../git/git.js";
import { writeJson } from "../runner/fs.js";
import { nowIso } from "../runner/types.js";
import { importEvidence } from "../evidence/importer.js";

function parseJson(stdout) {
  try {
    return JSON.parse(stdout);
  } catch {
    return {};
  }
}

export function runDeliveryEvalChain(projectRoot, runDir, runPackage) {
  const refs = {
    beacon_qa_verdict_ref: "",
    beacon_release_verdict_ref: "",
    closure_verdict: "not_provided_by_beacon_loop"
  };

  if (process.env.BEACON_LOOP_TEST_EVAL_CHAIN === "fixture") {
    writeJson(join(runDir, "eval-chain.json"), {
      schema_version: "1.0",
      import: { status: "imported" },
      qa: { status: "completed", surface: "beacon-qa" },
      release: { status: "completed", surface: "beacon-release" },
      ...refs,
      fixture: true,
      at: nowIso()
    });
    return { status: "completed", ...refs };
  }

  const imported = importEvidence(projectRoot, runPackage.run_id, true);
  if (imported.status !== "imported") {
    return { status: "blocked", reason_code: "evidence_import_failed", ...refs };
  }

  const qaArgs = ["qa", "run", runPackage.feature, "--project", projectRoot, "--version", runPackage.version, "--json"];
  const qaResult = run("beacon", qaArgs, { cwd: projectRoot });
  const qaPayload = parseJson(qaResult.stdout);
  refs.beacon_qa_verdict_ref = join(runDir, "qa-result.json");
  writeJson(refs.beacon_qa_verdict_ref, qaPayload);
  if (qaResult.code !== 0 || String(qaPayload.status || "").includes("blocked")) {
    return { status: "qa_failed", reason_code: "beacon_qa_failed", qa: qaPayload, ...refs };
  }

  const releaseArgs = ["release", "create", "--project", projectRoot, "--version", runPackage.version, "--json"];
  const releaseResult = run("beacon", releaseArgs, { cwd: projectRoot });
  const releasePayload = parseJson(releaseResult.stdout);
  refs.beacon_release_verdict_ref = join(runDir, "release-result.json");
  writeJson(refs.beacon_release_verdict_ref, releasePayload);

  writeJson(join(runDir, "eval-chain.json"), {
    schema_version: "1.0",
    import: imported,
    qa: qaPayload,
    release: releasePayload,
    ...refs,
    at: nowIso()
  });

  return {
    status: releaseResult.code === 0 ? "completed" : "release_failed",
    qa: qaPayload,
    release: releasePayload,
    ...refs
  };
}
