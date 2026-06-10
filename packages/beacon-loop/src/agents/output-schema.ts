import { join } from "node:path";
import { writeJson } from "../runner/fs.js";

export function buildAgentOutputSchema({ includeStopField = false } = {}) {
  const properties = {
    success: { type: "boolean" },
    summary: { type: "string" },
    key_changes_made: { type: "array", items: { type: "string" } },
    key_learnings: { type: "array", items: { type: "string" } }
  };
  const required = ["success", "summary", "key_changes_made", "key_learnings"];
  if (includeStopField) {
    properties.should_fully_stop = { type: "boolean" };
    required.push("should_fully_stop");
  }
  return {
    type: "object",
    additionalProperties: false,
    properties,
    required
  };
}

export function writeOutputSchemaFile(runDir, { includeStopField = false } = {}) {
  writeJson(join(runDir, "output-schema.json"), buildAgentOutputSchema({ includeStopField }));
}
