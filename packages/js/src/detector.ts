import fs from "node:fs";
import path from "node:path";

import type { EnvInfo, PackageManager } from "./models.js";

export function detectPackageManager(nodeModulesPath: string): PackageManager {
  const parent = path.dirname(nodeModulesPath);

  if (fs.existsSync(path.join(parent, "pnpm-lock.yaml"))) return "pnpm";
  if (fs.existsSync(path.join(parent, "yarn.lock"))) return "yarn";
  if (fs.existsSync(path.join(parent, "bun.lockb")) || fs.existsSync(path.join(parent, "bun.lock"))) return "bun";
  if (fs.existsSync(path.join(parent, "package-lock.json"))) return "npm";

  if (fs.existsSync(path.join(nodeModulesPath, ".modules.yaml"))) return "pnpm";
  if (fs.existsSync(path.join(nodeModulesPath, ".yarn-integrity"))) return "yarn";
  if (fs.existsSync(path.join(nodeModulesPath, ".package-lock.json"))) return "npm";

  return "unknown";
}

function countTopLevelPackages(nodeModulesPath: string): number {
  let count = 0;
  let entries: fs.Dirent[];
  try {
    entries = fs.readdirSync(nodeModulesPath, { withFileTypes: true });
  } catch {
    return 0;
  }
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (entry.name.startsWith(".")) continue;
    if (entry.name.startsWith("@")) {
      const scopedPath = path.join(nodeModulesPath, entry.name);
      let scoped: fs.Dirent[];
      try {
        scoped = fs.readdirSync(scopedPath, { withFileTypes: true });
      } catch {
        continue;
      }
      count += scoped.filter((item) => item.isDirectory()).length;
    } else {
      count += 1;
    }
  }
  return count;
}

function pathSizeBytes(targetPath: string): number {
  let stat: fs.Stats;
  try {
    stat = fs.lstatSync(targetPath);
  } catch {
    return 0;
  }
  if (stat.isSymbolicLink()) return stat.size;
  if (stat.isFile()) return stat.size;
  if (!stat.isDirectory()) return 0;

  let total = 0;
  const stack = [targetPath];
  while (stack.length > 0) {
    const current = stack.pop() as string;
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(current, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      const next = path.join(current, entry.name);
      try {
        const itemStat = fs.lstatSync(next);
        if (itemStat.isSymbolicLink()) {
          total += itemStat.size;
        } else if (itemStat.isFile()) {
          total += itemStat.size;
        } else if (itemStat.isDirectory()) {
          stack.push(next);
        }
      } catch {
        continue;
      }
    }
  }
  return total;
}

export function detectEnvironment(
  nodeModulesPath: string,
  staleDays: number,
  deep: boolean,
): EnvInfo {
  const parent = path.dirname(nodeModulesPath);
  const signals: string[] = [];

  const hasNpmMarker = fs.existsSync(path.join(nodeModulesPath, ".package-lock.json"));
  const hasYarnMarker = fs.existsSync(path.join(nodeModulesPath, ".yarn-integrity"));
  const hasPnpmMarker = fs.existsSync(path.join(nodeModulesPath, ".modules.yaml"));
  const hasPackageJson = fs.existsSync(path.join(parent, "package.json"));

  if (hasNpmMarker) signals.push("npm-marker");
  if (hasYarnMarker) signals.push("yarn-marker");
  if (hasPnpmMarker) signals.push("pnpm-marker");
  if (hasPackageJson) signals.push("package.json");

  let stat: fs.Stats;
  try {
    stat = fs.statSync(nodeModulesPath);
  } catch {
    return {
      path: nodeModulesPath,
      packageManager: detectPackageManager(nodeModulesPath),
      packageCount: deep ? countTopLevelPackages(nodeModulesPath) : null,
      sizeBytes: deep ? pathSizeBytes(nodeModulesPath) : null,
      created: null,
      modified: null,
      isStale: false,
      isOutdated: false,
      signals: [...signals, "stat-unavailable"],
    };
  }
  const created = stat.birthtime ?? null;
  const modified = stat.mtime ?? null;
  const staleThreshold = Date.now() - staleDays * 86400000;
  const isStale = modified.getTime() < staleThreshold;

  let isOutdated = false;
  const packageJsonPath = path.join(parent, "package.json");
  if (fs.existsSync(packageJsonPath)) {
    const pkgStat = fs.statSync(packageJsonPath);
    isOutdated = pkgStat.mtime.getTime() > modified.getTime();
  }

  return {
    path: nodeModulesPath,
    packageManager: detectPackageManager(nodeModulesPath),
    packageCount: deep ? countTopLevelPackages(nodeModulesPath) : null,
    sizeBytes: deep ? pathSizeBytes(nodeModulesPath) : null,
    created,
    modified,
    isStale,
    isOutdated,
    signals,
  };
}

export function installHint(packageManager: PackageManager): string {
  if (packageManager === "pnpm") return "pnpm install";
  if (packageManager === "yarn") return "yarn install";
  if (packageManager === "bun") return "bun install";
  return "npm install";
}
