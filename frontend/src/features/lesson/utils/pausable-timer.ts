export type PausableTimer = {
  readonly cancel: () => void;
  readonly pause: () => void;
  readonly resume: () => void;
};

/** A timer that runs from the moment it is created and keeps its remaining time while paused. */
export function startPausableTimer(milliseconds: number, onElapsed: () => void): PausableTimer {
  let remaining = milliseconds;
  let startedAt = performance.now();
  let handle: ReturnType<typeof setTimeout> | undefined = setTimeout(onElapsed, remaining);

  return {
    cancel() {
      clearTimeout(handle);
      handle = undefined;
    },
    pause() {
      if (handle === undefined) {
        return;
      }

      clearTimeout(handle);
      handle = undefined;
      remaining -= performance.now() - startedAt;
    },
    resume() {
      if (handle !== undefined || remaining <= 0) {
        return;
      }

      startedAt = performance.now();
      handle = setTimeout(onElapsed, remaining);
    },
  };
}
