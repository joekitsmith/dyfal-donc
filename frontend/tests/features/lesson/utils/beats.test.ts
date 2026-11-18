import { describe, expect, it } from "vitest";

import type { Timeline } from "@/features/lesson/types";

import { beatCount, beatIndexAt, thinkWindow } from "@/features/lesson/utils/beats";
import { thinkSeconds } from "@/utils/think-time";

const TIMELINE: Timeline = [
  { phase: "playing_english", startsAt: 0 },
  { phase: "thinking", startsAt: 2 },
  { phase: "playing_welsh_standard", startsAt: 7.76 },
];

describe("beatCount", () => {
  it("is the number of words and three more", () => {
    expect(beatCount("Galla i fynd")).toBe(6);
    expect(beatCount("Dw i eisiau mynd i'r siop heddiw")).toBe(10);
  });
});

describe("a beat's length", () => {
  it("is the same at the default setting however long the sentence is", () => {
    for (const welsh of ["Galla i fynd", "Dw i eisiau mynd i'r siop heddiw"]) {
      expect(thinkSeconds(welsh, 1) / beatCount(welsh)).toBeCloseTo(0.72);
    }
  });

  it("stretches with the setting without adding blocks", () => {
    expect(thinkSeconds("Galla i fynd", 2) / beatCount("Galla i fynd")).toBeCloseTo(1.44);
  });

  it("shortens when the longest think time applies", () => {
    const welsh = "un ".repeat(40);

    expect(thinkSeconds(welsh, 1) / beatCount(welsh)).toBeLessThan(0.72);
  });
});

describe("thinkWindow", () => {
  it("measures from where the think time starts, to where it ends", () => {
    const window = thinkWindow(TIMELINE, 3);

    expect(window?.elapsed).toBeCloseTo(1);
    expect(window?.duration).toBeCloseTo(5.76);
  });

  it("is negative before the think time and past its end after it", () => {
    expect(thinkWindow(TIMELINE, 1)?.elapsed).toBeLessThan(0);
    expect(thinkWindow(TIMELINE, 9)?.elapsed).toBeGreaterThan(5.76);
  });

  it("is null for a track with no think time", () => {
    expect(thinkWindow([{ phase: "playing_english", startsAt: 0 }], 1)).toBeNull();
  });
});

describe("beatIndexAt", () => {
  const window = (elapsed: number) => ({ duration: 7.2, elapsed });

  it("moves to the next block each beat", () => {
    expect(beatIndexAt(window(0), 10)).toBe(0);
    expect(beatIndexAt(window(0.71), 10)).toBe(0);
    expect(beatIndexAt(window(0.72), 10)).toBe(1);
    expect(beatIndexAt(window(3.6), 10)).toBe(5);
  });

  it("stays on the last block at the end of the time", () => {
    expect(beatIndexAt(window(7.2), 10)).toBe(9);
    expect(beatIndexAt(window(30), 10)).toBe(9);
  });

  it("stays on the first block before the time starts", () => {
    expect(beatIndexAt(window(-1), 10)).toBe(0);
  });
});
