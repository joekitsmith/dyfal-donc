import { countWords } from "@/utils/count-words";

import type { Timeline } from "../types";

/** How far into the think time the audio is, and how long that time lasts. */
export type ThinkWindow = { readonly duration: number; readonly elapsed: number };

/** The blocks that show the time to speak: one for each word, and three more. */
const EXTRA_BEATS = 3;

/** The block the learner is on. After the last block's time it stays on the last, until the phase changes. */
export function beatIndexAt({ duration, elapsed }: ThinkWindow, count: number): number {
  const beatSeconds = duration / count;

  return Math.min(count - 1, Math.max(0, Math.floor(elapsed / beatSeconds)));
}

export function beatCount(welsh: string): number {
  return countWords(welsh) + EXTRA_BEATS;
}

/** Where a position falls in the think time of a track, or null when the track has none. */
export function thinkWindow(timeline: Timeline, position: number): null | ThinkWindow {
  const index = timeline.findIndex((entry) => entry.phase === "thinking");
  const start = timeline[index]?.startsAt;
  const end = timeline[index + 1]?.startsAt;

  if (start === undefined || end === undefined) {
    return null;
  }

  return { duration: end - start, elapsed: position - start };
}
