import { join } from "node:path";
import { readJson, writeJson } from "../runner/fs.js";
import { nowIso } from "../runner/types.js";

export const DELIVERY_STATES = [
  "intent_capture",
  "intent_review",
  "user_decision_pending",
  "truth_gap_scan",
  "truth_fill",
  "truth_freeze_gate",
  "implement_loop",
  "evidence_import",
  "qa_pending",
  "release_pending",
  "repair_from_qa",
  "terminal_closed",
  "terminal_aborted"
];

const ALLOWED = {
  intent_capture: ["intent_review"],
  intent_review: ["truth_gap_scan", "user_decision_pending", "terminal_aborted"],
  user_decision_pending: ["intent_review", "truth_gap_scan", "terminal_aborted"],
  truth_gap_scan: ["truth_fill", "implement_loop", "terminal_aborted"],
  truth_fill: ["truth_freeze_gate"],
  truth_freeze_gate: ["implement_loop", "truth_fill", "terminal_aborted"],
  implement_loop: ["evidence_import", "terminal_aborted"],
  evidence_import: ["qa_pending"],
  qa_pending: ["release_pending", "repair_from_qa", "terminal_aborted"],
  repair_from_qa: ["implement_loop"],
  release_pending: ["terminal_closed", "repair_from_qa", "truth_fill"],
  terminal_closed: [],
  terminal_aborted: []
};

const INVALID_PAIRS = [
  ["intent_capture", "implement_loop"],
  ["implement_loop", "terminal_closed"],
  ["qa_pending", "terminal_closed"]
];

export function canTransition(from, to, context = {}) {
  const source = String(from || "");
  const target = String(to || "");
  if (!DELIVERY_STATES.includes(source) || !DELIVERY_STATES.includes(target)) return false;
  for (const [badFrom, badTo] of INVALID_PAIRS) {
    if (source === badFrom && target === badTo) return false;
  }
  if (source === "truth_gap_scan" && target === "implement_loop" && !context.truthFrozen) return false;
  if (source === "qa_pending" && target === "terminal_closed" && !context.releaseInvoked) return false;
  const allowed = ALLOWED[source] || [];
  return allowed.includes(target);
}

export function defaultDeliveryState(runId) {
  return {
    schema_version: "1.0",
    run_id: runId,
    state: "intent_capture",
    history: [],
    updated_at: nowIso()
  };
}

export function readDeliveryState(runDir) {
  return readJson(join(runDir, "delivery-state.json"), null);
}

export function writeDeliveryState(runDir, state) {
  writeJson(join(runDir, "delivery-state.json"), { ...state, updated_at: nowIso() });
}

export function transitionDeliveryState(runDir, nextState, context = {}) {
  const current = readDeliveryState(runDir) || defaultDeliveryState("");
  const from = current.state;
  if (!canTransition(from, nextState, context)) {
    return { ok: false, from, to: nextState, reason_code: "illegal_delivery_transition" };
  }
  const history = Array.isArray(current.history) ? current.history : [];
  history.push({ from, to: nextState, at: nowIso() });
  const updated = { ...current, state: nextState, history };
  writeDeliveryState(runDir, updated);
  return { ok: true, from, to: nextState, state: updated };
}
