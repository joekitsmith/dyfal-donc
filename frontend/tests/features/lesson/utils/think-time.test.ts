import { describe, expect, it } from "vitest";

import { thinkSeconds } from "@/features/lesson/utils/think-time";

describe("thinkSeconds", () => {
  it("is a base plus a second per word", () => {
    expect(thinkSeconds("Dw i'n moyn siarad Cymraeg", 1)).toBe(8);
  });

  it("scales with the multiplier", () => {
    expect(thinkSeconds("Siarad", 2)).toBe(8);
    expect(thinkSeconds("Siarad", 0.5)).toBe(2);
  });

  it("is capped", () => {
    expect(thinkSeconds("un ".repeat(100), 3)).toBe(30);
  });

  it("ignores extra spaces", () => {
    expect(thinkSeconds("  Galla   i fynd ", 1)).toBe(6);
  });
});
