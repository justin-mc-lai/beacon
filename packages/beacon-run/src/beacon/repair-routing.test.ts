import { describe, expect, it } from "vitest";
import {
  classifyHarnessRepairKind,
  isInfrastructureStopReason,
  parseHarnessStopReasons,
} from "./repair-routing.js";

describe("repair-routing", () => {
  it("detects infrastructure stop reasons", () => {
    expect(isInfrastructureStopReason("junit_missing_or_invalid")).toBe(true);
    expect(isInfrastructureStopReason("implementation_first_reconciliation_required")).toBe(
      true,
    );
    expect(isInfrastructureStopReason("harness_exit_failed")).toBe(false);
  });

  it("routes junit scorecard failures to governance repair", () => {
    const result = {
      command: "beacon qa run demo",
      exit_code: 2,
      stdout: JSON.stringify({
        status: "failed",
        scorecard: {
          stop_reasons: ["assertion_count_zero_pass", "junit_missing_or_invalid"],
        },
      }),
      stderr: "",
    };
    expect(parseHarnessStopReasons(result)).toEqual([
      "assertion_count_zero_pass",
      "junit_missing_or_invalid",
    ]);
    expect(classifyHarnessRepairKind(result)).toBe("governance");
  });

  it("routes implementation QA failures to implementation repair", () => {
    const result = {
      command: "beacon qa run demo",
      exit_code: 2,
      stdout: JSON.stringify({
        status: "blocked",
        reason_codes: ["coverage_gap_remaining"],
      }),
      stderr: "",
    };
    expect(classifyHarnessRepairKind(result, "coverage_gap_remaining")).toBe(
      "implementation",
    );
  });
});
