import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  getSnapshot,
  isHintVisible,
  recordUse,
  recordVisit,
  subscribe,
} from "@/features/home/stores/headphone-hint-store";

beforeEach(() => {
  localStorage.clear();
});

describe("isHintVisible", () => {
  it("shows for someone who has not been before", () => {
    expect(isHintVisible(getSnapshot())).toBe(true);
  });

  it("shows for the first five visits and not after", () => {
    for (let visit = 1; visit <= 5; visit++) {
      recordVisit();
      expect(isHintVisible(getSnapshot())).toBe(true);
    }

    recordVisit();
    expect(isHintVisible(getSnapshot())).toBe(false);
  });

  it("hides for good once a headphone control has been used", () => {
    recordVisit();
    recordUse();

    expect(isHintVisible(getSnapshot())).toBe(false);
  });

  it.each(["not json", '{"used":"yes","visits":1}', "[]", "null"])("starts again when storage holds %s", (stored) => {
    expect(isHintVisible(stored)).toBe(true);
  });

  it("keeps the visits already counted when a control is used", () => {
    recordVisit();
    recordVisit();
    recordUse();

    expect(JSON.parse(getSnapshot() ?? "null")).toEqual({ used: true, visits: 2 });
  });
});

describe("subscribe", () => {
  it("tells a listener about each change until it unsubscribes", () => {
    const listener = vi.fn();
    const unsubscribe = subscribe(listener);

    recordVisit();
    recordUse();
    unsubscribe();
    recordVisit();

    expect(listener).toHaveBeenCalledTimes(2);
  });
});
