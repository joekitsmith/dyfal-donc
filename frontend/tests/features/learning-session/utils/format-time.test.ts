import { describe, expect, it } from "vitest";

import { formatClock, formatDuration } from "@/features/learning-session/utils/format-time";

describe("formatClock", () => {
  it.each([
    [0, "0:00"],
    [7, "0:07"],
    [247, "4:07"],
    [3600, "1:00:00"],
    [3729, "1:02:09"],
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
