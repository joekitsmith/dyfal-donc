import { describe, expect, it } from "vitest";

import { beatGap } from "@/utils/beat-gap";

describe("beatGap", () => {
  it.each([
    [1, 8],
    [10, 8],
    [11, 6],
    [14, 6],
    [15, 4],
    [30, 4],
  ])("gives %d blocks a gap of %d", (count, gap) => {
    expect(beatGap(count)).toBe(gap);
  });
});
