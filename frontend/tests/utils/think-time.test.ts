import { describe, expect, it } from "vitest";

import { thinkSeconds } from "@/utils/think-time";

describe("thinkSeconds", () => {
  it("is a base plus a second per word", () => {
    expect(thinkSeconds("Dw i'n moyn siarad Cymraeg", 1)).toBeCloseTo(5.76);
  });

  it("scales with the multiplier", () => {
    expect(thinkSeconds("Siarad", 2)).toBeCloseTo(5.76);
    expect(thinkSeconds("Siarad", 0.5)).toBeCloseTo(1.44);
  });

  it("is capped", () => {
    expect(thinkSeconds("un ".repeat(100), 3)).toBe(21.6);
  });

  it("ignores extra spaces", () => {
    expect(thinkSeconds("  Galla   i fynd ", 1)).toBeCloseTo(4.32);
  });
});
