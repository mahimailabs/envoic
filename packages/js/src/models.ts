export type PackageManager = "npm" | "yarn" | "pnpm" | "bun" | "unknown";
export type SafetyLevel = "always_safe" | "usually_safe" | "careful";

export type ArtifactCategory =
  | "build_cache"
  | "build_output"
  | "tool_cache"
  | "test_output";

export interface EnvInfo {
  path: string;
  packageManager: PackageManager;
  packageCount: number | null;
  sizeBytes: number | null;
  created: Date | null;
  modified: Date | null;
  isStale: boolean;
  isOutdated: boolean;
  signals: string[];
}

export interface ArtifactInfo {
  path: string;
  category: ArtifactCategory;
  safety: SafetyLevel;
  sizeBytes: number | null;
  patternMatched: string;
}

export interface ArtifactSummary {
  category: ArtifactCategory;
  safety: SafetyLevel;
  count: number;
  totalSizeBytes: number;
  items: ArtifactInfo[];
  pattern: string;
}

export interface ScanResult {
  scanPath: string;
  scanDepth: number;
  staleDays: number;
  durationSeconds: number;
  environments: EnvInfo[];
  totalSizeBytes: number;
  hostname: string;
  timestamp: Date;
  artifacts: ArtifactInfo[];
  artifactSummary: ArtifactSummary[];
}
