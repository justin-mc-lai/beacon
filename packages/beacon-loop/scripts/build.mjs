import { cpSync, mkdirSync, rmSync, chmodSync, readdirSync, statSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const src = join(root, "src");
const dist = join(root, "dist");

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

function copyDir(from, to) {
  mkdirSync(to, { recursive: true });
  for (const name of readdirSync(from)) {
    const source = join(from, name);
    const target = join(to, name.replace(/\.ts$/, ".js"));
    if (statSync(source).isDirectory()) {
      copyDir(source, target);
      continue;
    }
    if (name.endsWith(".ts")) {
      writeFileSync(target, readFileSync(source, "utf8"), "utf8");
    } else {
      cpSync(source, target);
    }
  }
}

copyDir(src, dist);
chmodSync(join(dist, "cli.js"), 0o755);
