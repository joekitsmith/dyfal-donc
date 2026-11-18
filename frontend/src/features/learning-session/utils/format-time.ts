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

/** The same as `formatClock`, in words: "under a minute", "14 minutes", "1 hour 5 minutes". */
export function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / SECONDS_PER_MINUTE);

  if (minutes < 1) {
    return "under a minute";
  }

  if (minutes < MINUTES_PER_HOUR) {
    return plural(minutes, "minute");
  }

  const hours = plural(Math.floor(minutes / MINUTES_PER_HOUR), "hour");
  const rest = minutes % MINUTES_PER_HOUR;

  return rest === 0 ? hours : `${hours} ${plural(rest, "minute")}`;
}

function plural(count: number, unit: string): string {
  return `${count} ${unit}${count === 1 ? "" : "s"}`;
}
