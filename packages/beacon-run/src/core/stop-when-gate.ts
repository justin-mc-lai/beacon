import { execFileSync } from "node:child_process";

export type StopWhenGateInput = {
  stopWhen?: string;
  shouldFullyStop: boolean;
  stopCheckCmd?: string;
  cwd: string;
  hasBeaconHarness?: boolean;
  beaconHarnessOk?: boolean;
  beaconTerminalPhase?: boolean;
};

export type StopWhenGateResult = {
  verified: boolean;
  reason_code?: "stop_when_unverified" | "stop_check_cmd_failed";
  check?: string;
};

export function runStopCheckCmd(
  command: string,
  cwd: string,
): { ok: boolean; exitCode: number; stderr: string } {
  const trimmed = command.trim();
  if (!trimmed) {
    return { ok: false, exitCode: 2, stderr: "empty stop-check-cmd" };
  }
  try {
    execFileSync("sh", ["-c", trimmed], {
      cwd,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    });
    return { ok: true, exitCode: 0, stderr: "" };
  } catch (error) {
    const exitCode =
      typeof error === "object" &&
      error !== null &&
      "status" in error &&
      typeof (error as NodeJS.ErrnoException).status === "number"
        ? ((error as NodeJS.ErrnoException).status as number)
        : 1;
    const stderr =
      typeof error === "object" &&
      error !== null &&
      "stderr" in error &&
      typeof (error as { stderr?: unknown }).stderr === "string"
        ? String((error as { stderr: string }).stderr)
        : error instanceof Error
          ? error.message
          : String(error);
    return { ok: false, exitCode, stderr };
  }
}

export function evaluateStopWhenGate(
  input: StopWhenGateInput,
): StopWhenGateResult {
  const stopWhen = String(input.stopWhen || "").trim();
  if (!stopWhen || !input.shouldFullyStop) {
    return { verified: false };
  }

  if (input.beaconTerminalPhase) {
    return { verified: true, check: "beacon_terminal_phase" };
  }

  if (input.hasBeaconHarness) {
    if (input.beaconHarnessOk) {
      return { verified: true, check: "beacon_phase_harness" };
    }
    return { verified: false, reason_code: "stop_when_unverified" };
  }

  const stopCheckCmd = String(input.stopCheckCmd || "").trim();
  if (stopCheckCmd) {
    const result = runStopCheckCmd(stopCheckCmd, input.cwd);
    if (result.ok) {
      return { verified: true, check: "stop_check_cmd" };
    }
    return {
      verified: false,
      reason_code: "stop_check_cmd_failed",
      check: "stop_check_cmd",
    };
  }

  return { verified: false, reason_code: "stop_when_unverified" };
}
