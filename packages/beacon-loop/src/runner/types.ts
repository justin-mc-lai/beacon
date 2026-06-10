export const RUNTIME_ROLE = "runtime_process_record_not_requirement_truth";

export function slugify(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function nowIso() {
  return new Date().toISOString();
}
