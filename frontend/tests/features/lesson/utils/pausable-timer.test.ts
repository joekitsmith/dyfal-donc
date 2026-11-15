import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { startPausableTimer } from "@/features/lesson/utils/pausable-timer";

describe("startPausableTimer", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("fires after the time", () => {
    const onElapsed = vi.fn();

    startPausableTimer(1000, onElapsed);
    vi.advanceTimersByTime(999);

    expect(onElapsed).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1);

    expect(onElapsed).toHaveBeenCalledOnce();
  });

  it("keeps the remaining time while paused", () => {
    const onElapsed = vi.fn();
    const timer = startPausableTimer(1000, onElapsed);

    vi.advanceTimersByTime(400);
    timer.pause();
    vi.advanceTimersByTime(5000);

    expect(onElapsed).not.toHaveBeenCalled();

    timer.resume();
    vi.advanceTimersByTime(599);

    expect(onElapsed).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1);

    expect(onElapsed).toHaveBeenCalledOnce();
  });

  it("never fires once cancelled", () => {
    const onElapsed = vi.fn();

    startPausableTimer(1000, onElapsed).cancel();
    vi.advanceTimersByTime(2000);

    expect(onElapsed).not.toHaveBeenCalled();
  });
});
