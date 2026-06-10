import { nowIso } from "../runner/types.js";

export function buildIntentCapture(utterance) {
  const text = String(utterance || "").trim();
  return {
    schema_version: "1.0",
    utterance: text,
    normalized: text.replace(/\s+/g, " "),
    captured_at: nowIso()
  };
}
