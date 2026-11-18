import { describe, expect, it } from "vitest";

import { formatClock, formatDuration } from "@/features/learning-session/utils/format-time";

describe("formatClock", () => {
  it.each([
    [0, "under a minute"],
    [59, "under a minute"],
    [60, "1 min"],
    [119, "1 min"],
    [840, "14 min"],
    [3599, "59 min"],
    [3600, "1 h 00"],
    [3900, "1 h 05"],
    [7500, "2 h 05"],
  ])("shows %d seconds as %s", (seconds, shown) => {
    expect(formatClock(seconds)).toBe(shown);
  });
});

describe("formatDuration", () => {
  it.each([
    [0, "under a minute"],
    [29, "under a minute"],
    [30, "1 min"],
    [720, "12 min"],
    [3600, "1 h"],
    [3900, "1 h 5 min"],
  ])("shows %d seconds as %s", (seconds, shown) => {
    expect(formatDuration(seconds)).toBe(shown);
  });
});
