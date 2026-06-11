import type { IterationRecord } from "../core/orchestrator.js";
import type {
  BeaconAfterIterationDecision,
  BeaconBeforeIterationDecision,
  BeaconPhaseController,
} from "./phase-controller.js";

export type BeaconOrchestratorHooks = {
  beforeAgentIteration?: () => Promise<BeaconBeforeIterationDecision>;
  augmentIterationPrompt?: (basePrompt: string) => string;
  afterAgentIteration?: (
    record: IterationRecord,
    shouldFullyStop: boolean,
  ) => Promise<BeaconAfterIterationDecision>;
};

export function createBeaconOrchestratorHooks(
  controller: BeaconPhaseController,
): BeaconOrchestratorHooks {
  return {
    beforeAgentIteration: () => controller.beforeAgentIteration(),
    augmentIterationPrompt: (basePrompt) =>
      controller.augmentIterationPrompt(basePrompt),
    afterAgentIteration: (record, shouldFullyStop) =>
      controller.afterAgentIteration(record.success, shouldFullyStop),
  };
}
