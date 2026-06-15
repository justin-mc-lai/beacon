import { join } from "node:path";

export const RUN_STATES = {
  PREFLIGHT_BLOCKED: "preflight_blocked",
  RUN_INITIALIZED: "run_initialized",
  ITERATING: "iterating",
  ITERATION_SUCCESS_COMMIT: "iteration_success_commit",
  ITERATION_FAIL_ROLLBACK: "iteration_fail_rollback",
  REPAIR_REQUIRED: "repair_required",
  WAITING_BACKOFF: "waiting_backoff",
  GRACEFUL_STOP_PENDING: "graceful_stop_pending",
  FORCE_STOPPED: "force_stopped",
  CAP_REACHED: "cap_reached",
  IMPLEMENTATION_CANDIDATE: "implementation_candidate"
};

export function defaultRunState() {
  return {
    machine_state: RUN_STATES.RUN_INITIALIZED,
    iteration: 0,
    consecutive_failures: 0,
    total_tokens: 0,
    started_at: "",
    finished_at: "",
    stop_reason: "",
    cap_reason: ""
  };
}

export function shouldForceStop(runDir, readJson) {
  const interrupt = readJson(join(runDir, "interrupt-state.json"), null);
  return interrupt?.mode === "force" || interrupt?.status === "force_stopped";
}

export function shouldGracefulStop(runDir, readJson) {
  const interrupt = readJson(join(runDir, "interrupt-state.json"), null);
  return interrupt?.mode === "graceful" || interrupt?.status === "graceful_stop_requested";
}

export function sleepMs(ms) {
  if (ms <= 0) return;
  const start = Date.now();
  while (Date.now() - start < ms) {
    // busy-wait for short test backoff windows without async
  }
}
