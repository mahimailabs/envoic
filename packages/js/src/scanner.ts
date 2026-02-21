import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { matchArtifact, summarizeArtifacts } from "./artifacts.js";
import { detectEnvironment } from "./detector.js";
import type { ArtifactInfo, EnvInfo, ScanResult } from "./models.js";

export interface ScanOptions {
  root: string;
  depth: number;
  deep: boolean;
  staleDays: number;
  includeArtifacts: boolean;
}

const SKIP_NAMES = new Set([".git", ".hg", ".svn"]);
const ALLOWED_HIDDEN = new Set([".next", ".nuxt", ".turbo", ".swc", ".output", ".cache"]);

function dirSizeBytes(targetPath: string): number {
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

export function scan(options: ScanOptions): ScanResult {
  const scanPath = path.resolve(options.root);
  const start = performance.now();
  const environments: EnvInfo[] = [];
  const artifacts: ArtifactInfo[] = [];

  const seenEnv = new Set<string>();
  const seenArtifact = new Set<string>();

  function walk(current: string, depth: number): void {
    if (depth > options.depth) return;

    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(current, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      const next = path.join(current, entry.name);

      if (options.includeArtifacts) {
        const artifact = matchArtifact(entry, current, path.resolve(next));
        if (artifact) {
          if (!seenArtifact.has(artifact.path)) {
            if (options.deep) artifact.sizeBytes = dirSizeBytes(artifact.path);
            artifacts.push(artifact);
            seenArtifact.add(artifact.path);
          }
          if (entry.isDirectory()) continue;
        }
      }

      if (!entry.isDirectory()) continue;

      if (entry.name === "node_modules") {
        const abs = path.resolve(next);
        if (!seenEnv.has(abs)) {
          environments.push(detectEnvironment(abs, options.staleDays, options.deep));
          seenEnv.add(abs);
        }
        continue;
      }

      if (SKIP_NAMES.has(entry.name)) continue;
      if (entry.name.startsWith(".") && !ALLOWED_HIDDEN.has(entry.name)) continue;

      walk(next, depth + 1);
    }
  }

  walk(scanPath, 1);

  const durationSeconds = (performance.now() - start) / 1000;
  const totalSizeBytes = environments.reduce((acc, item) => acc + (item.sizeBytes ?? 0), 0);
  const artifactSummary = summarizeArtifacts(artifacts);

  return {
    scanPath,
    scanDepth: options.depth,
    durationSeconds,
    environments: environments.sort((a, b) => a.path.localeCompare(b.path)),
    totalSizeBytes,
    hostname: os.hostname(),
    timestamp: new Date(),
    artifacts: artifacts.sort((a, b) => a.path.localeCompare(b.path)),
    artifactSummary,
  };
}
