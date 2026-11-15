import { describe, expect, it } from "vitest";

import { thinkSeconds } from "@/features/lesson/utils/think-time";

describe("thinkSeconds", () => {
  it("is a base plus a second per word", () => {
    expect(thinkSeconds("Dw i'n moyn siarad Cymraeg", 1)).toBeCloseTo(7.2);
  });

  it("scales with the multiplier", () => {
    expect(thinkSeconds("Siarad", 2)).toBeCloseTo(7.2);
    expect(thinkSeconds("Siarad", 0.5)).toBeCloseTo(1.8);
  });

  it("is capped", () => {
    expect(thinkSeconds("un ".repeat(100), 3)).toBe(27);
  });

  it("ignores extra spaces", () => {
    expect(thinkSeconds("  Galla   i fynd ", 1)).toBeCloseTo(5.4);
  });
});
