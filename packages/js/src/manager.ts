import fs from "node:fs";
import path from "node:path";
import { stdin as input, stdout as output } from "node:process";
import readline from "node:readline/promises";

import { checkbox } from "@inquirer/prompts";

import type { ArtifactInfo, EnvInfo } from "./models.js";
import { formatAge, formatSize, normalizeDisplayPath } from "./utils.js";

export interface DeletionSummary {
  selectedCount: number;
  deletedCount: number;
  failedCount: number;
  skippedCount: number;
  bytesFreed: number;
  wouldFreeBytes: number;
  errors: string[];
  dryRun: boolean;
}

function insideRoot(candidate: string, scanRoot: string): boolean {
  const abs = path.resolve(candidate);
  const root = path.resolve(scanRoot);
  return abs === root || abs.startsWith(`${root}${path.sep}`);
}

function sizeForDelete(target: string): number {
  try {
    const st = fs.lstatSync(target);
    if (st.isSymbolicLink() || st.isFile()) return st.size;
  } catch {
    return 0;
  }

  let total = 0;
  const stack = [target];
  while (stack.length > 0) {
    const current = stack.pop() as string;
    let entries: fs.Dirent[] = [];
    try {
      entries = fs.readdirSync(current, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      const next = path.join(current, entry.name);
      try {
        const st = fs.lstatSync(next);
        if (st.isSymbolicLink() || st.isFile()) total += st.size;
        else if (st.isDirectory()) stack.push(next);
      } catch {
        continue;
      }
    }
  }
  return total;
}

function envLabel(env: EnvInfo, scanRoot: string): string {
  const stale = env.isStale ? " STALE" : "";
  const outdated = env.isOutdated ? " OUTDATED" : "";
  return `${normalizeDisplayPath(env.path, scanRoot).padEnd(45, " ")} ${String(env.packageManager).padEnd(8, " ")} ${formatSize(env.sizeBytes).padStart(6, " ")}  ${formatAge(env.modified).padStart(5, " ")}${stale}${outdated}`;
}

async function fallbackSelect(environments: EnvInfo[], scanRoot: string, staleOnly: boolean): Promise<EnvInfo[]> {
  console.log("Found environments. Enter numbers to delete (comma-separated):");
  environments.forEach((env, i) => {
    const marker = staleOnly && env.isStale ? "x" : " ";
    console.log(`${String(i + 1).padStart(3, " ")} [${marker}] ${envLabel(env, scanRoot)}`);
  });

  const rl = readline.createInterface({ input, output });
  const raw = await rl.question("Select [e.g. 1,3,5]: ");
  rl.close();

  const selected = new Set<number>();
  for (const token of raw.split(",").map((s) => s.trim())) {
    if (!/^\d+$/.test(token)) continue;
    const idx = Number(token);
    if (idx >= 1 && idx <= environments.length) selected.add(idx - 1);
  }
  return [...selected].sort((a, b) => a - b).map((idx) => environments[idx]);
}

export async function interactiveSelect(environments: EnvInfo[], scanRoot: string, staleOnly: boolean): Promise<EnvInfo[]> {
  if (environments.length === 0) return [];

  if (process.stdin.isTTY && process.stdout.isTTY) {
    try {
      const choices = environments.map((env, index) => ({
        name: envLabel(env, scanRoot),
        value: index,
        checked: staleOnly && env.isStale,
      }));
      const selected = await checkbox({
        message: "Select environments to delete",
        choices,
        instructions: "Use ↑↓ to move, Space to toggle, Enter to confirm",
      });
      return selected.map((idx) => environments[idx]);
    } catch {
      // fall through
    }
  }
  return fallbackSelect(environments, scanRoot, staleOnly);
}

export async function confirmDeletion(
  selected: Array<EnvInfo | ArtifactInfo>,
  scanRoot: string,
  dryRun: boolean,
  skipConfirm: boolean,
): Promise<boolean> {
  console.log("\n⚠ The following items will be PERMANENTLY DELETED:\n");
  let total = 0;
  selected.forEach((item, idx) => {
    const size = item.sizeBytes ?? 0;
    total += size;
    const p = "packageManager" in item ? normalizeDisplayPath(item.path, scanRoot) : normalizeDisplayPath(item.path, scanRoot);
    console.log(`  ${String(idx + 1).padEnd(3, " ")} ${p.padEnd(42, " ")} ${formatSize(size).padStart(6, " ")}`);
  });
  console.log(`\n  Total: ${formatSize(total)} will be freed`);

  if (dryRun) {
    console.log("\nDRY RUN — no files will be deleted.");
    return false;
  }
  if (skipConfirm) return true;

  const rl = readline.createInterface({ input, output });
  const typed = await rl.question('Type "delete" to confirm: ');
  rl.close();
  return typed.trim() === "delete";
}

export function deleteSelected(
  selected: Array<EnvInfo | ArtifactInfo>,
  scanRoot: string,
  dryRun: boolean,
  dryRunEcho = true,
): DeletionSummary {
  const summary: DeletionSummary = {
    selectedCount: selected.length,
    deletedCount: 0,
    failedCount: 0,
    skippedCount: 0,
    bytesFreed: 0,
    wouldFreeBytes: 0,
    errors: [],
    dryRun,
  };

  for (const item of selected) {
    const target = item.path;
    if (!insideRoot(target, scanRoot)) {
      summary.skippedCount += 1;
      summary.errors.push(`outside scan root: ${target}`);
      continue;
    }

    const size = sizeForDelete(target);
    summary.wouldFreeBytes += size;

    if (dryRun) {
      if (dryRunEcho) console.log(`[dry-run] Would delete ${normalizeDisplayPath(target, scanRoot)}`);
      continue;
    }

    if (!fs.existsSync(target) && !fs.lstatSync(path.dirname(target)).isDirectory()) {
      summary.skippedCount += 1;
      continue;
    }

    process.stdout.write(`Deleting ${normalizeDisplayPath(target, scanRoot)} ...`);
    try {
      const st = fs.lstatSync(target);
      if (st.isSymbolicLink()) fs.unlinkSync(target);
      else fs.rmSync(target, { recursive: true, force: false });
      summary.deletedCount += 1;
      summary.bytesFreed += size;
      console.log(" done");
    } catch (error) {
      const code = (error as NodeJS.ErrnoException).code;
      if (code === "EPERM" || code === "EACCES") {
        console.log(" failed (permission denied)");
      } else {
        console.log(" failed");
      }
      summary.failedCount += 1;
      summary.errors.push(String(error));
    }
  }

  return summary;
}

export function printDeletionReport(summary: DeletionSummary, initialTotal: number): void {
  const remaining = Math.max(0, initialTotal - summary.deletedCount);
  const freed = summary.dryRun ? summary.wouldFreeBytes : summary.bytesFreed;
  console.log("─".repeat(58));
  if (summary.dryRun) console.log("  DRY RUN SUMMARY");
  console.log(`  Deleted:   ${summary.deletedCount} environments`);
  console.log(`  Failed:    ${summary.failedCount}`);
  console.log(`  Skipped:   ${summary.skippedCount}`);
  console.log(`  Freed:     ${formatSize(freed)}`);
  console.log(`  Remaining: ${remaining} environments`);
  console.log("─".repeat(58));
}
