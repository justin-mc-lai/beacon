import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const extra = process.argv.slice(2);
const result = spawnSync(
  process.execPath,
  [
    "--test",
    "--test-concurrency=1",
    ...extra,
    join(root, "tests", "beacon-loop.test.mjs"),
    join(root, "tests", "delivery-orchestrator.test.mjs")
  ],
  { stdio: "inherit", cwd: root }
);
process.exit(result.status ?? 1);
