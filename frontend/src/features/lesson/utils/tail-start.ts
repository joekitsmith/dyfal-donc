import type { Timeline } from "../types";

/** Where the silent tail starts, which is where the exercise ends as far as the learner is concerned. */
export function tailStart(timeline: Timeline): number {
  return timeline.at(-1)?.startsAt ?? 0;
}
