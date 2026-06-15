import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export function ensureDir(path) {
  mkdirSync(path, { recursive: true });
}

export function readJson(path, fallback = {}) {
  if (!existsSync(path)) return fallback;
  return JSON.parse(readFileSync(path, "utf8"));
}

export function writeJson(path, payload) {
  ensureDir(join(path, ".."));
  writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

export function writeText(path, text) {
  ensureDir(join(path, ".."));
  writeFileSync(path, text, "utf8");
}

export function latestRunId(projectRoot) {
  const root = join(projectRoot, ".beacon", "loop", "runs");
  if (!existsSync(root)) return "";
  const ids = readdirSync(root).filter(Boolean).sort();
  return ids.at(-1) || "";
}
