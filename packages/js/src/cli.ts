import fs from "node:fs";
import path from "node:path";

import type { Command } from "commander";

import { installHint } from "./detector.js";
import { confirmDeletion, deleteSelected, interactiveSelect, printDeletionReport } from "./manager.js";
import type { EnvInfo } from "./models.js";
import { formatInfo, formatList, formatReport, topLargestPackages } from "./report.js";
import { scan } from "./scanner.js";
import { toSerializable } from "./utils.js";

function parseIntOption(value: string): number {
  const n = Number.parseInt(value, 10);
  if (!Number.isFinite(n) || n < 1) throw new Error("must be a positive integer");
  return n;
}

async function confirmAndDelete(
  selected: EnvInfo[],
  scanRoot: string,
  initialTotal: number,
  dryRun: boolean,
  yes: boolean,
): Promise<void> {
  const confirmed = await confirmDeletion(selected, scanRoot, dryRun, yes);
  if (dryRun) {
    const summary = deleteSelected(selected, scanRoot, true, false);
    printDeletionReport(summary, initialTotal);
    return;
  }
  if (!confirmed) {
    console.log("Deletion cancelled.");
    return;
  }
  const summary = deleteSelected(selected, scanRoot, false);
  printDeletionReport(summary, initialTotal);
}

export function registerCommands(program: Command): void {
  program
    .command("scan")
    .argument("[path]", "path to scan", ".")
    .option("-d, --depth <n>", "max directory depth", parseIntOption, 5)
    .option("--deep", "compute size and package metadata", false)
    .option("--json", "output JSON report", false)
    .option("--stale-days <n>", "mark stale after N days", parseIntOption, 90)
    .option("--no-artifacts", "disable JS artifact detection")
    .action((targetPath, options) => {
      const result = scan({
        root: targetPath,
        depth: options.depth,
        deep: options.deep,
        staleDays: options.staleDays,
        includeArtifacts: options.artifacts,
      });
      if (options.json) {
        console.log(JSON.stringify(toSerializable(result), null, 2));
        return;
      }
      console.log(formatReport(result, options.deep));
    });

  program
    .command("list")
    .argument("[path]", "path to scan", ".")
    .option("-d, --depth <n>", "max directory depth", parseIntOption, 5)
    .option("--deep", "compute size metadata", false)
    .option("--stale-days <n>", "mark stale after N days", parseIntOption, 90)
    .action((targetPath, options) => {
      const result = scan({
        root: targetPath,
        depth: options.depth,
        deep: options.deep,
        staleDays: options.staleDays,
        includeArtifacts: false,
      });
      console.log(formatList(result.environments, result.scanPath));
    });

  program
    .command("info")
    .argument("<nodeModulesPath>", "path to node_modules directory")
    .action(async (targetPath) => {
      const abs = path.resolve(targetPath);
      if (path.basename(abs) !== "node_modules" || !fs.existsSync(abs)) {
        console.error(`Not a recognized node_modules path: ${targetPath}`);
        process.exitCode = 1;
        return;
      }
      const scanRoot = path.dirname(abs);
      const result = scan({
        root: scanRoot,
        depth: 2,
        deep: true,
        staleDays: 90,
        includeArtifacts: false,
      });
      const env = result.environments.find((item) => path.resolve(item.path) === abs);
      if (!env) {
        console.error(`Could not inspect environment: ${targetPath}`);
        process.exitCode = 1;
        return;
      }
      const topPackages = topLargestPackages(abs, 10);
      console.log(formatInfo(env, topPackages, installHint(env.packageManager)));
    });

  program
    .command("manage")
    .argument("[path]", "path to scan", ".")
    .option("-d, --depth <n>", "max directory depth", parseIntOption, 5)
    .option("--stale-only", "pre-select stale environments", false)
    .option("--stale-days <n>", "stale threshold in days", parseIntOption, 90)
    .option("--dry-run", "preview without deleting", false)
    .option("-y, --yes", "skip final confirmation", false)
    .option("--deep", "compute size metadata", false)
    .action(async (targetPath, options) => {
      const result = scan({
        root: targetPath,
        depth: options.depth,
        deep: options.deep,
        staleDays: options.staleDays,
        includeArtifacts: false,
      });
      if (result.environments.length === 0) {
        console.log("No environments found.");
        return;
      }
      const selected = await interactiveSelect(result.environments, result.scanPath, options.staleOnly);
      if (selected.length === 0) {
        console.log("Nothing selected.");
        return;
      }
      await confirmAndDelete(selected, result.scanPath, result.environments.length, options.dryRun, options.yes);
    });

  program
    .command("clean")
    .argument("[path]", "path to scan", ".")
    .option("-d, --depth <n>", "max directory depth", parseIntOption, 5)
    .option("--stale-days <n>", "stale threshold in days", parseIntOption, 90)
    .option("--dry-run", "preview without deleting", false)
    .option("-y, --yes", "skip final confirmation", false)
    .option("--deep", "compute size metadata", true)
    .action(async (targetPath, options) => {
      const result = scan({
        root: targetPath,
        depth: options.depth,
        deep: options.deep,
        staleDays: options.staleDays,
        includeArtifacts: false,
      });
      const selected = result.environments.filter((item) => item.isStale);
      if (selected.length === 0) {
        console.log("No stale environments found.");
        return;
      }
      await confirmAndDelete(selected, result.scanPath, result.environments.length, options.dryRun, options.yes);
    });

  program.command("version").action(() => {
    console.log("0.1.0");
  });
}
