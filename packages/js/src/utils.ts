import os from "node:os";
import path from "node:path";

const VENV_NAMES = new Set(["node_modules"]);

export function formatSize(numBytes: number | null): string {
  if (numBytes === null) return "-";
  if (numBytes < 1024) return `${numBytes}B`;
  const units = ["K", "M", "G", "T"];
  let value = numBytes;
  for (const unit of units) {
    value /= 1024;
    if (value < 1024 || unit === units[units.length - 1]) {
      if (value >= 100) return `${value.toFixed(0)}${unit}`;
      return `${value.toFixed(1).replace(/\.0$/, "")}${unit}`;
    }
  }
  return `${numBytes}B`;
}

export function formatAge(moment: Date | null, now = new Date()): string {
  if (!moment) return "-";
  const days = Math.max(0, Math.floor((now.getTime() - moment.getTime()) / 86400000));
  if (days < 30) return `${days}d`;
  if (days < 365) return `${Math.floor(days / 30)}mo`;
  return `${Math.floor(days / 365)}y`;
}

export function barChart(value: number, maxValue: number, width = 24): string {
  if (maxValue <= 0) return `[${"░".repeat(width)}]`;
  const filled = Math.max(0, Math.min(width, Math.round((value / maxValue) * width)));
  return `[${"█".repeat(filled)}${"░".repeat(width - filled)}]`;
}

export function boxLine(text: string, width = 58): string {
  const clipped = text.slice(0, width);
  return `│${clipped.padEnd(width, " ")}│`;
}

export function shortenPath(inputPath: string, maxLen = 36): string {
  let text = inputPath;
  const home = os.homedir();
  if (text.startsWith(home)) text = `~${text.slice(home.length)}`;
  if (text.length <= maxLen) return text;
  const keep = maxLen - 3;
  const prefix = Math.floor(keep / 2);
  const suffix = keep - prefix;
  return `${text.slice(0, prefix)}...${text.slice(-suffix)}`;
}

export function normalizeDisplayPath(targetPath: string, scanRoot: string): string {
  try {
    const rel = path.relative(scanRoot, targetPath);
    const normalized = rel === "" ? "." : rel;
    const base = path.basename(normalized);
    if (VENV_NAMES.has(base)) {
      const parent = path.dirname(normalized);
      return parent === "." ? "." : parent;
    }
    return normalized;
  } catch {
    return targetPath;
  }
}

export type Serializable<T> = T extends Date
  ? string
  : T extends Array<infer U>
    ? Serializable<U>[]
    : T extends object
      ? { [K in keyof T]: Serializable<T[K]> }
      : T;

export function toSerializable<T>(value: T): Serializable<T> {
  return JSON.parse(
    JSON.stringify(value, (_key, val: unknown) =>
      val instanceof Date ? val.toISOString() : val,
    ),
  ) as Serializable<T>;
}
