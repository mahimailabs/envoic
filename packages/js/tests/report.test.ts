import { describe, expect, test } from "vitest";

import { barChart, formatAge, formatSize } from "../src/utils.js";

describe("report utils", () => {
  test("formatSize", () => {
    expect(formatSize(512)).toBe("512B");
    expect(formatSize(1024)).toBe("1K");
    expect(formatSize(1024 * 1024)).toBe("1M");
  });

  test("formatAge", () => {
    const now = new Date("2026-02-09T00:00:00Z");
    expect(formatAge(new Date("2026-02-08T00:00:00Z"), now)).toBe("1d");
  });

  test("barChart", () => {
    expect(barChart(0, 100, 10)).toBe("[░░░░░░░░░░]");
    expect(barChart(100, 100, 10)).toBe("[██████████]");
  });
});
