import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { afterAll, describe, expect, test } from "vitest";

import { scan } from "../src/scanner.js";

describe("scanner", () => {
  const tmpDirs: string[] = [];

  afterAll(() => {
    for (const dir of tmpDirs) {
      try {
        fs.rmSync(dir, { recursive: true, force: true });
      } catch {
        // ignore cleanup errors
      }
    }
  });

  test("finds node_modules", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-scan-"));
    tmpDirs.push(root);
    const nm = path.join(root, "app", "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(root, "app", "package.json"), "{}", "utf-8");

    const result = scan({ root, depth: 5, deep: false, staleDays: 90, includeArtifacts: false });
    expect(result.environments.length).toBe(1);
    const env = result.environments[0];
    if (!env) throw new Error("expected at least one environment");
    expect(path.basename(env.path)).toBe("node_modules");
  });
});
