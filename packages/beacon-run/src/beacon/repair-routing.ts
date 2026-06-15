import type { HarnessRunResult } from "./harness-checkpoint.js";

const INFRASTRUCTURE_STOP_REASONS = new Set([
  "junit_missing_or_invalid",
  "assertion_count_zero_pass",
  "implementation_first_reconciliation_required",
  "version_surface_governance_drift",
  "project_profile_gate_blocked",
  "auto_test_invocation_failed",
  "qa_feature_lock_timeout",
  "qa_runner_timeout",
  "evidence_binding_missing",
  "previous_feature_qa_not_passed",
]);

export type RepairKind = "implementation" | "governance";

export function isInfrastructureStopReason(reason: string): boolean {
  const normalized = String(reason || "").trim().toLowerCase();
  if (!normalized) return false;
  if (INFRASTRUCTURE_STOP_REASONS.has(normalized)) return true;
  return (
    normalized.includes("junit") ||
    normalized.includes("reconciliation") ||
    normalized.includes("version_surface") ||
    normalized.includes("assertion_count_zero")
  );
}

export function parseHarnessStopReasons(result: HarnessRunResult): string[] {
  const reasons = new Set<string>();
  const primary = parseHarnessPayload(result.stdout);
  for (const code of collectReasonCodes(primary)) {
    reasons.add(code);
  }
  if (!reasons.size) {
    for (const code of collectReasonCodes(parseHarnessPayload(result.stderr))) {
      reasons.add(code);
    }
  }
  return [...reasons];
}

function parseHarnessPayload(text: string): Record<string, unknown> | null {
  const raw = String(text || "").trim();
  if (!raw) return null;
  try {
    const payload = JSON.parse(raw) as Record<string, unknown>;
    return payload && typeof payload === "object" ? payload : null;
  } catch {
    return null;
  }
}

function collectReasonCodes(payload: Record<string, unknown> | null): string[] {
  if (!payload) return [];
  const codes: string[] = [];
  const push = (value: unknown) => {
    if (typeof value === "string" && value.trim()) {
      codes.push(value.trim());
    }
  };
  push(payload.reason_code);
  push(payload.blocked_reason);
  const result = payload.result;
  if (result && typeof result === "object") {
    push((result as Record<string, unknown>).reason_code);
  }
  for (const key of ["reason_codes", "stop_reasons"] as const) {
    const value = payload[key];
    if (Array.isArray(value)) {
      for (const item of value) push(item);
    }
  }
  const scorecard = payload.scorecard;
  if (scorecard && typeof scorecard === "object") {
    const stopReasons = (scorecard as Record<string, unknown>).stop_reasons;
    if (Array.isArray(stopReasons)) {
      for (const item of stopReasons) push(item);
    }
  }
  return codes;
}

export function classifyHarnessRepairKind(
  result: HarnessRunResult,
  fallbackReason = "",
): RepairKind {
  const reasons = parseHarnessStopReasons(result);
  if (!reasons.length && fallbackReason) {
    reasons.push(fallbackReason);
  }
  if (reasons.some((reason) => isInfrastructureStopReason(reason))) {
    return "governance";
  }
  return "implementation";
}
