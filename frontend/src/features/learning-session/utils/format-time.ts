import { SECONDS_PER_MINUTE } from "../constants";

const MINUTES_PER_HOUR = 60;

/** Whole minutes, rounded down as a clock does: "under a minute", "14 min", "1 h 05". */
export function formatClock(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / SECONDS_PER_MINUTE);

  if (minutes < 1) {
    return "under a minute";
  }

  if (minutes < MINUTES_PER_HOUR) {
    return `${minutes} min`;
  }

  return `${Math.floor(minutes / MINUTES_PER_HOUR)} h ${String(minutes % MINUTES_PER_HOUR).padStart(2, "0")}`;
}

/** How long something took, in words: "under a minute", "12 min", "1 h 5 min". */
export function formatDuration(totalSeconds: number): string {
  const minutes = Math.round(totalSeconds / SECONDS_PER_MINUTE);

  if (minutes < 1) {
    return "under a minute";
  }

  if (minutes < SECONDS_PER_MINUTE) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / SECONDS_PER_MINUTE);
  const rest = minutes % SECONDS_PER_MINUTE;

  return rest === 0 ? `${hours} h` : `${hours} h ${rest} min`;
}
