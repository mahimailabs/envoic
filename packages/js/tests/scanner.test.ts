import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { describe, expect, test } from "vitest";

import { scan } from "../src/scanner.js";

describe("scanner", () => {
  test("finds node_modules", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-scan-"));
    const nm = path.join(root, "app", "node_modules");
    fs.mkdirSync(nm, { recursive: true });
    fs.writeFileSync(path.join(root, "app", "package.json"), "{}", "utf-8");

    const result = scan({ root, depth: 5, deep: false, staleDays: 90, includeArtifacts: false });
    expect(result.environments.length).toBe(1);
    expect(path.basename(result.environments[0]!.path)).toBe("node_modules");
  });
});
