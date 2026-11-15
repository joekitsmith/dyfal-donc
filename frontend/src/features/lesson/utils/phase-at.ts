import type { PositionPhase, Timeline } from "../types";

/** The phase a track is in at a position: the last one that has started. Past the end it is still the last. */
export function phaseAt(timeline: Timeline, seconds: number): PositionPhase {
  let phase: PositionPhase = timeline[0]?.phase ?? "playing_english";

  for (const entry of timeline) {
    if (entry.startsAt > seconds) {
      break;
    }

    phase = entry.phase;
  }

  return phase;
}
