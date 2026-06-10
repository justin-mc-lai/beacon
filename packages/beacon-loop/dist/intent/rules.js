import { createHash } from "node:crypto";

export const CLASSIFIER_ID = "beacon-loop-intent-v1";

export const RULES_BODY = [
  "delivery_closed_loop:闭环,交付,验收,release,truth",
  "full_parity:完整,全量,parity,不要mvp",
  "patch:hotfix,bug,修复",
  "research:调研,探索,brainstorm",
  "execute_bound:frozen,仅实现,execute-only"
].join("\n");

export function rulesHash() {
  return createHash("sha256").update(`${CLASSIFIER_ID}\n${RULES_BODY}`).digest("hex");
}
