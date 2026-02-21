import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { describe, expect, test } from "vitest";

import { matchArtifact } from "../src/artifacts.js";

describe("artifacts", () => {
  test("matches .next", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-art-"));
    const p = path.join(root, ".next");
    fs.mkdirSync(p, { recursive: true });
    const entry = fs.readdirSync(root, { withFileTypes: true })[0]!;
    const found = matchArtifact(entry, root, p);
    expect(found?.patternMatched).toBe(".next");
  });

  test("dist requires package.json", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "envoic-art-"));
    const p = path.join(root, "dist");
    fs.mkdirSync(p, { recursive: true });
    const entry = fs.readdirSync(root, { withFileTypes: true })[0]!;
    expect(matchArtifact(entry, root, p)).toBeNull();
    fs.writeFileSync(path.join(root, "package.json"), "{}", "utf-8");
    expect(matchArtifact(entry, root, p)?.patternMatched).toBe("dist");
  });
});
