import { runAcpAdapter } from "./acp.js";
import { runClaudeAdapter } from "./claude.js";
import { runCodexAdapter } from "./codex.js";
import { assertIterationContract } from "./schema.js";

export { assertIterationContract, normalizeIterationResult, ITERATION_RESULT_FIELDS } from "./schema.js";

export function parseAgentName(agent) {
  const name = String(agent || "codex");
  if (name.startsWith("acp:")) return { kind: "acp", name, target: name.slice(4) || "default" };
  return { kind: name, name, target: "" };
}

export function runAgentAdapter(agent, worktreePath, runId, options = {}) {
  const parsed = parseAgentName(agent);
  if (parsed.kind === "acp") {
    return runAcpAdapter(worktreePath, runId, { ...options, target: parsed.target, agent: parsed.name });
  }
  if (parsed.kind === "claude") {
    return runClaudeAdapter(worktreePath, runId, { ...options, agent: "claude" });
  }
  return runCodexAdapter(worktreePath, runId, options);
}

export function runAgentContractSelfTest(agent, worktreePath, runId) {
  const result = runAgentAdapter(agent, worktreePath, runId, {
    prompt: "contract self test",
    iteration: 1
  });
  return { agent, valid: assertIterationContract(result), result };
}
