export const ITERATION_RESULT_FIELDS = ["success", "summary", "key_changes_made", "key_learnings"];

export function normalizeIterationResult(raw, adapter = "unknown") {
  const payload = raw && typeof raw === "object" ? raw : {};
  const normalized = {
    success: payload.success !== false,
    summary: String(payload.summary || payload.message || `${adapter} iteration completed`),
    key_changes_made: Array.isArray(payload.key_changes_made) ? payload.key_changes_made : [],
    key_learnings: Array.isArray(payload.key_learnings) ? payload.key_learnings : [],
    token_usage: payload.token_usage || payload.raw?.token_usage || {},
    adapter,
    raw: payload.raw || payload
  };
  if (payload.force_commit_failure === true) normalized.force_commit_failure = true;
  if (payload.retryable_hard_error === true) normalized.retryable_hard_error = true;
  return normalized;
}

export function assertIterationContract(result) {
  for (const field of ITERATION_RESULT_FIELDS) {
    if (!(field in result)) return false;
  }
  if (typeof result.success !== "boolean") return false;
  if (typeof result.summary !== "string") return false;
  if (!Array.isArray(result.key_changes_made)) return false;
  if (!Array.isArray(result.key_learnings)) return false;
  return true;
}
