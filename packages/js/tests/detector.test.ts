import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { afterEach, describe, expect, test } from "vitest";

import { detectPackageManager } from "../src/detector.js";

describe("detectPackageManager", () => {
  const tmpDirs: string[] = [];

  afterEach(() => {
    for (const dir of tmpDirs) {
      try {
        fs.rmSync(dir, { recursive: true, force: true });
      } catch {
        // ignore cleanup errors
      }
    }
    tmpDirs.length = 0;
  });

  test("detects npm from parent lock", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-det-"));
    tmpDirs.push(root);
    const nm = path.join(root, "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(root, "package-lock.json"), "{}", "utf-8");
    expect(detectPackageManager(nm)).toBe("npm");
  });

  test("detects pnpm from marker", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-det-"));
    tmpDirs.push(root);
    const nm = path.join(root, "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(nm, ".modules.yaml"), "", "utf-8");
    expect(detectPackageManager(nm)).toBe("pnpm");
  });

  test("detects yarn from lock file", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-det-"));
    tmpDirs.push(root);
    const nm = path.join(root, "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(root, "yarn.lock"), "", "utf-8");
    expect(detectPackageManager(nm)).toBe("yarn");
  });

  test("detects bun from bun.lockb", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-det-"));
    tmpDirs.push(root);
    const nm = path.join(root, "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(root, "bun.lockb"), "", "utf-8");
    expect(detectPackageManager(nm)).toBe("bun");
  });

  test("detects bun from bun.lock", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-det-"));
    tmpDirs.push(root);
    const nm = path.join(root, "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(root, "bun.lock"), "", "utf-8");
    expect(detectPackageManager(nm)).toBe("bun");
  });

  test("returns unknown when no lock files", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-det-"));
    tmpDirs.push(root);
    const nm = path.join(root, "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    expect(detectPackageManager(nm)).toBe("unknown");
  });
});
