import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { describe, expect, test } from "vitest";

import { detectPackageManager } from "../src/detector.js";

describe("detectPackageManager", () => {
  test("detects npm from parent lock", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-det-"));
    const nm = path.join(root, "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(root, "package-lock.json"), "{}", "utf-8");
    expect(detectPackageManager(nm)).toBe("npm");
  });

  test("detects pnpm from marker", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-det-"));
    const nm = path.join(root, "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(nm, ".modules.yaml"), "", "utf-8");
    expect(detectPackageManager(nm)).toBe("pnpm");
  });
});
