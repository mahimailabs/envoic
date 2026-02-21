import fs from "node:fs";
import path from "node:path";

import type { ArtifactCategory, ArtifactInfo, ArtifactSummary, SafetyLevel } from "./models.js";

export interface ArtifactPattern {
  name?: string;
  suffix?: string;
  type: "dir" | "file";
  category: ArtifactCategory;
  safety: SafetyLevel;
  requiresParentPackageJson?: boolean;
}

export const ARTIFACT_PATTERNS: ArtifactPattern[] = [
  { name: ".next", type: "dir", category: "build_cache", safety: "always_safe" },
  { name: ".nuxt", type: "dir", category: "build_cache", safety: "always_safe" },
  { name: ".turbo", type: "dir", category: "build_cache", safety: "always_safe" },
  { name: ".parcel-cache", type: "dir", category: "build_cache", safety: "always_safe" },
  { name: ".webpack", type: "dir", category: "build_cache", safety: "always_safe" },
  { name: ".swc", type: "dir", category: "build_cache", safety: "always_safe" },
  { name: ".output", type: "dir", category: "build_cache", safety: "always_safe" },
  { name: "storybook-static", type: "dir", category: "build_cache", safety: "always_safe" },

  { name: "dist", type: "dir", category: "build_output", safety: "usually_safe", requiresParentPackageJson: true },
  { name: "build", type: "dir", category: "build_output", safety: "usually_safe", requiresParentPackageJson: true },

  { name: ".eslintcache", type: "file", category: "tool_cache", safety: "always_safe" },
  { name: ".stylelintcache", type: "file", category: "tool_cache", safety: "always_safe" },
  { name: "tsconfig.tsbuildinfo", type: "file", category: "tool_cache", safety: "always_safe" },
  { name: ".cache", type: "dir", category: "tool_cache", safety: "always_safe" },

  { name: "coverage", type: "dir", category: "test_output", safety: "always_safe" },
  { name: ".nyc_output", type: "dir", category: "test_output", safety: "always_safe" },
];

export const SAFETY_TEXT: Record<SafetyLevel, string> = {
  always_safe: "safe to delete",
  usually_safe: "usually safe",
  careful: "careful",
};

export function isJsProjectDir(parentPath: string): boolean {
  return fs.existsSync(path.join(parentPath, "package.json"));
}

function artifactPatternName(pattern: ArtifactPattern): string {
  if (pattern.name) return pattern.name;
  return `*${pattern.suffix}`;
}

export function matchArtifact(
  entry: fs.Dirent,
  parentPath: string,
  fullPath: string,
): ArtifactInfo | null {
  for (const pattern of ARTIFACT_PATTERNS) {
    if (pattern.type === "dir" && !entry.isDirectory()) continue;
    if (pattern.type === "file" && !entry.isFile()) continue;

    if (pattern.name && entry.name !== pattern.name) continue;
    if (pattern.suffix && !entry.name.endsWith(pattern.suffix)) continue;
    if (pattern.requiresParentPackageJson && !isJsProjectDir(parentPath)) continue;

    return {
      path: fullPath,
      category: pattern.category,
      safety: pattern.safety,
      sizeBytes: null,
      patternMatched: artifactPatternName(pattern),
    };
  }
  return null;
}

export function summarizeArtifacts(artifacts: ArtifactInfo[]): ArtifactSummary[] {
  const grouped = new Map<string, ArtifactSummary>();
  for (const item of artifacts) {
    const key = `${item.patternMatched}:${item.category}:${item.safety}`;
    const existing = grouped.get(key);
    if (!existing) {
      grouped.set(key, {
        pattern: item.patternMatched,
        category: item.category,
        safety: item.safety,
        count: 1,
        totalSizeBytes: item.sizeBytes ?? 0,
        items: [item],
      });
    } else {
      existing.count += 1;
      existing.totalSizeBytes += item.sizeBytes ?? 0;
      existing.items.push(item);
    }
  }
  return [...grouped.values()].sort((a, b) => a.pattern.localeCompare(b.pattern));
}
