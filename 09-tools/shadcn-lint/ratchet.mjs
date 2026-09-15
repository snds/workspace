#!/usr/bin/env node
/**
 * Run lint:ds and compare error count to baseline.json.
 *
 * CDS uses baseline 0 (any overlay / no-raw-colors hit fails).
 * centric-ui and proto freeze today's count so debt cannot grow; lower the
 * baseline when a file is migrated.
 *
 *   node eslint/ds-lint/ratchet.mjs --config eslint/ds-lint/hosts/cds.config.mjs
 *   node eslint/ds-lint/ratchet.mjs --config … --write-baseline
 */
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const writeBaseline = args.includes("--write-baseline");
const configFlag = args.indexOf("--config");
const config =
  configFlag >= 0
    ? args[configFlag + 1]
    : join(here, "eslint.ds.config.mjs");
const baselinePath = join(here, "baseline.json");
const cwd = process.cwd();

const eslintBin = [
  join(cwd, "node_modules/eslint/bin/eslint.js"),
  join(here, "../../node_modules/eslint/bin/eslint.js"),
].find((p) => existsSync(p));

if (!eslintBin) {
  console.error("lint:ds ratchet: eslint not installed (peer @shadcn/lint needs eslint >= 9.30)");
  process.exit(2);
}

const result = spawnSync(
  process.execPath,
  [
    eslintBin,
    "--config",
    resolve(cwd, config),
    "--format",
    "json",
    "--no-error-on-unmatched-pattern",
    ".",
  ],
  { cwd, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 },
);

let reports = [];
try {
  reports = JSON.parse(result.stdout || "[]");
} catch {
  console.error(result.stderr || result.stdout || "eslint produced no JSON");
  process.exit(result.status === 0 ? 1 : result.status);
}

const errorCount = reports.reduce(
  (n, file) => n + (file.errorCount || 0) - (file.fatalErrorCount || 0),
  0,
);
const fatal = reports.reduce((n, file) => n + (file.fatalErrorCount || 0), 0);
if (fatal) {
  console.error("lint:ds ratchet: eslint fatals");
  console.error(result.stderr);
  process.exit(2);
}

if (writeBaseline) {
  writeFileSync(
    baselinePath,
    `${JSON.stringify({ errors: errorCount, updated: new Date().toISOString().slice(0, 10) }, null, 2)}\n`,
    "utf8",
  );
  console.log(`wrote ${baselinePath} errors=${errorCount}`);
  process.exit(0);
}

let baseline = { errors: 0 };
if (existsSync(baselinePath)) {
  baseline = JSON.parse(readFileSync(baselinePath, "utf8"));
}

const allowed = Number(baseline.errors) || 0;
if (errorCount > allowed) {
  console.error(
    `lint:ds ratchet FAIL: ${errorCount} errors > baseline ${allowed}. New tier leaks are not allowed.`,
  );
  for (const file of reports) {
    if (!file.errorCount) continue;
    for (const msg of file.messages || []) {
      if (msg.severity !== 2) continue;
      console.error(`  ${file.filePath}:${msg.line}:${msg.column}  ${msg.message}`);
    }
  }
  process.exit(1);
}

if (errorCount < allowed) {
  console.log(
    `lint:ds ratchet OK: ${errorCount} errors (baseline ${allowed}). Lower eslint/ds-lint/baseline.json to ${errorCount}.`,
  );
} else {
  console.log(`lint:ds ratchet OK: ${errorCount} errors (at baseline ${allowed}).`);
}
process.exit(0);
