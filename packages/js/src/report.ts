import fs from "node:fs";
import path from "node:path";

import { SAFETY_TEXT } from "./artifacts.js";
import type { EnvInfo, ScanResult } from "./models.js";
import { barChart, boxLine, formatAge, formatSize, normalizeDisplayPath, shortenPath } from "./utils.js";

const WIDTH = 58;

function boxTop(width = WIDTH): string {
  return `┌${"─".repeat(width)}┐`;
}

function boxMid(width = WIDTH): string {
  return `├${"─".repeat(width)}┤`;
}

function boxBottom(width = WIDTH): string {
  return `└${"─".repeat(width)}┘`;
}

function row(label: string, value: string, width = WIDTH): string {
  const left = `  ${label.padEnd(12, " ")}`;
  const rightWidth = Math.max(0, width - left.length - 2);
  const clipped = value.slice(0, rightWidth);
  return boxLine(`${left}${clipped.padStart(rightWidth, " ")}  `, width);
}

function envHeader(): string {
  return `  ${"#".padEnd(3, " ")} ${"Path".padEnd(30, " ")} ${"Pkg Mgr".padEnd(8, " ")} ${"Size".padStart(6, " ")} ${"Age".padStart(5, " ")}`;
}

function envRow(index: number, env: EnvInfo, scanRoot: string): string {
  const label = normalizeDisplayPath(env.path, scanRoot);
  const stale = env.isStale ? " STALE" : "";
  const outdated = env.isOutdated ? " OUTDATED" : "";
  return `  ${String(index).padEnd(3, " ")} ${shortenPath(label, 30).padEnd(30, " ")} ${env.packageManager.padEnd(8, " ")} ${formatSize(env.sizeBytes).padStart(6, " ")} ${formatAge(env.modified).padStart(5, " ")}${stale}${outdated}`;
}

export function formatReport(result: ScanResult, deep = false): string {
  const staleCount = result.environments.filter((item) => item.isStale).length;
  const outdatedCount = result.environments.filter((item) => item.isOutdated).length;
  const artifactCount = result.artifactSummary.reduce((acc, item) => acc + item.count, 0);
  const artifactSize = result.artifactSummary.reduce((acc, item) => acc + item.totalSizeBytes, 0);

  const lines: string[] = [];
  lines.push(boxTop());
  lines.push(boxLine("  ENVOIC - JavaScript Environment Report"));
  lines.push(boxLine("  TR-200  Environment Scanner"));
  lines.push(boxMid());
  lines.push(row("Date", result.timestamp.toISOString().replace("T", " ").slice(0, 19)));
  lines.push(row("Host", result.hostname));
  lines.push(row("Scan Path", shortenPath(result.scanPath, 36)));
  lines.push(row("Scan Depth", String(result.scanDepth)));
  lines.push(row("Duration", `${result.durationSeconds.toFixed(2)}s`));
  lines.push(boxMid());
  lines.push(row("NM Found", String(result.environments.length)));
  lines.push(row("Total Size", formatSize(result.totalSizeBytes)));
  lines.push(row("Stale", `>${result.staleDays}d: ${staleCount}`));
  lines.push(row("Outdated", String(outdatedCount)));
  lines.push(row("Artifacts", String(artifactCount)));
  lines.push(row("Art Size", deep ? formatSize(artifactSize) : "-"));
  lines.push(boxBottom());
  lines.push("");

  lines.push("NODE MODULES");
  lines.push("─".repeat(58));
  lines.push(envHeader());
  lines.push("─".repeat(58));
  if (result.environments.length === 0) {
    lines.push("  (no node_modules found)");
  } else {
    result.environments.forEach((env, i) => lines.push(envRow(i + 1, env, result.scanPath)));
  }
  lines.push("─".repeat(58));
  lines.push("");

  lines.push("ARTIFACTS");
  lines.push("─".repeat(58));
  lines.push(`  ${"Category".padEnd(22, " ")} ${"Count".padStart(6, " ")} ${"Size".padStart(8, " ")} ${"Safety".padStart(16, " ")}`);
  lines.push("─".repeat(58));
  for (const item of result.artifactSummary) {
    lines.push(`  ${item.pattern.padEnd(22, " ")} ${String(item.count).padStart(6, " ")} ${formatSize(item.totalSizeBytes).padStart(8, " ")} ${SAFETY_TEXT[item.safety].padStart(16, " ")}`);
  }
  if (result.artifactSummary.length === 0) lines.push("  (no artifacts found)");
  lines.push("─".repeat(58));

  if (deep) {
    lines.push("");
    lines.push("SIZE DISTRIBUTION");
    const sized = result.environments.filter((item) => item.sizeBytes !== null);
    const maxSize = sized.reduce((acc, item) => Math.max(acc, item.sizeBytes ?? 0), 0);
    for (const env of sized) {
      const size = env.sizeBytes ?? 0;
      const label = normalizeDisplayPath(env.path, result.scanPath);
      lines.push(`  ${barChart(size, maxSize, 24)} ${shortenPath(label, 24).padEnd(24, " ")} ${formatSize(size).padStart(6, " ")}`);
    }
  }

  return lines.join("\n");
}

export function formatList(environments: EnvInfo[], scanRoot: string): string {
  const lines = [envHeader(), "─".repeat(58)];
  environments.forEach((env, i) => lines.push(envRow(i + 1, env, scanRoot)));
  if (environments.length === 0) lines.push("  (no node_modules found)");
  return lines.join("\n");
}

export function formatInfo(env: EnvInfo, topPackages: Array<{ name: string; size: number }>, reinstallHint: string): string {
  const lines: string[] = [];
  lines.push(boxTop());
  lines.push(boxLine("  ENVOIC - Node Modules Detail"));
  lines.push(boxMid());
  lines.push(row("Path", env.path));
  lines.push(row("Manager", env.packageManager));
  lines.push(row("Packages", String(env.packageCount ?? "-")));
  lines.push(row("Size", formatSize(env.sizeBytes)));
  lines.push(row("Modified", env.modified ? env.modified.toISOString().replace("T", " ").slice(0, 19) : "-"));
  lines.push(row("Stale", env.isStale ? "yes" : "no"));
  lines.push(row("Outdated", env.isOutdated ? "yes" : "no"));
  lines.push(row("Reinstall", reinstallHint));
  lines.push(boxBottom());
  lines.push("");
  lines.push("TOP PACKAGES");
  lines.push("─".repeat(58));
  if (topPackages.length === 0) {
    lines.push("  (no packages found)");
  } else {
    topPackages.forEach((item, idx) => {
      lines.push(`  ${String(idx + 1).padStart(2, " ")}. ${item.name} (${formatSize(item.size)})`);
    });
  }
  lines.push("─".repeat(58));
  return lines.join("\n");
}

export function topLargestPackages(nodeModulesPath: string, limit = 10): Array<{ name: string; size: number }> {
  const resolvedPath = path.resolve(nodeModulesPath);
  const result: Array<{ name: string; size: number }> = [];
  const direct = fs.readdirSync(resolvedPath, { withFileTypes: true });
  for (const entry of direct) {
    if (!entry.isDirectory()) continue;
    if (entry.name.startsWith(".")) continue;

    // Handle scoped packages (@scope/pkg)
    if (entry.name.startsWith("@")) {
      const scopePath = path.join(resolvedPath, entry.name);
      let scopedEntries: fs.Dirent[];
      try {
        scopedEntries = fs.readdirSync(scopePath, { withFileTypes: true });
      } catch {
        continue;
      }
      for (const scoped of scopedEntries) {
        if (!scoped.isDirectory()) continue;
        if (scoped.name.startsWith(".")) continue;
        const full = path.join(scopePath, scoped.name);
        const size = measureDirSize(full);
        result.push({ name: `${entry.name}/${scoped.name}`, size });
      }
      continue;
    }

    const full = path.join(resolvedPath, entry.name);
    const size = measureDirSize(full);
    result.push({ name: entry.name, size });
  }
  return result.sort((a, b) => b.size - a.size).slice(0, limit);
}

function measureDirSize(dirPath: string): number {
  let size = 0;
  const stack = [dirPath];
  while (stack.length > 0) {
    const current = stack.pop() as string;
    let children: fs.Dirent[];
    try {
      children = fs.readdirSync(current, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const child of children) {
      const childPath = path.join(current, child.name);
      try {
        const st = fs.lstatSync(childPath);
        if (st.isSymbolicLink() || st.isFile()) size += st.size;
        else if (st.isDirectory()) stack.push(childPath);
      } catch {
        continue;
      }
    }
  }
  return size;
}
