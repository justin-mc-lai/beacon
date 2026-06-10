import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

function parseSimpleYaml(text) {
  const out = {};
  for (const line of String(text || "").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const idx = trimmed.indexOf(":");
    if (idx < 0) continue;
    const key = trimmed.slice(0, idx).trim();
    let value = trimmed.slice(idx + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (/^\d+$/.test(value)) out[key] = Number(value);
    else if (value === "true") out[key] = true;
    else if (value === "false") out[key] = false;
    else out[key] = value;
  }
  return out;
}

export function loadLoopConfig(projectRoot) {
  const paths = [join(homedir(), ".beacon-loop", "config.yml"), join(projectRoot, ".beacon-loop", "config.yml")];
  let merged = {};
  for (const path of paths) {
    if (!existsSync(path)) continue;
    merged = { ...merged, ...parseSimpleYaml(readFileSync(path, "utf8")) };
  }
  return merged;
}

export function resolveGoalOptions(projectRoot, args, cli = {}) {
  const config = loadLoopConfig(projectRoot);
  const has = (flag) => args.includes(flag);
  const askOnRaw = has("--ask-on") ? cli.askOn : config.ask_on || cli.askOn || "P0,P1";
  return {
    version: has("--version") ? cli.version : config.version || cli.version || "v1.6.0",
    feature: has("--feature") ? cli.feature : config.feature || cli.feature || "",
    mode: has("--mode") ? cli.mode : config.mode || cli.mode || "delivery",
    askOn: String(askOnRaw).split(",").map((item) => item.trim()).filter(Boolean),
    autoDecideDeferrals: has("--auto-decide") ? true : Boolean(cli.autoDecideDeferrals || config.auto_decide_deferrals),
    ackIntentDrift: has("--ack-intent-drift") ? true : Boolean(cli.ackIntentDrift),
    agent: has("--agent") ? cli.agent : config.agent || cli.agent || "codex",
    branchMode: has("--branch-mode") ? cli.branchMode : config.branch_mode || cli.branchMode || "worktree",
    maxIterations: has("--max-iterations") ? cli.maxIterations : String(config.max_iterations ?? cli.maxIterations ?? "1"),
    maxTokens: has("--max-tokens") ? cli.maxTokens : String(config.max_tokens ?? cli.maxTokens ?? "0"),
    stopWhen: has("--stop-when") ? cli.stopWhen : config.stop_when || cli.stopWhen || "",
    isolatedWorktree: has("--isolated-worktree") ? true : Boolean(cli.isolatedWorktree),
    dryRun: cli.dryRun,
    allowDirty: cli.allowDirty
  };
}
