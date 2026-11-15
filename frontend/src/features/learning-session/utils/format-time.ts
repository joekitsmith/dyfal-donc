import { SECONDS_PER_HOUR, SECONDS_PER_MINUTE } from "../constants";

/** A running clock: 4:07, or 1:02:09 once it passes an hour. */
export function formatClock(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / SECONDS_PER_HOUR);
  const minutes = Math.floor((totalSeconds % SECONDS_PER_HOUR) / SECONDS_PER_MINUTE);
  const seconds = totalSeconds % SECONDS_PER_MINUTE;
  const paddedSeconds = String(seconds).padStart(2, "0");

  return hours > 0 ? `${hours}:${String(minutes).padStart(2, "0")}:${paddedSeconds}` : `${minutes}:${paddedSeconds}`;
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
