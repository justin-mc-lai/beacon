import { run } from "../git/git.js";

export function resolveTruth(projectRoot, version, feature) {
  const args = ["truth-map", "resolve", feature, "--project", projectRoot, "--version", version, "--json"];
  const command = `beacon ${args.join(" ")}`;
  const result = run("beacon", args, { cwd: projectRoot });
  if (result.code !== 0) {
    return {
      status: "blocked",
      blocked: true,
      reason_code: "beacon_truth_resolver_failed",
      command,
      stderr: result.stderr,
      stdout: result.stdout,
      next_route: "beacon-gen-change"
    };
  }
  try {
    const payload = JSON.parse(result.stdout);
    const sourcePaths = payload?.feature_truth?.source_paths || {};
    const missing = ["truth", "tests"].filter((key) => !sourcePaths[key]);
    return {
      status: missing.length ? "blocked" : "pass",
      blocked: missing.length > 0 || Boolean(payload?.blocked),
      reason_code: missing.length ? "beacon_truth_package_gap" : "",
      command,
      payload,
      source_paths: sourcePaths,
      next_route: missing.length ? "beacon-gen-change" : ""
    };
  } catch (error) {
    return {
      status: "blocked",
      blocked: true,
      reason_code: "beacon_truth_resolver_json_invalid",
      command,
      stderr: String(error),
      stdout: result.stdout,
      next_route: "beacon-gen-change"
    };
  }
}
