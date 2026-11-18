import type { Passkey } from "../types";

import { DEFAULT_PASSKEY_LABEL } from "../constants";

const MILLISECONDS_PER_DAY = 86_400_000;

/** What to call a passkey: the name it was given, or that it has none. */
export function passkeyName(passkey: Passkey): string {
  return passkey.label === DEFAULT_PASSKEY_LABEL ? "Unnamed passkey" : passkey.label;
}

/** When a passkey was added and last used, such as "Added 3 March 2026 · last used today". */
export function describePasskey(passkey: Passkey, now: Date = new Date()): string {
  const used =
    passkey.lastUsedAt === null ? "never used" : `last used ${describeDay(new Date(passkey.lastUsedAt), now)}`;

  return `Added ${writtenDay(new Date(passkey.createdAt))} · ${used}`;
}

function describeDay(day: Date, now: Date): string {
  const daysAgo = Math.round((startOfDay(now) - startOfDay(day)) / MILLISECONDS_PER_DAY);

  if (daysAgo <= 0) {
    return "today";
  }

  return daysAgo === 1 ? "yesterday" : writtenDay(day);
}

function startOfDay(moment: Date): number {
  return new Date(moment.getFullYear(), moment.getMonth(), moment.getDate()).getTime();
}

function writtenDay(moment: Date): string {
  return moment.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
}
